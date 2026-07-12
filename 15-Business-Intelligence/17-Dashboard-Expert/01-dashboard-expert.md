# 01 — Tableau de bord BI niveau expert

| | |
|---|---|
| **Titre** | Concevoir un tableau de bord BI complet, de bout en bout, au niveau expert |
| **Phase** | Phase 3 — Flux & restitution BI |
| **Durée indicative** | ~35 h |
| **Compétences visées** | **C16** (concevoir et réaliser un tableau de bord), **C17** (sélectionner et représenter les indicateurs), **C18** (rendre la restitution accessible et interactive) — **NIVEAU 3 (transposer)** |
| **Bloc** | **BC06** — cœur de la certification |
| **Pré-requis** | Tous les modules BI précédents : 1.4 (besoin métier & KPI), 2.1 (data viz & règles de représentation), 2.2 (modèle en étoile), 2.3 (DAX & mesures), 2.4 (interactivité & accessibilité de base), plus la chaîne ETL de la Phase 3 (3.1 à 3.4) |

> **Ce module est l'aboutissement de toute la formation BI.** Tu ne vas pas apprendre une nouvelle fonctionnalité isolée : tu vas **assembler, justifier et optimiser** tout ce que tu sais déjà pour livrer un tableau de bord directionnel professionnel, comme on l'attend d'un Data Analyst junior en poste.

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Mener une démarche projet complète** de conception de tableau de bord, du **besoin métier brut** jusqu'au livrable documenté — sans qu'on te dise quoi mettre dedans (c'est ça, le niveau 3).
2. **Traduire un besoin métier** en questions analytiques, puis en KPI, puis en visualisations, en **justifiant chaque maillon** de la chaîne.
3. **Intégrer tous tes acquis** : modèle en étoile propre, mesures DAX avancées (time intelligence, ratios, segmentation), interactivité (filtres, drill-through, signets, info-bulles), design cohérent.
4. **Optimiser la performance** d'un rapport : réduire le nombre de visuels, écrire des mesures efficaces, alléger le modèle de données.
5. **Rendre le tableau de bord accessible** selon les critères **WCAG** (contraste, navigation clavier, lecteurs d'écran, texte alternatif, ordre de tabulation).
6. **Raconter une histoire avec les données** (storytelling expert) : hiérarchie visuelle, parcours de lecture, page de synthèse → pages de détail.
7. **Documenter** ton tableau de bord (sources, modèle, mesures, choix de design, mode d'emploi).
8. **Justifier à l'oral et à l'écrit** chacun de tes choix face à un commanditaire — la compétence clé évaluée en certification.

---

## Pourquoi c'est l'aboutissement (certification BC06)

Le bloc **BC06** ne valide pas « savoir faire un graphique ». Il valide ta capacité à **transformer un besoin métier en outil de décision fiable, lisible et défendable**.

En certification, on ne te donnera pas une recette. On te donnera **un contexte et un besoin** (« la direction veut piloter la performance commerciale du réseau de magasins du Nord »). À toi de :

- décider **quels indicateurs** répondent vraiment au besoin (et écarter le superflu),
- décider **comment les représenter** (et pourquoi cette visualisation plutôt qu'une autre),
- décider **comment organiser** les pages et l'interactivité,
- **prouver** que ton rapport est performant, accessible et maintenable.

C'est exactement la différence entre les niveaux :

| Niveau | Ce qu'on attend | Exemple |
|---|---|---|
| **1 — Imiter** | Reproduire un dashboard fourni | « Refais ce rapport à l'identique » |
| **2 — Adapter** | Modifier un dashboard existant pour un nouveau cas | « Adapte ce rapport aux données 2025 » |
| **3 — Transposer** | **Tout concevoir à partir d'un simple besoin, et le justifier** | « La direction veut piloter ses ventes. Conçois l'outil. » |

> **Ce module t'entraîne au niveau 3.** Si tu sais justifier chaque choix, tu as la certification.

---

## Contenu

### La démarche projet complète (le fil conducteur)

Un tableau de bord expert ne se construit pas en ouvrant Power BI et en glissant des champs. Il suit un **enchaînement projet** en 7 étapes. Garde cette grille en tête : c'est elle qu'on évalue.

```
1. CADRAGE        → Quel besoin ? Quel public ? Quelle décision à prendre ?
2. INDICATEURS    → Quelles questions analytiques ? Quels KPI ? Quelles cibles ?
3. DONNÉES        → Quelles sources ? Quel modèle en étoile ? Quelle granularité ?
4. MESURES        → Quelles mesures DAX ? (time intelligence, ratios, segmentation)
5. MAQUETTE       → Quelles pages ? Quelle hiérarchie ? Quel parcours de lecture ?
6. RÉALISATION    → Visuels, interactivité, design, accessibilité
7. OPTIMISATION & DOC → Performance, accessibilité WCAG, documentation, justification
```

#### Étape 1 — Cadrage du besoin

Avant tout, réponds à trois questions :

- **Qui** va utiliser le dashboard ? (direction générale ? responsable de magasin ? marketing ?) → ça change tout : un directeur veut une vue synthétique, un opérationnel veut le détail.
- **Quelle décision** doit-il prendre grâce à ce dashboard ? Un bon KPI est un indicateur qui **déclenche une action**.
- **À quelle fréquence** et **sur quel support** (écran de réunion, mobile, export PDF) ?

> 💡 **Méthode** : reformule le besoin en une phrase « En tant que [rôle], je veux [voir quoi] afin de [décider quoi] ». Si tu n'arrives pas à remplir le « afin de », l'indicateur est probablement inutile.

#### Étape 2 — Du besoin aux indicateurs (chaîne de justification)

C'est le cœur du niveau 3. Tu dois construire une **chaîne traçable** :

```
Besoin métier → Question analytique → KPI → Cible/seuil → Visualisation
```

Exemple sur le fil rouge retail :

| Besoin | Question | KPI | Cible | Visualisation |
|---|---|---|---|---|
| Piloter le CA | Le CA progresse-t-il vs l'an dernier ? | CA, **% évolution YoY** | +5 % | Carte KPI + sparkline |
| Surveiller la marge | La rentabilité tient-elle ? | **Taux de marge %** | ≥ 32 % | Jauge + carte |
| Identifier les magasins en difficulté | Quels magasins sous-performent ? | CA par magasin vs objectif | objectif atteint | Barres + écart à l'objectif |
| Comprendre le mix produit | Quelles familles tirent les ventes ? | CA par catégorie | — | Barres empilées |
| Anticiper la saisonnalité | Quand vendons-nous le plus ? | CA par mois | — | Courbe |

> **Règle d'or des KPI** : **5 à 7 indicateurs clés maximum** sur la page principale. Un dashboard qui veut tout montrer ne montre rien.

#### Étape 3 — Modèle de données (rappel intégrateur)

Ton dashboard ne vaut que par son modèle. Rappel des exigences niveau expert :

- **Schéma en étoile** : une table de faits (`Ventes`) entourée de dimensions (`Date`, `Magasin`, `Produit`, `Client`). Pas de flocon inutile, pas de tables en doublon.
- **Table de dates dédiée** marquée comme « table de dates », indispensable pour la **time intelligence** DAX.
- **Granularité maîtrisée** : la table de faits est à la maille la plus fine utile (ligne de ticket), les agrégations se font via les mesures.
- **Relations propres** : 1 (dimension) → * (faits), sens de filtrage simple, pas de relations bidirectionnelles sauf nécessité justifiée.

> ⚠️ **Erreur courante** : importer une grosse table « à plat » (un seul fichier Excel avec tout dedans). Ça gonfle le modèle, ralentit les mesures et casse la time intelligence. **Toujours modéliser en étoile.**

#### Étape 4 — Mesures DAX avancées

Le niveau expert se voit dans les mesures. Tu dois maîtriser au minimum :

- **Mesures de base** : `CA = SUM(Ventes[montant])`, `Quantité`, `Nb tickets`.
- **Ratios** : `Taux de marge % = DIVIDE([Marge], [CA])` — **toujours `DIVIDE`** (gère la division par zéro).
- **Time intelligence** :
  - `CA N-1 = CALCULATE([CA], SAMEPERIODLASTYEAR('Date'[Date]))`
  - `Évolution YoY % = DIVIDE([CA] - [CA N-1], [CA N-1])`
  - `Cumul annuel (YTD) = TOTALYTD([CA], 'Date'[Date])`
- **Mesures avec variables** (lisibilité + performance) :

```dax
Évolution YoY % =
VAR CaActuel = [CA]
VAR CaPrec   = [CA N-1]
RETURN DIVIDE( CaActuel - CaPrec, CaPrec )
```

> 💡 **Bonne pratique** : range toutes tes mesures dans une **table de mesures dédiée** (table vide servant de dossier). Ça structure le modèle et facilite la maintenance.

#### Étape 5 — Maquette & storytelling

Avant de glisser le moindre visuel, **dessine ta maquette** (papier ou outil). Tu organises un **parcours de lecture**.

**Structure type d'un dashboard directionnel multi-pages :**

1. **Page 1 — Synthèse / vue d'ensemble** : les 5-7 KPI clés en haut (cartes), une tendance, une répartition. C'est la page qu'un directeur regarde 30 secondes.
2. **Page 2 — Analyse géographique** : performance par magasin / région (carte, classement).
3. **Page 3 — Analyse produit** : familles, top/flop produits.
4. **Page 4 — Analyse temporelle** : saisonnalité, tendances, comparaisons.
5. **(optionnel) Page de détail / drill-through** : niveau ticket, masquée, accessible par clic.

**Principes de storytelling visuel :**

- **Hiérarchie en Z** : l'œil lit de haut-gauche à bas-droite. Mets l'info la plus importante en **haut à gauche**.
- **Du général au détail** : synthèse d'abord, détail ensuite (parcours guidé via drill-through et signets).
- **Un message par page** : chaque page répond à **une** question.
- **Cohérence** : même police, même palette, même position des titres sur toutes les pages.

#### Étape 6 — Réalisation : interactivité & design

Les leviers d'interactivité experte :

- **Segments (slicers)** : période, magasin, catégorie — synchronisés entre pages.
- **Filtres** : niveau visuel / page / rapport selon le besoin.
- **Interactions entre visuels** : un clic sur un magasin filtre les autres visuels (ou pas — à configurer via *Modifier les interactions*).
- **Drill-down / drill-through** : descendre dans une hiérarchie (Année→Trimestre→Mois) ou aller vers une page de détail.
- **Signets (bookmarks)** : créer des « vues » (ex. bouton « réinitialiser les filtres », ou basculer entre deux affichages).
- **Info-bulles personnalisées** (tooltip pages) : afficher un mini-graphique au survol.

Règles de **design** :

- Palette de **2-3 couleurs** + nuances. Une couleur d'accent pour l'essentiel.
- Couleurs **sémantiques** : vert = bon, rouge = alerte — **mais jamais le rouge/vert seuls** (daltonisme).
- Espaces blancs : ne sature pas. Aligne tout sur une grille.
- Titres explicites et **orientés insight** (« Le CA progresse de +6 % » plutôt que « CA »).

#### Étape 7 — Optimisation, accessibilité, documentation

##### a) Performance

C'est une compétence experte attendue. Les leviers, du plus impactant au moins impactant :

1. **Réduire le nombre de visuels par page** : vise **≤ 8 visuels**. Chaque visuel = une ou plusieurs requêtes.
2. **Alléger le modèle** :
   - supprimer les colonnes inutiles,
   - préférer **Import** (moteur compressé VertiPaq) à DirectQuery quand c'est possible,
   - bons types de données, peu de colonnes à forte cardinalité.
3. **Écrire des mesures efficaces** :
   - mesures plutôt que colonnes calculées,
   - `DIVIDE` au lieu de `/`,
   - variables (`VAR`) pour ne pas recalculer deux fois la même chose,
   - éviter `FILTER` sur une table entière quand un filtre simple suffit.
4. **Limiter le formatage conditionnel** lourd et les visuels personnalisés gourmands.
5. **Utiliser l'Analyseur de performances** (Performance Analyzer) de Power BI Desktop : il chronomètre chaque visuel et identifie les goulots.

> ⚠️ **Erreur courante** : empiler 20 visuels « parce que c'est joli ». Le rapport rame, le message se dilue. **Moins de visuels = plus rapide ET plus lisible.**

##### b) Accessibilité WCAG

Un dashboard expert est **utilisable par tous**. Checklist :

- **Contraste** : ratio ≥ **4,5:1** entre texte et fond (outil : WebAIM Contrast Checker).
- **Ne jamais coder l'info par la couleur seule** : ajoute icônes, libellés, formes.
- **Texte alternatif (alt text)** sur chaque visuel pertinent (lu par les lecteurs d'écran).
- **Ordre de tabulation** logique (volet *Sélection* → *Ordre des onglets*).
- **Navigation au clavier** possible (Tab, Entrée, flèches).
- **Titres et libellés** clairs, taille de police lisible (≥ 12 pt).
- **Thème accessible** : Power BI propose des thèmes haute lisibilité.

##### c) Documentation

Tu livres toujours une **documentation** avec le rapport :

- **Sources de données** et fréquence de rafraîchissement.
- **Schéma du modèle** (capture du modèle en étoile).
- **Dictionnaire des mesures** : nom, formule DAX, signification métier.
- **Choix de design** justifiés (pourquoi ces KPI, ces visuels, cette organisation).
- **Mode d'emploi** : comment utiliser les filtres, le drill-through.

---

### 🧩 Encadré récapitulatif — Les 6 erreurs qui font perdre des points en certification

| Erreur | Conséquence | Le réflexe expert |
|---|---|---|
| Choisir un graphique « parce qu'il est beau » | Choix non justifiable | Justifier : « courbe car évolution temporelle » |
| 20 KPI sur la page d'accueil | Illisible, pas de message | 5-7 KPI max, hiérarchisés |
| Table à plat au lieu d'étoile | Modèle lent, time intelligence cassée | Modèle en étoile + table de dates |
| Rouge/vert sans icône | Inaccessible (daltonisme) | Couleur **+** forme/libellé |
| Aucun alt text, contraste faible | Échec WCAG | Contraste ≥ 4,5:1, alt text partout |
| « C'est fait, je rends » sans doc | Non maintenable, non défendable | Documenter + justifier chaque choix |

---

## Quiz d'auto-évaluation (5 QCM)

**Q1.** Au niveau 3 (transposer), qu'attend-on principalement de toi ?
- A) Reproduire à l'identique un dashboard fourni
- B) Concevoir un dashboard à partir d'un simple besoin métier et justifier chaque choix
- C) Modifier un dashboard existant pour de nouvelles données
- D) Apprendre une nouvelle fonction DAX

**Q2.** Combien de KPI clés afficher au maximum sur une page de synthèse directionnelle ?
- A) Le plus possible
- B) Entre 5 et 7
- C) Exactement 12
- D) Un seul

