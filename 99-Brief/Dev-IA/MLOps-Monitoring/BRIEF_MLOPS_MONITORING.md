# Brief : Industrialiser l'API de scoring de Solvia — CI/CD, déploiement et monitoring en production

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire à avancé |
| **Modalité** | Individuel |
| **Technologies** | Python (FastAPI), scikit-learn, Docker & Docker Compose, GitHub Actions, pytest & coverage, GitHub Container Registry, Prometheus, Grafana, Alertmanager, Git |
| **Prérequis** | [Cours FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/) + [Qualité & tests Python](../../../01-Fondamentaux/Python/05-Qualite-Tests/) + [Cours Docker](../../../02-Containerisation/Docker/) + [CI/CD & GitHub Actions](../../../07-DevOps/01-CI-CD/03-GitHub-Actions/) + [Monitoring Prometheus/Grafana](../../../07-DevOps/02-Monitoring/) + [MLOps — Monitoring de modèle](../../../08-Machine-Learning/MLOps/06-Monitoring-Modele/) |

## Contexte

### L'entreprise

**Solvia** est une scale-up française de la *fintech* fondée à Nantes en 2019. Ses 60 salariés éditent une plateforme SaaS qui aide les TPE et PME à évaluer le risque de défaut de paiement de leurs clients professionnels avant d'accorder un délai de règlement. Le cœur du produit est un **modèle de scoring de risque de crédit** exposé via une **API REST** que les clients appellent depuis leur logiciel de facturation. L'équipe technique compte une dizaine de développeurs, un data scientist qui a entraîné le modèle, et une squad *plateforme* de deux personnes — dont vous, qui venez d'arriver comme **développeur·se IA en charge du MLOps**.

### Le problème

L'API de scoring fonctionne, mais elle a été construite « à la main » par le data scientist et déployée par copier-coller sur un serveur. Concrètement : aucune suite de tests ne tourne avant une mise en ligne, l'image n'est reconstruite qu'au gré des disponibilités, et **personne ne sait ce qui se passe une fois l'API en production**. Le mois dernier, une régression a laissé passer un bug qui renvoyait un score erroné pendant six heures avant qu'un client ne s'en plaigne par e-mail. Pire : le data scientist soupçonne que la distribution des demandes de scoring a « bougé » depuis l'entraînement (nouveaux secteurs d'activité, montants plus élevés), mais **personne ne le mesure** : le *drift* est invisible.

La direction technique a fixé un cap clair : plus aucune mise en production « à la main ». L'API doit passer par une **chaîne de livraison continue** (tests, couverture, construction et publication de l'image) et, une fois déployée, être **observée en continu** — latence, taux d'erreur, dérive des données entrantes — avec des **alertes** qui préviennent l'équipe *avant* le client.

### La question centrale

Le lead tech résume l'attendu de la semaine en une phrase, qui devient la question centrale du projet. Chaque choix d'outillage devra pouvoir être justifié par sa contribution à cette question :

> **« Notre API de scoring est-elle en bonne santé en ce moment, et le saurons-nous avant nos clients ? »**

### Les sources de données

Vous ne réentraînez **pas** le modèle : votre métier ici est de l'**industrialiser** et de le **surveiller**. Vous partez néanmoins de données et d'un modèle réels et reproductibles.

- **Jeu de données de référence — German Credit Data (UCI Machine Learning Repository)** : 1 000 demandes de crédit annotées « bon » / « mauvais » payeur, avec des variables comme le montant, la durée, l'historique de crédit et l'objet du prêt. C'est ce jeu qui sert de **base d'entraînement** et de **distribution de référence** pour la détection de drift. https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- **Modèle et API de départ** (fournis dans le kit de démarrage `starter-kit/`) : un modèle **scikit-learn** déjà entraîné sur German Credit (fichier sérialisé), et une **API FastAPI minimale** qui expose une route `POST /predict`. Le code est volontairement « brut » : peu de tests, aucune métrique exposée, pas de CI. C'est votre point de départ, pas votre livrable final.
- **Générateur de trafic** (fourni) : un script Python qui envoie des requêtes à votre API pour simuler l'usage en production. Il sait produire du **trafic nominal** (demandes proches de la distribution d'entraînement), du **trafic dégradé** (payloads invalides, champs manquants → erreurs) et du **trafic dérivé** (montants et durées volontairement décalés → drift), afin que vous puissiez déclencher vos alertes en démonstration.
- **Pour le bonus** : le jeu **Give Me Some Credit** (Kaggle, ~150 000 lignes) pour éprouver la détection de drift sur un volume plus réaliste. https://www.kaggle.com/c/GiveMeSomeCredit/data

