# Brief S24 — Défendre le tableau de bord de NordRetail en soutenance blanche

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S24 — Phase 3 : Préparer l'évaluation finale & la soutenance |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Confirmé |
| **Modalité** | Individuel |
| **Technologies** | Outil de présentation (PowerPoint / Google Slides / Canva) · Power BI (démo du dashboard) · outil de test de contraste · Git/GitHub |
| **Prérequis** | [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/) · [Accompagnement métier](../../../15-Business-Intelligence/13-Accompagnement-Metier/) · [Préparation à l'évaluation finale](../../../15-Business-Intelligence/18-Preparation-Certification/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Vous faites partie de son équipe data, désormais rodée : au fil des semaines, vous avez audité les ventes, bâti un modèle en étoile, calculé les indicateurs de pilotage et assemblé un tableau de bord interactif et accessible. Le travail est fait — reste à le **faire comprendre et adopter** par ceux qui décident.

### Le problème

Le comité de direction de NordRetail a bloqué un créneau : vous allez présenter le tableau de bord de pilotage à un auditoire mêlant profils très différents — un directeur commercial pressé qui veut des décisions, une contrôleuse de gestion attentive aux chiffres, un responsable des systèmes d'information qui sondera vos choix techniques, et une élue au comité d'entreprise, malvoyante, qui doit pouvoir suivre votre propos comme les autres. Un tableau de bord, aussi juste soit-il, ne vaut que s'il est **compris, cru et utilisé**. Une donnée mal restituée est une donnée perdue.

Cette semaine est votre **répétition générale**. Vous préparez et passez une **soutenance blanche** dans les conditions réelles de l'épreuve : un support structuré, une démonstration du dashboard, un temps d'oral chronométré, une salve de questions qui challengent vos choix, puis un retour critique. L'enjeu n'est pas de refaire l'analyse, mais d'apprendre à la **défendre** — poser un fil narratif, tenir le temps, argumenter un indicateur, dire « je ne sais pas » avec méthode, et rendre votre message accessible à toute votre audience.

### La question centrale

Toute la semaine, chaque slide, chaque phrase, chaque transition que vous préparez doit servir un seul objectif :

> **« Comment restituer le tableau de bord de NordRetail pour qu'un décideur pressé, un expert exigeant et une personne en situation de handicap en repartent tous convaincus et outillés pour agir ? »**

### Les données

Aucun nouveau jeu de données cette semaine : vous vous appuyez sur **vos livrables des semaines précédentes**, construits sur le socle NordRetail. Vous ne produisez plus d'analyse, vous en organisez la restitution. Pour rendre votre démonstration crédible et vérifiable, gardez sous la main :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) et les dimensions [`../data/Dim_Client.csv`](../data/Dim_Client.csv), [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv), [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv), [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — le modèle en étoile qui alimente votre dashboard ;
- [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) — les cibles commerciales que vos indicateurs comparent au réalisé.

Votre tableau de bord Power BI et vos rapports de synthèse antérieurs sont le matériau de votre soutenance.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Structurer un support de présentation** selon un fil narratif complet : besoin métier → sources & conformité → traitement des données → analyse & indicateurs → tableau de bord → recommandations.
- **Adapter le fond et la forme à l'auditoire** : parler « décision » à un dirigeant, « chiffre » à un contrôleur de gestion, « technique » à un responsable SI, sans perdre personne.
- **Rendre une restitution accessible à tous**, y compris aux personnes en situation de handicap : contrastes suffisants, information jamais portée par la seule couleur, texte lisible, propos qui n'exige pas de « voir » l'écran pour être suivi.
- **Démontrer un tableau de bord en direct** sur un scénario d'usage concret, sans se perdre dans l'outil.
- **Défendre ses choix et gérer les questions** : justifier un indicateur, un visuel, un traitement de données personnelles, et répondre à une objection avec honnêteté et méthode.
- **Tenir la posture et le temps** d'un oral d'évaluation finale, et transformer un retour critique en axes de progression concrets.

## Données fournies

Le socle NordRetail est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Aucune donnée n'est à télécharger ni à retraiter. Vous réutilisez le tableau de bord et les analyses que vous avez produits lors des semaines précédentes ; le rôle des fichiers cette semaine est de **sourcer et rendre vérifiable** votre démonstration, pas d'alimenter une nouvelle analyse.

## Travail demandé

Travail **individuel sur 5 jours**. L'entraide et les passages « blancs » croisés entre camarades sont encouragés — se voir présenter et présenter à d'autres est le meilleur entraînement — mais chacun prépare et passe **sa propre soutenance**. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus à l'aise.

### Phase 1 — Cadrage de la restitution, SANS construire de slide (J1)

Avant d'ouvrir votre outil de présentation, cadrez votre intention. Qui est dans la salle, et qu'attend chacun ? Notez, pour chaque profil d'auditeur (directeur commercial, contrôleuse de gestion, responsable SI, élue malvoyante), le **message-clé** qu'il doit retenir et l'objection qu'il risque de soulever. Quel est le **fil rouge** de votre présentation — l'histoire en une phrase que vous voulez que la salle retienne ? Où placez-vous l'accroche, et sur quelle recommandation voulez-vous conclure ? Réfléchissez déjà à ce que « accessible à une personne malvoyante » impose à votre support et à votre façon de parler : peut-on suivre votre propos sans voir l'écran ? Rédigez ce cadrage en une page (audience, message par profil, plan narratif, angle de la démo). Initialisez ou mettez à jour votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Construction du support (J1-J2)

Bâtissez votre présentation (10 à 15 diapositives) en suivant le fil narratif : contexte et besoin métier de NordRetail → sources de données et conformité (données personnelles, minimisation, anonymisation) → traitement et fiabilisation des données → analyse et indicateurs de pilotage → tableau de bord → conclusions et recommandations. Chaque slide porte **une idée** et un titre qui se lit seul. Soignez l'accessibilité dès la conception : palette à contraste suffisant (visez un ratio d'au moins 4,5:1, vérifié avec un outil de test), information jamais codée par la seule couleur, police assez grande pour être lue du fond d'une salle. Une présentation surchargée noie le message : que pouvez-vous retirer sans rien perdre ?

