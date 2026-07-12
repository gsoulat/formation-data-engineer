# 01 — Concevoir un processus de collecte de données

| | |
|---|---|
| **Phase** | Phase 3 — Flux de données & alimentation de la BI |
| **Durée indicative** | ~22 h |
| **Compétence visée** | **C1 — Concevoir et mettre en place un processus de collecte de données** (niveau 1) |
| **Pré-requis** | Module 2.5 (RGPD & éthique des données), notions de bases de données relationnelles, savoir lire un fichier CSV/Excel, première idée de ce qu'est une API |
| **Posture** | **Conception / architecture** : on dessine le processus de collecte sur le papier. L'implémentation technique (scripts, connecteurs, automatisation) viendra au module 3.2. |

> Fil rouge du module : tu es Data Analyst chez **NordRetail**, une enseigne fictive de 12 magasins répartis dans les Hauts-de-France (Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes…) plus une boutique e-commerce. La direction veut un **dashboard de ventes multi-magasins**. Avant de brancher quoi que ce soit, tu dois **concevoir** d'où viendront les données et comment les rassembler.

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Cartographier** les sources de données d'une organisation (type, format, volume, fréquence de mise à jour, propriétaire).
2. **Évaluer** chaque source selon trois critères clés : **accessibilité**, **sécurité**, **intégrité**.
3. Expliquer le principe de **centralisation** des données (entrepôt / datamart) et son rôle dans la BI.
4. **Choisir** les outils de collecte adaptés à chaque type de source et au besoin métier.
5. Intégrer les exigences **RGPD** dès la conception de la collecte (*privacy by design*).
6. **Documenter** le processus de collecte de façon claire et réutilisable.

---

## Pourquoi c'est utile au Data Analyst

Un dashboard n'est jamais meilleur que les données qui l'alimentent. **« Garbage in, garbage out »** : si la collecte est mal pensée, tout le reste s'effondre.

- **Tu gagnes du temps plus tard** : une collecte bien conçue évite des semaines de re-travail quand on découvre qu'une source manque ou qu'un champ est inexploitable.
- **Tu parles le même langage que les équipes** : DSI, métier, DPO… La cartographie est l'objet qui met tout le monde d'accord avant de coder.
- **Tu te couvres juridiquement** : penser RGPD en amont t'évite de collecter illégalement des données personnelles (et l'amende qui va avec).
- **Tu rends ton travail reproductible** : un processus documenté peut être repris, audité, automatisé.

En pratique, le DA est très souvent **celui qui conçoit la collecte** dans les PME et ETI, là où il n'y a pas (encore) de Data Engineer dédié.

---

## Cartographier les sources de données

Cartographier, c'est **faire l'inventaire** de toutes les données disponibles ou nécessaires, et décrire leurs caractéristiques. C'est l'étape n°1, avant tout choix technique.

### Les grandes familles de sources

| Famille | Exemples concrets (NordRetail) | Format typique | Accès |
|---|---|---|---|
| **Bases de données relationnelles** | Logiciel de caisse (PostgreSQL), ERP, base RH | Tables SQL | Requête SQL / connecteur |
| **Fichiers plats** | Export Excel des stocks, CSV des fournisseurs, budgets | `.csv`, `.xlsx`, `.json` | Dépôt partagé, mail |
| **APIs (web services)** | API météo, API du transporteur, API réseaux sociaux | JSON / XML via HTTP | Clé API, REST |
| **Web (scraping)** | Prix des concurrents sur leurs sites | HTML à parser | Scraping (avec prudence légale) |
| **Flux temps réel / IoT** | Compteurs de passage en magasin, capteurs | Streaming, MQTT | Connecteur dédié |
| **SaaS / outils métier** | Google Analytics (e-commerce), CRM, outil emailing | API / export | OAuth, export programmé |

### La fiche d'identité d'une source

Pour **chaque** source, tu documentes au minimum :

