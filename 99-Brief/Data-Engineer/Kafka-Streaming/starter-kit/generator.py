#!/usr/bin/env python3
"""
Générateur d'événements de vente flash Bouquineo — KIT DE DÉMARRAGE (fourni aux apprenants).

Simule le trafic d'une vente flash : événements de commande et de clickstream (JSON),
avec des pièges réalistes injectés volontairement :
  - doublons d'événements (~5 % : le même event_id est ré-émis à l'identique),
  - formats d'horodatage hétérogènes (ISO 8601, epoch millisecondes, format français),
  - montants parfois manquants (~3 % : prix_unitaire à null),
  - messages JSON malformés (~1 % : payload tronqué).

Deux modes :
  observe : affiche les événements sur la sortie standard (aucune dépendance externe).
            python3 generator.py --mode observe --orders-per-minute 50 --duration 60
  kafka   : publie les événements dans les topics Kafka (nécessite confluent-kafka).
            python3 generator.py --mode kafka --bootstrap localhost:9092 \
                --orders-topic bouquineo.commandes.v1 --clicks-topic bouquineo.clickstream.v1

Ce script N'EST PAS à réécrire par l'apprenant (niveau imiter côté producteur) :
il doit en revanche savoir expliquer son fonctionnement.
"""

import argparse
import json
import logging
import random
import signal
import sys
import time
import uuid
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] generator: %(message)s",
)
log = logging.getLogger("generator")

# ---------------------------------------------------------------------------
# Catalogue simulé : 12 000 références BQ-00001 à BQ-12000.
# Les 40 premières sont "en vente flash" et concentrent 90 % des commandes,
# avec une popularité décroissante (loi de Zipf) pour faire émerger un top ventes.
# ---------------------------------------------------------------------------
NB_REFERENCES = 12_000
NB_FLASH = 40
CANAUX = ["site_web", "site_web", "site_web", "marketplace", "librairie_affiliee"]
PAGES = ["/accueil", "/vente-flash", "/panier", "/recherche", "/produit/{ref}"]

# Probabilités des pièges injectés
P_DOUBLON = 0.05
P_PRIX_MANQUANT = 0.03
P_MALFORME = 0.01
# Répartition des formats de date : ISO 8601 (70 %), epoch ms (15 %), français (15 %)
FORMATS_TS = ["iso", "iso", "iso", "iso", "iso", "iso", "iso", "epoch_ms", "epoch_ms", "fr"]

_arret_demande = False


def _handler_arret(signum, _frame):
    """Arrêt propre sur Ctrl+C / SIGTERM."""
    global _arret_demande
    log.info("Signal %s reçu, arrêt du générateur...", signum)
    _arret_demande = True


def ref_produit(rng: random.Random) -> str:
    """Tire une référence produit : 90 % dans la sélection flash (pondérée Zipf), 10 % ailleurs."""
    if rng.random() < 0.90:
        # Loi de Zipf approchée sur les 40 titres de la vente flash
        poids = [1.0 / (i + 1) for i in range(NB_FLASH)]
        idx = rng.choices(range(NB_FLASH), weights=poids, k=1)[0] + 1
    else:
        idx = rng.randint(NB_FLASH + 1, NB_REFERENCES)
    return f"BQ-{idx:05d}"


def formater_ts(rng: random.Random, dt: datetime):
    """Retourne l'horodatage dans un des formats hétérogènes (piège volontaire)."""
    fmt = rng.choice(FORMATS_TS)
    if fmt == "iso":
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    if fmt == "epoch_ms":
        return int(dt.timestamp() * 1000)
    return dt.strftime("%d/%m/%Y %H:%M:%S")  # format français


def evenement_commande(rng: random.Random) -> dict:
    """Construit un événement de commande JSON."""
    now = datetime.now(timezone.utc)
    prix = None if rng.random() < P_PRIX_MANQUANT else round(rng.uniform(5.0, 45.0), 2)
    return {
        "event_id": str(uuid.uuid4()),
        "order_id": f"ORD-{now.strftime('%Y%m%d')}-{rng.randint(100000, 999999)}",
        "ts": formater_ts(rng, now),
        "product_ref": ref_produit(rng),
        "quantite": rng.choices([1, 2, 3], weights=[0.7, 0.2, 0.1], k=1)[0],
        "prix_unitaire": prix,
        "canal": rng.choice(CANAUX),
    }


def evenement_clic(rng: random.Random) -> dict:
    """Construit un événement de clickstream JSON."""
    now = datetime.now(timezone.utc)
    page = rng.choice(PAGES)
    ref = None
    if "{ref}" in page:
        ref = ref_produit(rng)
        page = page.format(ref=ref)
    return {
        "event_id": str(uuid.uuid4()),
        "session_id": f"SES-{rng.randint(1000, 9999)}",
        "ts": formater_ts(rng, now),
        "page": page,
        "product_ref": ref,
    }


