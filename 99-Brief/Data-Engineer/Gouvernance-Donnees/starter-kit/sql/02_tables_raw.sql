-- =====================================================================
-- Bouquineo — kit de démarrage brief 03
-- 02 : tables du schéma raw (avec commentaires = premières métadonnées)
-- =====================================================================

-- Table de référence clients : FAIT FOI pour le domaine "clients".
CREATE TABLE raw.clients (
    client_id              INTEGER PRIMARY KEY,
    nom                    TEXT        NOT NULL,
    prenom                 TEXT        NOT NULL,
    email                  TEXT        NOT NULL,          -- PII
    telephone              TEXT,                          -- PII
    adresse                TEXT,                          -- PII
    code_postal            TEXT,
    ville                  TEXT,
    date_inscription       DATE        NOT NULL,
    date_derniere_commande DATE,
    optin_marketing        BOOLEAN     NOT NULL DEFAULT FALSE
);
COMMENT ON TABLE  raw.clients IS 'Référentiel clients — table qui FAIT FOI. Contient des PII (email, téléphone, adresse).';
COMMENT ON COLUMN raw.clients.optin_marketing IS 'Consentement marketing À JOUR (source de vérité, contrairement à crm_export.optin).';

-- Table FANTÔME n°1 : migration abandonnée mi-2024, plus alimentée depuis.
CREATE TABLE raw.clients_v2 (
    id             INTEGER PRIMARY KEY,
    full_name      TEXT,        -- PII
    email_address  TEXT,        -- PII
    phone          TEXT,        -- PII
    postal_address TEXT,        -- PII
    signup_date    DATE,
    updated_at     DATE
);
COMMENT ON TABLE raw.clients_v2 IS 'Migration abandonnée (06/2024). NE FAIT PAS FOI. Candidate à la dépréciation puis suppression.';

-- Table FANTÔME n°2 : export CRM du 15/01/2025, à l''origine de la
-- campagne fautive (1 200 désinscrits recontactés).
CREATE TABLE raw.crm_export (
    client_id  INTEGER,
    prenom     TEXT,   -- PII
    nom        TEXT,   -- PII
    email      TEXT,   -- PII
    optin      BOOLEAN,
    exporte_le DATE
);
COMMENT ON TABLE  raw.crm_export IS 'Export CRM figé au 15/01/2025. NE FAIT PAS FOI : le flag optin y est obsolète (incident emailing).';
COMMENT ON COLUMN raw.crm_export.optin IS 'OBSOLÈTE — ne jamais utiliser pour cibler une campagne. Utiliser raw.clients.optin_marketing.';

CREATE TABLE raw.catalogue (
    reference_id INTEGER PRIMARY KEY,
    isbn         TEXT NOT NULL,
    titre        TEXT NOT NULL,
    auteur       TEXT,
    editeur      TEXT,
    categorie    TEXT,
    prix         NUMERIC(6,2),   -- ~3 % de NULL volontaires (test de complétude)
    stock        INTEGER,
    date_ajout   DATE
);
COMMENT ON TABLE raw.catalogue IS 'Catalogue produit (~12 000 références). Fait foi pour le domaine "catalogue".';

CREATE TABLE raw.ventes (
    vente_id      INTEGER PRIMARY KEY,
    client_id     INTEGER,
    reference_id  INTEGER,
    canal         TEXT CHECK (canal IN ('site', 'marketplace', 'librairie')),
    librairie_id  INTEGER,        -- renseigné uniquement pour le canal librairie
    quantite      INTEGER,
    prix_unitaire NUMERIC(6,2),
    date_vente    DATE
);
COMMENT ON TABLE raw.ventes IS 'Ventes des 3 canaux (~50 000 lignes). Fait foi pour le domaine "ventes".';

CREATE TABLE raw.evenements_web (
    event_id   BIGINT PRIMARY KEY,
    client_id  INTEGER,            -- NULL = visiteur anonyme ; pseudonymisable
    session_id TEXT,
    event_type TEXT,
    url        TEXT,
    ts         TIMESTAMP
);
COMMENT ON TABLE raw.evenements_web IS 'Flux de navigation issu du streaming (volumétrie la plus forte). client_id = donnée indirectement identifiante.';

CREATE TABLE raw.concurrent_prix (
    id               INTEGER PRIMARY KEY,
    titre            TEXT,
    prix_concurrent  NUMERIC(6,2),
    note             INTEGER,
    source           TEXT,
    date_releve      DATE
);
COMMENT ON TABLE raw.concurrent_prix IS 'Veille concurrentielle scrapée depuis books.toscrape.com (source externe, fréquence hebdo, fiabilité moyenne).';
