[← Precedent](06-outils-pratiques.md) | [🏠 Accueil](README.md)

---

# 07 - Exercices de Modelisation

## 🎯 Objectifs

- Mettre en pratique toutes les competences acquises dans les lecons precedentes
- Progresser du niveau debutant (lecture) au niveau avance (projet complet)
- S'entrainer avec des exercices realistes
- Appliquer la modelisation dans un contexte Data Engineering

---

## Niveau 1 - Lecture et Analyse

### 📝 Exercice 1.1 : Lecture d'un MCD

Observez le MCD suivant et repondez aux questions :

```
┌──────────────────┐                                    ┌──────────────────┐
│    MEDECIN       │                                    │    PATIENT       │
├──────────────────┤                                    ├──────────────────┤
│ id_medecin       │                                    │ id_patient       │
│ nom              │                                    │ nom              │
│ prenom           │                                    │ prenom           │
│ specialite       │                                    │ date_naissance   │
│ telephone        │                                    │ numero_secu      │
└───────┬──────────┘                                    │ telephone        │
        │                                               └────────┬─────────┘
        │ (0,n)                                                  │ (0,n)
        │                                                        │
   ┌────┴──────────────────────────────────────────────────┬─────┘
   │                    CONSULTATION                       │
   │               ┌──────────────────┐                    │
   │               │ date_consultation│                    │
   │               │ motif            │                    │
   │               │ diagnostic       │                    │
   │               │ prescription     │                    │
   │               └──────────────────┘                    │
   └───────────────────────────────────────────────────────┘

                              │ (0,n)
                              │
                     ┌────────┴────────┐
                     │    CONCERNE     │
                     └────────┬────────┘
                              │ (1,1)
                              │
                    ┌─────────▼────────┐
                    │   MEDICAMENT     │
                    ├──────────────────┤
                    │ id_medicament    │
                    │ nom_commercial   │
                    │ molecule         │
                    │ dosage           │
                    └──────────────────┘
```

**Questions :**

1. Listez toutes les entites et leurs identifiants.
2. Listez toutes les associations et indiquez si elles sont binaires, ternaires ou reflexives.
3. Quel est le type de relation entre MEDECIN et PATIENT (via CONSULTATION) ? 1:1, 1:N ou N:M ?
4. Un patient peut-il ne jamais avoir consulte ? Justifiez par la cardinalite.
5. L'association CONSULTATION porte-t-elle des attributs ? Lesquels et pourquoi ?
6. Redigez 4 regles de gestion correspondant a ce MCD.
7. Quel est le type de relation entre CONSULTATION et MEDICAMENT ? Pourquoi ?

### 📝 Exercice 1.2 : Detection d'erreurs

Le MCD suivant contient **4 erreurs**. Identifiez-les et proposez des corrections.

```
┌──────────────────┐                              ┌──────────────────┐
│    EMPLOYE       │         TRAVAILLE            │  DEPARTEMENT     │
├──────────────────┤    ┌──────────────┐          ├──────────────────┤
│ email            │────│  salaire     │──────────│ id_departement   │
│ nom              │    └──────────────┘          │ nom_departement  │
│ prenom           │  (1,n)              (1,1)    │ ville            │
│ telephone_1      │                              │ budget           │
│ telephone_2      │                              └──────────────────┘
└──────────────────┘
```

**Indices :**
- Probleme d'identifiant
- Probleme d'attribut multivaleur
- Probleme d'attribut dans l'association
- Probleme de cardinalite

---

## Niveau 1 - Solutions

### Solution 1.1

**1. Entites et identifiants :**

| Entite | Identifiant |
|--------|-------------|
| MEDECIN | id_medecin |
| PATIENT | id_patient |
| MEDICAMENT | id_medicament |

Note : CONSULTATION est une **association** (pas une entite), meme si elle porte des attributs.

**2. Associations :**

| Association | Type | Entites reliees |
|-------------|------|----------------|
| CONSULTATION | Binaire | MEDECIN - PATIENT |
| CONCERNE | Binaire | CONSULTATION - MEDICAMENT |

Note : CONSULTATION relie MEDECIN et PATIENT (binaire N:M). L'association CONCERNE relie une occurrence de CONSULTATION a un MEDICAMENT.

**3.** Relation entre MEDECIN et PATIENT (via CONSULTATION) : **N:M** (plusieurs-a-plusieurs).
- Un medecin peut consulter plusieurs patients → (0,n) cote MEDECIN
- Un patient peut consulter plusieurs medecins → (0,n) cote PATIENT

**4.** Oui, un patient peut ne jamais avoir consulte. La cardinalite **(0,n)** cote PATIENT indique un minimum de **0**. S'il devait obligatoirement avoir au moins une consultation, la cardinalite serait (1,n).

**5.** Oui, CONSULTATION porte des attributs :
- `date_consultation` : la date depend du couple (medecin, patient, moment)
- `motif` : le motif est specifique a cette consultation
- `diagnostic` : le diagnostic est specifique a cette consultation
- `prescription` : la prescription est specifique a cette consultation

Ces attributs n'appartiennent ni au medecin ni au patient seuls, mais au **lien** entre eux a un moment donne.

**6.** Regles de gestion :
- RG1 : Un medecin peut consulter 0 ou N patients
- RG2 : Un patient peut consulter 0 ou N medecins
- RG3 : Chaque consultation est caracterisee par une date, un motif, un diagnostic et une prescription
- RG4 : Une consultation concerne 0 ou N medicaments
- RG5 : Un medicament peut etre concerne par 0 ou N consultations
- RG6 : Un medicament est identifie par un identifiant unique et possede un nom commercial, une molecule et un dosage

