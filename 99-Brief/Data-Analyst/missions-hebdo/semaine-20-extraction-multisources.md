# Semaine 20 — Extraction multi-sources : SQL avancé (+ API & Excel en bonus) (mission hebdomadaire)

> Phase 3 — module 3.4 (extraction multi-sources) · Durée : ~1-2 jours · Modalité : binôme · Compétence : C4 (extraire des données via SQL avancé et API, croiser des sources) niv.2

## Contexte (court, retail Nord)

La direction de NordRetail veut confronter les ventes réelles aux **objectifs 2024** fixés pour chaque magasin. Ta mission cette semaine : aller chercher la donnée dans la base SQL transactionnelle avec des requêtes avancées (CTE + fenêtrage), puis la croiser avec le classeur d'objectifs. Elle soupçonne aussi que la météo influence les ventes (Sport l'été, Maison l'hiver) — un volet bonus si tu as le temps.

## Objectif de la mission

**Cœur de la mission (obligatoire) :** maîtriser le **SQL avancé** (CTE + fonctions de fenêtrage) sur la base NordRetail, et croiser le CA réel avec les **objectifs par magasin** (`objectifs_2024.csv`) pour calculer un taux d'atteinte. C'est l'essentiel attendu pour C4 niv.2.

**Pour aller plus loin (bonus, optionnel) :** enrichir l'analyse avec une source externe — l'API météo Open-Meteo — et le format Excel.

## Consignes (étapes)

### Partie obligatoire — SQL avancé + objectifs par magasin

1. **SQL avancé.** Monte la base avec `setup.sql` (SQLite ou Postgres). Écris au moins :
   - une **CTE** calculant le CA mensuel **par magasin** (jointures `commandes` × `produits` × `magasins`) ;
   - une **fonction de fenêtrage** : classement des magasins par CA (`RANK()`/`ROW_NUMBER() OVER (PARTITION BY mois ...)`) et/ou cumul glissant (`SUM(...) OVER (ORDER BY ...)`).
2. **Objectifs (CSV).** Charge `objectifs_2024.csv` avec `pandas.read_csv`. Il est structuré **par magasin** : colonnes `magasin_id, annee, mois, objectif_ca`.
3. **Merge.** Croise le CA réel (SQL) × objectifs sur **`magasin_id` + `mois`** → calcule le **taux d'atteinte** (`CA / objectif_ca`).
4. **Mini-analyse.** Rédige 8-10 lignes : quels **magasins** sous/sur-performent vs objectif ? Quel magasin progresse le plus sur l'année (lecture du cumul glissant) ?

### Pour aller plus loin (bonus — seulement si la partie obligatoire est terminée)

5. **API publique (bonus).** Appelle l'API gratuite **Open-Meteo** (sans clé) pour récupérer la température journalière 2024 de Lille (lat 50.63, lon 3.06, endpoint *archive*). Récupère le JSON en Python (`requests`), range-le en DataFrame, et explore une **piste de corrélation** ventes/météo (par catégorie : Sport, Maison...).
6. **Excel (bonus).** Recharge les objectifs depuis `objectifs_2024.xlsx` avec `pandas.read_excel` pour t'exercer à un second format de fichier (même contenu que le CSV).

## Données (fichier réel)

`../data/setup.sql` (tables `magasins, produits, clients, commandes`) et `../data/objectifs_2024.csv` (**par magasin** : `magasin_id, annee, mois, objectif_ca`). Bonus : `objectifs_2024.xlsx` (mêmes données), et l'API `https://archive-api.open-meteo.com/v1/archive` (paramètres `latitude, longitude, start_date, end_date, daily=temperature_2m_mean`).

## Livrable attendu

Le(s) fichier(s) `.sql` des requêtes, le notebook/script Python (chargement CSV + merge), le DataFrame final exporté en CSV, et la mini-analyse. Déposé sur la plateforme. Le volet API/Excel est un bonus valorisé mais non requis.

## Critères de réussite (OUI/NON)

**Obligatoire :**

- [ ] La requête utilise une **CTE** ET une **fonction de fenêtrage** correctes ?
- [ ] Les **objectifs** (`objectifs_2024.csv`) sont chargés et alignés sur **`magasin_id` + `mois`** ?
- [ ] Le **taux d'atteinte par magasin** (réel/objectif) est calculé sans erreur de jointure ?
- [ ] La mini-analyse est argumentée et le code **rejouable** ?

**Bonus (facultatif) :**

- [ ] L'**API Open-Meteo** est appelée et son JSON transformé en DataFrame exploitable ?
- [ ] Une **piste de corrélation** ventes/météo est formulée ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.4-extraction-multisources/`.
- SQL : CTE `WITH`, fenêtrage `OVER (PARTITION BY ... ORDER BY ...)`.
- [Open-Meteo — Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (gratuite, sans clé) — *pour le bonus*.
- Référentiel BC06 — compétence C4 (niv.2).
