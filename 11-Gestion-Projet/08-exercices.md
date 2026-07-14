[← Precedent](07-accessibilite-eco-conception.md) | [🏠 Accueil](README.md)

# 📝 Exercices Pratiques - Gestion de Projet Data

## 🎯 Objectifs

- Mettre en pratique les concepts des 7 lecons
- Progresser du niveau debutant au niveau avance
- Travailler sur des cas realistes issus du monde professionnel
- Se preparer a un projet de synthese en conditions reelles

---

## Niveau 1 - Bases

### Exercice 1.1 : Rediger des User Stories

**Contexte** : Une entreprise de distribution alimentaire souhaite mettre en place un **systeme de gestion des stocks intelligent**. Le systeme doit permettre aux gestionnaires de stocks de suivre les niveaux en temps reel, anticiper les ruptures et optimiser les commandes fournisseurs.

**Consigne** : Redigez **5 User Stories** completes au format standard avec au moins 2 criteres d'acceptation chacune (format Given/When/Then).

Les roles a considerer :
- Gestionnaire de stock
- Responsable des achats
- Directeur logistique

---

<details>
<summary>💡 Solution Exercice 1.1</summary>

**User Story 1 : Vue temps reel des stocks**

```
En tant que Gestionnaire de stock,
je veux voir le niveau de stock actuel de chaque produit en temps reel,
afin de pouvoir reagir rapidement aux variations imprevues.
```

Criteres d'acceptation :
```
CA-1.1 : Etant donne que je suis connecte a l'application,
         Quand j'accede au tableau de bord des stocks,
         Alors je vois le niveau de stock de chaque produit
         mis a jour toutes les 15 minutes.

CA-1.2 : Etant donne qu'un produit passe sous le seuil d'alerte (20% du stock cible),
         Quand le pipeline de donnees detecte cette situation,
         Alors le produit est affiche en rouge dans le tableau de bord
         et une notification est envoyee par email au gestionnaire.
```

**User Story 2 : Alertes de rupture de stock**

```
En tant que Gestionnaire de stock,
je veux recevoir une alerte automatique 48h avant une rupture de stock estimee,
afin de pouvoir passer une commande d'urgence a temps.
```

Criteres d'acceptation :
```
CA-2.1 : Etant donne que le modele de prediction estime une rupture dans les 48h
         (basee sur le taux de consommation moyen des 30 derniers jours),
         Quand le pipeline de prediction s'execute (toutes les 6h),
         Alors une alerte email et Slack est envoyee au gestionnaire et au responsable achats.

CA-2.2 : Etant donne que l'alerte a ete envoyee,
         Quand le gestionnaire clique sur le lien dans l'alerte,
         Alors il est redirige vers la fiche produit avec l'historique de consommation
         et une suggestion de quantite a commander.
```

**User Story 3 : Suggestions de commande**

```
En tant que Responsable des achats,
je veux recevoir des suggestions de commande automatiques basees sur l'historique de ventes,
afin d'optimiser les quantites commandees et reduire le gaspillage.
```

Criteres d'acceptation :
```
CA-3.1 : Etant donne que les donnees de ventes des 12 derniers mois sont disponibles,
         Quand le modele de suggestion s'execute (chaque lundi a 6h),
         Alors une liste de suggestions de commande est generee avec :
         produit, quantite suggeree, fournisseur, delai de livraison estime.

CA-3.2 : Etant donne que le responsable achats consulte les suggestions,
         Quand il valide une suggestion,
         Alors un bon de commande pre-rempli est genere dans le format du fournisseur.
```

**User Story 4 : Analyse du taux de rotation**

```
En tant que Directeur logistique,
je veux analyser le taux de rotation de chaque categorie de produit sur 12 mois,
afin d'identifier les produits a faible rotation et ajuster la strategie d'achat.
```

Criteres d'acceptation :
```
CA-4.1 : Etant donne que je suis sur le rapport "Rotation des stocks",
         Quand je selectionne une periode et une categorie,
         Alors un graphique affiche le taux de rotation mensuel
         avec la tendance (hausse/baisse).

CA-4.2 : Etant donne que le taux de rotation d'un produit est inferieur a 2 par an,
         Quand le rapport est genere,
         Alors le produit est signale comme "faible rotation"
         avec une estimation du cout de stockage inutile.
```

**User Story 5 : Export pour les fournisseurs**

```
En tant que Responsable des achats,
je veux exporter l'historique des commandes par fournisseur en format CSV,
afin de negocier les tarifs lors des revues annuelles.
```

Criteres d'acceptation :
```
CA-5.1 : Etant donne que je suis sur la page "Historique Fournisseurs",
         Quand je selectionne un fournisseur et une periode, puis clique sur "Exporter CSV",
         Alors un fichier CSV est telecharge avec : date, produit, quantite, prix unitaire,
         montant total, delai de livraison effectif.

CA-5.2 : Etant donne que l'export contient plus de 50 000 lignes,
         Quand je lance l'export,
         Alors un message m'informe que l'export sera envoye par email sous 5 minutes.
```

