# Conformité RNCP-38616 — Parcours Data Analyst (option Data Analyse)

Cette note relie les **18 compétences** de la certification aux contenus du dépôt.
L'option Data Analyse couvre le tronc commun **BC01→BC04** + l'option **BC06** (Business
Intelligence). Le bloc **BC05** (Data Science / Deep Learning) est hors périmètre.

> **Contexte.** Le parcours Data Analyst a été conçu à l'origine comme un dépôt autonome dont
> le rapport de conformité signalait trois manques : Machine Learning (BC03), gestion de
> projet & veille (BC04) et accessibilité WCAG (C6/C17). En l'intégrant **dans cette
> plateforme**, deux de ces manques sont **déjà couverts par des modules existants** ; seul
> le volet WCAG reste à intégrer dans les modules de dataviz.

---

## Matrice de couverture

| Bloc | Comp. | Exigence | Couverture dans ce dépôt | Statut |
|---|---|---|---|:--:|
| **BC01** | C1 | Concevoir la collecte (RGPD by design) | [15-BI/14-Collecte-Donnees](14-Collecte-Donnees/) | ✅ |
| | C2 | ETL / automatisation | [15-BI/15-ETL-Automatisation](15-ETL-Automatisation/) | ✅ |
| | C3 | Nettoyage (manquants, aberrants) | [15-BI/16-Nettoyage-Donnees](16-Nettoyage-Donnees/) | ✅ |
| **BC02** | C4 | Extraire SQL / Python multi-sources | [SQL/09-Extraction-Analyse](../01-Fondamentaux/SQL/09-Extraction-Analyse/) + 15-BI/04 | ✅ |
| | C5 | EDA & stats descriptives | [Mathématiques/03-Statistiques](../01-Fondamentaux/Mathematiques/) + 15-BI/04 | ✅ |
| | C6 | Tendances **+ accessibilité WCAG** | [15-BI/05](05-Tendances-Series-Temporelles/) (tendances) + WCAG dans [module 11](11-Visualisations-Avancees/) | ✅ |
| **BC03** | C7 | Sélectionner un algorithme ML | [08-ML/cours/09-modeles-lineaires, 10-arbres-forets, 11-boosting](../08-Machine-Learning/) | ✅ |
| | C8 | Preprocessing ML | [08-ML/cours/06-comprendre-donnees, 07-feature-engineering](../08-Machine-Learning/) | ✅ |
| | C9 | Entraîner & évaluer (loss, métriques, overfitting) | [08-ML/cours/04, 12-metriques, 13-validation](../08-Machine-Learning/) | ✅ |
| **BC04** | C10 | Veille IA / Big Data | [01-Fondamentaux/Veille-Technologique](../01-Fondamentaux/Veille-Technologique/) | ✅ |
| | C11 | Problématique métier (cahier des charges) | 15-BI/03 + [11-Gestion-Projet/02](../11-Gestion-Projet/) | ✅ |
| | C12 | Risques éthique / RGPD / environnement | [15-BI/12-Ethique-Biais-RGPD](12-Ethique-Biais-RGPD/) | ✅ |
| | C13 | Planifier ressources / délais / budgets | [11-Gestion-Projet/01, 04-RICE, 05-faisabilité](../11-Gestion-Projet/) | ✅ |
| | C14 | Piloter une équipe (agile) | [11-Gestion-Projet/03-methodes-agiles](../11-Gestion-Projet/) | ✅ |
| | C15 | Présenter les résultats (WCAG) | [15-BI/13-Accompagnement-Metier](13-Accompagnement-Metier/) + module 08 | ✅ |
| **BC06** | C16 | Identifier les KPI selon le besoin | [15-BI/06-KPI-Indicateurs](06-KPI-Indicateurs/) | ✅ |
| | C17 | Choisir les visualisations **+ WCAG** | [15-BI/07](07-Dashboards-Fondamentaux/) + WCAG dans [module 11](11-Visualisations-Avancees/) & [17](17-Dashboard-Expert/) | ✅ |
| | C18 | Créer des dashboards BI (Power BI / Looker) | [15-BI/09-Modelisation](09-Modelisation-Etoile-PowerQuery/) + 10, 17 | ✅ |

---

## Accessibilité WCAG (C6, C17) — couverte

Le référentiel exige explicitement les critères **WCAG 1.4.1 (usage de la couleur)** et
**1.4.4 (redimensionnement du texte)**. L'accessibilité est traitée en **contexte dataviz** dans :

- **[11-Visualisations-Avancees](11-Visualisations-Avancees/)** — palettes sûres pour daltoniens
  (Okabe-Ito, ColorBrewer), contraste ≥ 4,5:1, ne pas coder l'information par la seule couleur,
  alt text, ordre de tabulation, thèmes Power BI « Accessible ».
- **[17-Dashboard-Expert](17-Dashboard-Expert/)** — checklist d'accessibilité appliquée au tableau
  de bord final de niveau expert.

Un socle transverse existe par ailleurs côté projet
([11-Gestion-Projet/07-accessibilite-eco-conception](../11-Gestion-Projet/) — RGAA / WCAG 2.1).

---

## Numérotation activités ↔ blocs

Rappel utile pour éviter les confusions : dans le parcours officiel, l'activité **A5**
correspond au bloc **BC06** (décalage de numérotation sans conséquence). Les modalités
d'évaluation retenues pour un Data Analyst sont : blocs **1, 2, 3, 6** = cas pratique ;
bloc **4** = présentation orale au jury.
