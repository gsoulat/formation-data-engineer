# Brief : Automatiser la lecture des factures fournisseurs de Facturio avec un service d'IA cloud managé

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Service d'IA cloud managé (Azure AI Document Intelligence / Amazon Textract / Google Document AI, au choix), Python, FastAPI, Pydantic, Streamlit ou Gradio, Docker, Git |
| **Prérequis** | [Cours Python](../../../01-Fondamentaux/Python/) + [Cours FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/) + [Cours Services IA Cloud](../../../04-Cloud-Platforms/AI-Services/) + [Cours Streamlit](../../../12-Frontend-IA/02-Streamlit/) ou [Cours Gradio](../../../12-Frontend-IA/01-Gradio/) + [Cours Docker](../../../02-Containerisation/Docker/) |

## Contexte

### L'entreprise

**Facturio** est une scale-up française fondée en 2019 à Nantes. Elle édite un logiciel de gestion des notes de frais et des factures fournisseurs à destination des PME (comptables, offices managers, dirigeants). Ses 60 salariés servent aujourd'hui environ 1 200 entreprises clientes. Le produit historique repose sur une saisie **manuelle** : les clients photographient ou téléversent leurs factures, et une équipe d'opérateurs re-saisit à la main les champs clés (fournisseur, date, numéro de facture, montant HT, TVA, total TTC) avant de les injecter dans l'outil comptable.

Vous êtes développeur IA au sein de l'équipe produit, qui compte deux développeurs back-end, une product owner et un CTO sponsor du projet.

### Le problème

La saisie manuelle ne tient plus la charge. Avec la croissance, le volume de factures téléversées a triplé en dix-huit mois ; en période de clôture comptable, les délais de traitement explosent et des clients se plaignent. Recruter davantage d'opérateurs coûte cher et ne règle pas le problème de fond : la **re-saisie humaine** est lente, sujette aux erreurs, et n'apporte aucune valeur ajoutée.

Le CTO refuse d'entraîner un modèle de vision maison — trop long, trop coûteux, hors périmètre pour une équipe de cette taille. Il veut évaluer les **services d'extraction documentaire (OCR / Document Intelligence) déjà proposés par les grands fournisseurs cloud**, en choisir un sur des critères objectifs, et l'intégrer proprement dans le produit via une API interne, avec une interface de démonstration pour convaincre le comité de direction.

Attention : les factures contiennent des **données personnelles et d'entreprise** (noms, adresses, coordonnées bancaires parfois). Le choix du service et de sa région d'hébergement devra tenir compte du RGPD et de la souveraineté des données.

### La question centrale

Le CTO résume l'enjeu de la semaine en une phrase, qui devient la question centrale du projet. Chaque choix — service retenu, région, conception de l'API, contenu de l'interface — devra pouvoir être justifié par sa contribution à cette question :

> **« Peut-on faire lire nos factures par un service cloud sur étagère, de façon fiable, conforme et rentable, sans entraîner notre propre modèle ? »**

### Les sources de données

Aucune donnée client réelle n'est utilisée : vous travaillez sur des **jeux de factures publics**, ce qui est aussi une exigence RGPD (ne jamais tester une intégration sur des données personnelles réelles).

- **Jeu de factures « High-Quality Invoice Images for OCR »** (Kaggle) : images de factures synthétiques annotées, adaptées au test d'un service d'extraction — https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr
- **Jeu « FATURA / invoice datasets »** ou tout jeu de factures/reçus publics équivalent sur Kaggle (par exemple les datasets de reçus type SROIE) pour diversifier les mises en page — https://www.kaggle.com/datasets
- **Vos propres factures anonymisées ou fictives** : quelques PDF/photos que vous générez ou anonymisez vous-même pour tester des mises en page françaises (mentions TVA, SIRET, IBAN masqué).

Côté services, vous consommez les **offres réelles et leurs paliers gratuits** :

