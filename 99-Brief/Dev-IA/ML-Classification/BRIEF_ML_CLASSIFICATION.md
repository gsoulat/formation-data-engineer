# Brief : Prédire le désabonnement des clients de Fibrio et industrialiser le modèle avec MLflow

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Python (pandas, scikit-learn), MLflow (tracking + model registry), Evidently AI, Jupyter, Git & GitHub |
| **Prérequis** | [Cours Machine Learning](../../../08-Machine-Learning/) + [Métriques de classification](../../../08-Machine-Learning/cours/12-metriques-classification.md) + [Validation & généralisation](../../../08-Machine-Learning/cours/13-validation-generalisation.md) + [Cours MLflow](../../../08-Machine-Learning/MLOps/02-MLflow/) + [Détection de drift](../../../08-Machine-Learning/MLOps/06-Monitoring-Modele/) + [Cours Python](../../../01-Fondamentaux/Python/) |

## Contexte

### L'entreprise

**Fibrio** est un opérateur télécom alternatif français créé en 2017, spécialisé dans la fibre optique en zones péri-urbaines et rurales. Depuis son siège de Bordeaux, ses 120 salariés gèrent un parc d'environ 90 000 abonnés répartis sur trois offres (Essentiel, Confort, Premium). Le marché est saturé et la concurrence agressive : chaque mois, une part des clients résilient pour partir chez un opérateur national. L'équipe data est jeune : deux data analysts, un data engineer et vous, qui rejoignez l'entreprise comme développeur IA sur un premier projet de scoring.

### Le problème

La directrice de la relation client a un chiffre en tête : **recruter un nouvel abonné coûte environ cinq fois plus cher que d'en retenir un existant**. Or, aujourd'hui, Fibrio découvre les départs quand ils sont actés — la résiliation est déjà enregistrée, le client est déjà parti. Les campagnes de rétention (remise, upgrade, appel d'un conseiller) sont donc lancées trop tard, ou arrosent tout le monde sans distinction, ce qui coûte cher pour un effet marginal.

L'équipe marketing voudrait au contraire **concentrer l'effort de rétention sur les clients réellement à risque**, avant qu'ils ne partent. Pour cela, il faut un modèle capable, à partir du profil et de la consommation d'un abonné, d'estimer sa **probabilité de résiliation dans les prochaines semaines** — et il faut pouvoir faire confiance à ce modèle, comprendre pourquoi il se trompe, savoir quelle version tourne, et être alerté le jour où il vieillit mal.

### La question centrale

La directrice de la relation client résume l'attente en une phrase, qui devient la question centrale du projet. Chaque choix — jeu de données, métrique, modèle, seuil — devra pouvoir être justifié par sa contribution à cette question :

> **« Quels sont les abonnés que nous risquons de perdre bientôt, et pouvons-nous faire confiance à ce que le modèle nous dit ? »**

### Les sources de données

Fibrio n'ouvre pas encore ses données de production pour ce premier projet. Vous travaillez donc sur un **jeu de données public réel et représentatif du churn télécom**, que vous traiterez comme s'il s'agissait des données Fibrio :

- **Telco Customer Churn (IBM / Kaggle)** — jeu de référence du churn télécom : environ 7 000 clients, une vingtaine de variables (ancienneté, type de contrat, mode de paiement, services souscrits, charges mensuelles et totales) et une cible binaire `Churn` (Yes/No). URL : https://www.kaggle.com/datasets/blastchar/telco-customer-churn
- **Variante autorisée** si vous préférez un autre domaine de classification supervisée binaire : le **Bank Marketing Dataset** de l'UCI Machine Learning Repository (souscription d'un produit après campagne, ~45 000 lignes) — https://archive.ics.uci.edu/dataset/222/bank+marketing — ou le **Credit Card Fraud Detection** de Kaggle si vous voulez travailler un cas fortement déséquilibré — https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud. Un seul jeu suffit : choisissez et assumez votre choix.

> **Pièges réalistes assumés** : le jeu Telco contient des valeurs manquantes déguisées (des espaces dans `TotalCharges`), un déséquilibre de classes (~26 % de churn), des variables catégorielles à encoder et des colonnes inutiles au modèle (identifiant client). Ne les découvrez pas en production : traitez-les dès l'exploration.