Ce brief est un épisode de la vie technique de Solvia, mais il est réalisable de façon **autonome** : le kit de démarrage contient le modèle, l'API de départ et le générateur de trafic. Aucun livrable d'un brief précédent n'est nécessaire.

### Contraintes techniques

- Toute l'infrastructure d'observation tourne **en local via Docker Compose** : API, Prometheus, Grafana, Alertmanager. Aucun cloud payant n'est requis pour le socle.
- La chaîne CI/CD s'exécute sur **GitHub Actions** ; l'image est publiée sur **GitHub Container Registry (ghcr.io)** ou Docker Hub.
- Le modèle et l'API de départ **ne sont pas à réécrire de zéro** : vous les *industrialisez* (tests, métriques, packaging). Vous devez cependant savoir expliquer leur fonctionnement.
- **Prérequis machine** : Docker et Docker Compose installés, environ 4 Go de RAM libres. Vérifiez ce point dès la première heure et signalez tout blocage au formateur.
- Tout le code est **versionné sur GitHub dès le premier jour** ; aucun secret (token de registre) ne doit apparaître en clair dans le dépôt.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Automatiser les tests d'une API de modèle** : définir des cas de test unitaires et d'intégration sur les routes et sur le comportement du modèle (schéma de sortie, valeurs limites, gestion des erreurs), mesurer la **couverture** et faire échouer la chaîne sous un seuil.
- **Construire une chaîne de livraison continue** : orchestrer sur GitHub Actions les étapes de validation, de test, de construction de l'image Docker et de publication sur un registre, en gérant les secrets et le déclenchement.
- **Déployer l'API de façon reproductible** : packager l'API dans une image, la démarrer via Docker Compose et documenter une procédure de déploiement rejouable.
- **Instrumenter et surveiller un modèle en production** : exposer des métriques applicatives et métier (latence, taux d'erreur, volume de prédictions, indicateur de drift), les collecter avec Prometheus, les visualiser dans un tableau de bord Grafana et **alerter** sur des seuils, dans une logique de *feedback loop* MLOps.

## Architecture cible

Le pattern attendu enchaîne une **voie d'intégration/livraison** (à gauche) et une **voie d'observation en production** (à droite). Un `push` sur le dépôt déclenche la CI (tests + couverture) ; si elle passe, l'image est construite et publiée ; l'API déployée expose un endpoint de métriques que **Prometheus** scrute périodiquement ; **Grafana** lit Prometheus pour les tableaux de bord ; **Alertmanager** déclenche les notifications quand une règle est violée.

Vous produirez votre **propre schéma d'architecture au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu, distinguant clairement la chaîne CI/CD et la chaîne de monitoring.

```
      DÉVELOPPEUR                         CHAÎNE CI/CD (GitHub Actions)
      git push  ───────────────►  +-------------------------------------------+
                                   |  1. lint + tests (pytest)                 |
                                   |  2. couverture (coverage, seuil minimal)  |
                                   |  3. build image Docker                    |
                                   |  4. push vers registre (ghcr.io)          |
                                   +----------------------+--------------------+
                                                          |
                                                   (image publiée)
                                                          |
      CHAÎNE D'OBSERVATION (Docker Compose, local)        v
      +---------------------------------------------------------------+
      |   API FastAPI (modèle scoring)                                |
      |   route /predict    +    route /metrics (format Prometheus)   |
      +----------------------------+----------------------------------+
                                   | (scrape périodique)
      +----------------------------v----------------------------------+
      |   PROMETHEUS  (stockage séries temporelles + règles d'alerte) |
      +------------------+---------------------------+----------------+
                         | (datasource)              | (alertes)
      +------------------v-----------+   +-----------v----------------+
      |  GRAFANA                     |   |  ALERTMANAGER              |
      |  latence / erreurs / drift   |   |  notification (mail/Slack) |
      +------------------------------+   +----------------------------+

      GÉNÉRATEUR DE TRAFIC (fourni) ──► /predict
      trafic nominal | dégradé (erreurs) | dérivé (drift)
```

> Votre schéma d'architecture au format image distinguera nettement la **voie CI/CD** (du `push` à la publication de l'image) et la **voie monitoring** (de l'API instrumentée à l'alerte).

## Données et code fournis

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `model/` — le **modèle scikit-learn sérialisé** entraîné sur German Credit et le script qui l'a produit (pour compréhension, pas à ré-exécuter) ;
- `app/` — l'**API FastAPI de départ** exposant `POST /predict` : volontairement peu testée et non instrumentée ;
- `traffic_generator.py` — le **générateur de trafic** (modes nominal / dégradé / dérivé). Vous le **configurez** et le branchez sur votre API : il n'est pas à réécrire, mais vous devez savoir l'expliquer.

