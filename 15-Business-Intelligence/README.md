# Formation Business Intelligence — Data Analyst

## Présentation

La **Business Intelligence (BI)** regroupe les méthodes et les outils qui transforment les données brutes d'une organisation en informations exploitables pour la décision : recueil du besoin métier, collecte, nettoyage, modélisation, analyse et restitution sous forme de tableaux de bord.

Ce module couvre le cœur du métier de **Data Analyst** tel que défini par le titre **RNCP-38616** (Concepteur développeur en IA et analyse big data — option Data Analyse), et en particulier le bloc **BC06 — Analyser des données et concevoir des tableaux de bord**. Il progresse des fondamentaux du métier jusqu'au tableau de bord de niveau expert et à la préparation de la certification.

---

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Comprendre le métier de Data Analyst, son référentiel (RNCP-38616) et sa posture professionnelle
- Recueillir un besoin métier et le traduire en problématique data et en indicateurs (KPI, objectifs SMART)
- Mener une analyse exploratoire (EDA) avec pandas et analyser tendances et séries temporelles
- Modéliser des données en **schéma en étoile** et préparer les données avec **Power Query**
- Concevoir des mesures **DAX** et des visualisations avancées, interactives et accessibles (WCAG)
- Garantir la conformité **RGPD** d'un projet data et prévenir les biais dans les analyses
- Concevoir un processus de **collecte de données** et automatiser des pipelines **ETL**
- Appliquer des stratégies de **nettoyage** (valeurs manquantes, valeurs aberrantes)
- Construire un **tableau de bord expert** et accompagner son adoption par les équipes métier
- Préparer la **certification BC06** : portfolio, dossier de projet, soutenance

---

## Prérequis

- Bases de Python (pandas) — voir [01-Fondamentaux/Python](../01-Fondamentaux/Python/)
- Notions de SQL (jointures, clés) — voir [01-Fondamentaux/SQL](../01-Fondamentaux/SQL/)
- Un tableur (Excel, Google Sheets ou LibreOffice Calc)
- Power BI Desktop installé (à partir des modules sur les dashboards)
- Aucune connaissance préalable en BI n'est nécessaire pour démarrer

---

## Structure de la formation

```
15-Business-Intelligence/
├── README.md                              ← Ce fichier
├── 01-Metier-Data-Analyst/                ← Métier, référentiel RNCP-38616, posture, méthode & veille
├── 02-Panorama-Outils-BI/                 ← Installation des outils, panorama SQL / Python / Power BI / Looker Studio / Tableau
├── 03-Analyse-Besoin-Metier/              ← Recueil du besoin métier, formalisation d'une problématique
├── 04-Analyse-Exploratoire-EDA/           ← Analyse exploratoire des données avec pandas
├── 05-Tendances-Series-Temporelles/       ← Analyse de tendances, séries temporelles
├── 06-KPI-Indicateurs/                    ← KPI, objectifs SMART
├── 07-Dashboards-Fondamentaux/            ← Construire un premier tableau de bord
├── 08-Restitution-Storytelling/           ← Restituer & présenter les résultats
├── 09-Modelisation-Etoile-PowerQuery/     ← Modèle en étoile, granularité, relations, Power Query
├── 10-DAX/                                ← Mesures DAX, contexte de filtre, Time Intelligence
├── 11-Visualisations-Avancees/            ← Drill-down, interactivité, accessibilité WCAG
├── 12-Ethique-Biais-RGPD/                 ← RGPD, éthique, biais des données
├── 13-Accompagnement-Metier/              ← Conduite du changement, adoption par les équipes métier
├── 14-Collecte-Donnees/                   ← Processus de collecte, RGPD by design
├── 15-ETL-Automatisation/                 ← Pipelines ETL, automatisation de la collecte
├── 16-Nettoyage-Donnees/                  ← Valeurs manquantes, valeurs aberrantes
├── 17-Dashboard-Expert/                   ← Tableau de bord BI niveau expert (niveau 3)
└── 18-Preparation-Certification/          ← Révisions, portfolio, dossier de projet, soutenance BC06
```

---

## Les 18 sous-modules