**Q3.** Quel est le levier le plus impactant pour améliorer la performance d'une page ?
- A) Changer la couleur de fond
- B) Réduire le nombre de visuels sur la page
- C) Ajouter des info-bulles
- D) Mettre plus de texte

**Q4.** Pour respecter l'accessibilité WCAG, le contraste texte/fond doit être au minimum de :
- A) 1:1
- B) 2:1
- C) 4,5:1
- D) 10:1

**Q5.** Pourquoi range-t-on les KPI selon une lecture « en Z » ?
- A) Pour faire joli
- B) Parce que l'œil lit naturellement de haut-gauche vers bas-droite : on met l'essentiel en haut à gauche
- C) Parce que Power BI l'impose
- D) Pour économiser de la mémoire

<details>
<summary>👉 Voir les réponses</summary>

1. **B** — Transposer = concevoir et justifier à partir du besoin.
2. **B** — 5 à 7 KPI clés, hiérarchisés.
3. **B** — Moins de visuels = moins de requêtes = plus rapide (et plus lisible).
4. **C** — Ratio de contraste minimum 4,5:1.
5. **B** — La hiérarchie en Z suit le parcours naturel de lecture.

</details>

---

## TP / Projet guidé

> Ces TP s'enchaînent : ils construisent **un seul dashboard directionnel retail Nord** de A à Z. C'est ta répétition générale avant le brief certificatif.

