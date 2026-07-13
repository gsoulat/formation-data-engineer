# Brief S13 — Rendre le tableau de bord de NordRetail interactif et accessible à tous

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S13 — Phase 2 : Solution BI pour l'analyse avancée |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Power BI (hiérarchies, drill-down, segments, signets, thèmes) · outil de test de contraste · Git/GitHub |
| **Prérequis** | [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/) · [DAX](../../../15-Business-Intelligence/10-DAX/) · [Dashboards — fondamentaux](../../../15-Business-Intelligence/07-Dashboards-Fondamentaux/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Son équipe data, encore jeune, a construit ces dernières semaines les fondations analytiques de l'enseigne : un modèle de données en étoile fiable, puis un jeu de mesures de gestion (chiffre d'affaires, marge, panier moyen, évolution par rapport à l'an dernier) qui donnent enfin les mêmes chiffres d'une réunion à l'autre.

### Le problème

Le tableau de bord affiche désormais les bons chiffres — mais il reste **figé**. À chaque comité, c'est vous qui manipulez l'outil : quand la responsable de Roubaix veut voir *ses* chiffres, ou que la direction veut descendre du trimestre au mois pour comprendre un pic, il faut tout reconfigurer sous leurs yeux. Les responsables de magasin réclament de pouvoir **explorer eux-mêmes** : filtrer par ville, dérouler une période, retrouver d'un clic un point de vue déjà préparé.

Un second signal est remonté de la direction : une collègue du contrôle de gestion est **daltonienne** et ne distingue pas certaines courbes du tableau de bord actuel, entièrement codées par la couleur. Un outil de pilotage que 8 % des hommes ne peuvent pas lire correctement n'est pas un outil de pilotage fiable. L'accessibilité n'est donc pas un supplément d'âme : c'est une condition pour que le tableau de bord soit réellement partagé dans l'entreprise.

Votre mission de la semaine consiste à **transformer un rapport que l'on montre en un outil que l'on utilise**, lisible par tous.

### La question centrale

Toute la semaine, chaque interaction et chaque réglage que vous ajoutez doit contribuer à répondre à la question que la direction vous a posée :

> **« Comment permettre à chaque responsable de NordRetail — quel que soit son magasin, et quelle que soit sa vision des couleurs — d'explorer lui-même le tableau de bord et d'y trouver sa réponse en quelques clics ? »**

### Les données

Vous repartez du rapport construit lors des deux dernières semaines : le **modèle en étoile** et ses **mesures**. Les sources sont les fichiers du schéma dimensionnel déjà présents dans le dépôt :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — table de faits (`vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`).
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — points de vente (`magasin_id`, `ville`, `type`, `surface_m2`, `date_ouverture`).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — produits (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — calendrier (`date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour`, `jour_semaine`, `est_weekend`).

Aucune donnée n'est à télécharger ni à modifier : le travail de la semaine porte sur l'**expérience** offerte par le rapport, pas sur les chiffres eux-mêmes.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Construire des hiérarchies et activer le drill-down** (Année → Trimestre → Mois, Catégorie → Produit) pour permettre à l'utilisateur de descendre du général au détail.
- **Concevoir un filtrage cohérent** avec des segments (ville, catégorie, période) qui agissent sur l'ensemble d'une page sans se contredire.
- **Préparer des vues métier réutilisables** à l'aide de signets et de boutons de navigation, prêtes à être présentées d'un clic.
- **Piloter intentionnellement les interactions entre visuels** (ce qui filtre quoi, et ce qui ne doit pas filtrer).
- **Rendre une restitution accessible selon les principes WCAG** : contraste suffisant, information jamais portée par la seule couleur, titres explicites, texte de remplacement, ordre de tabulation logique, taille de police lisible.
- **Justifier chaque choix de visualisation et d'interaction** au regard d'un besoin utilisateur concret.

## Données fournies

Le schéma dimensionnel est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Vous réutilisez le rapport que votre binôme a construit précédemment (modèle en étoile + mesures) ; si vous n'en disposez pas, reconstruisez un modèle minimal à partir des `Dim_*.csv` et de `Faits_Ventes.csv` avant de commencer. On ne modifie jamais les fichiers sources : tout se joue dans le rapport.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre rapport et sa propre fiche d'accessibilité. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage des usages, SANS toucher au rapport (J1)

Avant d'ajouter la moindre interaction, mettez-vous dans la peau des utilisateurs. Listez les **profils** qui consulteront le tableau de bord (direction nationale, responsable d'un magasin, contrôle de gestion) et, pour chacun, la **question type** qu'il voudra résoudre seul : « quel est le CA de mon magasin ce mois-ci ? », « d'où vient le pic du trimestre ? », « quelle catégorie tire la marge ? ». Pour chaque question, notez le chemin d'exploration attendu : quel filtre, quel niveau de détail, quel graphique. Que doit pouvoir faire un utilisateur *sans vous* pour obtenir sa réponse ? Réfléchissez aussi, dès maintenant, à ce que « lisible par tous » implique concrètement : si l'on retirait toute couleur du rapport, l'information passerait-elle encore ? Consignez ces usages : ils serviront de cahier des charges pour toute la semaine. Initialisez (ou mettez à jour) votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Hiérarchies et drill-down (J1-J2)

Donnez de la profondeur aux analyses. Créez une **hiérarchie de dates** (Année → Trimestre → Mois) et une **hiérarchie produit** (Catégorie → Produit), en vous appuyant sur les colonnes de `Dim_Date` et `Dim_Produit`. Activez le drill-down sur au moins un visuel d'**évolution du chiffre d'affaires** : la direction doit pouvoir partir d'une vue annuelle, cliquer, et descendre au mois qui explique un écart. Vérifiez que le sens de lecture reste évident quand on descend ou remonte dans la hiérarchie. Est-ce qu'un utilisateur comprend, sans explication, à quel niveau il se trouve ?

### Phase 3 — Segments et interactions cohérentes (J2-J3)

Rendez le rapport filtrable. Ajoutez des **segments** par `ville`, par `categorie` et par **période**, et assurez-vous qu'ils filtrent l'ensemble de la page de façon cohérente : sélectionner « Roubaix » doit recadrer *tous* les visuels concernés, sans en oublier ni en fausser un. Configurez ensuite les **interactions entre visuels** de manière intentionnelle : un clic sur une catégorie doit-il filtrer le graphique voisin, le mettre en surbrillance, ou ne rien faire ? Désactivez les interactions qui n'ont pas de sens (un total national n'a pas à changer quand on survole un produit). Chaque interaction conservée doit répondre à un usage identifié en Phase 1 ; documentez vos choix.