### Contraintes techniques

- Tout est en **Python** : préparation et modélisation avec **pandas** et **scikit-learn**.
- Le suivi d'expériences passe **obligatoirement par MLflow** (serveur de tracking local, `mlflow ui`), avec versionnement des modèles via le **model registry**.
- La détection de dérive (drift) se fait avec **Evidently AI**.
- Aucun modèle pré-entraîné n'est fourni : vous construisez toute la chaîne, du CSV brut au modèle enregistré.
- Tout le code (notebooks et/ou scripts) est **versionné sur GitHub dès le premier jour**.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Préparer un jeu de données pour la classification supervisée** : explorer les données, traiter les valeurs manquantes et aberrantes, encoder les variables catégorielles, et construire une chaîne de préparation reproductible qui évite toute fuite de données (data leakage).
- **Entraîner et comparer plusieurs modèles de classification** : mettre en concurrence au moins trois familles d'algorithmes, choisir une stratégie de validation honnête (jeu de test tenu à l'écart, validation croisée), et régler leurs principaux hyperparamètres.
- **Évaluer un modèle avec rigueur** : sélectionner et interpréter les métriques adaptées à un problème déséquilibré (précision, rappel, F1, ROC-AUC, matrice de confusion), diagnostiquer le surapprentissage, et arbitrer un seuil de décision au regard de l'enjeu métier.
- **Assurer la traçabilité des expériences et des modèles** : journaliser paramètres, métriques et artefacts de chaque essai avec MLflow, comparer les runs, et promouvoir la version retenue dans le model registry.
- **Détecter la dérive d'un modèle en production** : simuler un lot de données futur, produire un rapport Evidently de dérive des données et de la cible, et proposer une règle de ré-entraînement.

## Démarche cible

Le projet est une **chaîne de classification supervisée end-to-end** : du CSV brut jusqu'à un modèle versionné et surveillé. Vous situerez chaque étape dans ce fil, et vous justifierez vos choix au regard de la question centrale.

```
        +----------------------------------------------+
        |   DONNÉES BRUTES (Telco Churn / UCI / CSV)   |
        +----------------------+-----------------------+
                               |
                    (exploration, nettoyage)
                               |
        +----------------------v-----------------------+
        |  PRÉPARATION  (valeurs manquantes, encodage, |
        |  split train/test SANS fuite de données)     |
        +----------------------+-----------------------+
                               |
                (entraînement de plusieurs modèles)
                               |
        +----------------------v-----------------------+
        |  EXPÉRIENCES  ── suivies dans MLflow ──       |
        |  modèle A / modèle B / modèle C              |
        |  params + métriques + artefacts par run      |
        +----------------------+-----------------------+
                               |
                  (évaluation rigoureuse, seuil)
                               |
        +----------------------v-----------------------+
        |  MODEL REGISTRY MLflow                       |
        |  version retenue promue en "Staging/Prod"    |
        +----------------------+-----------------------+
                               |
              (lot de données "futur" simulé)
                               |
        +----------------------v-----------------------+
        |  DÉTECTION DE DRIFT  (Evidently AI)          |
        |  rapport dérive données + cible → alerte     |
        +----------------------------------------------+
```

> Ce schéma vous sert de fil conducteur. Vous n'êtes pas obligé de le reproduire à l'identique, mais votre rendu doit rendre lisible ce cheminement du CSV brut au modèle surveillé.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, entraîne, évalue et soutient son propre modèle. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et exploration (J1)

Aucun modèle entraîné ce jour-là. Récupérez le jeu de données, chargez-le, et **explorez-le honnêtement** avant toute modélisation. C'est le moment de poser les bonnes questions et d'y répondre par des chiffres et des graphiques :

- Quelle est exactement la **cible** à prédire, et comment est-elle distribuée ? Le problème est-il **déséquilibré** ? De combien ?
- Quelles variables sont numériques, lesquelles sont catégorielles, lesquelles sont inutiles (identifiants) ou dangereuses (informations connues seulement après le départ du client) ?
- Où se cachent les **valeurs manquantes** — y compris celles déguisées en espaces ou en textes vides ?
- Quelles variables semblent, à l'œil, liées au churn ? Quelle serait une **hypothèse métier** que vous voudrez vérifier ?

