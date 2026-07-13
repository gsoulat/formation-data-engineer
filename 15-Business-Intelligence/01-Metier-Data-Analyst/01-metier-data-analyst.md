# 01 — Le métier de Data Analyst & le référentiel

| | |
|---|---|
| **Phase** | Phase 0 — La Prairie |
| **Durée** | ~14 heures |
| **Type de module** | Découverte (peu technique) |
| **Objectifs** | Sensibilisation au cœur du métier (Business Intelligence / conception de tableaux de bord) et aux compétences transversales (communication, collaboration). Aucune évaluation technique à ce stade. |
| **Pré-requis** | **Aucun.** Bienvenue, tu pars de zéro et c'est normal. |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Expliquer avec tes propres mots** ce que fait un Data Analyst au quotidien et pourquoi l'entreprise paie pour ça.
2. **Distinguer** le Data Analyst du Data Engineer et du Data Scientist (et arrêter de confondre les trois en entretien).
3. **Décrire les 5 grandes activités** du métier (A1 à A5) et repérer celle qui sera le cœur de ta formation.
4. **Lire et décoder un référentiel de compétences** : comprendre comment un métier data est structuré en activités et en compétences (techniques et transversales), pour savoir ce qui sera évalué.
5. **Comprendre les 3 niveaux de maîtrise** (découvrir → adapter → transposer) et savoir te situer.
6. **Analyser une fiche de poste** réelle pour en extraire missions, compétences et outils attendus.
7. **Identifier les débouchés** concrets dans les Hauts-de-France et avoir une idée réaliste des salaires.

> Ce module ne te demande pas de coder. Il te demande de **comprendre où tu mets les pieds**. C'est la carte avant le voyage.

---

## Pourquoi ce module ?

Tu es en reconversion. Tu vas passer 7 mois intensifs à apprendre du SQL, du Python, du Power BI, des statistiques. C'est dense. Si tu ne sais pas **à quoi ça sert** et **vers quel métier tu vas**, tu vas ramer pour rester motivé·e quand un script refusera de tourner à 22h.

Ce module répond à trois questions simples mais vitales :

- **« Je vais faire quoi, concrètement, dans une entreprise ? »**
- **« Ce métier, ça consiste en quoi exactement, et qu'est-ce qu'on va m'apprendre ? »**
- **« Est-ce qu'on recrute, près de chez moi, et combien je peux espérer gagner ? »**

Comprendre le référentiel te donne aussi un **super-pouvoir** : pendant toute la formation, chaque brief, chaque exercice est rattaché à une compétence précise. Si tu sais lire ces attendus, tu sais **exactement ce qu'on évalue chez toi** et tu peux piloter ta progression. Les apprenants qui réussissent sont ceux qui ont compris les objectifs de leur parcours dès le début.

---

## Contenu détaillé

### C'est quoi, un Data Analyst ?

Un Data Analyst est **le traducteur entre les données et les humains qui décident**.

D'un côté, il y a des données : des fichiers de ventes, des logs de site web, des bases clients, des relevés de stock. Brutes, elles ne disent rien à personne. De l'autre côté, il y a des gens qui doivent prendre des décisions : un directeur de magasin qui veut savoir quels rayons sous-performent, une responsable marketing qui veut savoir quelle campagne a rapporté, un chef de produit qui veut comprendre pourquoi les clients abandonnent leur panier.

**Le Data Analyst fait le pont.** Il va chercher les données, les nettoie, les analyse, et surtout il **raconte une histoire claire** avec, généralement sous forme de tableaux de bord (dashboards) que les décideurs consultent.

