-- =====================================================================
-- Bouquineo — kit de démarrage brief 03
-- 04 : construction des marts + droits par GROUPES
-- =====================================================================

-- ---------------------------------------------------------------------
-- Marts destinés au data analyst : agrégés, SANS PII.
-- ---------------------------------------------------------------------
CREATE TABLE marts.ventes_par_canal AS
SELECT canal,
       date_trunc('month', date_vente)::date AS mois,
       COUNT(*)                              AS nb_ventes,
       SUM(quantite)                         AS quantite_totale,
       ROUND(SUM(quantite * prix_unitaire), 2) AS ca_ttc
FROM raw.ventes
GROUP BY canal, date_trunc('month', date_vente);
COMMENT ON TABLE marts.ventes_par_canal IS 'CA et volumes mensuels par canal. Aucune PII. Fait foi pour le reporting canal.';

CREATE TABLE marts.top_titres AS
SELECT c.reference_id, c.isbn, c.titre, c.auteur, c.categorie,
       SUM(v.quantite)                          AS quantite_vendue,
       ROUND(SUM(v.quantite * v.prix_unitaire), 2) AS ca_ttc
FROM raw.ventes v
JOIN raw.catalogue c USING (reference_id)
GROUP BY c.reference_id, c.isbn, c.titre, c.auteur, c.categorie;
COMMENT ON TABLE marts.top_titres IS 'Classement des titres par volume et CA. Aucune PII.';

CREATE TABLE marts.activite_clients AS
SELECT v.client_id,                                  -- identifiant technique, pas de donnée de contact
       COUNT(*)                    AS nb_commandes,
       MIN(v.date_vente)           AS premiere_commande,
       MAX(v.date_vente)           AS derniere_commande,
       ROUND(SUM(v.quantite * v.prix_unitaire), 2) AS ca_cumule
FROM raw.ventes v
GROUP BY v.client_id;
COMMENT ON TABLE marts.activite_clients IS 'Activité agrégée par client_id (pseudonyme). Pas de nom/email/téléphone.';

-- ---------------------------------------------------------------------
-- Droits appliqués aux GROUPES (jamais aux individus).
-- data engineering : tout ; data analyst : marts uniquement ;
-- marketing : marts uniquement (jamais raw, donc jamais les emails).
-- ---------------------------------------------------------------------
GRANT ALL    ON SCHEMA raw, marts TO grp_data_engineering;
GRANT ALL    ON ALL TABLES IN SCHEMA raw   TO grp_data_engineering;
GRANT ALL    ON ALL TABLES IN SCHEMA marts TO grp_data_engineering;

GRANT USAGE  ON SCHEMA marts TO grp_data_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO grp_data_analyst;
-- Pas de GRANT sur raw pour grp_data_analyst => pas d'accès aux PII.

GRANT USAGE  ON SCHEMA marts TO grp_marketing;
GRANT SELECT ON marts.ventes_par_canal, marts.top_titres TO grp_marketing;
-- Le marketing n'accède ni à raw ni à marts.activite_clients.

-- Les objets créés plus tard hériteront des mêmes droits :
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT ON TABLES TO grp_data_analyst;
