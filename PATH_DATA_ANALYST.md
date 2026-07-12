# 📊 Parcours : Data Analyst

[🏠 Retour à l'accueil](README.md)

Ce parcours prépare au métier de **Data Analyst** et à la certification **RNCP-38616**
(*Concepteur développeur en IA et analyse big data*), **option Data Analyse — bloc BC06 :
Concevoir des tableaux de bord avancés (Business Intelligence)**.

Le Data Analyst fait le lien entre les métiers et les données : il **recueille un besoin**,
**collecte**, **nettoie**, **analyse** et surtout **restitue la donnée sous forme de
tableaux de bord** pour éclairer la décision. L'essentiel du contenu est dans le module
**[15-Business-Intelligence](15-Business-Intelligence/)**, complété par les mathématiques,
le SQL et des ponts vers le ML et la gestion de projet.

> Format de référence : **7 mois intensifs · 980 h · 28 semaines** (35 h/sem). La période
> d'alternance (12 mois) est hors périmètre de ce parcours.

---

## 📅 Timeline de Formation (28 semaines)

### 🌱 Phase 0 : La Prairie — découvrir le métier (S1-S3 · 98 h)
*Objectif : comprendre le métier, la posture et les outils, sans coder.*
- [ ] [Métier de Data Analyst & référentiel RNCP-38616](15-Business-Intelligence/01-Metier-Data-Analyst/)
- [ ] [Panorama & installation des outils BI](15-Business-Intelligence/02-Panorama-Outils-BI/) (SQL, Python, Power BI, Looker Studio, Tableau) — dont [initiation à Python](15-Business-Intelligence/02-Panorama-Outils-BI/03-initiation-python.md)
- [ ] [Recueillir & formaliser un besoin métier](15-Business-Intelligence/03-Analyse-Besoin-Metier/)
- [ ] 🎯 **[Brief 0 — Répliquer un dashboard (Looker Studio)](99-Brief/Data-Analyst/BRIEF_0_PRAIRIE.md)** (S2)

### 🧮 Phase Maths & Python (S4-S5 · 70 h)
*Objectif : sécuriser le socle statistique de l'analyse.*
- [ ] [Mathématiques : arithmétique, algèbre, **statistiques descriptives**, probabilités, stats inférentielle, maths pour la dataviz](01-Fondamentaux/Mathematiques/)

### 🟢 Phase 1 : Ajuster & analyser un tableau de bord métier (S6-S10 · 175 h)
*Objectif : de l'extraction à la restitution d'un premier tableau de bord (niveau 1→2).*
- [ ] [SQL d'extraction & d'analyse](01-Fondamentaux/SQL/09-Extraction-Analyse/)
- [ ] [Analyse exploratoire (EDA) avec pandas](15-Business-Intelligence/04-Analyse-Exploratoire-EDA/)
- [ ] [Tendances & séries temporelles](15-Business-Intelligence/05-Tendances-Series-Temporelles/)
- [ ] [KPI & structuration du tableau de bord](15-Business-Intelligence/06-KPI-Indicateurs/)
- [ ] [Construire un premier dashboard](15-Business-Intelligence/07-Dashboards-Fondamentaux/) · [Restituer & storytelling](15-Business-Intelligence/08-Restitution-Storytelling/)
- [ ] 🎯 **[Brief 1 — Tableau de bord de monitorage métier](99-Brief/Data-Analyst/BRIEF_1_TABLEAU_DE_BORD_METIER.md)** (S9)

### 🟡 Phase 2 : Solution BI avancée (S11-S17 · 245 h)
*Objectif : modélisation, DAX, visualisations avancées et conformité (niveau 2).*
- [ ] [Statistiques descriptives appliquées](15-Business-Intelligence/04-Analyse-Exploratoire-EDA/02-statistiques-appliquees.md)
- [ ] [Modélisation en étoile & Power Query](15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/)
- [ ] [Mesures DAX & Time Intelligence](15-Business-Intelligence/10-DAX/)
- [ ] [Visualisations avancées, interactivité & **accessibilité WCAG**](15-Business-Intelligence/11-Visualisations-Avancees/)
- [ ] [RGPD, éthique & biais](15-Business-Intelligence/12-Ethique-Biais-RGPD/) · [Accompagner le métier](15-Business-Intelligence/13-Accompagnement-Metier/)
- [ ] 🎯 **[Brief 2 — Solution BI avancée (modèle étoile, DAX)](99-Brief/Data-Analyst/BRIEF_2_SOLUTION_BI_AVANCEE.md)** (S16)

### 🔴 Phase 3 : Flux d'alimentation BI & certification (S18-S28 · 392 h)
*Objectif : collecte, ETL, nettoyage, dashboard expert et préparation BC06 (niveau 3).*
- [ ] [Processus de collecte (RGPD by design)](15-Business-Intelligence/14-Collecte-Donnees/) · [ETL & automatisation](15-Business-Intelligence/15-ETL-Automatisation/)
- [ ] [Nettoyage des données](15-Business-Intelligence/16-Nettoyage-Donnees/) · [Extraction multi-sources (SQL avancé)](01-Fondamentaux/SQL/09-Extraction-Analyse/)
- [ ] [Tableau de bord expert (WCAG, niveau 3)](15-Business-Intelligence/17-Dashboard-Expert/)
- [ ] [Préparation certification : portfolio, dossier, soutenance](15-Business-Intelligence/18-Preparation-Certification/)
- [ ] 🎯 **[Brief 3 — Projet certificatif BC06 (bout en bout)](99-Brief/Data-Analyst/BRIEF_3_CERTIFICATIF_BC06.md)** (S26-28)

> 🗓️ **Rythme hebdomadaire** : chaque semaine, une [mission hebdomadaire](99-Brief/Data-Analyst/missions-hebdo/)
> courte prépare le projet fil rouge de la phase. 22 missions couvrent les 28 semaines
> (voir l'[index des briefs & missions](99-Brief/Data-Analyst/README.md)).

---

## 🧩 Couverture du référentiel (18 compétences)

L'option Data Analyse couvre le tronc commun **BC01→BC04** + l'option **BC06**. Certaines
compétences hors BI s'appuient sur des modules **déjà présents dans ce dépôt** :

| Bloc | Compétences | Couvert par |
| :--- | :--- | :--- |
| **BC06** (option BI) | C16, C17, C18 | [15-Business-Intelligence](15-Business-Intelligence/) (cœur du parcours) |
| **BC01** Collecte/ETL/nettoyage | C1, C2, C3 | 15-BI modules 14-16 |
| **BC02** Analyse & stats | C4, C5, C6 | [Mathématiques](01-Fondamentaux/Mathematiques/) + 15-BI 04-05 |
| **BC03** Machine Learning | C7, C8, C9 | [08-Machine-Learning](08-Machine-Learning/) |
| **BC04** Gestion de projet & veille | C10, C13, C14 | [11-Gestion-Projet](11-Gestion-Projet/) + [Veille-Technologique](01-Fondamentaux/Veille-Technologique/) |
| **BC04** Problématique & restitution | C11, C12, C15 | 15-BI 03, 12, 13 |

> Détail : voir la [note de conformité RNCP-38616](15-Business-Intelligence/CONFORMITE-RNCP.md).

---

## 🎯 Passeport de Compétences

| Domaine | Compétence clé | Livrable attendu |
| :--- | :--- | :--- |
| **Métier & besoin** | Traduire un besoin métier en problématique data et KPI | Cahier des charges + KPI SMART |
| **Analyse** | Mener une EDA et interpréter tendances & stats | Notebook d'analyse (pandas) |
| **Modélisation BI** | Concevoir un modèle en étoile + mesures DAX | Modèle Power BI + mesures |
| **Restitution** | Concevoir un tableau de bord accessible (WCAG) | Dashboard interactif |
| **Flux de données** | Automatiser collecte, ETL et nettoyage | Pipeline d'alimentation documenté |
| **Conformité** | Garantir RGPD & prévenir les biais | Registre de traitements + note éthique |

---

## 🎓 Évaluation : le Projet Certificatif
Pour valider le bloc **BC06**, vous réalisez un tableau de bord BI de bout en bout :
👉 **[Brief 3 — Projet certificatif BC06](99-Brief/Data-Analyst/BRIEF_3_CERTIFICATIF_BC06.md)**
(collecte → nettoyage → modélisation → dashboard expert → soutenance).

---

## 🛠️ Outils enseignés
**SQL** · **Python** (pandas, numpy, matplotlib, seaborn) · **Power BI** (Power Query + DAX,
prioritaire dans le retail) · **Looker Studio** (cross-OS, confort Mac) · **Tableau Public** /
**Metabase** (optionnels) · **Excel / Google Sheets**.

---
[🏠 Retour à l'accueil](README.md)