> 📌 **L'image à retenir**
> Le Data Engineer construit les **tuyaux** (il achemine et stocke l'eau).
> Le Data Analyst ouvre le **robinet** et te sert un **verre d'eau claire et buvable** (une réponse à une question métier).
> Le Data Scientist invente une **machine qui prédit** s'il pleuvra demain pour remplir le réservoir.

#### Une journée type (exemple réel, retail Nord)

Imagine que tu es Data Analyst chez **Decathlon** (siège à Villeneuve-d'Ascq) :

- **9h** — Café. Un chef de produit « vélo » te demande pourquoi les ventes de VTT électriques ont chuté en mai dans la région.
- **9h30** — Tu écris une requête SQL pour extraire les ventes VTT par magasin et par semaine sur 6 mois.
- **10h30** — Tu nettoies : il manque des prix sur certaines lignes, deux magasins ont des codes produits différents pour le même vélo. Tu corriges.
- **11h30** — Tu explores dans Power BI : tu croises avec la météo et une rupture de stock fournisseur. Tu repères que la chute coïncide avec une rupture de 3 semaines.
- **14h** — Tu construis un tableau de bord clair : courbe des ventes, annotation de la rupture, comparaison avec l'an dernier.
- **16h** — Tu présentes au chef de produit en 10 minutes. Décision : sécuriser le réapprovisionnement. **Ton analyse a directement orienté une décision business.**

C'est ça, le métier. Pas du code pour le code : **une question métier → des données → une réponse actionnable**.

---

### Les 5 activités du métier (A1 à A5)

Le référentiel découpe le métier en **5 activités**. Garde-les en tête, elles structurent toute la formation.

| Code | Activité | En clair |
|------|----------|----------|
| **A1** | Automatiser la collecte et le traitement des données | Aller chercher les données automatiquement (scripts, ETL) au lieu de copier-coller à la main. |
| **A2** | Analyser et synthétiser les données | Explorer, calculer des statistiques, repérer des tendances et des anomalies. |
| **A3** | Appliquer des techniques d'analyse via des algorithmes d'IA | Utiliser du machine learning (introduction seulement pour un Data Analyst). |
| **A4** | Mener des projets data en équipe (légal & éthique) | Gérer un projet, respecter le RGPD, travailler avec d'autres. |
| **A5** | **Concevoir des tableaux de bord avancés** | **Le cœur du métier Data Analyst : la Business Intelligence (BI).** |

> 🎯 **Le cœur de ta formation = A5.**
> C'est l'activité que tu vas chercher à maîtriser en priorité : concevoir des tableaux de bord avancés. A1, A2 et A4 sont les fondations qui alimentent A5. A3 (le machine learning) n'est qu'une **introduction** pour toi : c'est le terrain principal du Data Scientist, pas du Data Analyst.

---

### Data Analyst vs Data Engineer vs Data Scientist

Les trois métiers travaillent avec la donnée mais ne font **pas du tout** la même chose. C'est LA question d'entretien classique.

| Critère | **Data Engineer** | **Data Analyst** | **Data Scientist** |
|---------|-------------------|------------------|--------------------|
| **Mission** | Construire et maintenir l'infrastructure (les « tuyaux ») | Répondre à des questions métier via analyse + dashboards | Construire des modèles prédictifs / IA |
| **Question type** | « Comment acheminer 10 To/jour de façon fiable ? » | « Pourquoi nos ventes ont baissé au T2 ? » | « Quels clients vont résilier le mois prochain ? » |
| **Outils clés** | SQL, Python, Spark, Airflow, cloud, data warehouse | **SQL, Excel, Power BI / Tableau / Looker, stats** | Python, scikit-learn, machine learning, maths avancées |
| **Livrable** | Pipelines, bases de données structurées | **Tableaux de bord, rapports, analyses** | Modèles, algorithmes, prédictions |
| **Maths** | Faibles à moyennes | **Statistiques descriptives** | Élevées (proba, algèbre, ML) |
| **Tourné vers** | La technique / le back-end | **Le métier / la décision** | La recherche / la prédiction |

> 💡 **À retenir**
> Si tu aimes **résoudre des énigmes business** et **communiquer des résultats clairs**, le Data Analyst est fait pour toi. Tu n'as PAS besoin d'être un génie des maths ni de tout coder. Tu as besoin de **curiosité**, de **rigueur** et de **pédagogie**.

> ⚠️ **Frontières floues dans la vraie vie**
> Dans une petite entreprise, une seule personne fait souvent les trois métiers. Dans un grand groupe comme **Auchan** ou **OVHcloud**, les rôles sont bien séparés. Un nouveau rôle hybride, l'**Analytics Engineer** (à mi-chemin Engineer/Analyst, autour de SQL et dbt), est de plus en plus demandé.

---

### Le métier structuré en compétences

#### Une formation reconnue

Cette formation prépare à un métier data **reconnu et recherché** sur le marché de l'emploi. Elle vise un titre de **niveau Bac+3/4** (niveau licence/master 1), qui couvre plusieurs métiers data. Toi, tu suis le **parcours Data Analyse**.

#### Les grandes familles de compétences

Le métier se découpe en **familles de compétences** que tu vas travailler tout au long du parcours. Certaines sont regroupées par thème et peuvent être validées de façon indépendante.

| Thème | Contenu |
|------|-------|
| Fondations data | Collecte, analyse, introduction à l'IA, gestion de projet... |
| **Business Intelligence** | **Concevoir des tableaux de bord avancés** |

> 🎯 **Ta cible principale : la Business Intelligence.**
> Sur cette formation intensive de 7 mois, l'objectif est de maîtriser la **conception de tableaux de bord avancés**. C'est le cœur du métier de Data Analyst (activité A5).

#### Ce que contient le cœur BI

La partie Business Intelligence repose principalement sur **3 compétences** :

- **Identifier les indicateurs clés (KPI)** à calculer en interrogeant les besoins métier.
- **Choisir des visualisations pertinentes** (en tenant compte de l'accessibilité, normes WCAG).
- **Créer des tableaux de bord** avec des outils de BI (Power BI, Looker Studio...).

Ces trois compétences vont progresser tout au long de la formation, du **niveau débutant en Prairie** jusqu'à la **maîtrise en Phase 3**.

---

### Comment lire un référentiel de compétences

Un référentiel, ça ressemble à une longue liste de phrases bizarres. Apprends à les décoder, c'est ta boussole pour 7 mois.

#### Les deux familles de compétences

- Les compétences **techniques** : faire de la data (collecter, nettoyer, analyser, visualiser).
- Les compétences **transversales** : travailler en équipe, résoudre des problèmes, communiquer. Elles comptent **autant** que les techniques dans l'évaluation !

#### Anatomie d'une compétence

Chaque compétence suit toujours la structure : **[ACTION] + [MOYEN] + [BUT/finalité]**. Exemple :

> « **Identifier les indicateurs clés à calculer** *(action)* **en interrogeant les besoins métier** *(moyen)* **afin de structurer les tableaux de bord nécessaires à des prises de décisions stratégiques** *(but)*. »

Quand tu lis une compétence, repère toujours ces 3 morceaux. Le « afin de » t'explique **pourquoi** la compétence existe.

#### Les 3 niveaux de maîtrise (découvrir → adapter → transposer)

Dans une pédagogie par projet, on évalue ta maîtrise sur **3 niveaux progressifs**. Sache toujours à quel niveau on t'attend.

| Niveau | Nom | Ce qu'on attend de toi |
|:------:|-----|------------------------|
| **1** | **Imiter** | Tu **reproduis** une solution à partir d'un exemple très similaire qu'on t'a fourni. |
| **2** | **Adapter** | Tu **transposes** une solution existante à un **nouveau contexte**, en documentant ce que tu fais. |
| **3** | **Transposer** | Tu **conçois une solution complète** à partir d'un simple besoin métier, et tu **justifies tes choix**. |

> 📌 **Exemple concret sur la création d'un tableau de bord**
> - **Niveau 1 (Prairie/Phase 1)** : on te donne un modèle de dashboard et des données, tu refais le même.
> - **Niveau 2 (Phase 2)** : on te donne de nouvelles données et un nouveau besoin, tu adaptes le dashboard.
> - **Niveau 3 (Phase 3)** : on te donne juste un besoin métier (« le directeur veut suivre la rentabilité »), tu conçois le dashboard de A à Z et tu expliques pourquoi tu as fait ces choix.

> 💡 En Prairie (maintenant), on est en **découverte / niveau 1 débutant**. Personne n'attend de toi de la maîtrise. On attend de la **curiosité** et de la **compréhension**.

---

### Analyser une fiche de poste

Savoir lire une offre d'emploi est une compétence en soi. Une fiche de poste contient toujours, dans le désordre :

1. **Le contexte / l'entreprise** — qui recrute et pourquoi.
2. **Les missions** — ce que tu feras (mappe-les sur A1-A5 !).
3. **Les compétences techniques attendues** — les outils (SQL, Power BI, Python, Excel...).
4. **Les compétences humaines** (soft skills) — communication, rigueur, esprit d'équipe (relie-les aux compétences transversales !).
5. **Le profil / formation** — niveau attendu, expérience.
6. **Conditions** — salaire, localisation, télétravail.

> 🔍 **Le réflexe à prendre dès maintenant**
> Quand tu lis une offre, surligne en deux couleurs : **les outils** (ce que tu dois apprendre) et **les missions** (ce qu'on te demandera de produire). Si « Power BI » et « tableaux de bord » reviennent dans 8 offres sur 10 → c'est exactement ce que cette formation t'apprend. Tu es au bon endroit.

---

### Débouchés dans les Hauts-de-France & salaires

Bonne nouvelle : **les Hauts-de-France sont une terre de retail et d'e-commerce**, et le retail est l'un des plus gros consommateurs de Data Analysts. Beaucoup de sièges sociaux sont concentrés autour de **Lille / Villeneuve-d'Ascq / Roubaix**.

#### Entreprises qui recrutent (région)

| Entreprise | Siège | Secteur | Pourquoi ils ont besoin de Data Analysts |
|-----------|-------|---------|-------------------------------------------|
| **Decathlon** | Villeneuve-d'Ascq | Retail sport | Ventes par magasin/produit, supply chain, e-commerce |
| **Auchan** | Villeneuve-d'Ascq | Grande distribution | Performance des rayons, fidélité, prix, logistique |
| **Leroy Merlin** (groupe Adeo) | Lezennes | Bricolage / retail | Parcours client, stocks magasins, web |
| **La Redoute** | Roubaix | E-commerce mode/maison | Comportement d'achat, taux de conversion, marketing |
| **Cofidis** | Villeneuve-d'Ascq | Crédit / banque en ligne | Scoring, risque, performance des offres |
| **OVHcloud** | Roubaix | Cloud / tech | Usage des infrastructures, performance, facturation |

> 🌍 **À savoir** : ces entreprises recrutent aussi via leurs **filiales digitales et data** (ex. les équipes data de Decathlon, Adeo Services, OVHcloud Data). Beaucoup d'offres passent par l'**alternance** — pertinent vu le format 7 mois + 12 mois.

#### Salaires indicatifs (France, ordre de grandeur)

> ⚠️ Fourchettes **indicatives** : elles varient fortement selon la ville (Paris > province), l'entreprise et l'expérience. À prendre comme repère, pas comme promesse.

| Profil | Salaire brut annuel (indicatif) |
|--------|--------------------------------|
| Data Analyst **junior** (0-2 ans) | ~30 000 – 38 000 € |
| Data Analyst **confirmé** (3-5 ans) | ~38 000 – 48 000 € |
| Data Analyst **senior / lead** | ~48 000 – 60 000 €+ |

> En province (Hauts-de-France), les fourchettes sont généralement un peu plus basses qu'à Paris, mais le **coût de la vie** est aussi nettement plus bas.

---

## Activités

### Activité 1 — Analyse de 2 fiches de poste réelles (≈ 2h, en binôme)

**Consigne :**
1. Va sur un site d'emploi (France Travail, Indeed, LinkedIn, Welcome to the Jungle, l'APEC).
2. Recherche « **Data Analyst** » localisé dans les **Hauts-de-France** (Lille, Villeneuve-d'Ascq, Roubaix...).
3. Choisis **2 offres distinctes** (idéalement une junior/débutant et une avec un peu d'expérience).
4. Pour **chaque offre**, remplis ce tableau :

| Élément | Offre 1 | Offre 2 |
|---------|---------|---------|
| Entreprise / secteur | | |
| 3 missions principales | | |
| Activités du métier concernées (A1-A5) | | |
| Outils techniques demandés | | |
| Soft skills demandés (compétences transversales) | | |
| Niveau / expérience attendu | | |
| Salaire affiché (s'il y en a) | | |

5. Conclus en 5 lignes : **quels outils reviennent le plus souvent ?** Sont-ils enseignés dans cette formation ?

<details>
<summary>💡 Pistes de corrigé</summary>

- **Missions → activités** : « créer des reportings / dashboards » → **A5** ; « extraire et nettoyer les données » → **A1/A2** ; « présenter aux équipes métier » → **A4 + communication**.
- **Outils récurrents attendus** : tu devrais voir **SQL** (quasi systématique), **Power BI** ou **Tableau** ou **Looker**, **Excel**, souvent **Python**, parfois un cloud (GCP/Azure/AWS) ou dbt.
- **Soft skills → transversales** : « bon relationnel / vulgarisation » → **communication, pédagogie** ; « autonomie / rigueur » → **cadrage de problème, recherche d'information** ; « travail en équipe » → **collaboration**.
- **Conclusion attendue** : SQL + un outil de BI reviennent presque partout. **Bonne nouvelle : c'est exactement le cœur de ta formation (la Business Intelligence).** Si tu vois beaucoup de Python/ML, c'est souvent des postes hybrides Analyst/Scientist.
- **Erreur fréquente** : confondre une offre « Data Analyst » avec une offre « Data Engineer » (beaucoup d'Airflow, Spark, pipelines) ou « Data Scientist » (machine learning, modèles). Vérifie le livrable principal : **dashboards = Analyst**.
</details>

---

### Activité 2 — Mini-recherche débouchés (≈ 1h, individuel)

**Consigne :**
1. Choisis **une** entreprise de la liste régionale (Decathlon, Auchan, Leroy Merlin, La Redoute, Cofidis, OVHcloud) **ou** une autre entreprise des Hauts-de-France qui t'intéresse.
2. Trouve **une** offre data réelle chez elle (ou une offre similaire dans le secteur).
3. Réponds en une demi-page :
   - Quel problème métier cette entreprise pourrait-elle résoudre avec un Data Analyst ?
   - Quel(s) tableau(x) de bord imagines-tu utile(s) pour elle ?
   - Cette entreprise te donne-t-elle envie ? Pourquoi ?

<details>
<summary>💡 Pistes de corrigé</summary>

- **Decathlon** : suivre les ventes par sport / par magasin, détecter les ruptures de stock, mesurer la performance du e-commerce. Dashboard « ventes & stocks par région ».
- **La Redoute** : taux de conversion du site, paniers abandonnés, performance des campagnes marketing. Dashboard « funnel e-commerce ».
- **Cofidis** : taux d'acceptation des crédits, suivi du risque, performance des offres. Dashboard « performance des produits financiers ».
- **OVHcloud** : usage et performance des serveurs, suivi de la facturation, satisfaction client. Dashboard « usage infrastructure & churn ».
- **Ce qui est valorisé** : que tu relies un **besoin métier réel** à un **livrable Data Analyst concret** (un dashboard, une analyse). C'est exactement le raisonnement « du besoin métier au tableau de bord ».
</details>

---

## Vidéos d'auto-formation

> Regarde-en **2 ou 3** (au moins une FR et une EN). Objectif : entendre de vraies personnes décrire le métier. Prends 5 notes par vidéo.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|-------|--------|:------:|:-----:|------|----------------------|
| Data Scientist / Data Analyst c'est quoi exactement ? | Cookie connecté | FR | ~15 min | https://www.youtube.com/watch?v=jls6_PqLzmw | Vue d'ensemble des métiers data, formation et salaires, expliquée simplement. |
| Data Scientist vs Data Analyst vs Data Engineer : quelles différences ? | (FR) | FR | ~10 min | https://www.youtube.com/watch?v=mEZIHFxUFEc | La distinction claire entre les 3 métiers data et leurs rôles. |
| Data analyst : traiter et interpréter des données | (FR) | FR | ~5 min | https://www.youtube.com/watch?v=cP4DTLbp38A | Témoignage d'un data analyst sur son quotidien réel. |
| Day in the Life of a Data Analyst (Work From Home) *Realistic* | (EN) | EN | ~12 min | https://www.youtube.com/watch?v=82uIsqAVVzA | À quoi ressemble vraiment une journée de Data Analyst, heure par heure. |
| How to Become a Data Analyst in 2025 (complete roadmap) | (EN) | EN | ~15 min | https://www.youtube.com/watch?v=qbbInxaFmw0 | La feuille de route des compétences à acquérir pour devenir Data Analyst. |

> 🔎 **Pour aller plus loin** (recherches YouTube, liens valides) :
> - Métier en français : https://www.youtube.com/results?search_query=métier+data+analyst+français
> - Différence des 3 métiers : https://www.youtube.com/results?search_query=différence+data+analyst+data+scientist+data+engineer
> - Chaîne de référence (EN) : https://www.youtube.com/@AlexTheAnalyst

---

## Quiz — 5 QCM

**Q1.** Quel est le rôle principal d'un Data Analyst ?
- A) Construire et maintenir les pipelines de données
- B) Faire le pont entre les données et les décisions métier (analyses + tableaux de bord)
- C) Développer des modèles de machine learning prédictifs
- D) Administrer les serveurs cloud

**Q2.** Quelle activité (A1-A5) constitue le **cœur** de la formation Data Analyst (la Business Intelligence) ?
- A) A1 — Automatiser la collecte
- B) A3 — Appliquer des algorithmes d'IA
- C) A5 — Concevoir des tableaux de bord avancés
- D) A4 — Mener des projets en équipe