**7.** Relation entre CONSULTATION et MEDICAMENT : **N:M** (via CONCERNE).
- (0,n) cote CONSULTATION : une consultation peut concerner 0 ou N medicaments
- (1,1) devrait etre (0,n) si un medicament peut etre prescrit dans plusieurs consultations

### Solution 1.2 : Erreurs detectees

| # | Erreur | Explication | Correction |
|---|--------|-------------|------------|
| 1 | **Identifiant** : `email` comme identifiant de EMPLOYE | L'email peut changer, il n'est pas stable | Ajouter `id_employe` comme identifiant |
| 2 | **Attribut multivaleur** : `telephone_1` et `telephone_2` | Violation du principe d'atomicite, et limite a 2 telephones | Creer une entite TELEPHONE ou un seul attribut `telephone` |
| 3 | **Attribut dans l'association** : `salaire` dans TRAVAILLE | Le salaire depend de l'employe, pas du lien employe-departement (sauf si le salaire change selon le departement) | Deplacer `salaire` dans l'entite EMPLOYE |
| 4 | **Cardinalite** : (1,n) cote EMPLOYE | Un employe travaille dans 1 ou N departements ? C'est inhabituel. Generalement, un employe travaille dans 1 seul departement | Changer en (1,1) cote EMPLOYE |

**MCD corrige :**

```
┌──────────────────┐                              ┌──────────────────┐
│    EMPLOYE       │         TRAVAILLE            │  DEPARTEMENT     │
├──────────────────┤    ┌──────────────┐          ├──────────────────┤
│ id_employe       │────│              │──────────│ id_departement   │
│ nom              │    └──────────────┘          │ nom_departement  │
│ prenom           │  (1,1)              (0,n)    │ ville            │
│ email            │                              │ budget           │
│ telephone        │                              └──────────────────┘
│ salaire          │
└──────────────────┘
```

---

## Niveau 2 - Conception Complete

### 📝 Exercice 2 : Systeme de gestion de bibliotheque

#### Enonce

Une bibliotheque municipale souhaite informatiser la gestion de ses emprunts. Voici les regles de gestion recueillies :

**Regles de gestion :**

| # | Regle |
|---|-------|
| RG1 | Un **livre** est identifie par un ISBN unique. Il possede un titre, une annee de publication, un nombre de pages et une langue |
| RG2 | Un livre peut avoir **un ou plusieurs auteurs** |
| RG3 | Un **auteur** est identifie par un identifiant unique. Il possede un nom, un prenom, une nationalite et une date de naissance |
| RG4 | Un auteur peut avoir ecrit **un ou plusieurs livres** |
| RG5 | Un **adherent** est identifie par un numero de carte unique. Il possede un nom, un prenom, un email, un telephone et une date d'adhesion |
| RG6 | Un adherent peut emprunter **0 ou N livres** au cours du temps |
| RG7 | Un livre peut etre emprunte par **0 ou N adherents** au cours du temps |
| RG8 | Chaque **emprunt** possede une date d'emprunt, une date de retour prevue et une date de retour effective (NULL si pas encore rendu) |
| RG9 | Un adherent ne peut pas emprunter plus de **5 livres simultanement** |
| RG10 | La duree d'un emprunt est de **21 jours maximum** |

#### Travail demande

1. **Dictionnaire de donnees** : redigez le dictionnaire complet (entite, attribut, code, type, taille, obligatoire, identifiant)
2. **MCD** : dessinez le MCD avec les entites, associations et cardinalites MERISE
3. **MLD** : transformez le MCD en MLD en appliquant les regles de passage
4. **SQL DDL** : ecrivez les scripts CREATE TABLE pour PostgreSQL

---

### Solution Niveau 2

#### 1. Dictionnaire de donnees

**Entite : LIVRE**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant |
|----------|------|------|--------|-------------|-------------|
| ISBN | isbn | VARCHAR | 17 | Oui | ✅ Oui |
| Titre | titre | VARCHAR | 300 | Oui | Non |
| Annee publication | annee_publication | INT | - | Oui | Non |
| Nombre de pages | nb_pages | INT | - | Non | Non |
| Langue | langue | VARCHAR | 50 | Oui | Non |

**Entite : AUTEUR**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant |
|----------|------|------|--------|-------------|-------------|
| ID Auteur | id_auteur | INT | - | Oui | ✅ Oui |
| Nom | nom_auteur | VARCHAR | 100 | Oui | Non |
| Prenom | prenom_auteur | VARCHAR | 100 | Oui | Non |
| Nationalite | nationalite | VARCHAR | 50 | Non | Non |
| Date naissance | date_naissance | DATE | - | Non | Non |

**Entite : ADHERENT**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant |
|----------|------|------|--------|-------------|-------------|
| Numero carte | num_carte | VARCHAR | 20 | Oui | ✅ Oui |
| Nom | nom_adherent | VARCHAR | 100 | Oui | Non |
| Prenom | prenom_adherent | VARCHAR | 100 | Oui | Non |
| Email | email | VARCHAR | 255 | Oui | Non |
| Telephone | telephone | VARCHAR | 20 | Non | Non |
| Date adhesion | date_adhesion | DATE | - | Oui | Non |

**Association : EMPRUNT (ADHERENT - LIVRE)**

| Attribut | Code | Type | Taille | Obligatoire |
|----------|------|------|--------|-------------|
| Date emprunt | date_emprunt | DATE | - | Oui |
| Date retour prevue | date_retour_prevue | DATE | - | Oui |
| Date retour effective | date_retour_effective | DATE | - | Non |

#### 2. MCD