</details>

---

### Exercice 1.2 : Transformer des objectifs en SMART

**Consigne** : Transformez ces 3 objectifs flous en objectifs SMART complets.

1. "Ameliorer les performances du data warehouse"
2. "Mettre en place une meilleure gouvernance des donnees"
3. "Faire de l'IA sur nos donnees clients"

---

<details>
<summary>💡 Solution Exercice 1.2</summary>

**1. Performance du data warehouse**

❌ "Ameliorer les performances du data warehouse"

✅ SMART : "Reduire le temps de reponse moyen des 10 requetes les plus utilisees du data warehouse Snowflake de 45 secondes a moins de 5 secondes, d'ici le 30 avril 2026, en implementant le clustering, les materialized views et l'optimisation des requetes SQL les plus couteuses."

| Critere | Verification |
|---------|-------------|
| S | 10 requetes les plus utilisees, Snowflake |
| M | De 45s a < 5s |
| A | Techniques d'optimisation connues, pas de refonte |
| R | Les utilisateurs se plaignent de la lenteur, impact sur la productivite |
| T | 30 avril 2026 |

**2. Gouvernance des donnees**

❌ "Mettre en place une meilleure gouvernance des donnees"

✅ SMART : "Documenter 100% des tables du data warehouse (80 tables) dans un catalogue de donnees (datahub ou dbt docs) avec description, owner, classification sensibilite et lineage, d'ici le 30 juin 2026, en y consacrant 2 jours par sprint (1 Data Engineer + 1 Data Analyst)."