| Attribut | Question à se poser | Exemple |
|---|---|---|
| **Nom / description** | Qu'est-ce que c'est ? | Base de caisse magasin Lille |
| **Type** | BDD, fichier, API, web… | Base PostgreSQL |
| **Format** | Structure des données | Tables relationnelles |
| **Volume** | Combien de données ? | ~50 000 lignes/jour |
| **Fréquence de MAJ** | À quel rythme ça change ? | Temps réel (transactions) |
| **Fréquence de collecte** | À quel rythme je la récupère ? | Batch quotidien à 2 h |
| **Propriétaire / contact** | Qui en est responsable ? | DSI — M. Dubois |
| **Mode d'accès** | Comment j'y accède ? | Connecteur SQL, lecture seule |
| **Données personnelles ?** | RGPD concerné ? | Oui (n° fidélité, email) |

### Comprendre les fréquences de mise à jour

La **fréquence de MAJ de la source** et la **fréquence de collecte** ne sont pas la même chose. Une caisse enregistre en continu (temps réel) mais tu peux choisir de ne collecter qu'**une fois par nuit** (batch). Le bon rythme dépend du **besoin métier** :

- Dashboard de **pilotage stratégique** (CA mensuel) → collecte **quotidienne** suffit.
- Dashboard de **suivi opérationnel** (ruptures de stock) → collecte **horaire** voire temps réel.

> **Règle d'or** : ne collecte jamais plus souvent que ce dont le métier a réellement besoin. Plus c'est fréquent, plus c'est coûteux et fragile.

> ⚠️ **Erreur courante** — *Confondre « données qui changent vite » et « besoin de les rafraîchir vite ».* Le CA change à chaque vente, mais le directeur le regarde une fois par jour. Inutile de monter un flux temps réel coûteux pour ça.

---

## Évaluer les sources : accessibilité, sécurité, intégrité

Toutes les sources cartographiées ne se valent pas. Avant de bâtir le processus, tu **notes** chaque source sur trois axes.

### Accessibilité

> *Suis-je capable, techniquement et juridiquement, de récupérer cette donnée ?*

- **Technique** : existe-t-il un connecteur, une API, un droit de lecture ? La donnée est-elle dans un format exploitable ou un PDF scanné illisible ?
- **Droits** : ai-je l'autorisation d'accès ? Faut-il une clé API, un compte de service, un accord du fournisseur ?
- **Disponibilité** : la source est-elle stable (un site web peut changer ou tomber) ?

### Sécurité

> *Comment je protège la donnée pendant et après la collecte ?*