Traduisez ensuite l'enjeu métier en enjeu de modélisation : dans le cas de Fibrio, **rater un client qui va partir** (faux négatif) et **déranger un client fidèle avec une offre de rétention** (faux positif) n'ont pas le même coût. Écrivez, en une phrase, laquelle de ces deux erreurs vous voudrez minimiser en priorité — cela guidera votre choix de métrique en phase 3.

Formalisez enfin votre plan de la semaine dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** un notebook (ou rapport) d'exploration commenté, la nature du problème (cible, déséquilibre, variables à écarter) et le Kanban présentés en 5 minutes au formateur.

### Phase 2 — Préparation et anti-fuite de données (J1-J2)

Construisez la **chaîne de préparation** : traitement des valeurs manquantes, encodage des variables catégorielles, éventuelle mise à l'échelle des variables numériques, suppression des colonnes inutiles.

Le point critique de cette phase est la **fuite de données (data leakage)**. Séparez le jeu en **entraînement et test** et gardez le test à l'écart. Puis posez-vous la question qui piège la moitié des débutants :

- Si vous calculez une moyenne pour combler les valeurs manquantes, ou les paramètres d'une normalisation, **sur quelles données** les calculez-vous ? Sur tout le jeu, ou seulement sur l'entraînement ?
- Une de vos variables « prédit-elle » un peu trop bien le churn parce qu'elle n'existe **qu'après** la résiliation ?

Idéalement, encapsulez la préparation dans un objet reproductible (par exemple un `Pipeline` scikit-learn) pour que la même transformation s'applique à l'entraînement, au test et, plus tard, aux données futures.

**Résultat testable :** un jeu d'entraînement et un jeu de test prêts à l'emploi, produits par un code rejouable, et une explication écrite de la manière dont vous avez évité la fuite de données.

### Phase 3 — Entraînement, comparaison et suivi MLflow (J2-J3)

Entraînez et comparez **au moins trois familles de modèles** (par exemple régression logistique, arbre / forêt aléatoire, et un modèle de boosting type gradient boosting). Chaque entraînement est une **expérience suivie dans MLflow** :

- lancez un serveur de tracking local (`mlflow ui`) ;
- pour **chaque run**, journalisez les **hyperparamètres**, les **métriques** (voir plus bas), et les **artefacts** (le modèle sérialisé, éventuellement une figure de la matrice de confusion) ;
- nommez et organisez vos runs pour pouvoir les **comparer** dans l'interface MLflow.

Côté évaluation, ne vous contentez pas de l'*accuracy* : sur un problème déséquilibré, un modèle qui prédit « personne ne part » peut afficher 74 % de bonnes réponses tout en étant inutile. Calculez et interprétez au minimum : **précision, rappel, F1, ROC-AUC** et la **matrice de confusion**. Reliez-les à la phase 1 : la métrique que vous mettez en avant doit correspondre à l'erreur que Fibrio veut éviter en priorité.

Enfin, traquez le **surapprentissage** : comparez la performance sur l'entraînement et sur le test (ou en validation croisée). Un écart important est un signal — que faites-vous alors ?

**Résultat testable :** dans l'interface MLflow, au moins trois runs comparables avec leurs hyperparamètres, leurs métriques et le modèle en artefact ; et un tableau de comparaison des modèles dans votre rapport.

### Phase 4 — Modèle retenu, seuil et model registry (J3-J4)

Choisissez le **modèle à retenir** et **justifiez ce choix** : ce n'est pas forcément celui qui a le meilleur ROC-AUC, c'est celui qui sert le mieux la question centrale.

Travaillez ensuite le **seuil de décision**. Par défaut, on classe « churn » au-dessus de 0,5 de probabilité, mais rien n'oblige à garder 0,5 : abaisser le seuil attrape plus de partants (meilleur rappel) au prix de plus de fausses alertes. Montrez, chiffres à l'appui, l'effet d'au moins deux seuils sur la précision et le rappel, et recommandez-en un pour Fibrio en argumentant sur le coût des erreurs.

Enregistrez enfin le modèle retenu dans le **model registry MLflow** : donnez-lui un nom, une version, et promouvez-le dans un stade (par exemple « Staging » ou « Production »). Documentez comment quelqu'un pourrait recharger cette version précise pour faire une prédiction.

