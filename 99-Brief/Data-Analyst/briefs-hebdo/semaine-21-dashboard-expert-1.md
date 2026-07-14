# Brief S21 — Concevoir en autonomie le tableau de bord régional de NordRetail (fondations & page d'accueil)

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S21 — Phase 3 : Tableau de bord expert (1/2) |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Avancé — conduite en autonomie |
| **Modalité** | Individuel |
| **Technologies** | Power BI (modélisation en étoile, DAX, table de dates) · Looker Studio accepté · Git/GitHub |
| **Prérequis** | [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/) · [DAX](../../../15-Business-Intelligence/10-DAX/) · [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) · [Tableau de bord expert](../../../15-Business-Intelligence/17-Dashboard-Expert/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel. Son équipe data, encore jeune, a construit ces derniers mois les fondations analytiques de l'enseigne : un audit des ventes, un modèle en étoile, des mesures de gestion, puis un premier croisement du chiffre d'affaires réel avec les **objectifs 2024** par magasin. Vous en faites partie.

### Le problème

Le comité de direction veut désormais un **tableau de bord régional unique** pour piloter l'activité 2024 : chiffre d'affaires, marge, atteinte des objectifs, classement des points de vente, dynamique par catégorie. Le sponsor — le directeur commercial — est pressé et n'a pas rédigé de cahier des charges détaillé : il vous confie l'objectif métier et vous laisse décider du « comment ».

C'est un changement de posture. Jusqu'ici, on vous guidait étape par étape ; cette fois, vous menez le travail **seul, de bout en bout**, comme un analyste face à un commanditaire qui n'a pas le temps de tout spécifier. On ne vous demande pas d'inventer des techniques nouvelles, mais de **piloter en autonomie** des savoir-faire que vous maîtrisez déjà : formaliser un besoin flou, poser un modèle de données propre, et livrer une page d'accueil qui donne les bons chiffres et se lit sans mode d'emploi.

### La question centrale

Toute la semaine, chaque choix que vous faites — quel indicateur, quel visuel, quelle place à l'écran — doit contribuer à répondre à la question que la direction vous a posée :

> **« En une page, un responsable de NordRetail comprend-il d'un coup d'œil où en est l'activité régionale — et sait-il quels magasins et quelles catégories décrochent des objectifs 2024 ? »**

### Les données

Vous repartez du schéma dimensionnel déjà présent dans le dépôt et des objectifs croisés la semaine précédente :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — table de faits (`vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`).
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — points de vente (`magasin_id`, `ville`, `type`, `surface_m2`, `date_ouverture`).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — produits (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Client.csv`](../data/Dim_Client.csv) — clients (`client_id`, attributs de segmentation).
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — calendrier (`date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour`, `jour_semaine`, `est_weekend`).
- [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) — objectifs mensuels par magasin (`magasin_id`, `annee`, `mois`, `objectif_ca`). Version tableur disponible : [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx).

Aucune donnée n'est à télécharger. On ne modifie jamais les fichiers sources : tout se joue dans le rapport.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Formaliser un besoin métier flou en autonomie** : identifier les utilisateurs, les décisions à éclairer, les questions métier prioritaires, et assumer par écrit vos hypothèses face à un commanditaire pressé.
- **Traduire chaque question métier en indicateur mesurable** (chiffre d'affaires, marge, taux de marge, taux d'atteinte des objectifs, panier moyen) — sans jamais poser un indicateur sans la question qui le justifie.
- **Construire un modèle de données propre en étoile** : table de faits au centre, dimensions en rayon, table de dates dédiée et marquée comme telle, relations et granularité vérifiées.
- **Écrire des mesures de gestion** (DAX ou équivalent) qui donnent des chiffres justes et reproductibles, y compris un taux d'atteinte des objectifs.
- **Concevoir une page d'accueil hiérarchisée** où le choix de chaque visualisation est justifié par un besoin utilisateur et se lit sans explication orale.

## Données fournies

Le schéma dimensionnel et les objectifs sont déjà présents dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Vous réutilisez ce que vous avez construit les semaines précédentes (modèle, mesures, croisement des objectifs) ; si vous n'en disposez pas, reconstruisez un modèle minimal à partir des `Dim_*.csv`, de `Faits_Ventes.csv` et de `objectifs_2024.csv` avant de commencer. Revenez à vos travaux existants au lieu de repartir de zéro.

## Travail demandé

Travail **individuel sur 5 jours**. L'entraide est encouragée, mais chacun conçoit son propre modèle, sa propre page et rédige sa propre note de cadrage. C'est votre première conduite de projet en pleine autonomie : c'est normal de se sentir un peu seul au départ — c'est précisément la compétence visée. Appuyez-vous sur la démarche ci-dessous. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage autonome du besoin, SANS ouvrir l'outil BI (J1)

Avant de poser le moindre visuel, mettez-vous dans la peau de l'analyste face à un sponsor pressé. Qui va réellement consulter ce tableau de bord — la direction régionale, un responsable de magasin, le contrôle de gestion ? Quelles **décisions** chacun doit-il pouvoir prendre en le regardant : relancer un magasin en retard, arbitrer un budget, comprendre un décrochage de catégorie ? Notez **5 à 7 questions métier prioritaires**, formulées comme un dirigeant les poserait (« quel magasin est le plus loin de son objectif ? », « la marge suit-elle le chiffre d'affaires ? »). Le sponsor n'a pas tout précisé : là où l'information manque, **formulez des hypothèses raisonnables et assumez-les par écrit** plutôt que d'attendre.

Pour chaque question, associez **un indicateur mesurable** — et un seul : pas de KPI sans une question derrière. Esquissez ensuite, sur papier, deux choses avant de cliquer : le **schéma en étoile** que vous visez (où est la table de faits ? quelles dimensions ? où passe la table de dates ? quelle granularité ?) et une **maquette de la page 1** (où placer les indicateurs clés, l'évolution dans le temps, le classement, le filtre ?). Pensez la hiérarchie visuelle *avant* de poser les visuels. Initialisez (ou mettez à jour) votre dépôt GitHub dès aujourd'hui et versionnez cette note de cadrage.

### Phase 2 — Modèle de données en étoile (J1-J2)

Passez du croquis à l'outil. À partir des `Dim_*.csv` et de `Faits_Ventes.csv`, montez un **modèle en étoile** dans Power BI (ou Looker Studio) : la table de faits au centre, les dimensions Date, Magasin, Produit et Client en rayon. Créez les **relations** et vérifiez leur cardinalité et leur sens. Intégrez `objectifs_2024` (CSV ou XLSX) de façon à pouvoir le rapprocher des ventes par magasin et par mois. Ajoutez une **table de dates dédiée**, marquée comme telle dans l'outil, condition sine qua non pour que les analyses temporelles soient fiables. Interrogez votre granularité : une ligne de faits, c'est quoi exactement, et vos objectifs sont-ils au même grain que vos ventes ?

### Phase 3 — Mesures de gestion (J2-J3)

Donnez au modèle sa puissance de calcul. Créez **au moins quatre mesures** (DAX ou équivalent) qui donneront partout les mêmes chiffres : `CA`, `Marge`, `Taux de marge %` et **`Taux d'atteinte objectif`** (chiffre d'affaires réel rapporté à `objectif_ca`). Soignez les divisions par zéro et le rattachement des objectifs au bon magasin et au bon mois — une erreur de jointure ici fausse tout le pilotage. Vérifiez chaque mesure sur un cas que vous savez recalculer à la main : un taux d'atteinte de 103 % doit correspondre à un magasin réellement au-dessus de son objectif.

### Phase 4 — Page d'accueil : vue d'ensemble régionale (J3-J4)

Concevez la **première page** du tableau de bord, celle qui doit tout dire en un écran. Prévoyez un **bandeau d'indicateurs clés** (cartes : CA, marge, taux d'atteinte…), une **évolution du chiffre d'affaires dans le temps**, un **classement des magasins** (par CA ou par taux d'atteinte), et un **filtre de période**. Chaque visuel doit répondre à une question posée en Phase 1 : pourquoi ce type de graphique pour cette question, et pas un autre ? Un histogramme, une courbe, un classement ne racontent pas la même chose. Travaillez la **hiérarchie visuelle** : ce qui est important se voit en premier, en haut à gauche, avant tout scroll. Un responsable qui découvre la page doit comprendre où en est l'activité **sans que vous soyez à côté de lui**.

