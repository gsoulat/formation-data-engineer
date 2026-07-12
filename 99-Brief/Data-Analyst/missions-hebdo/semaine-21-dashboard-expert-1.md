# Semaine 21 — Dashboard BI expert (1/2) : cadrage, modèle, première page (mission hebdomadaire)

> Phase 3 — module 3.5 (tableau de bord expert) · Durée : ~2 jours · Modalité : solo · Compétences : C16 (recueil du besoin), C17 (modélisation), C18 (conception du tableau de bord) niv.3

## Contexte (court, retail Nord)

Le comité de direction de NordRetail veut un **tableau de bord régional unique** pour piloter l'activité 2024 : CA, marge, atteinte des objectifs, classement des magasins, dynamique par catégorie. Cette fois, pas de cahier des charges détaillé : à toi de **cadrer le besoin en autonomie**, comme un analyste face à un sponsor pressé. C'est un livrable niveau expert (C16-C17-C18 niv.3), tu le mènes seul.

> **⚠️ Première mission en autonomie de niveau 3.** Jusqu'ici tu travaillais avec des consignes pas à pas (niveau 2). Ici, on te donne un objectif métier et tu décides du « comment ». C'est normal de se sentir un peu seul au départ — c'est exactement la compétence visée. Tu n'es pas lâché sans appui : suis la **checklist de démarrage** ci-dessous et réutilise tout ce que tu as déjà construit dans les missions précédentes. On ne te demande pas d'inventer des techniques nouvelles, mais de **piloter seul** des techniques que tu connais déjà.

### Checklist de démarrage (canevas de cadrage)

Avant d'ouvrir Power BI, déroule ces 4 étapes dans l'ordre — c'est le réflexe d'un analyste face à une demande floue :

1. **Recueil du besoin (C16).** Qui va utiliser le dashboard ? Quelles décisions doit-il aider à prendre ? Note 5-7 questions métier prioritaires. Si le sponsor est « pressé », formule des hypothèses raisonnables et assume-les par écrit.
2. **Définition des KPI.** Pour chaque question métier, associe 1 indicateur mesurable (CA, marge, taux d'atteinte, panier moyen...). Pas de KPI sans question derrière.
3. **Modèle de données (C17).** Esquisse le schéma en étoile sur papier *avant* de cliquer : table de faits au centre, dimensions autour, table de dates. Vérifie la granularité.
4. **Maquette de la page (C18).** Croquis rapide (papier ou outil) de la page 1 : où vont les KPI, l'évolution temporelle, le classement, le filtre. Pense hiérarchie visuelle avant de poser les visuels.

**Points d'appui — ce que tu peux réutiliser :** la modélisation en étoile et les mesures DAX vues en module 3.5 ; le travail de KPI/data-viz des missions de dashboard de niveau 2 (semaines précédentes) ; tes requêtes et ton merge objectifs de la **S20**. Reviens-y au lieu de repartir de zéro.

## Objectif de la mission

Démarrer un tableau de bord BI de niveau expert : **formaliser le besoin métier**, construire un **modèle de données propre** (étoile), et livrer une **première page** fonctionnelle avec les KPI clés.

## Consignes (étapes)

1. **Cadrage autonome.** Rédige une note de cadrage (½ page) : qui sont les utilisateurs, quelles décisions le dashboard doit éclairer, 5-7 questions métier prioritaires, et les **KPI** associés (CA, marge, taux d'atteinte objectif, panier moyen, top produits/magasins).
2. **Modélisation.** À partir des tables `Dim_*.csv` + `Faits_Ventes.csv`, construis un **modèle en étoile** dans l'outil BI (Power BI conseillé, Looker Studio accepté) : table de faits au centre, dimensions Date/Magasin/Produit/Client en rayon. Crée les relations et une **table de dates** marquée comme telle.
3. **Mesures.** Crée au moins 4 mesures (DAX ou équivalent) : `CA`, `Marge`, `Taux de marge %`, `Taux d'atteinte objectif` (via `objectifs_2024`).
4. **Page 1 — Vue d'ensemble.** Conçois la première page : bandeau de KPI (cartes), une évolution temporelle du CA, un classement des magasins, un filtre de période. Soigne la hiérarchie visuelle.
5. **Justifie tes choix** : 5 lignes expliquant le choix des KPI et du type de visuel pour chacun.

## Données (fichier réel)

`../data/Dim_Date.csv`, `Dim_Magasin.csv`, `Dim_Produit.csv`, `Dim_Client.csv`, `Faits_Ventes.csv`, `objectifs_2024.xlsx`.

## Livrable attendu

Le fichier `.pbix` (ou lien Looker Studio partagé), la note de cadrage, et une capture du modèle en étoile. Déposé sur la plateforme. **Tu poursuivras ce dashboard en S22 — garde-le propre et versionné.**

## Critères de réussite (OUI/NON)

- [ ] La **note de cadrage** identifie utilisateurs, décisions et 5+ questions métier ?
- [ ] Le modèle est en **étoile** (faits + dimensions) avec relations correctes ?
- [ ] Une **table de dates** dédiée est présente et marquée ?
- [ ] Au moins **4 mesures** dont le taux d'atteinte objectif fonctionnent ?
- [ ] La **page 1** présente KPI, évolution temporelle, classement et filtre période ?
- [ ] Les **choix de visuels** sont justifiés et la hiérarchie visuelle est lisible ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.5-dashboard-expert/`.
- Power BI : modèle en étoile, `CALCULATE`, `DIVIDE`, table de dates.
- Référentiel BC06 — compétences C16, C17, C18 (niv.3).