### TP 1 — Cadrage & chaîne de justification (≈ 4 h)

**Contexte** : La direction d'une enseigne retail du Nord (12 magasins, Lille, Roubaix, Tourcoing, Valenciennes…) veut « un outil pour piloter la performance commerciale ». C'est tout ce qu'on te dit. À toi de transposer.

**À faire** :
1. Identifier le **public** et la **décision** à prendre.
2. Produire le tableau de la **chaîne de justification** : Besoin → Question → KPI → Cible → Visualisation (minimum 6 lignes).
3. Esquisser la **maquette papier** des pages (4 pages minimum).

<details>
<summary>📋 Attendus & grille (TP1)</summary>

| Critère | Indicateurs de réussite |
|---|---|
| Cadrage | Public et décision identifiés et cohérents |
| Chaîne de justification | ≥ 6 KPI, chaque KPI relié à une question métier et une visualisation justifiée |
| Pertinence KPI | KPI actionnables (pas de « vanity metrics ») |
| Maquette | 4 pages, parcours synthèse→détail, hiérarchie en Z |
| Niveau 3 | Aucune visualisation imposée : tout est **choisi et justifié** par l'apprenant |

</details>

### TP 2 — Modèle en étoile & mesures DAX (≈ 8 h)

**À faire** :
1. Charger et nettoyer les sources (ventes, magasins, produits, calendrier).
2. Construire le **modèle en étoile** + table de dates marquée.
3. Créer une **table de mesures dédiée**.
4. Écrire au minimum : CA, Marge, Taux de marge %, CA N-1, Évolution YoY %, CA YTD, CA par magasin vs objectif.