> **Important** : le kit ne fournit **pas** de `Dockerfile`, ni de `docker-compose.yml`, ni de *workflow* GitHub Actions, ni de configuration Prometheus/Grafana/Alertmanager. C'est **à vous de les construire et de les adapter** à partir des ressources officielles listées en fin de brief. La procédure de déploiement qui en découle doit être documentée et rejouable.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient sa propre chaîne. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et conception (J1)

Aucune ligne de code de pipeline. Clonez le kit, lisez sa documentation, lancez l'API de départ localement et appelez `POST /predict` à la main pour comprendre ce qu'elle attend et ce qu'elle renvoie. Documentez le **contrat de l'API** (champs d'entrée, types, valeurs attendues, format de sortie) et repérez ses fragilités : que se passe-t-il si un champ manque ? si le montant est négatif ? si le corps de requête est vide ?

C'est aussi le moment de trancher des questions structurantes que vous justifierez par la question centrale :

- Quels **cas de test** garantiraient qu'une régression comme celle du mois dernier serait attrapée avant la mise en ligne ? Quel **seuil de couverture** est raisonnable pour ce projet, et pourquoi ?
- Quelles **métriques** faut-il exposer pour répondre à « l'API est-elle en bonne santé ? » — quelles sont applicatives (latence, taux d'erreur, débit) et quelles sont **métier** (volume de scores « mauvais payeur », indicateur de dérive des entrées) ?
- Comment mesurer un **drift** sans réentraîner : quelle distribution de référence, quelle statistique de comparaison (par exemple PSI — *Population Stability Index* — ou un test de distance sur une variable clé comme le montant) ?
- Sur quels **seuils** déclencher une alerte, et à qui doit-elle parvenir ?

Posez tout cela sur un **schéma d'architecture** (image, pas d'ASCII) séparant CI/CD et monitoring, puis formalisez votre plan dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** schéma d'architecture, contrat d'API documenté, liste des métriques et seuils, et Kanban présentés en 5 minutes au formateur.

### Phase 2 — Tests automatisés et couverture (J2)

Écrivez la **suite de tests** de l'API avec pytest. Visez au minimum : un test qui vérifie que `/predict` renvoie un score bien formé sur une requête valide ; des tests sur les **cas d'erreur** (champ manquant, type invalide, corps vide) ; et au moins un test qui « verrouille » le comportement du modèle sur un exemple connu (une entrée de référence doit toujours produire la même classe). Mesurez la **couverture** avec `coverage`/`pytest-cov` et fixez un **seuil minimal** en dessous duquel la suite échoue.

- Vos tests auraient-ils attrapé la régression du mois dernier (score erroné) ? Ajoutez-en un qui le prouve.
- Un test doit-il charger le vrai modèle ou un modèle factice ? Justifiez votre choix (rapidité, fidélité).

**Résultat testable en fin de J2 :** `pytest` passe en local avec un rapport de couverture, et la suite **échoue volontairement** si l'on baisse le score de couverture ou si l'on casse le contrat de sortie.

### Phase 3 — Chaîne CI/CD et publication de l'image (J2-J3)

Écrivez le **Dockerfile** de l'API, puis construisez le *workflow* **GitHub Actions**. À chaque `push` (et sur les *pull requests*), la chaîne doit : installer les dépendances, lancer la **suite de tests avec couverture**, et — seulement si les tests passent — **construire l'image Docker** et la **publier** sur ghcr.io (ou Docker Hub). Le token du registre doit passer par les **secrets GitHub**, jamais par le code.

- Que doit-il se passer si un test échoue : l'image est-elle quand même publiée ? (Non — démontrez que la publication est conditionnée à la réussite des tests.)
- Comment **taguez**-vous vos images (SHA de commit, `latest`, version) et pourquoi ?
- La construction fonctionne-t-elle **depuis un clone propre**, sans dépendre de votre poste ?

**Résultat testable en fin de J3 :** un commit qui casse un test **bloque** la publication (workflow rouge) ; un commit sain produit une image **publiée et récupérable** depuis le registre.

### Phase 4 — Déploiement et instrumentation observable (J3-J4)

