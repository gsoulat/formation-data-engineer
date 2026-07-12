#!/usr/bin/env python3
"""
KIT DE DEMARRAGE — Générateur des 6 mois de données de l'entrepôt Bouquineo.

Produit dans starter-kit/data/ :
  - dim_temps.csv        : calendrier 2025-01-01 -> 2026-07-31
  - dim_client.csv       : ~4 500 clients (dont ~10 % inactifs depuis +3 ans, pour le volet RGPD)
  - dim_produit.csv      : ~12 000 références (prix APRES l'écrasement de mars — c'est le bug)
  - ventes.csv           : ~180 000 lignes de ventes du 2026-01-01 au 2026-06-30
  - scenario_prix.csv    : changements de prix datés du 2026-03-15 (anciennes + nouvelles valeurs)
  - scenario_segments.csv: changements de segment datés (anciennes + nouvelles valeurs)
  - quotidien/           : batch du jour suivant (2026-07-01) pour l'ETL nocturne
                           (ventes + mises à jour produits/clients à historiser)

Point clé pédagogique : les montants de ventes.csv sont calculés avec le prix
EN VIGUEUR au jour de la vente, mais dim_produit.csv ne contient que le prix
final (écrasé). Sans SCD2, la marge de mars est donc irrécupérable.

Usage : python3 generate_data.py [--dossier data] [--seed 42]
Aucune dépendance externe (stdlib uniquement).
"""

import argparse
import csv
import logging
import random
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_data")

# ----------------------------- Paramètres métier -----------------------------
DEBUT_CALENDRIER = date(2025, 1, 1)
FIN_CALENDRIER = date(2026, 7, 31)
DEBUT_VENTES = date(2026, 1, 1)
FIN_VENTES = date(2026, 6, 30)
DATE_CHANGEMENT_PRIX = date(2026, 3, 15)   # l'écrasement de mars
JOUR_SUIVANT = date(2026, 7, 1)            # batch quotidien pour l'ETL

NB_CLIENTS = 4500
NB_PRODUITS = 12000
NB_VENTES_CIBLE = 180000
NB_PRODUITS_CHANGEMENT_PRIX = 300
NB_CLIENTS_CHANGEMENT_SEGMENT = 120

SEGMENTS = ["occasionnel", "regulier", "premium"]
CATEGORIES = ["Roman", "Policier", "Science-fiction", "Jeunesse", "BD & Manga",
              "Essai", "Histoire", "Cuisine", "Développement personnel", "Poésie"]
VILLES = ["Lille", "Paris", "Lyon", "Marseille", "Toulouse", "Nantes", "Bordeaux",
          "Strasbourg", "Rennes", "Roubaix", "Amiens", "Arras"]
CANAUX = {"site_web": 1, "librairie": 2, "marketplace": 3}
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]
PRENOMS = ["Camille", "Louis", "Emma", "Hugo", "Léa", "Nathan", "Chloé", "Jules",
           "Manon", "Gabriel", "Inès", "Arthur", "Jade", "Adam", "Zoé", "Sacha"]
NOMS = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand",
        "Dubois", "Moreau", "Laurent", "Lefebvre", "Leroy", "Roux", "Vandenberghe"]
AUTEURS = ["A. Vasseur", "B. Lemoine", "C. Deconinck", "D. Aubry", "E. Carlier",
           "F. Delattre", "G. Wattel", "H. Blanchard", "I. Nowak", "J. Segard"]