### Phase 3 — Démonstration préparée du dashboard (J2-J3)

Scénarisez une démonstration courte (2 à 3 minutes) de votre tableau de bord autour d'un cas d'usage concret : par exemple, « la direction veut identifier le magasin qui sous-performe par rapport à ses objectifs, et comprendre pourquoi ». Écrivez le déroulé exact — quels filtres, quel visuel, quelle lecture — et répétez-le jusqu'à ce qu'il soit fluide. Anticipez l'imprévu : que faites-vous si l'outil rame ou si un chiffre surprend en direct ? Une démo n'impressionne pas par le nombre de clics, mais par la clarté de la question à laquelle elle répond en trente secondes.

### Phase 4 — Oral chronométré et questions (J3-J4)

Passez votre soutenance devant un « comité de direction » (le formateur et un ou deux camarades jouant le jury), dans les conditions de l'épreuve : **20 minutes d'oral maximum**, démo comprise, suivies de **5 à 10 minutes de questions**. Travaillez l'accroche, les transitions entre parties, la conclusion. Le jury vous challenge : pourquoi cet indicateur plutôt qu'un autre ? pourquoi ce type de graphique ? comment avez-vous traité les données personnelles des clients ? quelle est la limite de cette analyse ? Entraînez-vous à défendre un choix… mais aussi à reconnaître une incertitude : « je ne sais pas précisément, voici comment je le vérifierais » vaut mieux qu'une réponse inventée. Adaptez vos réponses au profil qui questionne.

### Phase 5 — Retour, axes de progression et mise en ligne (J5)

Recueillez le **retour du jury** à l'aide d'une grille de restitution (clarté, structure, gestion du temps, qualité des réponses, accessibilité, posture). Identifiez **trois axes d'amélioration concrets** pour le vrai oral de soutenance finale, et pour chacun l'action précise que vous mènerez (ex. « raccourcir la partie ETL de 4 à 2 slides », « répéter la démo pour tenir sous 3 min »). Finalisez votre support, votre fiche de passage et poussez l'ensemble sur GitHub avec un README clair. Cette semaine ne se juge pas à la perfection du passage, mais à la **lucidité du diagnostic** que vous en tirez.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : cadrage d'audience documenté, support de 10-15 slides à fil narratif complet et accessible, démo scénarisée du dashboard, oral tenu en 20 minutes avec gestion des questions, grille de retour renseignée et 3 axes d'amélioration formulés, dépôt public à jour.

