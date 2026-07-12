# Semaine 04 — Dataviz honnête vs trompeuse + un peu de proba (mission hebdomadaire)

> Module Mathématiques · Durée : ~1 jour · Modalité : solo · Compétences : C5 (stats/proba) socle · C17 (choisir des visualisations pertinentes) socle

## Contexte (court, retail Nord)

Le directeur marketing de **NordRetail** veut « un graphe qui montre que nos ventes explosent » pour le prochain comité. Toi, tu sais qu'un graphique peut **dire la vérité ou mentir** selon la façon dont on le construit. Ta mission : montrer concrètement la différence, pour armer l'équipe contre les visualisations malhonnêtes — les siennes comme celles des fournisseurs.

## Objectif de la mission

Produire **2 visualisations à partir des mêmes données** — une honnête, une trompeuse — expliquer les pièges, puis appliquer une **loi normale** à un calcul de probabilité simple sur les ventes.

## Consignes (étapes claires)

1. **Prépare les données** : charge `ventes_magasins.csv`, agrège les ventes par période (ex. par mois ou par magasin) pour obtenir une série comparable.
2. **Visualisation honnête** : un graphique en barres ou courbe avec **axe Y partant de 0**, titre neutre et factuel, échelle régulière.
3. **Visualisation trompeuse** : les **mêmes données**, mais avec **au moins 2 pièges** parmi : axe Y tronqué (ne partant pas de 0), échelle non linéaire/déformée, titre orienté, sélection partielle de la période, ordre des barres manipulé.
4. **Décryptage** : sous chaque graphique, écris 3-4 lignes expliquant le piège utilisé et **comment un lecteur peut le repérer**.
5. **Probabilité / loi normale** : à partir de la moyenne et de l'écart-type du montant des ventes (calculés semaine 3 ou recalculés), réponds avec `scipy.stats.norm` à : *« En supposant les ventes journalières approximativement normales, quelle est la probabilité qu'une journée dépasse X € ? »* (choisis un seuil X pertinent). Commente brièvement la limite de l'hypothèse de normalité (cf. ta distribution réelle observée).

## Données (référence)

`../data/ventes_magasins.csv` — jeu de ventes propre (le même qu'en semaine 3, pour réutiliser tes indicateurs).

## Livrable attendu

Un **notebook Jupyter** avec : les 2 graphiques côte à côte (ou successifs), le décryptage des pièges en Markdown, le calcul de probabilité commenté, et une mini-conclusion (3-4 lignes) : *« comment garder mes dataviz honnêtes en tant que Data Analyst »*.

## Critères de réussite (OUI/NON)

- [ ] Les 2 graphiques utilisent **exactement les mêmes données** ?
- [ ] La version honnête a un **axe Y à 0** et un titre neutre ?
- [ ] La version trompeuse contient **au moins 2 pièges** clairement identifiés (dont l'axe tronqué) ?
- [ ] Chaque piège est expliqué ET la méthode pour le repérer est donnée ?
- [ ] Le calcul de probabilité via la **loi normale** est correct et commenté (avec sa limite) ?
- [ ] Le notebook s'exécute sans erreur de haut en bas ?

## Ressources

- Cours : `cours/00-mathematiques/` (probabilités, loi normale) + aide-mémoire « Choisir le bon graphique » (C17) du skill data-analyst.
- [scipy.stats.norm — doc](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html)
- Vidéo/article « How to lie with charts » / livre *The Truth About Statistics* — pour repérer les axes tronqués et échelles trompeuses.
