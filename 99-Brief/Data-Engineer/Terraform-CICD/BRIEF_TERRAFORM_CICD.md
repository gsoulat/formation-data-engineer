# Brief : Provisionner l'infrastructure data de Vélocité dans le cloud avec Terraform et automatiser le déploiement en CI/CD

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Terraform (HCL), un cloud provider au choix (Google Cloud, AWS ou Azure), backend distant pour l'état Terraform, GitHub & GitHub Actions, Git, un peu de SQL |
| **Prérequis** | [Cours Git](../../../01-Fondamentaux/Git/) + [Cours GitHub](../../../01-Fondamentaux/Github/) + [Cours Terraform](../../../03-Infrastructure-as-Code/Terraform/) + [Cours CI/CD](../../../07-DevOps/01-CI-CD/) + [Cours SQL](../../../01-Fondamentaux/SQL/) |

## Contexte

### L'entreprise

**Vélocité** est une scale-up française fondée à Nantes en 2018. Elle édite une plateforme de micromobilité (vélos et trottinettes en libre-service) déployée dans une douzaine de villes moyennes. Ses 90 salariés exploitent chaque jour des millions de points GPS, de trajets et d'états de batterie remontés par la flotte. L'équipe data compte trois personnes : un lead data engineer, une data analyst et vous, data engineer, recruté il y a deux mois.

### Le problème

L'infrastructure data de Vélocité a grandi « à la main ». Le premier bucket de stockage, la base de données analytique, les comptes de service : tout a été cliqué dans la console web du cloud, au fil des urgences, sans trace écrite. Personne ne sait exactement quelles ressources existent, dans quelle région, avec quels droits. Quand la data analyst a demandé un environnement de test isolé pour préparer la refonte du reporting, il a fallu trois jours et deux tickets au support cloud pour le reconstituer — imparfaitement.

La semaine dernière, l'incident a fait déclencher le sujet en réunion : un stagiaire a supprimé par erreur un bucket de logs en pensant faire le ménage. Aucune sauvegarde de la configuration, aucun moyen de le recréer à l'identique. Le lead data engineer a posé la règle du jour : **plus aucune ressource cloud ne sera créée à la main**. Toute l'infrastructure data doit devenir du **code**, versionnée, revue en pull request, et déployée automatiquement. C'est votre mission de la semaine : poser les fondations de cette approche « Infrastructure as Code » sur un périmètre volontairement restreint mais réaliste — un **bucket de stockage** et une **base de données managée** — et bâtir la chaîne d'intégration continue qui les déploie.

### La question centrale

Le lead data engineer résume l'objectif en une phrase, qui devient la question centrale du projet. Chaque choix de la semaine devra pouvoir être justifié par sa contribution à cette question :

> **« Si tout notre cloud disparaissait ce soir, pourrions-nous le reconstruire à l'identique demain matin, sans cliquer une seule fois ? »**

### Les sources de données

Ce projet porte sur l'**infrastructure** qui accueillera les données, pas sur un pipeline de transformation. Vous n'avez donc pas de gros dataset à traiter, mais vous devez prouver que l'infrastructure provisionnée est **réellement exploitable** en y déposant un jeu de données public et en y créant une table dans la base managée :