### Phase 5 — Justification des choix, restitution et mise en ligne (J5)

Complétez votre note de cadrage par une **justification des choix** (une demi-page) : pour chaque indicateur retenu et chaque type de visuel, expliquez en quelques lignes *pourquoi* ce choix sert la décision du lecteur. C'est ce raisonnement, plus que l'exécution, qui fait la valeur d'un tableau de bord de pilotage. Vérifiez que le modèle est propre (relations correctes, table de dates marquée, mesures qui tournent), que la page se lit seule, soignez le README, exportez une **capture du modèle en étoile**, et poussez le tout sur GitHub. Gardez ce projet **propre et versionné** : vous le poursuivrez la semaine prochaine pour le rendre pleinement exploitable en réunion.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : note de cadrage (utilisateurs, décisions, 5+ questions métier, KPI associés, hypothèses assumées), modèle en étoile avec relations correctes et table de dates marquée, au moins 4 mesures dont le taux d'atteinte des objectifs, page 1 avec bandeau d'indicateurs + évolution temporelle + classement des magasins + filtre de période, justification écrite des choix, dépôt public à jour avec capture du modèle.

### Pour aller plus loin (bonus)

- Ajoutez une mesure de **panier moyen** ou de **top produits** et intégrez-la à la page d'accueil.
- Proposez un premier **indicateur d'écart à l'objectif en euros** (et pas seulement en pourcentage) pour prioriser les magasins à relancer.
- Chargez les objectifs depuis [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx) au lieu du CSV pour vous exercer à un second format de source.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **fichier du rapport** (`.pbix` ou lien Looker Studio partagé) : modèle en étoile, mesures, page 1 ;
  - la **note de cadrage** (`CADRAGE.md` ou PDF) : utilisateurs, décisions, questions métier, KPI, hypothèses, et justification des choix d'indicateurs et de visuels ;
  - une **capture d'écran du modèle en étoile** (relations visibles) ;
  - un **`README.md`** : description du projet, technologies, mode d'emploi de la page, auteur.

