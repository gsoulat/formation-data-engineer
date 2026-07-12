# Semaine 10 — Statistiques appliquées & segmentation client (mission hebdomadaire)

> Phase 2 — Solution BI pour analyse avancée · Module 2.1 · Durée : 1 à 2 jours · Modalité : binôme · Compétences : C5 (analyse exploratoire) niv. 2 · C6 (interpréter les tendances) niv. 2

## Contexte

NordRetail, enseigne retail des Hauts-de-France (magasins à Lille, Roubaix, Tourcoing, Valenciennes, Dunkerque…), veut mieux connaître sa clientèle avant de lancer une campagne de fidélisation. La direction marketing pose une question simple en apparence : « Qui sont nos meilleurs clients, et lesquels risque-t-on de perdre ? » Jusqu'ici, personne n'a fait parler les données de vente autrement qu'en additionnant le chiffre d'affaires.

## Objectif de la mission

Produire une analyse statistique avancée sur les ventes et les clients : décrire les distributions, mesurer des corrélations, et segmenter les clients par une analyse RFM (Récence, Fréquence, Montant) pour identifier les segments actionnables.

## Consignes (étapes)

1. Charge `Faits_Ventes.csv`, `Dim_Client.csv`, `Dim_Produit.csv` et `Dim_Date.csv` dans un notebook Python (pandas).
2. **Stats descriptives** : pour `montant`, `marge`, `quantite` et `remise`, calcule moyenne, médiane, écart-type, quartiles. Repère asymétrie et valeurs extrêmes (boxplot, histogramme).
3. **Corrélations** : construis une matrice de corrélation (ex. `quantite` vs `montant`, `remise` vs `marge`). Visualise-la (heatmap) et interprète : une corrélation forte est-elle causale ?
4. **Analyse RFM** : par `client_id`, calcule la Récence (jours depuis le dernier achat, date de référence = max des dates du jeu), la Fréquence (nb de ventes) et le Montant (somme `montant`). Attribue un score 1 à 5 sur chaque axe (quintiles), puis crée 3 à 5 segments lisibles (ex. « Champions », « Fidèles », « À risque », « Endormis »).
5. **Croisement métier** : relie les segments aux `segment` de `Dim_Client` (Particulier/Pro) et à la `ville`. Que constate-t-on ?
6. Rédige une synthèse de 5 à 8 enseignements chiffrés et orientés action.

## Données (../data/)

`Faits_Ventes.csv` · `Dim_Client.csv` · `Dim_Produit.csv` · `Dim_Date.csv` (schéma en étoile prêt à l'emploi).

## Livrable attendu

Un notebook (`.ipynb`) propre et commenté, exporté aussi en PDF ou HTML, contenant : les stats descriptives, la matrice de corrélation, le tableau RFM avec les segments, et une synthèse écrite (1/2 page) des recommandations marketing.

## Critères de réussite

- [ ] Les stats descriptives sont calculées et correctement interprétées (OUI/NON)
- [ ] Au moins une matrice de corrélation est produite et commentée sans confondre corrélation et causalité (OUI/NON)
- [ ] Les scores RFM (R, F, M) sont calculés par client avec une méthode justifiée (OUI/NON)
- [ ] Au moins 3 segments clients nommés et décrits sont obtenus (OUI/NON)
- [ ] Les segments sont croisés avec une dimension métier (segment ou ville) (OUI/NON)
- [ ] La synthèse propose des actions concrètes appuyées sur les chiffres (OUI/NON)

## Ressources (renvoi au cours)

Module 2.1 — Statistiques appliquées (distributions, corrélation, segmentation). Rappels EDA de la Phase 1. Documentation pandas (`describe`, `corr`, `qcut`).
