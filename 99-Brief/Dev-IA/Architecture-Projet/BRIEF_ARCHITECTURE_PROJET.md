# Brief : Cadrer et concevoir « Trielo », l'assistant IA de triage des messages clients de Sereni

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Groupe (équipes de 3 à 4) |
| **Technologies** | Modélisation C4 (PlantUML / Mermaid / Structurizr), ADR (format MADR), Agile & Kanban (GitHub Projects ou Trello), Markdown, Git & GitHub. Aucun développement d'application. |
| **Prérequis** | [Cours C4 Architecture](../../../11-Gestion-Projet/03-C4-Architecture/) + [Cours ADR](../../../11-Gestion-Projet/02-ADR/) + [Cours Agile & Scrum](../../../11-Gestion-Projet/01-Agile-Scrum/) + [Cadrage & expression de besoins](../../../11-Gestion-Projet/02-cadrage-expression-besoins.md) + [Priorisation RICE / MoSCoW](../../../11-Gestion-Projet/04-objectifs-smart-priorisation-rice.md) |

## Contexte

### L'entreprise

**Sereni** est une scale-up française de l'assurance santé fondée à Nantes en 2018. Ses 90 salariés gèrent la complémentaire santé d'environ 40 000 assurés particuliers et de 600 TPE/PME clientes. Sereni se positionne comme « l'assurance qui répond vite » : la promesse commerciale est un premier retour humain en moins de deux heures ouvrées. L'équipe support, 12 conseillers, reçoit chaque jour entre 600 et 900 messages entrants (formulaire du site, e-mail, chat) : demandes de remboursement, questions sur les garanties, réclamations, résiliations, ou simple prise de contact commerciale.

Vous êtes missionné·e comme **équipe de conception** (avant-projet) : un binôme technique côté Sereni, un référent métier (la responsable du support) et un sponsor (le CTO). Aucune ligne de code applicatif ne vous est demandée cette semaine — la direction veut d'abord un **dossier de cadrage et d'architecture** solide avant d'engager un budget de développement.

### Le problème

Le support croule sous le volume. Aujourd'hui, chaque message est lu, catégorisé **à la main**, puis routé vers le bon conseiller. Résultat : les réclamations urgentes se noient parfois dans le flot des questions courantes, la promesse des « deux heures » n'est plus tenue une fois sur trois, et le sentiment de mécontentement d'un client n'est détecté que trop tard. Le CTO veut évaluer un **assistant IA de triage**, nom de code **« Trielo »** : à réception, chaque message serait automatiquement classé (thème, urgence, tonalité), enrichi des informations connues sur l'assuré ou l'entreprise cliente, puis proposé au bon conseiller avec un brouillon de réponse.

La direction ne veut **pas** entraîner un modèle maison : elle penche pour un **service d'IA cloud préexistant** (classification de texte, analyse de sentiment, génération de brouillon), à intégrer dans le système existant. Mais rien n'est tranché : quel fournisseur ? où hébergé ? à quel coût ? avec quelles garanties sur les données de santé (donc sensibles) ? Et surtout : par quoi commencer, dans quel ordre, avec quel périmètre pour une première version livrable en quelques semaines ?

### La question centrale

Le CTO résume l'enjeu de la semaine en une phrase, qui devient le fil rouge du projet. Chaque diagramme, chaque décision d'architecture et chaque story du backlog devra pouvoir se justifier par sa contribution à cette question :

> **« Avant d'écrire la moindre ligne de code, saurions-nous expliquer à un tiers ce que Trielo va faire, comment il s'assemble, pourquoi nous avons choisi ces briques, et dans quel ordre nous allons le construire ? »**

### Les sources de données

Vous ne construisez pas le système, mais votre cadrage doit s'appuyer sur des données et des services **réels** pour être crédible. Vous vous appuierez sur :

- **Un corpus de messages clients réels** pour dimensionner le besoin de classification et raisonner sur les catégories, les cas limites et la volumétrie. Au choix (un seul suffit) :
  - **Customer Support on Twitter** (Kaggle) — conversations réelles de support client, multi-secteurs : https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter
  - **UCI Drug Review Dataset** — avis textuels de patients avec note et thème, proche du domaine santé : https://archive.ics.uci.edu/dataset/462/drug+review+dataset+drugs+com
