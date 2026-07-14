# 05 — Quiz & ressources

## Vidéos d'auto-formation

> Les liens YouTube ci-dessous ont été vérifiés. Les ressources LinkedIn Learning / éditeurs sont indiquées en lien vers leur page officielle.

| Titre | Chaîne / Plateforme | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Les différentes relations entre les tables dans la vue Modèle de Power BI Desktop | YouTube (FR) | FR | ~15 min | https://www.youtube.com/watch?v=fFrK3X5xHBY | Créer/configurer les relations, cardinalité et sens du filtre en pratique |
| Créer une table des dates en DAX dans Power BI ! | YouTube (FR) | FR | ~12 min | https://www.youtube.com/watch?v=XvUc-W-t1MI | Construire la dimension Date avec CALENDAR/ADDCOLUMNS et la marquer |
| Power BI : la modélisation des données (modèle en étoile) | LinkedIn Learning | FR | Cours | https://fr.linkedin.com/learning/power-bi-la-modelisation-des-donnees/connaitre-le-modele-en-etoile | Le modèle en étoile « idéal » pour Power BI, faits vs dimensions |
| Learn Data Modelling & Star Schema for Power BI in 20 minutes | YouTube (EN) | EN | ~20 min | https://www.youtube.com/watch?v=4ePNrdxWtY0 | Modèle sémantique, étoile, mise en œuvre concrète dans Power BI |
| Star Schema in 10 Minutes: The ONLY Explanation You Need! | YouTube (EN) | EN | ~10 min | https://www.youtube.com/watch?v=mPnnygpy2lY | Synthèse rapide et claire des concepts du schéma en étoile |

> Si un lien ne fonctionne plus, recherche le titre sur YouTube : https://www.youtube.com/results?search_query=star+schema+power+bi+modeling

---

## Quiz (5 QCM)

**Q1.** Dans un schéma en étoile, qu'est-ce qui se trouve au centre ?
- a) Une table de dimension
- b) La table de faits
- c) La table de dates
- d) Le rapport

**Q2.** Quelle affirmation décrit le mieux la **granularité** ?
- a) Le nombre de colonnes d'une dimension
- b) Ce que représente une ligne de la table de faits
- c) La vitesse de rafraîchissement
- d) Le nombre de relations du modèle

**Q3.** Quelle cardinalité est **recommandée** entre une table de faits et une dimension ?
- a) Plusieurs-à-plusieurs (\* : \*)
- b) Un-à-un (1 : 1)
- c) Plusieurs-à-un (\* : 1)
- d) Aucune relation

**Q4.** Pourquoi évite-t-on généralement le modèle en **flocon** dans Power BI ?
- a) Parce que Power BI ne sait pas créer de relations
- b) Parce qu'il est plus complexe et multiplie les relations, alors que l'étoile est plus simple et performante
- c) Parce qu'il interdit les tables de dates
- d) Parce qu'il supprime les clés primaires

**Q5.** Une relation passe en **plusieurs-à-plusieurs** alors que tu attendais \* : 1. Cause la plus probable ?
- a) La table de faits est trop grande
- b) Le sens du filtre est bidirectionnel
- c) La clé primaire de la dimension contient des doublons
- d) La table de dates n'est pas marquée

<details>
<summary>Voir les réponses</summary>

1. **b** — la table de faits est au centre de l'étoile.
2. **b** — la granularité = ce que représente une ligne des faits.
3. **c** — plusieurs-à-un (faits → dimension) est le cas normal.
4. **b** — l'étoile est plus simple et plus performante ; VertiPaq compresse bien les dimensions aplaties.
5. **c** — une clé de dimension non unique (doublons) empêche le côté « 1 ».
</details>

---

## À retenir

- On **sépare** ce qui se mesure (**faits**) de ce qui décrit (**dimensions**) : fini le fichier plat.
- Le **schéma en étoile** = 1 table de faits centrale + dimensions reliées en **\* : 1**. C'est **le** modèle recommandé pour Power BI.
- La **granularité** (ce que vaut une ligne de faits) est la décision clé : prends le **grain le plus fin** utile, et **un seul grain** par table.
- **PK unique** dans chaque dimension, **FK** dans les faits ; relie **sur des ID**, pas sur des libellés.
- **Évite le flocon** par défaut (aplatis tes dimensions) et **évite le many-to-many** subi (= doublons dans la dimension).
- Crée une **table de dates dédiée**, marque-la comme table de dates, désactive l'Auto Date/Time.
- Dans la **vue Modèle** : vérifie **cardinalité (\* : 1)** et **sens du filtre (unique)** ; le bidirectionnel se réserve aux cas précis.
- Un bon dashboard repose sur un bon modèle : **la modélisation est la fondation d'un bon tableau de bord.**