```
┌──────────────────┐                                    ┌──────────────────┐
│     AUTEUR       │                                    │    ADHERENT      │
├──────────────────┤                                    ├──────────────────┤
│ id_auteur        │                                    │ num_carte        │
│ nom_auteur       │                                    │ nom_adherent     │
│ prenom_auteur    │                                    │ prenom_adherent  │
│ nationalite      │                                    │ email            │
│ date_naissance   │                                    │ telephone        │
└───────┬──────────┘                                    │ date_adhesion    │
        │                                               └────────┬─────────┘
        │ (1,n)                                                  │
        │                                                        │ (0,n)
   ┌────┴──────────┐                                             │
   │    ECRIT      │                                    ┌────────┴─────────┐
   └────┬──────────┘                                    │    EMPRUNTE      │
        │ (1,n)                                         ├──────────────────┤
        │                                               │ date_emprunt     │
┌───────▼──────────┐                                    │ date_retour_prevue│
│     LIVRE        │                                    │ date_retour_eff  │
├──────────────────┤                                    └────────┬─────────┘
│ isbn             │                                             │
│ titre            │                                             │ (0,n)
│ annee_publication│                                             │
│ nb_pages         │─────────────────────────────────────────────┘
│ langue           │
└──────────────────┘

CARDINALITES :
- AUTEUR  (1,n) --- ECRIT     --- (1,n) LIVRE     → N:M
  "Un auteur ecrit au moins 1 livre" / "Un livre a au moins 1 auteur"

- ADHERENT (0,n) --- EMPRUNTE --- (0,n) LIVRE     → N:M
  "Un adherent peut emprunter 0 ou N livres" / "Un livre peut etre emprunte par 0 ou N adherents"
  L'association EMPRUNTE porte : date_emprunt, date_retour_prevue, date_retour_effective
```

#### 3. MLD

Application des regles de transformation :

| Association | Cardinalites | Regle | Resultat |
|-------------|-------------|-------|----------|
| ECRIT | (1,n) - (1,n) | R3 : N:M → table de jonction | Table ECRITURE |
| EMPRUNTE | (0,n) - (0,n) | R3 : N:M → table de jonction | Table EMPRUNT |

```
Schema relationnel :

AUTEUR (
    id_auteur           PK,
    nom_auteur          VARCHAR(100)    NOT NULL,
    prenom_auteur       VARCHAR(100)    NOT NULL,
    nationalite         VARCHAR(50),
    date_naissance      DATE
)

LIVRE (
    isbn                PK,
    titre               VARCHAR(300)    NOT NULL,
    annee_publication   INT             NOT NULL,
    nb_pages            INT,
    langue              VARCHAR(50)     NOT NULL
)

ECRITURE (
    id_auteur           PK, FK → AUTEUR,
    isbn                PK, FK → LIVRE
)

ADHERENT (
    num_carte           PK,
    nom_adherent        VARCHAR(100)    NOT NULL,
    prenom_adherent     VARCHAR(100)    NOT NULL,
    email               VARCHAR(255)    NOT NULL UNIQUE,
    telephone           VARCHAR(20),
    date_adhesion       DATE            NOT NULL
)

EMPRUNT (
    id_emprunt          PK (auto),
    isbn                FK → LIVRE      NOT NULL,
    num_carte           FK → ADHERENT   NOT NULL,
    date_emprunt        DATE            NOT NULL,
    date_retour_prevue  DATE            NOT NULL,
    date_retour_effective DATE
)
```

💡 **Note** : pour la table EMPRUNT, on ajoute un `id_emprunt` auto-incremente comme PK plutot qu'une cle composee (isbn, num_carte), car un meme adherent peut emprunter le meme livre **plusieurs fois** a des dates differentes.

#### 4. SQL DDL (PostgreSQL)

```sql
-- =============================================================
-- Systeme de gestion de bibliotheque
-- SGBD : PostgreSQL
-- =============================================================

-- TABLE : auteur
CREATE TABLE auteur (
    id_auteur       SERIAL      PRIMARY KEY,
    nom_auteur      VARCHAR(100) NOT NULL,
    prenom_auteur   VARCHAR(100) NOT NULL,
    nationalite     VARCHAR(50),
    date_naissance  DATE
);

-- TABLE : livre
CREATE TABLE livre (
    isbn                VARCHAR(17)  PRIMARY KEY,
    titre               VARCHAR(300) NOT NULL,
    annee_publication   INT          NOT NULL,
    nb_pages            INT,
    langue              VARCHAR(50)  NOT NULL,

    CONSTRAINT chk_livre_annee CHECK (annee_publication > 0 AND annee_publication <= EXTRACT(YEAR FROM NOW())),
    CONSTRAINT chk_livre_pages CHECK (nb_pages IS NULL OR nb_pages > 0)
);

-- TABLE : ecriture (jonction auteur-livre)
CREATE TABLE ecriture (
    id_auteur   INT NOT NULL,
    isbn        VARCHAR(17) NOT NULL,

    PRIMARY KEY (id_auteur, isbn),

    CONSTRAINT fk_ecriture_auteur
        FOREIGN KEY (id_auteur) REFERENCES auteur(id_auteur)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ecriture_livre
        FOREIGN KEY (isbn) REFERENCES livre(isbn)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- TABLE : adherent
CREATE TABLE adherent (
    num_carte       VARCHAR(20)  PRIMARY KEY,
    nom_adherent    VARCHAR(100) NOT NULL,
    prenom_adherent VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    telephone       VARCHAR(20),
    date_adhesion   DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- TABLE : emprunt
CREATE TABLE emprunt (
    id_emprunt              SERIAL  PRIMARY KEY,
    isbn                    VARCHAR(17) NOT NULL,
    num_carte               VARCHAR(20) NOT NULL,
    date_emprunt            DATE    NOT NULL DEFAULT CURRENT_DATE,
    date_retour_prevue      DATE    NOT NULL,
    date_retour_effective   DATE,

    CONSTRAINT fk_emprunt_livre
        FOREIGN KEY (isbn) REFERENCES livre(isbn)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_emprunt_adherent
        FOREIGN KEY (num_carte) REFERENCES adherent(num_carte)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- RG10 : duree max 21 jours
    CONSTRAINT chk_emprunt_duree
        CHECK (date_retour_prevue <= date_emprunt + INTERVAL '21 days'),
    -- Date retour effective >= date emprunt
    CONSTRAINT chk_emprunt_retour
        CHECK (date_retour_effective IS NULL OR date_retour_effective >= date_emprunt)
);

-- INDEX
CREATE INDEX idx_emprunt_livre ON emprunt(isbn);
CREATE INDEX idx_emprunt_adherent ON emprunt(num_carte);
CREATE INDEX idx_emprunt_date ON emprunt(date_emprunt);
CREATE INDEX idx_emprunt_non_rendu ON emprunt(num_carte)
    WHERE date_retour_effective IS NULL;

-- Commentaires
COMMENT ON TABLE emprunt IS 'Emprunts de livres par les adherents';
COMMENT ON COLUMN emprunt.date_retour_effective IS 'NULL si le livre n est pas encore rendu';
```