### Phase 4 — Signets, navigation et accessibilité (J3-J4)

Préparez des points de vue prêts à présenter. Créez au moins **deux signets** correspondant à des vues métier concrètes — par exemple « Vue direction — national » et « Vue manager — Roubaix » — et rendez-les atteignables par des **boutons de navigation** clairs. Un responsable doit retrouver sa vue d'un seul clic.

Rendez ensuite le rapport **accessible** (principes WCAG). Adoptez une **palette à contraste suffisant et compatible daltonisme** (palettes sûres type Okabe-Ito ou ColorBrewer, thème Power BI « accessible ») et vérifiez que l'information n'est **jamais portée par la seule couleur** — ajoutez libellés, formes ou motifs si nécessaire. Donnez à chaque visuel un **titre explicite** et un **texte de remplacement** sur les visuels clés. Contrôlez l'**ordre de tabulation** et une **taille de police lisible**. Enfin, **mesurez le contraste** de vos couleurs de texte et de graphique avec un outil dédié (ratio visé ≥ 4,5:1) et corrigez ce qui ne passe pas. Reprenez la question de la Phase 1 : votre collègue daltonienne peut-elle maintenant tout lire ?

### Phase 5 — Fiche d'accessibilité, restitution et mise en ligne (J5)

Rédigez une **fiche d'accessibilité et d'interactions** (1 page) qui liste les interactions ajoutées (hiérarchies, drill-down, segments, signets) et les contrôles d'accessibilité effectués, **avec les résultats chiffrés du test de contraste**. Cette fiche s'adresse à la direction : elle doit prouver que le tableau de bord est utilisable et lisible par tous. Vérifiez que chaque signet s'ouvre proprement, que chaque segment filtre juste, soignez le README, et poussez le rapport enrichi et la fiche sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : au moins une hiérarchie avec drill-down fonctionnel, segments ville/catégorie/période cohérents, ≥ 2 signets accessibles par boutons, interactions configurées intentionnellement, palette accessible sans dépendance à la seule couleur, titres + alt text, test de contraste réalisé et documenté, fiche d'accessibilité, dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez une **info-bulle personnalisée** (tooltip) qui affiche un mini-détail (top produits, marge) au survol d'une barre.
- Créez un **signet de réinitialisation** (« Effacer tous les filtres ») via un bouton, pour remettre la page à zéro d'un clic.
- Proposez une **version « présentation »** épurée de la page (mode plein écran, éléments non essentiels masqués par signet) pour les comités de direction.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **rapport enrichi** (`.pbix` ou export équivalent) : hiérarchies, drill-down, segments, signets, interactions et réglages d'accessibilité ;
  - la **fiche d'accessibilité et d'interactions** (`ACCESSIBILITE.md` ou PDF, 1 page) listant les interactions ajoutées et les contrôles WCAG effectués, avec les résultats du test de contraste ;
  - un **`README.md`** : description du projet, technologies, mode d'emploi des vues et signets, auteur(s).