- **L'API Recherche d'entreprises** (data.gouv, ouverte, sans clé, 7 appels/seconde) pour l'enrichissement des clients TPE/PME (dénomination, SIREN/SIRET, code NAF) : https://recherche-entreprises.api.gouv.fr — documentation : https://recherche-entreprises.api.gouv.fr/docs
- **Les catalogues de services d'IA cloud réels** que vous comparerez dans vos décisions d'architecture, sur pièces (documentation, grilles tarifaires publiques) : Azure AI Language / Azure OpenAI, AWS Comprehend, Google Cloud Natural Language, **Mistral AI** (fournisseur français, argument de souveraineté). Documentation : https://learn.microsoft.com/azure/ai-services/language-service/ · https://docs.aws.amazon.com/comprehend/ · https://cloud.google.com/natural-language/docs · https://docs.mistral.ai/

> Vous ne collectez pas ces données en masse : vous les **explorez** (quelques centaines de lignes suffisent) pour ancrer votre cadrage dans le réel — catégories observées, longueur des messages, langue, cas ambigus, données personnelles présentes.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Analyser et formaliser un besoin** intégrant un service d'IA : recueillir les exigences fonctionnelles et non fonctionnelles auprès d'un commanditaire, distinguer le besoin métier de la solution technique, et cadrer un périmètre réaliste pour une première version.
- **Concevoir le cadre technique d'une application intégrant un service d'IA** : produire des diagrammes d'architecture C4 (contexte, conteneurs, composants) lisibles et cohérents, sélectionner les technologies et le service d'IA cloud adaptés, et justifier chaque choix structurant par un ADR argumenté.
- **Organiser la réalisation d'un projet en méthode Agile** : traduire le besoin en user stories avec critères d'acceptation, prioriser un backlog, le découper en sprints et le matérialiser dans un Kanban, de façon à guider une future équipe de développement.

## Travail demandé

Travail en équipe de 3 à 4 sur 5 jours. La méthode Agile n'est pas qu'un livrable : **vivez-la**. Tenez un daily de 10 minutes, mettez votre Kanban à jour en continu, et répartissez-vous les rôles (un·e facilitateur·rice, un·e porteur·se du besoin métier, des concepteur·rices). Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : sécurisez d'abord un dossier de cadrage complet et cohérent avant d'aller plus loin.

Ce projet ne comporte **pas de développement d'application**. Le seul « code » toléré est celui des diagrammes-as-code (PlantUML, Mermaid, Structurizr DSL) et, si vous le souhaitez, un court script d'exploration du corpus. La valeur du rendu est dans la **qualité du raisonnement**, pas dans un livrable exécutable.

### Phase 1 — Cadrage et expression du besoin (J1)

Aucun diagramme d'architecture ce jour-là : on part du besoin, pas de la solution. Explorez d'abord le corpus de messages choisi (quelques centaines de lignes) pour vous forger une intuition : quelles catégories de demandes reviennent ? quelle est la longueur typique d'un message ? quelle langue ? quels cas sont ambigus (un message qui est à la fois une question et une réclamation) ? quelles données personnelles apparaissent ?

Menez ensuite le cadrage comme un vrai atelier. Formalisez :

- les **parties prenantes** et leurs attentes (assuré, conseiller support, responsable support, CTO, DPO) ;
- les **exigences fonctionnelles** (que doit faire Trielo : classer, prioriser, enrichir, proposer un brouillon ?) et **non fonctionnelles** (délai de traitement, volumétrie de 600 à 900 messages/jour, disponibilité, confidentialité des données de santé, coût cible) ;
- une **matrice besoin ↔ solution** : pour chaque besoin, la fonctionnalité qui y répond, afin d'éviter le « effet catalogue » où l'on empile des fonctions sans lien avec le problème.

Qu'est-ce qui est **hors périmètre** de la première version ? Où placez-vous la frontière entre ce que fait l'IA et ce que valide un humain ? Notez ces décisions : elles nourriront vos ADRs.

**Résultat testable en fin de J1 :** un document de cadrage (parties prenantes, exigences fonctionnelles et non fonctionnelles, périmètre et hors-périmètre) présenté en 5 minutes au formateur, avec au moins trois observations concrètes tirées du corpus réel.

