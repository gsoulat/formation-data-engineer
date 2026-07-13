# Brief S01 — Découvrir le métier de data analyst et cadrer son projet chez NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S01 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant |
| **Modalité** | Binôme |
| **Technologies** | Markdown, Git/GitHub, tableur (Excel / Google Sheets), navigateur web |
| **Prérequis** | Aucun prérequis technique · une adresse e-mail pour créer un compte GitHub |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Sa direction commerciale veut se doter, au fil des prochains mois, d'un **tableau de bord de pilotage** pour suivre l'activité des points de vente — un chantier que vous allez construire semaine après semaine. Mais l'équipe data est naissante : un responsable BI, une contrôleuse de gestion, et vous qui arrivez.

### Le problème

Avant de brancher le moindre indicateur, la responsable des ressources humaines de NordRetail se pose une question très concrète : **quel profil recruter, et pour faire quoi exactement ?** Le mot « data analyst » circule dans tous les comités, mais chacun y met une définition différente — pour l'un c'est « la personne Excel », pour l'autre « celle qui fait des graphiques », pour un troisième « le développeur de la base ». Cette confusion ralentit le projet de tableau de bord : on ne sait ni quelles missions confier, ni quels outils prévoir, ni quelles compétences chercher sur le bassin d'emploi local (Auchan, Decathlon, Leroy Merlin, Cofidis, La Redoute, OVHcloud recrutent régulièrement dans la région).

On vous demande donc, en tout premier lieu, de **clarifier le métier** en le confrontant à la réalité du marché de l'emploi des Hauts-de-France, puis de poser noir sur blanc ce que vous, futur membre de l'équipe, apportez déjà et ce que vous allez développer. C'est le point de départ de tout le parcours : comprendre le rôle avant de l'exercer.

### La question centrale

Toute la semaine, chaque élément que vous produisez doit contribuer à répondre à la question que la direction vous a posée :

> **« Qu'est-ce qu'un data analyst fait vraiment sur le terrain dans le Nord — et où est-ce que je me situe aujourd'hui par rapport à ce métier ? »**

### Les données

Pas de fichier de ventes cette semaine. La « donnée » à collecter, ce sont les **offres d'emploi réelles** de la région et l'écosystème d'outils du métier. Vous les traiterez avec la même rigueur qu'un jeu de données : sources tracées, informations rangées dans un tableau, constats argumentés. Pour un premier contact concret avec un fichier tel qu'on en manipule chez NordRetail, un extrait de référentiel produit est mis à disposition (voir *Données fournies*).

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Décrire le métier de data analyst** en distinguant ses missions, ses livrables et sa place dans une équipe, par opposition aux métiers voisins (data engineer, développeur, contrôleur de gestion).
- **Mener une veille structurée sur le marché de l'emploi** : identifier des sources fiables, collecter des offres réelles et en extraire les attentes récurrentes (missions, outils, compétences).
- **Cartographier l'écosystème d'outils** de la donnée (tableur, SQL, Python, outils de tableau de bord) et associer chaque outil à un usage métier.
- **Vous auto-positionner honnêtement** : reconnaître vos points d'appui et formuler des axes de progression concrets.
- **Formaliser un projet professionnel** clair et personnel, et le publier proprement dans un dépôt versionné (premier pas Git/GitHub).

## Données fournies

