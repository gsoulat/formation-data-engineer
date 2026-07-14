# Brief : Un assistant conversationnel RAG pour répondre aux questions réglementaires de Cavéo sur un corpus documentaire réel

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Python, LangChain (multi-providers), base vectorielle (Chroma ou Qdrant), modèles d'embeddings, RAGAS, Streamlit, Git |
| **Prérequis** | [Cours Python](../../../01-Fondamentaux/Python/) + [Cours LLM](../../../10-Large-Language-Model/LLM/) + [Cours RAG](../../../10-Large-Language-Model/RAG/) + [Cours LangChain](../../../10-Large-Language-Model/LangChain/) + [Cours Bases vectorielles](../../../05-Databases/VectorDB/) + [Cours Streamlit](../../../12-Frontend-IA/02-Streamlit/) |

## Contexte

### L'entreprise

**Cavéo** est une scale-up française de la _RegTech_ créée en 2019 à Nantes. Ses 60 salariés éditent une plateforme SaaS qui aide les PME industrielles à rester en conformité avec les réglementations européennes (RGPD, sécurité produit, et depuis peu le règlement européen sur l'intelligence artificielle, l'« AI Act »). L'équipe compte deux juristes, une équipe produit et une petite cellule data/IA (vous), rattachée à la CTO qui sponsorise le projet.

### Le problème

Le support de Cavéo croule sous les questions réglementaires de ses clients : _« Mon logiciel de tri de CV est-il un système à haut risque ? »_, _« Quelles obligations de transparence pour un chatbot ? »_, _« Ai-je le droit de faire de la reconnaissance faciale en temps réel ? »_. Aujourd'hui, un client ouvre un ticket, un juriste cherche la réponse dans des centaines de pages de texte réglementaire, recopie l'article pertinent et répond en 48 heures. Les juristes passent un tiers de leur temps sur des questions récurrentes, et les réponses ne citent pas toujours la source précise.

La CTO veut un **assistant conversationnel** capable de répondre à ces questions **en s'appuyant strictement sur le texte officiel**, en **citant l'article ou le considérant** d'où vient l'information, et en **assumant de ne pas savoir** plutôt que d'inventer. Un LLM seul, interrogé directement, « hallucine » des articles qui n'existent pas : c'est inacceptable pour un usage réglementaire. La solution retenue est un pipeline **RAG** (Retrieval-Augmented Generation), où la réponse est ancrée dans les documents réels de l'entreprise.

### La question centrale

La CTO résume l'attente en une phrase, qui devient la question centrale du projet. Chaque choix technique de la semaine devra pouvoir être justifié par sa contribution à cette question :

> **« L'assistant répond-il à partir de nos documents, en citant sa source, ou est-ce qu'il invente ? »**

### Les sources de données

Le corpus est **public et réel**. Vous constituez une base documentaire à partir d'au moins l'une de ces sources (le socle en exige une, les bonus en combinent plusieurs) :

- **Règlement (UE) 2024/1689 sur l'intelligence artificielle (« AI Act »)** — texte officiel intégral sur EUR-Lex, disponible en français, en HTML et en PDF : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=OJ:L_202401689 . C'est le corpus recommandé : il est structuré en articles, considérants et annexes, ce qui rend les citations vérifiables.
- **Règlement général sur la protection des données (RGPD, Règlement UE 2016/679)** — texte officiel EUR-Lex : https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra , et sa version annotée par la CNIL : https://www.cnil.fr/fr/reglement-europeen-protection-donnees .
- **Documentation ouverte de l'administration française** via **data.gouv.fr** (guides, référentiels au format PDF/HTML publiés en licence ouverte) : https://www.data.gouv.fr .

Constituer le corpus (téléchargement, nettoyage du texte, découpage) fait **partie du travail**. Le sujet est autonome : aucun livrable d'un brief précédent n'est nécessaire.

### Contraintes techniques

