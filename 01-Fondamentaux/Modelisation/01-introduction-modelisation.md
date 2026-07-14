[🏠 Accueil](README.md) | [Suivant →](02-dictionnaire-donnees.md)

---

# 01 - Introduction a la Modelisation des Donnees

## 🎯 Objectifs de cette lecon

- Comprendre pourquoi la modelisation est indispensable avant de coder
- Connaitre les 3 niveaux de modelisation : Conceptuel, Logique, Physique
- Decouvrir l'histoire et les principes de la methode MERISE
- Comparer MERISE, UML et Entity-Relationship
- Maitriser le workflow complet : du besoin metier au script SQL
- Comprendre l'importance de la modelisation pour le Data Engineer

---

## 1. Pourquoi modeliser avant de coder ?

### 1.1 L'analogie de l'architecte

Imaginez construire une maison sans plan. Vous commencez par poser des briques, puis vous realisez que la salle de bain est trop petite, que l'escalier ne mene nulle part, et que les fondations ne supportent pas l'etage. Vous demolissez, vous recommencez. Temps perdu, argent gaspille.

**La modelisation des donnees, c'est le plan de l'architecte pour votre base de donnees.**

```
Sans modelisation :                   Avec modelisation :

  Besoin → Code → Bugs →              Besoin → Modele → Validation →
  Refonte → Re-code → Bugs →          Code → Succes
  Abandon du projet
```

### 1.2 Les consequences d'une mauvaise modelisation

| Probleme | Consequence | Cout |
|----------|-------------|------|
| Donnees dupliquees | Incoherences, espace disque gaspille | Maintenance x3 |
| Relations manquantes | Jointures impossibles, perte d'information | Refonte complete |
| Types de donnees inadaptes | Erreurs de calcul, perte de precision | Bugs en production |
| Pas de contraintes | Donnees invalides en base | Qualite des donnees = 0 |
| Pas de cles etrangeres | Orphelins, integrite violee | Rapports faux |

### 1.3 Ce que la modelisation apporte

- **Communication** : un MCD est lisible par les developpeurs ET les metiers
- **Documentation** : le modele est la documentation vivante de vos donnees
- **Qualite** : les contraintes sont pensees des la conception
- **Performance** : les index et le partitionnement sont anticipes
- **Evolutivite** : un bon modele s'enrichit facilement sans tout casser

💡 **Conseil** : En Data Engineering, la qualite de vos pipelines depend directement de la qualite de votre modele de donnees. Un pipeline ETL sur un schema mal concu produira des donnees inutilisables.

---

## 2. Les 3 niveaux de modelisation

La modelisation se fait en 3 etapes progressives, du plus abstrait au plus concret :

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   NIVEAU CONCEPTUEL (MCD)                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  "QUOI ?"                                               │   │
│   │  - Entites, Associations, Cardinalites                  │   │
│   │  - Independant de toute technologie                     │   │
│   │  - Langage commun metier / technique                    │   │
│   │  - Exemple : Un CLIENT passe des COMMANDES              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼ Transformation                      │
│   NIVEAU LOGIQUE (MLD)                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  "COMMENT ? (structure)"                                │   │
│   │  - Tables, Colonnes, Cles primaires, Cles etrangeres   │   │
│   │  - Modele relationnel (tables et relations)             │   │
│   │  - Normalisation (1NF, 2NF, 3NF)                       │   │
│   │  - Exemple : Table client(id_client PK, nom, email)    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼ Implementation                      │
│   NIVEAU PHYSIQUE (MPD)                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  "COMMENT ? (technique)"                                │   │
│   │  - SQL DDL : CREATE TABLE, types exacts, contraintes    │   │
│   │  - Index, partitionnement, tablespaces                  │   │
│   │  - Specifique au SGBD choisi (PostgreSQL, MySQL...)     │   │
│   │  - Exemple : CREATE TABLE client (                      │   │
│   │              id_client SERIAL PRIMARY KEY, ...)          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Niveau Conceptuel - MCD (Modele Conceptuel de Donnees)

Le MCD repond a la question **"QUOI ?"** : quelles sont les donnees du systeme et comment sont-elles liees entre elles ?

**Caracteristiques :**
- Independant de toute technologie ou SGBD
- Utilise le vocabulaire du metier (Client, Commande, Produit)
- Comprehensible par les non-techniciens
- Base sur les entites, associations et cardinalites

**Qui le lit ?**
- Le client / Product Owner (validation fonctionnelle)
- L'architecte donnees (validation technique)
- Le Data Engineer (comprehension du domaine)

### 2.2 Niveau Logique - MLD (Modele Logique de Donnees)

Le MLD repond a la question **"COMMENT structurer ?"** : comment organiser les donnees en tables relationnelles ?

**Caracteristiques :**
- Derive du MCD par des regles de transformation precises
- Exprime en termes de tables, colonnes, cles
- Inclut la normalisation (elimination des redondances)
- Encore independant du SGBD specifique

**Qui le lit ?**
- Le DBA (administration)
- Le Data Engineer (conception des pipelines)
- Le developpeur backend (acces aux donnees)

