# 01 — Visualisations avancées & interactivité

| | |
|---|---|
| **Phase** | Phase 2 — BI avancée |
| **Durée estimée** | ~25 h |
| **Compétence visée** | **C17 — Réaliser des représentations visuelles de données** (niveau 2) |
| **Pré-requis** | Module 1.5 (Initiation à la dataviz : choisir le bon graphique, premiers visuels Power BI / Looker Studio) ; notions de modélisation (2.2) et de mesures DAX (2.3) recommandées |
| **Outils** | Power BI Desktop + Looker Studio (les deux sont décrits) |

> Fil rouge du module : tu pars d'un tableau de bord retail « brut » (ventes d'une enseigne du Nord — magasins Lille, Roubaix, Valenciennes, Dunkerque…) et tu le transformes en outil de pilotage **interactif, lisible et accessible**.

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Rendre un tableau de bord interactif** : filtres croisés, segments, drill-down / drill-through, signets (bookmarks), info-bulles personnalisées.
2. **Choisir et construire des visuels avancés** adaptés au message : treemap, jauge, carte géographique, graphique combiné, petits multiples.
3. **Mettre en page** un rapport selon les principes de design (grille, hiérarchie visuelle, thème, cohérence).
4. **Appliquer les règles d'accessibilité WCAG** à une dataviz : palettes adaptées au daltonisme, contraste suffisant, ordre de tabulation, texte alternatif, compatibilité lecteur d'écran.
5. **Optimiser la performance** d'un dashboard (limiter le nombre de visuels, alléger les requêtes).
6. **Repérer et éviter les visualisations trompeuses** (rappel des pièges vus en maths, ch. 6).

---

## Pourquoi c'est utile au Data Analyst ?

Un tableau de bord, ce n'est pas une galerie de graphiques : c'est un **outil de décision**. Le DA est souvent jugé non pas sur la donnée elle-même, mais sur la capacité de son public (direction, chef de rayon, marketing) à **comprendre et agir vite**.

- **L'interactivité** transforme un rapport figé en outil d'exploration : le directeur régional clique sur « Roubaix » et voit instantanément se recalculer ses KPI, puis « creuse » jusqu'au produit. Tu ne produis plus 12 rapports, tu en produis **un seul, paramétrable**.
- **Le design et l'accessibilité** ne sont pas du « décoratif » : un dashboard surchargé ou illisible n'est pas utilisé, donc inutile. Et l'accessibilité est une **obligation légale** (RGAA en France, transposition de WCAG) pour les organismes publics et de plus en plus exigée en entreprise.
- **La performance** : un rapport qui met 30 secondes à charger ne sera pas consulté. Savoir l'alléger fait partie du métier.
- **Éviter les visuels trompeurs** : la crédibilité du DA repose sur l'honnêteté de ses représentations. Un axe tronqué qui exagère une hausse, c'est ta réputation qui est en jeu.

C17 niveau 2 attend justement que tu ailles **au-delà du graphique simple** : interactivité, accessibilité et esprit critique sur la représentation.

---

## Contenu détaillé

### L'interactivité dans un tableau de bord

#### a) Segments et filtres croisés (cross-filtering)

Le **segment** (Power BI) / **contrôle de filtre** (Looker Studio) est un filtre cliquable posé sur le canevas. Le **filtrage croisé** est le comportement par défaut : cliquer sur un élément d'un visuel filtre les autres.

**Power BI — pas à pas**
1. Onglet **Insertion** ou volet **Visualisations** → icône **Segment**.
2. Glisse le champ (ex. `Magasin` ou `Catégorie`) dans le segment.
3. Mets-le en forme : liste, liste déroulante, ou « entre » pour les dates/nombres (en-tête du segment → flèche).
4. Filtrage croisé : sélectionne un visuel → onglet **Format** → **Modifier les interactions**. Sur chaque autre visuel apparaissent 3 icônes : **Filtrer** (entonnoir), **Mettre en surbrillance**, **Aucune**. Choisis le comportement souhaité.
5. **Sync segments** (multi-pages) : menu **Affichage → Synchroniser les segments** → coche les pages où le segment doit agir.

