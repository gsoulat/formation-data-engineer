# Brief S18 — Consolider les ventes des magasins de NordRetail en un flux unique (ETL)

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S18 — Phase 3 : Industrialiser la donnée qui alimente le tableau de bord |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas (ou Power Query) · Git/GitHub · tableur (contrôle) |
| **Prérequis** | [ETL & automatisation](../../../15-Business-Intelligence/15-ETL-Automatisation/) · [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/) · [Audit & EDA (S06)](semaine-06-eda-ventes-nordretail.md) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Depuis quelques semaines, l'équipe data — dont vous faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion — a fiabilisé les données de ventes et fait vivre un premier tableau de bord de pilotage. Mais jusqu'ici, chaque analyse partait d'un export déjà rassemblé. Dans la vraie vie de l'enseigne, la donnée arrive en morceaux.

### Le problème

Chaque magasin exporte ses ventes 2023 depuis sa propre caisse… mais personne ne s'est mis d'accord sur un format. Roubaix a renommé ses colonnes (`qte`, `CA`), Lille sépare ses champs par des points-virgules, Tourcoing et Valenciennes sont propres mais **n'indiquent nulle part de quelle ville il s'agit**. Résultat : impossible d'empiler ces fichiers tels quels. Chaque semaine, un membre de l'équipe les recolle à la main dans un tableur — une manipulation lente, non traçable et truffée d'erreurs de copier-coller.

La direction régionale veut passer à un **reporting consolidé** rafraîchi régulièrement. Pour cela, il faut arrêter de bricoler : votre mission de la semaine est de construire le **flux de consolidation reproductible** qui alimentera, en amont, tout le tableau de bord de pilotage. C'est la « tuyauterie » invisible sans laquelle aucun indicateur régional n'est fiable.

### La question centrale

Toute la semaine, chaque étape de votre pipeline doit contribuer à répondre à la question que la direction vous a posée :

> **« Peut-on transformer les exports disparates des magasins de NordRetail en un fichier régional unique, fiable et régénérable sans intervention manuelle ? »**

### Les données

Quatre exports magasins, un par point de vente, tous volontairement hétérogènes — plus un fichier de référence pour contrôler votre résultat :

- [`../data/ventes_lille.csv`](../data/ventes_lille.csv) — séparateur **`;`**, colonnes `date;categorie;produit;quantite;montant`.
- [`../data/ventes_roubaix.csv`](../data/ventes_roubaix.csv) — séparateur `,`, colonnes **renommées** `date,categorie,produit,qte,CA`.
- [`../data/ventes_tourcoing.csv`](../data/ventes_tourcoing.csv) — séparateur `,`, colonnes `date,categorie,produit,quantite,montant`, **sans ville**.
- [`../data/ventes_valenciennes.csv`](../data/ventes_valenciennes.csv) — même format que Tourcoing, **sans ville**.
- [`../data/ventes_consolidees.csv`](../data/ventes_consolidees.csv) — **fichier de référence** au format cible `date,ville,categorie,produit,quantite,montant`. Attention : il contient aussi des villes que vous n'avez pas en source (Dunkerque, Amiens, canal en ligne). Il sert de contrôle, pas de modèle à recopier.

Aucune donnée n'est à télécharger : tout est déjà dans le dépôt. Vous travaillez en lecture seule sur les sources ; vos transformations ne modifient jamais les fichiers d'origine.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Extraire des sources hétérogènes** : lire des fichiers aux séparateurs et aux noms de colonnes différents sans les modifier manuellement.
- **Harmoniser vers un schéma cible commun** : renommer, réordonner, enrichir (ajouter la ville manquante) et fiabiliser les types (date normalisée, quantité entière, montant décimal).
- **Empiler et charger un jeu consolidé** : concaténer des sources alignées et produire un fichier unique propre, exploitable par le reste de la chaîne BI.
- **Contrôler un pipeline par confrontation à une référence** : comparer volumes, colonnes et agrégats, repérer et expliquer les écarts.
- **Documenter un flux pour le rendre rejouable** par un tiers, sans manipulation cachée.

## Données fournies