Déployez l'API (image construite en Phase 3) via **Docker Compose**, aux côtés de **Prometheus**, **Grafana** et **Alertmanager**. Instrumentez l'API pour qu'elle expose une route **`/metrics`** au format Prometheus, comptabilisant au minimum : la **latence** des prédictions, le **nombre de requêtes** ventilé par code de statut (donc le **taux d'erreur**), le **volume de prédictions**, et un **indicateur de drift** calculé sur les entrées (par exemple un PSI sur le montant, rafraîchi par lots).

Configurez Prometheus pour *scraper* l'API, construisez un **tableau de bord Grafana** répondant à la question centrale (latence, taux d'erreur, drift au fil du temps), puis définissez des **règles d'alerte** acheminées par Alertmanager (par exemple : taux d'erreur > seuil sur 5 min, latence p95 au-dessus d'un seuil, PSI franchissant le seuil de drift).

- Que montre votre tableau de bord quand vous lancez le **trafic dégradé** du générateur ? le **trafic dérivé** ?
- Une alerte qui se déclenche puis se résout doit-elle **spammer** l'équipe ? Comment évitez-vous le bruit (durée `for`, regroupement) ?
- Le calcul du drift respecte-t-il la **minimisation des données personnelles** — n'agrège-t-il que ce qui est nécessaire ?

**Résultat testable en fin de J4 :** en lançant le générateur en mode dégradé puis dérivé, le tableau de bord réagit **en direct** et **au moins deux alertes distinctes** (une erreur/latence, une de drift) se déclenchent et sont visibles dans Alertmanager.

### Phase 5 — Consolidation, documentation et démo (J5)

Finalisez le README (description, technologies, installation et lancement, architecture, procédure de déploiement, auteur), vérifiez que **toute la stack se relance de zéro** en suivant uniquement votre documentation, mettez à jour le schéma d'architecture et le Kanban, puis répétez votre démonstration : ordre des étapes (push → CI → image → stack → trafic → alerte), et plan B si un composant refuse de démarrer le jour J.

### Socle commun (obligatoire)