## Modalités d'évaluation

Évaluation en deux volets :

- **Rapport et note de cadrage (60 %)** : pertinence du cadrage et des KPI, propreté du modèle en étoile, justesse des mesures (dont le taux d'atteinte), qualité et hiérarchie de la page d'accueil, clarté des justifications.
- **Restitution orale (40 %)** : 10 minutes de présentation devant un « comité de direction » (le formateur et un pair) — vous exposez votre cadrage, faites la démonstration de la page 1 et justifiez vos choix — suivies de 5 minutes de questions.

**Validation partielle** : un apprenant dont la page n'est pas totalement finalisée mais dont le cadrage est structuré, le modèle en étoile propre et les mesures justes peut valider partiellement les compétences travaillées.

## Critères de performance

**Cadrer le besoin en autonomie**
- La note de cadrage identifie les utilisateurs, les décisions à éclairer et au moins 5 questions métier prioritaires.
- Chaque question métier est associée à un indicateur mesurable (pas de KPI sans question).
- Les zones d'incertitude sont couvertes par des hypothèses assumées par écrit.

**Modéliser les données**
- Le modèle est en étoile : table de faits au centre, dimensions en rayon, relations correctes.
- Une table de dates dédiée est présente et marquée comme telle.
- Au moins 4 mesures fonctionnent, dont le taux d'atteinte des objectifs, sans erreur de jointure ni division par zéro.

**Concevoir la page d'accueil**
- La page 1 présente un bandeau d'indicateurs, une évolution temporelle, un classement des magasins et un filtre de période.
- Chaque visuel est rattaché à une question métier du cadrage.
- Le choix du type de visuel est justifié et la hiérarchie visuelle est lisible sans explication orale.

**Restituer**
- La justification écrite des choix (indicateurs + visuels) est claire et argumentée.
- La présentation orale expose le cadrage et démontre la page en autonomie.
- Le dépôt GitHub public est complet (rapport + note de cadrage + capture du modèle + README).

## Ressources

- Module de cours — [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/)
- Module de cours — [DAX](../../../15-Business-Intelligence/10-DAX/)
- Module de cours — [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/)
- Module de cours — [Tableau de bord expert](../../../15-Business-Intelligence/17-Dashboard-Expert/)
- Rappel — [Analyse du besoin métier](../../../15-Business-Intelligence/03-Analyse-Besoin-Metier/)
- Documentation Power BI — modèle en étoile : https://learn.microsoft.com/power-bi/guidance/star-schema
- Documentation DAX — fonctions `CALCULATE`, `DIVIDE` : https://learn.microsoft.com/dax/
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_3 — Projet final](../BRIEF_3_PROJET_FINAL.md)
