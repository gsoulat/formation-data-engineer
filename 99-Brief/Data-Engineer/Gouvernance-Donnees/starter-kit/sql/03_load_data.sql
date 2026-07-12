-- =====================================================================
-- Bouquineo — kit de démarrage brief 03
-- 03 : chargement des CSV générés par scripts/generate_data.py
-- Le dossier ../data est monté dans le conteneur sous /data (cf. compose).
-- PRÉREQUIS : avoir lancé generate_data.py AVANT le premier `docker compose up`.
-- =====================================================================

\echo 'Chargement raw.clients...'
COPY raw.clients        FROM '/data/clients.csv'         WITH (FORMAT csv, HEADER true);

\echo 'Chargement raw.clients_v2...'
COPY raw.clients_v2     FROM '/data/clients_v2.csv'      WITH (FORMAT csv, HEADER true);

\echo 'Chargement raw.crm_export...'
COPY raw.crm_export     FROM '/data/crm_export.csv'      WITH (FORMAT csv, HEADER true);

\echo 'Chargement raw.catalogue...'
COPY raw.catalogue      FROM '/data/catalogue.csv'       WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Chargement raw.ventes...'
COPY raw.ventes         FROM '/data/ventes.csv'          WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Chargement raw.evenements_web...'
COPY raw.evenements_web FROM '/data/evenements_web.csv'  WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Chargement raw.concurrent_prix...'
COPY raw.concurrent_prix FROM '/data/concurrent_prix.csv' WITH (FORMAT csv, HEADER true, NULL '');

ANALYZE;
