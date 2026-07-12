#!/usr/bin/env python3
"""
KIT DE DEMARRAGE — Générateur des exports CSV quotidiens de la marketplace.

Simule le fichier déposé chaque jour par la DSI, avec les défauts annoncés
dans le brief :
  - colonnes RENOMMEES par rapport aux conventions de l'entrepôt
    (order_ref, order_date, sku, qty, unit_price_cents, customer_uid, partner_name)
  - dates au format AMERICAIN (MM/DD/YYYY)
  - montants en CENTIMES (unit_price_cents)
  - ~2 % de DOUBLONS exacts (lignes répétées)
  - quelques lignes invalides (sku vide, qty négative, date impossible)
  - 1 fichier volontairement CORROMPU (en-têtes inconnues + lignes tronquées)

Produit dans starter-kit/data/marketplace/ :
  marketplace_2026-07-01.csv, marketplace_2026-07-02.csv,
  marketplace_2026-07-03_corrompu.csv

Usage : python3 generate_marketplace.py [--jours 2] [--lignes 2000] [--seed 7]
Aucune dépendance externe (stdlib uniquement).
"""

import argparse
import csv
import logging
import random
import sys
from datetime import date, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_marketplace")

PREMIER_JOUR = date(2026, 7, 1)
PARTENAIRES = ["LivresExpress", "PagesEnLigne", "BouquinMarket", "LireDemain"]
COLONNES = ["order_ref", "order_date", "sku", "qty", "unit_price_cents",
            "customer_uid", "partner_name"]


def isbn(rng):
    i = rng.randint(1, 12000)
    return f"978-2-{1000 + i // 10:04d}-{i % 10000:04d}-{i % 10}"


def generer_fichier(rng, jour, nb_lignes, dossier):
    lignes, seq = [], 0
    for _ in range(nb_lignes):
        seq += 1
        ligne = {
            "order_ref": f"MKT-{jour.strftime('%Y%m%d')}-{seq:05d}",
            "order_date": jour.strftime("%m/%d/%Y"),           # format US, à homogénéiser
            "sku": isbn(rng),
            "qty": rng.choices([1, 2, 3], weights=[85, 12, 3])[0],
            "unit_price_cents": rng.randint(500, 4500),        # centimes, à convertir
            "customer_uid": f"CLI-{rng.randint(1, 4500):06d}",
            "partner_name": rng.choice(PARTENAIRES),
        }
        lignes.append(ligne)
        if rng.random() < 0.02:                                # ~2 % de doublons exacts
            lignes.append(dict(ligne))

    # Quelques lignes invalides à rejeter et tracer (motifs variés)
    lignes[10]["sku"] = ""                                     # sku manquant
    lignes[25]["qty"] = -2                                     # quantité négative
    lignes[40]["order_date"] = "13/45/2026"                    # date impossible
    lignes[55]["unit_price_cents"] = "n/a"                     # montant non numérique

    chemin = dossier / f"marketplace_{jour.isoformat()}.csv"
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        w.writerows(lignes)
    log.info("écrit %s (%d lignes dont doublons/invalides)", chemin, len(lignes))


def generer_fichier_corrompu(dossier):
    """Fichier livré un jour de panne côté DSI : en-têtes inattendues et
    lignes tronquées. Doit déclencher journalisation ERREUR + alerte e-mail."""
    chemin = dossier / "marketplace_2026-07-03_corrompu.csv"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("ref;date;produit\n")           # mauvais séparateur ET mauvaises colonnes
        f.write("MKT-BROKEN-1;07/03/2026\n")
        f.write("\x00\x00???donnees_binaires???\x00\n")
    log.info("écrit %s (fichier volontairement corrompu)", chemin)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jours", type=int, default=2, help="nombre de fichiers quotidiens valides")
    parser.add_argument("--lignes", type=int, default=2000, help="lignes par fichier")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--dossier", default=str(Path(__file__).parent / "data" / "marketplace"))
    args = parser.parse_args()

    rng = random.Random(args.seed)
    dossier = Path(args.dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    try:
        for j in range(args.jours):
            generer_fichier(rng, PREMIER_JOUR + timedelta(days=j), args.lignes, dossier)
        generer_fichier_corrompu(dossier)
        log.info("génération marketplace terminée")
    except OSError as exc:
        log.error("échec de la génération : %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
