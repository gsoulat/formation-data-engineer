# Brief S05 — Interroger la base NordRetail en SQL pour préparer l'analyse

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S05 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant → intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | SQLite, SQL (SELECT / JOIN / GROUP BY), Git/GitHub, Markdown |
| **Prérequis** | [Introduction SELECT](../../../01-Fondamentaux/SQL/01-Introduction-Select/) · [Agrégations GROUP BY](../../../01-Fondamentaux/SQL/02-Agregations-Groupby/) · [Jointures](../../../01-Fondamentaux/SQL/03-Jointures/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, mais son équipe data est naissante — vous en faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion.

### Le problème

La direction commerciale veut se doter d'un **tableau de bord de pilotage**, mais aujourd'hui chaque chiffre demandé déclenche la même course : on ouvre trois fichiers Excel éparpillés, on recopie des colonnes, on additionne à la main, et le lundi suivant le chiffre a déjà changé. Personne ne sait dire d'où vient exactement un total, ni comment le refaire à l'identique.

Le responsable BI a fait migrer les données de caisse dans une **base relationnelle** unique. Avant de dessiner le moindre indicateur, l'équipe a besoin d'une chose : savoir **aller chercher les bons chiffres à la source**, avec des requêtes propres, commentées et **reproductibles**. Une requête écrite une fois doit pouvoir être relancée dans six mois et donner le même résultat, sans copier-coller manuel.

Votre mission de la semaine intervient donc **en amont** du tableau de bord : constituer le **socle de requêtes d'extraction** qui alimentera toutes les analyses des semaines suivantes.

### La question centrale

Toute la semaine, chaque requête que vous écrivez doit contribuer à répondre à la question que la direction vous a posée :

> **« Que peut-on faire dire à la base NordRetail sur l'activité de l'enseigne — et ces chiffres sont-ils reproductibles à l'identique ? »**

### Les données

Une seule base cette semaine, montée à partir d'un script d'installation fourni :

- [`../data/setup.sql`](../data/setup.sql) — script qui crée et remplit la base NordRetail (**~12 000 ventes**, période à partir de 2023). Quatre tables reliées entre elles : `magasins` (ville, type, surface), `produits` (produit, catégorie, prix, coût), `clients` (segment, ville, inscription) et `commandes` (la table de faits : date, quantité, montant, et les clés vers les trois autres tables).

Le cœur du travail sera de **relier ces tables entre elles** : un montant de vente n'a de sens qu'une fois rattaché à sa ville (via `magasins`) et à sa catégorie de produit (via `produits`).

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Monter une base relationnelle** à partir d'un script d'installation et **reconnaître un schéma** : tables, colonnes, clés primaires et clés étrangères.
- **Écrire des requêtes SELECT ciblées** pour extraire exactement l'information demandée par un besoin métier, ni plus ni moins.
- **Agréger des données** avec `GROUP BY`, `SUM`, `COUNT`, et hiérarchiser les résultats avec `ORDER BY` / `LIMIT` (top produits, top villes).
- **Combiner plusieurs tables** avec des jointures (`JOIN … ON …`) pour croiser ventes, magasins et produits.
- **Documenter et versionner** un jeu de requêtes reproductibles, et en restituer les résultats à un lecteur métier non technique.

## Données fournies

Le script de la base est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/setup.sql`](../data/setup.sql). Aucune donnée n'est à télécharger. Vous montez la base **en local** à partir de ce script et travaillez en **lecture seule** dessus : on n'écrit jamais dans la base source, on écrit seulement des requêtes de lecture qui l'interrogent.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre fichier de requêtes et son propre compte rendu. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et lecture du schéma, SANS écrire de requête d'analyse (J1)

Avant d'agréger quoi que ce soit, appropriez-vous le terrain. Montez la base à partir de `setup.sql`, puis observez sa structure : combien de tables, et que représente chacune ? Dessinez à la main (ou sur un schéma simple) les **liens entre les tables** — quelle colonne de `commandes` pointe vers `magasins` ? vers `produits` ? vers `clients` ? Demandez-vous ce que représente **une ligne de `commandes`** : une vente unitaire, un panier, une ligne de ticket ? Notez enfin les questions métier auxquelles la direction voudra répondre (quelle ville vend le plus ? quel produit ? quelle catégorie ?) et, en regard, **quelles tables il faudra relier** pour y répondre. Ces hypothèses guideront toutes vos requêtes. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Comptages de cadrage et premières extractions (J1-J2)

Établissez vos **totaux de contrôle**, ceux qui vous serviront de garde-fou toute la semaine : nombre de lignes de chaque table, période couverte par les ventes (date la plus ancienne, date la plus récente), et chiffre d'affaires total sur l'ensemble. Ces valeurs sont votre référence : si plus tard la somme d'un CA par ville ne retombe pas sur ce total, c'est qu'une jointure a perdu ou dupliqué des lignes. Écrivez ensuite vos premières requêtes ciblées sur une seule table (`commandes`) : les ventes d'une période donnée, les plus gros montants. À ce stade, comment vérifieriez-vous qu'une requête renvoie bien ce que vous croyez ?

### Phase 3 — Agrégations : top produits et classements (J2-J3)

Faites parler les volumes. Écrivez la requête qui sort le **top 10 des produits par chiffre d'affaires** (`GROUP BY` sur le produit, `SUM` du montant, `ORDER BY … DESC`, `LIMIT 10`). Interrogez le résultat : le classement par CA est-il le même que par **quantités vendues** ? Un produit peut vendre beaucoup d'unités mais peser peu en euros — lequel des deux classements recommanderiez-vous à la direction, et pour répondre à quelle question ? Produisez au moins deux classements de ce type.

### Phase 4 — Jointures : croiser ventes, villes et catégories (J3-J4)

C'est le cœur de la semaine. Calculez le **CA par ville** en joignant `commandes` à `magasins` (`JOIN … ON commandes.magasin_id = magasins.magasin_id`), trié du plus fort au plus faible. Calculez le **CA par catégorie** en joignant `commandes` à `produits`, trié de la même façon. Vérifiez systématiquement : la somme de vos CA par ville retombe-t-elle sur le CA total de la Phase 2 ? Si non, votre jointure a un problème. Produisez enfin **une requête plus riche** au choix : panier moyen par segment de client (jointure vers `clients`), ou CA mois par mois (extraction du mois depuis la date). Quelle ville porte l'activité ? Quelle catégorie ? Le canal e-commerce pèse-t-il autant que les magasins physiques ?

### Phase 5 — Documentation, compte rendu et mise en ligne (J5)

Rangez toutes vos requêtes dans un fichier `extraction.sql`, chacune précédée d'un **commentaire clair** (`-- Q1 : top 10 produits par CA`). Le fichier doit pouvoir être rejoué de bout en bout sur une base fraîche. Rédigez ensuite un court **compte rendu** (`resultats.md`) : pour chaque requête, les premières lignes du résultat et **une phrase d'interprétation métier** en langage courant. Terminez par une synthèse de 5 à 8 lignes adressée à la direction, répondant frontalement à la question centrale. Soignez le README et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : base montée, schéma décrit, totaux de contrôle établis, top produits, CA par ville **avec jointure**, CA par catégorie **avec jointure**, une requête plus riche, le tout commenté dans `extraction.sql` et interprété dans `resultats.md`, dépôt public à jour.

### Pour aller plus loin (bonus)

- Calculez le **CA mensuel** et repérez d'éventuels pics (soldes, fêtes) : la base raconte-t-elle une saisonnalité ?
- Combinez **trois tables** dans une même requête (ex. CA par ville **et** par catégorie) pour trouver le couple ville × catégorie le plus rentable.
- Ajoutez la **marge** au classement produits (montant − coût) : le produit qui rapporte le plus de CA est-il aussi le plus rentable ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `extraction.sql` — 8 à 12 requêtes commentées (un commentaire `-- Qn : …` par requête), rejouable de bout en bout sur une base montée depuis `setup.sql` ;
  - un **compte rendu** (`resultats.md`) : pour chaque requête, les premières lignes du résultat + une phrase d'interprétation, et une synthèse finale pour la direction ;
  - un **`README.md`** : description du projet, technologies, commande de montage de la base et de lancement des requêtes, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Requêtes et compte rendu (60 %)** : justesse des extractions, correction des jointures et des agrégations, cohérence des totaux de contrôle, clarté des commentaires et des interprétations.
- **Restitution orale (40 %)** : 10 minutes pour présenter à un « comité de direction » (le formateur et un autre binôme) comment vous avez interrogé la base et ce qu'elle révèle + 5 minutes de questions, dont une démonstration en direct d'une requête relancée.

**Validation partielle** : un binôme dont le fichier de requêtes n'est pas complètement finalisé mais dont les extractions produites sont correctes, commentées et dont la démarche (schéma, totaux de contrôle, jointures) est structurée et documentée peut valider partiellement les compétences travaillées.

## Critères de performance

**Monter et lire la base**
- La base est montée à partir de `setup.sql` et les 4 tables sont interrogeables.
- Le schéma est décrit : rôle de chaque table et clés étrangères de `commandes` vers `magasins`, `produits`, `clients` identifiées.
- Les totaux de contrôle (lignes par table, période, CA total) sont établis et servent de référence.

**Extraire et agréger**
- Le top 10 des produits par CA est correct et trié en ordre décroissant.
- Au moins deux classements agrégés (`GROUP BY` + `ORDER BY` / `LIMIT`) pertinents sont produits.
- Chaque requête est rattachée à une question métier explicite.

**Combiner plusieurs tables**
- Le CA par ville utilise une jointure `commandes` × `magasins`.
- Le CA par catégorie utilise une jointure `commandes` × `produits`.
- Au moins une requête combine 3 tables ou une agrégation temporelle.
- La cohérence des jointures est vérifiée (la somme des CA agrégés retombe sur le CA total).

**Documenter et restituer**
- Toutes les requêtes sont commentées et versionnées dans `extraction.sql`, rejouable de bout en bout.
- Le compte rendu associe à chaque requête un extrait de résultat et une interprétation en langage courant.
- Le dépôt GitHub public est complet (requêtes + README + compte rendu).

## Ressources

- Rappels — [Introduction SELECT](../../../01-Fondamentaux/SQL/01-Introduction-Select/) · [Agrégations GROUP BY](../../../01-Fondamentaux/SQL/02-Agregations-Groupby/) · [Jointures](../../../01-Fondamentaux/SQL/03-Jointures/)
- Approfondissement — [Extraction & analyse](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/)
- Documentation SQLite : https://www.sqlite.org/docs.html
- Aide-mémoire SQL : `SELECT … FROM … JOIN … ON … GROUP BY … ORDER BY … LIMIT`
- Prochaine étape du parcours — [Brief S06 — Auditer et explorer les ventes de NordRetail (EDA)](semaine-06-eda-ventes-nordretail.md), puis le projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