<details>
<summary>📋 Attendus & grille (TP2)</summary>

| Critère | Indicateurs de réussite |
|---|---|
| Modèle | Étoile propre, relations 1→*, table de dates marquée |
| Granularité | Faits à la maille fine, agrégations par mesures |
| Mesures de base | CA, Marge, Quantité corrects |
| Mesures avancées | YoY, YTD via time intelligence fonctionnelles |
| Robustesse | `DIVIDE` partout, variables utilisées |
| Maintenabilité | Mesures regroupées, nommées clairement |

</details>

### TP 3 — Réalisation, interactivité & design (≈ 12 h)

**À faire** :
1. Construire les 4 pages selon la maquette.
2. Page 1 : cartes KPI + tendance + répartition.
3. Ajouter segments synchronisés, drill-through vers une page de détail, au moins 1 signet, 1 info-bulle personnalisée.
4. Appliquer un **design cohérent** (palette, titres orientés insight, alignement sur grille).

<details>
<summary>📋 Attendus & grille (TP3)</summary>

| Critère | Indicateurs de réussite |
|---|---|
| Lisibilité page 1 | 5-7 KPI hiérarchisés, message clair en < 30 s |
| Choix de visuels | Chaque visuel justifiable (courbe=temps, barres=comparaison…) |
| Interactivité | Segments synchronisés + drill-through + signet + tooltip fonctionnels |
| Storytelling | Parcours synthèse→détail cohérent, 1 message/page |
| Design | Palette maîtrisée, titres orientés insight, cohérence inter-pages |