### Phase 2 — Diagrammes C4 : contexte et conteneurs (J2)

Passez à la conception. Produisez d'abord le **diagramme de contexte** (niveau 1) : Trielo au centre, les acteurs autour (assuré, conseiller), les systèmes externes avec lesquels il dialogue (le CRM support existant, le service d'IA cloud, l'API Recherche d'entreprises pour l'enrichissement B2B). Un lecteur non technique doit comprendre le périmètre en 30 secondes.

Descendez ensuite au **diagramme de conteneurs** (niveau 2) : quelles briques déployables composent Trielo ? Une API d'ingestion des messages, un composant d'appel au service d'IA, une base de données, une file d'attente, une interface conseiller ? Où passe la donnée ? Où appelle-t-on le service d'IA cloud ? Interrogez chaque flèche : que transporte-t-elle, dans quel sens, avec quel protocole ?

- Le service d'IA est-il appelé de façon **synchrone** (le conseiller attend) ou **asynchrone** (traitement en file) ? Qu'est-ce que cela change pour l'assuré ?
- Où atterrissent les **données de santé** ? Quittent-elles l'Union européenne en transitant par le service d'IA ? (Cette question ouvre un ADR.)

Vos diagrammes sont **versionnés** (diagrams-as-code de préférence) et intégrés au dépôt.

**Résultat testable en fin de J2 :** diagrammes C4 de contexte et de conteneurs, lisibles, avec une légende explicite des acteurs, systèmes et flux.

### Phase 3 — Composants et décisions d'architecture (ADR) (J3)

Zoomez sur **un** conteneur central — le composant qui orchestre la classification et l'appel au service d'IA — avec un **diagramme de composants** (niveau 3) : réception du message, validation, appel au service d'IA, post-traitement du résultat, enrichissement, routage. Montrez les responsabilités, pas l'implémentation.

Rédigez ensuite **au minimum quatre ADR** au format MADR, chacun documentant une décision structurante, avec le contexte, les options envisagées, la décision et ses conséquences :

- **Choix du service d'IA cloud** : comparez au moins trois offres réelles (par exemple Azure AI Language, AWS Comprehend, Mistral AI) sur des critères explicites — capacités (classification, sentiment, génération), langue française, localisation des données, coût au volume de Sereni, réversibilité. Quelle offre, et pourquoi ?
- **Traitement synchrone vs asynchrone** des messages entrants.
- **Confidentialité des données de santé** : anonymisation/pseudonymisation avant appel externe, résidence des données, base légale.
- **Un quatrième ADR de votre choix** : format de stockage, stratégie de fallback si le service d'IA est indisponible, ou périmètre du brouillon généré (l'humain valide-t-il toujours ?).

Un bon ADR ne cache pas les alternatives rejetées : il explique **pourquoi** on les a écartées.

**Résultat testable en fin de J3 :** un diagramme de composants et un registre d'au moins quatre ADR, dont le choix du service d'IA appuyé sur un comparatif chiffré.

### Phase 4 — Découpage Agile : user stories, backlog, sprints (J4)

Traduisez le tout en plan de réalisation pour une future équipe. Rédigez les **user stories** au format « En tant que… je veux… afin de… » avec des **critères d'acceptation** vérifiables, en couvrant les personas identifiés en phase 1. Appliquez le principe INVEST : une story indépendante, négociable, ayant de la valeur, estimable, petite, testable.

Constituez un **product backlog priorisé** : ordonnez les stories avec une méthode explicite (MoSCoW ou RICE, vues en cours) et justifiez l'ordre. Qu'est-ce qui doit absolument être dans la première version livrable, et qu'est-ce qui peut attendre ?

Découpez le backlog en **sprints** (au moins deux) avec un objectif de sprint par itération, et définissez une **Definition of Done** commune. Vérifiez la cohérence : chaque story se rattache-t-elle à une exigence de la phase 1 et à un élément d'architecture des phases 2-3 ? Aucune fonctionnalité ne doit sortir de nulle part.

**Résultat testable en fin de J4 :** un backlog priorisé de user stories avec critères d'acceptation, réparti en au moins deux sprints, avec objectifs de sprint et Definition of Done.

