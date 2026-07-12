-- ============================================================
-- KIT DE DEMARRAGE — Schéma en étoile "entrepôt ventes Bouquineo"
-- Etat hérité du prédécesseur : AUCUNE historisation (les mises
-- à jour des dimensions se font par écrasement — c'est le bug
-- métier au coeur du brief).
-- Usage : psql -d bouquineo_dwh -f 01_schema_etoile.sql
-- ============================================================

CREATE SCHEMA IF NOT EXISTS entrepot;
SET search_path TO entrepot;

-- ---------- Dimension temps (grain : le jour) ----------
CREATE TABLE dim_temps (
    temps_id     INTEGER      PRIMARY KEY,          -- format AAAAMMJJ
    date_jour    DATE         NOT NULL UNIQUE,
    annee        INTEGER      NOT NULL,
    trimestre    INTEGER      NOT NULL,
    mois         INTEGER      NOT NULL,
    nom_mois     VARCHAR(20)  NOT NULL,
    jour         INTEGER      NOT NULL,
    jour_semaine VARCHAR(10)  NOT NULL,
    est_weekend  BOOLEAN      NOT NULL
);

-- ---------- Dimension client ----------
-- NOTE (héritage) : le segment est écrasé à chaque changement,
-- ce qui fausse les analyses de cohortes passées.
CREATE TABLE dim_client (
    client_id              VARCHAR(12)  PRIMARY KEY,   -- ex : CLI-000042
    nom                    VARCHAR(100) NOT NULL,
    email                  VARCHAR(150),
    ville                  VARCHAR(80),
    segment                VARCHAR(20)  NOT NULL
        CHECK (segment IN ('occasionnel', 'regulier', 'premium')),
    date_inscription       DATE         NOT NULL,
    date_derniere_activite DATE         NOT NULL
);

-- ---------- Dimension produit ----------
-- NOTE (héritage) : prix_achat et prix_vente sont écrasés à chaque
-- mise à jour tarifaire → la marge passée devient irrécupérable.
CREATE TABLE dim_produit (
    produit_id VARCHAR(17)   PRIMARY KEY,   -- ISBN-13, ex : 978-2-1234-5680-3
    titre      VARCHAR(200)  NOT NULL,
    auteur     VARCHAR(120),
    categorie  VARCHAR(50)   NOT NULL,
    prix_achat NUMERIC(8,2)  NOT NULL CHECK (prix_achat >= 0),
    prix_vente NUMERIC(8,2)  NOT NULL CHECK (prix_vente >= 0)
);

-- ---------- Dimension canal ----------
CREATE TABLE dim_canal (
    canal_id   SERIAL       PRIMARY KEY,
    code_canal VARCHAR(30)  NOT NULL UNIQUE,
    libelle    VARCHAR(80)  NOT NULL
);

INSERT INTO dim_canal (code_canal, libelle) VALUES
    ('site_web',    'Site e-commerce bouquineo.fr'),
    ('librairie',   'Librairies physiques affiliées'),
    ('marketplace', 'Marketplace partenaires (agrégat manuel, pas de source détaillée)');

-- ---------- Table de faits ventes (grain : ligne de commande) ----------
CREATE TABLE fait_ventes (
    vente_id    BIGSERIAL    PRIMARY KEY,
    temps_id    INTEGER      NOT NULL REFERENCES dim_temps(temps_id),
    client_id   VARCHAR(12)  NOT NULL REFERENCES dim_client(client_id),
    produit_id  VARCHAR(17)  NOT NULL REFERENCES dim_produit(produit_id),
    canal_id    INTEGER      NOT NULL REFERENCES dim_canal(canal_id),
    quantite    INTEGER      NOT NULL CHECK (quantite > 0),
    montant_ttc NUMERIC(10,2) NOT NULL CHECK (montant_ttc >= 0)
);

CREATE INDEX idx_fait_ventes_temps   ON fait_ventes(temps_id);
CREATE INDEX idx_fait_ventes_produit ON fait_ventes(produit_id);
CREATE INDEX idx_fait_ventes_client  ON fait_ventes(client_id);
CREATE INDEX idx_fait_ventes_canal   ON fait_ventes(canal_id);