**Looker Studio — pas à pas**
1. Barre d'outils → **Ajouter une commande** → choisis le type (Liste déroulante, Case à cocher, Curseur, Période…).
2. Dans le panneau de droite, définis le **champ de contrôle** (ex. `Région`).
3. Par défaut, une commande filtre **tous les graphiques de la page reliés à la même source**. Pour restreindre la portée, sélectionne les éléments puis **Ressource → Gérer les groupes** ou utilise **Sélection groupée** (clic droit → Grouper).
4. Filtrage croisé : sélectionne le graphique → panneau de droite, onglet **Style** → coche **Appliquer un filtre croisé**. Les clics sur le graphique filtrent alors le reste.

> 🛒 **Exemple retail** — Tableau « Ventes enseigne Nord ». Un segment `Magasin` + un sélecteur de `Période`. Le chef de rayon sélectionne « Dunkerque » + « Mai 2026 » : CA, panier moyen, top produits se recalculent. En cliquant sur la barre « Boissons » de l'histogramme, le tableau détaillé ne montre plus que les boissons (filtrage croisé).

#### b) Drill-down (descente dans une hiérarchie)

Le drill-down permet de cliquer pour descendre un niveau : **Région → Ville → Magasin**, ou **Année → Trimestre → Mois**.

**Power BI**
1. Crée une **hiérarchie** : dans le volet Données, glisse un champ sur un autre (ex. `Ville` sur `Région`) → tu obtiens une hiérarchie.
2. Mets la hiérarchie dans l'axe du visuel.
3. Active les flèches de drill en haut à droite du visuel : **double flèche bas** = drill-down activé ; clic sur une barre = descend. La flèche **fourche** descend tous les éléments à la fois ; la flèche **double bas** remonte.

**Looker Studio**
1. Sélectionne le graphique → panneau de droite → section **Dimension** : ajoute plusieurs dimensions (ex. `Région`, `Ville`, `Magasin`).
2. Active **Exploration (Drill down)** (interrupteur sous les dimensions).
3. L'utilisateur clique droit sur un élément → **Explorer** ou utilise les flèches haut/bas du graphique.

> 🛒 **Exemple retail** — Histogramme du CA par `Région`. L'utilisateur clique sur « Hauts-de-France » → descend sur les villes → puis sur les magasins de Lille. Un seul visuel remplace trois.

#### c) Drill-through (extraction vers une page de détail)

Le drill-through fait passer d'une vue d'ensemble vers **une autre page** filtrée sur l'élément cliqué.

**Power BI — pas à pas**
1. Crée une page « Détail produit ».
2. Sur cette page, volet **Visualisations → Extraction (Drill through)** → glisse le champ qui servira de filtre d'entrée (ex. `Produit`).
3. Power BI ajoute automatiquement un **bouton retour** (flèche). Conserve-le.
4. Sur la page de synthèse, clic droit sur un point de donnée → **Extraire (Drill through) → Détail produit**. La page de détail s'ouvre filtrée sur ce produit.

**Looker Studio**
- Looker Studio n'a pas de « drill-through » natif identique. On le simule avec :
  - **Liens de page** : sélectionne un élément → ajoute un **lien** vers une autre page du rapport, ou
  - les **paramètres d'URL** / boutons de navigation entre pages, combinés à un filtre passé en paramètre.
- Alternative simple : une page « détail » avec un contrôle de filtre, et un bouton de navigation (Insérer → Bouton / forme avec action « Aller à la page »).

> 🛒 **Exemple retail** — Page synthèse : top 10 des produits. Clic droit sur « Bière artisanale 33cl » → drill-through → page « Fiche produit » : évolution mensuelle, marge, stock, magasins concernés, le tout filtré sur ce produit.

#### d) Signets (bookmarks)

Un signet **mémorise l'état d'une page** : filtres appliqués, visuels visibles, sélections. On l'utilise pour des **vues prédéfinies**, des **boutons de navigation** ou un **mode présentation**.

