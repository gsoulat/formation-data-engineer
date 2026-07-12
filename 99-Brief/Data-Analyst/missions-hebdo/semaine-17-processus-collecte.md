# Semaine 17 — Cartographier les sources et concevoir un processus de collecte RGPD (mission hebdomadaire)

> Phase 3 — module 3.1 (flux d'alimentation BI) · Durée : ~1 jour · Modalité : binôme · Compétence : C1 (recueillir/cartographier les besoins et sources de données) niv.1

## Contexte (court, retail Nord)

NordRetail veut enfin alimenter sa BI de façon structurée. Aujourd'hui, la donnée vient de partout : caisses des magasins de Lille, Roubaix, Tourcoing, Valenciennes, Dunkerque et Amiens, site e-commerce, fichier clients fidélité, exports comptables, et même des fichiers Excel d'objectifs envoyés par la direction. Avant de construire le moindre pipeline, la DSI te demande de **poser le plan** : d'où vient la donnée, qui la possède, et comment la collecter sans enfreindre le RGPD (les clients sont des personnes physiques identifiables).

## Objectif de la mission

Produire une **cartographie des sources de données** de NordRetail et un **schéma de processus de collecte** conforme RGPD, sur papier ou outil de schéma (pas de code cette semaine).

## Consignes (étapes)

1. **Inventaire des sources.** À partir des datasets fournis (`../data/`), identifie au moins 6 sources distinctes (ventes magasins, e-commerce, référentiel produits, objectifs, base SQL clients/commandes, etc.). Pour chacune, note : nom, format (CSV/XLSX/SQL/API), propriétaire métier, fréquence de mise à jour, volume estimé.
2. **Tableau de cartographie.** Synthétise l'inventaire dans un tableau : `Source | Format | Donnée contenue | Propriétaire | Fréquence | Données personnelles (O/N)`.
3. **Repère les données personnelles.** Marque les champs relevant du RGPD (ex. `email`, `nom`, `prenom`, `client_id` rattaché à une personne). Indique pour chacun la **finalité** et la **base légale** (intérêt légitime, consentement, contrat).
4. **Schéma de collecte.** Dessine le flux : source → mode de collecte (export manuel, connecteur, API, requête SQL) → zone de réception (dossier brut / staging) → étape de pseudonymisation. Représente clairement **où** les données personnelles sont minimisées ou pseudonymisées.
5. **Mini-registre RGPD.** Rédige 4-5 lignes de registre de traitement : finalité, données collectées, durée de conservation, mesures de sécurité.

## Données (fichier réel)

Dossier `../data/` : `ventes_magasins.csv`, les `ventes_<ville>.csv`, `referentiel_produits.csv`, `objectifs_2024.xlsx`, `setup.sql` (tables `clients` avec `email`/`nom`/`prenom`, `commandes`, `produits`, `magasins`). Tu n'exécutes rien : tu observes en-têtes et schéma pour cartographier.

## Livrable attendu

Un document (PDF/Markdown) contenant : le tableau de cartographie des sources, le schéma de processus de collecte (photo du croquis ou export d'outil type draw.io/Excalidraw), et le mini-registre RGPD. Déposé sur la plateforme.

## Critères de réussite (OUI/NON)

- [ ] Au moins **6 sources** sont inventoriées avec format, propriétaire et fréquence ?
- [ ] Le tableau distingue clairement les sources contenant des **données personnelles** ?
- [ ] Chaque donnée personnelle a une **finalité ET une base légale** indiquées ?
- [ ] Le schéma montre le flux source → staging avec une étape de **pseudonymisation/minimisation** ?
- [ ] Le mini-registre mentionne **durée de conservation et mesures de sécurité** ?
- [ ] Le rendu est lisible, sourcé sur les vrais datasets, et déposé dans les temps ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.1-collecte-sources/`.
- [CNIL — Le registre des activités de traitement](https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement) et les 6 bases légales.
- Référentiel BC06 — compétence C1.
