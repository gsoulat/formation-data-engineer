#!/usr/bin/env python3
"""
KIT DE DEMARRAGE — L'ETL nocturne HERITE du prédécesseur. NE PAS AMELIORER
CE FICHIER : il représente l'existant que l'apprenant doit auditer puis
remplacer. Ses défauts sont volontaires et documentés dans le brief :

  1. mise à jour des dimensions PAR ECRASEMENT (ON CONFLICT DO UPDATE)
     -> c'est lui, le coupable de « la marge de mars est fausse » ;
  2. AUCUNE journalisation, AUCUNE alerte : s'il plante à 3 h du matin,
     personne ne le sait ;
  3. non idempotent : rejouer le même fichier de ventes crée des doublons ;
  4. gestion d'erreurs inexistante (le moindre problème stoppe tout,
     silencieusement du point de vue de l'équipe).

Usage : python3 etl_nocturne.py data/quotidien 2026-07-01
Dépendances : psycopg2-binary (connexion via variables d'environnement PG*).
"""

import csv
import sys

import psycopg2


def main(dossier, jour):
    conn = psycopg2.connect("")  # lit PGHOST/PGDATABASE/PGUSER/PGPASSWORD
    cur = conn.cursor()

    # 1. Mise à jour des produits — PAR ECRASEMENT (aucune trace de l'ancien prix)
    with open(f"{dossier}/produits_maj_{jour}.csv", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            cur.execute(
                """
                INSERT INTO entrepot.dim_produit (produit_id, titre, auteur, categorie, prix_achat, prix_vente)
                VALUES (%(produit_id)s, %(titre)s, %(auteur)s, %(categorie)s, %(prix_achat)s, %(prix_vente)s)
                ON CONFLICT (produit_id) DO UPDATE
                SET prix_achat = EXCLUDED.prix_achat,
                    prix_vente = EXCLUDED.prix_vente,
                    categorie  = EXCLUDED.categorie
                """,
                ligne,
            )

    # 2. Mise à jour des clients — PAR ECRASEMENT (le segment passé est perdu)
    with open(f"{dossier}/clients_maj_{jour}.csv", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            cur.execute(
                """
                INSERT INTO entrepot.dim_client (client_id, nom, email, ville, segment,
                                                 date_inscription, date_derniere_activite)
                VALUES (%(client_id)s, %(nom)s, %(email)s, %(ville)s, %(segment)s,
                        %(date_inscription)s, %(date_derniere_activite)s)
                ON CONFLICT (client_id) DO UPDATE
                SET segment = EXCLUDED.segment,
                    date_derniere_activite = EXCLUDED.date_derniere_activite
                """,
                ligne,
            )

    # 3. Chargement des ventes — non idempotent : rejouer = doublons
    with open(f"{dossier}/ventes_{jour}.csv", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            cur.execute(
                """
                INSERT INTO entrepot.fait_ventes (temps_id, client_id, produit_id, canal_id, quantite, montant_ttc)
                VALUES (%(temps_id)s, %(client_id)s, %(produit_id)s, %(canal_id)s, %(quantite)s, %(montant_ttc)s)
                """,
                ligne,
            )

    conn.commit()
    conn.close()
    print("ok")  # seule "supervision" existante...


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
