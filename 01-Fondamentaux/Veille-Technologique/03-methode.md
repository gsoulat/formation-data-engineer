# Méthode de Veille — RSS, Feedly, Workflow de lecture et Prise de notes

## Introduction

Avoir de bonnes sources ne suffit pas. Sans méthode, l'information s'accumule, devient anxiogène et finit par être ignorée. Ce fichier décrit un workflow pratique pour transformer un flux d'information brut en veille utile et actionnable.

---

## Le problème : le syndrome de l'information overdose

Sans organisation, voici ce qui arrive :
- Vous vous abonnez à 15 newsletters → votre boîte mail déborde
- Vous suivez 200 comptes sur LinkedIn → le feed est du bruit
- Vous avez 500 onglets ouverts "à lire plus tard" → vous ne les lisez jamais
- Vous passez 2h à "faire de la veille" → vous retenez 2 idées

Le résultat : vous êtes **informé** mais pas **renseigné**. La quantité remplace la qualité.

**La solution** : un système clair avec des entrées limitées, un workflow de traitement, et une sortie (notes, rapport) qui force la synthèse.

---

## Architecture d'un système de veille efficace

```
SOURCES               AGRÉGATEUR          TRAITEMENT           SORTIE
─────────             ──────────          ──────────           ──────
Flux RSS         →    Feedly / Inoreader  →  Lecture rapide  → Notes Obsidian/Notion
Newsletters      →    Boîte dédiée        →  Sélection       → Tags
GitHub Trending  →    (visite hebdo)      →  Résumé LLM      → Rapport mensuel
Podcasts         →    App podcast         →  Écoute active   → Fiche thème
Conférences      →    YouTube (playlist)  →  Prise de notes  → Présentation équipe
```

---

## Outil 1 : Feedly — Agrégateur RSS

### Qu'est-ce qu'un flux RSS ?