| # | Sous-module | Contenu | Compétences RNCP |
|---|---|---|---|
| 01 | [Metier-Data-Analyst](01-Metier-Data-Analyst/) | Le métier de Data Analyst, le référentiel RNCP-38616, la posture professionnelle, méthode & veille | Référentiel RNCP-38616 |
| 02 | [Panorama-Outils-BI](02-Panorama-Outils-BI/) | Installation des outils, panorama SQL / Python / Power BI / Looker Studio / Tableau | — (outillage, socle) |
| 03 | [Analyse-Besoin-Metier](03-Analyse-Besoin-Metier/) | Recueil du besoin métier, formalisation d'une problématique | **C11** (niveau 1→3) |
| 04 | [Analyse-Exploratoire-EDA](04-Analyse-Exploratoire-EDA/) | Analyse exploratoire des données (EDA) avec pandas | **C4, C5** (niveau 1) |
| 05 | [Tendances-Series-Temporelles](05-Tendances-Series-Temporelles/) | Analyse de tendances, séries temporelles | **C6** (niveau 1) |
| 06 | [KPI-Indicateurs](06-KPI-Indicateurs/) | Définir des KPI pertinents, objectifs SMART | **C16** (niveau 1→2) |
| 07 | [Dashboards-Fondamentaux](07-Dashboards-Fondamentaux/) | Construire un premier tableau de bord | **C17, C18** (niveau 1→2) |
| 08 | [Restitution-Storytelling](08-Restitution-Storytelling/) | Restituer et présenter les résultats d'une analyse | **C15** (niveau 1→3), **C17** |
| 09 | [Modelisation-Etoile-PowerQuery](09-Modelisation-Etoile-PowerQuery/) | Table de faits et dimensions, granularité, schéma en étoile, relations Power BI, table de dates | C18 (BC06) |
| 10 | [DAX](10-DAX/) | Mesures DAX, colonnes calculées, contexte de filtre, CALCULATE, Time Intelligence | C18 (BC06) |
| 11 | [Visualisations-Avancees](11-Visualisations-Avancees/) | Drill-down, hiérarchies, interactivité, infobulles, accessibilité WCAG | C17 (niveau 2) |
| 12 | [Ethique-Biais-RGPD](12-Ethique-Biais-RGPD/) | RGPD appliqué au projet data, éthique, biais des données | C12 (niveau 1) |
| 13 | [Accompagnement-Metier](13-Accompagnement-Metier/) | Accompagner une équipe métier : conduite du changement, adoption, cahier des charges | C11 (niveau 2), C15 (niveau 2) |
| 14 | [Collecte-Donnees](14-Collecte-Donnees/) | Concevoir un processus de collecte de données, RGPD by design | C1 (niveau 1) |
| 15 | [ETL-Automatisation](15-ETL-Automatisation/) | Automatiser la collecte : pipelines ETL, extraction et préparation des données | C2 (niveau 1) |
| 16 | [Nettoyage-Donnees](16-Nettoyage-Donnees/) | Stratégies de nettoyage : valeurs manquantes, valeurs aberrantes | C3 (niveau 1) |
| 17 | [Dashboard-Expert](17-Dashboard-Expert/) | Tableau de bord BI de niveau expert : conception complète, interactivité, accessibilité | C16, C17, C18 (niveau 3) |
| 18 | [Preparation-Certification](18-Preparation-Certification/) | Préparer la certification BC06 : révisions, portfolio, dossier de projet, soutenance | C16, C17, C18 (niveau 3) |

---

## Parcours conseillé

1. **Fondamentaux du métier et de l'analyse** (01 → 08) : découverte du métier, des outils, du besoin métier, de l'EDA et de la restitution.
2. **BI avancée** (09 → 13) : modélisation en étoile, DAX, visualisations avancées, conformité et accompagnement métier.
3. **Flux de données & certification** (14 → 18) : collecte, ETL, nettoyage, dashboard expert et préparation de la certification BC06.

Ce module s'inscrit dans le parcours complet du Data Analyst : voir [PATH_DATA_ANALYST.md](../PATH_DATA_ANALYST.md) à la racine du dépôt.

---

## Durée estimée (modules 09 à 18)

| Sous-module | Durée |
|---|---|
| 09 — Modélisation en étoile & Power Query | ~30 h |
| 10 — DAX & mesures avancées | ~35 h |
| 11 — Visualisations avancées & interactivité | ~25 h |
| 12 — RGPD, éthique & biais | ~20 h |
| 13 — Accompagnement métier | ~25 h |
| 14 — Processus de collecte | ~22 h |
| 15 — ETL & automatisation | ~30 h |
| 16 — Nettoyage de données | ~25 h |
| 17 — Dashboard expert | ~35 h |
| 18 — Préparation certification | ~20 h |
| **Total (09-18)** | **~267 h** |

Les durées des modules 01 à 08 sont indiquées dans leurs fichiers respectifs.

---

## Liens avec les autres modules du dépôt

- Modélisation dimensionnelle côté Data Engineering : [05-Databases/DataWarehouse](../05-Databases/DataWarehouse/)
- Socle RGPD & gouvernance des données : [01-Fondamentaux/RGPD-Gouvernance](../01-Fondamentaux/RGPD-Gouvernance/)
- Orchestration de pipelines : [06-Data-Engineering/Airflow](../06-Data-Engineering/Airflow/)
- Transformations SQL industrialisées : [06-Data-Engineering/Dbt](../06-Data-Engineering/Dbt/)

---

## Ressources complémentaires

- [Fiche RNCP-38616 — France Compétences](https://www.francecompetences.fr/recherche/rncp/38616/)
- [Documentation Power BI (Microsoft Learn)](https://learn.microsoft.com/fr-fr/power-bi/)
- [DAX Guide (SQLBI)](https://dax.guide/)
- [Looker Studio](https://cloud.google.com/looker-studio)
- [CNIL — RGPD](https://www.cnil.fr/fr/reglement-europeen-protection-donnees)
