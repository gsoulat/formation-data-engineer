# Semaine 05 — Extraire les indicateurs de vente en SQL (mission hebdomadaire)

> Phase 1 — Ajuster/analyser un tableau de bord métier · Module 1.1 (Extraction de données) · Durée : ~1 jour · Modalité : binôme · Compétence C4 (Extraire des données via des scripts) — niveau 1 (IMITER)

## Contexte (court, retail Nord)

NordRetail, enseigne de distribution des Hauts-de-France (Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes, Amiens + un site e-commerce), veut moderniser son pilotage. Aujourd'hui, la direction commerciale réclame des chiffres à des fichiers Excel éparpillés. Première étape avant tout tableau de bord : savoir aller chercher les bons chiffres directement dans la base de données, avec des requêtes propres et reproductibles.

Cette mission t'entraîne sur la compétence d'extraction SQL en vue du projet de fin de phase (`BRIEF_1_TABLEAU_DE_BORD_METIER.md`). Le projet se déroule sur le **même univers NordRetail** (dossier `data/`) en scénario complet de bout en bout : tu y **réinvestiras et approfondiras** la démarche d'extraction acquise ici. Cette montée en autonomie est attendue au niveau RNCP.

## Objectif de la mission

Charger la base NordRetail puis écrire une dizaine de requêtes SQL qui extraient les indicateurs commerciaux clés : top produits, chiffre d'affaires par ville, par catégorie, et au moins une requête multi-tables avec jointures.

## Consignes (étapes)

1. **Monter la base.** Charge `../data/setup.sql` dans SQLite (le plus simple) :
   `sqlite3 nordretail.db < setup.sql`. Tu obtiens 4 tables : `magasins`, `produits`, `clients`, `commandes`.
2. **Reconnaître le schéma.** Liste les tables (`.tables`) et leurs colonnes (`.schema commandes`). Repère les clés étrangères de `commandes` vers `magasins`, `produits`, `clients`.
3. **Comptages de cadrage.** Compte les lignes de chaque table, la période couverte (`MIN(date)`, `MAX(date)`) et le CA total (`SUM(montant)`). Ces totaux te serviront de contrôle de cohérence.
4. **Top ventes.** Écris une requête qui sort le **top 10 des produits par CA** (`GROUP BY produit ORDER BY SUM(montant) DESC LIMIT 10`).
5. **CA par ville.** Agrège le CA par ville du magasin via une **jointure** `commandes` × `magasins` (`JOIN ... ON commandes.magasin_id = magasins.magasin_id`).
6. **CA par catégorie.** Jointure `commandes` × `produits`, agrégation par `categorie`, triée du plus gros au plus petit.
7. **Une requête plus riche.** Au choix : panier moyen par segment de client (jointure vers `clients`), ou CA mensuel (`strftime('%Y-%m', date)`).
8. **Versionner.** Range toutes tes requêtes dans un fichier `extraction.sql` commenté (un commentaire `-- Q1 : ...` par requête).

## Données (fichier réel)

`../data/setup.sql` — base NordRetail (tables `magasins`, `produits`, `clients`, `commandes` ; ~12 000 ventes, période 2023+).

## Livrable attendu

Un fichier `extraction.sql` (8 à 12 requêtes commentées) + un court `resultats.md` qui colle, pour chaque requête, les premières lignes du résultat et une phrase d'interprétation.

## Critères de réussite (OUI/NON)

- La base est chargée et les 4 tables sont interrogeables : OUI / NON
- Le top 10 des produits par CA est correct (tri décroissant) : OUI / NON
- Le CA par ville utilise une jointure `commandes` × `magasins` : OUI / NON
- Le CA par catégorie utilise une jointure `commandes` × `produits` : OUI / NON
- Au moins une requête combine 3 tables ou une agrégation temporelle : OUI / NON
- Les requêtes sont commentées et versionnées dans `extraction.sql` : OUI / NON

## Ressources (renvoi au cours)

- Cours module 1.1 — Extraction de données / SQL.
- Documentation SQLite : https://www.sqlite.org/docs.html
- Aide-mémoire SQL : `SELECT … FROM … JOIN … ON … GROUP BY … ORDER BY … LIMIT`.
- Projet de fin de phase associé : `BRIEF_1_TABLEAU_DE_BORD_METIER.md`.
