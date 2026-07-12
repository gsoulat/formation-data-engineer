# Semaine 11 — Modèle en étoile dans Power BI (mission hebdomadaire)

> Phase 2 — Solution BI pour analyse avancée · Module 2.2 · Durée : 1 à 2 jours · Modalité : binôme · Compétence : C18 (créer un tableau de bord BI / modéliser) niv. 2

## Contexte

NordRetail a centralisé ses ventes mais les fichiers Excel circulant entre services ne concordent jamais. La cellule data décide de poser une fondation propre : un modèle de données analytique. Avant de tracer le moindre graphique, il faut un schéma en étoile fiable, sur lequel toutes les analyses futures s'appuieront.

## Objectif de la mission

Construire un modèle en étoile dans Power BI à partir des tables de dimensions et de la table de faits, créer les relations correctes, et ajouter une table de dates dédiée pour les analyses temporelles.

## Consignes (étapes)

1. Importe dans Power BI Desktop : `Faits_Ventes.csv` (table de faits), `Dim_Magasin.csv`, `Dim_Produit.csv`, `Dim_Client.csv`, `Dim_Date.csv`.
2. Dans Power Query, vérifie et corrige les **types de colonnes** (clés en nombre entier, dates en date, montants en décimal). Garde les noms parlants.
3. En vue Modèle, crée les relations **1 → \*** entre chaque dimension et la table de faits :
   - `Dim_Magasin[magasin_id]` → `Faits_Ventes[magasin_id]`
   - `Dim_Produit[produit_id]` → `Faits_Ventes[produit_id]`
   - `Dim_Client[client_id]` → `Faits_Ventes[client_id]`
   - `Dim_Date[date_id]` → `Faits_Ventes[date_id]`
4. Vérifie le **sens de filtrage** (simple, des dimensions vers les faits) et l'absence de relations ambiguës ou inactives non voulues.
5. Marque `Dim_Date` comme **table de dates** (champ `date`). Confirme qu'elle est continue et sans trous sur la période couverte.
6. Teste le modèle avec une matrice simple (ex. `montant` par `ville` et par `nom_mois`) pour valider que les filtres se propagent bien.

## Données (../data/)

`Faits_Ventes.csv` · `Dim_Magasin.csv` · `Dim_Produit.csv` · `Dim_Client.csv` · `Dim_Date.csv`.

> Pas de licence Power BI ? Reproduis le modèle dans un outil équivalent (Tableau, Looker Studio) ou **décris** le modèle : schéma annoté + tableau des relations (table source, table cible, clés, cardinalité, sens de filtrage).

## Livrable attendu

Un fichier `.pbix` (ou équivalent) avec le modèle en étoile fonctionnel, **plus** une capture d'écran de la vue Modèle annotée et un court paragraphe expliquant pourquoi l'étoile est préférée à des tables à plat.

## Critères de réussite

- [ ] Les 5 tables sont importées avec des types de colonnes corrects (OUI/NON)
- [ ] Les 4 relations dimension → faits existent en cardinalité 1 → \* (OUI/NON)
- [ ] Le sens de filtrage va bien des dimensions vers la table de faits (OUI/NON)
- [ ] `Dim_Date` est marquée comme table de dates et est continue (OUI/NON)
- [ ] Une matrice de test prouve que les filtres se propagent correctement (OUI/NON)
- [ ] L'intérêt du schéma en étoile est expliqué clairement (OUI/NON)

## Ressources (renvoi au cours)

Module 2.2 — Modélisation dimensionnelle (faits/dimensions, étoile vs flocon, table de dates). Documentation Power BI : relations, Power Query, marquage table de dates.