RSS (Really Simple Syndication) est un format de flux standardisé qui permet de s'abonner aux mises à jour d'un site sans le visiter. Presque tous les blogs techniques, sites d'actualités et plateformes de documentation proposent un flux RSS.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir Feedly (feedly.com) → créer un compte → ajouter un feed RSS en tapant une URL de blog (ex: netflixtechblog.com) → montrer comment les articles s'affichent → créer un "Board" (dossier) "Data Engineering" → y ajouter plusieurs blogs → montrer la vue "Today" et la vue par board → expliquer le mode de lecture "Save for later".
> **Expliquer :** Insister sur la différence entre suivre un blog par RSS (on choisit et on lit quand on veut) vs recevoir une newsletter (l'auteur envoie quand il veut). Montrer comment Feedly agrège 50 sources en un seul endroit sans polluer la boîte mail.
---

### Configuration Feedly pour un data engineer

**Étape 1 : Créer des Boards (dossiers)**
```
Boards recommandés :
├── Data Engineering         ← Spark, dbt, Airflow, Kafka...
├── LLM & IA                 ← Papers, outils, use cases
├── Cloud                    ← AWS/Azure/GCP annonces
├── Architecture Systèmes    ← Design patterns, scalabilité
└── Industrie & Carrière     ← Tendances marché, recrutement
```

**Étape 2 : Ajouter des flux RSS**

```
# Flux RSS à ajouter dans Feedly (exemples)

Data Engineering :
  https://netflixtechblog.com/feed
  https://eng.uber.com/feed
  https://www.dataengineeringweekly.com/feed
  https://medium.com/feed/airbnb-engineering
  https://engineering.linkedin.com/blog.rss

LLM & IA :
  https://huggingface.co/blog/feed.xml
  https://bair.berkeley.edu/blog/feed.xml
  https://www.deeplearning.ai/the-batch/feed/
  https://lilianweng.github.io/feed.xml

Cloud :
  https://aws.amazon.com/blogs/aws/feed/
  https://azure.microsoft.com/en-us/blog/feed/
  https://cloud.google.com/blog/rss

Architecture :
  https://martinfowler.com/feed.atom
  https://blog.bytebytego.com/feed
```

**Étape 3 : Configurer les alertes**
- Feedly Pro permet de créer des alertes sur des mots-clés (ex: "Apache Iceberg", "vector database")
- La version gratuite suffit pour commencer

### Workflow de lecture Feedly

```
LUNDI MATIN (30 minutes)
├── Ouvrir Feedly
├── Parcourir "Today" : lire les titres
│   ├── Si titre intéressant → lire l'intro (30 sec)
│   │   ├── Si article utile → sauvegarder dans "Read Later"
│   │   └── Si non pertinent → marquer comme lu
│   └── Vider le board "Today"
└── Optionnel : lire immédiatement les 2-3 articles sauvegardés

MERCREDI OU VENDREDI (45 minutes)
├── Lire les articles "Read Later" sauvegardés
├── Pour chaque article lu :
│   ├── Prendre des notes dans Obsidian/Notion (5-10 lignes)
│   └── Ajouter les tags pertinents
└── Vider "Read Later" (même si certains ne sont pas lus)
```

---

## Outil 2 : Boîte mail dédiée pour les newsletters

Ne mélangez pas vos newsletters de veille avec votre boîte mail professionnelle. Créez une adresse dédiée (ex: `votrenom.veille@gmail.com`) pour :
- Séparer le signal (veille) du bruit (email professionnel)
- Pouvoir consulter la veille en bloc sur un créneau dédié
- Éviter la dispersion pendant le travail

### Traitement des newsletters

```
1x par semaine : "Newsletter Morning" (15-20 minutes)
├── Ouvrir la boîte dédiée
├── Parcourir les newsletters reçues
├── Pour chaque newsletter :
│   ├── Lire les titres / résumés
│   ├── Cliquer sur les 1-2 liens vraiment pertinents
│   └── Marquer comme lus (ne pas garder les non-lus indéfiniment)
└── Copier les liens intéressants dans Notion/Obsidian pour lecture ultérieure
```

---

## Outil 3 : Obsidian — Prise de notes et gestion des connaissances

**Obsidian** ([obsidian.md](https://obsidian.md)) est un outil de notes local, basé sur des fichiers Markdown, avec des liens entre notes (graph de connaissance). Il est particulièrement adapté à la veille technologique car :
- Les notes restent locales (pas de dépendance à un cloud tiers)
- Les liens `[[bidirectionnels]]` connectent les idées entre elles
- Le format Markdown est portable et versionnable (git)

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir Obsidian → montrer un vault de veille existant → créer une nouvelle note "Apache Iceberg vs Delta Lake" → ajouter des tags `#open-table-format #data-lake #veille` → créer un lien vers une note existante sur Delta Lake → afficher le graph view montrant les connexions entre notes → montrer la fonctionnalité "Daily Note" pour le journal de veille.
> **Expliquer :** Insister sur l'idée que la valeur est dans les connexions entre les notes, pas dans les notes elles-mêmes. Une note isolée a peu de valeur ; une note liée à 5 autres est un nœud de connaissance. Montrer comment retrouver rapidement une info avec Cmd+O (quick open).
---

### Structure de vault Obsidian pour la veille

```
vault-veille/
├── _daily/              ← Journal quotidien (Daily Notes)
│   ├── 2025-03-01.md
│   └── 2025-03-08.md
├── technologies/        ← Une note par technologie
│   ├── apache-kafka.md
│   ├── dbt.md
│   ├── langchain.md
│   └── pgvector.md
├── articles/            ← Notes de lecture d'articles
│   ├── 2025-02-netflix-data-mesh.md
│   └── 2025-03-bytebytego-raft.md
├── rapports/            ← Rapports de veille finalisés
│   └── 2025-Q1-veille-llm.md
└── templates/           ← Templates de notes
    ├── tech-note.md
    └── article-note.md
```

### Template de note technologie

```markdown
# [Nom de la technologie]

**Date de découverte** : {{date}}
**Catégorie** : #data-engineering / #llm / #cloud / #mlops
**Statut personnel** : #a-explorer / #en-cours / #maîtrisé / #obsolète

## Qu'est-ce que c'est ?
(2-3 phrases)

## Problème résolu
(Quel problème ça résout, dans quel contexte)

## Acteurs principaux
- Créé par :
- Maintenu par :
- Version stable actuelle :

## Alternatives
- Vs [[outil-concurrent-1]] : ...
- Vs [[outil-concurrent-2]] : ...

## Sources
- [Documentation officielle](url)
- [Article de découverte](url)
- [Repo GitHub](url)

## Notes personnelles
(Observations, expériences, questions ouvertes)

## Liens vers d'autres notes
- [[thème-connexe-1]]
- [[projet-qui-utilise-cet-outil]]
```

### Template de note d'article

```markdown
# [Titre de l'article]

**Source** : [Blog / Newsletter / Conférence]
**Auteur** :
**Date de publication** :
**Date de lecture** : {{date}}
**Tags** : #veille #[catégorie] #[technologie]

## Résumé en 3 points
1.
2.
3.

## Citation ou insight clé
> "..."

## Ce que j'ai retenu
(Ce qui est utile pour mon travail actuel ou futur)

## Actions à faire
- [ ] Tester [outil mentionné]
- [ ] Partager à l'équipe
- [ ] Creuser [concept non compris]

## Lien
[Lire l'article original](url)
```

---

## Alternative : Notion

Si vous préférez un outil cloud, **Notion** ([notion.so](https://notion.so)) offre une expérience similaire avec des bases de données.

### Structure Notion pour la veille

```
Base de données "Tech Watch"
Propriétés :
├── Nom (titre)
├── Source (sélection : GitHub / HN / Newsletter / Podcast)
├── Catégorie (multi-sélection : Data / IA / Cloud / DevOps...)
├── Statut (sélection : Lu / En cours / A lire)
├── Date
├── Tags (multi-sélection)
├── Score (note 1-5 : valeur de l'article)
└── Actions (checkbox : Partagé équipe / Testé / Noté rapport)

Vues :
├── All (liste complète)
├── A lire cette semaine (filtre Statut = "A lire")
├── High value (filtre Score >= 4)
└── By category (groupé par Catégorie)
```

---

## Workflow de veille hebdomadaire — Vue d'ensemble

```
LUNDI (30 min)
├── Feedly : parcourir Today, sauvegarder les intéressants
└── Emails newsletters : identifier les 2-3 liens à garder

MERCREDI (30 min)
├── Lire les articles sauvegardés Feedly
├── GitHub Trending : 10 minutes de navigation
└── Prendre des notes Obsidian sur ce qui a été lu

VENDREDI (15 min)
├── Hacker News : top of the week
└── Optionnel : épisode de podcast

FIN DE MOIS (1-2h)
├── Rédiger le rapport de veille mensuel
├── Mettre à jour le tech radar personnel
└── Partager les 3 insights clés avec l'équipe
```

---

## Le Tech Radar personnel

Le **Tech Radar** (popularisé par ThoughtWorks) est un document qui catégorise les technologies selon 4 quadrants et 4 anneaux :

**Quadrants :**
- Techniques & Outils
- Plateformes
- Langages & Frameworks
- Data & IA

**Anneaux :**
- **Adopt** : À utiliser en production, maturité prouvée
- **Trial** : En cours d'évaluation, tests concluants
- **Assess** : À surveiller, pas encore évalué en profondeur
- **Hold** : À ne pas adopter (pour l'instant), ou à abandonner progressivement

### Votre tech radar au format Markdown

```markdown
# Tech Radar Personnel — Q1 2025

## ADOPT (j'utilise en production / je recommande)
- Python 3.12
- dbt Core
- Apache Airflow
- PostgreSQL + pgvector
- Docker + Docker Compose
- FastAPI
- Git + GitHub Actions

## TRIAL (en cours d'évaluation)
- Apache Iceberg
- DuckDB
- LangGraph (agents)
- uv (gestionnaire de paquets Python)

## ASSESS (à surveiller, pas encore évalué)
- Apache Polars
- Modal (serverless Python)
- Marimo (notebooks réactifs)
- Weaviate (vector DB)

## HOLD (ne pas adopter actuellement)
- Apache Spark (pour les petits volumes : overkill)
- Jupyter Notebooks en production
- PyMongo (préférer Motor pour l'async)
```

Mettez à jour ce document chaque trimestre. Les changements d'un trimestre à l'autre racontent l'histoire de votre évolution technique.

---

## Gérer la FOMO (Fear Of Missing Out)

La FOMO technologique est réelle : l'impression que si vous ne suivez pas tout, vous allez rater quelque chose d'important.

### Antidotes à la FOMO tech

1. **Acceptez que vous raterez toujours quelque chose.** Le volume d'information est trop grand pour une seule personne. L'objectif n'est pas la complétude.

2. **Les vraies ruptures durent.** Une vraie technologie disruptive restera visible pendant 6-18 mois avant d'être adoptée massivement. Vous aurez le temps.

3. **La profondeur bat la largeur.** Maîtriser 5 outils en profondeur vaut mieux que connaître superficiellement 50 outils.

4. **Faites confiance à votre réseau.** Si quelque chose de vraiment important émerge, un collègue ou une source fiable vous l'apportera.

---

## Ressources

- Obsidian : [https://obsidian.md](https://obsidian.md)
- Feedly : [https://feedly.com](https://feedly.com)
- Inoreader (alternative à Feedly) : [https://www.inoreader.com](https://www.inoreader.com)
- ThoughtWorks Tech Radar : [https://www.thoughtworks.com/radar](https://www.thoughtworks.com/radar)
- Outil pour créer votre propre tech radar : [https://radar.thoughtworks.com](https://radar.thoughtworks.com)
