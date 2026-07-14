# Brief : Sauver le pipeline « qualité de l'air » de VéloCité — d'un script spaghetti à un code propre, testé et outillé

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Python 3.11+, pandas, Pydantic, pytest, pytest-cov, ruff, mypy, pre-commit, module `logging`, Git & GitHub |
| **Prérequis** | [Cours Python](../../../01-Fondamentaux/Python/) + [Python — Qualité & Tests](../../../01-Fondamentaux/Python/05-Qualite-Tests/) + [Python — Data Engineering (ETL)](../../../01-Fondamentaux/Python/06-Data-Engineering/) + [Bonnes pratiques](../../../01-Fondamentaux/Bonne%20pratique/) + [Pre-commit](../../../07-DevOps/03-Pre-commit/) + [Cours Git](../../../01-Fondamentaux/Git/) |

## Contexte

### L'entreprise

**VéloCité** est une scale-up française de mobilité douce, née à Nantes en 2018. Elle exploite une flotte de vélos et trottinettes en libre-service dans une dizaine de villes de taille moyenne, et vend à ces collectivités un service d'analyse : « où et quand vos habitants se déplacent, et dans quel air ». L'entreprise compte 70 salariés, dont une petite équipe data de quatre personnes. Pour étoffer son offre auprès des villes, VéloCité croise ses trajets avec la **qualité de l'air** locale, afin de recommander des itinéraires moins pollués.

### Le problème

Il y a huit mois, un stagiaire a écrit **en une nuit** un script Python qui récupère les mesures de qualité de l'air de plusieurs stations, les nettoie et produit un fichier quotidien pour les data analysts. Le script « marche » — la plupart du temps. Mais le stagiaire est parti, personne d'autre n'ose y toucher, et les symptômes s'accumulent :

- c'est **un seul fichier de 400 lignes**, une longue suite d'instructions sans une seule fonction, avec des variables nommées `df`, `df2`, `df3`, `tmp`, `x` ;
- **aucun test** : la seule façon de savoir si une modification casse quelque chose, c'est de lancer le script en entier et de regarder le fichier de sortie « à l'œil » ;
- des `print()` partout, mais **aucun log exploitable** quand le script plante à 4 h du matin ;
- des **valeurs codées en dur** (chemins, seuils, codes de polluants) au milieu du code ;
- quand une station renvoie une valeur aberrante ou un format de date exotique, le script **plante** ou, pire, produit un résultat faux **sans rien signaler**.

Le lead data l'a dit clairement en réunion : *« On ne réécrit pas tout, et on ne rajoute aucune fonctionnalité cette semaine. On prend ce script, on le rend lisible, testable et robuste — sans changer ce qu'il produit. »* C'est un **refactoring**, pas une réécriture : à la fin, la sortie du pipeline propre doit être **identique** à celle du script d'origine sur les mêmes données. Vous héritez du script brouillon (fourni dans le kit de démarrage) et de cette mission.

### La question centrale

Le lead data résume l'enjeu en une phrase, qui devient la question centrale du projet. Chaque décision de refactoring de la semaine devra pouvoir se justifier par sa contribution à cette question :

> **« Le jour où ce pipeline plante à 4 h du matin, combien de temps me faut-il pour comprendre pourquoi, et pour prouver que ma correction n'a rien cassé ? »**

### Les sources de données

- **Script brouillon de départ** (`legacy/pipeline_legacy.py`, fourni dans le kit de démarrage) : le script « spaghetti » à refactorer, avec ses pièges volontaires (fonction unique, noms opaques, valeurs codées en dur, `print` de debug, absence de gestion d'erreur, formats de date hétérogènes traités « au petit bonheur »).
- **Un extrait de données figé** (`data/mesures_sample.csv`, fourni) : un échantillon réel de mesures capturé un jour donné, servant de **jeu de référence** pour prouver la non-régression. Il contient des cas piégeux réalistes : valeurs négatives impossibles, doublons horaires, dates au format `JJ/MM/AAAA` et `AAAA-MM-JJ` mélangées, codes de polluants inconnus, cellules vides.
- **La source réelle branchée en fin de semaine** : l'API publique **OpenAQ v3** (mesures de qualité de l'air dans le monde, dont la France) — https://docs.openaq.org/ (une clé gratuite s'obtient en quelques minutes). En repli ou en complément, le portail **data.gouv.fr** expose des jeux de données de qualité de l'air de **Geod'Air / Atmo** : https://www.data.gouv.fr/fr/datasets/?q=qualit%C3%A9%20de%20l%27air.
- **Pour le bonus** : l'API **OpenAQ** en direct (plusieurs stations, pagination), et un second polluant pour éprouver la généricité de votre code refactoré.

