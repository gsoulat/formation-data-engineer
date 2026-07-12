# Semaine 13 — Visualisations interactives & accessibilité (mission hebdomadaire)

> Phase 2 — Solution BI pour analyse avancée · Module 2.4 · Durée : 1 à 2 jours · Modalité : binôme · Compétence : C17 (choisir des visualisations pertinentes) niv. 2

## Contexte

Le tableau de bord de NordRetail affiche les bons chiffres, mais reste figé : les responsables de magasin veulent pouvoir filtrer eux-mêmes par ville, descendre du trimestre au mois, et retrouver un point de vue préparé sans tout reconfigurer. La direction insiste aussi pour que l'outil reste lisible par tous, y compris une collègue daltonienne.

## Objectif de la mission

Enrichir le tableau de bord existant avec de l'interactivité (drill-down, segments, signets) et le rendre accessible selon les principes WCAG.

## Consignes (étapes)

1. Repars du rapport des semaines 11-12 (modèle + mesures DAX).
2. **Hiérarchie & drill-down** : crée une hiérarchie de dates (Année → Trimestre → Mois) et une hiérarchie produit (Catégorie → Produit). Active le drill-down sur au moins un visuel d'évolution du CA.
3. **Segments (slicers)** : ajoute des segments par `ville`, par `categorie` et par période. Vérifie qu'ils filtrent l'ensemble de la page de façon cohérente.
4. **Signets (bookmarks)** : crée au moins 2 signets correspondant à des vues métier prêtes à présenter (ex. « Vue direction — national », « Vue manager — Lille »), avec des boutons de navigation.
5. **Interactions** : configure les interactions entre visuels (un clic sur une catégorie filtre les autres graphiques) et désactive celles qui n'ont pas de sens.
6. **Accessibilité (WCAG)** :
   - palette à contraste suffisant et compatible daltonisme (ne pas coder l'info uniquement par la couleur) ;
   - titres explicites, texte de remplacement (alt text) sur les visuels clés ;
   - ordre de tabulation logique et taille de police lisible.
7. Vérifie le contraste avec un outil dédié et corrige si besoin.

## Données (../data/)

Modèle et mesures issus de `Faits_Ventes.csv` + `Dim_*.csv` (semaines 11-12).

## Livrable attendu

Le `.pbix` enrichi (drill-down, segments, signets, interactions, réglages d'accessibilité), **plus** une mini-fiche (1 page) listant les interactions ajoutées et les contrôles d'accessibilité effectués (avec résultats du test de contraste).

## Critères de réussite

- [ ] Le drill-down fonctionne sur au moins une hiérarchie (date ou produit) (OUI/NON)
- [ ] Des segments par ville, catégorie et période filtrent la page de façon cohérente (OUI/NON)
- [ ] Au moins 2 signets de vues métier sont accessibles via des boutons (OUI/NON)
- [ ] Les interactions entre visuels sont configurées intentionnellement (OUI/NON)
- [ ] La palette respecte le contraste et ne repose pas que sur la couleur (OUI/NON)
- [ ] Titres, alt text et lisibilité respectent les principes WCAG (OUI/NON)

## Ressources (renvoi au cours)

Module 2.4 — Visualisations interactives (hiérarchies, drill-down, slicers, bookmarks). Principes WCAG (contraste, daltonisme, alt text). Documentation Power BI : accessibilité des rapports.