| Critere | Verification |
|---------|-------------|
| S | 80 tables, catalogue datahub ou dbt docs, 4 champs par table |
| M | 100% de couverture (0% aujourd'hui) |
| A | 2 jours/sprint, 80 tables / ~5 sprints = ~16 tables/sprint |
| R | Prerequis pour la conformite RGPD et l'onboarding des nouveaux |
| T | 30 juin 2026 |

**3. IA sur les donnees clients**

❌ "Faire de l'IA sur nos donnees clients"

✅ SMART : "Deployer en production un modele de scoring d'appetence produit atteignant un AUC >= 0.75 sur le jeu de test, permettant de cibler les 20% de clients les plus susceptibles d'acheter le produit X, d'ici le 30 septembre 2026, avec un budget de 50 000 EUR (1 Data Scientist + infrastructure GPU)."

| Critere | Verification |
|---------|-------------|
| S | Modele de scoring d'appetence, produit X, top 20% clients |
| M | AUC >= 0.75 |
| A | 1 DS, 6 mois, budget 50k, donnees clients existantes |
| R | Objectif marketing d'augmenter les ventes du produit X de 15% |
| T | 30 septembre 2026 |

</details>

---

### Exercice 1.3 : Remplir une matrice RACI

**Contexte** : Equipe data composee de :
- 1 Product Owner (PO)
- 1 Scrum Master (SM)
- 2 Data Engineers (DE1, DE2)
- 1 Data Scientist (DS)
- 1 Data Analyst (DA)
- 1 DPO

**Consigne** : Remplissez la matrice RACI pour les activites suivantes. Rappel : R = Responsible, A = Accountable, C = Consulted, I = Informed. Un seul A par activite.

| Activite | PO | SM | DE1 | DE2 | DS | DA | DPO |
|----------|:--:|:--:|:---:|:---:|:--:|:--:|:---:|
| Definir les priorites du backlog | ? | ? | ? | ? | ? | ? | ? |
| Concevoir l'architecture du pipeline | ? | ? | ? | ? | ? | ? | ? |
| Developper le modele ML | ? | ? | ? | ? | ? | ? | ? |
| Creer le dashboard | ? | ? | ? | ? | ? | ? | ? |
| Valider la conformite RGPD | ? | ? | ? | ? | ? | ? | ? |
| Animer la retrospective | ? | ? | ? | ? | ? | ? | ? |
| Mettre en production | ? | ? | ? | ? | ? | ? | ? |

---

<details>
<summary>💡 Solution Exercice 1.3</summary>

| Activite | PO | SM | DE1 | DE2 | DS | DA | DPO |
|----------|:--:|:--:|:---:|:---:|:--:|:--:|:---:|
| Definir les priorites du backlog | **R/A** | I | C | C | C | C | C |
| Concevoir l'architecture du pipeline | C | I | **R/A** | R | C | I | I |
| Developper le modele ML | C | I | C | I | **R/A** | C | I |
| Creer le dashboard | C | I | I | I | C | **R/A** | I |
| Valider la conformite RGPD | C | I | C | C | C | I | **R/A** |
| Animer la retrospective | R | **R/A** | R | R | R | R | I |
| Mettre en production | I | I | **R/A** | R | C | I | I |

**Justifications** :
- **Priorites du backlog** : Le PO est le seul responsable et redevable des priorites. L'equipe est consultee pour la faisabilite.
- **Architecture pipeline** : DE1 (le plus senior) est R et A. DE2 contribue (R). DS consulte pour les besoins ML.
- **Modele ML** : DS est le seul R/A. DE1 est consulte pour l'integration dans le pipeline.
- **Dashboard** : DA est R/A car c'est son expertise. DS consulte pour les metriques.
- **RGPD** : Le DPO est le seul R/A. Tous les producteurs de donnees sont consultes.
- **Retrospective** : SM facilite (R/A). Toute l'equipe participe activement (R).
- **Mise en production** : DE1 est R/A (infrastructure). DE2 aide. DS consulte pour verifier le modele.

</details>

---

## Niveau 2 - Intermediaire

### Exercice 2.1 : Prioriser avec RICE

**Contexte** : Vous etes Data Product Manager chez un assureur. Votre equipe de 3 personnes (1 DE, 1 DS, 1 DA) dispose de 12 personne-semaines pour le prochain trimestre. Vous avez 6 projets candidats :

| # | Projet | Description |
|---|--------|------------|
| A | Dashboard sinistres | Tableau de bord de suivi des sinistres pour les 150 gestionnaires |
| B | Pipeline donnees partenaires | Ingestion automatique des donnees de 3 partenaires (50 utilisateurs internes impactes) |
| C | Modele de detection de fraude | ML pour detecter les fraudes dans les declarations (impact sur 200 000 dossiers/an) |
| D | Migration DWH vers le cloud | Migration du DWH Oracle on-premise vers BigQuery (80 utilisateurs) |
| E | API de tarification | API pour calculer les primes en temps reel (100 courtiers) |
| F | Data Quality framework | Mise en place de Great Expectations sur les 20 tables principales (equipe data de 10) |

**Informations supplementaires** :

| Projet | Impact estime | Confidence | Effort (p-s) |
|--------|:------------:|:----------:|:------------:|
| A | Eleve (2) | 100% | 4 |
| B | Moyen (1) | 80% | 3 |
| C | Massif (3) | 50% | 8 |
| D | Eleve (2) | 80% | 16 |
| E | Eleve (2) | 80% | 6 |
| F | Faible (0.5) | 100% | 2 |

**Consigne** :
1. Calculez le score RICE de chaque projet
2. Classez-les par priorite
3. Recommandez quels projets realiser ce trimestre (budget : 12 p-s)
4. Justifiez vos choix

---

<details>
<summary>💡 Solution Exercice 2.1</summary>

**1. Calcul des scores RICE**

| Projet | Reach | Impact | Confidence | Effort | RICE Score | Calcul |
|--------|:-----:|:------:|:----------:|:------:|:----------:|--------|
| A | 150 | 2 | 1.00 | 4 | **75.0** | (150 x 2 x 1.00) / 4 |
| B | 50 | 1 | 0.80 | 3 | **13.3** | (50 x 1 x 0.80) / 3 |
| C | 200 000 | 3 | 0.50 | 8 | **37 500** | (200000 x 3 x 0.50) / 8 |
| D | 80 | 2 | 0.80 | 16 | **8.0** | (80 x 2 x 0.80) / 16 |
| E | 100 | 2 | 0.80 | 6 | **26.7** | (100 x 2 x 0.80) / 6 |
| F | 10 | 0.5 | 1.00 | 2 | **2.5** | (10 x 0.5 x 1.00) / 2 |

**2. Classement par RICE**

| Rang | Projet | RICE Score |
|:----:|--------|:---------:|
| 1 | C - Detection de fraude | 37 500 |
| 2 | A - Dashboard sinistres | 75.0 |
| 3 | E - API de tarification | 26.7 |
| 4 | B - Pipeline partenaires | 13.3 |
| 5 | D - Migration DWH | 8.0 |
| 6 | F - Data Quality | 2.5 |

**3. Recommandation (budget : 12 p-s)**

| Projet | Effort | Cumul | Decision |
|--------|:------:|:-----:|----------|
| C - Detection de fraude | 8 | 8 | ✅ **Retenu avec reserves** (spike de 2 p-s d'abord car confidence = 50%) |
| A - Dashboard sinistres | 4 | 12 | ✅ **Retenu** |
| E - API tarification | 6 | 18 | ❌ Budget depasse |

**Proposition ajustee** :
- **Sprint 1-2** : Spike sur le projet C (2 p-s) pour valider la faisabilite
- Si GO sur C : **Sprint 3-6** : Projet C (6 p-s restantes) + Projet A en parallele (4 p-s)
- Si NO-GO sur C : **Sprint 3-6** : Projet A (4 p-s) + Projet E (6 p-s)
- Total : 12 p-s

**4. Justification** :
- Le projet C a un score RICE astronomique grace a son Reach (200 000 dossiers), mais sa confidence est basse (50%). Un spike est indispensable.
- Le projet A est un "quick win" : effort faible, confidence elevee, impact direct sur 150 utilisateurs.
- Le projet D (migration) est important mais trop couteux (16 p-s > budget) : a reporter au trimestre suivant.

</details>

---

### Exercice 2.2 : Mini cahier des charges

**Contexte** : Une chaine de fast-food avec 200 restaurants veut un **dashboard temps reel** affichant les ventes par restaurant, par produit et par heure, pour le comite de direction (10 personnes) et les directeurs de restaurant (200 personnes).

**Consigne** : Redigez un mini cahier des charges contenant :
1. Contexte et objectifs (5 lignes)
2. 3 User Stories prioritaires avec criteres d'acceptation
3. Besoins non-fonctionnels (performance, volumetrie, disponibilite)
4. Liste des sources de donnees probables
5. Perimetre "in scope" et "out of scope"

---

<details>
<summary>💡 Solution Exercice 2.2</summary>

```
MINI CAHIER DES CHARGES
========================
Dashboard Temps Reel des Ventes - FastFood Corp

1. CONTEXTE ET OBJECTIFS
========================

FastFood Corp opere 200 restaurants en France. Aujourd'hui, le suivi
des ventes se fait via des rapports Excel hebdomadaires produits
manuellement par chaque directeur de restaurant. Ce processus est
lent (donnees disponibles a J+7), source d'erreurs et ne permet
pas de reagir en temps reel. L'objectif est de centraliser les
donnees de ventes et de fournir un dashboard temps reel accessible
au comite de direction et aux directeurs de restaurant.

2. USER STORIES PRIORITAIRES
=============================

US1 : Vue globale du CA en temps reel
--------------------------------------
En tant que membre du comite de direction,
je veux voir le CA total de la chaine et par restaurant en temps reel,
afin de suivre la performance commerciale au fil de la journee.

Criteres d'acceptation :
- Etant donne que je suis connecte au dashboard,
  Quand la page d'accueil se charge,
  Alors je vois le CA cumule du jour pour l'ensemble de la chaine,
  avec un comparatif par rapport au meme jour de la semaine precedente.

- Etant donne qu'une nouvelle transaction est enregistree en caisse,
  Quand le pipeline rafraichit les donnees (toutes les 5 minutes),
  Alors le CA affiche est mis a jour.

US2 : Classement des produits par restaurant
---------------------------------------------
En tant que Directeur de restaurant,
je veux voir le classement des produits les plus vendus dans mon restaurant,
afin d'ajuster la mise en avant des produits et la gestion des stocks.

Criteres d'acceptation :
- Etant donne que je selectionne mon restaurant et une periode (jour/semaine/mois),
  Quand le classement s'affiche,
  Alors je vois les 20 produits les plus vendus avec quantite, CA,
  et evolution par rapport a la periode precedente.

- Etant donne que je filtre par categorie de produit (burger, boisson, dessert),
  Quand le filtre est applique,
  Alors le classement est mis a jour en temps reel.

US3 : Analyse des heures de pointe
------------------------------------
En tant que membre du comite de direction,
je veux voir la repartition des ventes par heure pour chaque restaurant,
afin d'optimiser le staffing et les approvisionnements.

Criteres d'acceptation :
- Etant donne que je selectionne un restaurant et une semaine,
  Quand le graphique horaire s'affiche,
  Alors je vois un heatmap des ventes par heure et par jour de la semaine.

- Etant donne que je survole une cellule du heatmap,
  Quand le tooltip s'affiche,
  Alors je vois le CA, le nombre de transactions et le panier moyen.

3. BESOINS NON-FONCTIONNELS
============================
- Performance : Temps de chargement du dashboard < 5 secondes
- Latence : Donnees mises a jour toutes les 5 minutes
- Volumetrie : ~200 restaurants x ~500 transactions/jour = 100 000 transactions/jour
- Disponibilite : 99.5% (hors maintenance planifiee)
- Utilisateurs : 210 simultanes max (200 directeurs + 10 direction)
- Securite : Chaque directeur ne voit que les donnees de son restaurant
- Accessibilite : Conformite WCAG 2.1 niveau AA

4. SOURCES DE DONNEES
======================
- Systeme de caisse (POS) de chaque restaurant : API REST ou export CSV toutes les 5 min
- Referentiel produits : Base de donnees centrale (PostgreSQL)
- Referentiel restaurants : Base de donnees centrale (PostgreSQL)
- Referentiel employes : SIRH (pour le staffing, phase 2)

5. PERIMETRE
============
IN SCOPE (v1) :
- Ingestion des donnees de ventes des 200 restaurants
- Dashboard avec les 3 vues (CA global, produits, heures de pointe)
- Filtres par restaurant, periode, categorie
- Droits d'acces par restaurant

OUT OF SCOPE (v2+) :
- Prediction des ventes (ML)
- Optimisation automatique du staffing
- Gestion des stocks
- Application mobile
- Donnees de satisfaction client
```

</details>

---

### Exercice 2.3 : Analyse SWOT

**Contexte** : Votre entreprise (PME de 300 salaries, secteur retail) envisage de migrer son infrastructure data on-premise (SQL Server + SSIS + SSRS) vers le cloud (Azure : Synapse + Data Factory + Power BI).

**Consigne** : Realisez une analyse SWOT complete avec au moins 4 elements par quadrant.

---

<details>
<summary>💡 Solution Exercice 2.3</summary>

| | **Positif** | **Negatif** |
|---|-------------|-------------|
| **Interne** | **Forces (Strengths)** | **Faiblesses (Weaknesses)** |
| | 1. Equipe technique motivee et volontaire pour monter en competences | 1. Aucune experience cloud dans l'equipe (0/5 personnes) |
| | 2. Donnees bien structurees dans SQL Server (schema documente) | 2. Budget IT limite (PME) : pas de marge pour les depassements |
| | 3. Direction convaincue et sponsor engage | 3. 150+ rapports SSRS a migrer (dette technique importante) |
| | 4. Infrastructure on-premise vieillissante (fin de support SQL Server 2016) | 4. Pas de processus CI/CD en place |
| | 5. Processus ETL SSIS bien documentes | 5. Dependance a 1 DBA qui connait tout (bus factor = 1) |
| **Externe** | **Opportunites (Opportunities)** | **Menaces (Threats)** |
| | 1. Reduction des couts infra de 30-50% a moyen terme (plus de serveurs on-premise) | 1. Couts cloud imprevisibles si mal geres (facture surprise) |
| | 2. Scalabilite automatique (absorber les pics de fin de mois) | 2. Lock-in Microsoft Azure (difficulte a changer ensuite) |
| | 3. Acces a des services avances (ML, streaming) sans investissement infra | 3. Reglementation RGPD : donnees clients dans le cloud = analyse d'impact requise |
| | 4. Attractivite pour le recrutement (les profils data veulent du cloud) | 4. Concurrents deja sur le cloud : retard a combler |
| | 5. Partenariat possible avec un integrateur Microsoft | 5. Risque de penurie de consultants Azure (marche tendu) |

**Plan d'action derivee du SWOT** :
- **Force + Opportunite** : Profiter de la motivation de l'equipe pour organiser des formations Azure (certifications AZ-900, DP-203)
- **Force + Menace** : La bonne documentation existante facilite la migration et reduit le risque d'erreur
- **Faiblesse + Opportunite** : Le partenariat integrateur compense le manque d'experience cloud
- **Faiblesse + Menace** : Le budget limite et les couts cloud imprevisibles = necessite un POC avec suivi des couts strict

</details>

---

## Niveau 3 - Avance

### Exercice 3.1 : Projet Complet de Bout en Bout

**Contexte** :

Vous etes le/la **Lead Data Engineer** chez **RetailPlus**, une chaine de magasins de sport avec 50 magasins en France, un site e-commerce, et 500 employes. Le Directeur Marketing vous sollicite pour un projet data strategique.

**Extraits des entretiens realises** :

#### Entretien 1 : Directeur Marketing (Sponsor)

> "Nos clients achetent en magasin et en ligne mais on n'a aucune vue unifiee. On ne sait pas qui achete quoi, ou et quand. Je veux une 'Customer 360' : une vue complete de chaque client. On a aussi besoin de mieux cibler nos campagnes email. Aujourd'hui on envoie le meme email a tout le monde, c'est du gaspillage. Mon budget pour ce projet est de 150 000 EUR sur 12 mois."

#### Entretien 2 : Responsable CRM

> "Notre base CRM (Salesforce) contient 200 000 clients, mais je suis sure qu'il y a beaucoup de doublons (meme personne avec des comptes differents en magasin et en ligne). Les donnees de contact ne sont pas toujours fiables : emails invalides, telephones errones. On a aussi un programme de fidelite avec 80 000 adherents."

#### Entretien 3 : Responsable E-commerce

> "Le site tourne sur Shopify. On fait 30% du CA en ligne. On a toutes les donnees de navigation et d'achat. Le probleme c'est qu'on ne peut pas les relier aux achats en magasin. On utilise Google Analytics pour le web mais il n'y a pas de lien avec le CRM."

#### Entretien 4 : DSI

> "On a un serveur SQL Server on-premise pour les donnees magasins (systeme de caisse). Les donnees e-commerce sont dans Shopify (API). Le CRM est dans Salesforce (API). On a un budget cloud Azure, pas encore utilise pour la data. L'equipe data actuelle : 2 Data Engineers et 1 Data Analyst."

---

**Consigne** : Realisez les 7 livrables suivants :

#### Livrable 1 : Expression de besoins

Redigez 5 User Stories avec criteres d'acceptation pour le projet "Customer 360".

#### Livrable 2 : Objectifs SMART

Definissez 3 objectifs SMART pour le projet.

#### Livrable 3 : Priorisation RICE

Identifiez 5 fonctionnalites et priorisez-les avec le framework RICE.

#### Livrable 4 : TCO et ROI

Estimez le TCO sur 12 mois et le ROI attendu.

#### Livrable 5 : Planning Sprints

Planifiez les 3 premiers sprints (2 semaines chacun) avec Sprint Goals et stories.

#### Livrable 6 : Squelette du DAT

Redigez les sections 1-3 du Document d'Architecture Technique.

#### Livrable 7 : Strategie d'eco-conception

Proposez 5 mesures d'eco-conception pour ce projet.

---

<details>
<summary>💡 Solution Exercice 3.1</summary>

### Livrable 1 : User Stories

**US1 : Vue client unifiee**

```
En tant que Responsable CRM,
je veux une vue unifiee de chaque client avec ses achats magasin et en ligne,
afin d'avoir une vision complete du comportement d'achat.
```

Criteres d'acceptation :
```
CA-1.1 : Etant donne qu'un client a un compte CRM et un compte Shopify,
         Quand le pipeline de deduplication s'execute (quotidien),
         Alors les deux profils sont fusionnes en un seul profil client
         avec un identifiant unique.

CA-1.2 : Etant donne que je recherche un client par email ou telephone,
         Quand le resultat s'affiche,
         Alors je vois l'historique complet des achats (magasin + web),
         le statut de fidelite, et la derniere interaction.
```

**US2 : Segmentation clients pour les campagnes**

```
En tant que Directeur Marketing,
je veux segmenter automatiquement les clients en groupes homogenes (RFM),
afin de cibler les campagnes email par segment.
```

Criteres d'acceptation :
```
CA-2.1 : Etant donne que le pipeline RFM s'execute chaque semaine,
         Quand la segmentation est calculee,
         Alors chaque client est assigne a un segment (Champions, Loyal,
         A risque, Perdu, etc.) base sur la Recence, la Frequence et
         le Montant des achats.

CA-2.2 : Etant donne que les segments sont calcules,
         Quand le Directeur Marketing consulte le dashboard segmentation,
         Alors il voit la taille de chaque segment, l'evolution vs mois precedent,
         et peut exporter la liste des clients d'un segment pour une campagne.
```

**US3 : Deduplication des clients**

```
En tant que Responsable CRM,
je veux que les doublons soient automatiquement detectes et fusionnes,
afin d'avoir une base client propre et fiable.
```

Criteres d'acceptation :
```
CA-3.1 : Etant donne que le pipeline de deduplication s'execute,
         Quand deux profils ont le meme email OU le meme nom+prenom+date_naissance,
         Alors ils sont signales comme doublons potentiels avec un score de confiance.

CA-3.2 : Etant donne qu'un doublon a un score de confiance > 95%,
         Quand le pipeline s'execute,
         Alors la fusion est automatique (le profil le plus complet est conserve).
         Les doublons avec un score < 95% sont soumis a validation manuelle.
```

**US4 : Dashboard Customer 360**

```
En tant que Directeur Marketing,
je veux un dashboard avec les KPIs client (LTV, panier moyen, frequence),
afin de piloter la strategie client.
```

Criteres d'acceptation :
```
CA-4.1 : Etant donne que je suis sur le dashboard Customer 360,
         Quand je selectionne une periode,
         Alors je vois : nombre de clients actifs, LTV moyenne,
         panier moyen, frequence d'achat, taux de retention, NPS.

CA-4.2 : Etant donne que je clique sur un segment client,
         Quand le detail s'affiche,
         Alors je vois les memes KPIs filtres pour ce segment.
```

**US5 : Enrichissement qualite des donnees**

```
En tant que Responsable CRM,
je veux que les emails et telephones invalides soient detectes automatiquement,
afin d'ameliorer la delivrabilite des campagnes.
```

Criteres d'acceptation :
```
CA-5.1 : Etant donne que le pipeline de qualite s'execute quotidiennement,
         Quand un email est invalide (format incorrect ou domaine inexistant),
         Alors il est marque comme "invalide" dans le CRM avec la raison.

CA-5.2 : Etant donne que le taux d'emails invalides est calcule,
         Quand le rapport qualite s'affiche,
         Alors le taux actuel est compare a l'objectif (< 5%).
```

---

### Livrable 2 : Objectifs SMART

**Objectif 1** : "Reduire le taux de doublons clients de 15% (estime) a moins de 2% d'ici le 30 juin 2026, en implementant un pipeline de deduplication base sur le matching email + nom/prenom/date_naissance."

**Objectif 2** : "Augmenter le taux d'ouverture des campagnes email de 12% (actuel) a 20% d'ici le 30 septembre 2026, en passant d'un envoi uniforme a un ciblage par segment RFM (au moins 5 segments)."

**Objectif 3** : "Disposer d'une vue client 360 unifiee (magasin + web + fidelite) couvrant 100% des 200 000 clients, avec un rafraichissement quotidien, d'ici le 31 mars 2026."

---

### Livrable 3 : Priorisation RICE

| # | Fonctionnalite | Reach | Impact | Confidence | Effort (p-s) | RICE |
|---|---------------|:-----:|:------:|:----------:|:------------:|:----:|
| 1 | Pipeline d'ingestion unifie (3 sources) | 200 000 | 3 | 80% | 6 | **80 000** |
| 2 | Deduplication clients | 200 000 | 2 | 80% | 4 | **80 000** |
| 3 | Segmentation RFM | 200 000 | 2 | 80% | 3 | **106 667** |
| 4 | Dashboard Customer 360 | 15 | 2 | 100% | 4 | **7.5** |
| 5 | Enrichissement qualite (emails/tel) | 200 000 | 0.5 | 100% | 2 | **50 000** |

**Ordre recommande** : 3 > 1 = 2 > 5 > 4

Mais logiquement, 1 (ingestion) doit etre fait avant 2 (dedup) et 3 (segmentation). L'ordre reel est : **1 → 2 → 3 → 5 → 4**.

---

### Livrable 4 : TCO et ROI

**TCO sur 12 mois** :

| Poste | Cout |
|-------|:----:|
| Azure (Synapse Serverless + Data Factory + Storage) | 12 000 EUR |
| Salesforce API (inclus dans le contrat) | 0 EUR |
| Shopify API (inclus) | 0 EUR |
| Power BI Pro (15 licences) | 2 700 EUR |
| Equipe (2 DE + 1 DA, 50% du temps sur ce projet) | 105 000 EUR |
| Formation Azure (3 personnes) | 6 000 EUR |
| Consultant architecture (10 jours) | 15 000 EUR |
| Marge imprevus (10%) | 14 000 EUR |
| **TOTAL** | **154 700 EUR** |

**ROI estime** :

| Gain | Montant annuel |
|------|:--------------:|
| Augmentation CA par campagnes ciblees (+8% sur 30% du CA en ligne = 2M EUR) | +160 000 EUR |
| Reduction du gaspillage emailing (envoi cible vs masse) | +20 000 EUR |
| Gain de temps CRM (deduplication manuelle = 2j/semaine actuellement) | +30 000 EUR |
| **Total gains** | **210 000 EUR** |

```
ROI annee 1 = (210 000 - 154 700) / 154 700 x 100 = 35.7%
```

---

### Livrable 5 : Planning des 3 premiers sprints

**Sprint 1 (S1-S2) : "Poser les fondations"**
- Sprint Goal : "Infrastructure cloud deployee et premier pipeline d'ingestion fonctionnel"
- Stories :
  1. Provisionner l'environnement Azure (Synapse, Data Factory, Storage) - 3 pts
  2. Pipeline d'ingestion CRM Salesforce -> Azure Storage (raw) - 5 pts
  3. Audit de qualite sur les donnees CRM (echantillon 10 000) - 3 pts
  4. Setup CI/CD avec GitHub Actions pour les pipelines - 3 pts

**Sprint 2 (S3-S4) : "Toutes les sources connectees"**
- Sprint Goal : "Les 3 sources (CRM, E-commerce, Caisses) sont ingerees quotidiennement"
- Stories :
  1. Pipeline d'ingestion Shopify -> Azure Storage (raw) - 5 pts
  2. Pipeline d'ingestion SQL Server (caisses) -> Azure Storage (raw) - 5 pts
  3. Tests de qualite automatises sur les 3 sources - 3 pts
  4. Documentation des schemas sources (dictionnaire de donnees) - 2 pts

**Sprint 3 (S5-S6) : "Client unifie"**
- Sprint Goal : "Vue client unifiee avec deduplication operationnelle"
- Stories :
  1. Modele de matching/deduplication (email + nom/prenom/DoB) - 8 pts
  2. Table unifiee `dim_customer` avec identifiant unique - 5 pts
  3. Dashboard qualite : taux de doublons, taux completude - 3 pts
  4. Documentation technique du pipeline de deduplication - 2 pts

---

### Livrable 6 : Squelette du DAT (Sections 1-3)

```
DOCUMENT D'ARCHITECTURE TECHNIQUE
Projet Customer 360 - RetailPlus
Version 1.0 - Fevrier 2026

1. CONTEXTE ET OBJECTIFS
========================

1.1 Contexte
RetailPlus, chaine de 50 magasins de sport, souhaite unifier les donnees
clients provenant de 3 sources (CRM Salesforce, e-commerce Shopify,
caisses SQL Server) pour creer une vue Customer 360.

1.2 Objectifs techniques
- Ingerer quotidiennement les donnees de 3 sources dans Azure
- Dedupliquer les 200 000 clients avec un taux de faux positifs < 1%
- Fournir un modele de donnees Client unifie avec rafraichissement < 6h
- Supporter 15 utilisateurs concurrents sur Power BI

1.3 Contraintes
- Budget : 150 000 EUR (12 mois)
- Stack : Azure (imposee par la DSI)
- RGPD : Donnees personnelles clients (anonymisation en dev/test)
- Equipe : 2 DE + 1 DA (50% du temps alloue)

2. ARCHITECTURE GENERALE
=========================

2.1 Vue d'ensemble

  Salesforce ──> Azure Data Factory ──> Azure Data Lake (Raw)
  Shopify    ──> Azure Data Factory ──>       │
  SQL Server ──> Azure Data Factory ──>       │
                                              ▼
                                    Azure Synapse (Transformation)
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                     Bronze          Silver          Gold
                     (raw)         (cleaned)      (business)
                                                      │
                                                      ▼
                                                  Power BI

2.2 Composants

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Ingestion | Azure Data Factory | Connecteurs natifs Salesforce, Shopify |
| Stockage | Azure Data Lake Gen2 | Cout faible, scalable, Delta Lake |
| Transformation | Synapse Serverless + dbt | SQL-based, serverless = pas de cluster |
| Serving | Azure Synapse Dedicated (petit) | Performance pour Power BI |
| Visualisation | Power BI | Deja utilise, 15 licences Pro |
| Orchestration | Azure Data Factory | Integre, pas besoin d'Airflow |
| Monitoring | Azure Monitor + alertes | Integre a Azure |

3. ARCHITECTURE DES DONNEES
=============================

3.1 Sources de donnees

| Source | Type | Volume | Frequence | Format |
|--------|------|--------|-----------|--------|
| CRM Salesforce | API REST | 200 000 clients, 500 000 interactions | Quotidien | JSON |
| Shopify | API REST | 60 000 clients web, 1M commandes | Quotidien | JSON |
| Caisses (SQL Server) | Base relationnelle | 150 000 clients, 3M transactions | Quotidien | Tables SQL |

3.2 Modele de donnees

Bronze : Tables brutes (1 table par source, format identique a la source)
- raw_salesforce_contacts
- raw_salesforce_opportunities
- raw_shopify_customers
- raw_shopify_orders
- raw_pos_customers
- raw_pos_transactions

Silver : Tables nettoyees et standardisees
- stg_customers_salesforce (schema unifie)
- stg_customers_shopify (schema unifie)
- stg_customers_pos (schema unifie)
- stg_transactions (toutes sources)

Gold : Tables metier
- dim_customer (vue unifiee, deduplication)
- dim_product
- dim_store
- dim_date
- fact_transactions
- fact_customer_rfm (segmentation)

3.3 Logique de deduplication
- Matching exact : email
- Matching fuzzy : nom + prenom (Levenshtein distance < 2) + date de naissance
- Score de confiance : > 95% = fusion auto, 80-95% = validation manuelle, < 80% = pas de fusion
```

---

### Livrable 7 : Strategie d'eco-conception

1. **Choisir la region Azure France Central (Paris)** : Facteur carbone ~55g CO2/kWh grace au nucleaire. Eviter les regions Allemagne ou USA.

2. **Utiliser Synapse Serverless plutot que Dedicated Pool** : Le serverless ne consomme des ressources que lors de l'execution des requetes. Pour un usage quotidien de quelques heures, c'est 70% plus econome que un Dedicated Pool 24/7.

3. **Format Parquet + compression** : Stocker les donnees en Parquet compresse (Snappy ou Zstd) plutot qu'en CSV ou JSON. Gain de 70-90% en stockage et en scan. Partitionner par date.

4. **Politique de retention** : Raw (bronze) = 6 mois puis archivage en cold tier. Silver = 2 ans. Gold = 5 ans. Logs Data Factory = 30 jours. Supprimer automatiquement les donnees de dev/test apres 7 jours.

5. **Requetes optimisees** : Ne jamais faire `SELECT *`. Filtrer sur les partitions de date systematiquement. Utiliser des materialized views pour les requetes Power BI repetitives. Mesurer le volume scanne par requete et optimiser les plus couteuses.

</details>

---

## Recapitulatif des exercices

| Exercice | Niveau | Concepts mobilises | Duree estimee |
|----------|:------:|-------------------|:-------------:|
| 1.1 User Stories | Bases | User Stories, Given/When/Then | 30 min |
| 1.2 SMART | Bases | Methode SMART | 20 min |
| 1.3 RACI | Bases | Matrice RACI, roles | 15 min |
| 2.1 RICE | Intermediaire | RICE, priorisation, planning | 45 min |
| 2.2 Cahier des charges | Intermediaire | Expression de besoins, non-fonctionnel | 60 min |
| 2.3 SWOT | Intermediaire | Analyse de risques, migration cloud | 30 min |
| 3.1 Projet complet | Avance | Tous les concepts des 7 lecons | 3-4 h |

---

[← Precedent](07-accessibilite-eco-conception.md) | [🏠 Accueil](README.md)

---

**Academy** - Formation Data Engineer
