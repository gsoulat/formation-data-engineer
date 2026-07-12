# Semaine 06 — Analyse exploratoire des ventes avec pandas (mission hebdomadaire)

> Phase 1 — Ajuster/analyser un tableau de bord métier · Module 1.2 (Analyse exploratoire) · Durée : ~1 à 2 jours · Modalité : binôme · Compétence C5 (Mener des analyses exploratoires) — niveau 1 (IMITER)

## Contexte (court, retail Nord)

NordRetail t'a confié l'export brut de ses ventes magasins (`ventes_magasins.csv`). Avant de calculer des KPI ou de construire un tableau de bord, la direction veut être sûre que les données sont saines : pas de trous, pas de valeurs aberrantes, des montants cohérents. C'est le rôle de l'analyse exploratoire (EDA) : prendre la température du jeu de données avant de l'exploiter.

Cette mission t'entraîne à l'analyse exploratoire en vue du projet de fin de phase (`brief-1-tableau-de-bord-metier.md`). Ce dernier porte sur un autre jeu de données (Online Retail / UCI) : tu ne réutiliseras pas directement ton EDA NordRetail, mais tu **transposeras** la démarche acquise ici sur cette nouvelle source. Cette transposition est volontaire et attendue au niveau RNCP.

## Objectif de la mission

Mener une EDA complète sur `ventes_magasins.csv` avec pandas : chargement, contrôle qualité, statistiques descriptives, agrégations par groupe et premières visualisations.

## Consignes (étapes)

1. **Charger.** `import pandas as pd` puis `df = pd.read_csv("ventes_magasins.csv", parse_dates=["date"])`. Affiche `df.shape`, `df.head()`, `df.dtypes`.
2. **Vue d'ensemble.** Lance `df.describe()` (numériques) et `df.describe(include="object")` (texte). Note la période couverte (`df["date"].min()` / `max()`).
3. **Qualité des données.** Mesure les valeurs manquantes (`df.isna().sum()`), les doublons (`df.duplicated().sum()`), et vérifie la cohérence : y a-t-il des `montant`, `quantite` ou `prix_unitaire` négatifs ou nuls ? Documente ce que tu trouves.
4. **Statistiques descriptives.** Pour `montant` et `quantite` : moyenne, médiane, écart-type, quartiles. La moyenne ou la médiane décrit-elle mieux le montant typique d'une ligne ? Pourquoi ?
5. **Agrégations (`groupby`).** Calcule le CA total (`montant`) :
   - par `ville` ;
   - par `categorie` ;
   - par `type` de point de vente (Magasin vs E-commerce).
   Utilise `df.groupby("ville")["montant"].sum().sort_values(ascending=False)`.
6. **Premières visualisations.** Produis au moins 3 graphiques (matplotlib ou pandas `.plot`) : un histogramme de `montant`, un bar chart du CA par ville, un bar chart du CA par catégorie. Donne un titre clair à chacun.
7. **Synthèse.** En 5 à 8 lignes, écris ce que tu as appris : qualité des données, ville/catégorie dominantes, présence d'éventuelles valeurs extrêmes.

## Données (fichier réel)

`../data/ventes_magasins.csv` — ~12 000 lignes. Colonnes : `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`.

## Livrable attendu

Un notebook `eda_ventes.ipynb` (ou script `.py`) exécuté de bout en bout, contenant le code, les 3+ graphiques et une cellule Markdown de synthèse.

## Critères de réussite (OUI/NON)

- Le fichier est chargé avec les bons types (`date` en datetime) : OUI / NON
- Valeurs manquantes et doublons sont mesurés et commentés : OUI / NON
- Moyenne, médiane et écart-type de `montant` sont calculés et interprétés : OUI / NON
- Au moins 3 agrégations `groupby` pertinentes sont produites (ville, catégorie, type) : OUI / NON
- Au moins 3 graphiques titrés sont générés : OUI / NON
- Une synthèse écrite résume les constats clés : OUI / NON

## Ressources (renvoi au cours)

- Cours module 1.2 — Analyse exploratoire / statistiques descriptives.
- Documentation pandas : https://pandas.pydata.org/docs/
- Rappels stats descriptives : https://fr.wikipedia.org/wiki/Statistique_descriptive
- Projet de fin de phase associé : `brief-1-tableau-de-bord-metier.md`.
