[← Precedent](05-modele-physique-mpd.md) | [🏠 Accueil](README.md) | [Suivant →](07-exercices.md)

---

# 06 - Outils Pratiques de Modelisation

## 🎯 Objectifs de cette lecon

- Connaitre les principaux outils de modelisation de donnees
- Savoir utiliser Looping pour la methode MERISE (MCD → MLD → MPD → SQL)
- Utiliser MySQL Workbench pour le forward et reverse engineering
- Prototyper rapidement avec dbdiagram.io et sa syntaxe DBML
- Choisir l'outil adapte a chaque situation

---

## 1. Looping (Recommande pour MERISE)

### 1.1 Presentation

**Looping** est un logiciel **gratuit** et **francais** dedie a la modelisation de donnees avec la methode MERISE. C'est l'outil de reference pour les formations et certifications en France.

| Caracteristique | Detail |
|----------------|--------|
| **Prix** | Gratuit |
| **Editeur** | Patrick Music (developpeur independant francais) |
| **Plateforme** | Windows natif (fonctionne sur Mac/Linux via Wine ou machine virtuelle) |
| **Methode** | MERISE (MCD, MLD, MPD) |
| **Export** | SQL (PostgreSQL, MySQL, Oracle, SQL Server, SQLite) |
| **Site officiel** | https://www.looping-mcd.fr/ |

### 1.2 Installation

**Sur Windows :**
1. Telecharger Looping depuis https://www.looping-mcd.fr/
2. Decompresser le fichier ZIP
3. Lancer `Looping.exe` (pas d'installation necessaire, c'est un portable)

**Sur Mac/Linux (alternatives) :**
- **Option 1** : Utiliser **Wine** ou **CrossOver** pour executer Looping
- **Option 2** : Utiliser une **machine virtuelle** Windows (VirtualBox, Parallels)
- **Option 3** : Utiliser **un autre outil** (dbdiagram.io) et dessiner le MCD sur papier

💡 **Conseil formation** : si vous etes sur Mac, installez Wine avec Homebrew :
```bash
brew install --cask wine-stable
# Puis lancez Looping via Wine
wine Looping.exe
```

### 1.3 Fonctionnalites principales

| Fonctionnalite | Description |
|----------------|-------------|
| **Editeur MCD** | Interface drag-and-drop pour creer entites et associations |
| **Cardinalites** | Cliquer sur les liens pour definir (0,1), (1,1), (0,n), (1,n) |
| **Transformation automatique** | MCD → MLD en un clic (applique les regles de passage) |
| **Transformation MLD → MPD** | MLD → SQL DDL pour le SGBD choisi |
| **Export SQL** | Genere les scripts CREATE TABLE, ALTER TABLE, etc. |
| **Export image** | Exporte le diagramme en PNG, BMP |
| **Reverse engineering** | Importe un script SQL pour generer le MLD |
| **Dictionnaire** | Genere automatiquement le dictionnaire de donnees |
| **Verification** | Detecte les erreurs de modelisation |

### 1.4 Workflow type avec Looping

```
Etape 1 : Creer un nouveau MCD
┌────────────────────────────────────────┐
│  Fichier → Nouveau → MCD              │
│                                        │
│  - Ajouter des entites (bouton Entite) │
│  - Definir les attributs               │
│  - Souligner l'identifiant             │
│  - Tracer les associations             │
│  - Definir les cardinalites            │
└────────────────────────────────────────┘
            │
            ▼
Etape 2 : Transformer en MLD
┌────────────────────────────────────────┐
│  MCD → Transformer → MLD              │
│                                        │
│  Looping applique automatiquement :    │
│  - Regle 1 : Entites → Tables         │
│  - Regle 2 : FK pour (x,1)-(x,n)     │
│  - Regle 3 : Tables jonction N:M      │
│  - Verification de la normalisation    │
└────────────────────────────────────────┘
            │
            ▼
Etape 3 : Generer le SQL
┌────────────────────────────────────────┐
│  MLD → Generer SQL → PostgreSQL        │
│                                        │
│  Looping genere :                      │
│  - CREATE TABLE avec types             │
│  - PRIMARY KEY                         │
│  - FOREIGN KEY                         │
│  - NOT NULL, UNIQUE                    │
│  - Dans le bon ordre de creation       │
└────────────────────────────────────────┘
            │
            ▼
Etape 4 : Exporter
┌────────────────────────────────────────┐
│  Fichier → Exporter → SQL / Image     │
│                                        │
│  - Script .sql pret a executer         │
│  - Image .png pour la documentation    │
│  - Dictionnaire de donnees en texte    │
└────────────────────────────────────────┘
```