**Power BI — pas à pas**
1. **Affichage → Volet Signets** et **Volet Sélection** (pour gérer la visibilité des visuels).
2. Règle la page dans l'état voulu (filtres, visuels affichés).
3. Volet Signets → **Ajouter**. Renomme-le (ex. « Vue Direction »).
4. Options du signet (… ) : choisis ce qu'il mémorise — Données, Affichage, Page active, et « Tous les visuels » ou « Sélectionnés ».
5. Relier à un **bouton** : Insertion → Bouton → dans Format, **Action = Signet** → choisis le signet.

**Looker Studio**
- Pas de signets natifs. On reproduit l'idée avec :
  - **plusieurs pages** correspondant à chaque « vue »,
  - des **boutons de navigation**,
  - et, depuis la vue rapport, l'utilisateur peut **partager une URL incluant les filtres actifs** (le filtre est mémorisé dans l'URL).

> 🛒 **Exemple retail** — Trois signets : « Vue Direction » (synthèse régionale), « Vue Magasin » (détail), « Reset » (filtres effacés). Une barre de boutons permet de naviguer entre les vues pendant le comité de direction.

#### e) Info-bulles (tooltips) personnalisées

Au survol, une info-bulle affiche un complément d'info. On peut afficher une **page entière** en tooltip.

**Power BI — pas à pas**
1. Crée une page → **Format de la page → Informations sur la page → Type = Info-bulle** + règle la taille (petit format).
2. Construis-y un mini-visuel (ex. courbe de tendance du produit).
3. Sur le visuel principal : **Format → Info-bulle → Type = Page rapport →** choisis la page tooltip.
4. Pour une tooltip simple : glisse des champs dans le puits **Info-bulles** du visuel.

**Looker Studio**
- Active **Afficher l'info-bulle** dans le style du graphique. Le contenu reprend dimensions/métriques du graphique. Personnalisation plus limitée que Power BI (pas de page-tooltip).

> 🛒 **Exemple retail** — Survol d'une barre « Roubaix » → tooltip-page : évolution du CA sur 12 mois + marge + nombre de clients, sans quitter la vue d'ensemble.

> ⚠️ **Encadré — erreurs courantes (interactivité)**
> - **Tout filtrer en croisé** sans réfléchir : un clic involontaire « casse » la lecture. Désactive le filtrage croisé là où il n'a pas de sens.
> - Oublier le **bouton retour** d'une page drill-through → l'utilisateur est coincé.
> - Trop de segments : 5 segments visibles = page surchargée. Préfère un volet de filtres dépliable.
> - Signets qui mémorisent « Tous les visuels » par erreur → un signet écrase l'affichage d'autres pages. Vérifie l'option **Sélectionnés**.

---

### Les visuels avancés

| Visuel | Quand l'utiliser | Piège à éviter |
|---|---|---|
| **Treemap** | Montrer une part-de-tout hiérarchique avec beaucoup de catégories (ex. CA par catégorie/sous-catégorie) | Difficile de comparer des aires proches → pas pour des valeurs très voisines |
| **Jauge (gauge)** | Suivre **un** KPI vs une cible (ex. CA réalisé / objectif) | Une jauge = un chiffre ; n'en aligne pas 10, ça prend de la place pour peu d'info |
| **Carte géographique** | Données ayant une dimension spatiale (ventes par ville/département) | Carte de bulles trompeuse si l'aire n'est pas proportionnelle ; attention aux densités de population |
| **Graphique combiné** (barres + courbe) | Deux mesures d'échelles différentes (CA en barres, marge % en courbe) | Deux axes Y peuvent suggérer une corrélation qui n'existe pas |
| **Petits multiples** (small multiples) | Comparer la même métrique sur plusieurs catégories (un mini-graphe par magasin) | Trop de petits multiples = illisible ; garde la même échelle partout |

**Power BI**
- Treemap / Jauge / Carte / Combiné : disponibles directement dans le volet **Visualisations**.
- **Carte** : « Carte » (bulles) et « Carte choroplèthe (Map / Filled map) » ; renseigne un champ **Catégorie de données = Lieu/Ville/Pays** (onglet Modélisation) pour un géocodage fiable.
- **Petits multiples** : sur un graphique en barres/courbes, glisse un champ dans le puits **Petits multiples** (natif depuis 2021).