### Phase 5 — Kanban, consolidation et soutenance (J5)

Matérialisez votre organisation dans un **Kanban public** (GitHub Projects ou Trello) : colonnes de flux (À faire / En cours / En revue / Terminé), les stories du sprint 1 posées, et l'historique réel de votre semaine de conception (les tâches de cadrage, de diagrammes et d'ADR que vous avez vous-mêmes déplacées). Le Kanban doit raconter comment votre équipe a travaillé, pas seulement le plan futur.

Finalisez le README du dépôt (contexte, question centrale, sommaire des livrables, comment lire les diagrammes), vérifiez la cohérence de bout en bout (besoin → C4 → ADR → backlog), puis préparez une **soutenance** : vous présentez le dossier comme à un comité d'investissement qui décide s'il finance le développement de Trielo.

### Socle commun (obligatoire)

- Un **document de cadrage** : parties prenantes, exigences fonctionnelles et non fonctionnelles, périmètre et hors-périmètre, ancré dans l'exploration du corpus réel.
- Les **diagrammes C4** : contexte (niveau 1), conteneurs (niveau 2) et au moins un diagramme de composants (niveau 3), lisibles et versionnés.
- Un **registre d'au moins quatre ADR** au format MADR, dont le choix du service d'IA cloud appuyé sur un comparatif d'au moins trois offres réelles avec critères explicites.
- Un **backlog de user stories** avec critères d'acceptation, priorisé par une méthode explicite, découpé en au moins deux sprints avec Definition of Done.
- Un **Kanban public** reflétant le travail réel de l'équipe.
- Un **dépôt GitHub public** documenté avec un README qui relie tous les livrables.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Un **court script d'exploration** du corpus (Python/pandas) produisant deux ou trois statistiques réelles (répartition des catégories, longueur des messages) citées dans le cadrage.
- Une **maquette d'appel réel** à l'API Recherche d'entreprises (une requête, sa réponse JSON commentée) pour prouver la faisabilité de l'enrichissement B2B.
- Une **estimation de coût mensuel chiffrée** du service d'IA retenu, à partir des grilles tarifaires publiques et du volume de Sereni (600 à 900 messages/jour).
- Une **matrice de risques** (technique, réglementaire RGPD/données de santé, dépendance fournisseur) avec plans de mitigation.
- Une **cinquième vue C4** ou un diagramme de déploiement, ou l'export du workspace Structurizr.

Chaque bonus doit être documenté et rattaché au dossier, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du dépôt posté sur la plateforme) :