- **Azure AI Document Intelligence** (ex-Form Recognizer), modèle « Invoice » pré-entraîné, palier gratuit ~500 pages/mois — https://learn.microsoft.com/azure/ai-services/document-intelligence/
- **Amazon Textract** (`AnalyzeExpense` pour les factures/reçus), palier gratuit ~1 000 pages/mois la première année — https://docs.aws.amazon.com/textract/
- **Google Document AI** (processeur « Invoice Parser »), palier gratuit sur certains processeurs — https://cloud.google.com/document-ai/docs

Ce brief est un épisode de la vie produit de Facturio, mais il est réalisable de façon **autonome** : les jeux de factures sont publics et les paliers gratuits des services suffisent au périmètre demandé. Aucun livrable d'un brief précédent n'est nécessaire.

### Contraintes techniques

- **Deux services d'extraction documentaire minimum** doivent être évalués et comparés ; **un seul** est ensuite intégré de bout en bout.
- L'intégration se fait via une **API REST FastAPI** que vous concevez : elle reçoit une facture, appelle le service cloud, et renvoie les champs extraits en JSON structuré.
- Une **interface cliente Streamlit ou Gradio** consomme votre API : téléversement d'une facture, affichage des champs extraits, indication de confiance.
- Les **clés et secrets** (clés API, credentials cloud) ne doivent **jamais** être committés : variables d'environnement, fichier `.env` ignoré par Git, `.env.example` fourni.
- Vous travaillez avec les **paliers gratuits** ; surveillez votre consommation pour éviter toute facturation. Vérifiez ce point dès la première heure et signalez tout blocage d'accès cloud au formateur.
- Tout le code est **versionné sur GitHub dès le premier jour**.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Identifier et comparer des services d'IA cloud préexistants** : établir une grille de comparaison d'au moins deux services d'extraction documentaire au regard de contraintes techniques, budgétaires et réglementaires, puis justifier un choix argumenté plutôt qu'intuitif.
- **Paramétrer un service d'IA managé** en suivant la documentation du fournisseur (création de la ressource, région, authentification, appel du bon modèle/processeur) pour extraire les champs d'une facture sans entraîner de modèle.
- **Développer une API REST exposant le service d'IA** avec FastAPI : concevoir les routes, valider les entrées et structurer les sorties, gérer les erreurs et les réponses du service cloud.
- **Intégrer l'API dans une interface cliente** Streamlit ou Gradio qui consomme les routes, gère les réponses et rend le résultat exploitable par un utilisateur non technique.
- **Prendre en compte le RGPD et la souveraineté** dans un usage de service cloud IA : choix de la région, non-versionnement des secrets, absence de données personnelles réelles dans les tests, traçabilité des appels.

## Architecture cible

L'application attendue est une chaîne simple mais complète : une **interface cliente** (Streamlit ou Gradio) envoie une facture à une **API FastAPI** que vous développez ; cette API appelle le **service d'IA cloud managé** retenu, récupère les champs extraits, les **normalise** en un JSON structuré et les renvoie à l'interface, qui les affiche pour relecture.