- Deux **captures d'écran** au minimum illustrant deux signets métier distincts.

## Modalités d'évaluation

Évaluation en deux volets :

- **Rapport enrichi et fiche d'accessibilité (60 %)** : richesse et pertinence des interactions, cohérence du filtrage, qualité des signets, respect des principes WCAG (contraste vérifié, information non portée par la seule couleur, alt text), clarté de la fiche.
- **Restitution orale (40 %)** : 10 minutes de démonstration devant un « comité de direction » (le formateur et un autre binôme), en laissant un membre du comité manipuler lui-même le rapport, + 5 minutes de questions.

**Validation partielle** : un binôme dont le rapport n'est pas totalement finalisé mais qui démontre des interactions fonctionnelles ET une démarche d'accessibilité argumentée (choix de palette, test de contraste réalisé) peut valider partiellement les compétences travaillées.

## Critères de performance

**Rendre le tableau de bord interactif**
- Le drill-down fonctionne sur au moins une hiérarchie (date ou produit).
- Des segments par ville, catégorie et période filtrent la page de façon cohérente.
- Au moins 2 signets de vues métier sont accessibles via des boutons de navigation.
- Les interactions entre visuels sont configurées intentionnellement (activées OU désactivées à dessein).

**Rendre la restitution accessible (WCAG)**
- La palette respecte un contraste suffisant et ne repose pas uniquement sur la couleur.
- Titres explicites et texte de remplacement sont présents sur les visuels clés.
- Un test de contraste a été réalisé et ses résultats chiffrés sont documentés.

**Justifier et restituer**
- Chaque interaction et chaque signet est rattaché à un usage utilisateur identifié.
- La fiche d'accessibilité et d'interactions est claire et complète.
- Le dépôt GitHub public est complet (rapport enrichi + fiche + README).

## Ressources

- Module de cours — [Dashboards : fondamentaux](../../../15-Business-Intelligence/07-Dashboards-Fondamentaux/)
- Module de cours — [Visualisations avancées & accessibilité](../../../15-Business-Intelligence/11-Visualisations-Avancees/)
- Module de cours — [Tableau de bord expert (checklist d'accessibilité)](../../../15-Business-Intelligence/17-Dashboard-Expert/)
- Rappel — [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/)
- Principes WCAG : usage de la couleur (1.4.1) et redimensionnement du texte (1.4.4) ; palettes sûres pour daltoniens (Okabe-Ito, ColorBrewer)
- Documentation Power BI — accessibilité des rapports : https://learn.microsoft.com/power-bi/create-reports/desktop-accessibility-overview
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_2 — Solution BI avancée](../BRIEF_2_SOLUTION_BI_AVANCEE.md)
</content>
</invoke>