💡 **Note sur RG9** (max 5 livres simultanes) : cette regle ne peut pas etre implementee par une simple contrainte CHECK. Elle necessite soit un trigger, soit une verification applicative :

```sql
-- Trigger pour limiter a 5 emprunts simultanes (RG9)
CREATE OR REPLACE FUNCTION verifier_limite_emprunts()
RETURNS TRIGGER AS $$
DECLARE
    nb_emprunts_en_cours INT;
BEGIN
    SELECT COUNT(*) INTO nb_emprunts_en_cours
    FROM emprunt
    WHERE num_carte = NEW.num_carte
      AND date_retour_effective IS NULL;

    IF nb_emprunts_en_cours >= 5 THEN
        RAISE EXCEPTION 'L adherent % a deja 5 emprunts en cours', NEW.num_carte;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_limite_emprunts
    BEFORE INSERT ON emprunt
    FOR EACH ROW
    EXECUTE FUNCTION verifier_limite_emprunts();
```

---

## Niveau 3 - Projet Complet Data Engineering

### 📝 Exercice 3 : Systeme de Monitoring de Pipelines de Donnees

#### Contexte

Vous etes Data Engineer dans une entreprise qui opere de nombreux pipelines de donnees (ETL/ELT). La direction souhaite un systeme de monitoring centralise pour suivre l'execution des pipelines, detecter les erreurs et generer des alertes.

#### Compte-rendu d'interview (simule)

> **Interview avec le Tech Lead Data :**
>
> "Nous avons environ 50 pipelines qui tournent en production. Chaque pipeline a un nom, une description, un type (ETL, ELT, streaming), une frequence d'execution (horaire, journalier, hebdomadaire) et un proprietaire (un membre de l'equipe).
>
> Chaque pipeline a une source de donnees et une destination. Une source ou destination peut etre une base de donnees, un bucket S3, une API, un topic Kafka, etc. On veut savoir le type de source/destination, l'URL de connexion et le nom du schema ou du dataset.
>
> Un pipeline peut avoir plusieurs sources mais une seule destination. Certains pipelines partagent les memes sources.
>
> Chaque fois qu'un pipeline s'execute, on enregistre une execution avec sa date de debut, sa date de fin, son statut (en_cours, succes, echec, annule), le nombre de lignes traitees et la duree en secondes.
>
> Quand une execution echoue, on enregistre une ou plusieurs erreurs avec le type d'erreur (connexion, transformation, chargement, timeout), le message d'erreur, la ligne concernee si applicable, et l'etape du pipeline ou l'erreur s'est produite.
>
> Enfin, le systeme doit generer des alertes. Une alerte est liee a une execution. Elle a un niveau de severite (info, warning, critical), un message, un canal de notification (email, slack, pagerduty) et un statut (envoyee, acquittee, resolue).
>
> On veut pouvoir repondre a des questions comme : quel est le taux d'echec par pipeline ce mois-ci ? Quels pipelines ont le plus d'erreurs ? Quelle est la duree moyenne d'execution par pipeline ? Combien d'alertes critiques non resolues avons-nous ?"

#### Travail demande

A partir de ce compte-rendu d'interview, realisez **le workflow complet de modelisation** :

1. **Regles de gestion** : identifiez et numerotez au moins 15 regles
2. **Dictionnaire de donnees** : redigez le dictionnaire complet pour toutes les entites
3. **MCD** : dessinez le MCD avec toutes les entites, associations et cardinalites
4. **MLD** : transformez le MCD en schema relationnel
5. **SQL DDL** : ecrivez les scripts CREATE TABLE pour PostgreSQL avec contraintes, index et commentaires

---

### Solution Niveau 3

#### 1. Regles de gestion

| # | Regle de gestion |
|---|-----------------|
| RG1 | Un **pipeline** est identifie par un identifiant unique |
| RG2 | Un pipeline possede un nom (unique), une description, un type (ETL, ELT, streaming), une frequence (horaire, journalier, hebdomadaire), un proprietaire et un statut (actif, inactif, archive) |
| RG3 | Un pipeline a **une et une seule destination** |
| RG4 | Un pipeline a **une ou plusieurs sources** |
| RG5 | Une **source/destination** est identifiee par un identifiant unique et possede un nom, un type (database, s3, api, kafka), une URL de connexion et un nom de schema/dataset |
| RG6 | Une source peut etre utilisee par **0 ou N pipelines** |
| RG7 | Une destination peut etre utilisee par **0 ou N pipelines** |
| RG8 | Un pipeline a **0 ou N executions** au cours du temps |
| RG9 | Une **execution** est identifiee par un identifiant unique et possede une date de debut, une date de fin (NULL si en cours), un statut (en_cours, succes, echec, annule), un nombre de lignes traitees et une duree en secondes |
| RG10 | Une execution appartient a **un et un seul pipeline** |
| RG11 | Une execution peut generer **0 ou N erreurs** |
| RG12 | Une **erreur** est identifiee par un identifiant unique et possede un type (connexion, transformation, chargement, timeout), un message, un numero de ligne (facultatif), une etape du pipeline et un horodatage |
| RG13 | Une erreur appartient a **une et une seule execution** |
| RG14 | Une execution peut generer **0 ou N alertes** |
| RG15 | Une **alerte** est identifiee par un identifiant unique et possede un niveau de severite (info, warning, critical), un message, un canal de notification (email, slack, pagerduty), un statut (envoyee, acquittee, resolue) et un horodatage |
| RG16 | Une alerte est liee a **une et une seule execution** |
| RG17 | La date de fin d'execution doit etre posterieure a la date de debut |