### 1.5 Raccourcis utiles dans Looping

| Action | Raccourci |
|--------|----------|
| Nouvelle entite | Double-clic sur le canevas |
| Nouvelle association | Clic sur le bouton "Association" puis clic sur les entites |
| Modifier cardinalites | Double-clic sur le lien |
| Transformer MCD → MLD | Menu MCD → Passage au MLD |
| Generer SQL | Menu MLD → Generation SQL |
| Verification | Menu Outils → Verification |

---

## 2. MySQL Workbench

### 2.1 Presentation

**MySQL Workbench** est un outil gratuit et multiplateforme edite par Oracle. Il offre des fonctionnalites de modelisation visuelle, d'administration de bases de donnees et de developpement SQL.

| Caracteristique | Detail |
|----------------|--------|
| **Prix** | Gratuit (Community Edition) |
| **Editeur** | Oracle |
| **Plateforme** | Windows, Mac, Linux |
| **Methode** | Entity-Relationship (notation Crow's Foot / UML, pas MERISE) |
| **SGBD** | MySQL principalement |
| **Site** | https://www.mysql.com/products/workbench/ |

### 2.2 Forward Engineering (Modele → SQL)

Le forward engineering consiste a **creer un modele graphique** puis a **generer le SQL**.

```
Workflow Forward Engineering :

1. File → New Model
2. Ajouter un diagramme EER (Enhanced Entity-Relationship)
3. Creer les tables avec l'outil Table
4. Definir les colonnes, types, PK, FK
5. Tracer les relations entre tables
6. Database → Forward Engineer → Generer le script SQL
```

**Ce que MySQL Workbench genere :**
- Script CREATE TABLE complet
- Cles primaires et etrangeres
- Index
- Schemas et vues

### 2.3 Reverse Engineering (Base existante → Modele)

Le reverse engineering consiste a **se connecter a une base existante** et a **generer le diagramme** automatiquement.

```
Workflow Reverse Engineering :

1. Se connecter a la base de donnees MySQL
2. Database → Reverse Engineer
3. Selectionner les tables a inclure
4. MySQL Workbench genere le diagramme EER
5. Reorganiser les tables pour la lisibilite
6. Exporter en image ou PDF
```

💡 **Usage Data Engineer** : le reverse engineering est extremement utile quand vous reprenez un projet existant. En quelques clics, vous visualisez la structure complete d'une base de donnees.

### 2.4 Diagrammes EER

Les diagrammes **EER** (Enhanced Entity-Relationship) de MySQL Workbench utilisent la notation **Crow's Foot** :

```
Notation Crow's Foot dans MySQL Workbench :

  ──||──  : un et un seul (1:1 obligatoire)
  ──|○──  : zero ou un (0:1)
  ──<──   : un ou plusieurs (1:N)
  ──○<──  : zero ou plusieurs (0:N)
```

⚠️ **Attention** : MySQL Workbench n'utilise PAS la notation MERISE. Si vous devez produire des MCD MERISE, utilisez Looping.

---

## 3. dbdiagram.io

### 3.1 Presentation

**dbdiagram.io** est un outil **en ligne** pour creer des diagrammes de bases de donnees rapidement en ecrivant du code DBML.

| Caracteristique | Detail |
|----------------|--------|
| **Prix** | Gratuit (plan de base), Pro payant |
| **Editeur** | Holistics Software |
| **Plateforme** | Navigateur web (rien a installer) |
| **Methode** | Schema relationnel (pas de MCD) |
| **Export** | SQL (PostgreSQL, MySQL, SQL Server), PDF, PNG |
| **Site** | https://dbdiagram.io |

### 3.2 Syntaxe DBML (Database Markup Language)

DBML est un langage simple pour decrire des schemas de bases de donnees :

```dbml
// Exemple complet e-commerce en DBML

Table categorie {
  id_categorie int [pk, increment]
  nom_categorie varchar(100) [not null, unique]
  description_categorie text
  date_creation timestamp [default: `now()`]
}

Table client {
  id_client int [pk, increment]
  nom varchar(100) [not null]
  prenom varchar(100) [not null]
  email varchar(255) [not null, unique]
  telephone varchar(20)
  date_inscription timestamp [not null, default: `now()`]
  est_actif boolean [not null, default: true]
}

Table produit {
  id_produit int [pk, increment]
  nom_produit varchar(200) [not null]
  description text
  prix_unitaire decimal(10,2) [not null]
  stock_disponible int [not null, default: 0]
  id_categorie int [not null, ref: > categorie.id_categorie]
}

Table commande {
  id_commande int [pk, increment]
  date_commande timestamp [not null, default: `now()`]
  statut varchar(20) [not null, default: 'en_attente', note: 'en_attente, validee, expediee, livree, annulee']
  montant_total decimal(10,2) [not null]
  id_client int [not null, ref: > client.id_client]
}

Table ligne_commande {
  id_commande int [not null, ref: > commande.id_commande]
  id_produit int [not null, ref: > produit.id_produit]
  quantite int [not null]
  prix_unitaire_cmd decimal(10,2) [not null]

  indexes {
    (id_commande, id_produit) [pk]
  }
}
```

### 3.3 Syntaxe des relations en DBML

```dbml
// Relation un-a-plusieurs (1:N)
ref: commande.id_client > client.id_client
// ou inline : id_client int [ref: > client.id_client]

// Relation plusieurs-a-plusieurs (N:M)
// → utiliser une table de jonction (pas de syntaxe directe)

// Relation un-a-un (1:1)
ref: badge.id_employe - employe.id_employe

// Symboles :
// >  : many-to-one
// <  : one-to-many
// -  : one-to-one
// <> : many-to-many
```

### 3.4 Avantages de dbdiagram.io

- ✅ **Rien a installer** : fonctionne dans le navigateur
- ✅ **Rapide** : quelques lignes de DBML et le diagramme est genere
- ✅ **Export SQL** : genere du PostgreSQL, MySQL ou SQL Server
- ✅ **Partage** : URL partageable pour la collaboration
- ✅ **Versionnable** : le code DBML peut etre versionne avec Git

### 3.5 Limites de dbdiagram.io

- ❌ **Pas de MCD MERISE** : uniquement des schemas relationnels (MLD/MPD)
- ❌ **Pas de cardinalites MERISE** : notation simplifiee
- ❌ **Plan gratuit limite** : nombre de diagrammes limite
- ❌ **Pas de reverse engineering** : pas de connexion a une base existante

---

## 4. draw.io / diagrams.net

### 4.1 Presentation

**draw.io** (renomme diagrams.net) est un outil de dessin de diagrammes generaliste et gratuit. Il peut etre utilise pour des diagrammes personnalises (MCD, MLD, architecture).

| Caracteristique | Detail |
|----------------|--------|
| **Prix** | Gratuit et open source |
| **Editeur** | JGraph Ltd |
| **Plateforme** | Navigateur web, application desktop, integration VS Code |
| **Usage** | Diagrammes libres (pas specifique aux bases de donnees) |
| **Site** | https://www.diagrams.net |

### 4.2 Utilisation pour la modelisation

**Forces :**
- ✅ Totalement libre : dessinez ce que vous voulez
- ✅ Bibliotheques de formes pour les diagrammes ER et UML
- ✅ Integration avec Google Drive, OneDrive, GitHub
- ✅ Export en PNG, SVG, PDF
- ✅ Application desktop disponible (pas besoin d'internet)

**Limites :**
- ❌ Pas de generation automatique MCD → MLD
- ❌ Pas de generation SQL
- ❌ Pas de verification de coherence
- ❌ Tout est manuel (dessin libre)

### 4.3 Quand utiliser draw.io ?

- Pour dessiner des **diagrammes d'architecture** (pipeline, infrastructure)
- Pour creer des **schemas personnalises** que les autres outils ne supportent pas
- Pour des **presentations** ou de la **documentation**
- Quand vous avez besoin d'un outil **gratuit et sans inscription**

💡 **Astuce** : dans draw.io, utilisez le template "Entity Relationship" (disponible dans les templates) pour dessiner des MCD rapidement avec les bonnes formes.

---

## 5. Autres outils notables

### 5.1 PowerAMC / SAP PowerDesigner

- Outil professionnel de reference (ex-Sybase, maintenant SAP)
- Support complet de MERISE, UML, data warehouse
- Tres utilise dans les grandes entreprises
- **Prix** : payant (licence entreprise)
- **Plateforme** : Windows uniquement

### 5.2 DBeaver

- Outil gratuit d'administration de bases de donnees
- Inclut un editeur de diagrammes ER (reverse engineering)
- Supporte tous les SGBD (PostgreSQL, MySQL, Oracle, SQL Server, SQLite...)
- Ideal pour visualiser la structure d'une base existante
- **Site** : https://dbeaver.io/

### 5.3 pgModeler

- Outil specialise PostgreSQL
- Modelisation visuelle avec generation SQL
- Reverse engineering depuis PostgreSQL
- **Prix** : payant (licence modique)
- **Site** : https://pgmodeler.io/

---

## 6. Tableau comparatif

| Critere | Looping | MySQL Workbench | dbdiagram.io | draw.io |
|---------|---------|-----------------|-------------|---------|
| **Prix** | Gratuit | Gratuit | Freemium | Gratuit |
| **Plateforme** | Windows | Win/Mac/Linux | Web | Web/Desktop |
| **MERISE (MCD)** | ✅ Oui | ❌ Non | ❌ Non | ⚠️ Manuel |
| **MLD/MPD** | ✅ Oui | ✅ Oui | ✅ Oui | ⚠️ Manuel |
| **Generation SQL** | ✅ Multi-SGBD | ✅ MySQL | ✅ Multi-SGBD | ❌ Non |
| **Reverse engineering** | ✅ SQL→MLD | ✅ BDD→Diagramme | ❌ Non | ❌ Non |
| **Transformation auto** | ✅ MCD→MLD | ❌ Non | ❌ Non | ❌ Non |
| **Collaboration** | ❌ Fichier local | ❌ Fichier local | ✅ URL partagee | ✅ Cloud |
| **Facilite d'utilisation** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Ideal pour** | MERISE, certification | Admin MySQL | Prototypage rapide | Diagrammes libres |

---

## 7. Recommandations par contexte

### 7.1 Pour la formation et la modelisation MERISE

📐 **Utilisez Looping** : c'est le seul outil gratuit qui supporte nativement MERISE avec la transformation automatique MCD → MLD → SQL. C'est l'outil attendu dans les certifications.

### 7.2 Pour le prototypage rapide

📐 **Utilisez dbdiagram.io** : en quelques minutes, vous avez un schema relationnel propre avec du code DBML versionnable et exportable en SQL.

### 7.3 Pour un projet en equipe

📐 **Utilisez dbdiagram.io** (partage par URL) ou **draw.io** (integration Git/Drive) pour faciliter la collaboration.

### 7.4 Pour le reverse engineering d'une base existante

📐 **Utilisez DBeaver** (gratuit, multi-SGBD) ou **MySQL Workbench** (si MySQL).

### 7.5 Pour la documentation d'architecture

📐 **Utilisez draw.io** : il excelle pour les diagrammes d'architecture de pipelines, les schemas de flux de donnees, et les presentations.

---

## 8. Workflow recommande pour la formation

```
1. Papier + Crayon        → Premier brouillon du MCD (rapide, iteratif)
2. Looping                → MCD propre, transformation MLD, generation SQL
3. dbdiagram.io           → Prototypage rapide du MLD pour validation equipe
4. PostgreSQL (psql/DBeaver) → Execution du SQL, tests, validation
5. draw.io                → Schema d'architecture pour la documentation
```

---

## 9. Resume

| Outil | Usage principal | Force cle |
|-------|----------------|-----------|
| **Looping** | MCD MERISE (certification) | Transformation auto MCD → MLD → SQL |
| **MySQL Workbench** | Admin MySQL, reverse engineering | Forward + reverse engineering |
| **dbdiagram.io** | Prototypage rapide | Code DBML, rapide, partage URL |
| **draw.io** | Diagrammes libres | Gratuit, flexible, integration Cloud |
| **DBeaver** | Administration multi-SGBD | Reverse engineering, gratuit |

---

## 📝 Auto-evaluation

1. Quel outil utiliseriez-vous pour produire un MCD en notation MERISE ? Pourquoi ?
2. Ecrivez le code DBML pour le schema IoT (capteur, zone, mesure, alerte).
3. Quel est l'avantage du reverse engineering ? Dans quelle situation l'utiliseriez-vous ?
4. Pourquoi est-il recommande de commencer par un brouillon papier avant d'utiliser un outil ?
5. Quel outil choisiriez-vous pour un projet en equipe distribue ? Justifiez.

---

[← Precedent](05-modele-physique-mpd.md) | [🏠 Accueil](README.md) | [Suivant →](07-exercices.md)

---

**Academy** - Formation Data Engineer
