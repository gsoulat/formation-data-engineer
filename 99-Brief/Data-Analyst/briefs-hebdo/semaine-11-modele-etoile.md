# Brief S11 — Poser les fondations analytiques de NordRetail : le modèle en étoile

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S11 — Phase 2 : Construire une solution BI pour l'analyse avancée |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Power BI Desktop, Power Query, modélisation dimensionnelle (faits/dimensions), Git/GitHub |
| **Prérequis** | [EDA des ventes (S06)](semaine-06-eda-ventes-nordretail.md) · [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/) · [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution des Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Depuis l'audit des ventes mené en amont (S06), l'équipe data — un responsable BI, une contrôleuse de gestion et vous — a gagné la confiance de la direction. Le **tableau de bord de pilotage** promis se construit désormais semaine après semaine, brique par brique.

### Le problème

L'audit a prouvé que les données pouvaient être fiabilisées, mais un problème d'organisation demeure : **chaque service travaille sur son propre fichier**. Les exports Excel qui circulent entre le commerce, la logistique et la finance ne concordent jamais — un même chiffre d'affaires apparaît sous trois valeurs différentes selon le tableur consulté. Empiler des tables « à plat » et des colonnes redondantes mène à des analyses fausses et impossibles à maintenir.

Avant de tracer le moindre graphique dans l'outil de BI, la cellule data décide de poser une **fondation propre et partagée** : un modèle de données analytique unique, sur lequel toutes les analyses futures — CA par ville, par mois, par catégorie, par segment client — s'appuieront sans ambiguïté. C'est le socle qui transformera une collection de fichiers en un vrai système décisionnel.

### La question centrale

Toute la semaine, chaque choix de modélisation que vous faites doit servir cet objectif :

> **« Comment structurer les données de NordRetail pour qu'une seule et même vérité alimente, demain, tous les indicateurs du tableau de bord ? »**

### Les données

Fini le fichier unique : cette semaine, les données arrivent **déjà séparées en faits et dimensions**, prêtes à être reliées. C'est vous qui devez recomposer le puzzle.

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — la **table de faits** : chaque ligne est une vente, avec ses mesures (`quantite`, `prix_unitaire`, `remise`, `montant`, `marge`) et ses clés étrangères (`date_id`, `magasin_id`, `produit_id`, `client_id`).
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — la dimension **magasin** (`magasin_id`, `ville`, `type`, `surface_m2`, `date_ouverture`).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — la dimension **produit** (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Client.csv`](../data/Dim_Client.csv) — la dimension **client** (`client_id`, `prenom`, `nom`, `ville`, `segment`, `date_inscription`, `email`).
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — la dimension **date** (`date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour`, `jour_semaine`, `est_weekend`).

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Cadrer et planifier un chantier de modélisation** : découper le travail en étapes, estimer les délais, anticiper les points de blocage et répartir les tâches au sein du binôme.
- **Préparer et fiabiliser les tables dans Power Query** : contrôler et corriger les types de colonnes, traiter les valeurs manquantes ou aberrantes qui empêcheraient une relation propre, garder des noms de colonnes parlants.
- **Concevoir un schéma en étoile** : distinguer table de faits et tables de dimensions, créer les relations avec la bonne cardinalité et le bon sens de filtrage.
- **Configurer une table de dates** dédiée aux analyses temporelles et vérifier sa continuité.
- **Valider et documenter un modèle** : prouver par un test que les filtres se propagent, et expliquer à un lecteur non technique pourquoi l'étoile surpasse une table à plat.

## Données fournies

Les cinq tables sont déjà présentes dans le dépôt : dossier [`99-Brief/Data-Analyst/data/`](../data/). Aucune donnée n'est à télécharger. Vous travaillez à partir de ces fichiers en lecture ; vos corrections de préparation vivent dans Power Query (on ne modifie jamais les CSV sources).

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre modèle et sa propre documentation. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et plan de chantier, SANS modélisation (J1)

Avant d'importer quoi que ce soit, appropriez-vous le sujet et **organisez votre semaine**. Ouvrez les cinq fichiers dans un tableur pour un premier regard : laquelle de ces tables est la table de faits, lesquelles sont des dimensions, et à quoi le voyez-vous ? Repérez pour chaque table sa **clé** et les colonnes qui feront le lien entre elles (les `*_id`).

Sur le papier (schéma à la main ou outil de diagramme), dessinez l'étoile cible : la table de faits au centre, les quatre dimensions autour. Rédigez ensuite un **micro plan de projet** : quelles étapes, dans quel ordre, réparties comment entre vous deux, avec quelle échéance par jour ? Où voyez-vous les risques (une clé qui ne correspond pas ? une date manquante ?) et comment comptez-vous les lever ? Ce cadrage est votre feuille de route : il vous évitera de découvrir un blocage le vendredi. Initialisez votre dépôt GitHub dès aujourd'hui et déposez-y ce plan.

### Phase 2 — Import et préparation dans Power Query (J1-J2)

Importez les cinq tables dans Power BI Desktop. Ne passez surtout pas directement à la modélisation : ouvrez d'abord **Power Query** et inspectez chaque table. Les types sont-ils corrects ? Les clés (`magasin_id`, `produit_id`, `client_id`, `date_id`) doivent être des **nombres entiers**, les dates des **dates**, les montants des **décimaux**. Une clé restée en texte ou une date mal typée cassera silencieusement une relation plus tard.

Confrontez aussi les tables à la réalité : y a-t-il des valeurs manquantes sur une clé, des lignes en double dans une dimension, des valeurs aberrantes (une remise hors bornes, un `montant` négatif hérité de l'audit S06) ? Documentez et corrigez ce qui empêcherait une relation propre — une dimension avec un `magasin_id` en double ne peut pas jouer son rôle. Gardez des **noms de colonnes parlants** : c'est ce que verront les futurs utilisateurs du tableau de bord.

### Phase 3 — Construction du modèle en étoile (J2-J3)

Passez en vue **Modèle**. Créez les quatre relations qui relient chaque dimension à la table de faits, en cardinalité **un-à-plusieurs** (une ligne de dimension éclaire plusieurs ventes) :

- `Dim_Magasin[magasin_id]` → `Faits_Ventes[magasin_id]`
- `Dim_Produit[produit_id]` → `Faits_Ventes[produit_id]`
- `Dim_Client[client_id]` → `Faits_Ventes[client_id]`
- `Dim_Date[date_id]` → `Faits_Ventes[date_id]`

Vérifiez le **sens de filtrage** : il doit aller des dimensions vers les faits, en filtrage simple. Traquez les relations ambiguës, inactives non voulues ou les cardinalités « plusieurs-à-plusieurs » qui trahiraient une clé mal préparée. Pourquoi une étoile plutôt que de tout fusionner en une seule grande table ? Notez vos arguments au fil de l'eau, ils nourriront la restitution.

### Phase 4 — Table de dates et validation du modèle (J3-J4)

Marquez `Dim_Date` comme **table de dates** (sur le champ `date`) et confirmez qu'elle est **continue et sans trous** sur toute la période couverte par les ventes — une table de dates trouée fausserait toute analyse temporelle.

Testez ensuite votre modèle avec une **matrice simple** : par exemple `montant` en valeurs, `ville` en lignes et `nom_mois` en colonnes. Les filtres se propagent-ils correctement d'une dimension à l'autre à travers la table de faits ? Ajoutez un second test croisant une autre paire de dimensions (segment client × catégorie, par exemple). Si un total paraît faux ou vide, remontez la piste : c'est presque toujours une relation ou un type mal réglé en amont.

### Phase 5 — Documentation, restitution et mise en ligne (J5)

Rédigez la **documentation du modèle** à destination de la cellule data et de la direction : une capture de la vue Modèle **annotée**, un **tableau des relations** (table source, table cible, clés, cardinalité, sens de filtrage) et un court paragraphe expliquant, sans jargon, **pourquoi l'étoile est préférée à des tables à plat** (lisibilité, non-redondance, performance, une seule vérité). Confrontez au passage le résultat à votre plan de la Phase 1 : qu'aviez-vous bien anticipé, qu'avez-vous dû réajuster ? Soignez le README, versionnez vos livrables et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : plan de chantier, cinq tables importées et préparées (types corrects, anomalies traitées), quatre relations dimension → faits en un-à-plusieurs, table de dates continue marquée, matrice de test qui prouve la propagation des filtres, documentation du modèle et dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez une **hiérarchie** temporelle (année → trimestre → mois) ou géographique et montrez le drill-down dans la matrice de test.
- Créez une première **mesure** simple (CA total, marge moyenne) et vérifiez qu'elle réagit bien aux filtres des dimensions.
- Pas de licence Power BI ? Reproduisez le modèle dans un outil équivalent (Tableau, Looker Studio) ou **décrivez-le entièrement** : schéma annoté + tableau des relations complet, la rigueur du raisonnement primant sur l'outil.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **modèle** : un fichier `.pbix` (ou l'équivalent de l'outil choisi, ou la description écrite complète si aucune licence) ;
  - une **capture annotée** de la vue Modèle montrant l'étoile et ses relations ;
  - la **documentation du modèle** (`MODELE.md` ou PDF) : tableau des relations + paragraphe « étoile vs table à plat » ;
  - le **plan de chantier** rédigé en Phase 1 ;
  - un **`README.md`** : description du projet, technologies, instructions d'ouverture, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Modèle et documentation (60 %)** : justesse de la préparation des données, correction des relations et du sens de filtrage, configuration de la table de dates, clarté de la documentation et du plan de chantier.
- **Restitution orale (40 %)** : 10 minutes de démonstration du modèle et de la matrice de test devant un « comité data » (le formateur et un autre binôme) + 5 minutes de questions, dont la justification du choix de l'étoile.

**Validation partielle** : un binôme dont le modèle n'est pas totalement finalisé mais dont le plan de chantier, la préparation des données et le raisonnement de modélisation sont structurés et documentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Cadrer et planifier le chantier**
- Un plan de chantier découpe le travail en étapes ordonnées, réparties dans le binôme et échéancées sur les 5 jours.
- Les risques de modélisation (clés non concordantes, dates manquantes) sont anticipés avec une parade proposée.
- Le bilan final compare ce qui était prévu à ce qui a été réalisé.

**Préparer et fiabiliser les données**
- Les types de colonnes sont contrôlés et corrigés (clés en entier, dates en date, montants en décimal).
- Les valeurs manquantes, doublons et aberrations empêchant une relation propre sont détectés et traités.
- Les noms de colonnes restent parlants pour un utilisateur métier.

**Concevoir le modèle en étoile**
- Les quatre relations dimension → faits existent en cardinalité un-à-plusieurs.
- Le sens de filtrage va bien des dimensions vers la table de faits, sans relation ambiguë ni inactive non voulue.
- `Dim_Date` est marquée comme table de dates et est continue sans trous.

**Valider et restituer**
- Au moins une matrice de test prouve que les filtres se propagent correctement.
- L'intérêt du schéma en étoile face à une table à plat est expliqué clairement et sans jargon.
- Le dépôt GitHub public est complet (modèle + capture annotée + documentation + README).

## Ressources

- Module de cours — [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/)
- Rappels — [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/)
- Cadrage & planification — [Gestion de projet data](../../../11-Gestion-Projet/)
- Documentation Power BI — relations, cardinalité et sens de filtrage : https://learn.microsoft.com/power-bi/transform-model/desktop-relationships-understand
- Documentation Power BI — marquer une table de dates : https://learn.microsoft.com/power-bi/transform-model/desktop-date-tables
- Étape précédente du parcours — [Audit & EDA des ventes (S06)](semaine-06-eda-ventes-nordretail.md)