### 2.3 Niveau Physique - MPD (Modele Physique de Donnees)

Le MPD repond a la question **"COMMENT implementer ?"** : quel code SQL ecrire concretement ?

**Caracteristiques :**
- Specifique a un SGBD (PostgreSQL, MySQL, SQL Server...)
- Inclut les types de donnees exacts, les index, le partitionnement
- Contient le script SQL DDL executable
- Optimise pour la performance

**Qui le lit ?**
- Le DBA (deploiement, maintenance)
- Le Data Engineer (creation des tables dans le pipeline)
- Le DevOps (automatisation des migrations)

---

## 3. La methode MERISE

### 3.1 Origine et histoire

**MERISE** (Methode d'Etude et de Realisation Informatique pour les Systemes d'Entreprise) est une methode francaise de conception de systemes d'information, creee en **1978** par un consortium comprenant :

- Hubert Tardieu
- Arnold Rochfeld
- Rene Colletti
- Et des equipes du CETE d'Aix-en-Provence et du CTI (ministere de l'Industrie)

**Historique :**

| Annee | Evenement |
|-------|-----------|
| 1978 | Creation de MERISE par le ministere de l'Industrie francais |
| 1979 | Premiere publication officielle |
| 1980s | Adoption massive dans les administrations et entreprises francaises |
| 1990s | MERISE/2 : evolution pour integrer l'oriente objet |
| 2000s | Concurrence avec UML, mais MERISE reste la reference pour la modelisation de donnees |
| Aujourd'hui | Toujours enseigne et utilise en France, notamment dans les formations et certifications |

### 3.2 Les principes fondamentaux de MERISE

1. **Approche systemique** : le systeme d'information est vu comme un tout coherent
2. **Separation donnees/traitements** : on modelise les donnees (MCD) et les traitements (MCT) separement
3. **3 niveaux d'abstraction** : conceptuel, logique, physique (que nous etudions)
4. **Cycle de vie** : schema directeur → etude prealable → etude detaillee → realisation → mise en oeuvre
5. **Validation progressive** : chaque niveau est valide avant de passer au suivant

### 3.3 Pourquoi MERISE est encore pertinente

- **Rigueur** : les regles de passage MCD → MLD sont automatiques et sans ambiguite
- **Pedagogie** : la notation est simple a apprendre et a enseigner
- **Certification** : exigee dans de nombreuses certifications en France
- **Universalite** : le MCD MERISE se transforme vers n'importe quel SGBD relationnel
- **Outils** : des logiciels gratuits comme Looping automatisent le workflow

---

## 4. MERISE vs UML vs Entity-Relationship

### 4.1 Tableau comparatif

| Critere | MERISE | UML (diagramme de classes) | Entity-Relationship (Chen) |
|---------|--------|---------------------------|---------------------------|
| **Origine** | France (1978) | International (1997) | USA - Peter Chen (1976) |
| **Notation cardinalites** | (0,1), (1,1), (0,n), (1,n) | 0..1, 1, 0..*, 1..* | 1, N, M |
| **Placement cardinalites** | Cote de l'entite concernee | Cote de l'entite opposee | Variable |
| **Force** | Modelisation de donnees | Modelisation objet complete | Simplicite |
| **Faiblesse** | Peu adapte a l'objet | Complexe pour les donnees seules | Moins rigoureux |
| **Usage principal** | BDD relationnelles, SI | Applications orientees objet | Enseignement, documentation |
| **Outils** | Looping, PowerAMC | Enterprise Architect, StarUML | draw.io, Lucidchart |
| **En France** | Tres utilise (certifications) | Utilise en dev logiciel | Peu utilise seul |

### 4.2 Quand utiliser quoi ?