**Looker Studio**
- Treemap, Jauge, **Carte Google (carte de densité / à bulles / choroplèthe)**, graphique **combiné** : tous présents dans **Ajouter un graphique**.
- Cartes : s'appuie sur le géocodage Google ; renseigne le bon type de champ géographique (Ville, Région, Pays, Latitude/Longitude).
- **Petits multiples** : pas de puits natif → on duplique un graphique filtré, ou on utilise une grille de graphiques répétés.

> 🛒 **Exemple retail** — Treemap du CA par catégorie (Alimentaire > Boissons > Bières) ; jauge « CA mois / objectif » ; carte des magasins du Nord colorée par CA ; combiné CA (barres) + taux de marge (courbe) par mois ; petits multiples « ventes hebdo » par magasin pour repérer celui qui décroche.

> ⚠️ **Encadré — erreurs courantes (visuels avancés)**
> - **Camembert/treemap avec 15+ parts** : illisible. Regroupe en « Autres ».
> - **Jauge sans cible claire** : sans référence, la jauge n'apprend rien.
> - **Carte à bulles** où la plus grosse bulle = juste la plus grosse ville : tu cartographies la population, pas ton phénomène. Normalise (CA / habitant) si besoin.

---

### Mise en page et design

Quatre principes simples :

1. **Grille & alignement** : aligne les visuels, marges régulières. Power BI : active **Affichage → Quadrillage + Magnétisme**. Looker Studio : **Affichage → Grille / Aligner**.
2. **Hiérarchie visuelle** : ce qui compte le plus est en haut à gauche (sens de lecture occidental) et plus grand. KPI clés (cartes / scorecards) en haut, détail en bas.
3. **Thème & cohérence** : une **palette** limitée (2-3 couleurs + neutres), une police, des titres homogènes.
   - Power BI : **Affichage → Thèmes** (choisir, personnaliser, ou importer un fichier `theme.json`).
   - Looker Studio : menu **Thème et mise en page** → personnaliser couleurs/polices, ou « Extraire le thème d'une image ».
4. **Espaces blancs** : ne remplis pas chaque pixel. Le vide aide la lecture.

> 🛒 **Exemple retail** — Bandeau de titre + logo enseigne, ligne de 4 cartes KPI (CA, marge, panier moyen, nb clients), puis 2 visuels principaux, puis détail. Couleurs de l'enseigne (bleu nuit + orange), fond clair.

> ⚠️ **Encadré — erreurs courantes (design)**
> - **Effet « sapin de Noël »** : trop de couleurs vives. La couleur doit porter du sens, pas décorer.
> - Titres absents ou cryptiques. Chaque visuel doit dire **ce qu'il montre**, idéalement avec l'insight (« Le CA recule de 8 % à Roubaix »).
> - Mélange de polices/tailles → impression d'amateurisme.

---

### Accessibilité (WCAG / RGAA) — niveau avancé

L'accessibilité vise à rendre le rapport utilisable par **tous**, y compris personnes daltoniennes, malvoyantes, ou naviguant au clavier / lecteur d'écran.

**Les points clés**

1. **Palette adaptée au daltonisme** : ~8 % des hommes sont daltoniens. Évite le couple **rouge/vert** comme seul code. Utilise des palettes « color-blind safe » (ex. Okabe-Ito, ColorBrewer). Power BI propose des thèmes nommés **« Accessible »**.
2. **Ne jamais coder l'info par la couleur seule** : ajoute une **étiquette, une icône, un motif** ou du texte (ex. + / − en plus du vert/rouge).
3. **Contraste suffisant** : ratio de **4,5:1** minimum entre texte et fond (texte normal). Vérifie avec un outil (Color Contrast Analyzer, ou la fonctionnalité intégrée).
4. **Ordre de tabulation** :
   - Power BI : volet **Sélection → Ordre de tabulation** → réordonne les visuels dans l'ordre de lecture logique.
   - Looker Studio : l'ordre suit l'empilement des éléments ; organise-les proprement.
5. **Texte alternatif (alt text)** : décris chaque visuel pour le lecteur d'écran.
   - Power BI : sélectionne le visuel → **Format → Général → Texte de remplacement**.
   - Looker Studio : support plus limité ; soigne titres et libellés.
