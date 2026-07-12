# Semaine 03 — Mini-analyse statistique des ventes (mission hebdomadaire)

> Module Mathématiques · Durée : ~1 jour · Modalité : solo · Compétence : C5 (analyses exploratoires / statistiques descriptives) niv.1 — remise à niveau

## Contexte (court, retail Nord)

Le contrôleur de gestion de **NordRetail** a posé une question simple sur le tchat de l'équipe : *« On vend combien en moyenne par jour et par magasin ? Et pourquoi certaines journées semblent complètement à côté de la plaque ? »* Avant de sortir un dashboard, on a besoin de **chiffres solides** : tendance centrale, dispersion, et repérage des valeurs aberrantes. C'est ton job cette semaine.

## Objectif de la mission

Mener une analyse statistique descriptive **de bout en bout** sur les ventes propres, et **traduire les résultats en langage métier** pour le contrôleur de gestion.

## Consignes (étapes claires)

1. **Charge** `ventes_magasins.csv` avec pandas et explore-le : nombre de lignes, colonnes, types, valeurs manquantes (`.info()`, `.describe()`, `.head()`).
2. **Tendance centrale** : calcule la **moyenne, la médiane et le mode** du montant des ventes. Compare moyenne et médiane : la distribution est-elle symétrique ou tirée par des valeurs extrêmes ?
3. **Dispersion** : calcule l'**étendue, la variance, l'écart-type** et les **quartiles (Q1, Q3, IQR)**.
4. **Distribution** : trace un **histogramme** et un **boxplot** du montant des ventes (matplotlib/seaborn).
5. **Outliers** : applique la **règle de l'IQR** — toute valeur hors de `[Q1 − 1,5·IQR ; Q3 + 1,5·IQR]` est aberrante. Compte combien il y en a et liste-les.
6. **Interprétation métier** : rédige 5-8 lignes répondant à la question du contrôleur. Qu'est-ce qu'une journée « normale » ? Faut-il garder ou écarter les outliers, et pourquoi (promo exceptionnelle ? erreur de saisie ?) ? Quel indicateur (moyenne ou médiane) recommandes-tu pour le reporting et pourquoi ?

## Données (référence)

`../data/ventes_magasins.csv` — jeu de ventes **propre** (pas de nettoyage lourd requis cette semaine, on se concentre sur la stat).

## Livrable attendu

Un **notebook Jupyter** (`.ipynb`) exécuté de haut en bas, avec : le code commenté, les 2 graphiques (histogramme + boxplot), un tableau récapitulatif des indicateurs, et la cellule Markdown d'interprétation métier. Export PDF ou HTML accepté en complément.

## Critères de réussite (OUI/NON)

- [ ] Moyenne, médiane ET mode sont calculés, et l'écart moyenne/médiane est commenté ?
- [ ] Écart-type, variance et IQR (Q1, Q3) sont présents ?
- [ ] L'histogramme ET le boxplot sont tracés, titrés et lisibles ?
- [ ] Les outliers sont détectés **par la règle de l'IQR** (pas « à l'œil ») et comptés ?
- [ ] L'interprétation répond explicitement à la question du contrôleur en langage métier ?
- [ ] Le notebook s'exécute sans erreur de haut en bas ?

## Ressources

- Cours : `cours/00-mathematiques/` (statistiques descriptives, IQR, z-score) + aide-mémoire « Statistiques descriptives » du skill data-analyst.
- [pandas — `describe()` & stats](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html)
- [seaborn — boxplot & histplot](https://seaborn.pydata.org/generated/seaborn.boxplot.html)
