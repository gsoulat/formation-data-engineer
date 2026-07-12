# Semaine 12 — Mesures DAX décisionnelles (mission hebdomadaire)

> Phase 2 — Solution BI pour analyse avancée · Module 2.3 · Durée : 1 à 2 jours · Modalité : binôme · Compétence : C18 (créer un tableau de bord BI / mesures) niv. 2

## Contexte

Le modèle en étoile de NordRetail est en place (semaine 11). La direction veut maintenant des indicateurs fiables et toujours identiques d'une réunion à l'autre : chiffre d'affaires, marge, panier moyen et évolution par rapport à l'an dernier. Ces calculs doivent vivre dans le modèle, pas dans des colonnes Excel recopiées à la main.

## Objectif de la mission

Créer 6 à 8 mesures DAX réutilisables sur le modèle de la semaine 11, dont au moins une mesure d'évolution temporelle (N-1 / YoY), et les valider sur des cas connus.

## Consignes (étapes)

1. Repars du modèle `.pbix` de la semaine 11 (table de faits `Faits_Ventes` + dimensions).
2. Crée les mesures suivantes (regroupe-les dans une table de mesures dédiée) :
   - **CA total** = `SUM(Faits_Ventes[montant])`
   - **Marge totale** = `SUM(Faits_Ventes[marge])`
   - **Taux de marge %** = Marge totale / CA total (formaté en %)
   - **Quantité vendue** = `SUM(Faits_Ventes[quantite])`
   - **Nombre de ventes** = `DISTINCTCOUNT(Faits_Ventes[vente_id])`
   - **Panier moyen** = CA total / Nombre de ventes
   - **CA N-1** = `CALCULATE([CA total], SAMEPERIODLASTYEAR(Dim_Date[date]))`
   - **Évolution CA YoY %** = (CA total − CA N-1) / CA N-1
3. Soigne le **formatage** (€, %, séparateurs de milliers) et nomme les mesures clairement.
4. **Valide** chaque mesure : recoupe le CA total et le taux de marge avec un calcul manuel (pandas ou Excel) sur un sous-ensemble (ex. une ville, un mois).
5. Mets les mesures à l'épreuve dans une matrice (CA, marge %, panier moyen, YoY % par `ville` et par `annee`).

## Données (../data/)

Modèle issu de `Faits_Ventes.csv` + `Dim_*.csv` (semaine 11). Données 2023 et 2024 présentes → la comparaison N-1 est possible.

## Livrable attendu

Le `.pbix` enrichi des mesures, **plus** un tableau récapitulatif (1 page) listant chaque mesure : nom, formule DAX, format, et résultat attendu vérifié. Une capture de la matrice de validation.

## Critères de réussite

- [ ] Au moins 6 mesures DAX sont créées et nommées clairement (OUI/NON)
- [ ] CA, marge % et panier moyen sont corrects et bien formatés (OUI/NON)
- [ ] Au moins une mesure d'évolution N-1 / YoY fonctionne via `Dim_Date` (OUI/NON)
- [ ] Les mesures sont validées par recoupement avec un calcul indépendant (OUI/NON)
- [ ] Les mesures réagissent correctement aux filtres dans une matrice (OUI/NON)
- [ ] Le tableau récapitulatif documente formules et résultats (OUI/NON)

## Ressources (renvoi au cours)

Module 2.3 — Langage DAX (mesures vs colonnes calculées, contexte de filtre, time intelligence : `CALCULATE`, `SAMEPERIODLASTYEAR`). Documentation Power BI DAX.