- **MERISE** : quand vous concevez une base de donnees relationnelle, ou dans un contexte francais
- **UML** : quand vous concevez une application objet complete (classes, sequences, cas d'utilisation)
- **Entity-Relationship** : quand vous avez besoin d'un schema simple et rapide, ou dans un contexte international

💡 **Pour le Data Engineer** : MERISE est votre outil principal pour la modelisation des bases de donnees operationnelles. Pour le Data Warehouse, vous utiliserez aussi les schemas en etoile et en flocon (modelisation dimensionnelle), qui feront l'objet d'un module dedie.

---

## 5. Le workflow complet de modelisation

### 5.1 Les etapes du processus

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. BESOINS  │────→│ 2. DICTION-  │────→│   3. MCD     │
│    METIER    │     │    NAIRE     │     │ (Conceptuel) │
│              │     │  DE DONNEES  │     │              │
│ Interviews,  │     │ Entites,     │     │ Entites,     │
│ cahier des   │     │ attributs,   │     │ associations,│
│ charges      │     │ types, RG    │     │ cardinalites │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   6. SQL     │←────│   5. MPD     │←────│   4. MLD     │
│  (Scripts)   │     │ (Physique)   │     │  (Logique)   │
│              │     │              │     │              │
│ CREATE TABLE,│     │ Types SGBD,  │     │ Tables, PK,  │
│ INSERT,      │     │ index,       │     │ FK, normali- │
│ migrations   │     │ partitions   │     │ sation       │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 5.2 Detail de chaque etape

**Etape 1 - Recueil des besoins metier**
- Interviews avec les parties prenantes
- Analyse du cahier des charges
- Identification des regles de gestion

**Etape 2 - Dictionnaire de donnees**
- Lister toutes les entites identifiees
- Definir les attributs de chaque entite
- Specifier les types, tailles, contraintes
- Documenter les regles de gestion

**Etape 3 - MCD (Modele Conceptuel)**
- Dessiner les entites et leurs attributs
- Tracer les associations entre entites
- Placer les cardinalites MERISE
- Valider avec le metier

**Etape 4 - MLD (Modele Logique)**
- Appliquer les regles de transformation MCD → MLD
- Normaliser (1NF, 2NF, 3NF)
- Identifier les cles primaires et etrangeres
- Verifier l'integrite referentielle

**Etape 5 - MPD (Modele Physique)**
- Choisir les types de donnees specifiques au SGBD
- Definir les index necessaires
- Planifier le partitionnement si necessaire
- Prevoir les strategies de stockage

**Etape 6 - Scripts SQL**
- Ecrire les CREATE TABLE
- Ajouter les contraintes (PK, FK, CHECK, UNIQUE)
- Creer les index
- Preparer les scripts de migration

---

## 6. Pourquoi c'est essentiel pour le Data Engineer

### 6.1 La qualite des donnees commence par le modele

En tant que Data Engineer, vous etes responsable de la **qualite** et de la **fiabilite** des donnees qui alimentent les Data Scientists, les analystes et les tableaux de bord. Un modele de donnees bien concu est votre premiere ligne de defense :

```sql
-- ❌ Sans modelisation : aucune garantie
CREATE TABLE donnees (
    id INT,
    info TEXT,
    valeur TEXT,
    date TEXT
);
-- Qu'est-ce que "info" ? Quelle est la precision de "valeur" ?
-- Le champ "date" contient-il "2024-01-15" ou "15 janvier 2024" ?

-- ✅ Avec modelisation : donnees fiables par construction
CREATE TABLE mesure_capteur (
    id_mesure       SERIAL PRIMARY KEY,
    id_capteur      INT NOT NULL REFERENCES capteur(id_capteur),
    valeur_mesuree  DECIMAL(10,4) NOT NULL,
    unite_mesure    VARCHAR(10) NOT NULL CHECK (unite_mesure IN ('°C', '%HR', 'hPa')),
    date_mesure     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    est_valide      BOOLEAN NOT NULL DEFAULT TRUE
);
-- Chaque colonne est documentee, typee, contrainte. Pas d'ambiguite.
```

### 6.2 Cas d'usage en Data Engineering

| Contexte | Utilisation de la modelisation |
|----------|-------------------------------|
| **Pipeline ETL** | Modeliser les tables source, staging et destination |
| **Data Warehouse** | Concevoir les schemas en etoile (faits + dimensions) |
| **Data Lake** | Definir les schemas des fichiers Parquet/Delta |
| **API de donnees** | Structurer les endpoints et les reponses JSON |
| **Monitoring** | Modeliser les tables de logs, metriques, alertes |
| **IoT** | Concevoir les schemas de series temporelles |

### 6.3 Le Data Engineer comme architecte des donnees

```
                    ┌─────────────────────┐
                    │   Data Scientist    │
                    │   "J'ai besoin de   │
                    │   donnees propres"  │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Data Engineer     │
                    │   MODELISATION      │◄── Vous etes ici !
                    │   + Pipelines       │
                    │   + Qualite         │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Base de donnees   │
                    │   Bien modelisee    │
                    │   = Donnees fiables │
                    └─────────────────────┘
```

---

## 7. Resume

| Concept | A retenir |
|---------|-----------|
| Modelisation | Plan d'architecte avant la construction de la BDD |
| MCD | Niveau conceptuel : QUOI ? (entites, associations, cardinalites) |
| MLD | Niveau logique : COMMENT structurer ? (tables, cles, normalisation) |
| MPD | Niveau physique : COMMENT implementer ? (SQL DDL, index, types) |
| MERISE | Methode francaise (1978), rigoureuse, encore tres utilisee |
| Workflow | Besoins → Dictionnaire → MCD → MLD → MPD → SQL |

---

## 📝 Auto-evaluation

1. Quels sont les 3 niveaux de modelisation et a quelle question chacun repond-il ?
2. Citez 3 consequences d'une base de donnees non modelisee.
3. Quelle est la difference principale entre la notation des cardinalites en MERISE et en UML ?
4. Dans quel ordre se deroule le workflow de modelisation ?
5. Pourquoi le Data Engineer doit-il maitriser la modelisation ?

---

[🏠 Accueil](README.md) | [Suivant →](02-dictionnaire-donnees.md)

---

**Academy** - Formation Data Engineer
