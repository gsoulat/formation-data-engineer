---
title: 07_introduction_rag
tags:
  - LLM
  - 10-Large-Language-Model
category: 10-Large-Language-Model
---
# Module 7 : RAG - Donnez une Mémoire Externe à votre IA

Bienvenue dans cette deuxième journée de formation ! Hier, nous avons appris à dialoguer avec un LLM et à lui faire utiliser des outils. Aujourd'hui, nous allons résoudre l'un de ses plus grands problèmes : son ignorance de vos données personnelles et du monde récent. Pour cela, nous allons utiliser une technique fondamentale : le **RAG (Retrieval-Augmented Generation)**.

> 🧭 **Deux niveaux de RAG dans ce dépôt** — ce chapitre est l'**introduction** (comprendre et construire un premier pipeline RAG). Pour la version **production** (chunking avancé, recherche hybride, reranking, évaluation RAGAS + CI), va au module dédié [**RAG/**](../../RAG/). Voir la [carte des deux pistes](../../README.md).

---

## 1. Le Double Handicap d'un LLM Standard

Les grands modèles de langage, même les plus performants, ont deux limites majeures qui les empêchent d'être vraiment utiles dans un contexte professionnel ou personnel :

1.  **Connaissances Figées dans le Temps** : Un LLM comme Llama 3 a été entraîné sur des données qui s'arrêtent à une certaine date. Il ne connaît rien des événements récents, des nouvelles de votre entreprise, ou des derniers potins.
2.  **Absence de Connaissances Privées** : Le modèle ignore tout de VOS documents. Il n'a jamais lu vos rapports internes, vos notes de projet, votre documentation technique, ou vos emails.

Le RAG est la solution la plus efficace et la plus utilisée aujourd'hui pour résoudre ces deux problèmes en même temps.

---

## 2. Le Principe du RAG : Un Examen à Livre Ouvert pour l'IA

Le RAG transforme la manière dont le LLM répond à une question. Au lieu de simplement utiliser ses connaissances internes (sa "mémoire"), il va suivre un processus intelligent en trois étapes :

![Diagramme simple expliquant le processus RAG en 3 étapes : Recherche, Augmentation, Génération](https://i.imgur.com/uQx05Gk.png)

1.  **Recherche (Retrieval)** :
    * Face à une question de l'utilisateur ("Quel est le statut du projet Alpha ?"), le système ne se précipite pas vers le LLM. Il commence par **rechercher des informations pertinentes** dans une base de connaissances que nous lui avons fournie (un ensemble de PDFs, de fichiers textes, de pages web, etc.).

2.  **Augmentation (Augmented)** :
    * Le système prend les extraits les plus pertinents trouvés à l'étape 1 et les insère dans le prompt, à côté de la question initiale de l'utilisateur. On "augmente" la question avec un contexte factuel et précis.

3.  **Génération (Generation)** :
    * Ce prompt "augmenté" est ensuite envoyé au LLM. Le modèle utilise alors à la fois ses connaissances générales et, surtout, **le contexte spécifique fourni** pour formuler une réponse précise et factuelle, basée sur vos documents.

> **💡 Analogie :** Le RAG, c'est comme si vous donniez à votre LLM le droit de passer un examen **"à livre ouvert"**. Au lieu de devoir tout mémoriser, il peut consulter les documents pertinents (vos livres) juste avant de répondre à chaque question.

---

## 3. L'Architecture d'un Système RAG

Pour mettre cela en place, nous avons besoin de deux processus principaux qui composent l'architecture RAG :

-   **L'Ingestion de Données (une seule fois par document)** : C'est le processus de préparation de notre base de connaissances. On prend nos documents, on les découpe en morceaux ("chunks"), on les transforme en vecteurs numériques ("embeddings") et on les stocke dans une base de données spéciale : une **base de données vectorielle** (comme ChromaDB).

-   **L'Interrogation (à chaque question)** : C'est le processus en 3 étapes (Recherche, Augmentation, Génération) décrit ci-dessus, qui se produit chaque fois qu'un utilisateur pose une question.

![Architecture RAG standard montrant les deux phases d'ingestion et d'interrogation](https://raw.githubusercontent.com/aws-samples/aws-genai-llm-chatbot/main/docs/images/rag-pattern.png)
*(Source du diagramme : AWS Samples)*

Cette technique est au cœur de la majorité des applications d'IA générative professionnelles aujourd'hui car elle permet de réduire les "hallucinations" et de fonder les réponses des LLMs sur des faits vérifiables.

---

Maintenant que nous avons compris la théorie, passons à la pratique. Dans le prochain module, nous allons construire la première partie de notre système RAG : la base de connaissances vectorielle.

**[➡️ Prochain Module : Construire une Base de Connaissances Vectorielle](./08_database_vectorielle.md)**
