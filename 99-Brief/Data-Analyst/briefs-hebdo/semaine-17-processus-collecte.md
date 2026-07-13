# Brief S17 — Cartographier les sources et concevoir un processus de collecte RGPD pour NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S17 — Phase 3 : Industrialiser l'alimentation du tableau de bord |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Modélisation de flux (draw.io / Excalidraw), tableur, Markdown, Git/GitHub — **aucun code cette semaine** |
| **Prérequis** | [Collecte des données](../../../15-Business-Intelligence/14-Collecte-Donnees/) · [Éthique, biais & RGPD](../../../15-Business-Intelligence/12-Ethique-Biais-RGPD/) · [Extraction SQL](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes, Amiens) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Son équipe data, encore jeune, a déjà audité les ventes, produit ses premiers indicateurs et livré un tableau de bord de pilotage. Vous en faites partie, aux côtés d'un responsable BI, d'une contrôleuse de gestion et, désormais, d'un correspondant DSI qui veille à la conformité.

### Le problème

Le tableau de bord fonctionne, mais son alimentation reste **artisanale** : chaque semaine, quelqu'un exporte à la main un CSV de caisse, récupère un fichier d'objectifs par mail, télécharge un extrait de la base clients… Les fichiers arrivent de partout, dans des formats hétérogènes, sans traçabilité. Pire : parmi ces données circulent des informations **directement rattachées à des personnes physiques** (nom, prénom, email des clients fidélité). Tant que le flux n'est ni cartographié ni encadré, NordRetail pilote à l'aveugle sur le plan technique **et** s'expose sur le plan réglementaire.

La direction veut passer d'une collecte bricolée à un **processus de collecte structuré et conforme**. Avant d'automatiser quoi que ce soit — et avant d'écrire la moindre ligne de pipeline —, la DSI vous demande de **poser le plan** : d'où vient chaque donnée, qui la possède, à quel rythme elle change, et comment la collecter sans enfreindre le RGPD. Cette semaine ne produit pas de code : elle produit la **conception** qui rendra l'automatisation possible et défendable.

### La question centrale

Toute la semaine, chaque schéma et chaque tableau que vous produisez doit contribuer à répondre à la question que la DSI vous a posée :

> **« Comment NordRetail peut-elle collecter et centraliser ses données de façon fiable, traçable et conforme au RGPD, sans perdre la confiance de ses clients ? »**

### Les données

Cette semaine, vous n'analysez pas les données : vous les **inventoriez**. Vous observez leurs en-têtes et leur schéma pour comprendre ce que chaque source contient, sans jamais l'exécuter ni la modifier. Le dossier `data/` du dépôt vous sert de photographie du système d'information de NordRetail :

- des exports de caisse, consolidés ou par ville ;
- un référentiel produits ;
- un fichier d'objectifs transmis par la direction ;
- une base relationnelle décrivant clients, commandes, produits et magasins — c'est là que se cachent les données personnelles.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Cartographier les sources de données d'une organisation** : recenser chaque source, son format, son propriétaire métier, sa fréquence de mise à jour et son volume.
- **Identifier les données à caractère personnel** dans un système d'information et distinguer les sources sensibles des sources anonymes.
- **Rattacher un traitement à une finalité et une base légale** (contrat, consentement, intérêt légitime) au sens du RGPD.
- **Concevoir un schéma de processus de collecte** allant de la source jusqu'à une zone de réception, en positionnant explicitement les étapes de minimisation et de pseudonymisation.
- **Rédiger un registre de traitement** synthétique (finalité, données, durée de conservation, mesures de sécurité) lisible par un responsable non technique.

## Données fournies

Toutes les sources à cartographier sont déjà présentes dans le dépôt, dans [`99-Brief/Data-Analyst/data/`](../data/). Vous travaillez **en observation seule** : on ouvre les en-têtes, on lit le schéma, on ne modifie ni n'exécute rien.