Les cinq fichiers ci-dessus sont présents dans [`99-Brief/Data-Analyst/data/`](../data/). Rien à installer côté données. Les quatre exports magasins sont vos **entrées** ; `ventes_consolidees.csv` est votre **oracle de contrôle**. Ne modifiez jamais les fichiers sources : toute correction se fait dans votre code, en mémoire.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre pipeline, son propre fichier consolidé et sa propre documentation. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et relevé des écarts, SANS code (J1)

Avant d'écrire la moindre ligne de transformation, ouvrez les quatre exports dans un tableur et **cartographiez leurs différences**. Dressez à la main un tableau de correspondance : pour chaque fichier, quel séparateur ? quels noms de colonnes ? une colonne `ville` existe-t-elle ? Que représente une ligne — une vente, un ticket, un agrégat journalier ? Décidez ensemble du **schéma cible commun** que devra respecter chaque source une fois harmonisée, et notez précisément la règle de transformation à appliquer à chacune (quoi renommer, quoi ajouter, quels types forcer). Interrogez-vous : d'où viendra la valeur de `ville` pour Tourcoing et Valenciennes, puisqu'elle n'apparaît nulle part dans le fichier ? Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Extract : charger les quatre sources telles qu'elles sont (J1-J2)

Chargez les quatre fichiers **sans les uniformiser à la main**. Lille exige de préciser le séparateur `;` ; les autres se lisent en `,`. Pour chaque source chargée, vérifiez la volumétrie (`shape`), les colonnes réellement obtenues et un aperçu des premières lignes. À ce stade, ne corrigez rien : constatez. Roubaix a-t-il bien les colonnes `qte` et `CA` ? Lille est-il correctement découpé, ou tout est-il tombé dans une seule colonne (signe d'un mauvais séparateur) ? Ce contrôle d'entrée vous évitera de propager une erreur de lecture jusqu'au fichier final.

### Phase 3 — Transform : harmoniser vers le schéma cible (J2-J3)

Amenez chaque source au schéma commun **`date, ville, categorie, produit, quantite, montant`**. Pour Roubaix, renommez `qte → quantite` et `CA → montant`. Pour Tourcoing et Valenciennes, **ajoutez la colonne `ville`** avec la valeur codée en dur correspondant au fichier (respectivement Tourcoing et Valenciennes) ; faites de même pour Lille et Roubaix. Fiabilisez ensuite les types : `date` en date normalisée (`YYYY-MM-DD`), `quantite` en entier, `montant` en décimal. Réordonnez les colonnes dans l'ordre cible. Une bonne pratique : écrivez une fonction de transformation paramétrée par le nom de ville, plutôt que de dupliquer quatre fois le même code — pourquoi est-ce plus sûr quand un cinquième magasin arrivera ?

### Phase 4 — Load & vérification contre la référence (J3-J4)

Empilez (union) vos quatre sources harmonisées en un seul tableau, puis exportez-le en CSV séparé par des virgules, avec en-têtes, sous un nom explicite (par exemple `ventes_consolidees_<binome>.csv`). Confrontez ensuite votre résultat au fichier de référence [`../data/ventes_consolidees.csv`](../data/ventes_consolidees.csv) : votre nombre de lignes et vos colonnes concordent-ils, une fois la comparaison **restreinte à vos quatre villes** (la référence contient aussi Dunkerque, Amiens et le canal en ligne, absents de vos sources) ? Calculez la **somme de `montant` par ville** de votre côté et du côté référence, et vérifiez qu'elles coïncident. Le moindre écart doit être investigué et expliqué : mauvais typage ? ligne perdue à la lecture ? arrondi ?

### Phase 5 — Documentation, robustesse et mise en ligne (J5)

Rédigez une **note de pipeline** (10 à 15 lignes) qui décrit, pour un collègue qui ne connaît pas votre code : les entrées, les transformations appliquées à chaque source, la sortie produite, et **comment relancer le flux de zéro** sans manipulation manuelle. Vérifiez que votre script s'exécute proprement de bout en bout et régénère le fichier consolidé à l'identique. Nettoyez le code, soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : les 4 sources chargées malgré leurs formats, harmonisées au schéma cible avec la ville ajoutée et les types forcés, union exportée en CSV, contrôle par somme de `montant` par ville contre la référence, note de pipeline rejouable, dépôt public à jour.

### Pour aller plus loin (bonus)

- **Générique et extensible** : structurez le pipeline pour qu'ajouter un 5ᵉ magasin ne demande qu'une ligne de configuration, pas une réécriture.
- **Contrôle qualité intégré** : avant l'export, faites échouer le pipeline (ou lever une alerte) si une colonne cible manque, si `montant` contient des valeurs négatives ou si des dates sont hors 2023.
- **Réconciliation complète** : reproduisez la comparaison à la référence sur **toutes** les villes en expliquant proprement pourquoi Dunkerque, Amiens et le canal en ligne ne peuvent pas correspondre à vos sources.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **pipeline** : script `.py` (ou classeur / requête Power Query) qui exécute Extract → Transform → Load de bout en bout ;
  - le **fichier consolidé produit** (`ventes_consolidees_<binome>.csv`) ;
  - une **note de pipeline** (`PIPELINE.md`) : entrées, transformations par source, sortie, procédure de relance ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Un **tableau de contrôle** (dans la note ou le code) comparant, ville par ville, votre somme de `montant` à celle de la référence, avec la conclusion (concorde / écart expliqué).

## Modalités d'évaluation

Évaluation en deux volets :

- **Pipeline et fichier consolidé (60 %)** : robustesse de l'extraction, exactitude de l'harmonisation (schéma, ville, types), correction de l'union et concordance du contrôle par ville, propreté et rejouabilité du code.
- **Restitution orale (40 %)** : 10 minutes de démonstration du flux relancé « à froid » devant un « comité data » (le formateur et un autre binôme) + 5 minutes de questions sur les choix de transformation et les écarts constatés.

**Validation partielle** : un binôme dont le fichier final n'est pas parfaitement réconcilié mais dont le pipeline est structuré, documenté et rejouable, et dont les écarts sont clairement identifiés et expliqués, peut valider partiellement les compétences travaillées.

## Critères de performance

**Extraire des sources hétérogènes**
- Les 4 fichiers sont chargés malgré séparateurs et noms de colonnes différents (Lille en `;`, Roubaix avec `qte`/`CA`).
- La volumétrie et les colonnes réelles de chaque source sont vérifiées à l'entrée.
- Aucune source n'est modifiée manuellement en amont du pipeline.

**Harmoniser vers le schéma cible**
- Le schéma cible `date, ville, categorie, produit, quantite, montant` est respecté par chaque source.
- La colonne `ville` est correctement ajoutée pour chaque fichier (dont Tourcoing et Valenciennes qui ne l'ont pas).
- Les types sont forcés : `date` normalisée (`YYYY-MM-DD`), `quantite` entière, `montant` décimal.

**Charger et contrôler**
- Les 4 sources harmonisées sont empilées et exportées en un CSV unique (`,`, avec en-têtes).
- La somme de `montant` par ville est comparée à la référence sur les 4 villes communes.
- Les écarts éventuels sont identifiés ET expliqués (pas seulement constatés).

**Documenter et rendre rejouable**
- La note de pipeline décrit entrées, transformations par source et sortie.
- La procédure de relance permet de régénérer le fichier sans manipulation manuelle.
- Le dépôt GitHub public est complet (pipeline exécutable + README).

## Ressources

- Module de cours — [ETL & automatisation](../../../15-Business-Intelligence/15-ETL-Automatisation/)
- Rappels — [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/)
- Semaine précédente sur la fiabilité des données — [Audit & EDA (S06)](semaine-06-eda-ventes-nordretail.md)
- Documentation pandas : https://pandas.pydata.org/docs/ — voir `read_csv(sep=...)`, `rename`, `assign`, `concat`
- Power Query : Append Queries, Rename/Replace, Change Type
- Prochaine étape du parcours — projet final de bout en bout : [BRIEF_3 — Tableau de bord BI](../BRIEF_3_PROJET_FINAL.md)