- Orchestration en **Python avec LangChain**. La conception doit rester **multi-providers** : votre code doit pouvoir basculer d'un fournisseur de LLM à un autre (par exemple OpenAI et Anthropic, ou un modèle local via Ollama) **sans réécrire le pipeline**. Les clés d'API vivent dans un fichier `.env` **jamais commité**.
- La base vectorielle est **Chroma** (démarrage rapide, local) ou **Qdrant** (via Docker) : à vous de choisir et de justifier.
- Tout choix de modèle, de base et de fournisseur doit tenir compte des **contraintes de coût, de confidentialité et de langue** (le corpus est en français). Un modèle appelé des centaines de fois pendant l'évaluation a un coût : anticipez-le.
- Tout le code est **versionné sur GitHub dès le premier jour**.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Comparer et sélectionner des services d'IA existants** (fournisseurs de LLM et de modèles d'embeddings, bases vectorielles) au regard de contraintes techniques, budgétaires, de confidentialité et de langue, puis justifier votre choix par écrit.
- **Concevoir et intégrer un service d'IA préexistant** en le paramétrant selon les préconisations du fournisseur, sans entraîner de modèle : ingérer un corpus (chunking + embeddings), le stocker dans une base vectorielle, et brancher un LLM en génération.
- **Développer une application conversationnelle intégrant un service d'IA** : orchestrer avec LangChain un pipeline de retrieval, gérer une mémoire conversationnelle, exposer une interface, et garder l'architecture agnostique du fournisseur.
- **Évaluer systématiquement le comportement de l'IA** : construire un jeu de test, mesurer avec RAGAS des métriques de qualité (fidélité aux sources, pertinence, précision et rappel du retrieval), interpréter les résultats et itérer.

## Architecture cible

Le pattern attendu est un pipeline **RAG** en deux temps. **Hors ligne (ingestion)** : les documents du corpus sont nettoyés, **découpés en chunks**, transformés en **embeddings** et stockés dans une **base vectorielle**. **En ligne (requête)** : la question de l'utilisateur est encodée, les chunks les plus proches sont **récupérés (retrieval)**, injectés dans un **prompt** avec la question et l'historique de conversation, et un **LLM** génère une réponse **citant ses sources**. Une boucle d'**évaluation RAGAS** mesure la qualité de bout en bout et guide les itérations.

```
   INGESTION (hors ligne)                          REQUÊTE (en ligne)
   ┌───────────────────────┐                  ┌──────────────────────────┐
   │  Corpus réel           │                  │  Question utilisateur    │
   │  (AI Act / RGPD / PDF) │                  │  + historique de conv.   │
   └───────────┬───────────┘                  └────────────┬─────────────┘
               │                                            │
        nettoyage + chunking                          embedding requête
               │                                            │
        embeddings (modèle)                                 │
               │                                            ▼
               ▼                                  ┌──────────────────────┐
   ┌───────────────────────┐   retrieval (top-k)  │  Retriever           │
   │  BASE VECTORIELLE     │◄─────────────────────┤  (similarité)        │
   │  (Chroma / Qdrant)    │─────────────────────►│  chunks + métadonnées│
   └───────────────────────┘                      └──────────┬───────────┘
                                                             │
                                              prompt = question + contexte + mémoire
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │  LLM (multi-provider)│
                                                  │  via LangChain       │
                                                  └──────────┬───────────┘
                                                             │
                                          réponse + sources citées (article / considérant)
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │  Interface (Streamlit)│
                                                  └──────────────────────┘

   ┌──────────────────────────────────────────────────────────────────┐
   │  ÉVALUATION RAGAS : faithfulness, answer relevancy,               │
   │  context precision, context recall  → rapport + itérations        │
   └──────────────────────────────────────────────────────────────────┘
```

> Vous produirez votre **propre schéma d'architecture au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu, en distinguant clairement la phase d'ingestion hors ligne et la phase de requête en ligne, et en positionnant la boucle d'évaluation.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient son propre assistant. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage, veille et conception (J1)

Aucune ligne de code de pipeline. Commencez par comprendre le besoin de Cavéo : reformulez la question centrale, listez 8 à 10 questions réelles que les clients pourraient poser à l'assistant, et identifiez ce qui distingue une bonne réponse (ancrée, sourcée, honnête sur ses limites) d'une mauvaise (inventée, hors sujet, sans source).

Menez ensuite une **veille comparative** et tranchez, par écrit, les choix structurants :

