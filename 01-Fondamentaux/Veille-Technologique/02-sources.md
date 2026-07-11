# Sources de Veille Technologique

## Introduction

La qualité de votre veille dépend directement de la qualité de vos sources. Une mauvaise source vous fait perdre du temps ou vous induit en erreur. Une bonne source vous apporte du signal fiable et actionnable.

Ce fichier recense les meilleures sources pour un data engineer / ML engineer, organisées par catégorie.

---

## Catégorie 1 — GitHub

GitHub est la source de veille technologique la plus sous-exploitée par les débutants et la plus utilisée par les experts.

### GitHub Trending

**URL** : [https://github.com/trending](https://github.com/trending)

Affiche les dépôts les plus populaires du jour, de la semaine, ou du mois, filtrables par langage.

**Comment l'utiliser :**
1. Visitez la page une fois par semaine
2. Filtrez par `Python` ou laissez "All languages"
3. Regardez les repos en tendance sur la semaine
4. Pour chaque repo intéressant : lisez le README en 2 minutes
5. Notez ceux qui méritent une exploration approfondie

**Signaux à surveiller :**
- Un repo passe de 0 à 5 000 étoiles en une semaine : phénomène à observer
- Un nouveau player dans une catégorie établie (ex: nouvelle librairie RAG)
- Des outils de grandes entreprises publiés en open source (Meta, Google, Netflix...)

### GitHub Topics / Explore

**URL** : [https://github.com/topics](https://github.com/topics)

Permet de suivre une catégorie : `data-engineering`, `llm`, `vector-database`, `mlops`, etc.

### Awesome Lists

Les **awesome lists** sont des listes curées de ressources sur un sujet, maintenues par la communauté.

Exemples incontournables pour un data engineer :
- [awesome-data-engineering](https://github.com/igorbarinov/awesome-data-engineering) : outils et frameworks
- [awesome-mlops](https://github.com/visenger/awesome-mlops) : MLOps
- [awesome-llm](https://github.com/Hannibal046/Awesome-LLM) : LLMs
- [awesome-vector-search](https://github.com/currentslab/awesome-vector-search) : bases vectorielles
- [awesome-airflow](https://github.com/jghoman/awesome-apache-airflow)
- [the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) : outils DevOps/SRE

**Astuce** : Étoilez ces repos pour les garder accessibles, et visitez-les quand vous cherchez un outil pour une catégorie spécifique.

### Repos à étoiler pour la veille continue

Étoiler un repo vous permet de recevoir des notifications sur ses releases. Stratégie :
- Étoilez les projets que vous utilisez en production → suivre les releases et changelogs
- Suivez les comptes GitHub des entreprises tech : `apache`, `apache/arrow`, `dbt-labs`, etc.
- Suivez les profils GitHub de personnalités influentes

---

## Catégorie 2 — Hacker News

**URL** : [https://news.ycombinator.com](https://news.ycombinator.com)

Hacker News (HN) est le forum communautaire de Y Combinator. C'est la source la plus dense en signal technique de l'écosystème tech mondial.

### Comment lire Hacker News

**Format de la page principale :**
- 30 liens par page, upvotés par la communauté
- Mélange : startups, articles techniques, débats, Show HN (projets présentés), Ask HN

**Pour la veille data/IA, ce qui compte :**
- `Show HN: [outil que j'ai construit]` → nouvelles librairies, outils
- Articles de fond sur les architectures (Substack, personal blogs)
- Annonces de grandes entreprises (AWS, Google, Meta)
- Débats techniques qui révèlent des tensions dans l'écosystème

### HN Search pour la veille rétrospective

**URL** : [https://hn.algolia.com](https://hn.algolia.com)

Recherchez une technologie pour voir tous les posts passés et leur réception par la communauté.

```
Recherches utiles :
- "dbt" → Historique des discussions sur dbt
- "vector database" → Comment la conversation a évolué
- "Apache Iceberg" → Les critiques, comparatifs, use cases
```

### Abonnement email Hacker News

Le site [hckrnews.com](https://hckrnews.com) ou l'extension **HackerNewsTop** permettent de recevoir un digest quotidien.

---

## Catégorie 3 — arXiv et recherche académique

**URL** : [https://arxiv.org](https://arxiv.org)

arXiv est le serveur de preprints en mathématiques, informatique et physique. En IA/ML, quasiment tous les articles importants sont publiés en preprint sur arXiv avant (ou au lieu d'être publiés dans des journaux).

### Catégories pertinentes

| Catégorie arXiv | Contenu |
|----------------|---------|
| `cs.AI` | Intelligence artificielle |
| `cs.LG` | Machine Learning |
| `cs.CL` | NLP, traitement du langage |
| `cs.CV` | Vision par ordinateur |
| `cs.DB` | Bases de données |
| `stat.ML` | Statistiques pour le ML |

### Comment lire des articles arXiv sans se noyer

Lire des articles de recherche prend du temps. Pour la veille, adoptez un flux en entonnoir :

```
NIVEAU 1 : Titre + Abstract (30 secondes)
       ↓ Si intéressant
NIVEAU 2 : Introduction + Conclusion (3 minutes)
       ↓ Si applicable à votre travail
NIVEAU 3 : Lecture complète (30-60 minutes)
```

### Outils pour arXiv

- **arXiv Sanity** : [http://www.arxiv-sanity.com](http://www.arxiv-sanity.com) — recommandations personnalisées
- **Semantic Scholar** : [https://www.semanticscholar.org](https://www.semanticscholar.org) — moteur de recherche académique
- **Papers With Code** : [https://paperswithcode.com](https://paperswithcode.com) — articles avec leur implémentation GitHub associée

### Articles fondateurs à connaître

Ces articles ont changé l'industrie. Même si vous ne les lisez pas entièrement, connaître leur existence et leur contribution est une base de culture technique :

| Article | Année | Contribution |
|---------|-------|-------------|
| Attention Is All You Need | 2017 | Architecture Transformer |
| BERT | 2018 | Pre-training bidirectionnel du langage |
| GPT-3 | 2020 | Few-shot learning avec les LLMs |
| LoRA | 2021 | Fine-tuning efficace des LLMs |
| RAG (Lewis et al.) | 2020 | Retrieval-Augmented Generation |
| MapReduce (Google) | 2004 | Fondation du big data distribué |
| Dynamo (Amazon) | 2007 | Bases NoSQL distribuées |
| BigTable (Google) | 2006 | Fondation des BD colonnes |
| Attention Mechanism | 2015 | Seq2Seq avec attention |

---

## Catégorie 4 — Newsletters

Les newsletters sont idéales pour recevoir de la veille curatée directement dans votre boîte mail.

### TLDR Newsletter

**URL** : [https://tldr.tech](https://tldr.tech)

Newsletter quotidienne couvrant la tech, la data, l'IA et le DevOps en résumés de 2-3 lignes. Lire TLDR chaque matin est une bonne habitude de veille : 5 minutes suffisent pour rester informé des grands titres.

**Sous-newsletters disponibles :**
- TLDR (tech générale)
- TLDR AI (IA et ML)
- TLDR Data Eng (data engineering)
- TLDR DevOps

### ByteByteGo Newsletter

**URL** : [https://bytebytego.com](https://bytebytego.com) — [Newsletter](https://blog.bytebytego.com)

Fondée par Alex Xu (auteur de *System Design Interview*). Diagrammes clairs sur les architectures systèmes, les protocoles réseau, le cloud. Excellente pour la veille architecture.

### The Pragmatic Engineer

**URL** : [https://newsletter.pragmaticengineer.com](https://newsletter.pragmaticengineer.com)

Gergely Orosz (ex-Uber). Articles longs et fouillés sur l'industrie tech, les carrières, les architectures à l'échelle. Payant mais de très haute qualité.

### Data Engineering Weekly

**URL** : [https://www.dataengineeringweekly.com](https://www.dataengineeringweekly.com)

Veille spécialisée data engineering. Articles, tutoriels, annonces d'outils.

### The Batch (deeplearning.ai)

**URL** : [https://www.deeplearning.ai/the-batch/](https://www.deeplearning.ai/the-batch/)

Newsletter d'Andrew Ng. Hebdomadaire, couvre les avancées en IA avec un regard pédagogique et critique.

### Import AI

**URL** : [https://importai.substack.com](https://importai.substack.com)

Jack Clark (cofondateur d'Anthropic). Veille sur les avancées en IA avec une analyse approfondie des enjeux.

### Tableau de bord newsletters recommandées

| Newsletter | Fréquence | Niveau | Gratuit ? |
|------------|----------|--------|----------|
| TLDR AI | Quotidien | Débutant | Oui |
| TLDR Data Eng | Hebdomadaire | Intermédiaire | Oui |
| ByteByteGo | Hebdomadaire | Intermédiaire | Partiellement |
| The Pragmatic Engineer | Bi-hebdomadaire | Avancé | Partiellement |
| The Batch (deeplearning.ai) | Hebdomadaire | Tous niveaux | Oui |
| Data Engineering Weekly | Hebdomadaire | Intermédiaire | Oui |

---

## Catégorie 5 — Podcasts

Les podcasts permettent de faire de la veille pendant les trajets, le sport ou la cuisine.

### Data Engineering Podcast

**URL** : [https://www.dataengineeringpodcast.com](https://www.dataengineeringpodcast.com)

Animé par Tobias Macey. Interviews approfondies avec des créateurs d'outils data (maintainers d'Airflow, Spark, dbt...). Chaque épisode présente une technologie ou un pattern en profondeur.

### Lex Fridman Podcast

**URL** : [https://lexfridman.com/podcast/](https://lexfridman.com/podcast/)

Interviews longues avec les figures majeures de l'IA (Yann LeCun, Sam Altman, Andrej Karpathy...). Moins technique mais excellent pour comprendre les visions et enjeux de fond.

### TWIML AI Podcast (This Week in Machine Learning)

**URL** : [https://twimlai.com](https://twimlai.com)

Interviews avec des chercheurs et praticiens en ML/IA. Format technique et approfondi.

### Latent Space

**URL** : [https://www.latent.space/podcast](https://www.latent.space/podcast)

Podcast sur l'ingénierie IA (pas la recherche). Très bon pour comprendre comment les entreprises construisent avec les LLMs.

### Software Engineering Daily

**URL** : [https://softwareengineeringdaily.com](https://softwareengineeringdaily.com)

Large spectre : cloud, data, sécurité, architecture. Plusieurs épisodes par semaine.

---

## Catégorie 6 — Conférences et talks

Les conférences publient leurs talks sur YouTube, ce qui est une mine de veille.

### Conférences IA/ML

| Conférence | Domaine | Chaîne YouTube |
|------------|---------|---------------|
| **NeurIPS** | ML fondamental | NeurIPS Foundation |
| **ICML** | Machine Learning | ICML |
| **ICLR** | Représentations | ICLR |
| **CVPR** | Vision | CVPR |

### Conférences Data Engineering

| Conférence | Domaine | Ressources |
|------------|---------|-----------|
| **Data + AI Summit** | Databricks, Apache Spark | databricks.com/sessions |
| **dbt Coalesce** | dbt, data transformation | getdbt.com/coalesce |
| **Kafka Summit** | Apache Kafka, streaming | kafka.apache.org |
| **Airflow Summit** | Apache Airflow | airflowsummit.org |
| **PGConf** | PostgreSQL | pgconf.eu |

### Conférences Cloud

| Conférence | Domaine | Notes |
|------------|---------|-------|
| **AWS re:Invent** | AWS (décembre) | Annonces majeures de l'année AWS |
| **Google Next** | GCP | Annonces Vertex AI, BigQuery |
| **Microsoft Build** | Azure | Annonces Azure OpenAI, Fabric |
| **KubeCon** | Kubernetes, Cloud Native | CNCF, workflows ML sur K8s |

**Astuce veille conférences** : En décembre (re:Invent) et en octobre (Google Next), notez dans votre agenda une demi-journée de veille pour parcourir les annonces. Ces événements structurent le calendrier tech de l'année suivante.

---

## Catégorie 7 — Blogs et Substack

### Blogs d'entreprises techniques

Ces entreprises publient régulièrement des articles techniques de haute qualité sur leurs propres blogs :

| Entreprise | Blog | Contenu |
|-----------|------|---------|
| Netflix | [netflixtechblog.com](https://netflixtechblog.com) | Architecture, data, ML à l'échelle |
| Uber | [eng.uber.com](https://eng.uber.com) | Data infrastructure, ML Ops |
| Airbnb | [medium.com/airbnb-engineering](https://medium.com/airbnb-engineering) | Data, ML, infrastructure |
| Spotify | [engineering.atspotify.com](https://engineering.atspotify.com) | ML, data, audio |
| LinkedIn | [engineering.linkedin.com](https://engineering.linkedin.com) | Kafka origine, data infra |
| Stripe | [stripe.com/blog/engineering](https://stripe.com/blog/engineering) | Fiabilité, APIs, sécurité |
| Hugging Face | [huggingface.co/blog](https://huggingface.co/blog) | NLP, LLMs, modèles open source |

### Blogs individuels à suivre

| Auteur | Blog | Spécialité |
|-------|------|-----------|
| Martin Fowler | [martinfowler.com](https://martinfowler.com) | Architecture, patterns, agile |
| Simon Willison | [simonwillison.net](https://simonwillison.net) | IA, SQLite, outils dev |
| Julia Evans | [jvns.ca](https://jvns.ca) | Linux, réseau, debugging |
| Chip Huyen | [huyenchip.com](https://huyenchip.com) | ML Systems, MLOps |
| Lilian Weng (OpenAI) | [lilianweng.github.io](https://lilianweng.github.io) | LLMs, RL, agents |

---

## Catégorie 8 — Réseaux sociaux professionnels

### LinkedIn

Utile pour suivre des professionnels du domaine, mais le rapport signal/bruit y est faible. Stratégie :
- Suivre les pages de Databricks, dbt Labs, Hugging Face, Anthropic
- Suivre des CTO et data engineers reconnus
- Désactiver les notifications des posts "inspirationnels" sans contenu

### X (Twitter)

Malgré l'évolution de la plateforme, X reste très actif pour la communauté ML/IA. La communauté #MLTwitter est dense.

Comptes à suivre (sélection) :
- `@karpathy` (Andrej Karpathy, ex-OpenAI/Tesla)
- `@ylecun` (Yann LeCun, Meta AI)
- `@emollick` (Ethan Mollick, recherche sur les LLMs)
- `@simon_w` (Simon Willison)
- `@jeremyphoward` (Jeremy Howard, fast.ai)

---

## Construire votre liste de sources personnelle

Chaque développeur a des besoins différents selon son rôle, son secteur et ses projets. Voici comment construire votre liste :

### Étape 1 : Identifiez vos 3 domaines prioritaires

Ex: `data pipelines + LLMs + cloud Azure`

### Étape 2 : Sélectionnez 5 sources maximum par catégorie

Moins c'est plus. 5 newsletters + 3 podcasts + GitHub trending = déjà beaucoup.

### Étape 3 : Testez pendant 1 mois

Suivez vos sources pendant un mois. Lesquelles vous ont apporté de la valeur ? Désinscrivez-vous des autres sans hésitation.

### Étape 4 : Réévaluez chaque trimestre

Votre domaine d'intérêt évolue. Vos sources doivent évoluer avec vous.

---

## Ressources complémentaires

- **ThoughtWorks Tech Radar** : [thoughtworks.com/radar](https://www.thoughtworks.com/radar) — le tech radar de référence, publié deux fois par an
- **CNCF Landscape** : [landscape.cncf.io](https://landscape.cncf.io) — panorama des outils cloud native
- **OSS Insight** : [ossinsight.io](https://ossinsight.io) — analytics sur l'activité GitHub
- **State of Data Engineering** (Airbyte) : rapport annuel sur l'état du data engineering
