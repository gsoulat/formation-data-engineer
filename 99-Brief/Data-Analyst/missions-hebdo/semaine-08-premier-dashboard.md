# Semaine 08 — Premier tableau de bord BI (mission hebdomadaire)

> Phase 1 — Ajuster/analyser un tableau de bord métier · Module 1.5 (Construction de tableau de bord) · Durée : ~2 jours · Modalité : binôme · Compétences C17 (Choisir des visualisations pertinentes) — niveau 1 → 2 ; C18 (Créer un tableau de bord BI) — niveau 1 → 2 (IMITER → ADAPTER)

## Contexte (court, retail Nord)

Tu as extrait (S5), exploré (S6) puis dégagé tendances et KPI (S7) des ventes de NordRetail. Il est temps de tout réunir dans un **tableau de bord** que la direction commerciale pourra lire « en 30 secondes ». Fini les exports Excel : un décideur ouvre le dashboard et comprend où en est l'activité.

Cette mission est la **répétition générale** du projet de fin de phase (`brief-1-tableau-de-bord-metier.md`, semaine 9) : tu y construiras un tableau de bord plus complet, accompagné d'une note d'analyse et d'une soutenance. Attention : le projet repose sur un autre jeu de données (Online Retail / UCI). Tu ne reprendras donc pas directement ce dashboard NordRetail ; tu **transposeras** sur la nouvelle source la démarche de construction travaillée ici. Cette transposition est volontaire et attendue au niveau RNCP.

## Objectif de la mission

Construire un premier tableau de bord BI à partir de `ventes_magasins.csv`, avec 4 à 5 visuels pertinents et au moins 1 filtre interactif, en t'appuyant sur les KPI définis en semaine 7.

## Consignes (étapes)

1. **Choisir l'outil.** Looker Studio recommandé (gratuit, partage par lien). Power BI Desktop accepté.
2. **Importer les données.** Charge `ventes_magasins.csv` comme source. Vérifie que `date` est bien typée en date et `montant`/`marge` en numérique.
3. **Bloc KPI en haut.** Place 3 à 4 **cartes** (scorecards) reprenant les KPI de la S7 : CA total, panier/ligne moyen, marge totale, nombre de ventes.
4. **Visuels d'analyse (4 à 5 au total).** Choisis le bon graphique selon l'intention :
   - **courbe** : CA par mois (tendance) ;
   - **barres** : CA par ville **et/ou** par catégorie (comparaison) ;
   - un visuel au choix : top produits, ou CA par `type` (Magasin vs E-commerce).
5. **Interactivité.** Ajoute au moins **1 filtre** (sélecteur de période, de ville ou de catégorie) qui met à jour tout le rapport.
6. **Soigner la lecture.** Titres explicites, axes non tronqués, palette lisible et accessible, pas de camembert surchargé ni de 3D inutile. L'info principale est en haut à gauche.
7. **Contrôle de justesse.** Compare le CA total affiché au total calculé en pandas (S6) : les chiffres doivent coïncider.
8. **Partage.** Looker Studio → lien public en lecture ; Power BI → fichier `.pbix`. Dans les deux cas, joins une **capture d'écran**.

## Données (fichier réel)

`../data/ventes_magasins.csv` — colonnes `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`.

## Livrable attendu

Le tableau de bord (lien public Looker Studio **ou** fichier `.pbix`) + une capture d'écran + un court `notes_dashboard.md` (3-5 lignes) justifiant le choix de chaque visuel et du filtre.

## Critères de réussite (OUI/NON)

- Le tableau de bord est construit dans Looker Studio ou Power BI à partir de `ventes_magasins.csv` : OUI / NON
- 3 à 4 cartes KPI sont affichées en évidence (lisibles en 30 s) : OUI / NON
- 4 à 5 visuels au total, chacun adapté à son intention (courbe/barres) : OUI / NON
- Au moins 1 filtre interactif fonctionne sur l'ensemble du rapport : OUI / NON
- Le CA total affiché correspond au total calculé en pandas : OUI / NON
- Titres, axes et palette sont soignés (pas de piège visuel) : OUI / NON

## Ressources (renvoi au cours)

- Cours module 1.5 — Construction de tableau de bord BI.
- Looker Studio (aide) : https://support.google.com/looker-studio
- Power BI (Microsoft Learn) : https://learn.microsoft.com/fr-fr/power-bi/
- Choisir le bon graphique : https://www.data-to-viz.com/
- **Aboutissement** : projet de fin de phase `brief-1-tableau-de-bord-metier.md` (semaine 9) — tableau de bord complet + note d'analyse + soutenance.