- **Suite de tests** pytest couvrant routes valides, cas d'erreur et comportement du modèle, avec **couverture mesurée et seuil bloquant**.
- **Workflow GitHub Actions** : tests + couverture, puis **build & push** d'image conditionnés à la réussite des tests, secrets gérés proprement.
- Image **publiée** sur un registre et **déployable** via Docker Compose.
- API **instrumentée** exposant `/metrics` : latence, taux d'erreur, volume, **indicateur de drift**.
- **Prometheus** qui scrute l'API, **tableau de bord Grafana** (latence, erreurs, drift) et **au moins deux règles d'alerte** acheminées par Alertmanager.
- Repo public documenté avec schéma d'architecture (image) et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Ajouter un **badge de couverture** et publier le rapport de couverture comme *artifact* de la CI.
- Mettre en place un **environnement de *staging*** et une promotion manuelle vers la « production » (approbation dans GitHub).
- Éprouver la détection de drift sur le volume réel de **Give Me Some Credit** (Kaggle).
- Router les alertes vers **Slack** ou un e-mail réel, avec des messages contextualisés (quelle métrique, quelle valeur, quel seuil).
- Ajouter une **route de *health check*** et une sonde de disponibilité, et distinguer *liveness* et *readiness*.
- Ajouter un **run book** décrivant, pour chaque alerte, la marche à suivre pour diagnostiquer et corriger.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un **README structuré** : description du projet et de la question métier, technologies, instructions d'installation et de lancement pas à pas (prérequis Docker et RAM inclus), architecture (schéma intégré au README), procédure de déploiement, auteur.
- Le **fichier de workflow GitHub Actions** (`.github/workflows/…`) réalisant tests, couverture, build et push de l'image, avec gestion des secrets.
- Le **Dockerfile** de l'API et le **`docker-compose.yml`** orchestrant API + Prometheus + Grafana + Alertmanager.
- Les **tests** (`tests/`) et la configuration de couverture, avec le seuil bloquant documenté.
- Le **code d'instrumentation** de l'API (route `/metrics`, métriques latence/erreurs/volume/drift) et l'explication du **calcul de drift** (référence, statistique, seuil).
- Les **fichiers de configuration** Prometheus (`prometheus.yml`, règles d'alerte), Grafana (export JSON du tableau de bord) et Alertmanager.
- Le **schéma d'architecture au format image** (PNG ou export draw.io) distinguant voie CI/CD et voie monitoring. Pas de schéma ASCII.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture d'écran ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous poussez un commit et montrez la **CI qui teste, mesure la couverture, construit et publie l'image** ; vous prouvez qu'un test cassé **bloque** la publication ; vous démarrez la stack de monitoring, lancez le **générateur de trafic** (dégradé puis dérivé) et montrez le **tableau de bord Grafana** réagir et **au moins deux alertes** se déclencher. Les questions portent sur vos choix : cas de test et seuil de couverture, tagging d'images et gestion des secrets, métriques retenues, méthode et seuil de drift, conception des alertes (bruit, durée, routage).
- **Revue de code et d'architecture — 30 %** : examen du repo GitHub public (structure, lisibilité, qualité des tests, absence de secrets en clair, qualité du README), du workflow CI/CD (clarté, conditionnement des étapes), des configurations Prometheus/Grafana/Alertmanager et du schéma d'architecture (distinction CI/CD vs monitoring, formalisme lisible).

> **Validation partielle** : une chaîne qui ne fonctionne pas intégralement en démonstration mais dont le code est structuré, versionné et documenté peut valider partiellement les capacités concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de documentation ne valide pas les critères documentaires.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Automatisation des tests de l'API

- La suite de tests couvre au moins une route valide, plusieurs cas d'erreur et un test « verrou » sur le comportement du modèle. — OUI / NON
- La **couverture** est mesurée et un **seuil minimal bloquant** est configuré (la suite échoue en dessous). — OUI / NON
- Un test démontre qu'une régression du contrat de sortie est détectée avant la mise en ligne. — OUI / NON
- L'exécution des tests est reproductible depuis un clone propre (dépendances déclarées). — OUI / NON

### Chaîne de livraison continue

- Le workflow GitHub Actions se déclenche sur `push`/PR et exécute tests + couverture. — OUI / NON
- La **construction** et la **publication** de l'image sont **conditionnées à la réussite des tests** (un test cassé bloque la publication). — OUI / NON
- L'image est effectivement publiée sur un registre et récupérable ; le tagging est explicite et justifié. — OUI / NON
- Les secrets (token de registre) sont gérés via les secrets GitHub et **n'apparaissent pas** dans le dépôt. — OUI / NON

### Déploiement reproductible

- L'API est packagée dans une image et démarre via Docker Compose aux côtés de la stack de monitoring. — OUI / NON
- La procédure de déploiement du README se déroule sans erreur sur une machine propre. — OUI / NON
- La documentation couvre la configuration (ports, volumes, variables d'environnement, prérequis). — OUI / NON

### Instrumentation et surveillance du modèle

- L'API expose une route `/metrics` au format Prometheus (latence, requêtes par statut / taux d'erreur, volume). — OUI / NON
- Un **indicateur de drift** est calculé sur les entrées, avec référence, statistique et seuil documentés, dans le respect de la minimisation des données personnelles. — OUI / NON
- Prometheus scrute l'API et le **tableau de bord Grafana** affiche latence, taux d'erreur et drift dans le temps. — OUI / NON
- **Au moins deux règles d'alerte distinctes** (erreur/latence et drift) se déclenchent via Alertmanager et sont conçues pour limiter le bruit (durée, regroupement). — OUI / NON

## Ressources

- [Cours FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/)
- [Qualité & tests Python](../../../01-Fondamentaux/Python/05-Qualite-Tests/)
- [Cours Docker](../../../02-Containerisation/Docker/)
- [CI/CD & GitHub Actions](../../../07-DevOps/01-CI-CD/03-GitHub-Actions/)
- [Monitoring Prometheus/Grafana](../../../07-DevOps/02-Monitoring/)
- [MLOps — Monitoring de modèle (drift)](../../../08-Machine-Learning/MLOps/06-Monitoring-Modele/)
- Documentation GitHub Actions (workflows, secrets, jobs conditionnels) : https://docs.github.com/actions
- Publier une image sur GitHub Container Registry : https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- pytest (framework de tests) : https://docs.pytest.org/
- Coverage.py / pytest-cov (mesure de couverture) : https://coverage.readthedocs.io/
- Client Prometheus pour Python (exposition de métriques) : https://prometheus.github.io/client_python/
- Documentation Prometheus (scrape, règles d'alerte) : https://prometheus.io/docs/introduction/overview/
- Documentation Grafana (tableaux de bord, datasource Prometheus) : https://grafana.com/docs/grafana/latest/
- Prometheus Alertmanager (routage et regroupement des alertes) : https://prometheus.io/docs/alerting/latest/alertmanager/
- German Credit Data (UCI) : https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- Give Me Some Credit (Kaggle, bonus) : https://www.kaggle.com/c/GiveMeSomeCredit/data
- Population Stability Index (PSI) — principe de mesure de drift : https://en.wikipedia.org/wiki/Population_stability_index