### Pour aller plus loin (bonus)

- Produisez **deux versions** de l'accroche (une orientée « décision business », une orientée « rigueur méthodologique ») et testez laquelle porte le mieux selon l'auditoire.
- Enregistrez votre passage (audio ou vidéo) et faites votre **auto-analyse** : tics de langage, débit, temps réel par partie.
- Préparez une **fiche « objections / réponses »** anticipant les 5 questions les plus probables du jury et vos réponses argumentées.
- Rédigez une version « une page » de votre restitution (executive summary) pour un décideur qui n'assisterait pas à l'oral.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **support de présentation** (PDF ou PPTX) — 10 à 15 diapositives, fil narratif complet et accessible ;
  - la **fiche de cadrage** de la Phase 1 (audience, messages par profil, plan narratif) ;
  - le **déroulé de la démonstration** (scénario d'usage + étapes) ;
  - un **`README.md`** : description du projet, contexte de la soutenance, contenu du dépôt, auteur.
- La **grille de retour du jury** complétée, accompagnée de vos **3 axes d'amélioration** (constat → action).
- Une **fiche de passage** (ou un enregistrement) attestant du déroulé de l'oral blanc.

## Modalités d'évaluation

Évaluation en deux volets :

- **Passage oral et gestion des questions (60 %)** : clarté et structure du propos, respect du temps, qualité de la démo, capacité à défendre ses choix et à gérer les objections, posture, accessibilité du discours.
- **Support et exploitation du retour (40 %)** : qualité et accessibilité des slides, cohérence du fil narratif, pertinence des 3 axes d'amélioration, complétude du dépôt.

**Validation partielle** : un apprenant dont le passage n'est pas encore abouti (timing dépassé, une question mal gérée) mais dont le support est structuré et accessible, et qui tire de son passage un diagnostic lucide et des axes d'amélioration précis, peut valider partiellement les compétences travaillées.

## Critères de performance

**Structurer et adapter la restitution**
- Le cadrage d'audience identifie, par profil d'auditeur, un message-clé et une objection anticipée.
- Le support suit un fil narratif complet : besoin → sources & conformité → traitement → analyse & indicateurs → dashboard → recommandations.
- Le contenu et le vocabulaire sont adaptés aux différents profils présents (décideur, expert chiffres, expert technique).

**Rendre la restitution accessible à tous**
- La palette respecte un contraste suffisant (ratio visé ≥ 4,5:1), vérifié avec un outil, et l'information n'est jamais portée par la seule couleur.
- Les titres, la taille de texte et le déroulé oral permettent de suivre le propos sans dépendre uniquement de la vue.

**Démontrer et défendre**
- La démonstration du dashboard illustre un scénario d'usage concret et répond à une question métier en quelques minutes.
- L'oral tient dans 20 minutes avec accroche, transitions et conclusion identifiables.
- Les choix (indicateur, visuel, traitement des données personnelles) sont défendus face aux questions ; une incertitude est assumée avec une méthode de vérification.

**Progresser**
- La posture (regard, débit, gestion du temps et du stress) est travaillée et perceptible.
- La grille de retour est complétée et 3 axes d'amélioration concrets (constat → action) sont formulés.
- Le dépôt GitHub public est complet (support + cadrage + déroulé démo + README).

## Ressources

- Module de cours — [Restitution & storytelling](../../../15-Business-Intelligence/08-Restitution-Storytelling/)
- Module de cours — [Accompagnement métier](../../../15-Business-Intelligence/13-Accompagnement-Metier/)
- Module de cours — [Préparation à l'évaluation finale](../../../15-Business-Intelligence/18-Preparation-Certification/)
- Rappels accessibilité — [Visualisations avancées & WCAG](../../../15-Business-Intelligence/11-Visualisations-Avancees/)
- Aboutissement du parcours — projet final : [BRIEF_3 — Projet final](../BRIEF_3_PROJET_FINAL.md)
