# Brief S22 — Finaliser le tableau de bord expert de NordRetail : exploration, performance, accessibilité et récit

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S22 — Phase 3 : Tableau de bord expert en autonomie (2/2) |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Avancé — autonomie |
| **Modalité** | Individuel |
| **Technologies** | Power BI (drill-down, segments synchronisés, signets, Performance Analyzer, thèmes accessibles) ou Looker Studio · outil de test de contraste · Git/GitHub |
| **Prérequis** | [Visualisations avancées & accessibilité](../../../15-Business-Intelligence/11-Visualisations-Avancees/) · [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/) · [Tableau de bord expert](../../../15-Business-Intelligence/17-Dashboard-Expert/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Son équipe data, encore jeune, a construit au fil des semaines les fondations analytiques de l'enseigne — un modèle en étoile fiable, des mesures de gestion cohérentes, un rapport interactif et accessible — et vous en êtes désormais un membre autonome. La semaine dernière, seul face à un sponsor pressé, vous avez cadré le besoin, monté un modèle propre et livré la **première page** d'un tableau de bord de pilotage régional.

### Le problème

Cette première page a plu au comité de direction. Mais un dashboard « correct » n'est pas encore un dashboard **réellement exploitable en réunion**. Quand la direction descend du trimestre au mois pour comprendre un pic, il faut encore intervenir. Sur l'année complète, l'affichage traîne. Un membre du comité, **daltonien**, ne distingue pas certaines séries codées uniquement par la couleur. Et surtout, l'outil aligne des graphiques sans **raconter** ce qui se passe dans l'enseigne : le lecteur voit des chiffres, pas un message.

Votre mission de la semaine intervient donc **en aval** du cadrage : transformer une première page prometteuse en un **outil de pilotage complet** que le comité manipule seul, qui reste fluide sur toute l'année, que tout le monde peut lire, et qui délivre une histoire. Vous ne repartez pas de zéro : vous **enrichissez** le rapport de la semaine précédente.

### La question centrale

Toute la semaine, chaque page, chaque interaction et chaque réglage que vous ajoutez doit contribuer à répondre à la question que la direction vous a posée :

> **« Comment faire de ce tableau de bord un outil que le comité de NordRetail utilise seul, sans moi, pour comprendre en quelques clics ce qui porte — ou freine — l'activité de l'enseigne ? »**

### Les données

Vous repartez du rapport construit en S21 : le **modèle en étoile** et ses **mesures** (chiffre d'affaires, marge, taux de marge, taux d'atteinte des objectifs). Les sources sont les fichiers du schéma dimensionnel déjà présents dans le dépôt :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — table de faits (`vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`).
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — points de vente (`magasin_id`, `ville`, `type`, `surface_m2`, `date_ouverture`).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — produits (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — calendrier (`date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour`, `jour_semaine`, `est_weekend`).
- [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx) — objectifs de chiffre d'affaires par magasin et par mois, pour le calcul du taux d'atteinte.

Aucune donnée n'est à télécharger ni à modifier : le travail de la semaine porte sur l'**expérience**, la **performance** et le **récit** offerts par le rapport, pas sur les chiffres eux-mêmes.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Structurer un tableau de bord multi-pages cohérent** (vue d'ensemble, magasins, produits/catégories, objectifs) navigable d'un clic, avec une identité visuelle constante.
- **Rendre un rapport réellement explorable en autonomie** : drill-down, segments synchronisés entre pages, info-bulles enrichies, navigation par boutons ou signets.
- **Optimiser les performances d'un modèle BI** : granularité de la table de faits, colonnes inutiles retirées, mesures privilégiées aux colonnes calculées, et savoir le mesurer.
- **Concevoir une restitution accessible selon les principes WCAG** : palette sûre pour daltoniens, contraste suffisant, information jamais portée par la seule couleur, titres explicites et textes de remplacement.
- **Construire un récit de données (storytelling)** qui guide la lecture du général au détail et met en avant les enseignements clés par des annotations.
- **Justifier chacun de ses choix** (page, visuel, palette, optimisation, parcours de lecture) au regard d'un besoin utilisateur concret.

## Données fournies

Le schéma dimensionnel et les objectifs sont déjà présents dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Vous réutilisez le rapport construit en S21 (modèle en étoile + mesures + page 1) ; si vous ne disposez pas d'un rapport propre, reconstruisez un modèle minimal à partir des `Dim_*.csv`, de `Faits_Ventes.csv` et de `objectifs_2024.xlsx` avant de commencer. On ne modifie jamais les fichiers sources : tout se joue dans le rapport.

## Travail demandé

Travail **individuel sur 5 jours**. L'entraide est encouragée, mais chacun produit son propre rapport et sa propre documentation. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides. Vous êtes en autonomie : on vous donne un objectif métier et vous décidez du « comment ». On n'attend pas de vous des techniques inédites, mais que vous **pilotiez seul** des techniques déjà connues et que vous **justifiiez** vos décisions.

### Phase 1 — Cadrage de la finalisation, SANS toucher au rapport (J1)

Avant d'ajouter la moindre page, prenez du recul sur ce qui manque à votre page 1 pour qu'un comité l'utilise seul. Listez les **profils** qui consulteront le tableau de bord (direction régionale, responsable d'un magasin, contrôle de gestion) et, pour chacun, la **décision** qu'il doit pouvoir éclairer sans vous : « quel magasin décroche par rapport à son objectif ? », « quelle catégorie tire la marge ? », « d'où vient l'écart du trimestre ? ». À partir de là, esquissez le **plan des pages** (Vue d'ensemble, Magasins, Produits/Catégories, Objectifs) et le **parcours de lecture** que vous voulez imposer : par où commence le regard, où le menez-vous ensuite ? Réfléchissez dès maintenant à ce que « lisible par tous » implique — si l'on retirait toute couleur, l'information passerait-elle encore ? — et à ce qui pourrait ralentir le rapport sur l'année complète. Consignez ce cadrage : il sert de feuille de route pour la semaine. Mettez à jour votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Pages thématiques et cohérence visuelle (J1-J2)

Donnez de l'ampleur au rapport. Ajoutez **2 à 3 pages** cohérentes avec la page 1 : une page **Magasins** (comparaison régionale : CA, marge, classement), une page **Produits/Catégories** (mix de ventes et marge par catégorie, drill vers le produit), une page **Objectifs** (atteinte vs réel à partir de `objectifs_2024.xlsx`). Chaque page doit répondre à un besoin identifié en Phase 1. Soignez la **cohérence visuelle** : mêmes polices, mêmes codes de couleur pour les mêmes notions, même emplacement des titres et des filtres d'une page à l'autre. Un utilisateur qui passe d'une page à l'autre ne doit jamais se sentir dans un autre outil.

### Phase 3 — Interactivité et navigation autonome (J2-J3)

Rendez le rapport explorable **sans vous**. Mettez en place des **segments synchronisés** (ville, catégorie, période) qui agissent de façon cohérente d'une page à l'autre, un **drill-down** au moins de la catégorie vers le produit (et, si pertinent, de l'année vers le mois), des **info-bulles enrichies** qui apportent un détail au survol (top produits, marge), et une **navigation entre pages** par boutons ou signets. Posez-vous la question à chaque interaction : est-elle rattachée à un usage identifié ? Un clic sur une catégorie doit-il filtrer le visuel voisin, le mettre en surbrillance, ou ne rien faire ? Désactivez à dessein ce qui n'a pas de sens. Testez : un responsable de Roubaix retrouve-t-il *ses* chiffres seul, en quelques clics ?

### Phase 4 — Performance, accessibilité et récit (J3-J4)

Trois exigences de niveau expert sur cette phase.

**Performance.** Optimisez le modèle pour qu'il reste fluide sur l'année complète : vérifiez la **granularité** de la table de faits, retirez les **colonnes inutiles**, privilégiez les **mesures** aux colonnes calculées. Mesurez l'effet (par exemple avec Performance Analyzer sous Power BI) et notez **au moins 2 optimisations** réalisées, avec ce qu'elles ont changé.

**Accessibilité (WCAG).** Adoptez une **palette sûre pour daltoniens** (type Okabe-Ito ou ColorBrewer, thème « accessible ») et vérifiez que l'information n'est **jamais portée par la seule couleur** — ajoutez libellés, formes ou motifs si besoin. Donnez à chaque visuel un **titre explicite** et un **texte de remplacement** sur les visuels clés, contrôlez l'**ordre de tabulation** et une **taille de police lisible**, puis **mesurez le contraste** (ratio visé ≥ 4,5:1) avec un outil dédié et corrigez ce qui ne passe pas. Votre collègue daltonien peut-il désormais tout lire ?

**Storytelling.** Structurez la lecture **du général au détail** : la page d'ouverture donne le message, les pages suivantes l'expliquent. Remplacez les titres neutres par des **titres porteurs de sens** (« La marge décroche à Valenciennes au T3 » plutôt que « Marge par magasin ») et ajoutez **2 à 3 annotations** qui pointent l'insight clé de chaque page. Le tableau de bord doit délivrer un message, pas seulement des chiffres.

### Phase 5 — Fiche utilisateur, note d'optimisation et restitution (J5)

Rédigez une **fiche utilisateur** (½ page) : à quoi sert chaque page, comment naviguer, comment filtrer. Rédigez aussi une **note d'optimisation et d'accessibilité** : les 2+ optimisations de performance réalisées, la palette et les contrôles WCAG effectués avec les **résultats chiffrés du test de contraste**. Vérifiez que chaque page s'ouvre proprement, que chaque segment filtre juste, que le rapport reste fluide, soignez le README, et poussez le tout sur GitHub. Préparez enfin une courte démonstration : vous laisserez un membre du comité manipuler le rapport lui-même.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : 3 à 4 pages cohérentes et navigables, interactivité fonctionnant sans aide (segments synchronisés, drill-down, navigation), au moins 2 optimisations de performance documentées, accessibilité traitée (palette daltoniens, contraste testé, titres, alt text), storytelling présent (parcours de lecture + insights annotés), fiche utilisateur, note d'optimisation/accessibilité, dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez un **signet de réinitialisation** (« Effacer tous les filtres ») accessible par un bouton, pour remettre le rapport à zéro d'un clic.
- Proposez une **page de synthèse « comité »** épurée, en mode présentation, qui tient le message essentiel de l'enseigne en un seul écran.
- Ajoutez un **indicateur d'alerte visuel** (magasin sous objectif) qui ne repose pas sur la couleur seule (icône, forme), et documentez pourquoi ce choix est accessible.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **rapport final** (`.pbix` ou lien Looker Studio partagé) : 3-4 pages cohérentes, interactivité, optimisations, réglages d'accessibilité et récit ;
  - une **fiche utilisateur** (`FICHE_UTILISATEUR.md` ou PDF, ½ page) : rôle de chaque page et mode de navigation ;
  - une **note d'optimisation et d'accessibilité** (`OPTIMISATION.md` ou PDF) : optimisations réalisées + contrôles WCAG avec résultats du test de contraste ;
  - un **`README.md`** : description du projet, technologies, mode d'emploi, auteur.
- Au moins **deux captures d'écran** illustrant deux pages métier distinctes (ex. Vue d'ensemble et Objectifs).

## Modalités d'évaluation

Évaluation en deux volets :

- **Rapport final et documentation (60 %)** : cohérence et navigabilité des pages, richesse et pertinence de l'interactivité, réalité des optimisations de performance, respect des principes WCAG (contraste vérifié, information non portée par la seule couleur, alt text), qualité du storytelling, clarté de la fiche utilisateur et de la note d'optimisation.
- **Restitution orale (40 %)** : 10 minutes de démonstration devant un « comité de direction » (le formateur et un pair), en laissant un membre du comité manipuler lui-même le rapport, + 5 minutes de questions au cours desquelles vous justifiez vos choix (pages, visuels, palette, optimisations, parcours de lecture).

**Validation partielle** : un apprenant dont le rapport n'est pas totalement finalisé mais qui démontre des pages cohérentes et interactives, ET une démarche d'accessibilité et de storytelling argumentée (palette justifiée, test de contraste réalisé, parcours de lecture explicite), peut valider partiellement les compétences travaillées.

## Critères de performance

**Concevoir un tableau de bord multi-pages exploitable**
- Le rapport compte 3 à 4 pages cohérentes et navigables entre elles.
- L'interactivité (segments synchronisés, drill-down, navigation) fonctionne sans aide extérieure.
- Chaque page et chaque interaction est rattachée à un usage utilisateur identifié.
- Au moins 2 optimisations de performance sont réalisées et documentées (avec leur effet).

**Rendre la restitution accessible et porteuse de sens**
- La palette respecte un contraste suffisant (test réalisé et chiffré) et ne repose pas uniquement sur la couleur.
- Titres explicites et textes de remplacement sont présents sur les visuels clés.
- Le storytelling est présent : parcours de lecture du général au détail + 2-3 insights annotés.

**Documenter, justifier et restituer**
- La fiche utilisateur explique le rôle de chaque page et le mode de navigation.
- La note d'optimisation et d'accessibilité est claire et complète.
- Les choix (pages, visuels, palette, optimisations) sont justifiés à l'oral.
- Le dépôt GitHub public est complet (rapport final + fiche + note + README).

## Ressources

- Module de cours — [Tableau de bord expert](../../../15-Business-Intelligence/17-Dashboard-Expert/)
- Module de cours — [Visualisations avancées & accessibilité](../../../15-Business-Intelligence/11-Visualisations-Avancees/)
- Module de cours — [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/)
- Rappel — [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/) · [DAX](../../../15-Business-Intelligence/10-DAX/)
- Principes WCAG : usage de la couleur (1.4.1) et redimensionnement du texte (1.4.4) ; palettes sûres pour daltoniens (Okabe-Ito, ColorBrewer)
- Documentation Power BI — accessibilité des rapports : https://learn.microsoft.com/power-bi/create-reports/desktop-accessibility-overview
- Documentation Power BI — Performance Analyzer : https://learn.microsoft.com/power-bi/create-reports/desktop-performance-analyzer
- Prochaine étape du parcours — projet final : [BRIEF_3 — Projet final](../BRIEF_3_PROJET_FINAL.md)