def euros(valeur):
    """Arrondit proprement à 2 décimales (évite les flottants sales dans les CSV)."""
    return Decimal(str(valeur)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def isbn(i):
    return f"978-2-{1000 + i // 10:04d}-{i % 10000:04d}-{i % 10}"


def temps_id(d):
    return d.year * 10000 + d.month * 100 + d.day


def generer_calendrier():
    lignes, d = [], DEBUT_CALENDRIER
    while d <= FIN_CALENDRIER:
        lignes.append({
            "temps_id": temps_id(d), "date_jour": d.isoformat(), "annee": d.year,
            "trimestre": (d.month - 1) // 3 + 1, "mois": d.month,
            "nom_mois": MOIS_FR[d.month - 1], "jour": d.day,
            "jour_semaine": JOURS_FR[d.weekday()], "est_weekend": d.weekday() >= 5,
        })
        d += timedelta(days=1)
    return lignes


def generer_clients(rng):
    clients = []
    for i in range(1, NB_CLIENTS + 1):
        prenom, nom = rng.choice(PRENOMS), rng.choice(NOMS)
        inscription = DEBUT_CALENDRIER.replace(year=rng.randint(2015, 2025),
                                               month=rng.randint(1, 12), day=rng.randint(1, 28))
        # ~10 % de clients inactifs depuis plus de 3 ans -> candidats à la purge RGPD
        if rng.random() < 0.10:
            derniere = date(rng.randint(2016, 2023), rng.randint(1, 6), rng.randint(1, 28))
        else:
            derniere = date(2026, rng.randint(1, 6), rng.randint(1, 28))
        clients.append({
            "client_id": f"CLI-{i:06d}",
            "nom": f"{prenom} {nom}",
            "email": f"{prenom.lower()}.{nom.lower()}{i}@example.org",
            "ville": rng.choice(VILLES),
            "segment": rng.choices(SEGMENTS, weights=[50, 35, 15])[0],
            "date_inscription": inscription.isoformat(),
            "date_derniere_activite": derniere.isoformat(),
        })
    return clients


def generer_produits(rng):
    produits = []
    for i in range(1, NB_PRODUITS + 1):
        prix_achat = euros(rng.uniform(3.0, 22.0))
        marge = Decimal(str(rng.uniform(1.25, 1.85)))
        produits.append({
            "produit_id": isbn(i),
            "titre": f"Livre n°{i} — {rng.choice(CATEGORIES)}",
            "auteur": rng.choice(AUTEURS),
            "categorie": rng.choice(CATEGORIES),
            "prix_achat": prix_achat,
            "prix_vente": euros(prix_achat * marge),
        })
    return produits


def generer_scenario_prix(rng, produits):
    """Changements du 15 mars : anciennes ET nouvelles valeurs (indispensable
    pour reconstruire l'historique en SCD2 — les CSV dimensions ne contiennent
    que les valeurs écrasées)."""
    changements = []
    for p in rng.sample(produits, NB_PRODUITS_CHANGEMENT_PRIX):
        nouveau_achat = euros(Decimal(str(p["prix_achat"])) * Decimal(str(rng.uniform(1.05, 1.30))))
        nouveau_vente = euros(Decimal(str(p["prix_vente"])) * Decimal(str(rng.uniform(1.05, 1.25))))
        changements.append({
            "date_effet": DATE_CHANGEMENT_PRIX.isoformat(),
            "produit_id": p["produit_id"],
            "ancien_prix_achat": p["prix_achat"], "nouveau_prix_achat": nouveau_achat,
            "ancien_prix_vente": p["prix_vente"], "nouveau_prix_vente": nouveau_vente,
        })
        # dim_produit.csv reflète l'état APRES écrasement
        p["prix_achat"], p["prix_vente"] = nouveau_achat, nouveau_vente
    return changements


def generer_scenario_segments(rng, clients):
    changements = []
    for c in rng.sample(clients, NB_CLIENTS_CHANGEMENT_SEGMENT):
        nouveau = rng.choice([s for s in SEGMENTS if s != c["segment"]])
        changements.append({
            "date_effet": date(2026, rng.choice([2, 3, 4]), rng.randint(1, 28)).isoformat(),
            "client_id": c["client_id"],
            "ancien_segment": c["segment"], "nouveau_segment": nouveau,
        })
        c["segment"] = nouveau  # écrasé dans dim_client.csv
    return changements


def generer_ventes(rng, clients, produits, scenario_prix):
    """Montants calculés avec le prix en vigueur AU JOUR de la vente."""
    anciens_prix = {c["produit_id"]: Decimal(str(c["ancien_prix_vente"])) for c in scenario_prix}
    nb_jours = (FIN_VENTES - DEBUT_VENTES).days + 1
    ventes, vente_seq = [], 0
    for j in range(nb_jours):
        d = DEBUT_VENTES + timedelta(days=j)
        nb_jour = int(NB_VENTES_CIBLE / nb_jours * rng.uniform(0.7, 1.3))
        for _ in range(nb_jour):
            vente_seq += 1
            p = rng.choice(produits)
            prix_du_jour = Decimal(str(p["prix_vente"]))
            if p["produit_id"] in anciens_prix and d < DATE_CHANGEMENT_PRIX:
                prix_du_jour = anciens_prix[p["produit_id"]]
            qte = rng.choices([1, 2, 3], weights=[80, 15, 5])[0]
            ventes.append({
                "temps_id": temps_id(d),
                "client_id": rng.choice(clients)["client_id"],
                "produit_id": p["produit_id"],
                "canal_id": rng.choices([1, 2, 3], weights=[60, 30, 10])[0],
                "quantite": qte,
                "montant_ttc": euros(prix_du_jour * qte),
            })
    return ventes


def generer_batch_quotidien(rng, clients, produits, dossier):
    """Fichiers du 2026-07-01 pour faire tourner l'ETL nocturne (et, une fois
    le SCD2 en place, démontrer la création de nouvelles versions)."""
    quotidien = dossier / "quotidien"
    quotidien.mkdir(parents=True, exist_ok=True)

    maj_produits = []
    for p in rng.sample(produits, 5):
        maj_produits.append({
            "produit_id": p["produit_id"], "titre": p["titre"], "auteur": p["auteur"],
            "categorie": p["categorie"],
            "prix_achat": euros(Decimal(str(p["prix_achat"])) * Decimal("1.10")),
            "prix_vente": euros(Decimal(str(p["prix_vente"])) * Decimal("1.08")),
        })
    ecrire_csv(quotidien / f"produits_maj_{JOUR_SUIVANT.isoformat()}.csv", maj_produits)

    maj_clients = []
    for c in rng.sample(clients, 3):
        maj = dict(c)
        maj["segment"] = rng.choice([s for s in SEGMENTS if s != c["segment"]])
        maj_clients.append(maj)
    ecrire_csv(quotidien / f"clients_maj_{JOUR_SUIVANT.isoformat()}.csv", maj_clients)

    ventes_jour = []
    for _ in range(950):
        p = rng.choice(produits)
        qte = rng.choices([1, 2, 3], weights=[80, 15, 5])[0]
        ventes_jour.append({
            "temps_id": temps_id(JOUR_SUIVANT),
            "client_id": rng.choice(clients)["client_id"],
            "produit_id": p["produit_id"],
            "canal_id": rng.choices([1, 2], weights=[65, 35])[0],
            "quantite": qte,
            "montant_ttc": euros(Decimal(str(p["prix_vente"])) * qte),
        })
    ecrire_csv(quotidien / f"ventes_{JOUR_SUIVANT.isoformat()}.csv", ventes_jour)


def ecrire_csv(chemin, lignes):
    if not lignes:
        raise ValueError(f"aucune ligne à écrire dans {chemin}")
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)
    log.info("écrit %s (%d lignes)", chemin, len(lignes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", default=str(Path(__file__).parent / "data"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    dossier = Path(args.dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    try:
        clients = generer_clients(rng)
        produits = generer_produits(rng)
        scenario_prix = generer_scenario_prix(rng, produits)       # modifie produits (écrasement)
        scenario_segments = generer_scenario_segments(rng, clients)  # modifie clients (écrasement)
        ventes = generer_ventes(rng, clients, produits, scenario_prix)

        ecrire_csv(dossier / "dim_temps.csv", generer_calendrier())
        ecrire_csv(dossier / "dim_client.csv", clients)
        ecrire_csv(dossier / "dim_produit.csv", produits)
        ecrire_csv(dossier / "ventes.csv", ventes)
        ecrire_csv(dossier / "scenario_prix.csv", scenario_prix)
        ecrire_csv(dossier / "scenario_segments.csv", scenario_segments)
        generer_batch_quotidien(rng, clients, produits, dossier)
        log.info("génération terminée : %d ventes, %d clients, %d produits",
                 len(ventes), len(clients), len(produits))
    except (OSError, ValueError) as exc:
        log.error("échec de la génération : %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
