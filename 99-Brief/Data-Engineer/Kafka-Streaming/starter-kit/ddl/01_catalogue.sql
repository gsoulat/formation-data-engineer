-- =============================================================================
-- KIT DE DÉMARRAGE — Catalogue produits et stocks de Bouquineo
-- Exécuté automatiquement au premier démarrage de PostgreSQL
-- (monté dans /docker-entrypoint-initdb.d par le docker-compose.yml).
-- Environ 12 000 références, quelques Mo.
-- =============================================================================

CREATE TABLE IF NOT EXISTS produits (
    product_ref     TEXT PRIMARY KEY,          -- ex : BQ-00042
    titre           TEXT NOT NULL,
    prix_catalogue  NUMERIC(8, 2) NOT NULL CHECK (prix_catalogue > 0),
    stock_initial   INTEGER NOT NULL CHECK (stock_initial >= 0)
);

COMMENT ON TABLE produits IS 'Catalogue Bouquineo : 12 000 références générées, dont 40 en vente flash (BQ-00001 à BQ-00040).';

-- Génération déterministe de 12 000 références.
-- setseed() fige l'aléatoire pour que tous les apprenants aient les mêmes données.
SELECT setseed(0.42);

INSERT INTO produits (product_ref, titre, prix_catalogue, stock_initial)
SELECT
    'BQ-' || LPAD(g::TEXT, 5, '0'),
    'Livre n°' || g || ' — catalogue Bouquineo',
    ROUND((5 + random() * 40)::NUMERIC, 2),
    CASE
        -- Les titres en vente flash (1 à 40) ont un stock volontairement serré :
        -- l'alerte de rupture doit pouvoir se déclencher pendant une démo.
        WHEN g <= 40 THEN (15 + FLOOR(random() * 60))::INTEGER
        ELSE (50 + FLOOR(random() * 250))::INTEGER
    END
FROM generate_series(1, 12000) AS g
ON CONFLICT (product_ref) DO NOTHING;

-- Sélection "vente flash" du mois : les 40 premières références, remisées.
CREATE TABLE IF NOT EXISTS ventes_flash (
    product_ref  TEXT PRIMARY KEY REFERENCES produits (product_ref),
    remise_pct   INTEGER NOT NULL CHECK (remise_pct BETWEEN 5 AND 70)
);

INSERT INTO ventes_flash (product_ref, remise_pct)
SELECT product_ref, (10 + FLOOR(random() * 40))::INTEGER
FROM produits
WHERE product_ref <= 'BQ-00040'
ON CONFLICT (product_ref) DO NOTHING;
