-- ============================================================
-- KIT DE DEMARRAGE — Chargement initial des 6 mois de données.
-- A exécuter APRES ddl/01_schema_etoile.sql et generate_data.py,
-- depuis le dossier starter-kit :
--   psql -d bouquineo_dwh -f chargement_initial.sql
-- (\copy est une méta-commande psql : le fichier est lu côté client)
-- ============================================================

SET search_path TO entrepot;

\copy dim_temps   FROM 'data/dim_temps.csv'   WITH (FORMAT csv, HEADER true)
\copy dim_client  FROM 'data/dim_client.csv'  WITH (FORMAT csv, HEADER true)
\copy dim_produit FROM 'data/dim_produit.csv' WITH (FORMAT csv, HEADER true)
\copy fait_ventes (temps_id, client_id, produit_id, canal_id, quantite, montant_ttc) FROM 'data/ventes.csv' WITH (FORMAT csv, HEADER true)

-- Contrôle rapide
SELECT 'dim_temps' AS table_, count(*) FROM dim_temps
UNION ALL SELECT 'dim_client', count(*) FROM dim_client
UNION ALL SELECT 'dim_produit', count(*) FROM dim_produit
UNION ALL SELECT 'fait_ventes', count(*) FROM fait_ventes;