**Résultat testable :** un modèle nommé et versionné visible dans le model registry, une justification écrite du modèle et du seuil retenus, et une démonstration de rechargement du modèle depuis le registry pour prédire sur un client.

### Phase 5 — Détection de drift et consolidation (J5)

Un modèle ne reste pas bon éternellement : les comportements des clients changent, une nouvelle offre concurrente apparaît, et les données d'entrée dérivent. Simulez ce futur : construisez un **lot de données « courant »** différent du jeu d'entraînement (par exemple en sous-échantillonnant un segment, en décalant une variable, ou en réservant une partie du jeu comme « données de production »).

Avec **Evidently AI**, produisez un **rapport de dérive** comparant les données d'entraînement (référence) et ce lot courant :

- Quelles variables ont **dérivé** ? La distribution de la cible a-t-elle bougé ?
- À partir de quel niveau de dérive **déclencheriez-vous un ré-entraînement** ? Écrivez cette règle noir sur blanc.

Finalisez ensuite le **README** (description, question métier, technologies, installation, comment relancer l'entraînement, comment consulter MLflow, comment lire le rapport de drift, auteur), vérifiez que tout est **rejouable de zéro**, mettez à jour le Kanban, et préparez votre démonstration : ordre des étapes, plan B si MLflow refuse de démarrer le jour J.

### Socle commun (obligatoire)

- Une **exploration** documentée du jeu de données (cible, déséquilibre, variables écartées, valeurs manquantes).
- Une **chaîne de préparation reproductible** avec split train/test et **anti-fuite de données** explicité.
- Au moins **trois modèles** entraînés et comparés, chacun suivi comme un **run MLflow** (params, métriques, artefacts).
- Une **évaluation rigoureuse** : précision, rappel, F1, ROC-AUC, matrice de confusion, et diagnostic de surapprentissage.
- Un **modèle retenu justifié**, avec travail du **seuil de décision**, enregistré et promu dans le **model registry MLflow**.
- Un **rapport de drift Evidently** entre un jeu de référence et un lot courant, avec une règle de ré-entraînement.
- Un **repo GitHub public** documenté avec un Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- **Optimiser les hyperparamètres** du modèle retenu par recherche systématique (grid/random search) et tracer chaque essai dans MLflow.
- Ajouter une **interprétabilité** du modèle (importance des variables, ou valeurs SHAP) pour expliquer au marketing pourquoi un client est jugé à risque.
- Traiter explicitement le **déséquilibre de classes** (rééchantillonnage, pondération des classes) et mesurer le gain.
- **Servir** le modèle du registry derrière une petite API (FastAPI) ou un `mlflow models serve`, et prédire via une requête.
- Automatiser le **rapport de drift** en script rejouable, avec un seuil qui renvoie un code de sortie « ré-entraînement nécessaire ».

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un **README structuré** : description du projet et de la question métier, jeu de données utilisé (avec sa source), technologies, instructions d'installation et de lancement pas à pas (dont le lancement de `mlflow ui`), comment relancer l'entraînement, comment lire le rapport de drift, auteur.
- Le **notebook (ou script) d'exploration et de préparation** : traitement des valeurs manquantes, encodage, split train/test, avec l'explication de la parade anti-fuite de données.
- Le **code d'entraînement et de comparaison** des trois modèles, instrumenté avec MLflow, et un **tableau de comparaison** des modèles (métriques côte à côte) dans le rapport ou le README.
- Une **capture ou export du model registry MLflow** montrant le modèle retenu, sa version et son stade, plus le code de **rechargement** du modèle pour prédire.
- Le **rapport de dérive Evidently** (HTML ou export) et la **règle de ré-entraînement** écrite.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture ou extrait) dans un dossier `bonus/` clairement séparé du socle.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous montrez le cheminement du CSV brut au modèle surveillé : l'exploration et la préparation, l'interface MLflow avec vos trois runs comparés, le modèle retenu dans le model registry rechargé pour prédire sur un client, et le rapport de drift Evidently. Les questions portent sur vos choix : pourquoi cette métrique, comment vous avez évité la fuite de données, pourquoi ce modèle et ce seuil, comment vous diagnostiquez un surapprentissage, quand vous ré-entraîneriez.
- **Revue de code et de méthode — 30 %** : examen du repo GitHub public (structure, lisibilité, reproductibilité, qualité du README), de la rigueur de l'évaluation (métriques adaptées au déséquilibre, honnêteté du split, absence de fuite de données) et de la clarté des justifications métier.