Aucune donnée n'est à télécharger pour l'analyse d'emploi : vous collectez vous-même les offres. Pour un premier regard sur un fichier « métier » représentatif de ceux que vous manipulerez plus tard, ouvrez [`../data/referentiel_produits.csv`](../data/referentiel_produits.csv) dans un tableur : observez ses colonnes, son volume, ce qu'une ligne représente. Vous travaillez en lecture seule ; on ne modifie jamais la source.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre dossier et son propre projet professionnel (l'auto-positionnement, lui, est individuel). Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et prise en main, SANS analyse (J1)

Avant de collecter quoi que ce soit, appropriez-vous le sujet. Que croyez-vous, à cet instant, que fait un data analyst au quotidien ? Écrivez votre définition « à chaud », en une ou deux phrases — vous la relirez en fin de semaine pour mesurer le chemin parcouru. Interrogez-vous sur les frontières du métier : en quoi diffère-t-il d'un data engineer, d'un développeur, d'un contrôleur de gestion ? Ouvrez ensuite [`../data/referentiel_produits.csv`](../data/referentiel_produits.csv) dans un tableur : que représente une ligne ? combien y en a-t-il ? quelles informations une enseigne comme NordRetail range-t-elle dans un tel fichier ? Ce simple regard vous donne une idée de la matière première du métier. Enfin, créez votre compte GitHub si nécessaire et **initialisez votre dépôt aujourd'hui** : il accueillera tous vos travaux de la semaine.

### Phase 2 — Collecte d'offres d'emploi réelles (J1-J2)

Partez à la chasse aux **deux fiches de poste réelles** de data analyst (ou intitulé proche : analyste de données, chargé d'études data, BI analyst) localisées en **Hauts-de-France**. Sources possibles : France Travail, LinkedIn, Indeed, HelloWork, les sites carrière des enseignes citées. Pour chaque offre, conservez le **lien** et le **nom de l'entreprise** — sans source traçable, une information ne vaut rien, exactement comme une donnée sans provenance. Demandez-vous si les offres que vous retenez sont représentatives : une offre « senior » et une offre « junior » racontent-elles le même métier ? Gardez une capture d'écran en cas de retrait de l'annonce.

### Phase 3 — Cartographie des attentes et de l'écosystème d'outils (J2-J3)

Faites parler vos offres. Construisez un **tableau comparatif** des deux annonces couvrant, pour chacune : les **missions principales** (formulées avec des verbes d'action), les **outils et technologies** cités (tableur, SQL, Python, outils de tableau de bord…), les **compétences techniques** attendues, les **compétences humaines** (communication, rigueur, esprit d'analyse…), le niveau d'expérience et le type de contrat. Qu'est-ce qui revient dans les deux offres ? Qu'est-ce qui les distingue ? Prolongez ensuite ce tableau par une courte **cartographie des outils** : pour au moins quatre outils relevés, expliquez en une phrase à quoi ils servent concrètement dans le quotidien d'un analyste (par exemple : à quoi sert un outil de tableau de bord que ne fait pas un tableur ?).

### Phase 4 — Auto-positionnement (J3-J4)

Regardez-vous dans le miroir du métier. À partir des compétences relevées dans vos offres, listez **trois points que vous maîtrisez déjà** (même partiellement — savoir organiser une information, présenter un résultat, apprendre vite comptent) et **trois axes que vous devrez travailler** pendant la formation. Soyez honnête et précis : « progresser en SQL » est plus utile que « m'améliorer ». Cet exercice est **individuel** : chaque membre du binôme rédige le sien. Interrogez-vous : parmi les axes de progrès, lesquels le parcours à venir va-t-il justement couvrir ?

### Phase 5 — Projet professionnel, restitution et mise en ligne (J5)

Rédigez votre **projet professionnel** : un paragraphe de 8 à 12 lignes qui répond frontalement à trois questions — pourquoi ce métier vous attire, quel type d'entreprise ou de secteur vous motive en Hauts-de-France, et où vous vous voyez dans dix-huit mois. Ce texte est personnel et destiné à être lu par un jury : soignez-le. Relisez enfin votre définition « à chaud » de la Phase 1 : qu'ajouteriez-vous aujourd'hui ? Rassemblez tableau, cartographie, auto-positionnements et projet professionnel dans un dossier propre, rédigez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : deux offres réelles sourcées, tableau comparatif (missions, outils, compétences techniques ET humaines), cartographie d'au moins quatre outils, auto-positionnement individuel (3 acquis + 3 axes), projet professionnel rédigé, dépôt public à jour avec README.

### Pour aller plus loin (bonus)

- Ajoutez une **troisième offre** issue d'un secteur différent (industrie, banque, e-commerce pur) : le métier change-t-il de visage selon le secteur ?
- Réalisez une **mini-veille outils** : comparez deux outils de tableau de bord du marché (forces, limites, gratuité éventuelle) en 5 lignes.
- Reliez explicitement quatre attentes de vos offres aux **modules à venir** du parcours : le tableau de bord de pilotage de NordRetail mobilisera-t-il ce que le marché demande ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - un **dossier d'analyse du métier** (`decouverte_metier.md` ou PDF) réunissant le tableau comparatif des deux offres, la cartographie des outils et les auto-positionnements ;
  - le **projet professionnel** de chaque membre du binôme (dans le dossier ou en fichier séparé) ;
  - un **`README.md`** : description du travail, sources utilisées, auteur(s), et vos deux définitions du métier (celle du J1 et celle du J5).
- Une **table des sources** (liens des offres + entreprises + date de consultation) — dans le dossier d'analyse ou le README.

## Modalités d'évaluation

Évaluation en deux volets :

- **Dossier et projet professionnel (60 %)** : réalité et traçabilité des offres, complétude du tableau comparatif, pertinence de la cartographie d'outils, sincérité de l'auto-positionnement, qualité du projet professionnel.
- **Restitution orale (40 %)** : 10 minutes de présentation à un « comité de recrutement » (le formateur et un autre binôme) où vous expliquez ce qu'est le métier dans le Nord et où vous vous situez, + 5 minutes de questions.

**Validation partielle** : un binôme dont le dossier n'est pas entièrement finalisé mais dont la démarche de veille est structurée, les sources traçables et l'auto-positionnement argumenté peut valider partiellement les compétences travaillées.

## Critères de performance

**Comprendre le métier et l'écosystème d'outils**
- Le métier de data analyst est décrit avec ses missions et distingué d'au moins un métier voisin.
- Au moins quatre outils relevés sont associés à un usage métier concret.
- Le tableau comparatif couvre missions, outils, compétences techniques ET humaines.

**Mener une veille structurée**
- Deux offres réelles, localisées en Hauts-de-France, sont sourcées (lien + entreprise).
- Les sources sont traçables (liens conservés, date de consultation, capture au besoin).
- Les attentes récurrentes des offres sont dégagées et confrontées.

**Se positionner et projeter son parcours**
- L'auto-positionnement liste 3 acquis ET 3 axes de progrès, précis et personnels.
- Le projet professionnel est rédigé, personnel et mentionne un secteur/horizon concrets.
- Il répond aux trois questions attendues (pourquoi le métier, quel secteur, horizon 18 mois).

**Restituer et publier**
- Le dossier répond explicitement à la question centrale de la semaine.
- Le rendu est lisible, structuré et rédigé sans jargon inutile.
- Le dépôt GitHub public est complet (dossier + README + sources).

## Ressources

- Module de cours — [Le métier de data analyst](../../../15-Business-Intelligence/01-Metier-Data-Analyst/)
- Module de cours — [Panorama des outils BI](../../../15-Business-Intelligence/02-Panorama-Outils-BI/)
- Rappels — [Méthode de veille technologique](../../../01-Fondamentaux/Veille-Technologique/)
- Premiers pas versionnage — [Git & GitHub](../../../01-Fondamentaux/Github/)
- [France Travail — recherche d'offres](https://candidat.francetravail.fr/offres/recherche) (filtre région Hauts-de-France)
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
