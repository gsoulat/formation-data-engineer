# Semaine 07 — Tendances temporelles et KPI SMART (mission hebdomadaire)

> Phase 1 — Ajuster/analyser un tableau de bord métier · Modules 1.3 (Tendances) + 1.4 (Indicateurs clés) · Durée : ~1 à 2 jours · Modalité : binôme · Compétences C6 (Identifier et interpréter des tendances) — niveau 1 (IMITER) ; C16 (Identifier les indicateurs clés) — niveau 1 → 2 (IMITER → ADAPTER)

## Contexte (court, retail Nord)

Le retail des Hauts-de-France vit au rythme des saisons : les soldes d'hiver, le pic de Noël, le creux de la rentrée. La direction de NordRetail veut comprendre **quand** l'activité monte et descend, et surtout disposer d'une poignée d'indicateurs fiables pour piloter mois après mois. Cette mission transforme l'EDA de la semaine 6 en lecture temporelle + en KPI prêts à afficher.

C'est l'avant-dernière brique avant le projet de fin de phase (`BRIEF_1_TABLEAU_DE_BORD_METIER.md`). Ce projet se déroule sur le **même univers NordRetail** (dossier `data/`) en scénario complet de bout en bout : la démarche de définition de tendances et d'indicateurs travaillée ici y sera **réinvestie et approfondie**. Cette montée en autonomie est attendue au niveau RNCP.

## Objectif de la mission

1. Analyser les tendances temporelles des ventes (saisonnalité, pics de soldes et de Noël).
2. Définir et documenter 4 à 5 KPI **SMART** prêts à intégrer un tableau de bord.

## Consignes (étapes)

1. **Agrégation mensuelle.** À partir de `ventes_magasins.csv`, crée une colonne `mois` (`df["date"].dt.to_period("M")`) et calcule le CA mensuel : `df.groupby("mois")["montant"].sum()`.
2. **Courbe d'évolution.** Trace le CA mensuel. Repère visuellement les pics (décembre / Noël) et les creux. Annote la saisonnalité.
3. **Effet soldes / Noël.** Compare les mois de soldes (janvier, juillet) et décembre au reste de l'année. Le CA y est-il significativement plus élevé ? De combien (%) ?
4. **Comparaison par groupe dans le temps.** Trace au moins une tendance segmentée : CA mensuel par `categorie` **ou** par `type` (Magasin vs E-commerce). Une saisonnalité diffère-t-elle d'un groupe à l'autre ?
5. **Prudence d'interprétation.** Pour chaque constat, distingue ce que tu observes (corrélation) de ce que tu supposes (cause). Pas de raccourci corrélation → causalité.
6. **Définir 4-5 KPI SMART.** Pour le tableau de bord à venir, choisis 4 ou 5 indicateurs (ex. CA total, panier moyen, marge totale, nombre de commandes, taux de remise moyen). Pour chacun, remplis : **nom · formule exacte · granularité (mois/ville/…) · cible chiffrée · source (colonne)**. Vérifie que chaque KPI est SMART (Spécifique, Mesurable, Atteignable, Réaliste, Temporel).

## Données (fichier réel)

`../data/ventes_magasins.csv` — colonnes `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`.

## Livrable attendu

- Un notebook `tendances.ipynb` : courbe CA mensuel + tendance segmentée + interprétations écrites.
- Un fichier `dictionnaire_kpi.md` : tableau des 4-5 KPI (nom, formule, granularité, cible, source) avec la justification SMART.

## Critères de réussite (OUI/NON)

- Le CA mensuel est calculé et visualisé sous forme de courbe : OUI / NON
- La saisonnalité (Noël, soldes) est repérée et chiffrée (% vs moyenne) : OUI / NON
- Au moins une tendance segmentée (catégorie ou type) est analysée : OUI / NON
- Les interprétations ne confondent pas corrélation et causalité : OUI / NON
- 4 à 5 KPI sont définis avec formule, granularité, cible et source : OUI / NON
- Chaque KPI est justifié comme SMART : OUI / NON

## Ressources (renvoi au cours)

- Cours modules 1.3 (tendances) + 1.4 (indicateurs clés / KPI).
- Méthode SMART pour objectifs et indicateurs.
- Documentation pandas séries temporelles : https://pandas.pydata.org/docs/user_guide/timeseries.html
- Projet de fin de phase associé : `BRIEF_1_TABLEAU_DE_BORD_METIER.md`.