- **Confidentialité** : qui a le droit de voir ces données ? Faut-il les chiffrer en transit (HTTPS) et au repos ?
- **Authentification** : utiliser des comptes de service en **lecture seule**, ne jamais coder un mot de passe en dur (utiliser des variables d'environnement / coffre à secrets).
- **Traçabilité** : qui a collecté quoi, et quand ?
- **Moindre privilège** : ne demander que les accès strictement nécessaires.

### Intégrité

> *La donnée est-elle complète, exacte et fiable ?*

- **Complétude** : manque-t-il des lignes, des colonnes, des périodes ?
- **Exactitude** : les valeurs sont-elles plausibles (un prix négatif = problème) ?
- **Cohérence** : la même information dit-elle la même chose dans deux sources (le CA de la caisse colle-t-il avec celui de la compta) ?
- **Fraîcheur** : la donnée est-elle à jour ou périmée ?

> 💡 **Astuce** : note chaque source de 🔴 / 🟠 / 🟢 sur chaque axe. Une source 🔴 en accessibilité = blocage à régler en priorité ; une source 🔴 en intégrité = il faudra prévoir un gros nettoyage en aval.

> ⚠️ **Erreur courante** — *Supposer que la donnée est « propre » parce qu'elle vient d'une base officielle.* Même un ERP contient des doublons, des champs vides et des saisies fantaisistes. On vérifie **toujours** l'intégrité.

---

## Centraliser les données : entrepôt et datamart

Une fois les sources collectées, où mettre tout ça ? On les **centralise** dans un lieu unique, pensé pour l'analyse. C'est le cœur de la **BI** (Business Intelligence).

### Pourquoi centraliser ?

- **Une seule source de vérité** : tout le monde regarde les mêmes chiffres.
- **Performance** : un entrepôt est optimisé pour les requêtes d'analyse (lecture massive), contrairement aux bases de production optimisées pour les transactions.
- **On ne perturbe pas la production** : interroger directement la caisse en pleine journée la ralentirait.
- **Historique** : l'entrepôt conserve l'historique, même si la source l'écrase.

### Les concepts à connaître

| Concept | Définition courte | Pour qui |
|---|---|---|
| **Data Warehouse (entrepôt)** | Dépôt central de données **structurées**, nettoyées et organisées pour l'analyse (*schema-on-write* : on structure avant de stocker) | Analystes, métier, BI |
| **Datamart** | Un **sous-ensemble thématique** de l'entrepôt, dédié à un métier (datamart « Ventes », datamart « RH ») | Une équipe précise |
| **Data Lake (lac)** | Dépôt de données **brutes**, tous formats (y compris non structurées : images, logs), structurées seulement à la lecture (*schema-on-read*) | Data Scientists / Engineers |
| **ETL** | **Extract – Transform – Load** : on extrait, on transforme/nettoie, **puis** on charge dans l'entrepôt | Alimentation d'un entrepôt |
| **ELT** | **Extract – Load – Transform** : on charge brut, **puis** on transforme dans l'entrepôt (plus moderne, cloud) | Gros volumes, cloud |

```
   SOURCES                COLLECTE              CENTRALISATION         RESTITUTION
 ┌──────────┐                                  ┌────────────────┐
 │  Caisses │──┐                               │  DATA WAREHOUSE│      ┌──────────┐
 │  ERP     │──┤    Extract  Transform  Load   │  ┌──────────┐  │      │ Dashboard│
 │  API     │──┼──►   ───────────────────────► │  │ Datamart │  │ ───► │  ventes  │
 │  CSV     │──┤                               │  │  Ventes  │  │      │  Power BI│
 │  Web     │──┘                               │  └──────────┘  │      └──────────┘
 └──────────┘                                  └────────────────┘
```

> **Pour NordRetail** : un entrepôt central reçoit caisses + ERP + e-commerce, et on en dérive un **datamart « Ventes »** dédié au dashboard de la direction commerciale.

> ⚠️ **Erreur courante** — *Croire qu'entrepôt = data lake.* L'entrepôt stocke du **structuré nettoyé** pour la BI ; le data lake stocke du **brut** tous formats pour l'exploration/ML. Confondre les deux, c'est se tromper d'outil et de coût.

---

## Choisir les outils de collecte

Le bon outil dépend du **type de source** et du **besoin** (volume, fréquence, budget, compétences de l'équipe).

| Type de source | Outils possibles | Quand le choisir |
|---|---|---|
| Base SQL | Connecteur natif (Power BI/Tableau), requête SQL, Python (`pandas`/`SQLAlchemy`) | Données structurées, accès direct |
| Fichiers CSV/Excel | Import manuel, Python (`pandas`), Power Query | Petits volumes, MAJ peu fréquente |
| API REST | Python (`requests`), connecteurs no-code, outils ELT (Airbyte, Fivetran) | Données SaaS, MAJ régulière |
| Web (scraping) | `BeautifulSoup`, `Scrapy` (avec prudence légale) | Quand aucune API n'existe |
| Multi-sources / automatisation | Outils ETL/ELT (Talend, Airbyte), orchestrateur (Airflow) | Pipeline régulier, plusieurs sources |

**Critères de choix :**
1. **Adéquation au besoin** : volume, fréquence, temps réel ou batch ?
2. **Compétences disponibles** : no-code vs code Python.
3. **Coût** : licence, infrastructure, maintenance.
4. **Maintenabilité** : un connecteur standard se maintient mieux qu'un script maison.
5. **Sécurité & conformité** : l'outil gère-t-il les secrets, le chiffrement, les logs ?

> ⚠️ **Erreur courante** — *Choisir l'outil avant d'avoir cartographié le besoin.* On ne part pas de « j'ai envie d'utiliser tel outil » mais de « voici mes sources et mon besoin, quel outil y répond ? ».

---

## RGPD dans la collecte (rappel module 2.5)

Dès qu'une source contient des **données personnelles** (nom, email, n° de fidélité, IP, géolocalisation…), le RGPD s'applique **dès la conception**.

Les réflexes à intégrer dans ta conception :

- **Base légale** : ai-je le droit de collecter ? (consentement, contrat, intérêt légitime…)
- **Minimisation** : ne collecte **que** les données nécessaires au dashboard. Pas besoin du n° de téléphone pour analyser le CA.
- **Finalité** : la donnée n'est utilisée que pour l'objectif déclaré.
- **Durée de conservation** : prévoir une date de purge.
- **Sécurité** : chiffrement, accès restreint (cf. §4.2).
- **Pseudonymisation / anonymisation** : remplacer l'identité par un identifiant quand l'analyse n'a pas besoin de la personne.
- **Droits des personnes** : accès, rectification, effacement doivent rester possibles.
- **Registre des traitements** : documenter le traitement (lien direct avec la doc, §8).

> 💡 **Privacy by design** : la conformité ne se rajoute pas à la fin, elle se **conçoit** en même temps que la collecte.

> ⚠️ **Erreur courante** — *Collecter « au cas où ».* Aspirer toutes les colonnes « parce qu'elles sont là » viole le principe de minimisation. On collecte ce dont le besoin métier a besoin, point.

---

## Documenter le processus de collecte

La documentation transforme une intuition en **processus reproductible et auditable**. Elle doit répondre à : **Quoi ? D'où ? Comment ? À quel rythme ? Par qui ? Avec quelles précautions ?**

Une bonne doc de collecte contient :

1. **La cartographie des sources** (le tableau du §3.2 rempli).
2. **Le schéma de flux** : sources → collecte → entrepôt → restitution (cf. §5.2).
3. **Pour chaque flux** : outil utilisé, fréquence, format de sortie, responsable.
4. **L'évaluation** accessibilité / sécurité / intégrité (les notes 🔴🟠🟢).
5. **Le volet RGPD** : données personnelles concernées, base légale, durée de conservation.
6. **Les règles de transformation/nettoyage prévues** (même si l'implémentation vient après).
7. **Le dictionnaire de données** : signification de chaque champ collecté.

> 💡 **Astuce** : une doc se relit dans 6 mois par quelqu'un d'autre. Sois explicite, date-la, versionne-la.

> ⚠️ **Erreur courante** — *Reporter la doc « à plus tard ».* Sans documentation, le processus n'est pas reproductible : personne ne pourra le reprendre, l'auditer ou l'automatiser. La doc fait **partie** de la conception.

---

## Exercices

> Garde ton fil rouge **NordRetail** en tête. Rédige tes réponses avant d'ouvrir les corrigés.

### Exercice 1 — Cartographier les sources

NordRetail dispose de : un logiciel de caisse (base PostgreSQL, transactions temps réel) ; un ERP de gestion des stocks (export CSV quotidien) ; une boutique e-commerce avec Google Analytics (API) ; un fichier Excel de budgets mis à jour chaque mois par la compta ; un programme de fidélité (base avec emails clients).

**Consigne** : construis le tableau de cartographie (nom, type, format, fréquence de MAJ, fréquence de collecte conseillée, données personnelles ?).

<details>
<summary>Voir le corrigé</summary>

| Source | Type | Format | MAJ source | Collecte conseillée | Données perso ? |
|---|---|---|---|---|---|
| Caisse magasins | Base PostgreSQL | Tables SQL | Temps réel | Batch quotidien (nuit) | Oui (n° fidélité lié) |
| ERP stocks | Fichier | CSV | Quotidienne | Quotidienne | Non |
| E-commerce / GA | API | JSON | Continue | Quotidienne | Oui (IP, identifiants) |
| Budgets compta | Fichier | Excel | Mensuelle | Mensuelle | Non |
| Programme fidélité | Base | Tables SQL | Quasi temps réel | Hebdomadaire | **Oui** (email, nom) |

Points clés : la fréquence de collecte ≤ besoin métier (pas de temps réel pour un dashboard de pilotage). Deux sources contiennent des données personnelles → RGPD à activer.
</details>

### Exercice 2 — Évaluer accessibilité / sécurité / intégrité

Pour les sources « Caisse magasins » et « Prix des concurrents (scraping de leurs sites web) », évalue les 3 critères (🔴🟠🟢) et justifie.

<details>
<summary>Voir le corrigé</summary>

**Caisse magasins** : Accessibilité 🟢 (connecteur SQL, droit de lecture demandable à la DSI) · Sécurité 🟠 (données perso → chiffrement + compte lecture seule indispensables) · Intégrité 🟢 (source transactionnelle fiable, mais vérifier doublons/annulations).

**Prix concurrents (scraping)** : Accessibilité 🔴 (pas d'API, le site peut changer ou interdire le scraping dans ses CGU) · Sécurité 🟠 (pas de données perso, mais risque juridique/CGU) · Intégrité 🔴 (HTML fragile, structure pouvant casser, valeurs à fiabiliser).

Conclusion : la caisse est exploitable rapidement ; le scraping concurrents est risqué (légal + technique) et devrait être traité en dernier, voire remplacé par une source d'open data ou un panel d'études.
</details>

### Exercice 3 — Concevoir le processus de collecte (schéma de flux)

À partir de ta cartographie de l'exercice 1, dessine (en ASCII ou sur papier) le schéma de flux complet jusqu'au dashboard de ventes, en plaçant un **entrepôt** et un **datamart « Ventes »**. Indique pour chaque flux la fréquence.

<details>
<summary>Voir le corrigé</summary>

```
Caisse (PostgreSQL) ──[batch quotidien]──┐
ERP stocks (CSV)    ──[quotidien]─────────┤
E-commerce (API GA) ──[quotidien]─────────┼──► ENTREPÔT ──► DATAMART "Ventes" ──► Dashboard
Budgets (Excel)     ──[mensuel]───────────┤      (ETL/ELT)     (structuré, BI)        (Power BI)
Fidélité (SQL)      ──[hebdo, pseudonym.]─┘
```

Bonnes pratiques attendues : entrepôt central, datamart thématique, fréquences alignées sur le besoin, pseudonymisation de la source fidélité avant intégration. La transformation/nettoyage (ETL) est mentionnée même si elle sera implémentée en 3.2.
</details>

### Exercice 4 — Choisir les outils

Pour chacune des sources de NordRetail, propose un outil de collecte adapté et justifie en une phrase (besoin, volume, fréquence, compétences).

<details>
<summary>Voir le corrigé</summary>

- **Caisse SQL** : connecteur SQL natif du BI ou Python `SQLAlchemy` — accès direct, structuré, batch nocturne.
- **ERP CSV** : Power Query ou `pandas` — fichier simple, quotidien, faible volume.
- **E-commerce GA** : connecteur Google Analytics ou outil ELT (Airbyte) — API SaaS, MAJ régulière, peu de maintenance.
- **Budgets Excel** : import Power Query — mensuel, manuel acceptable vu la fréquence.
- **Fidélité SQL** : connecteur SQL + étape de pseudonymisation — données perso, hebdomadaire.

Justification transverse : on privilégie des connecteurs standards (maintenables) et on réserve le code Python aux cas sans connecteur.
</details>

### Exercice 5 — RGPD & documentation (cas pratique)

La direction marketing te demande de collecter aussi le **numéro de téléphone** et la **date de naissance** des clients fidélité « pour avoir des stats sympas ». Quelle est ta réponse argumentée ? Quels éléments RGPD documentes-tu ?

<details>
<summary>Voir le corrigé</summary>

Réponse : **refuser la collecte non justifiée** au nom de la **minimisation**. Le dashboard de ventes n'a besoin ni du téléphone ni de la date de naissance pour analyser le CA. Collecter « pour avoir des stats sympas » n'est pas une **finalité** valable et viole le principe de minimisation.

À documenter : la finalité réelle, la base légale (consentement pour le programme fidélité), les seules données nécessaires (n° fidélité pseudonymisé, montant, date d'achat, magasin), la durée de conservation, les mesures de sécurité. Si le marketing a un vrai besoin distinct, il fera l'objet d'un **traitement séparé** avec sa propre base légale.
</details>

---

## Vidéos d'auto-formation

> Les liens directs ont été vérifiés quand c'était possible ; les autres pointent vers une **recherche YouTube** (chaîne/sujet fiable) pour t'éviter tout lien mort ou inventé.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| ETL / ELT : comprendre l'essentiel en 4 minutes | DataBird | FR | ~4 min | https://www.youtube.com/watch?v=_QP-Kblt61U | La logique Extract-Transform-Load et la différence ETL/ELT, version express en français |
| Devenir Analytics Engineer (collecte & pipelines) | DataBird | FR | ~variable | https://www.youtube.com/watch?v=5NcQqhTd4X8 | Comment on structure la collecte et l'alimentation d'un entrepôt côté métier |
| Chaîne DataBird (data engineering & analytics FR) | DataBird | FR | — | https://www.youtube.com/channel/UCDxL97NthSZuwAfxFyfhuhA | Playlist francophone : ETL, entrepôt, métiers de la data |
| What is ETL? / Data Warehouse vs Data Lake | IBM Technology | EN | ~5–8 min | https://www.youtube.com/results?search_query=IBM+Technology+what+is+ETL+data+warehouse+data+lake | Définitions claires et schématisées d'ETL, entrepôt et data lake (chaîne de référence) |
| Data Analyst Bootcamp — fondamentaux | Alex The Analyst | EN | série | https://www.youtube.com/@AlexTheAnalyst | Vue d'ensemble du métier de DA, dont les étapes de collecte et de préparation |

---

## Quiz (5 QCM)

**Q1.** La fréquence de **collecte** d'une source doit être déterminée principalement par :
- a) La fréquence à laquelle la source change
- b) Le besoin métier réel
- c) La puissance du serveur
- d) La taille de l'équipe

**Q2.** Quelle affirmation décrit le mieux un **data warehouse** ?
- a) Un dépôt de données brutes tous formats, structurées à la lecture
- b) Un dépôt central de données structurées et nettoyées, optimisé pour la BI
- c) Une base de production transactionnelle
- d) Un simple dossier de fichiers CSV