> **Validation partielle** : un projet dont un maillon ne fonctionne pas en démonstration (par exemple le rechargement depuis le registry) mais dont le code est structuré, versionné et documenté peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de documentation et de justifications ne valide pas les critères de méthode.

## Critères de performance

### Préparation des données pour la classification

- L'exploration identifie la cible, le déséquilibre de classes et les variables à écarter (identifiants, variables issues du futur).
- Les valeurs manquantes (y compris déguisées) et les variables catégorielles sont traitées de façon documentée.
- Le jeu est séparé en entraînement et test, et la **fuite de données est explicitement évitée** (transformations ajustées sur l'entraînement seulement).
- La chaîne de préparation est **reproductible** : relancer le code produit les mêmes jeux préparés.

### Entraînement et comparaison de modèles

- Au moins **trois familles de modèles** sont entraînées sur les mêmes données préparées.
- La stratégie de validation est honnête (jeu de test tenu à l'écart et/ou validation croisée).
- Les principaux hyperparamètres de chaque modèle sont renseignés et journalisés.
- Un **tableau de comparaison** met les modèles en regard sur des métriques communes.

### Évaluation rigoureuse

- Les métriques adaptées à un problème déséquilibré sont calculées et interprétées : **précision, rappel, F1, ROC-AUC, matrice de confusion**.
- Le **surapprentissage** est diagnostiqué (comparaison entraînement / test ou validation croisée) et commenté.
- Le **seuil de décision** est étudié (au moins deux seuils comparés) et un choix est recommandé au regard du coût des erreurs pour Fibrio.
- La métrique mise en avant correspond à l'erreur métier prioritaire identifiée en phase 1.

### Traçabilité MLflow et model registry

- Chaque run MLflow journalise **paramètres, métriques et artefacts** et les runs sont comparables dans l'interface.
- Le modèle retenu est **justifié** au regard de la question centrale, pas seulement du meilleur score brut.
- Le modèle retenu est **enregistré et promu** dans le model registry (nom, version, stade).
- Le rechargement du modèle depuis le registry pour produire une prédiction est démontré.

### Détection de dérive

- Un lot de données « courant » distinct de la référence est construit et documenté.
- Un **rapport Evidently** de dérive des données (et de la cible) est produit et lu.
- Les variables ayant dérivé sont identifiées et commentées.
- Une **règle de ré-entraînement** (seuil de dérive déclencheur) est écrite explicitement.

## Ressources

- [Cours Machine Learning](../../../08-Machine-Learning/)
- [Comprendre les données](../../../08-Machine-Learning/cours/06-comprendre-donnees.md)
- [Feature engineering](../../../08-Machine-Learning/cours/07-feature-engineering.md)
- [Data leakage](../../../08-Machine-Learning/cours/08-data-leakage.md)
- [Métriques de classification](../../../08-Machine-Learning/cours/12-metriques-classification.md)
- [Validation & généralisation](../../../08-Machine-Learning/cours/13-validation-generalisation.md)
- [Cours MLflow (tracking & model registry)](../../../08-Machine-Learning/MLOps/02-MLflow/)
- [Détection de drift](../../../08-Machine-Learning/MLOps/06-Monitoring-Modele/)
- [Cours Python](../../../01-Fondamentaux/Python/)
- Documentation scikit-learn — modèles de classification et métriques : https://scikit-learn.org/stable/supervised_learning.html
- scikit-learn — Pipeline et prévention de la fuite de données : https://scikit-learn.org/stable/modules/compose.html
- Documentation officielle MLflow (tracking) : https://mlflow.org/docs/latest/tracking.html
- MLflow Model Registry : https://mlflow.org/docs/latest/model-registry.html
- Evidently AI — détection de data drift : https://docs.evidentlyai.com/
- Jeu de données Telco Customer Churn (Kaggle) : https://www.kaggle.com/datasets/blastchar/telco-customer-churn
- UCI Machine Learning Repository — Bank Marketing (variante) : https://archive.ics.uci.edu/dataset/222/bank+marketing