- Un **dépôt GitHub public** contenant l'ensemble du dossier de cadrage, avec un **README** structuré : contexte et question centrale, sommaire des livrables, comment lire les diagrammes, comment naviguer les ADR, auteurs de l'équipe et rôles tenus.
- Le **document de cadrage** (Markdown) : parties prenantes, exigences fonctionnelles et non fonctionnelles, périmètre / hors-périmètre, observations tirées du corpus réel.
- Les **diagrammes C4** aux niveaux contexte, conteneurs et composants, de préférence en diagrams-as-code (PlantUML, Mermaid ou Structurizr) versionnés, ou à défaut exportés en image intégrée au dépôt, avec légende.
- Le **registre d'ADR** (un fichier par décision, format MADR), dont l'ADR de choix du service d'IA cloud accompagné de son comparatif d'offres.
- Le **backlog de user stories** avec critères d'acceptation, la priorisation justifiée, le découpage en sprints et la Definition of Done.
- Le lien vers le **tableau Kanban public** (GitHub Projects ou Trello) reflétant l'historique de la semaine.
- Pour chaque **bonus** réalisé : livrable et preuve (script, capture, extrait JSON) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Soutenance du dossier de cadrage — 70 %** : 15 minutes de présentation en équipe + 10 minutes de questions, façon comité d'investissement. Vous déroulez le fil besoin → architecture → décisions → plan de réalisation, et répondez aux questions sur vos choix (pourquoi ce service d'IA, pourquoi asynchrone, comment protégez-vous les données de santé, pourquoi cette priorisation). La cohérence de bout en bout est examinée : chaque story doit se rattacher à une exigence et à un élément d'architecture.
- **Revue du dépôt — 30 %** : examen du dépôt GitHub public (structure, lisibilité, README), de la qualité des diagrammes C4 (respect des niveaux, légende, formalisme), de la rigueur des ADR (alternatives, justification, conséquences) et du backlog (format INVEST, critères d'acceptation, priorisation explicite).

> **Validation partielle** : un dossier dont la soutenance est incomplète mais dont les livrables écrits (cadrage, C4, ADR, backlog) sont structurés, versionnés et cohérents peut valider partiellement les compétences concernées. À l'inverse, une soutenance convaincante non appuyée par des livrables versionnés et documentés ne valide pas les critères documentaires.

Sans dépôt GitHub public accessible et sans livrables versionnés, le travail ne peut pas être évalué.

## Critères de performance

### Analyse et formalisation du besoin

- Les parties prenantes et leurs attentes sont identifiées et documentées.
- Les exigences fonctionnelles et non fonctionnelles sont formalisées et distinguées l'une de l'autre.
- Le périmètre et le hors-périmètre de la première version sont explicités et justifiés.
- Le cadrage est ancré dans le réel : au moins trois observations concrètes sont tirées de l'exploration du corpus de messages.

### Conception du cadre technique (C4 et ADR)

- Les trois niveaux C4 attendus sont produits (contexte, conteneurs, au moins un composant) et respectent le formalisme de chaque niveau, avec une légende lisible.
- Les diagrammes sont cohérents entre eux : les conteneurs découlent du contexte, les composants d'un conteneur.
- Au moins quatre ADR au format MADR documentent des décisions structurantes, chacun avec contexte, options, décision et conséquences.
- Le choix du service d'IA cloud s'appuie sur un comparatif d'au moins trois offres réelles avec des critères explicites (capacités, langue, localisation des données, coût, réversibilité).
- La protection des données de santé (anonymisation, résidence, base légale) fait l'objet d'une décision argumentée.

### Organisation Agile (user stories, backlog, sprints, Kanban)

- Les user stories respectent le format « En tant que… je veux… afin de… » et disposent de critères d'acceptation vérifiables.
- Le backlog est priorisé selon une méthode explicite (MoSCoW ou RICE) et l'ordre est justifié.
- Le backlog est découpé en au moins deux sprints, avec un objectif par sprint et une Definition of Done commune.
- Chaque user story se rattache à une exigence du cadrage et à un élément d'architecture (traçabilité de bout en bout).
- Le Kanban public reflète l'historique réel du travail de l'équipe pendant la semaine.

## Ressources

- [Cours C4 Architecture](../../../11-Gestion-Projet/03-C4-Architecture/)
- [Cours ADR](../../../11-Gestion-Projet/02-ADR/)
- [Cours Agile & Scrum](../../../11-Gestion-Projet/01-Agile-Scrum/)
- [Cadrage et expression de besoins](../../../11-Gestion-Projet/02-cadrage-expression-besoins.md)
- [Objectifs SMART et priorisation RICE / MoSCoW](../../../11-Gestion-Projet/04-objectifs-smart-priorisation-rice.md)
- [Documentation et communication (docs as code)](../../../11-Gestion-Projet/06-documentation-communication.md)
- Modèle C4 officiel (Simon Brown) : https://c4model.com
- C4-PlantUML : https://github.com/plantuml-stdlib/C4-PlantUML
- Structurizr DSL : https://docs.structurizr.com/dsl
- Format MADR (Markdown Any Decision Records) : https://adr.github.io/madr/
- Exemples d'ADR publics : https://github.com/joelparkerhenderson/architecture-decision-record
- Scrum Guide officiel (FR) : https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-French.pdf
- User Stories (Mountain Goat Software) : https://www.mountaingoatsoftware.com/agile/user-stories
- API Recherche d'entreprises (data.gouv, ouverte) : https://recherche-entreprises.api.gouv.fr/docs
- Corpus Customer Support on Twitter (Kaggle) : https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter
- UCI Drug Review Dataset : https://archive.ics.uci.edu/dataset/462/drug+review+dataset+drugs+com
- Azure AI Language : https://learn.microsoft.com/azure/ai-services/language-service/ · AWS Comprehend : https://docs.aws.amazon.com/comprehend/ · Mistral AI : https://docs.mistral.ai/