6. **Mode lecteur d'écran / navigation clavier** : Power BI est compatible NVDA/JAWS ; teste avec **Tab** que tout est atteignable et dans le bon ordre.
7. **Taille de police** lisible (≥ 12 pt pour le corps), pas de texte écrasé.

> 🛒 **Exemple retail** — Le tableau « objectifs atteints / non atteints » n'utilise plus seulement vert/rouge : ajout d'icônes ✔ / ✖ et d'un libellé. Le thème passe sur une palette accessible. Chaque carte KPI a un alt text (« CA total mai 2026 : 1,2 M€, +6 % vs avril »).

> ⚠️ **Encadré — erreurs courantes (accessibilité)**
> - **Penser l'accessibilité à la fin** : c'est dès la conception (choix de palette) qu'on gagne du temps.
> - **Contraste faible** (gris clair sur blanc) très fréquent → illisible au vidéoprojecteur aussi.
> - Alt text oublié ou générique (« graphique 1 »).

---

### Performance d'un dashboard

Un rapport doit charger **vite** (objectif courant : < 5 s).

- **Limiter le nombre de visuels par page** (repère : viser ≤ ~8 visuels). Chaque visuel = une requête.
- **Réduire les colonnes/lignes** ramenées : ne charge que ce qui sert (Power Query, requêtes Looker).
- **Préférer des mesures** (agrégées) à des tables détaillées affichées telles quelles.
- **Éviter les visuels custom lourds** et les images très haute résolution.
- Power BI : **Analyseur de performances** (Affichage → Analyseur de performances) → enregistre, identifie le visuel/la requête lente.
- Looker Studio : limite les sources mixtes (blends) et les champs calculés coûteux ; active la **mise en cache** / fraîcheur des données adaptée.

> 🛒 **Exemple retail** — Une page affichait un tableau de 50 000 lignes de tickets : remplacé par des agrégats + un drill-through vers le détail. Temps de chargement divisé par 4.

---

### Éviter les visualisations trompeuses (rappel maths ch. 6)

- **Axe Y tronqué** : commencer un axe à 90 au lieu de 0 exagère les écarts. Pour les barres, **part de 0**.
- **Double axe Y** : peut faire croire à une corrélation. À manier avec précaution, légender clairement.
- **3D et effets** : déforment les proportions → à proscrire.
- **Choix d'échelle / d'agrégation** orienté : cherry-picking de la période, axe logarithmique non signalé.
- **Cartes à bulles** non normalisées (cf. 3.2).
- **Camembert** avec trop de parts ou parts presque égales : on ne sait plus comparer.

> 🛒 **Exemple retail** — Un graphe montrait une « explosion » des ventes : en réalité l'axe démarrait à 95 000 €. Remis à 0, la hausse réelle est de 3 %. La présentation honnête évite une décision d'investissement injustifiée.

> ⚠️ **Encadré — erreurs courantes (honnêteté)**
> - Tronquer l'axe « pour mieux voir la tendance » : si tu le fais, **signale-le explicitement**.
> - Comparer des périodes de longueurs différentes (un mois vs un trimestre) sans le préciser.

---

## Travaux pratiques

> Support : ton tableau de bord retail « Ventes enseigne Nord » (ou le jeu de données fourni dans le brief Phase 2). Réalise chaque TP **dans Power BI ET, si possible, dans Looker Studio**.

### TP 1 — Rendre le dashboard interactif
Ajoute : un segment `Magasin`, un sélecteur de `Période`, le filtrage croisé sur l'histogramme du CA par catégorie, et une hiérarchie `Région → Ville → Magasin` avec drill-down activé.

<details>
<summary>Attendu / corrigé</summary>

- Segment `Magasin` (liste ou déroulant) + segment/contrôle `Période`.
- Histogramme CA par catégorie : interaction = **Filtrer** sur le tableau détaillé.
- Hiérarchie créée et posée en axe ; flèche de drill-down activée ; on peut descendre Région → Ville → Magasin.
- **Point de contrôle** : un clic sur une barre filtre bien les autres visuels ; un clic sur le segment restreint toute la page.
- Erreur fréquente corrigée : penser à **désactiver** le filtrage croisé sur les cartes KPI si on veut qu'elles restent globales… ou pas, selon le besoin métier (à justifier).
</details>

