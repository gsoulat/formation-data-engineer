# Brief S08 — Construire le premier tableau de bord de pilotage de NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S08 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant → intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Looker Studio (ou Power BI Desktop), tableur, Git/GitHub |
| **Prérequis** | [Module KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) · [Dashboards fondamentaux](../../../15-Business-Intelligence/07-Dashboards-Fondamentaux/) · [Tendances & séries temporelles](../../../15-Business-Intelligence/05-Tendances-Series-Temporelles/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, et son équipe data — dont vous faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion — commence à livrer ses premiers résultats.

### Le problème

Ces dernières semaines, l'équipe a audité les données de ventes, décrit l'activité avec des statistiques, puis dégagé les grandes tendances et les indicateurs clés. Tout ce travail vit aujourd'hui dans des notebooks et des tableurs que **seule l'équipe data sait lire**. En comité de direction, on continue de faire circuler des exports Excel figés, imprimés la veille, déjà périmés le lendemain.

La direction commerciale a été claire : elle ne veut plus « d'un tableur de plus ». Elle veut **un écran unique** qu'un décideur ouvre et comprend « en 30 secondes » — où en est le chiffre d'affaires, quelle ville tire l'activité, comment se comporte le e-commerce — et qu'il puisse filtrer lui-même sans appeler l'équipe data. Votre mission de la semaine : transformer les analyses des semaines précédentes en un **premier tableau de bord de pilotage** vivant et interactif.

### La question centrale

Toute la semaine, chaque écran, chaque graphique, chaque filtre que vous ajoutez doit servir une seule intention :

> **« Un décideur de NordRetail peut-il, en ouvrant ce tableau de bord et en moins d'une minute, savoir où en est l'activité de l'enseigne ? »**

### Les données

Vous repartez du fichier de ventes déjà connu de l'équipe, pour garantir la continuité des chiffres d'une semaine sur l'autre :

- [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) — ventes détaillées de l'enseigne. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

C'est le même export que celui audité les semaines précédentes : les indicateurs que votre tableau de bord affichera devront donc **coïncider avec ceux déjà calculés**. Cette cohérence est un point de contrôle, pas un détail.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Traduire un besoin métier en tableau de bord** : partir de la question de la direction pour décider quoi montrer, dans quel ordre, et ce qu'il faut au contraire écarter.
- **Choisir la bonne visualisation selon l'intention** : distinguer une comparaison (barres), une évolution dans le temps (courbe), une part relative, une valeur clé (carte) — et justifier chaque choix.
- **Construire un tableau de bord interactif** dans un outil de BI (Looker Studio ou Power BI) : sources, cartes d'indicateurs, graphiques et filtres qui rafraîchissent l'ensemble du rapport.
- **Garantir une lecture accessible et honnête** : titres explicites, axes non tronqués, palette lisible y compris pour un lecteur daltonien, information principale placée là où l'œil se pose d'abord.
- **Contrôler la justesse des chiffres affichés** en les confrontant aux calculs de référence, et **documenter vos choix** de conception.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_magasins.csv`](../data/ventes_magasins.csv). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur ce fichier : le tableau de bord se branche sur la source, il ne la modifie pas.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme livre son propre tableau de bord et sa propre note de conception. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage : maquette et choix de conception, SANS outil (J1)

Avant de toucher au moindre logiciel de BI, décidez de ce que vous allez montrer. Reprenez la question centrale et l'inventaire des indicateurs des semaines précédentes : parmi tout ce que vous savez calculer, qu'est-ce qui mérite vraiment sa place sur un écran de pilotage ? Un décideur pressé ne lit pas quinze graphiques.

Esquissez à la main (papier ou tableur) une **maquette** de votre tableau de bord : où placez-vous les indicateurs clés, où l'évolution dans le temps, où les comparaisons entre villes ou catégories ? Pour chaque bloc que vous prévoyez, posez-vous l'intention : montre-t-il une **valeur** (un total à retenir), une **comparaison** (qui fait plus que qui), une **évolution** (ça monte ou ça descend) ? Cette intention dictera plus tard le type de graphique. Interrogez aussi le lecteur : qu'est-ce qu'un directeur commercial veut voir en premier, et qu'est-ce qui, pour lui, est du bruit ? Initialisez votre dépôt GitHub dès aujourd'hui et déposez-y la photo de votre maquette.

### Phase 2 — Branchement de la source et bloc d'indicateurs clés (J1-J2)

Choisissez votre outil : **Looker Studio** est recommandé (gratuit, partage par lien), **Power BI Desktop** est accepté. Importez `ventes_magasins.csv` comme source et vérifiez d'emblée les types : `date` doit être reconnue comme une date, `montant`, `marge`, `quantite` comme des nombres — sinon aucun total ne sera juste.

Construisez ensuite le **bandeau d'indicateurs** en haut du rapport : 3 à 4 **cartes** reprenant les chiffres clés de l'enseigne (par exemple chiffre d'affaires total, marge totale, panier moyen par ligne, nombre de ventes). Ce sont ces cartes qu'un décideur lit en premier : elles doivent être immédiatement compréhensibles, chiffre et libellé, sans ambiguïté d'unité.

### Phase 3 — Visuels d'analyse : la bonne forme pour la bonne question (J2-J3)

Complétez le tableau de bord avec **4 à 5 visuels au total** (cartes comprises), chacun choisi pour son intention, pas par habitude. Une **courbe** pour l'évolution du chiffre d'affaires dans le temps (par mois) : monte-t-il, marque-t-il un creux ? Des **barres** pour comparer le chiffre d'affaires par ville et/ou par catégorie : qui porte l'activité ? Un dernier visuel au choix, selon ce que raconte votre analyse : top produits, ou répartition Magasin vs E-commerce. Pour chaque graphique, demandez-vous : la forme que j'ai choisie répond-elle vraiment à la question posée ? Un camembert à douze parts, une échelle 3D, un axe qui ne part pas de zéro trahissent l'information autant qu'ils l'illustrent — évitez-les.

### Phase 4 — Interactivité, accessibilité et contrôle de justesse (J3-J4)

Rendez le tableau de bord vivant. Ajoutez au moins **un filtre interactif** (sélecteur de période, de ville ou de catégorie) qui met à jour **l'ensemble du rapport** d'un seul geste : c'est ce qui permet au décideur d'explorer sans vous solliciter. Testez-le sur plusieurs valeurs.

Soignez la lecture pour tous : titres explicites (un visuel doit se comprendre seul), axes lisibles et non tronqués, **palette accessible** — ne codez jamais une information par la seule couleur, et vérifiez que vos contrastes restent lisibles pour un lecteur daltonien. Enfin, procédez au **contrôle de justesse** : le chiffre d'affaires total affiché par vos cartes doit coïncider avec le total de référence calculé les semaines précédentes. S'il diffère, ne masquez pas l'écart : trouvez sa cause (type mal reconnu, ligne filtrée, doublon) et corrigez.

### Phase 5 — Partage, note de conception et mise en ligne (J5)

Publiez votre tableau de bord : Looker Studio → **lien public en lecture** ; Power BI → fichier **`.pbix`**. Dans les deux cas, joignez une **capture d'écran** de l'écran complet. Rédigez une courte **note de conception** (`notes_dashboard.md`, 5 à 10 lignes) qui justifie, pour chaque visuel et pour le filtre, *pourquoi cette forme-là* : quelle intention, quel public, quelle décision aidée. Soignez le README et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : maquette de cadrage, tableau de bord construit dans un outil de BI à partir de `ventes_magasins.csv`, 3 à 4 cartes d'indicateurs, 4 à 5 visuels adaptés à leur intention, au moins 1 filtre fonctionnel sur tout le rapport, contrôle de justesse du CA total, capture d'écran, note de conception, dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez un visuel de **comparaison à un objectif** : confrontez le CA réalisé aux cibles de [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) et signalez visuellement l'écart.
- Enrichissez d'un **second filtre croisé** (par exemple période *et* canal) et vérifiez que les visuels réagissent de façon cohérente.
- Proposez une **variante daltonien-safe** de votre palette et documentez le choix des couleurs (par exemple Okabe-Ito), en vous appuyant sur le module [Visualisations avancées](../../../15-Business-Intelligence/11-Visualisations-Avancees/).

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **tableau de bord** : lien public Looker Studio (dans le README) **ou** fichier `.pbix` versionné ;
  - une **capture d'écran** de l'écran complet du tableau de bord ;
  - `notes_dashboard.md` — note de conception justifiant chaque visuel et le filtre (5 à 10 lignes) ;
  - la **maquette** de cadrage (photo ou schéma) issue de la Phase 1 ;
  - un **`README.md`** : description du projet, outil utilisé, lien du tableau de bord ou instructions d'ouverture, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Tableau de bord et note de conception (60 %)** : pertinence des visuels au regard de l'intention, justesse des indicateurs, interactivité effective, lisibilité et accessibilité, qualité de la justification des choix.
- **Restitution orale (40 %)** : 10 minutes de démonstration du tableau de bord à un « comité de direction » (le formateur et un autre binôme), filtre manipulé en direct, + 5 minutes de questions.

**Validation partielle** : un binôme dont le tableau de bord n'est pas totalement finalisé mais dont la maquette, le choix des visuels et la justification de conception sont structurés et argumentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Cadrer et choisir les visualisations**
- Une maquette précède la construction et hiérarchise l'information (indicateur clé en premier).
- Chaque visuel est adapté à son intention (carte pour une valeur, courbe pour une évolution, barres pour une comparaison).
- Les pièges visuels sont évités (pas d'axe tronqué, pas de 3D inutile, pas de camembert surchargé).
- La palette est lisible et accessible : l'information n'est jamais portée par la seule couleur.

**Construire le tableau de bord**
- La source `ventes_magasins.csv` est branchée avec les bons types (`date` en date, montants en numérique).
- 3 à 4 cartes d'indicateurs clés sont affichées en évidence, lisibles en 30 secondes.
- 4 à 5 visuels au total composent un tableau de bord cohérent.
- Au moins 1 filtre interactif fonctionne sur l'ensemble du rapport.
- Le chiffre d'affaires total affiché coïncide avec le total de référence des analyses précédentes.

**Restituer**
- Le tableau de bord est partagé (lien public ou `.pbix`) avec une capture d'écran.
- La note de conception justifie explicitement chaque visuel et le filtre.
- Le dépôt GitHub public est complet (tableau de bord + README + note).

## Ressources

- Module de cours — [Dashboards fondamentaux](../../../15-Business-Intelligence/07-Dashboards-Fondamentaux/)
- Module de cours — [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/)
- Rappels — [Tendances & séries temporelles](../../../15-Business-Intelligence/05-Tendances-Series-Temporelles/)
- Accessibilité des visualisations — [Visualisations avancées](../../../15-Business-Intelligence/11-Visualisations-Avancees/)
- Aide Looker Studio : https://support.google.com/looker-studio
- Power BI (Microsoft Learn) : https://learn.microsoft.com/fr-fr/power-bi/
- Choisir le bon graphique : https://www.data-to-viz.com/
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