- [`../data/ventes_consolidees.csv`](../data/ventes_consolidees.csv) — export consolidé des ventes tous magasins.
- [`../data/ventes_lille.csv`](../data/ventes_lille.csv), [`../data/ventes_roubaix.csv`](../data/ventes_roubaix.csv), [`../data/ventes_tourcoing.csv`](../data/ventes_tourcoing.csv), [`../data/ventes_valenciennes.csv`](../data/ventes_valenciennes.csv) — exports de caisse par point de vente.
- [`../data/referentiel_produits.csv`](../data/referentiel_produits.csv) — catalogue produits (colonnes `produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`, `marque`, `actif`).
- [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx) — objectifs de CA par magasin et par mois, transmis par la direction.
- [`../data/setup.sql`](../data/setup.sql) — script de la base relationnelle : tables `clients` (`client_id`, `prenom`, `nom`, `ville`, `segment`, `date_inscription`, `email`), `commandes`, `produits`, `magasins`.

Prenez le temps de regarder **quelles colonnes désignent une personne** : c'est le point de bascule de tout le brief.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit sa propre cartographie, son propre schéma et son propre registre. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et lecture des sources, SANS schéma ni tableau final (J1)

Avant de cartographier, appropriez-vous le terrain. Ouvrez chaque fichier de `data/` dans un tableur ou un éditeur et regardez uniquement ses **en-têtes** ; ouvrez `setup.sql` et repérez les instructions `CREATE TABLE` pour comprendre le schéma relationnel. Posez-vous les bonnes questions : une même vente apparaît-elle dans plusieurs sources (un export par ville *et* un consolidé) ? Où se trouve l'identité des clients ? Qu'est-ce qui distingue une donnée « produit » (publique, stable) d'une donnée « client » (personnelle, sensible) ? Notez, en quelques phrases, ce que vous croyez être le **propriétaire métier** de chaque source (caisse ? marketing ? direction ? DSI ?) et à quelle **fréquence** elle bouge. Ces hypothèses guideront votre cartographie. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Inventaire et cartographie des sources (J1-J2)

Recensez **au moins 6 sources distinctes**. Pour chacune, documentez : nom, format (CSV / XLSX / SQL / API), donnée contenue, propriétaire métier, fréquence de mise à jour, volume estimé. Synthétisez le tout dans un **tableau de cartographie** unique, colonnes : `Source | Format | Donnée contenue | Propriétaire | Fréquence | Volume | Données personnelles (O/N)`. Interrogez chaque ligne : deux sources qui décrivent la même réalité (ventes par ville vs. consolidé) sont-elles redondantes ou complémentaires ? Laquelle fait foi ? À ce stade, comment décideriez-vous quelle source devient la **référence** pour alimenter la BI ?

### Phase 3 — Repérage des données personnelles, finalités et bases légales (J2-J3)

Passez la cartographie au filtre du RGPD. Marquez précisément les champs qui relèvent de données à caractère personnel — `email`, `nom`, `prenom`, ou un `client_id` rattachable à une personne. Pour chaque donnée personnelle, indiquez la **finalité** du traitement (pourquoi NordRetail la collecte : programme de fidélité ? relation contractuelle ? analyse marketing ?) et sa **base légale** parmi les fondements prévus par le RGPD (exécution d'un contrat, consentement, intérêt légitime…). Un `client_id` seul, détaché du nom et de l'email, est-il encore une donnée personnelle ? Cette question doit orienter la suite : la réponse conditionne votre schéma de pseudonymisation.

### Phase 4 — Schéma du processus de collecte (J3-J4)

Dessinez le flux, à l'aide d'un outil de schéma (draw.io, Excalidraw) ou d'un croquis propre photographié. Représentez, pour chaque source : **source → mode de collecte** (export manuel, connecteur, appel d'API, requête SQL) **→ zone de réception** (dossier brut / staging) **→ étape de pseudonymisation ou de minimisation**. Faites apparaître **clairement où** les données personnelles sont réduites au strict nécessaire ou remplacées par un identifiant technique avant d'entrer dans la BI. Le schéma doit se lire seul : un lecteur doit comprendre, sans explication orale, à quel endroit du flux la conformité est assurée. Où placez-vous la frontière entre la « zone identifiante » et la « zone d'analyse » ?

### Phase 5 — Registre de traitement, synthèse et mise en ligne (J5)