### TP 2 — Drill-through + signets de navigation
Crée une page « Fiche produit » en drill-through depuis le top produits (avec bouton retour). Crée 3 signets (« Vue Direction », « Vue Magasin », « Reset ») reliés à des boutons.

<details>
<summary>Attendu / corrigé</summary>

- Page « Fiche produit » avec champ `Produit` en puits **Extraction** ; bouton retour conservé.
- Clic droit sur un produit → Extraire → la fiche s'ouvre filtrée.
- 3 signets enregistrés (option **Sélectionnés** quand pertinent), reliés à 3 boutons (Action = Signet).
- **Looker Studio** : pages séparées + boutons « Aller à la page », filtres via contrôles.
- **Point de contrôle** : la navigation est fluide, aucun cul-de-sac, le « Reset » efface bien les filtres.
</details>

### TP 3 — Visuels avancés
Ajoute au moins **trois** visuels avancés pertinents : une carte des magasins colorée par CA, un graphique combiné CA (barres) + marge % (courbe), et des petits multiples « ventes par magasin ».

<details>
<summary>Attendu / corrigé</summary>

- Carte : champ géographique correctement typé (Ville), bulles/choroplèthe proportionnelles au CA.
- Combiné : axe principal = CA, axe secondaire = marge %, légende explicite ; pas d'interprétation abusive de corrélation.
- Petits multiples : **même échelle** sur tous, un mini-graphe par magasin, magasin « décrocheur » repérable.
- **Point de contrôle** : chaque visuel a un titre porteur de sens. Justifie pourquoi tu n'as PAS utilisé tel visuel (ex. pas de camembert à 15 parts).
</details>

### TP 4 — Accessibilité & honnêteté
Rends le dashboard accessible : palette adaptée daltonisme, contraste ≥ 4,5:1, info non codée par la couleur seule, ordre de tabulation, alt text sur les visuels. Corrige tout axe tronqué.

<details>
<summary>Attendu / corrigé</summary>

- Thème « Accessible » (Power BI) ou palette color-blind safe.
- Statuts objectif : couleur **+ icône/libellé** (pas vert/rouge seul).
- Contraste vérifié (outil) ≥ 4,5:1 pour le texte.
- Ordre de tabulation logique (volet Sélection).
- Alt text rédigé sur chaque visuel clé.
- Axes de barres repartis de 0 ; tout axe tronqué signalé.
- **Point de contrôle** : naviguer au clavier (Tab) atteint tous les éléments dans le bon ordre.
</details>

### TP 5 — Performance & mise en page (synthèse)
Optimise : limite les visuels par page, utilise l'Analyseur de performances (Power BI), réorganise selon la grille et la hiérarchie visuelle. Documente en 5 lignes ce que tu as changé et pourquoi.

<details>
<summary>Attendu / corrigé</summary>

- Page allégée (≤ ~8 visuels), tableau détaillé volumineux remplacé par agrégat + drill-through.
- Analyseur de performances lancé : visuel le plus lent identifié et corrigé/justifié.
- Mise en page sur grille : KPI en haut, alignements propres, palette cohérente, titres clairs.
- Note de synthèse (avant/après) : temps de chargement, lisibilité, choix de design.
- **Point de contrôle** : le rapport charge nettement plus vite et la lecture est immédiate.
</details>

---

## Vidéos d'auto-formation