#### 2. Dictionnaire de donnees

**Entite : SOURCE_DONNEES**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Source | id_source | INT | - | Oui | ✅ Oui | Identifiant unique |
| Nom | nom_source | VARCHAR | 100 | Oui | Non | Nom de la source (unique) |
| Type | type_source | VARCHAR | 20 | Oui | Non | database, s3, api, kafka |
| URL connexion | url_connexion | VARCHAR | 500 | Oui | Non | Chaine de connexion |
| Schema/Dataset | nom_schema | VARCHAR | 100 | Non | Non | Nom du schema ou dataset |

**Entite : DESTINATION_DONNEES**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Destination | id_destination | INT | - | Oui | ✅ Oui | Identifiant unique |
| Nom | nom_destination | VARCHAR | 100 | Oui | Non | Nom de la destination (unique) |
| Type | type_destination | VARCHAR | 20 | Oui | Non | database, s3, api, kafka |
| URL connexion | url_connexion_dest | VARCHAR | 500 | Oui | Non | Chaine de connexion |
| Schema/Dataset | nom_schema_dest | VARCHAR | 100 | Non | Non | Nom du schema ou dataset |

**Entite : PIPELINE**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Pipeline | id_pipeline | INT | - | Oui | ✅ Oui | Identifiant unique |
| Nom | nom_pipeline | VARCHAR | 100 | Oui | Non | Nom unique du pipeline |
| Description | description_pipeline | TEXT | - | Non | Non | Description fonctionnelle |
| Type | type_pipeline | VARCHAR | 20 | Oui | Non | ETL, ELT, streaming |
| Frequence | frequence | VARCHAR | 20 | Oui | Non | horaire, journalier, hebdomadaire |
| Proprietaire | proprietaire | VARCHAR | 100 | Oui | Non | Nom du responsable |
| Statut | statut_pipeline | VARCHAR | 20 | Oui | Non | actif, inactif, archive |
| Date creation | date_creation_pipeline | TIMESTAMP | - | Oui | Non | Date de creation du pipeline |

**Entite : EXECUTION**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Execution | id_execution | BIGINT | - | Oui | ✅ Oui | Identifiant unique (BIGINT car volume eleve) |
| Date debut | date_debut | TIMESTAMP WITH TZ | - | Oui | Non | Debut de l'execution |
| Date fin | date_fin | TIMESTAMP WITH TZ | - | Non | Non | Fin de l'execution (NULL si en cours) |
| Statut | statut_execution | VARCHAR | 20 | Oui | Non | en_cours, succes, echec, annule |
| Lignes traitees | nb_lignes_traitees | BIGINT | - | Non | Non | Nombre de lignes processees |
| Duree (sec) | duree_secondes | INT | - | Non | Non | Duree totale en secondes |

**Entite : ERREUR**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Erreur | id_erreur | BIGINT | - | Oui | ✅ Oui | Identifiant unique |
| Type | type_erreur | VARCHAR | 30 | Oui | Non | connexion, transformation, chargement, timeout |
| Message | message_erreur | TEXT | - | Oui | Non | Message d'erreur detaille |
| Ligne concernee | ligne_concernee | BIGINT | - | Non | Non | Numero de la ligne en erreur |
| Etape | etape_pipeline | VARCHAR | 50 | Oui | Non | Etape du pipeline (extract, transform, load) |
| Horodatage | date_erreur | TIMESTAMP WITH TZ | - | Oui | Non | Moment de l'erreur |

**Entite : ALERTE**

| Attribut | Code | Type | Taille | Obligatoire | Identifiant | Description |
|----------|------|------|--------|-------------|-------------|-------------|
| ID Alerte | id_alerte | INT | - | Oui | ✅ Oui | Identifiant unique |
| Severite | severite | VARCHAR | 20 | Oui | Non | info, warning, critical |
| Message | message_alerte | TEXT | - | Oui | Non | Description de l'alerte |
| Canal | canal_notification | VARCHAR | 20 | Oui | Non | email, slack, pagerduty |
| Statut | statut_alerte | VARCHAR | 20 | Oui | Non | envoyee, acquittee, resolue |
| Horodatage | date_alerte | TIMESTAMP WITH TZ | - | Oui | Non | Moment de l'alerte |

#### 3. MCD