def serialiser(rng: random.Random, evenement: dict) -> str:
    """Sérialise l'événement en JSON ; ~1 % des messages sont volontairement tronqués."""
    payload = json.dumps(evenement, ensure_ascii=False)
    if rng.random() < P_MALFORME:
        return payload[: max(10, len(payload) // 2)]  # JSON malformé (piège)
    return payload


class SortieStdout:
    """Sortie 'observe' : affiche les événements, aucune dépendance externe."""

    def emettre(self, topic: str, cle: str, payload: str) -> None:
        print(f"[{topic}] key={cle} {payload}", flush=True)

    def fermer(self) -> None:
        pass


class SortieKafka:
    """Sortie 'kafka' : publie les événements via confluent-kafka."""

    def __init__(self, bootstrap: str):
        from confluent_kafka import Producer  # import paresseux : inutile en mode observe

        self._producer = Producer(
            {
                "bootstrap.servers": bootstrap,
                "acks": "all",           # attend la confirmation du broker
                "retries": 5,            # ré-essaie en cas d'erreur transitoire
                "linger.ms": 20,         # micro-batching côté producteur
            }
        )

    def _callback(self, err, msg):
        if err is not None:
            log.error("Échec de livraison sur %s : %s", msg.topic(), err)

    def emettre(self, topic: str, cle: str, payload: str) -> None:
        # La clé garantit que tous les événements d'une même commande / session
        # partent dans la même partition (ordre préservé par partition).
        self._producer.produce(topic, key=cle, value=payload, callback=self._callback)
        self._producer.poll(0)

    def fermer(self) -> None:
        log.info("Vidage du tampon du producteur (flush)...")
        self._producer.flush(10)


def principal() -> int:
    parser = argparse.ArgumentParser(description="Générateur d'événements de vente flash Bouquineo")
    parser.add_argument("--mode", choices=["observe", "kafka"], default="observe")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Brokers Kafka (mode kafka)")
    parser.add_argument("--orders-topic", default="bouquineo.commandes.v1")
    parser.add_argument("--clicks-topic", default="bouquineo.clickstream.v1")
    parser.add_argument("--orders-per-minute", type=int, default=50, help="Débit de commandes (max ~50 en vente flash)")
    parser.add_argument("--clicks-per-order", type=int, default=5, help="Ratio clics / commande")
    parser.add_argument("--duration", type=int, default=0, help="Durée en secondes (0 = illimité)")
    parser.add_argument("--seed", type=int, default=None, help="Graine aléatoire (tests reproductibles)")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    signal.signal(signal.SIGINT, _handler_arret)
    signal.signal(signal.SIGTERM, _handler_arret)

    try:
        sortie = SortieStdout() if args.mode == "observe" else SortieKafka(args.bootstrap)
    except Exception as exc:  # ex : confluent-kafka absent, broker injoignable
        log.error("Impossible d'initialiser la sortie %s : %s", args.mode, exc)
        return 1

    intervalle = 60.0 / max(1, args.orders_per_minute)
    debut = time.time()
    compteurs = {"commandes": 0, "clics": 0, "doublons": 0, "malformes_potentiels": 0}
    derniere_commande = None

    log.info(
        "Démarrage : mode=%s, %d commandes/min, %d clics/commande, durée=%s",
        args.mode, args.orders_per_minute, args.clicks_per_order,
        f"{args.duration}s" if args.duration else "illimitée",
    )

    while not _arret_demande:
        if args.duration and (time.time() - debut) >= args.duration:
            break

        # --- Doublon (~5 %) : ré-émission à l'identique de la dernière commande ---
        if derniere_commande is not None and rng.random() < P_DOUBLON:
            sortie.emettre(args.orders_topic, derniere_commande["order_id"],
                           json.dumps(derniere_commande, ensure_ascii=False))
            compteurs["doublons"] += 1

        commande = evenement_commande(rng)
        derniere_commande = commande
        sortie.emettre(args.orders_topic, commande["order_id"], serialiser(rng, commande))
        compteurs["commandes"] += 1

        for _ in range(args.clicks_per_order):
            clic = evenement_clic(rng)
            sortie.emettre(args.clicks_topic, clic["session_id"], serialiser(rng, clic))
            compteurs["clics"] += 1

        time.sleep(intervalle)

    sortie.fermer()
    log.info("Arrêt. Statistiques : %s", compteurs)
    return 0


if __name__ == "__main__":
    sys.exit(principal())