Rédigez un **mini-registre de traitement** (4 à 5 entrées) : pour chaque traitement, finalité, données collectées, durée de conservation, et mesures de sécurité. Rédigez ensuite une **synthèse** (8 à 15 lignes) qui répond frontalement à la question centrale : comment NordRetail peut-elle collecter et centraliser ses données de façon fiable et conforme ? Cette synthèse s'adresse à la DSI et à la direction : pas de jargon technique, des recommandations actionnables (quelle source devient la référence, quels champs pseudonymiser, quels risques subsistent). Soignez le README, rangez vos livrables et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : au moins 6 sources cartographiées, données personnelles repérées avec finalité et base légale, schéma de collecte avec étape de pseudonymisation, mini-registre de traitement, synthèse, dépôt public à jour.

### Pour aller plus loin (bonus)

- Proposez pour chaque source un **mode de collecte automatisable** (connecteur, API, planification SQL) et justifiez lequel remplace avantageusement l'export manuel actuel.
- Ajoutez une **durée de conservation différenciée** par catégorie de donnée (ventes vs. données clients) et argumentez-la.
- Confrontez `ventes_consolidees.csv` aux exports par ville : identifiez le risque de **double comptage** dans la collecte et proposez la règle de déduplication à appliquer en amont de la BI.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - un **document de cartographie** (`CARTOGRAPHIE.md` ou PDF) avec le tableau des sources ;
  - le **schéma du processus de collecte** (export draw.io/Excalidraw ou photo du croquis, intégré au dépôt) ;
  - un **mini-registre de traitement** (dans le document ou un fichier dédié) ;
  - une **synthèse** rédigée pour un lecteur métier / DSI ;
  - un **`README.md`** : description du projet, méthode, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Dossier de conception (60 %)** : exhaustivité et justesse de la cartographie, pertinence du repérage des données personnelles (finalité + base légale), qualité et lisibilité du schéma de collecte, rigueur du registre de traitement.
- **Restitution orale (40 %)** : 10 minutes de présentation du processus conçu à un « comité DSI » (le formateur et un autre binôme) + 5 minutes de questions, dont au moins une portant sur un arbitrage RGPD.

**Validation partielle** : un binôme dont le schéma n'est pas totalement finalisé mais dont la cartographie et le raisonnement RGPD (données personnelles, finalités, bases légales) sont structurés et documentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Cartographier les sources**
- Au moins 6 sources sont inventoriées avec format, donnée contenue, propriétaire, fréquence et volume.
- Le tableau distingue clairement les sources contenant des données personnelles de celles qui n'en contiennent pas.
- Le lien avec les vrais fichiers du dépôt (`data/`) est explicite et exact.

**Traiter la conformité RGPD**
- Chaque champ à caractère personnel (`email`, `nom`, `prenom`, `client_id` rattachable) est identifié.
- Chaque donnée personnelle est associée à une finalité ET une base légale cohérente.
- Le raisonnement sur la nature personnelle d'un identifiant technique (`client_id` pseudonymisé) est explicité.

**Concevoir le processus de collecte**
- Le schéma représente le flux source → mode de collecte → zone de réception.
- Une étape de pseudonymisation ou de minimisation est positionnée et localisée sans ambiguïté.
- Le schéma est lisible de façon autonome, sans explication orale.

**Restituer et tracer**
- Le mini-registre mentionne finalité, données, durée de conservation et mesures de sécurité.
- La synthèse répond explicitement à la question centrale, sans jargon, avec des recommandations actionnables.
- Le dépôt GitHub public est complet (cartographie + schéma + registre + README).

## Ressources

- Module de cours — [Collecte des données](../../../15-Business-Intelligence/14-Collecte-Donnees/)
- Module de cours — [Éthique, biais & RGPD](../../../15-Business-Intelligence/12-Ethique-Biais-RGPD/)
- Rappels — [Extraction SQL](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/)
- [CNIL — Le registre des activités de traitement](https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement)
- [CNIL — Les bases légales d'un traitement](https://www.cnil.fr/fr/les-bases-legales)
- Outil de schéma : https://www.drawio.com/ · https://excalidraw.com/
