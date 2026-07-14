# Étude de marché — Outils de Data Visualization / BI pour la formation Data Analyst
### Focus : marché national français & Hauts-de-France · contrainte multi-OS (formateur Mac)
*Date : juin 2026 · Étude documentaire pour le choix des outils à enseigner*

---

## 1. Résumé exécutif

- **Power BI est l'outil n°1 du marché de l'emploi data en France** en 2025-2026, à la fois en parts de marché logiciel (~23 % du marché BI mondial, devant Tableau ~17-18 %) et en nombre d'offres d'emploi citant l'outil. Microsoft Power BI est positionné « Leader » au Magic Quadrant Gartner Analytics & BI 2024 et 2025.
- **Tableau reste le solide n°2**, surtout dans les grands comptes, le conseil et les ESN. La France est l'un des plus gros marchés Tableau au monde (~12 000 clients).
- **Le socle technique réel d'un data analyst en 2025 = SQL (présent dans ~95 % des offres) + un outil de dataviz (Power BI en tête) + Python.** La dataviz seule ne suffit pas : elle s'enseigne par-dessus SQL/Python.
- **Dans les Hauts-de-France / métropole lilloise**, le tissu économique est dominé par le **retail / e-commerce** (galaxie Mulliez : Auchan, Decathlon, Leroy Merlin/Adeo, Boulanger, Kiabi, Norauto ; + La Redoute, Cofidis, OVHcloud, Vilogia, AG2R). Ce profil **renforce encore la domination de Power BI** (écosystème Microsoft très répandu dans le retail), avec présence de Tableau et de la stack Google (Looker Studio) chez les acteurs e-commerce/marketing.
- **Contrainte Mac confirmée et structurante** : **Power BI Desktop n'existe pas sur macOS ni Linux (Windows-only)**, alors que **Tableau Desktop est nativement Mac + Windows** (mais pas Linux desktop), et que les outils web (Looker Studio, Metabase, Superset) + Python sont **100 % cross-OS**.
- **Recommandation** : enseigner **Power BI en priorité** (employabilité n°1) malgré la contrainte Mac (contournée par Power BI Service web + VM Windows / Parallels côté formateur), **complété par Python (matplotlib/seaborn/plotly) comme socle cross-OS pérenne**, et **un outil web cross-OS** (Looker Studio gratuit, et/ou Metabase open source) pour démontrer la dataviz nativement sur Mac. Tableau Public (gratuit, natif Mac) constitue une introduction optionnelle au n°2 du marché.

---

## 2. Méthodologie

- **Approche** : étude documentaire (desk research) via 10 requêtes web croisées (avril-juin 2026), priorisant les sources 2025-2026.
- **Sources mobilisées** : agrégateurs d'offres (Indeed, LinkedIn, Glassdoor, APEC, Welcome to the Jungle, Hellowork, Meteojob), études de parts de marché (6sense, comparatifs BI), documentation éditeurs (Tableau techspecs, Microsoft Power BI, Looker Studio), presse spécialisée FR (Jedha, Stage.fr, ScreeningPass), presse économique régionale (Le Journal des Entreprises).
- **Limites & honnêteté méthodologique** :
  - Les agrégateurs d'offres ne publient pas de ventilation officielle « % d'offres citant Power BI vs Tableau ». Les proportions citées sont **des tendances convergentes issues de plusieurs sources**, pas un comptage exhaustif.
  - Les volumes d'offres (« 25+ », « 100+ ») sont des **ordres de grandeur** affichés par Indeed à une date donnée, qui varient dans le temps.
  - Distinction explicite ci-dessous entre **[SOURCÉ]** (chiffre/fait issu d'une source) et **[ESTIMATION]** (analyse/déduction de l'auteur).
  - **Absence de données primaires** : cette étude repose **exclusivement sur des sources secondaires** (offres en ligne, études de marché, documentation éditeurs, presse). **Aucun entretien direct** n'a été mené avec des **recruteurs / responsables data du bassin Hauts-de-France**, des **anciens apprenants (alumni)** ou des **entreprises locales**. Les constats sur les outils réellement utilisés en poste, les attentes en entretien et l'adéquation formation/emploi restent donc **déduits des annonces**, pas vérifiés sur le terrain.