```
        +-------------------------------------------------+
        |   INTERFACE CLIENTE  (Streamlit ou Gradio)      |
        |   - téléversement d'une facture (PDF / image)   |
        |   - affichage des champs extraits + confiance   |
        +-----------------------+-------------------------+
                                |  (requête HTTP)
                                v
        +-------------------------------------------------+
        |         API REST  (FastAPI, développée)         |
        |   - route d'extraction : reçoit le fichier      |
        |   - validation Pydantic des entrées/sorties     |
        |   - appel du service cloud, gestion des erreurs |
        |   - normalisation en JSON structuré             |
        +-----------------------+-------------------------+
                                |  (SDK / appel REST)
                                v
        +-------------------------------------------------+
        |   SERVICE D'IA CLOUD MANAGÉ (au choix, 1 seul)  |
        |   Azure Document Intelligence / Amazon Textract |
        |   / Google Document AI  — région EU             |
        +-------------------------------------------------+

        ------------------------------------------------------
        EN AMONT (phase 1) : évaluation comparative d'AU MOINS
        2 services sur un même échantillon de factures.
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu, faisant apparaître l'interface, l'API, le service cloud et la frontière où transitent les données.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient sa propre application. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et évaluation comparative (J1)

Aucune ligne de code d'intégration. Commencez par **cadrer le besoin** : qu'est-ce qu'une extraction réussie pour Facturio ? Formalisez la liste des **champs cibles** (fournisseur, date, numéro de facture, montant HT, montant de TVA, total TTC) et ce qui constitue une erreur acceptable ou bloquante.

Constituez ensuite un **échantillon de test représentatif** à partir des jeux publics : une dizaine de factures variées (mises en page différentes, qualité inégale, au moins quelques factures « à la française » avec TVA et SIRET).

Réalisez alors l'**évaluation comparative d'au moins 2 services** d'extraction documentaire (par exemple Azure Document Intelligence vs Amazon Textract, ou l'un des deux vs Google Document AI). Testez chaque service sur le même échantillon et comparez-les sur des critères explicites :

- **Qualité d'extraction** : quels champs sont correctement reconnus, sur combien de factures ? Comment mesurer un taux de réussite plutôt que de rester au ressenti ?
- **Contraintes techniques** : formats acceptés, limites de taille, SDK Python disponible, facilité d'appel.
- **Contraintes budgétaires** : palier gratuit, prix par page au-delà, unité de facturation. À volume Facturio (estimez-le), combien coûterait chaque service par mois ?
- **Contraintes réglementaires** : région EU disponible ? Engagement de non-réutilisation des données pour l'entraînement ? Ces points sont-ils décisifs vu que Facturio traite des données d'entreprise ?

Tranchez : **quel service intégrez-vous, et pourquoi ?** Votre choix doit tenir dans un tableau comparatif argumenté, pas dans une préférence personnelle.

Formalisez enfin votre plan de la semaine dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** champs cibles, échantillon de test, tableau comparatif des 2 services avec choix justifié et Kanban présentés en 5 minutes au formateur.

### Phase 2 — Paramétrage du service et premier appel (J2)

Passez au concret sur le service retenu. Créez la ressource cloud dans une **région européenne**, récupérez la clé / les credentials, et installez le SDK Python correspondant. Réalisez un **premier appel isolé** (script Python ou notebook) qui envoie une facture de votre échantillon et affiche la réponse brute du service.

- Où placez-vous la clé pour qu'elle ne finisse **jamais** sur GitHub ? (variable d'environnement, `.env` ignoré, `.env.example` fourni)
- Quelle **structure** a la réponse du service ? Quels champs correspondent à vos champs cibles, et avec quel **score de confiance** ?
- Que renvoie le service sur une facture **difficile** (photo floue, champ manquant) : une erreur, une valeur vide, une valeur fausse avec confiance faible ?

**Résultat testable en fin de J2 :** un script appelle le service sur une facture et affiche les champs cibles extraits, sans aucun secret présent dans le dépôt.

### Phase 3 — API d'extraction avec FastAPI (J2-J3)

Encapsulez cet appel dans une **API REST FastAPI**. Concevez au minimum une route qui **reçoit une facture** (fichier téléversé), appelle le service cloud, et renvoie les **champs extraits normalisés** en JSON. C'est ici que se joue la robustesse et la propreté :

- Comment **valider** l'entrée (type de fichier, taille) et **structurer** la sortie ? (schémas Pydantic pour les champs de facture)
- Que renvoie votre API si le service cloud est **indisponible**, lève une erreur, ou n'extrait rien ? (codes HTTP adaptés, message clair, pas de crash)
- La réponse brute du fournisseur est verbeuse et propre à son format : comment la **normalisez-vous** en un contrat de sortie stable, indépendant du fournisseur, pour que l'interface n'ait pas à connaître le service utilisé ?
- Votre API **journalise-t-elle** ses appels (document traité, durée, succès/échec) sans logguer de données personnelles ?

Documentez vos routes (FastAPI expose `/docs` automatiquement — exploitez-le).

**Résultat testable :** un appel à votre route (via `/docs` ou `curl`) avec une facture renvoie un JSON structuré des champs cibles, et un cas d'erreur renvoie un code HTTP explicite plutôt qu'une trace.

### Phase 4 — Interface cliente et boucle complète (J3-J4)

Développez l'**interface Streamlit ou Gradio** qui consomme votre API. Elle doit permettre à un utilisateur non technique de :

- **téléverser** une facture (PDF ou image) ;
- déclencher l'extraction (appel à votre API FastAPI) ;
- **afficher** les champs extraits de façon lisible (tableau ou formulaire), avec l'indication de **confiance** quand le service la fournit ;
- **signaler visuellement** un champ manquant ou à faible confiance, pour qu'un humain sache où relire.

Soignez l'expérience : un message d'attente pendant l'appel, un message d'erreur compréhensible si l'API échoue, un rendu propre du résultat.

- L'interface reste-t-elle utilisable quand l'extraction **échoue** ou renvoie des champs vides ?
- Un comptable de Facturio comprendrait-il l'écran sans explication ?

**Résultat testable :** depuis l'interface, vous téléversez une facture de l'échantillon et les champs extraits s'affichent, confiance comprise ; un cas d'échec affiche un message clair sans planter.

### Phase 5 — Consolidation, RGPD, documentation et démo (J5)

Finalisez le README (description, technologies, installation et lancement, architecture, gestion des secrets, auteur). Rédigez une courte **note RGPD/souveraineté** : région choisie, nature des données, engagement du fournisseur sur la non-réutilisation, pourquoi vous n'avez testé que sur des factures publiques. Vérifiez que **rien de secret n'est versionné** et que la procédure d'installation est rejouable de zéro (avec `.env.example`). Mettez à jour le schéma d'architecture et le Kanban, puis répétez votre démonstration : scénario, ordre de lancement (API puis interface), plan B si le service cloud refuse de répondre le jour J (facture en cache, capture d'écran de secours).

### Socle commun (obligatoire)

- **Comparatif d'au moins 2 services** d'extraction documentaire avec critères techniques, budgétaires, réglementaires et **choix justifié**.
- Service retenu **paramétré** (région EU) et appelé avec succès depuis Python, **sans secret versionné**.
- **API FastAPI** avec au moins une route d'extraction : entrée validée, sortie JSON normalisée, erreurs gérées.
- **Interface Streamlit ou Gradio** consommant l'API : téléversement, affichage des champs et de la confiance, gestion d'un cas d'échec.
- **Note RGPD/souveraineté** (région, données, non-réutilisation, tests sur données publiques).
- Repo public documenté avec README, schéma d'architecture et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- **Mesurer et afficher un taux de réussite** d'extraction sur l'échantillon (champ par champ) plutôt qu'une impression qualitative.
- Ajouter un **second type de document** (reçu / ticket) ou brancher un **second service** derrière la même API via un paramètre de configuration.
- **Conteneuriser** l'API (et l'interface) avec Docker / Docker Compose pour un lancement en une commande.
- Ajouter une étape d'**anonymisation** des données avant appel (masquage IBAN, e-mail) et le documenter comme mesure RGPD.
- Écrire quelques **tests automatisés** de l'API (réponse sur une facture connue, comportement en cas d'erreur), avec un client HTTP de test.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un **README** structuré : description du projet et de la question métier, technologies utilisées, instructions d'installation et de lancement pas à pas (dont configuration des secrets via `.env.example`), architecture (schéma intégré au README), gestion de la confidentialité, auteur.
- Le **tableau comparatif des services** (au moins 2), avec critères techniques, budgétaires et réglementaires, et la justification du choix — dans le repo (une à deux pages).
- Le **code de l'API FastAPI** : routes, schémas Pydantic, appel du service cloud, gestion des erreurs et journalisation.
- Le **code de l'interface** Streamlit ou Gradio consommant l'API.
- Le **fichier `.env.example`** listant les variables attendues (jamais les vraies clés) et un `.gitignore` excluant les secrets.
- La **note RGPD/souveraineté** (région, données, non-réutilisation, tests sur données publiques).
- Le **schéma d'architecture au format image** (PNG ou export draw.io) : interface, API, service cloud, frontière des données. Pas de schéma ASCII.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture ou log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous lancez votre API puis votre interface, téléversez une facture de l'échantillon, montrez les champs extraits et leur confiance, puis déclenchez au moins un **cas d'erreur** (facture illisible ou service indisponible) pour prouver que la chaîne ne casse pas. Les questions portent sur vos choix : pourquoi ce service, quelle région et pourquoi, comment l'API normalise la réponse, comment les secrets sont protégés, ce qui changerait à l'échelle de Facturio.
- **Revue de code, d'architecture et de conformité — 30 %** : examen du repo GitHub public (structure, lisibilité, gestion des erreurs, absence de secret versionné, qualité du README), du schéma d'architecture, du tableau comparatif (pertinence des critères) et de la note RGPD/souveraineté.

> **Validation partielle** : une application qui ne fonctionne pas en démonstration mais dont le code est structuré, versionné et documenté peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de comparatif, de documentation ou expose des secrets ne valide pas les critères correspondants.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Comparaison et choix d'un service d'IA cloud

- Un comparatif d'**au moins 2 services** d'extraction documentaire est documenté avec des critères explicites (qualité, technique, budget, réglementaire).
- Le comparatif s'appuie sur un **même échantillon de test** appliqué à chaque service, et pas seulement sur la documentation.
- Le **choix du service intégré est justifié** au regard des contraintes techniques, budgétaires et réglementaires de Facturio.
- Les **coûts** à l'échelle de Facturio sont estimés à partir des grilles tarifaires réelles (palier gratuit et prix au-delà).

### Paramétrage et appel du service managé

- Le service retenu est **créé dans une région européenne** et appelé avec succès depuis Python (champs cibles extraits d'au moins une facture).
- **Aucun secret** (clé API, credentials) n'est présent dans le dépôt ; un `.env.example` et un `.gitignore` adéquat sont fournis.
- Le comportement du service sur une facture **difficile ou invalide** est observé et documenté (erreur, champ vide, faible confiance).

### API REST d'exposition du service

- L'API FastAPI expose au moins une **route d'extraction** qui reçoit une facture et renvoie les champs en **JSON structuré**.
- Les **entrées sont validées** (type/taille de fichier) et la **sortie est normalisée** via des schémas, indépendamment du format brut du fournisseur.
- Les **erreurs** (service indisponible, extraction vide) renvoient un **code HTTP explicite** et un message clair, sans crash ni trace exposée.
- Les appels sont **journalisés** sans consigner de données personnelles.

### Interface cliente et intégration de bout en bout

- L'interface Streamlit ou Gradio permet de **téléverser une facture** et **affiche les champs extraits** de façon lisible.
- L'interface **consomme réellement l'API** (et non le service cloud en direct) et affiche l'**indication de confiance** quand elle est disponible.
- Un **cas d'échec** (extraction vide, API en erreur) est géré côté interface par un message clair, sans plantage.
- La **note RGPD/souveraineté** est présente et cohérente avec les choix techniques (région, données publiques, non-réutilisation).

## Ressources

- [Cours Python](../../../01-Fondamentaux/Python/)
- [Cours FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/)
- [Cours Services IA Cloud (Azure / AWS / GCP)](../../../04-Cloud-Platforms/AI-Services/)
- [Cours Streamlit](../../../12-Frontend-IA/02-Streamlit/)
- [Cours Gradio](../../../12-Frontend-IA/01-Gradio/)
- [Cours Docker](../../../02-Containerisation/Docker/)
- Azure AI Document Intelligence (modèle Invoice, régions, SDK Python) : https://learn.microsoft.com/azure/ai-services/document-intelligence/
- Amazon Textract — `AnalyzeExpense` pour factures et reçus : https://docs.aws.amazon.com/textract/latest/dg/analyzing-document-expense.html
- Google Document AI — Invoice Parser : https://cloud.google.com/document-ai/docs/processors-list
- Documentation FastAPI (routes, Pydantic, `UploadFile`, gestion des erreurs) : https://fastapi.tiangolo.com/
- Documentation Streamlit : https://docs.streamlit.io/
- Documentation Gradio : https://www.gradio.app/docs/
- Jeu de factures pour OCR (Kaggle) : https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr
- CNIL — IA et RGPD, régions et transferts de données : https://www.cnil.fr/fr/intelligence-artificielle