**Q3.** Qui, parmi ces métiers, est le plus orienté **construction de l'infrastructure / des « tuyaux »** de données ?
- A) Data Analyst
- B) Data Engineer
- C) Data Scientist
- D) Product Owner

**Q4.** Dans une pédagogie par projet, que signifie le **niveau 3 « Transposer »** ?
- A) Reproduire une solution à partir d'un exemple identique
- B) Adapter une solution existante à un nouveau contexte
- C) Concevoir une solution complète à partir d'un simple besoin métier et justifier ses choix
- D) Copier-coller du code trouvé en ligne

**Q5.** Que désignent les compétences **transversales** dans le référentiel ?
- A) Les compétences techniques de collecte
- B) Travailler en équipe, résoudre des problèmes, communiquer
- C) Les chapitres du cours de Python
- D) Les niveaux de progression

<details>
<summary>✅ Réponses</summary>

1. **B** — Le Data Analyst fait le pont entre les données et la décision (analyses + dashboards).
2. **C** — A5 (tableaux de bord avancés) = cœur du métier, la Business Intelligence.
3. **B** — Le Data Engineer construit l'infrastructure (les tuyaux).
4. **C** — « Transposer » = concevoir une solution complète depuis un besoin et justifier ses choix.
5. **B** — Les compétences transversales = soft skills professionnelles (équipe, résolution de problème, communication).
</details>