- **Recommandation pour compléter l'étude (données primaires)** : pour renforcer la validité des conclusions, mener une courte phase qualitative :
  - **3 à 5 entretiens semi-directifs avec des recruteurs / managers data** d'employeurs du bassin (retail/distribution Mulliez, e-commerce, ESN d'EuraTechnologies, OVHcloud) — questions : outils réellement utilisés, niveau attendu sur Power BI/Tableau, importance de SQL/Python à l'embauche.
  - **Sondage des alumni** de la formation déjà en poste (questionnaire court : outil principal utilisé au quotidien, écart ressenti avec la formation, ce qu'ils auraient voulu apprendre davantage).
  - **Échange avec 1-2 ESN / agences data locales** (ex. Cenisis) sur la stack demandée par leurs clients.
  - Ces données primaires permettraient de **confirmer ou nuancer** la hiérarchie des outils et la grille de décision pondérée (§6), et de **calibrer les pondérations** sur des retours terrain plutôt que sur les seules annonces.

---

## 3. Marché national français (2025-2026)

### 3.1 Hiérarchie des outils demandés

| Rang | Outil | Statut sur le marché FR | Type de demande |
|------|-------|------------------------|-----------------|
| 1 | **Power BI** | Dominant, surtout grands comptes & PME Microsoft | Le plus cité dans les offres data analyst |
| 2 | **Tableau** | Fort en ESN, conseil, grands comptes, e-commerce | Souvent demandé en binôme « Power BI/Tableau » |
| 3 | **SQL** (transversal) | Incontournable — n'est pas un outil de viz mais le prérequis | ~95 % des offres |
| 4 | **Python** (matplotlib/seaborn/plotly) | Standard pour manipulation + viz programmatique | Très fréquent, souvent « + » |
| 5 | **Looker Studio** (ex-Google Data Studio) | Répandu en marketing / web analytics / e-commerce | Fréquent en complément |
| 6 | **Qlik / QlikView / Qlik Sense** | Historique, en recul mais présent | Niche grands comptes |
| 7 | **Metabase / Superset** | En croissance côté start-up / scale-up / tech | Émergent |
| 8 | **Excel** | Toujours omniprésent comme outil de base | Quasi systématique (implicite) |

**Faits sourcés :**
- **Parts de marché BI mondial** : Power BI ~**23,2 %** vs Tableau ~**17,7 %** [SOURCÉ — 6sense]. Power BI devant Tableau en 2025.
- **France** : l'un des tout premiers marchés Tableau au monde (~**12 200 clients**, ~16-17 % de la base Tableau) [SOURCÉ — 6sense].
- **Gartner Magic Quadrant Analytics & BI 2024 & 2025** : Power BI = « Leader » [SOURCÉ — Jedha].
- **SQL = compétence n°1**, présente dans **~95 % des offres** data analyst FR [SOURCÉ — mes-formations-data.fr]. Souvent testée en entretien technique.
- Les offres listent fréquemment un **panel** : « Tableau, Looker, Superset, Power BI, Metabase » comme outils interchangeables de dataviz [SOURCÉ — Indeed/datackathon].
- **Croissance du marché** : offres data analyst FR **+35 % en 2024** ; **67 % des entreprises** prévoient d'augmenter leur budget data [SOURCÉ — Stage.fr]. (Note : à interpréter avec prudence, source secondaire.)

### 3.2 Lecture analytique

[ESTIMATION] La combinaison qui maximise l'employabilité nationale d'un futur data analyst est : **SQL (socle) + Power BI (outil n°1 entreprise) + Python (polyvalence/automatisation)**. Tableau est un « plus » différenciant, surtout pour viser les ESN, le conseil et les grands comptes. Looker Studio est un atout pour les profils orientés marketing/web/e-commerce.

---

## 4. Focus Hauts-de-France / Métropole lilloise

### 4.1 Tissu économique : un bassin retail / e-commerce exceptionnel

La région est **structurellement marquée par le commerce et la distribution**, ce qui oriente fortement les outils utilisés.

- **Galaxie Mulliez (Association Familiale Mulliez, siège à Roubaix)** : Auchan, Decathlon, Leroy Merlin/**Adeo**, Boulanger, Kiabi, Norauto, Pimkie… — tous présents dans le top des employeurs régionaux [SOURCÉ — Wikipedia AFM, Le Journal des Entreprises].
- **E-commerce / VAD historique** : **La Redoute** (Roubaix), 3 Suisses historiquement.
- **Banque / crédit** : **Cofidis**, AG2R La Mondiale, Crédit Mutuel/CIC Nord.
- **Tech / cloud** : **OVHcloud** (siège Roubaix) — ~22-25 offres actives Lille/Roubaix dont rôles data [SOURCÉ — Indeed/LinkedIn].
- **Immobilier social / services** : Vilogia, Nhood.
- **Écosystème data local** : **EuraTechnologies** (Lille) — pôle tech majeur ; ESN/agences data comme **Cenisis** y opèrent et listent comme clients **ADEO, AG2R, Cofidis, Decathlon, Leroy Merlin, Nhood, Vilogia** (74 projets data en 2024) [SOURCÉ — Cenisis].

### 4.2 Outils cités dans les offres lilloises

**Faits sourcés :**
- Offres « Data Analyst » à Lille (59) : ordre de grandeur **25-44 offres** selon les plateformes (Indeed, Glassdoor) à un instant T [SOURCÉ].
- Compétences récurrentes dans les offres lilloises : **Power BI (souvent « niveau avancé / expert »), Tableau, SQL, Python, statistiques** [SOURCÉ — Indeed Lille].
- Offres mentionnant explicitement **« dashboards Power BI »** majoritaires parmi les annonces visibles ; mentions Tableau présentes mais moins nombreuses [SOURCÉ — Indeed, première page].
- Postes data orientés **gouvernance / qualité de données / master data** chez les acteurs retail (ex. Cenisis pour des clients retail) [SOURCÉ].

**[ESTIMATION] Lecture régionale :**
- **Power BI domine encore davantage qu'au niveau national** dans le Nord, car l'écosystème Microsoft (Office 365, Azure) est très implanté dans le retail et la distribution — secteurs surreprésentés ici.
- **Looker Studio + Google Analytics** ont une présence notable côté e-commerce / marketing digital (La Redoute, pure players).
- **Tableau** est présent surtout via les grands comptes, les ESN et le conseil.
- **Metabase / Superset** apparaissent côté start-up / scale-up de l'écosystème EuraTechnologies.

**Conclusion régionale** : pour un apprenant visant un premier emploi dans le Nord, **Power BI est le pari le plus sûr**, suivi de SQL/Python comme socle, avec Looker Studio comme bonus e-commerce.

---

## 5. Tableau comparatif — Multi-OS & coût (état réel 2026)

| Outil | macOS | Windows | Linux (desktop) | Modèle | Coût (2025-2026) | Note pour la formation |
|-------|:----:|:------:|:--------------:|--------|------------------|------------------------|
| **Power BI Desktop** | ❌ | ✅ | ❌ | Gratuit (Desktop) | **Gratuit** (Desktop Windows) | **Windows-only** [SOURCÉ Microsoft] — bloquant pour Mac/Linux en natif |
| **Power BI Service** (web) | ✅ navigateur | ✅ | ✅ navigateur | SaaS | **Power BI Pro ~14 $/user/mois** (hausse +40 % vs 10 $, avril 2025) [SOURCÉ] | Édition limitée vs Desktop ; suffisant pour consultation/édition légère sur Mac |
| **Tableau Desktop** | ✅ natif (Apple Silicon dès v24.2, macOS Ventura 13+) | ✅ | ❌ | Payant | **Tableau Creator ~75 $/user/mois** (≈900 $/an) [SOURCÉ] | Natif Mac = atout formateur ; pas de Linux desktop |
| **Tableau Public** | ✅ | ✅ | ❌ | Gratuit | **Gratuit** | Données **publiques uniquement** (tout est publié en ligne) [SOURCÉ] — parfait pour TP/portfolio, pas pour données confidentielles |
| **Looker Studio** | ✅ web | ✅ web | ✅ web | SaaS | **Gratuit** (Pro ~9 $/user/projet/mois pour features entreprise + Gemini) [SOURCÉ] | 100 % navigateur, zéro install — idéal Mac ; limites ~50 rapports / connecteurs |
| **Metabase** | ✅ web | ✅ web | ✅ web | Open source (self-host) ou Cloud | **Gratuit** (OSS) / Cloud payant | Web, tous OS ; orienté non-techniciens (question builder) [SOURCÉ] |
| **Apache Superset** | ✅ web | ✅ web | ✅ web | Open source (self-host) | **Gratuit** (OSS) | Web, tous OS ; puissant mais setup lourd (Docker + Postgres + Redis) [SOURCÉ] |
| **Python** (matplotlib / seaborn / plotly) | ✅ | ✅ | ✅ | Open source | **Gratuit** | 100 % cross-OS ; socle programmatique et pérenne |
| **Excel** | ✅ | ✅ | ❌ (web partiel) | Payant (M365) | Licence M365 | Omniprésent, base incontournable |

**Points clés de compatibilité (vérifiés 2026) :**
- ✅ **Power BI Desktop = Windows uniquement**, construit sur .NET avec intégrations Windows profondes ; **aucune version Mac/Linux native** [SOURCÉ Microsoft/MacPaw]. Contournements : **Power BI Service (navigateur, Safari supporté)**, **VM Windows 11 via Parallels Desktop** (solution la plus fiable sur Apple Silicon), VirtualBox, VM cloud + accès distant, ou Boot Camp (**Intel uniquement**, pas Apple Silicon).
- ✅ **Tableau Desktop = Mac + Windows nativement** (Apple Silicon natif depuis v24.2 sur macOS Ventura 13+), **pas de Linux desktop** (Linux seulement côté Tableau Server) [SOURCÉ Tableau techspecs].
- ✅ **Looker Studio / Metabase / Superset = applications web** → fonctionnent sur **tout OS** via navigateur.
- ✅ **Python = totalement cross-OS**.

---

## 6. Grille de décision pondérée

Pour objectiver le choix des outils et **dépasser le simple jugement narratif**, on note ci-dessous les principaux outils sur 5 critères pondérés, alignés sur les constats des sections précédentes. Chaque critère reçoit une note **/5** ; le score pondéré total est la somme des notes multipliées par le poids du critère (sur 100 %). Les outils web open source Metabase et Superset sont regroupés (profils proches : web cross-OS gratuit, orientés tech/start-up).

### 6.1 Critères et pondération

| Critère | Poids | Justification du poids |
|---------|:----:|------------------------|
| **Employabilité Nord / France** | **30 %** | Finalité première de la formation : décrocher un premier emploi data dans le bassin. Critère le plus discriminant (cf. §3 et §4). |
| **Pérennité / pertinence pédagogique** | **20 %** | Un outil enseigné doit rester pertinent plusieurs années et transmettre des concepts transférables (modélisation, viz, requêtage). |
| **Compatibilité multi-OS / contrainte Mac** | **20 %** | Contrainte structurante du formateur Mac (cf. §5) : un outil non installable nativement complique l'enseignement. |
| **Coût / accessibilité gratuite** | **15 %** | Budget formation et reproductibilité côté apprenants (install à la maison sans licence payante). |
| **Courbe d'apprentissage débutant** | **15 %** | Capacité à produire un livrable valorisable rapidement dans un parcours court. |

### 6.2 Notation des outils (/5 par critère)

| Outil | Employabilité (30 %) | Pérennité péda. (20 %) | Multi-OS / Mac (20 %) | Coût (15 %) | Courbe débutant (15 %) | **Score pondéré /5** |
|-------|:----:|:----:|:----:|:----:|:----:|:----:|
| **Power BI** | 5 | 4 | 2 | 4 | 4 | **3,90** |
| **Looker Studio** | 3 | 3 | 5 | 5 | 5 | **3,85** |
| **Python (matplotlib/seaborn/plotly)** | 4 | 5 | 5 | 5 | 2 | **4,15** |
| **Tableau / Tableau Public** | 4 | 4 | 4 | 3 | 4 | **3,85** |
| **Metabase / Superset** | 2 | 3 | 5 | 5 | 3 | **3,10** |

> Détail d'un calcul (exemple Power BI) : (5×0,30) + (4×0,20) + (2×0,20) + (4×0,15) + (4×0,15) = 1,50 + 0,80 + 0,40 + 0,60 + 0,60 = **3,90**.

### 6.3 Justification des notes (cohérence avec l'étude)

- **Power BI** — Employabilité **5/5** : outil n°1 national et surtout régional (retail/distribution = écosystème Microsoft, cf. §3.1 et §4). Multi-OS **2/5** : Windows-only, contournable seulement via Parallels/VM + Power BI Service web (cf. §5). Coût **4/5** : Desktop gratuit mais Power BI Pro payant (~14 $/mois) pour le partage. Pérennité **4/5** et courbe **4/5** : très structurant pédagogiquement, prise en main rapide pour des dashboards simples.
- **Looker Studio** — Multi-OS **5/5** et coût **5/5** : 100 % navigateur, gratuit, zéro install — idéal sur Mac. Courbe **5/5** : le plus accessible aux débutants. Employabilité **3/5** : présent mais cantonné au marketing/web/e-commerce, pas l'outil entreprise généraliste. Pérennité **3/5** : dépendance à l'écosystème Google, limites (~50 rapports / connecteurs).
- **Python** — Pérennité **5/5** : socle programmatique indépendant des modes éditeurs, transférable à toute la data. Multi-OS **5/5** et coût **5/5** : cross-OS et gratuit. Employabilité **4/5** : très demandé en complément (rarement comme seul outil de viz). Courbe **2/5** : le plus exigeant pour un grand débutant (code), d'où le bémol.
- **Tableau / Tableau Public** — Employabilité **4/5** : solide n°2, fort en ESN/conseil/grands comptes. Multi-OS **4/5** : natif Mac + Windows, mais pas de Linux desktop. Coût **3/5** : Tableau Desktop cher (~75 $/mois), compensé par Tableau Public gratuit (mais données publiques uniquement). Courbe **4/5** : ergonomie réputée intuitive.
- **Metabase / Superset** — Multi-OS **5/5** et coût **5/5** : web open source. Employabilité **2/5** : niche start-up/scale-up (EuraTechnologies), peu demandé hors tech. Courbe **3/5** : Metabase accessible, Superset au setup lourd (Docker + Postgres + Redis).

### 6.4 Classement et lecture

1. **Python — 4,15** : score le plus élevé, porté par la pérennité et le cross-OS gratuit ; pénalisé seulement par la courbe débutant. → confirme son rôle de **socle**.
2. **Power BI — 3,90** : dominé sur le multi-OS, mais son employabilité maximale (poids fort 30 %) le maintient en tête des outils BI dédiés. → confirme son rôle d'**outil d'employabilité prioritaire**.
3. **Looker Studio — 3,85** *(ex æquo)* : top sur multi-OS / coût / courbe, ce qui en fait le **meilleur outil web sur Mac**, mais bridé par une employabilité moyenne. → confirme son rôle d'**outil web cross-OS complémentaire**.
3. **Tableau / Tableau Public — 3,85** *(ex æquo)* : profil équilibré, employabilité de n°2 et natif Mac. → confirme son rôle de **différenciation optionnelle** (via Tableau Public gratuit).
5. **Metabase / Superset — 3,10** : excellents sur coût/OS mais employabilité de niche. → confirme leur statut d'**option** (open source / contexte start-up).

**Lecture d'ensemble** : aucun outil unique ne domine sur tous les critères — le grand demandé (Power BI) est le plus contraint sur Mac, tandis que les meilleurs sur Mac (Looker Studio, Python) ne couvrent pas à eux seuls la demande entreprise. La grille **conforte donc la combinaison multi-couches** de la section 7 plutôt qu'un choix unique : Python (socle pérenne), Power BI (employabilité), Looker Studio (web Mac), Tableau Public + Metabase (options). Les scores serrés entre les outils de rangs 2 à 4 (3,85-3,90) justifient précisément de les enseigner **ensemble et à des niveaux de priorité différents**, et non d'en sacrifier un.

---

## 7. Recommandation finale (argumentée)

### Objectif : maximiser l'employabilité dans le Nord **tout en** gérant la contrainte Mac du formateur.

Le dilemme est clair : **l'outil le plus demandé (Power BI) est précisément celui qui ne tourne pas nativement sur Mac/Linux.** On ne peut pas le contourner en l'évitant — ce serait pénaliser l'employabilité, surtout dans un bassin retail où Power BI domine. La solution est donc une **combinaison à 3 couches**.

### Couche 1 — SOCLE (cross-OS, non négociable)
**SQL + Python (pandas + matplotlib/seaborn/plotly)**
- 100 % cross-OS, gratuit, pérenne, indépendant des modes éditeurs.
- SQL = compétence n°1 (~95 % des offres). Python = polyvalence + viz programmatique pour le portfolio.
- Se prête parfaitement à l'enseignement sur Mac.

### Couche 2 — OUTIL PRINCIPAL EMPLOYABILITÉ : **Power BI** (priorité haute)
- **Justification** : n°1 national ET régional (retail/distribution = écosystème Microsoft). C'est la compétence la plus « monétisable » à court terme.
- **Gestion de la contrainte Mac** :
  - **Côté formateur (Mac)** : installer une **VM Windows 11 via Parallels Desktop** (solution la plus fiable Apple Silicon) pour démontrer Power BI Desktop en cours ; secondairement utiliser **Power BI Service** dans le navigateur.
  - **Côté apprenants Windows** : Power BI Desktop **gratuit**, natif.
  - **Côté apprenants Mac/Linux** : **Power BI Service (web)** pour l'édition légère + **VM Parallels/UTM** ou **poste virtuel cloud** pour la partie modélisation/DAX/Power Query. Prévoir un **lab Windows distant mutualisé** si le budget VM individuel est un frein.
- **Périmètre pédagogique** : Power Query (ETL), modèle en étoile, DAX, dashboards, publication sur Power BI Service.

### Couche 3 — OUTIL WEB CROSS-OS (confort formateur Mac + démonstration BI native)
**Looker Studio (gratuit)** en priorité, **+ Metabase (open source)** en option.
- **Looker Studio** : zéro installation, 100 % navigateur, gratuit, pertinent pour le **e-commerce/marketing** très présent dans le Nord. Permet au formateur Mac d'enseigner la dataviz **sans VM**.
- **Metabase** : introduit l'open source / le self-hosting et le requêtage SQL en environnement BI ; valorisé dans les start-up d'EuraTechnologies. (Superset = optionnel/avancé, setup lourd.)

### Couche 4 — OPTIONNEL / DIFFÉRENCIATION : **Tableau Public** (gratuit, natif Mac)
- Permet d'exposer au **n°2 du marché** (fort en ESN/conseil/grands comptes) **sans coût ni VM** (natif Mac).
- Limite à expliquer : données **publiques uniquement**. Idéal pour un projet portfolio.

### Synthèse de la combinaison recommandée

| Priorité | Outil | Rôle pédagogique | OS formateur Mac |
|----------|-------|------------------|------------------|
| 🔴 Essentiel | **SQL + Python (matplotlib/seaborn/plotly)** | Socle data + viz code | ✅ natif |
| 🔴 Essentiel | **Power BI** | Outil employabilité n°1 (Nord = retail) | ⚠️ via Parallels/VM + Power BI Service web |
| 🟠 Recommandé | **Looker Studio** | Dataviz web cross-OS, e-commerce | ✅ navigateur |
| 🟡 Optionnel | **Tableau Public** | Exposition au n°2, portfolio | ✅ natif Mac |
| 🟡 Optionnel | **Metabase** | Open source / BI start-up | ✅ navigateur |

**En une phrase** : *enseigner SQL + Python comme socle cross-OS, Power BI comme outil d'employabilité prioritaire (contrainte Mac gérée par Parallels + Power BI Service), Looker Studio comme outil de dataviz web confortable sur Mac, et Tableau Public en différenciation optionnelle.*

---

## 8. Sources

**Marché de l'emploi & offres**
- Indeed — Data Analyst Tableau Power BI : https://fr.indeed.com/q-data-analyst-tableau-power-bi-emplois.html
- Indeed — Data Visualisation : https://fr.indeed.com/Emplois-Data-Visualisation
- Indeed — Data Analyst Lille (59) : https://fr.indeed.com/Lille-(59)-Emplois-Analyst-Data-Analyst
- Glassdoor — Data Analyst Lille : https://www.glassdoor.fr/Emploi/lille-data-analyst-emplois-SRCH_IL.0,5_IC3061391_KO6,18.htm
- LinkedIn — Data Analyst Power BI France : https://fr.linkedin.com/jobs/data-analyst-power-bi-emplois
- APEC — Fiche métier Data Analyst : https://www.apec.fr/tous-nos-metiers/informatique/data-analyst.html
- EuraTechnologies — offre Data Analyst : https://www.euratechnologies.com/job-offers/241-data-analyst
- Datackathon — Emploi Data Visualisation : https://www.datackathon.com/emploi/data-visualisation/

**Parts de marché & classements outils**
- 6sense — Microsoft Power BI (BI) : https://6sense.com/tech/business-intelligence-bi/microsoft-power-bi-market-share
- 6sense — Tableau (Data Visualization) : https://6sense.com/tech/data-visualization/tableau-software-market-share
- Jedha — 10 meilleurs outils BI : https://www.jedha.co/formation-analyse-donnee/les-10-meilleurs-outils-bi-a-maitriser-en-2025
- mes-formations-data.fr — 21 compétences data analyst : https://www.mes-formations-data.fr/blog/2026/21-competences-data-analyst
- ScreeningPass — compétences data 2025 : https://screeningpass.fr/article/les-competences-data-les-plus-recherchees-en-2025/
- Stage.fr — compétences data analysts 2025 : https://www.stage.fr/blog/quelles-comp%C3%A9tences-data-analysts-2025/

**Compatibilité multi-OS**
- MacPaw — Power BI on Mac : https://macpaw.com/how-to/power-bi-work-on-mac
- The Bricks — Does Power BI Work on a Mac : https://www.thebricks.com/resources/guide-does-power-bi-work-on-mac
- Tableau — Technical specs : https://www.tableau.com/products/techspecs
- Tableau — Releases Desktop 2025.1 : https://www.tableau.com/support/releases/desktop/2025.1
- The Bricks — Tableau on Mac/Linux : https://www.thebricks.com/resources/guide-can-tableau-desktop-be-used-on-a-mac-or-linux
- Tableau — Linux requirements (Server) : https://help.tableau.com/current/server-linux/en-us/requ.htm

**Coûts & licences**
- Microsoft — mise à jour pricing Power BI : https://powerbi.microsoft.com/en-us/blog/important-update-to-microsoft-power-bi-pricing/
- The Register — Power BI Pro +40 % : https://www.theregister.com/2025/04/02/microsoft_power_bi_hikes/
- Onware — Tableau licences (Creator/Explorer/Viewer) : https://onware.com/blog/tableau-product-and-licenses/
- Tableau — Tableau Public : https://www.tableau.com/products/public
- Looker Studio Masterclass — Pro vs Free : https://lookerstudiomasterclass.com/blog/looker-studio-pro-vs-free
- Coefficient — Is Looker Studio Free : https://coefficient.io/is-looker-studio-free

**Outils open source web**
- KDnuggets — Self-hosted alternatives 2026 : https://www.kdnuggets.com/5-self-hosted-alternatives-for-data-scientists-in-2026
- Elest.io — Superset vs Metabase vs Redash : https://blog.elest.io/apache-superset-vs-metabase-vs-redash-which-open-source-bi-tool-to-self-host-in-2026/
- Metabase vs Superset : https://www.metabase.com/lp/metabase-vs-superset

**Tissu économique Hauts-de-France**
- Le Journal des Entreprises — Top 20 entreprises Hauts-de-France : https://www.lejournaldesentreprises.com/article/top-20-des-entreprises-des-hauts-de-france-un-classement-toujours-domine-par-lassociation-famille-2137610
- Wikipedia — Association Familiale Mulliez : https://en.wikipedia.org/wiki/Association_Familiale_Mulliez
- Cenisis — Data Quality Analyst (clients retail Nord) : https://www.cenisis.com/carriere/data-quality-analyst-senior-f-h/
- Indeed — OVHcloud Lille : https://fr.indeed.com/q-ovhcloud-l-lille-(59)-emplois.html
- LinkedIn — La Redoute Roubaix : https://fr.linkedin.com/jobs/la-redoute-emplois-roubaix

---

*Note de fiabilité : les parts de marché (6sense), prix éditeurs et specs OS sont des données sourcées et datées. Les proportions d'outils dans les offres (national et régional) sont des tendances convergentes issues de plusieurs agrégateurs, non un comptage exhaustif officiel — elles sont signalées [ESTIMATION] lorsqu'il s'agit d'une analyse de l'auteur.*