</details>

### TP 4 — Optimisation, accessibilité & documentation (≈ 8 h)

**À faire** :
1. Lancer l'**Analyseur de performances**, identifier et corriger le visuel le plus lent ; réduire à ≤ 8 visuels/page.
2. Passer la **checklist WCAG** : contraste ≥ 4,5:1, alt text, ordre de tabulation, info non codée par la couleur seule.
3. Rédiger la **documentation** : sources, schéma du modèle, dictionnaire des mesures, justification des choix, mode d'emploi.
4. Préparer une **soutenance de 5 min** : présenter et **justifier** le dashboard à la « direction ».

<details>
<summary>📋 Attendus & grille (TP4)</summary>

| Critère | Indicateurs de réussite |
|---|---|
| Performance | Analyseur lancé, goulot corrigé, ≤ 8 visuels/page, mesures efficaces |
| Accessibilité | Contraste OK, alt text présents, tabulation logique, pas d'info couleur-seule |
| Documentation | Sources + modèle + dictionnaire mesures + justifs + mode d'emploi |
| Soutenance | Chaque choix (KPI, visuel, design) justifié face au commanditaire |
| Niveau 3 global | L'apprenant défend l'ensemble de sa démarche de bout en bout |

</details>

---

## Vidéos d'auto-formation

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Créez un Tableau de Bord Professionnel avec Power BI — Guide Complet de A à Z | (FR, 2025) | 🇫🇷 | ~1 h | https://www.youtube.com/watch?v=Kk6QtM8dWus | Concevoir un dashboard pro de bout en bout, étape par étape |
| Power BI : la formation complète de A à Z | (FR, 2025) | 🇫🇷 | long | https://www.youtube.com/watch?v=m43FEBFLicA | Démarche projet complète : modèle, mesures, visuels, mise en forme |
| How to Build Power BI Reports from Start to Finish | YouTube | 🇬🇧 | ~moyen | https://www.youtube.com/watch?v=Z2t7l8b1uWU | Construire un rapport de zéro jusqu'au livrable |
| Power BI Beginner's / advanced tutorials | Guy in a Cube | 🇬🇧 | série | https://www.youtube.com/guyinacube | Best practices, performance, modélisation (référence mondiale Power BI) |
| Power BI Report Design Series | YouTube (playlist) | 🇬🇧 | série | https://www.youtube.com/playlist?list=PLcwrIWK7WBcToAJA_Y6eY0hvCXM9S3p_- | Design de rapports, mise en page, storytelling visuel |

> Si un lien ne fonctionne plus, fais une recherche YouTube avec le titre exact ci-dessus.
> Ressources écrites de référence : [Design for accessibility (Microsoft Learn)](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) · [Performance best practices (Microsoft Learn)](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embedded-performance-best-practices).

---

## À retenir

- Le niveau 3, c'est **concevoir à partir d'un besoin** et **justifier chaque choix** — pas suivre une recette.
- Une **chaîne traçable** Besoin → Question → KPI → Cible → Visualisation est ton meilleur outil de justification.
- **5-7 KPI** par page de synthèse, **≤ 8 visuels** par page : moins, c'est plus (lisible **et** rapide).
- Tout repose sur un **modèle en étoile** propre + une **table de dates** + des **mesures DAX** avec `DIVIDE` et `VAR`.
- **Storytelling** : du général au détail, un message par page, hiérarchie en Z, titres orientés insight.
- **Performance** : réduire les visuels, alléger le modèle, mesures efficaces, Analyseur de performances.
- **Accessibilité WCAG** : contraste ≥ 4,5:1, jamais la couleur seule, alt text, navigation clavier.
- **Documenter** systématiquement : c'est ce qui rend ton travail maintenable et défendable.