---

## À retenir

- Le **Data Analyst** est un **traducteur entre données et décisions** : question métier → données → réponse claire (souvent un **tableau de bord**).
- Le métier se découpe en **5 activités (A1-A5)**. Le **cœur de ta formation = A5** (tableaux de bord avancés), c'est la **Business Intelligence**.
- **Analyst ≠ Engineer ≠ Scientist** : l'Engineer construit les tuyaux, l'Analyst sert le verre d'eau (analyse/BI), le Scientist invente la machine à prédire.
- Tu prépares un titre reconnu de **niveau Bac+3/4**, et cette formation vise la maîtrise de la **Business Intelligence**.
- Le référentiel distingue deux familles : les compétences **techniques** et les compétences **transversales** (tout aussi importantes). Le cœur BI = identifier les KPI, choisir les visualisations, créer les tableaux de bord.
- 3 niveaux de maîtrise : **Imiter (1) → Adapter (2) → Transposer (3)**. En Prairie, tu es en découverte ; on attend de la **curiosité**.
- Les **Hauts-de-France** recrutent (retail/e-commerce : Decathlon, Auchan, Leroy Merlin, La Redoute, Cofidis, OVHcloud). Salaire junior indicatif : **~30-38 k€** brut/an.
- L'outil roi de l'Analyst : **SQL + un outil de BI** (Power BI / Tableau / Looker). C'est exactement ce que tu vas apprendre.