- **Vélib' – Comptage temps réel des stations** (Open Data Ville de Paris / Smovengo), un export CSV/JSON de disponibilité de vélos en libre-service, cohérent avec le métier de Vélocité : https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/ — vous en téléverserez un extrait dans votre bucket comme donnée de démonstration.
- **En alternative ou en complément**, tout jeu de données ouvert de mobilité de [data.gouv.fr](https://www.data.gouv.fr/) (par exemple des comptages de trafic urbain) fait l'affaire : l'important est de manipuler un fichier réel, léger (quelques Mo), déposé dans le stockage cloud provisionné.

L'objectif n'est pas d'analyser ces données, mais de **démontrer que le bucket accepte un fichier et que la base managée accepte une table** — c'est-à-dire que l'infrastructure décrite en code fonctionne pour de vrai.

### Contraintes techniques

- **Aucune ressource n'est créée à la main dans la console cloud.** Toute ressource visible dans votre projet cloud doit correspondre à une ligne de code Terraform. C'est le critère non négociable du brief : une ressource « cliquée » invalide la démarche.
- Choisissez **un seul cloud provider** parmi Google Cloud (recommandé : offre d'essai généreuse et compatible avec le [cours GCP](../../../04-Cloud-Platforms/GCP/)), AWS ou Azure. Restez dans l'**offre gratuite / niveau d'essai** : instances de plus petite taille, une seule région, ressources détruites en fin de semaine.
- L'**état Terraform** ne doit pas rester sur votre poste : configurez un **backend distant** (bucket dédié ou équivalent) afin que l'état soit partageable et versionné.
- Les **secrets** (clé de service cloud, mot de passe de la base) ne doivent **jamais** apparaître dans le dépôt : ni en clair, ni dans l'état commité, ni dans les logs de CI. Utilisez les variables d'environnement et les *secrets* GitHub Actions.
- **Prérequis compte** : ouvrez dès la première heure un compte cloud avec l'offre d'essai (carte bancaire souvent demandée pour vérification, mais périmètre gratuit respecté) et vérifiez que vous pouvez vous authentifier en ligne de commande. Signalez tout blocage administratif au formateur immédiatement.
- Tout le code est **versionné sur GitHub dès le premier jour** ; l'infrastructure évolue **uniquement par pull request**.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Concevoir un cadre technique d'infrastructure data cloud** : choisir un provider et des services managés adaptés au besoin, définir l'architecture cible (stockage objet + base managée + backend d'état), et justifier vos choix au regard du coût, de la région et de la sécurité.
- **Décrire une infrastructure sous forme de code reproductible** : modéliser en HCL un bucket de stockage et une base de données managée avec des variables, des sorties et une gestion propre de l'état distant, sans configuration manuelle.
- **Créer et exploiter une base de données managée** : paramétrer le moteur, les accès et le réseau via le code, puis prouver que la base est fonctionnelle en y créant une table et en y déposant une donnée réelle.
- **Automatiser et fiabiliser le déploiement** : construire une chaîne GitHub Actions qui enchaîne formatage, validation, `plan` sur les pull requests et `apply` contrôlé, en protégeant les secrets et en garantissant que l'infrastructure reste conforme au code.

## Architecture cible

Le pattern attendu est une **infrastructure décrite intégralement en code** et déployée par une **chaîne d'intégration continue**. Du code Terraform versionné sur GitHub décrit trois briques : un **bucket de stockage objet**, une **base de données managée**, et un **backend distant** qui héberge l'état Terraform. À chaque *pull request*, GitHub Actions vérifie le formatage, valide la syntaxe et produit un `plan` que le relecteur examine avant fusion ; à la fusion sur la branche principale, un `apply` contrôlé applique les changements au cloud. Aucune ressource n'existe en dehors de ce code.

```
        DÉVELOPPEUR (vous)
              |
        commit + pull request
              |
   +----------v-----------------------------------------------+
   |                   GitHub (dépôt public)                  |
   |   code Terraform (HCL) : bucket, base managée, backend   |
   +----------+-----------------------------------------------+
              |
     déclenche GitHub Actions
              |
   +----------v-----------------------------------------------+
   |                  PIPELINE CI/CD (Actions)                |
   |  sur PR    : fmt  ->  validate  ->  plan  (commenté)     |
   |  sur main  : fmt  ->  validate  ->  apply (contrôlé)     |
   |  secrets injectés (clé cloud, mdp base) — jamais en clair|
   +----------+-----------------------------------------------+
              |
       terraform apply
              |
   +----------v-----------------------------------------------+
   |                     CLOUD PROVIDER                       |
   |   +-------------------+     +-------------------------+   |
   |   | BUCKET STOCKAGE   |     | BASE DE DONNÉES MANAGÉE |   |
   |   | (extrait dataset) |     | (table + donnée démo)   |   |
   |   +-------------------+     +-------------------------+   |
   |   +--------------------------------------------------+   |
   |   | BACKEND DISTANT : état Terraform versionné       |   |
   |   +--------------------------------------------------+   |
   +----------------------------------------------------------+
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu, faisant apparaître le dépôt, la chaîne CI/CD, les ressources cloud provisionnées et l'emplacement de l'état.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient sa propre infrastructure. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et conception (J1)

Aucune ligne de code d'infrastructure. Ouvrez votre compte cloud sur l'offre d'essai, vérifiez que vous pouvez vous authentifier en ligne de commande, et **cartographiez votre cible** avant de coder quoi que ce soit.

Commencez par les décisions structurantes. Quel **provider** choisissez-vous, et pourquoi (offre gratuite, région européenne, services managés disponibles) ? Quel **service de stockage objet** et quel **moteur de base managée** répondent au besoin de Vélocité sans exploser le budget d'essai ? Dans quelle **région** provisionnez-vous, et quel impact cela a-t-il sur la latence, la conformité et le coût ?

Réfléchissez ensuite à l'**état Terraform** : pourquoi est-il dangereux de le laisser sur votre poste, et où le stockerez-vous pour qu'il soit partageable ? Un détail vous attend ici : le bucket qui héberge l'état ne peut pas être créé par le même code qui l'utilise comme backend — comment résolvez-vous ce problème de l'œuf et de la poule ?

Posez tout cela sur un **schéma d'architecture** (image, pas d'ASCII) : dépôt, chaîne CI/CD, ressources cloud, emplacement de l'état. Listez les **secrets** que la chaîne aura besoin de manipuler et où ils vivront. Formalisez votre plan dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** schéma d'architecture, choix de provider et de services justifiés, liste des secrets et Kanban présentés en 5 minutes au formateur — sans avoir provisionné la moindre ressource.

### Phase 2 — Premier code Terraform et backend distant (J2)

Initialisez votre projet Terraform. Déclarez le **provider** choisi, mettez en place l'**authentification** en ligne de commande (jamais de clé en clair dans le code), puis provisionnez votre **première ressource** : le bucket de stockage. Faites tourner le cycle `init` → `plan` → `apply` et vérifiez dans la console cloud que le bucket existe bien — sans y avoir cliqué.

Basculez ensuite l'état sur un **backend distant**. C'est ici que se joue la reproductibilité :

- Où réside l'état après cette bascule, et pourquoi est-ce plus sûr que sur votre disque ?
- Si vous détruisez tout votre code local et le reclonez sur une machine neuve, un `terraform plan` doit annoncer **« aucun changement »**. Est-ce le cas ?
- Que contient exactement le fichier d'état, et pourquoi ne doit-il **jamais** être commité dans le dépôt ?

Structurez votre code proprement dès maintenant : séparez les **variables**, les **sorties** et la configuration du provider dans des fichiers dédiés, et prévoyez un fichier d'exemple de variables (sans secret) pour que quelqu'un d'autre puisse reprendre le projet.

**Résultat testable en fin de J2 :** le bucket est provisionné par le code, l'état vit dans un backend distant, et un `plan` sur une copie fraîche du dépôt n'annonce aucun changement.

### Phase 3 — Base de données managée et preuve d'exploitation (J3)

Ajoutez la **base de données managée** à votre code Terraform : moteur, taille d'instance (la plus petite de l'offre d'essai), région, et surtout les **accès**. Le mot de passe de la base ne doit **pas** être écrit en clair : injectez-le par variable, et réfléchissez à qui peut se connecter à la base et depuis où.

- Comment le **mot de passe** de la base transite-t-il sans jamais apparaître dans le code ni dans l'état commité ?
- Quelles **règles réseau** ouvrez-vous, et quel est le risque d'ouvrir la base à tout Internet ?
- Les **sorties** Terraform exposent-elles ce qu'il faut pour se connecter (hôte, port) sans divulguer de secret ?

Prouvez ensuite que l'infrastructure **fonctionne pour de vrai** : connectez-vous à la base, créez une **table**, et téléversez un **extrait du dataset public** (Vélib' ou équivalent) dans votre bucket. Documentez la procédure de ce test d'exploitation.

**Résultat testable en fin de J3 :** la base managée est provisionnée par le code, une table y est créée, un fichier de données réel est déposé dans le bucket, et rien de tout cela n'a été fait à la main dans la console.

### Phase 4 — Chaîne CI/CD GitHub Actions (J4)

Automatisez le déploiement. Construisez un **workflow GitHub Actions** qui, sur chaque **pull request**, enchaîne le **formatage** (`fmt`), la **validation** (`validate`) et un **`plan`** dont le résultat est visible pour le relecteur ; et qui, sur la **branche principale**, applique les changements de façon **contrôlée** (`apply`). Les identifiants cloud et le mot de passe de la base sont injectés via les **secrets GitHub Actions**, jamais écrits dans le dépôt.

- Que se passe-t-il si le code n'est **pas formaté** ou ne **valide pas** — la chaîne bloque-t-elle la fusion ?
- Le `plan` produit sur une PR est-il **lisible** par le relecteur pour qu'il décide en connaissance de cause ?
- L'`apply` automatique est-il **sécurisé** : ne se déclenche-t-il que sur la branche principale, après revue ? Faut-il une **approbation manuelle** avant d'appliquer ?
- Un secret peut-il **fuiter** dans les logs de la chaîne ? Comment le vérifiez-vous ?

Ouvrez une vraie pull request qui modifie l'infrastructure (par exemple une variable, un tag, une option du bucket) et montrez le cycle complet : PR → `plan` en commentaire → revue → fusion → `apply` → ressource modifiée dans le cloud.

**Résultat testable en fin de J4 :** une pull request déclenche `fmt`/`validate`/`plan`, la fusion déclenche un `apply` contrôlé, et aucun secret n'apparaît en clair dans le dépôt ni dans les logs.

### Phase 5 — Consolidation, destruction propre et démo (J5)

Finalisez le README (description, technologies, prérequis compte cloud, procédure d'installation et d'authentification, architecture, auteur). Vérifiez qu'un tiers pourrait **reprendre votre dépôt de zéro** : cloner, configurer ses secrets, lancer la chaîne, obtenir la même infrastructure.

Démontrez enfin la promesse du projet : un **`terraform destroy`** propre détruit toutes les ressources (utile pour ne pas laisser filer le budget), puis un **`apply`** les recrée à l'identique. C'est la preuve tangible que « si tout disparaissait ce soir, on reconstruirait demain matin ». Mettez à jour le schéma et le Kanban, puis répétez votre démonstration : ordre des commandes, plan B si une ressource refuse de se créer le jour J.

### Socle commun (obligatoire)

- Un **bucket de stockage** et une **base de données managée** entièrement décrits en **code Terraform** — aucune ressource créée à la main.
- L'**état Terraform** stocké dans un **backend distant**, jamais commité.
- Code structuré : **variables**, **sorties**, fichier d'exemple de variables **sans secret**.
- Preuve d'exploitation : une **table** créée dans la base et un **fichier de données réel** déposé dans le bucket.
- Une **chaîne GitHub Actions** : `fmt` + `validate` + `plan` sur les PR, `apply` contrôlé sur la branche principale.
- **Aucun secret** en clair dans le dépôt (clé cloud et mot de passe de base gérés par variables et secrets Actions).
- Une **pull request** de démonstration montrant le cycle complet plan → revue → apply.
- Cycle **`destroy` puis `apply`** rejouable, prouvant la reproductibilité.
- Repo public documenté avec schéma d'architecture et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Factoriser votre code en **modules Terraform** réutilisables (un module « stockage », un module « base »).
- Gérer **plusieurs environnements** (par exemple `dev` et `prod`) via des workspaces ou des dossiers séparés, avec des états distincts.
- Ajouter à la chaîne un **scan de sécurité** de l'infrastructure (par exemple `tflint`, `checkov` ou `tfsec`) qui bloque en cas de mauvaise configuration.
- Exiger une **approbation manuelle** (environnement protégé GitHub) avant tout `apply` en production.
- Détecter la **dérive de configuration** : un job planifié qui lance un `plan` régulier et alerte si le cloud a été modifié en dehors du code.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du code Terraform et des workflows, avec un **README** structuré : description du projet et de la question métier, technologies utilisées, prérequis (compte cloud, offre d'essai), instructions d'installation et d'authentification pas à pas, procédure de déploiement, architecture (schéma intégré au README), auteur.
- Le **code Terraform** organisé : configuration du provider, déclaration du bucket, de la base managée et du backend distant, fichiers de **variables** et de **sorties** séparés, fichier d'exemple de variables **sans secret**.
- Le ou les **workflows GitHub Actions** (`.github/workflows/`) réalisant `fmt`, `validate`, `plan` sur les PR et `apply` contrôlé sur la branche principale.
- La **preuve d'exploitation** : script ou procédure documentée de création de la table et de dépôt du fichier de données réel dans le bucket, avec captures d'écran ou logs.
- Le **schéma d'architecture au format image** (PNG ou export draw.io) : dépôt, chaîne CI/CD, ressources cloud, emplacement de l'état. Pas de schéma ASCII.
- Une **pull request** (ouverte puis fusionnée) illustrant le cycle complet plan → revue → apply, avec le `plan` visible dans la PR.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique de progression.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous partez d'un dépôt propre, montrez l'authentification cloud, lancez le cycle Terraform (ou une chaîne CI/CD) qui provisionne bucket et base, prouvez dans la console que les ressources correspondent au code, créez la table et déposez le fichier de données, puis déclenchez le **cycle `destroy`/`apply`** qui prouve la reproductibilité. Les questions portent sur les choix de conception : provider et services, gestion de l'état distant, protection des secrets, comportement de la chaîne sur une PR, sécurisation de l'`apply`.
- **Revue de code et d'architecture — 30 %** : examen du repo GitHub public (structure du code Terraform, séparation variables/sorties, absence de secret, lisibilité, qualité du README), du ou des workflows GitHub Actions, du schéma d'architecture et de la pull request de démonstration.

> **Validation partielle** : une infrastructure qui ne se déploie pas entièrement en démonstration mais dont le code est structuré, versionné, documenté et exempt de secret peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo contient des ressources créées à la main ou des secrets en clair ne valide pas les critères correspondants.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Conception du cadre technique d'infrastructure

- Le schéma d'architecture fait apparaître clairement le dépôt, la chaîne CI/CD, les ressources cloud provisionnées et l'emplacement de l'état, avec un formalisme lisible.
- Le choix du provider et des services managés (stockage, base) est justifié au regard du coût, de la région et de la sécurité.
- L'emplacement et le rôle du backend distant de l'état sont expliqués et argumentés.
- La liste des secrets manipulés par la chaîne et leur mode de protection sont documentés.

### Description de l'infrastructure en code

- Le bucket de stockage et la base managée sont **intégralement** décrits en code Terraform : aucune ressource n'existe dans le cloud sans ligne de code correspondante.
- L'état Terraform est stocké dans un backend distant et n'est jamais commité dans le dépôt.
- Le code est structuré : variables, sorties et configuration du provider sont séparés, avec un fichier d'exemple de variables sans secret.
- Sur une copie fraîche du dépôt, un `plan` n'annonce aucun changement (l'infrastructure est conforme au code).

### Création et exploitation de la base de données managée

- La base managée est provisionnée par le code avec un moteur, une taille et une région explicites et cohérents avec l'offre d'essai.
- Le mot de passe de la base et les accès réseau sont paramétrés sans qu'aucun secret n'apparaisse en clair dans le code ou l'état.
- Une table est créée dans la base et un fichier de données réel est déposé dans le bucket, prouvant que l'infrastructure est exploitable.
- La procédure de test d'exploitation (connexion, création de table, dépôt du fichier) est documentée et rejouable.

### Automatisation et fiabilisation du déploiement

- La chaîne GitHub Actions exécute `fmt` et `validate` et bloque la fusion si le code n'est pas conforme.
- Un `plan` est produit et lisible sur chaque pull request avant fusion.
- L'`apply` ne se déclenche que sur la branche principale, de façon contrôlée, et une pull request de démonstration illustre le cycle complet plan → revue → apply.
- Aucun secret n'apparaît en clair dans le dépôt ni dans les logs de la chaîne (identifiants injectés par les secrets Actions).

## Ressources

- [Cours Git](../../../01-Fondamentaux/Git/)
- [Cours GitHub](../../../01-Fondamentaux/Github/)
- [Cours Terraform](../../../03-Infrastructure-as-Code/Terraform/)
- [Cours CI/CD](../../../07-DevOps/01-CI-CD/)
- [Cours GCP](../../../04-Cloud-Platforms/GCP/)
- [Cours SQL](../../../01-Fondamentaux/SQL/)
- Documentation officielle Terraform (langage HCL, ressources, variables) : https://developer.hashicorp.com/terraform/language
- Terraform — configuration d'un backend distant pour l'état : https://developer.hashicorp.com/terraform/language/backend
- Terraform — bonnes pratiques de gestion de l'état et des secrets : https://developer.hashicorp.com/terraform/language/state
- Documentation GitHub Actions (workflows, jobs, déclencheurs) : https://docs.github.com/actions
- GitHub Actions — secrets chiffrés dans les workflows : https://docs.github.com/actions/security-guides/using-secrets-in-github-actions
- Provider Terraform Google Cloud (bucket, Cloud SQL) : https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Provider Terraform AWS (S3, RDS) : https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Provider Terraform Azure (Storage, Database) : https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
- Vélib' — disponibilité en temps réel (Open Data Ville de Paris) : https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/
- Portail data.gouv.fr (jeux de données de mobilité) : https://www.data.gouv.fr/