> Les liens directs ci-dessous ont été vérifiés. Les liens « recherche YouTube » t'amènent à une liste de résultats à jour (préfère une vidéo récente, en HD, d'une chaîne reconnue).

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Color Blind Friendly Power BI Reports – Complete Guide | (YouTube) | EN | ~15 min | https://www.youtube.com/watch?v=Gj4wQeYlRn0 | Construire des rapports adaptés au daltonisme : palettes, thèmes accessibles, bonnes pratiques |
| Power BI Accessibility Enhancements for Color Blind or Blind Users (Color Contrast Check) | (YouTube) | EN | ~12 min | https://www.youtube.com/watch?v=9ZY3daqc6pg | Vérifier le contraste, accessibilité pour daltoniens et non-voyants, alt text |
| How To Test And Develop Color-blind Friendly Themes For Power BI | (YouTube) | EN | ~14 min | https://www.youtube.com/watch?v=bmoqjwCeXJs | Tester et créer un thème color-blind safe, importer un theme.json |
| Power BI — Drill-down, drill-through et bookmarks (tutoriel FR) | recherche YouTube | FR | variable | https://www.youtube.com/results?search_query=power+bi+drill+through+bookmarks+fran%C3%A7ais | Interactivité : descente de hiérarchie, extraction, signets et boutons |
| Looker Studio — contrôles, filtres et interactivité (tutoriel FR) | recherche YouTube | FR | variable | https://www.youtube.com/results?search_query=looker+studio+filtres+interactivit%C3%A9+contr%C3%B4les+fran%C3%A7ais | Ajouter contrôles, filtres croisés et navigation entre pages dans Looker Studio |

---

## Quiz (5 QCM)

**Q1.** Quelle fonctionnalité Power BI permet de passer d'une vue d'ensemble à **une autre page** filtrée sur l'élément cliqué ?
- A) Drill-down — B) Drill-through (Extraction) — C) Signet — D) Info-bulle

**Q2.** Pour rendre un dashboard accessible aux daltoniens, la meilleure pratique est :
- A) Utiliser uniquement rouge/vert mais en plus vif
- B) Ne coder l'information que par la couleur
- C) Ajouter icônes/libellés en complément de la couleur et choisir une palette accessible
- D) Supprimer toute couleur

**Q3.** Le ratio de contraste minimum recommandé (WCAG) pour un texte normal est :
- A) 1,5:1 — B) 3:1 — C) 4,5:1 — D) 10:1

**Q4.** Quel visuel est le plus adapté pour comparer **la même métrique** entre une dizaine de magasins ?
- A) Une seule jauge — B) Petits multiples (même échelle) — C) Un camembert à 10 parts — D) Une carte 3D

**Q5.** Un graphique en barres dont l'axe Y commence à 90 000 € au lieu de 0 :
- A) Est une bonne pratique pour mieux voir la tendance
- B) Peut exagérer visuellement les écarts → potentiellement trompeur
- C) Est obligatoire pour les grandes valeurs
- D) Améliore la performance du rapport

<details>
<summary>Réponses</summary>

1. **B** — Drill-through (Extraction) ouvre une autre page filtrée. (Drill-down reste dans le même visuel.)
2. **C** — Couleur accessible + redondance par icône/libellé.
3. **C** — 4,5:1 pour le texte normal.
4. **B** — Petits multiples avec une échelle commune.
5. **B** — Axe tronqué : à éviter sur des barres, ou à signaler explicitement.
</details>

---

## À retenir

- **Interactivité** = un seul rapport paramétrable : segments, **filtrage croisé**, **drill-down** (même visuel), **drill-through** (autre page), **signets** (vues mémorisées), **info-bulles** (contexte au survol).
- **Visuels avancés** : choisis selon le message — treemap (part-de-tout), jauge (1 KPI vs cible), carte (spatial), combiné (2 échelles), petits multiples (comparer). Chaque visuel a son piège.
- **Design** : grille, hiérarchie visuelle, thème cohérent, espaces blancs. La couleur porte du sens.
- **Accessibilité (WCAG/RGAA)** : palette daltonisme, **contraste ≥ 4,5:1**, info pas codée par la couleur seule, ordre de tabulation, **alt text**, navigation clavier/lecteur d'écran. À penser dès la conception.
- **Performance** : limiter les visuels, alléger les requêtes, mesurer (Analyseur de performances).
- **Honnêteté** : axe de barres part de 0, pas de 3D, double axe prudent, cartes normalisées. Ta crédibilité en dépend.
- Power BI et Looker Studio offrent l'essentiel ; **Power BI** est plus riche sur drill-through, signets, tooltips-page et accessibilité.
