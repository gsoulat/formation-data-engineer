# Brief S15 — Cadrer le besoin métier de NordRetail et animer un atelier de recueil

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S15 — Phase 2 : Solution BI pour l'analyse avancée |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Cahier des charges (Markdown / traitement de texte) · trame d'animation · matrice MoSCoW · Git/GitHub |
| **Prérequis** | [Analyse du besoin métier](../../../15-Business-Intelligence/03-Analyse-Besoin-Metier/) · [Cadrage & expression des besoins](../../../11-Gestion-Projet/02-cadrage-expression-besoins.md) · [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Son équipe data, encore jeune, a construit ces dernières semaines les fondations analytiques de l'enseigne : un modèle de données en étoile fiable, un jeu de mesures de gestion (chiffre d'affaires, marge, panier moyen, évolution par rapport à l'an dernier), puis un tableau de bord interactif et accessible que chaque responsable peut désormais explorer lui-même.

### Le problème

L'outil existe, il est propre, il est lisible par tous. Et pourtant, un signal inquiète la direction : lors des derniers comités, plusieurs responsables ont admis ne l'ouvrir « presque jamais ». Un tableau de bord techniquement réussi mais que personne n'utilise ne pilote rien. Avant d'engager la phase suivante — une solution BI plus avancée — la direction veut comprendre **ce dont les métiers ont réellement besoin**, plutôt que de continuer à empiler des indicateurs que l'équipe data juge intéressants.

Le risque est classique : construire pour soi, pas pour l'utilisateur. La responsable de Roubaix ne cherche pas les mêmes chiffres que le service marketing, qui lui-même ne décide pas comme la direction nationale. Votre mission de la semaine intervient donc **en amont** de la prochaine étape : cadrer proprement le besoin, aller le chercher auprès des métiers dans un atelier structuré, et en tirer une feuille de route d'évolution justifiée. Autrement dit, passer d'un outil que l'on montre à un outil que l'on a **commandé**.

### La question centrale

Toute la semaine, chaque document que vous produisez et chaque question que vous posez en atelier doit contribuer à répondre à la question que la direction vous a posée :

> **« De quoi les métiers de NordRetail ont-ils réellement besoin pour piloter leur activité — et comment le tableau de bord doit-il évoluer pour y répondre ? »**

### Les données

Cette semaine, votre « matière » n'est pas un fichier de ventes mais l'outil que vous avez construit et les personnes qui doivent s'en servir. Le tableau de bord NordRetail des semaines 11 à 13 (modèle en étoile, mesures, interactivité et accessibilité) sert de **support concret** à l'atelier : c'est l'objet que l'équipe métier va commenter, critiquer et faire évoluer. Pour situer les échanges, vous pouvez vous appuyer sur le schéma dimensionnel déjà présent dans le dépôt, qui décrit ce que l'outil sait aujourd'hui mesurer :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — table de faits (ventes, quantités, montants, marge).
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — points de vente (ville, type, surface, date d'ouverture).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — produits et catégories.
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — calendrier (année, trimestre, mois, week-end).
- [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) — objectifs commerciaux par magasin, utiles pour discuter des KPI attendus par la direction.

Aucune donnée n'est à télécharger ni à modifier : le travail de la semaine porte sur le **besoin** et sur la **démarche de cadrage**, pas sur les chiffres eux-mêmes.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Formuler une problématique métier claire** et la traduire dans un cahier des charges structuré (contexte, objectifs, utilisateurs cibles, KPI, contraintes, critères de succès).
- **Identifier et caractériser les utilisateurs cibles** d'un outil décisionnel et relier chaque indicateur à une décision concrète.
- **Concevoir et animer un atelier de recueil du besoin** : trame d'animation, ordre du jour, questions ouvertes qui font émerger les vrais besoins derrière les demandes.
- **Recueillir, reformuler et prioriser des besoins** exprimés par des interlocuteurs métier (méthode MoSCoW) et les rattacher à ce que l'outil sait — ou ne sait pas encore — faire.
- **Formuler des recommandations d'évolution argumentées**, justifiées par les besoins recueillis, et les restituer clairement à un lecteur métier non technique.

## Données fournies

Le schéma dimensionnel et les objectifs sont déjà présents dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Vous réutilisez le tableau de bord que votre binôme a construit précédemment (modèle en étoile + mesures + interactivité) comme support de l'atelier ; si vous n'en disposez pas, une capture d'écran ou une description écrite de ses pages et de ses indicateurs suffit pour faire réagir l'équipe métier. On ne modifie aucun fichier source : tout se joue dans les documents de cadrage.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est non seulement encouragée mais nécessaire : chaque binôme animera son atelier avec un autre binôme jouant l'équipe métier, et réciproquement. Chaque binôme produit néanmoins son propre cahier des charges, son propre compte rendu et ses propres recommandations. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et rédaction du cahier des charges, SANS atelier encore (J1)

Avant de convoquer qui que ce soit, posez le problème par écrit. Rédigez un **cahier des charges** (2 à 3 pages) du tableau de bord NordRetail. Il doit poser : le **contexte** (où en est l'enseigne, ce que l'outil fait déjà), la **problématique métier** en une phrase actionnable, les **objectifs** poursuivis, les **utilisateurs cibles** (qui consulte, pour décider quoi ?), les **KPI attendus** de chacun, les **contraintes** (protection des données personnelles des clients, accessibilité pour tous, périmètre de ce qui est dans ou hors du projet) et les **critères de succès** qui permettront de dire, plus tard, que l'outil est utile. Interrogez chaque indicateur que vous listez : *quelle décision un responsable prend-il grâce à ce chiffre ?* Un KPI qui ne débouche sur aucune décision n'a pas sa place dans le cahier des charges. Initialisez (ou mettez à jour) votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Préparation de l'atelier de recueil du besoin (J1-J2)

Un atelier ne s'improvise pas. Préparez une **trame d'animation** : objectif de la séance, ordre du jour minuté, durée (30 à 45 min), méthode d'animation, et surtout un jeu de **questions ouvertes** pour faire parler les métiers sans leur souffler la réponse. Bannissez les questions fermées qui valident vos propres idées ; privilégiez les questions du type « quelle décision veux-tu prendre avec ce chiffre ? », « qu'est-ce qui te fait perdre du temps aujourd'hui ? », « que regardes-tu en premier le lundi matin ? ». Prévoyez comment vous allez **capter et tracer** ce qui se dit (qui note, sur quel support) pour ne rien perdre. Comment éviterez-vous que l'atelier ne dérive vers une simple démonstration de votre outil ?

### Phase 3 — Animation de l'atelier (jeu de rôle) (J2-J3)

Organisez l'atelier avec un autre binôme jouant l'**équipe métier** : un responsable de magasin, un profil marketing, un membre de la direction — trois postures qui n'ont pas les mêmes priorités. Présentez brièvement le tableau de bord existant comme point de départ, puis **écoutez** : recueillez les besoins, les frustrations, les manques. Reformulez systématiquement ce que vous entendez pour vérifier que vous avez bien compris (« si je te suis, ce qu'il te manque c'est… »). Prenez appui sur les postures : ce que réclame la responsable de Roubaix (comparer *son* magasin à son objectif) n'est pas ce que cherche la direction nationale (un pilotage consolidé de l'enseigne). Consignez chaque besoin exprimé, en distinguant la **demande** (ce qui est dit) du **besoin** réel (ce qui est visé). À votre tour, jouez l'équipe métier pour le binôme partenaire.

### Phase 4 — Reformulation et priorisation (J3-J4)

Faites le tri. Rédigez un **compte rendu d'atelier** qui liste les besoins recueillis, chacun reformulé clairement. Priorisez-les avec la méthode **MoSCoW** : *indispensable* (Must), *souhaitable* (Should), *optionnel* (Could), *hors périmètre* (Won't). Pour chaque besoin, indiquez s'il est **déjà couvert** par le tableau de bord actuel, **partiellement couvert**, ou **absent** — et à quel KPI ou quel visuel il se rattacherait. Un besoin classé « indispensable » mais aujourd'hui absent devient un candidat prioritaire pour la suite. Justifiez vos arbitrages : sur quel critère un besoin est-il « indispensable » plutôt que « souhaitable » — la fréquence de la décision, son enjeu financier, le nombre d'utilisateurs concernés ?

### Phase 5 — Recommandations, restitution et mise en ligne (J5)

Formulez **3 à 5 recommandations d'évolution** du tableau de bord, chacune justifiée par un ou plusieurs besoins recueillis en atelier et reliée à la question centrale. Une recommandation n'est pas une idée en l'air : elle nomme le besoin d'origine, propose une évolution concrète (un nouvel indicateur, une nouvelle vue, un filtre manquant) et dit à qui elle profite. Rassemblez le cahier des charges, la trame, le compte rendu priorisé et les recommandations dans un livrable propre destiné à la direction : pas de jargon technique, des phrases décidables. Soignez le README et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : cahier des charges (problématique, utilisateurs, KPI, contraintes, critères de succès), trame d'animation avec questions ouvertes, atelier joué et compte rendu des besoins reformulés, priorisation MoSCoW rattachée au tableau de bord, 3 à 5 recommandations argumentées, dépôt public à jour.

### Pour aller plus loin (bonus)

- Construisez une **cartographie des utilisateurs** (persona léger par profil : rôle, décisions, indicateurs suivis, frustrations) pour appuyer le cahier des charges.
- Traduisez vos recommandations en une **feuille de route** simple (court / moyen terme) avec une estimation de l'effort perçu.
- Reliez chaque KPI retenu aux [`objectifs_2024.csv`](../data/objectifs_2024.csv) : quels besoins métier nécessiteraient de croiser le réalisé avec l'objectif, et le tableau de bord le permet-il déjà ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - un **cahier des charges** (`CAHIER_DES_CHARGES.md` ou PDF, 2-3 pages) : contexte, problématique, objectifs, utilisateurs cibles, KPI, contraintes, critères de succès ;
  - la **trame d'animation** de l'atelier (`TRAME_ATELIER.md`) : objectifs, ordre du jour, durée, méthode, questions ouvertes ;
  - un **compte rendu d'atelier** (`COMPTE_RENDU.md`) : besoins reformulés + priorisation MoSCoW rattachée au tableau de bord ;
  - une **liste de 3 à 5 recommandations** argumentées (dans le compte rendu ou un fichier dédié) ;
  - un **`README.md`** : description du projet, démarche suivie, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Documents de cadrage (60 %)** : clarté de la problématique et du cahier des charges, pertinence des utilisateurs et KPI identifiés, qualité de la trame et des questions ouvertes, rigueur de la priorisation MoSCoW, solidité de l'argumentation des recommandations.
- **Restitution orale (40 %)** : 10 minutes de présentation du cadrage et des recommandations à un « comité de direction » (le formateur et un autre binôme) + 5 minutes de questions. La qualité de l'animation observée pendant l'atelier (Phase 3) est prise en compte dans ce volet.

**Validation partielle** : un binôme dont tous les documents ne sont pas totalement finalisés mais qui démontre une problématique métier bien posée ET une démarche de recueil du besoin structurée (atelier réellement animé, besoins reformulés) peut valider partiellement les compétences travaillées.

## Critères de performance

**Cadrer le besoin métier**
- Le cahier des charges formule clairement la problématique métier et les objectifs.
- Les utilisateurs cibles, les KPI attendus et les contraintes (données personnelles, accessibilité, périmètre) sont identifiés.
- Chaque KPI retenu est rattaché à une décision métier concrète.
- Des critères de succès du tableau de bord sont explicités.

**Recueillir et prioriser le besoin**
- Une trame d'animation est préparée avec un ordre du jour et des questions ouvertes.
- L'atelier (jeu de rôle) a été animé et les besoins sont reformulés dans un compte rendu.
- Les besoins sont priorisés (MoSCoW) et rattachés au tableau de bord (couvert / partiel / absent).
- Les arbitrages de priorisation sont justifiés par un critère explicite.

**Restituer et recommander**
- 3 à 5 recommandations d'évolution sont formulées et justifiées par les besoins recueillis.
- La restitution est claire, sans jargon technique, et répond à la question centrale.
- Le dépôt GitHub public est complet (cahier des charges + trame + compte rendu + README).

## Ressources

- Module de cours — [Analyse du besoin métier](../../../15-Business-Intelligence/03-Analyse-Besoin-Metier/)
- Module de cours — [Cadrage & expression des besoins](../../../11-Gestion-Projet/02-cadrage-expression-besoins.md)
- Rappel — [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/)
- Rappel — [Accompagnement métier](../../../15-Business-Intelligence/13-Accompagnement-Metier/)
- Méthode de priorisation MoSCoW (indispensable / souhaitable / optionnel / hors périmètre)
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_2 — Solution BI avancée](../BRIEF_2_SOLUTION_BI_AVANCEE.md)
