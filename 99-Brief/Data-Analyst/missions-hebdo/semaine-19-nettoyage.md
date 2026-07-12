# Semaine 19 — Nettoyer un jeu de ventes sale en Python (mission hebdomadaire)

> Phase 3 — module 3.3 (qualité & nettoyage) · Durée : ~1-2 jours · Modalité : binôme · Compétence : C3 (nettoyer et fiabiliser un jeu de données) niv.1

## Contexte (court, retail Nord)

L'export `ventes_sales.csv` 2024 de NordRetail est arrivé… dans un état déplorable. Dates au format français, quantités manquantes, doublons de saisie, casse incohérente sur les villes, montants négatifs (retours mal codés), et quelques valeurs aberrantes qui faussent les totaux. La contrôleuse de gestion refuse de l'utiliser tant qu'il n'est pas fiabilisé. C'est ton job.

## Objectif de la mission

Produire une version **propre et fiable** de `ventes_sales.csv` en Python/pandas, en documentant **chaque règle de nettoyage** appliquée et son impact (lignes touchées).

## Consignes (étapes)

1. **Diagnostic.** Charge le fichier et dresse un état des lieux : `df.info()`, `describe()`, comptage des manquants par colonne, doublons, valeurs uniques de `ville` et `type`.
2. **Manquants.** Traite `quantite` (et autres colonnes) manquantes : choisis et justifie une stratégie (suppression, imputation médiane, recalcul depuis `montant/prix_unitaire`).
3. **Doublons.** Identifie et supprime les doublons exacts (et quasi-doublons si pertinent), en gardant une trace du nombre retiré.
4. **Casse & libellés.** Normalise la casse des `ville`/`categorie` (ex. `lille`, `LILLE`, `Lille` → `Lille`). Nettoie les espaces parasites.
5. **Dates.** Convertis `date` (format `JJ/MM/AAAA`) en date ISO `YYYY-MM-DD`. Rejette/signale les dates invalides.
6. **Négatifs & cohérence.** Traite les `montant`/`quantite` négatifs : décide s'il s'agit de retours à isoler ou d'erreurs à corriger. Vérifie la cohérence `montant ≈ quantite * prix_unitaire * (1 - remise)`.
7. **Outliers.** Détecte les valeurs aberrantes de `montant`/`quantite` (méthode IQR ou z-score), documente-les et décide du traitement.
8. **Export + journal.** Exporte `ventes_clean_<binome>.csv` et un **tableau-journal** des règles : `Problème | Règle appliquée | Justification | Lignes impactées`.

## Données (fichier réel)

`../data/ventes_sales.csv` (colonnes : `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`).

## Livrable attendu

Un notebook ou script `.py` commenté, le CSV nettoyé, et le journal des règles de nettoyage (dans le notebook ou en Markdown). Déposé sur la plateforme.

## Critères de réussite (OUI/NON)

- [ ] Le **diagnostic initial** (manquants, doublons, types) est présenté avant tout nettoyage ?
- [ ] Manquants, doublons et casse sont traités avec une **justification** pour chaque choix ?
- [ ] Les **dates** sont converties en ISO et les invalides gérées ?
- [ ] Les **négatifs/outliers** sont détectés et traités (pas juste supprimés sans réflexion) ?
- [ ] Un **journal des règles** liste problème, action, justification et lignes impactées ?
- [ ] Le CSV final est cohérent (`montant` recalculable) et le script est **rejouable** ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.3-nettoyage-qualite/`.
- pandas : `isna`, `drop_duplicates`, `str.strip/.title`, `to_datetime(format=...)`, IQR/quantile.
- Référentiel BC06 — compétence C3.