Ce brief est un épisode de la vie data de VéloCité, mais il est réalisable de façon **autonome** : le kit de démarrage contient le script brouillon et l'extrait de données figé. Aucun livrable d'un brief précédent n'est nécessaire, et vous pouvez travailler toute la semaine **sans clé d'API** grâce au jeu de référence — l'API réelle n'intervient qu'en fin de parcours.

### Contraintes techniques

- **Refactoring, pas réécriture** : à iso-données (l'extrait figé), la sortie du pipeline propre doit être **identique** à celle du script d'origine. Vous ne changez pas la fonctionnalité, vous changez la **qualité**.
- **Python 3.11+**, environnement isolé (`venv` ou équivalent), dépendances épinglées dans un fichier (`requirements.txt` ou `pyproject.toml`).
- Outillage qualité **automatisé via pre-commit** : formatage/lint (`ruff`), typage statique (`mypy`), et exécution des tests.
- **Aucun secret dans le dépôt** : la clé d'API OpenAQ passe par une variable d'environnement (`.env` ignoré par Git), et un `.env.example` documente les variables attendues.
- Tout le travail est **versionné sur GitHub dès le premier jour**, avec des commits atomiques et parlants.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Cadrer un refactoring sans régression** : lire un script existant, en cartographier les étapes, capturer sa sortie de référence et définir le contrat de non-régression avant de toucher une ligne de code.
- **Structurer un pipeline data en code propre** : découper une logique monolithique en fonctions et modules à responsabilité unique, appliquer des conventions de nommage lisibles, annoter les types, externaliser la configuration et documenter le code par des docstrings.
- **Fiabiliser un traitement de données par les tests** : écrire une suite de tests `pytest` couvrant les cas nominaux et les cas limites (doublons, valeurs aberrantes, formats de date hétérogènes), mesurer la couverture et garantir la reproductibilité des résultats.
- **Outiller la qualité en continu** : configurer `pre-commit` (formatage, lint, typage, tests) et une journalisation structurée (`logging`) qui permettent de diagnostiquer un incident et d'empêcher qu'un code non conforme n'entre dans le dépôt.

## Architecture cible

Le script d'origine est un **bloc unique**. La cible est un **pipeline modulaire** où chaque étape — extraction, validation/nettoyage, transformation, chargement — est une fonction (ou un module) testable isolément, orchestrée par un point d'entrée mince. La configuration (chemins, seuils, codes de polluants, clé d'API) est **externalisée**, la journalisation remplace les `print`, et l'outillage qualité s'exécute automatiquement avant chaque commit.

```
   AVANT (legacy)                              APRÈS (cible)
   ==============                              =============

   pipeline_legacy.py                          src/velocite_air/
   ┌───────────────────────┐                   ├── config.py      (chemins, seuils, env)
   │ import ...             │                   ├── extract.py     (lecture CSV / API)
   │ df = read_csv(...)     │                   ├── validate.py    (schéma, cas limites)
   │ df2 = ...  # 400       │   refactoring     ├── transform.py   (nettoyage, agrégats)
   │ lignes, 0 fonction,    │  ────────────►    ├── load.py        (écriture sortie)
   │ print() partout,       │  (iso-sortie)     ├── logging_conf.py(journalisation)
   │ seuils codés en dur    │                   └── pipeline.py    (orchestration, main)
   │ aucun test             │                   tests/
   └───────────────────────┘                   ├── test_validate.py
                                                ├── test_transform.py
                                                └── test_pipeline.py  (non-régression)
        │                                       .pre-commit-config.yaml (ruff, mypy, pytest)
        │  MÊME entrée figée                    │
        ▼                                       ▼
   sortie_reference.csv        ═══ doit être identique ═══        sortie.csv
```

> Vous produirez votre propre schéma (avant/après, ou diagramme des modules) **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu. Le découpage en modules ci-dessus est un point de départ : vous pouvez l'adapter et devez le justifier.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `legacy/pipeline_legacy.py` — le **script brouillon** à refactorer (à conserver intact comme référence, ne pas l'effacer) ;
- `data/mesures_sample.csv` — l'**extrait de données figé** servant de jeu de référence pour la non-régression ;
- un court `README` décrivant ce que le script est censé produire et comment le lancer.

> **Important** : le kit ne fournit **ni** structure de projet propre, **ni** tests, **ni** configuration d'outillage. C'est à vous de construire l'arborescence cible, la suite de tests, le `.pre-commit-config.yaml` et la journalisation à partir des cours listés en fin de brief.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun refactore et défend son propre pipeline. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et filet de sécurité (J1)

Aucune ligne de refactoring. Clonez le kit, **lisez le script brouillon de bout en bout** et cartographiez ce qu'il fait réellement : quelles sont ses étapes ? Que lit-il, que produit-il, dans quel ordre ? Où sont les valeurs codées en dur, les `print`, les endroits fragiles ?

Avant de changer quoi que ce soit, **fabriquez votre filet de sécurité** : exécutez le script d'origine sur l'extrait figé et **capturez sa sortie de référence** (le fichier produit). C'est votre étalon : à la fin de la semaine, votre pipeline propre devra reproduire cette sortie à l'identique. Réfléchissez :

- Comment allez-vous **prouver** que votre refactoring ne change pas le résultat ? Comparaison de fichiers ? Test automatisé qui rejoue l'entrée figée et compare à la référence ?
- Quels **cas limites** repérez-vous déjà dans les données (valeurs négatives, doublons, dates au format mélangé, codes de polluants inconnus, cellules vides) et comment le script actuel les traite-t-il — bien, mal, ou pas du tout ?

Établissez enfin un **inventaire des « odeurs de code »** (code smells) : fonction géante, noms opaques, duplication, magie des nombres, absence de gestion d'erreur. Formalisez votre plan de refactoring dans un **Kanban public** avec des user stories (« En tant que mainteneur, je veux… »).

**Résultat testable en fin de J1 :** sortie de référence capturée, inventaire des code smells et Kanban présentés en 5 minutes au formateur — sans avoir encore modifié la logique.

### Phase 2 — Découpage, nommage et configuration (J2)

Commencez le refactoring par la **structure**. Transformez le bloc unique en fonctions à **responsabilité unique** : une fonction qui extrait, une qui valide, une qui transforme, une qui charge, et un point d'entrée mince qui orchestre. Répartissez-les dans des **modules** cohérents.

- Chaque fonction fait-elle **une seule chose**, et son nom le dit-il sans commentaire ?
- Les variables `df2`, `tmp`, `x` ont-elles disparu au profit de noms qui racontent l'intention ?
- Les valeurs codées en dur (chemins, seuils, codes de polluants) sont-elles **externalisées** dans une configuration (module dédié, variables d'environnement, fichier `.env` pour les secrets) ?

Ajoutez au fil de l'eau des **annotations de types** sur les signatures de fonctions et des **docstrings** qui expliquent le *pourquoi*, pas le *comment*. Après chaque étape de découpage, **relancez le pipeline sur l'entrée figée** et vérifiez que la sortie n'a pas bougé.

**Résultat testable en fin de J2 :** le pipeline découpé en fonctions/modules typés et documentés produit **exactement** la même sortie que la référence, configuration externalisée à l'appui.

### Phase 3 — Tests pytest et cas limites (J3)

Le cœur de la fiabilité. Écrivez une suite de tests **`pytest`** qui verrouille le comportement de votre code :

- des tests **unitaires** sur les fonctions de validation et de transformation (une valeur négative est-elle bien rejetée ? un doublon horaire est-il bien dédupliqué ? une date `JJ/MM/AAAA` est-elle bien normalisée ?) ;
- un test de **non-régression** qui rejoue l'entrée figée dans le pipeline complet et compare le résultat à la sortie de référence capturée en phase 1 ;
- des tests des **cas limites** repérés : fichier vide, colonne manquante, code de polluant inconnu, cellule vide.

Mesurez la **couverture** (`pytest-cov`) et concentrez l'effort là où la logique métier est dense (validation, transformation) plutôt que de courir après 100 %.

- Que se passe-t-il quand un test échoue : **comprenez-vous immédiatement** ce qui est cassé ?
- Vos tests sont-ils **reproductibles** (pas de dépendance à l'heure courante, à un fichier hors dépôt, à un ordre d'exécution) ?

**Résultat testable en fin de J3 :** `pytest` s'exécute au vert, la couverture est mesurée et commentée, et le test de non-régression prouve l'iso-sortie.

### Phase 4 — Journalisation et pre-commit (J4)

Rendez le pipeline **diagnosticable** et **infranchissable pour du code non conforme**. Remplacez les `print` par une **journalisation structurée** (`logging`) : niveaux (`INFO` pour le déroulé, `WARNING` pour une valeur écartée, `ERROR` pour un échec), messages qui situent l'incident (quelle station, quelle ligne, quelle valeur), et une gestion d'erreur explicite là où le script d'origine plantait en silence.

- En relisant vos logs d'une exécution, **peut-on raconter** ce qui s'est passé et pourquoi telle mesure a été écartée ?

Configurez ensuite **`pre-commit`** pour automatiser la qualité à chaque commit : formatage et lint (`ruff`), typage statique (`mypy`), et exécution des tests. Vérifiez qu'un commit contenant du code mal formaté, non typé ou cassant un test est **bien bloqué**.

- Si un collègue clone le repo, une seule commande installe-t-elle les hooks et fait-elle tourner toute la chaîne qualité ?

**Résultat testable en fin de J4 :** `pre-commit run --all-files` passe au vert, les logs remplacent tous les `print`, et une modification volontairement fautive est refusée par les hooks.

### Phase 5 — Branchement de la source réelle, doc et démo (J5)

Branchez enfin la **source réelle** : remplacez (ou complétez) la lecture du CSV figé par un appel à l'**API OpenAQ v3** (clé en variable d'environnement) ou par un jeu **data.gouv.fr / Geod'Air**, en réutilisant vos fonctions refactorées — c'est le test ultime de votre découpage : si l'extraction est bien isolée, changer de source ne doit toucher qu'un module.

Finalisez le **README** (description, question métier, technologies, installation, lancement, lancement des tests et de pre-commit, avant/après du refactoring, auteur), intégrez le **schéma avant/après**, vérifiez que tout se relance **de zéro** sur une machine propre, puis répétez votre démonstration : ordre des commandes, plan B si l'API est indisponible (repli sur le jeu figé).

### Socle commun (obligatoire)

- **Sortie de référence** capturée et **non-régression prouvée** par un test automatisé (iso-sortie sur l'entrée figée).
- Pipeline **découpé en fonctions/modules** à responsabilité unique, **noms lisibles**, **types annotés**, **docstrings**.
- **Configuration externalisée** (aucune valeur métier ni secret codé en dur ; `.env` ignoré, `.env.example` fourni).
- Suite **`pytest`** couvrant cas nominaux et **cas limites** (doublons, valeurs aberrantes, formats de date, colonnes manquantes), **couverture mesurée**.
- **Journalisation `logging`** (niveaux, messages situés) à la place des `print`, gestion d'erreur explicite.
- **`.pre-commit-config.yaml`** opérationnel (ruff + mypy + pytest) et démontré.
- Source **réelle branchée** (OpenAQ ou data.gouv.fr) via le module d'extraction, clé en variable d'environnement.
- Repo public documenté avec **README**, **schéma avant/après** et **Kanban**.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Ajouter une **validation de schéma déclarative** avec **Pydantic** (types, bornes, valeurs autorisées) et des messages d'erreur parlants.
- Consommer l'API **OpenAQ en direct sur plusieurs stations** avec pagination et gestion des limites de débit.
- Ajouter un second **polluant** pour prouver que le code refactoré est générique (aucune duplication).
- Mettre en place une **intégration continue GitHub Actions** qui rejoue lint + typage + tests à chaque push.
- Générer un **badge de couverture** et une **documentation d'API** à partir des docstrings.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un **README structuré** : description du projet et de la question métier, technologies utilisées, instructions d'installation et de lancement pas à pas, **comment lancer les tests** et **pre-commit**, tableau ou paragraphe **avant/après** du refactoring, auteur.
- Le **script brouillon d'origine conservé** (`legacy/`) et le **pipeline refactoré** structuré en fonctions/modules typés et documentés.
- La **suite de tests `pytest`**, dont le **test de non-régression** (iso-sortie) et les tests de cas limites, avec le **rapport de couverture** (fichier ou capture).
- Le **`.pre-commit-config.yaml`** (ruff, mypy, pytest) et le fichier de dépendances épinglées.
- La **configuration externalisée** et le **`.env.example`** (aucun secret dans le dépôt).
- Le **schéma avant/après au format image** (PNG ou export draw.io, pas d'ASCII).
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories de refactoring.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous montrez l'avant/après du code, lancez `pytest` (dont le test de non-régression) et `pre-commit`, prouvez que le pipeline refactoré produit la **même sortie** que la référence, déclenchez au moins un **scénario de robustesse** (une donnée aberrante correctement écartée et journalisée, ou un commit fautif bloqué par les hooks) et exécutez le pipeline sur la **source réelle**. Les questions portent sur vos choix : découpage en modules, stratégie de test, gestion d'erreur, externalisation de la configuration.
- **Revue de code et de qualité — 30 %** : examen du repo (structure, lisibilité, nommage, types, docstrings, absence de valeurs codées en dur), de la suite de tests (pertinence des cas limites, couverture), de la configuration pre-commit, de la journalisation et de la qualité du README.

> **Validation partielle** : un pipeline dont la source réelle ne se branche pas en démonstration mais dont le code est proprement structuré, testé, journalisé et versionné peut valider partiellement les compétences concernées. À l'inverse, un code qui « tourne » mais reste monolithique, non testé et sans journalisation ne valide pas les critères de qualité.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Cadrage du refactoring et non-régression

- La sortie de référence du script d'origine est capturée et sert d'étalon documenté.
- Un test automatisé rejoue l'entrée figée dans le pipeline complet et prouve l'iso-sortie (OUI/NON).
- L'inventaire des code smells du script d'origine est présent et exploité dans le plan de refactoring.
- Le Kanban public retrace les user stories de refactoring et leur progression.

### Structuration en code propre

- Le pipeline est découpé en fonctions/modules à responsabilité unique, sans bloc monolithique résiduel.
- Les identifiants (fonctions, variables) portent des noms lisibles qui expriment l'intention (plus de `df2`, `tmp`, `x`).
- Les signatures de fonctions sont annotées de types et les fonctions publiques disposent de docstrings.
- Aucune valeur métier ni secret n'est codé en dur : la configuration est externalisée et `.env` est ignoré par Git (`.env.example` fourni).

### Fiabilisation par les tests

- Une suite `pytest` couvre les cas nominaux et les cas limites (doublons, valeurs aberrantes, formats de date hétérogènes, colonnes manquantes).
- La couverture de tests est mesurée (`pytest-cov`) et commentée.
- Les tests sont reproductibles (pas de dépendance à l'heure courante, à l'ordre d'exécution ou à un fichier hors dépôt).
- Un échec de test produit un message qui identifie clairement la fonction et le cas en cause.

### Outillage qualité et journalisation

- Un `.pre-commit-config.yaml` opérationnel enchaîne formatage/lint (ruff), typage (mypy) et tests, et bloque effectivement un commit non conforme.
- Les `print` de debug sont remplacés par une journalisation `logging` à niveaux, avec des messages qui situent l'incident.
- La gestion d'erreur est explicite là où le script d'origine plantait ou produisait un résultat faux en silence.
- La source réelle (OpenAQ ou data.gouv.fr) est branchée via le module d'extraction, avec la clé/les paramètres en variable d'environnement.

## Ressources

- [Cours Python](../../../01-Fondamentaux/Python/)
- [Python — Qualité & Tests (analyse statique, pytest, couverture, pre-commit, logging)](../../../01-Fondamentaux/Python/05-Qualite-Tests/)
- [Python — Data Engineering (ETL en Python, Pydantic, formats de données)](../../../01-Fondamentaux/Python/06-Data-Engineering/)
- [Bonnes pratiques (structure, conventions de nommage, code propre)](../../../01-Fondamentaux/Bonne%20pratique/)
- [Pre-commit](../../../07-DevOps/03-Pre-commit/)
- [Cours Git](../../../01-Fondamentaux/Git/)
- Documentation pytest : https://docs.pytest.org/
- Couverture de code avec pytest-cov : https://pytest-cov.readthedocs.io/
- Ruff (linter et formateur Python) : https://docs.astral.sh/ruff/
- mypy (typage statique) : https://mypy.readthedocs.io/
- pre-commit (hooks Git) : https://pre-commit.com/
- Journalisation en Python (module `logging`) : https://docs.python.org/fr/3/howto/logging.html
- PEP 8 — style de code Python : https://peps.python.org/pep-0008/
- API OpenAQ v3 (qualité de l'air) : https://docs.openaq.org/
- Jeux de données qualité de l'air sur data.gouv.fr : https://www.data.gouv.fr/fr/datasets/?q=qualit%C3%A9%20de%20l%27air
