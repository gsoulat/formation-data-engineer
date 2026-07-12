# Kit de démarrage — Brief « Veille concurrentielle Bouquineo »

Ce kit contient **des données et une infrastructure, aucun code d'extraction ni de
nettoyage** : l'extraction, l'agrégation et le chargement sont votre travail.

## Contenu

- `data/catalogue_bouquineo.csv` — extrait du catalogue (~1 000 références, ISBN,
  métadonnées incomplètes sur ~1/3 des fiches).
- `data/ventes_librairies/*.csv` — 8 exports de ventes hétérogènes (~10 000 lignes
  cumulées) : colonnes différentes, formats de dates incohérents, doublons,
  encodage latin-1 (lib4), prix négatifs et ISBN manquants (lib8), etc.
- `docker-compose.yml` — PostgreSQL 16 prêt à l'emploi (`docker compose up -d`).

## Démarrage

```bash
docker compose up -d          # PostgreSQL 16 sur localhost:5432
```

Les identifiants de connexion sont dans le `docker-compose.yml`. À vous d'écrire les
scripts d'extraction (scraping, API, CSV), d'agrégation/nettoyage, le DDL et l'import.