```
┌──────────────────┐                                    ┌──────────────────┐
│ SOURCE_DONNEES   │                                    │DESTINATION_DONNEES│
├──────────────────┤                                    ├──────────────────┤
│ id_source        │                                    │ id_destination   │
│ nom_source       │                                    │ nom_destination  │
│ type_source      │                                    │ type_destination │
│ url_connexion    │                                    │ url_connexion_dst│
│ nom_schema       │                                    │ nom_schema_dest  │
└───────┬──────────┘                                    └──────┬───────────┘
        │                                                      │
        │ (0,n)                                                │ (0,n)
        │                                                      │
   ┌────┴──────────┐      ┌────────────────────┐    ┌────────┴────────┐
   │   ALIMENTE    │      │     PIPELINE       │    │    ECRIT_DANS   │
   └────┬──────────┘      ├────────────────────┤    └────────┬────────┘
        │ (1,n)           │ id_pipeline        │             │ (1,1)
        │                 │ nom_pipeline       │             │
        └────────────────→│ description_pipeline│←────────────┘
                          │ type_pipeline      │
                          │ frequence          │
                          │ proprietaire       │
                          │ statut_pipeline    │
                          │ date_creation_pipe │
                          └─────────┬──────────┘
                                    │
                                    │ (0,n)
                                    │
                           ┌────────┴────────┐
                           │    A_POUR       │
                           └────────┬────────┘
                                    │ (1,1)
                                    │
                          ┌─────────▼──────────┐
                          │    EXECUTION       │
                          ├────────────────────┤
                          │ id_execution       │
                          │ date_debut         │
                          │ date_fin           │
                          │ statut_execution   │
                          │ nb_lignes_traitees │
                          │ duree_secondes     │
                          └───┬────────────┬───┘
                              │            │
                     (0,n)    │            │    (0,n)
                              │            │
                    ┌─────────┴──┐    ┌────┴──────────┐
                    │  GENERE_ERR│    │  GENERE_ALERTE│
                    └─────────┬──┘    └────┬──────────┘
                              │            │
                     (1,1)    │            │    (1,1)
                              │            │
                    ┌─────────▼──┐    ┌────▼──────────┐
                    │   ERREUR   │    │    ALERTE     │
                    ├────────────┤    ├───────────────┤
                    │ id_erreur  │    │ id_alerte     │
                    │ type_erreur│    │ severite      │
                    │ message_err│    │ message_alerte│
                    │ ligne_conc │    │ canal_notif   │
                    │ etape_pipe │    │ statut_alerte │
                    │ date_erreur│    │ date_alerte   │
                    └────────────┘    └───────────────┘

RESUME DES CARDINALITES :
- SOURCE_DONNEES (0,n) --- ALIMENTE --- (1,n) PIPELINE   → N:M
- PIPELINE (1,1) --- ECRIT_DANS --- (0,n) DESTINATION    → 1:N (FK dans PIPELINE)
- PIPELINE (0,n) --- A_POUR --- (1,1) EXECUTION          → 1:N (FK dans EXECUTION)
- EXECUTION (0,n) --- GENERE_ERR --- (1,1) ERREUR        → 1:N (FK dans ERREUR)
- EXECUTION (0,n) --- GENERE_ALERTE --- (1,1) ALERTE     → 1:N (FK dans ALERTE)
```

#### 4. MLD

Application des regles :

| Association | Cardinalites | Regle | Resultat |
|-------------|-------------|-------|----------|
| ALIMENTE (Source-Pipeline) | (0,n)-(1,n) | R3 : N:M | Table PIPELINE_SOURCE |
| ECRIT_DANS (Pipeline-Destination) | (1,1)-(0,n) | R2 | FK id_destination dans PIPELINE |
| A_POUR (Pipeline-Execution) | (0,n)-(1,1) | R2 | FK id_pipeline dans EXECUTION |
| GENERE_ERR (Execution-Erreur) | (0,n)-(1,1) | R2 | FK id_execution dans ERREUR |
| GENERE_ALERTE (Execution-Alerte) | (0,n)-(1,1) | R2 | FK id_execution dans ALERTE |

```
Schema relationnel :

SOURCE_DONNEES (
    id_source               PK,
    nom_source              VARCHAR(100)    NOT NULL UNIQUE,
    type_source             VARCHAR(20)     NOT NULL,
    url_connexion           VARCHAR(500)    NOT NULL,
    nom_schema              VARCHAR(100)
)

DESTINATION_DONNEES (
    id_destination          PK,
    nom_destination         VARCHAR(100)    NOT NULL UNIQUE,
    type_destination        VARCHAR(20)     NOT NULL,
    url_connexion_dest      VARCHAR(500)    NOT NULL,
    nom_schema_dest         VARCHAR(100)
)

PIPELINE (
    id_pipeline             PK,
    nom_pipeline            VARCHAR(100)    NOT NULL UNIQUE,
    description_pipeline    TEXT,
    type_pipeline           VARCHAR(20)     NOT NULL,
    frequence               VARCHAR(20)     NOT NULL,
    proprietaire            VARCHAR(100)    NOT NULL,
    statut_pipeline         VARCHAR(20)     NOT NULL,
    date_creation_pipeline  TIMESTAMP       NOT NULL,
    #id_destination         FK → DESTINATION_DONNEES    NOT NULL
)

PIPELINE_SOURCE (
    #id_pipeline            PK, FK → PIPELINE,
    #id_source              PK, FK → SOURCE_DONNEES
)

EXECUTION (
    id_execution            PK,
    date_debut              TIMESTAMP WITH TZ NOT NULL,
    date_fin                TIMESTAMP WITH TZ,
    statut_execution        VARCHAR(20)     NOT NULL,
    nb_lignes_traitees      BIGINT,
    duree_secondes          INT,
    #id_pipeline            FK → PIPELINE   NOT NULL
)

ERREUR (
    id_erreur               PK,
    type_erreur             VARCHAR(30)     NOT NULL,
    message_erreur          TEXT            NOT NULL,
    ligne_concernee         BIGINT,
    etape_pipeline          VARCHAR(50)     NOT NULL,
    date_erreur             TIMESTAMP WITH TZ NOT NULL,
    #id_execution           FK → EXECUTION  NOT NULL
)

ALERTE (
    id_alerte               PK,
    severite                VARCHAR(20)     NOT NULL,
    message_alerte          TEXT            NOT NULL,
    canal_notification      VARCHAR(20)     NOT NULL,
    statut_alerte           VARCHAR(20)     NOT NULL,
    date_alerte             TIMESTAMP WITH TZ NOT NULL,
    #id_execution           FK → EXECUTION  NOT NULL
)
```

