-- =====================================================================
-- Bouquineo — kit de démarrage brief 03 (Gouvernance des données)
-- 01 : schémas et rôles PostgreSQL
-- Exécuté automatiquement au premier démarrage du conteneur
-- (docker-entrypoint-initdb.d, ordre alphabétique des fichiers).
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS marts;

COMMENT ON SCHEMA raw   IS 'Données brutes opérationnelles Bouquineo (dont tables héritées non documentées)';
COMMENT ON SCHEMA marts IS 'Tables agrégées mises à disposition du data analyst';

-- ---------------------------------------------------------------------
-- Rôles de GROUPE (jamais de droits individuels : exigence du brief).
-- Ces rôles côté base illustrent le pendant SQL des policies OpenMetadata.
-- ---------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'grp_data_engineering') THEN
        CREATE ROLE grp_data_engineering NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'grp_data_analyst') THEN
        CREATE ROLE grp_data_analyst NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'grp_marketing') THEN
        CREATE ROLE grp_marketing NOLOGIN;
    END IF;
END
$$;

-- Comptes de service rattachés aux groupes (mots de passe de démo :
-- à surcharger via variables d'environnement en usage réel, cf. .env.example)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'svc_analyst') THEN
        CREATE ROLE svc_analyst LOGIN PASSWORD 'analyst_demo';
        GRANT grp_data_analyst TO svc_analyst;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'svc_marketing') THEN
        CREATE ROLE svc_marketing LOGIN PASSWORD 'marketing_demo';
        GRANT grp_marketing TO svc_marketing;
    END IF;
END
$$;