**Q3.** Dans **ETL**, la lettre « T » correspond à :
- a) Transfert
- b) Test
- c) Transformation
- d) Téléchargement

**Q4.** Le principe RGPD de **minimisation** signifie :
- a) Réduire la taille des fichiers
- b) Ne collecter que les données nécessaires à la finalité
- c) Minimiser le nombre de sources
- d) Compresser les données personnelles

**Q5.** Un **datamart** est :
- a) Un magasin de données physique
- b) Un sous-ensemble thématique d'un entrepôt dédié à un métier
- c) Un outil de scraping
- d) Une API de collecte

<details>
<summary>Voir les réponses</summary>

**Q1 : b** — on cale la collecte sur le besoin métier, jamais plus souvent que nécessaire.
**Q2 : b** — l'entrepôt = structuré, nettoyé, schema-on-write, pour la BI (le a) décrit un data lake).
**Q3 : c** — Extract, **Transform**, Load.
**Q4 : b** — ne collecter que le nécessaire à la finalité déclarée.
**Q5 : b** — un datamart est une vue thématique d'un entrepôt (ex. datamart « Ventes »).
</details>

---

## À retenir

- **Cartographier d'abord** : inventorie chaque source (type, format, volume, fréquence, propriétaire, données perso) avant tout choix d'outil.
- **Trois critères d'évaluation** : accessibilité (puis-je y accéder ?), sécurité (comment je la protège ?), intégrité (est-elle fiable ?).
- **Centraliser dans un entrepôt** (structuré, BI) ≠ data lake (brut) ; un **datamart** est une vue thématique de l'entrepôt.
- **ETL/ELT** : Extract – Transform – Load, le chemin de la source vers l'entrepôt.
- **L'outil suit le besoin**, jamais l'inverse : volume, fréquence, compétences, coût, maintenabilité.
- **RGPD by design** : base légale, minimisation, finalité, sécurité, pseudonymisation — dès la conception.
- **Documenter, c'est concevoir** : sans doc, pas de processus reproductible ni auditable.
- Souviens-toi : **garbage in, garbage out** — la qualité du dashboard commence à la collecte.