#### 5. SQL DDL complet (PostgreSQL)

```sql
-- =============================================================
-- SYSTEME DE MONITORING DE PIPELINES DE DONNEES
-- SGBD : PostgreSQL 15+
-- Contexte : Data Engineering
-- =============================================================

CREATE SCHEMA IF NOT EXISTS monitoring;
SET search_path TO monitoring;

-- =============================================================
-- TABLE : source_donnees
-- =============================================================
CREATE TABLE source_donnees (
    id_source       SERIAL          PRIMARY KEY,
    nom_source      VARCHAR(100)    NOT NULL,
    type_source     VARCHAR(20)     NOT NULL,
    url_connexion   VARCHAR(500)    NOT NULL,
    nom_schema      VARCHAR(100),

    CONSTRAINT uk_source_nom UNIQUE (nom_source),
    CONSTRAINT chk_source_type
        CHECK (type_source IN ('database', 's3', 'api', 'kafka', 'fichier'))
);

COMMENT ON TABLE source_donnees IS 'Sources de donnees des pipelines';

-- =============================================================
-- TABLE : destination_donnees
-- =============================================================
CREATE TABLE destination_donnees (
    id_destination      SERIAL          PRIMARY KEY,
    nom_destination     VARCHAR(100)    NOT NULL,
    type_destination    VARCHAR(20)     NOT NULL,
    url_connexion_dest  VARCHAR(500)    NOT NULL,
    nom_schema_dest     VARCHAR(100),

    CONSTRAINT uk_destination_nom UNIQUE (nom_destination),
    CONSTRAINT chk_destination_type
        CHECK (type_destination IN ('database', 's3', 'api', 'kafka', 'fichier'))
);

COMMENT ON TABLE destination_donnees IS 'Destinations de donnees des pipelines';

-- =============================================================
-- TABLE : pipeline
-- =============================================================
CREATE TABLE pipeline (
    id_pipeline             SERIAL          PRIMARY KEY,
    nom_pipeline            VARCHAR(100)    NOT NULL,
    description_pipeline    TEXT,
    type_pipeline           VARCHAR(20)     NOT NULL,
    frequence               VARCHAR(20)     NOT NULL,
    proprietaire            VARCHAR(100)    NOT NULL,
    statut_pipeline         VARCHAR(20)     NOT NULL DEFAULT 'actif',
    date_creation_pipeline  TIMESTAMP       NOT NULL DEFAULT NOW(),
    id_destination          INT             NOT NULL,

    CONSTRAINT uk_pipeline_nom UNIQUE (nom_pipeline),
    CONSTRAINT fk_pipeline_destination
        FOREIGN KEY (id_destination)
        REFERENCES destination_donnees(id_destination)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_pipeline_type
        CHECK (type_pipeline IN ('ETL', 'ELT', 'streaming')),
    CONSTRAINT chk_pipeline_frequence
        CHECK (frequence IN ('horaire', 'journalier', 'hebdomadaire', 'temps_reel')),
    CONSTRAINT chk_pipeline_statut
        CHECK (statut_pipeline IN ('actif', 'inactif', 'archive'))
);

COMMENT ON TABLE pipeline IS 'Pipelines de donnees supervises';
COMMENT ON COLUMN pipeline.proprietaire IS 'Membre de l equipe responsable du pipeline';

-- =============================================================
-- TABLE : pipeline_source (jonction N:M)
-- =============================================================
CREATE TABLE pipeline_source (
    id_pipeline     INT     NOT NULL,
    id_source       INT     NOT NULL,

    PRIMARY KEY (id_pipeline, id_source),

    CONSTRAINT fk_ps_pipeline
        FOREIGN KEY (id_pipeline)
        REFERENCES pipeline(id_pipeline)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ps_source
        FOREIGN KEY (id_source)
        REFERENCES source_donnees(id_source)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

COMMENT ON TABLE pipeline_source IS 'Association entre pipelines et leurs sources de donnees';

-- =============================================================
-- TABLE : execution
-- =============================================================
CREATE TABLE execution (
    id_execution        BIGSERIAL                   PRIMARY KEY,
    date_debut          TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    date_fin            TIMESTAMP WITH TIME ZONE,
    statut_execution    VARCHAR(20)                 NOT NULL DEFAULT 'en_cours',
    nb_lignes_traitees  BIGINT,
    duree_secondes      INT,
    id_pipeline         INT                         NOT NULL,

    CONSTRAINT fk_execution_pipeline
        FOREIGN KEY (id_pipeline)
        REFERENCES pipeline(id_pipeline)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_execution_statut
        CHECK (statut_execution IN ('en_cours', 'succes', 'echec', 'annule')),
    CONSTRAINT chk_execution_dates
        CHECK (date_fin IS NULL OR date_fin >= date_debut),
    CONSTRAINT chk_execution_lignes
        CHECK (nb_lignes_traitees IS NULL OR nb_lignes_traitees >= 0),
    CONSTRAINT chk_execution_duree
        CHECK (duree_secondes IS NULL OR duree_secondes >= 0)
);

COMMENT ON TABLE execution IS 'Executions des pipelines avec metriques';
COMMENT ON COLUMN execution.date_fin IS 'NULL si l execution est encore en cours';

-- =============================================================
-- TABLE : erreur
-- =============================================================
CREATE TABLE erreur (
    id_erreur           BIGSERIAL                   PRIMARY KEY,
    type_erreur         VARCHAR(30)                 NOT NULL,
    message_erreur      TEXT                        NOT NULL,
    ligne_concernee     BIGINT,
    etape_pipeline      VARCHAR(50)                 NOT NULL,
    date_erreur         TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    id_execution        BIGINT                      NOT NULL,

    CONSTRAINT fk_erreur_execution
        FOREIGN KEY (id_execution)
        REFERENCES execution(id_execution)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_erreur_type
        CHECK (type_erreur IN ('connexion', 'transformation', 'chargement', 'timeout', 'validation', 'autre')),
    CONSTRAINT chk_erreur_etape
        CHECK (etape_pipeline IN ('extract', 'transform', 'load', 'validation', 'autre'))
);

COMMENT ON TABLE erreur IS 'Erreurs survenues pendant l execution des pipelines';

-- =============================================================
-- TABLE : alerte
-- =============================================================
CREATE TABLE alerte (
    id_alerte           SERIAL                      PRIMARY KEY,
    severite            VARCHAR(20)                 NOT NULL,
    message_alerte      TEXT                        NOT NULL,
    canal_notification  VARCHAR(20)                 NOT NULL,
    statut_alerte       VARCHAR(20)                 NOT NULL DEFAULT 'envoyee',
    date_alerte         TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    id_execution        BIGINT                      NOT NULL,

    CONSTRAINT fk_alerte_execution
        FOREIGN KEY (id_execution)
        REFERENCES execution(id_execution)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_alerte_severite
        CHECK (severite IN ('info', 'warning', 'critical')),
    CONSTRAINT chk_alerte_canal
        CHECK (canal_notification IN ('email', 'slack', 'pagerduty')),
    CONSTRAINT chk_alerte_statut
        CHECK (statut_alerte IN ('envoyee', 'acquittee', 'resolue'))
);

COMMENT ON TABLE alerte IS 'Alertes generees suite aux executions des pipelines';

-- =============================================================
-- INDEX
-- =============================================================

-- Recherche d'executions par pipeline (jointure tres frequente)
CREATE INDEX idx_execution_pipeline ON execution(id_pipeline);

-- Recherche d'executions par date (filtrage temporel, dashboards)
CREATE INDEX idx_execution_date ON execution(date_debut DESC);

-- Recherche d'executions en echec (monitoring)
CREATE INDEX idx_execution_echec ON execution(id_pipeline, date_debut)
    WHERE statut_execution = 'echec';

-- Recherche d'executions en cours
CREATE INDEX idx_execution_en_cours ON execution(id_pipeline)
    WHERE statut_execution = 'en_cours';

-- Recherche d'erreurs par execution
CREATE INDEX idx_erreur_execution ON erreur(id_execution);

-- Recherche d'erreurs par type (analyse des erreurs recurrentes)
CREATE INDEX idx_erreur_type ON erreur(type_erreur);

-- Recherche d'alertes par execution
CREATE INDEX idx_alerte_execution ON alerte(id_execution);

-- Recherche d'alertes non resolues (dashboard monitoring)
CREATE INDEX idx_alerte_non_resolue ON alerte(severite, date_alerte)
    WHERE statut_alerte != 'resolue';

-- Recherche de pipelines par destination
CREATE INDEX idx_pipeline_destination ON pipeline(id_destination);

-- =============================================================
-- REQUETES UTILES POUR LE MONITORING (bonus)
-- =============================================================

-- Taux d'echec par pipeline ce mois-ci
-- SELECT
--     p.nom_pipeline,
--     COUNT(*) AS total_executions,
--     COUNT(*) FILTER (WHERE e.statut_execution = 'echec') AS nb_echecs,
--     ROUND(
--         100.0 * COUNT(*) FILTER (WHERE e.statut_execution = 'echec') / COUNT(*),
--         2
--     ) AS taux_echec_pct
-- FROM pipeline p
-- JOIN execution e ON e.id_pipeline = p.id_pipeline
-- WHERE e.date_debut >= DATE_TRUNC('month', NOW())
-- GROUP BY p.nom_pipeline
-- ORDER BY taux_echec_pct DESC;

-- Duree moyenne d'execution par pipeline
-- SELECT
--     p.nom_pipeline,
--     ROUND(AVG(e.duree_secondes), 0) AS duree_moyenne_sec,
--     ROUND(AVG(e.nb_lignes_traitees), 0) AS lignes_moyennes
-- FROM pipeline p
-- JOIN execution e ON e.id_pipeline = p.id_pipeline
-- WHERE e.statut_execution = 'succes'
-- GROUP BY p.nom_pipeline
-- ORDER BY duree_moyenne_sec DESC;

-- Alertes critiques non resolues
-- SELECT
--     a.id_alerte,
--     a.message_alerte,
--     a.date_alerte,
--     p.nom_pipeline,
--     e.date_debut AS date_execution
-- FROM alerte a
-- JOIN execution e ON e.id_execution = a.id_execution
-- JOIN pipeline p ON p.id_pipeline = e.id_pipeline
-- WHERE a.severite = 'critical'
--   AND a.statut_alerte != 'resolue'
-- ORDER BY a.date_alerte DESC;
```

---

## Recapitulatif des competences evaluees

| Niveau | Competences | Validation |
|--------|------------|------------|
| **N1 - Lecture** | Lire un MCD, identifier entites/associations/cardinalites, rediger des RG | Theorie + comprehension |
| **N2 - Conception** | Dictionnaire → MCD → MLD → SQL pour un domaine classique | Maitrise du workflow complet |
| **N3 - Projet** | Interview → RG → Dictionnaire → MCD → MLD → MPD → SQL optimise dans un contexte Data Engineering | Autonomie professionnelle |

💡 **Conseil** : l'exercice de Niveau 3 est representatif d'un projet de synthese complet. Entralnez-vous a realiser le workflow complet en moins de 3 heures.

---

[← Precedent](06-outils-pratiques.md) | [🏠 Accueil](README.md)

---

**Academy** - Formation Data Engineer