- Quel **fournisseur de LLM** et quel **modèle d'embeddings** ? Comparez au moins deux options au regard du coût, de la confidentialité (le corpus part-il chez un tiers ?), de la qualité en **français** et de la facilité d'intégration. Pourquoi une architecture multi-providers est-elle un atout ici ?
- **Chroma ou Qdrant** ? Qu'est-ce qui justifie votre choix pour ce volume et ce contexte ?
- Comment allez-vous **découper** le corpus ? Un chunk trop grand noie l'information, trop petit la fragmente : quelle taille, quel recouvrement, et faut-il respecter la structure du document (un article = un chunk) ? Quelles **métadonnées** conserverez-vous pour pouvoir citer la source (numéro d'article, considérant, page, URL) ?

Posez tout cela sur un **schéma d'architecture** (image, pas d'ASCII) distinguant ingestion et requête, et formalisez votre plan dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** note de cadrage (questions cibles, choix de providers/base/stratégie de chunking justifiés), schéma d'architecture et Kanban présentés en 5 minutes au formateur.

### Phase 2 — Ingestion : chunking, embeddings et base vectorielle (J2)

Constituez la base de connaissances. Téléchargez le corpus choisi, **nettoyez** le texte (en-têtes, pieds de page, artefacts d'extraction PDF), **découpez** en chunks selon la stratégie décidée en phase 1 en **conservant les métadonnées de source**, calculez les **embeddings** et **indexez** le tout dans Chroma ou Qdrant. L'indexation doit être **rejouable** : quelqu'un qui clone votre repo doit pouvoir reconstruire la base d'une commande.

- Combien de chunks obtenez-vous, et est-ce cohérent avec la taille du corpus ?
- Si vous relancez l'ingestion, dupliquez-vous les vecteurs ou repartez-vous d'une base propre ?
- Une recherche de similarité sur une question test renvoie-t-elle des chunks **manifestement pertinents** ? Inspectez à la main quelques résultats avant d'aller plus loin.

**Résultat testable en fin de J2 :** le script d'ingestion construit la base sans erreur, et une requête de similarité en ligne de commande renvoie les chunks attendus avec leurs métadonnées de source.

### Phase 3 — Orchestration RAG multi-providers et mémoire (J3)

Assemblez le pipeline avec **LangChain**. Branchez le retriever sur votre base, construisez le **prompt** (consigne système exigeant de répondre uniquement à partir du contexte, de citer la source et de dire « je ne trouve pas cette information dans les documents » le cas échéant), et connectez le **LLM**. Ajoutez une **mémoire conversationnelle** pour que l'assistant tienne une conversation cohérente (questions de suivi, pronoms, « et dans ce cas-là ? »).

- Votre code peut-il **changer de fournisseur de LLM** via une variable de configuration, sans toucher au reste du pipeline ? Démontrez-le avec deux providers.
- Que répond l'assistant à une question **hors corpus** (par exemple sur la fiscalité) ? Refuse-t-il proprement ou invente-t-il ?
- La **source citée** correspond-elle réellement au chunk qui a servi à répondre ?
- Sans mémoire, une question de suivi (« et pour un chatbot ? ») perd son contexte : votre mémoire corrige-t-elle ce comportement ?

Exposez enfin l'assistant dans une **interface Streamlit** (chat avec historique affiché) — c'est le minimum du socle pour la démo.

**Résultat testable en fin de J3 :** dans l'interface, une question du corpus reçoit une réponse sourcée, une question de suivi est comprise grâce à la mémoire, et une question hors corpus est refusée proprement.

### Phase 4 — Évaluation systématique avec RAGAS (J4)

Le cœur de la démarche d'ingénieur : ne pas se fier à quelques essais « à l'œil », mais **mesurer**. Construisez un **jeu de test** d'au moins 15 questions représentatives, avec pour chacune la réponse attendue et/ou l'article de référence. Faites tourner votre pipeline dessus, collectez pour chaque question la réponse générée et les chunks récupérés, puis évaluez avec **RAGAS** au moins :

- **faithfulness** (fidélité) — la réponse est-elle bien ancrée dans le contexte récupéré, sans invention ?
- **answer relevancy** (pertinence de la réponse) — répond-elle vraiment à la question ?
- **context precision** et **context recall** — le retriever ramène-t-il les bons chunks, et seulement eux ?

Produisez un **rapport d'évaluation** (tableau des scores, moyennes, questions les mieux et les plus mal traitées) et surtout : **itérez**. Identifiez au moins **une faiblesse** (par exemple un chunking trop grossier, un top-k inadapté, un prompt trop permissif), appliquez **une modification**, ré-évaluez, et **documentez l'avant/après** chiffré.

- Une métrique basse traduit-elle un problème de **retrieval** (mauvais chunks) ou de **génération** (mauvaise réponse malgré de bons chunks) ? Le diagnostic conditionne le correctif.
- Attention au coût : RAGAS appelle un LLM juge pour chaque question. Anticipez le volume d'appels.

**Résultat testable en fin de J4 :** un rapport RAGAS chiffré avant/après une itération d'amélioration, avec l'interprétation des scores et la modification justifiée.

### Phase 5 — Consolidation, documentation et démo (J5)

Finalisez le README (description, question métier, technologies, installation et lancement pas à pas, reconstruction de la base, architecture, résultats d'évaluation, auteur), vérifiez que la procédure est **rejouable de zéro** (clé d'API mise à part), mettez à jour le schéma et le Kanban, puis répétez votre démonstration : scénario de questions, question hors corpus, question de suivi, et lecture commentée du rapport RAGAS. Prévoyez un plan B si le réseau ou un fournisseur est indisponible le jour J.

### Socle commun (obligatoire)

- Note de cadrage avec **comparatif justifié** des providers de LLM/embeddings et du choix de base vectorielle.
- Pipeline d'**ingestion rejouable** : nettoyage, chunking avec métadonnées de source, embeddings, indexation dans Chroma ou Qdrant.
- Pipeline **RAG orchestré avec LangChain**, **agnostique du fournisseur** (bascule de LLM par configuration), avec **mémoire conversationnelle**.
- L'assistant **cite ses sources** et **refuse proprement** les questions hors corpus.
- Interface **Streamlit** de conversation.
- **Évaluation RAGAS** sur un jeu de test d'au moins 15 questions, avec **au moins une itération** d'amélioration documentée (avant/après chiffré).
- Repo public documenté avec schéma d'architecture et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- **Enrichir le retrieval** : ajouter un _re-ranker_, une recherche hybride (mots-clés + vecteurs) ou du _query rewriting_, et **prouver par RAGAS** le gain.
- **Combiner plusieurs corpus** (AI Act + RGPD) avec filtrage par métadonnées de source.
- **Générer un jeu de test synthétique** avec le `TestsetGenerator` de RAGAS et comparer aux questions écrites à la main.
- **Comparer deux fournisseurs de LLM** sur le même jeu de test RAGAS (qualité vs coût) et en tirer une recommandation chiffrée.
- **Exposer le pipeline via une API** ([FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/)) consommée par l'interface, pour une architecture plus proche de la production.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un **README structuré** : description du projet et de la question métier, technologies utilisées, instructions d'installation et de lancement pas à pas, procédure de reconstruction de la base vectorielle, architecture (schéma intégré), résultats d'évaluation, auteur. Le fichier `.env` **ne doit pas être commité** (fournir un `.env.example`).
- Le **script d'ingestion** (nettoyage, chunking, embeddings, indexation) rejouable, et la configuration de la base vectorielle.
- Le **pipeline RAG LangChain** multi-providers avec mémoire conversationnelle, et l'**application Streamlit**.
- La **note de cadrage** et le **comparatif** des providers/base vectorielle (une à deux pages, dans le repo).
- Le **jeu de test** (questions + références) et le **rapport d'évaluation RAGAS** (scores, moyennes, avant/après itération, interprétation).
- Le **schéma d'architecture au format image** (PNG ou export draw.io) distinguant ingestion et requête. Pas de schéma ASCII.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (rapport, capture d'écran ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous lancez l'assistant, posez une série de questions du corpus (réponses sourcées attendues), une question de suivi (mémoire), une question hors corpus (refus attendu), démontrez la **bascule de fournisseur de LLM** par configuration, puis commentez votre **rapport RAGAS** et l'itération d'amélioration menée. Les questions portent sur vos choix : stratégie de chunking, métadonnées de citation, top-k du retrieval, contenu du prompt, interprétation des métriques et diagnostic retrieval vs génération.
- **Revue de code et d'architecture — 30 %** : examen du repo GitHub public (structure, lisibilité, gestion des secrets via `.env`, qualité du README et de la procédure de reconstruction), du schéma d'architecture (distinction ingestion/requête, lisibilité) et de la note de cadrage (pertinence du comparatif de providers et du choix de base vectorielle).

> **Validation partielle** : un assistant qui répond mal en démonstration mais dont le code est structuré, versionné, documenté et **accompagné d'un rapport RAGAS qui diagnostique honnêtement les faiblesses** peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de documentation et d'évaluation ne valide pas les critères correspondants.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Sélection et comparaison des services d'IA

- La note de cadrage compare au moins deux fournisseurs de LLM et/ou d'embeddings avec des critères explicites (coût, confidentialité, qualité en français, intégration). — OUI / NON
- Le choix de la base vectorielle (Chroma ou Qdrant) est justifié au regard du contexte et du volume. — OUI / NON
- Les contraintes de coût, de confidentialité et de langue du corpus sont prises en compte dans les choix. — OUI / NON
- La stratégie de chunking (taille, recouvrement, respect de la structure) et les métadonnées de source sont documentées et argumentées. — OUI / NON

### Intégration du service d'IA et ingestion

- Le pipeline d'ingestion (nettoyage, chunking, embeddings, indexation) s'exécute sans erreur et est rejouable depuis le repo. — OUI / NON
- Les chunks conservent les métadonnées permettant de citer la source (article, considérant, page ou URL). — OUI / NON
- Une recherche de similarité renvoie des chunks manifestement pertinents pour une question du corpus. — OUI / NON
- La procédure de reconstruction de la base est documentée dans le README. — OUI / NON

### Application conversationnelle RAG

- Le pipeline est orchestré avec LangChain et le fournisseur de LLM est interchangeable par configuration, sans réécriture du pipeline. — OUI / NON
- L'assistant répond aux questions du corpus **en citant la source** correspondant réellement au contexte récupéré. — OUI / NON
- Une question hors corpus reçoit un refus explicite plutôt qu'une réponse inventée. — OUI / NON
- La mémoire conversationnelle permet de traiter correctement une question de suivi. — OUI / NON

### Évaluation systématique de l'IA

- Un jeu de test d'au moins 15 questions représentatives est constitué. — OUI / NON
- Le pipeline est évalué avec RAGAS sur au moins la fidélité, la pertinence de la réponse, la précision et le rappel du contexte. — OUI / NON
- Le rapport présente les scores et distingue les questions bien et mal traitées. — OUI / NON
- Au moins une itération d'amélioration est menée, avec comparaison chiffrée avant/après et interprétation (diagnostic retrieval vs génération). — OUI / NON

## Ressources

- [Cours Python](../../../01-Fondamentaux/Python/)
- [Cours LLM](../../../10-Large-Language-Model/LLM/)
- [Cours RAG](../../../10-Large-Language-Model/RAG/)
- [Cours LangChain](../../../10-Large-Language-Model/LangChain/)
- [Cours Bases vectorielles](../../../05-Databases/VectorDB/)
- [Cours Streamlit](../../../12-Frontend-IA/02-Streamlit/)
- [Cours FastAPI](../../../01-Fondamentaux/Python/08-FastAPI/) (pour le bonus API)
- Règlement (UE) 2024/1689 sur l'IA — texte officiel EUR-Lex (FR) : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=OJ:L_202401689
- Règlement général sur la protection des données (RGPD) — EUR-Lex (FR) : https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra
- RGPD annoté par la CNIL : https://www.cnil.fr/fr/reglement-europeen-protection-donnees
- Portail de données publiques data.gouv.fr : https://www.data.gouv.fr
- Documentation LangChain (RAG, retrievers, mémoire, providers) : https://python.langchain.com/docs/tutorials/rag/
- Documentation Chroma : https://docs.trychroma.com/
- Documentation Qdrant : https://qdrant.tech/documentation/
- Documentation RAGAS (métriques et évaluation) : https://docs.ragas.io/
