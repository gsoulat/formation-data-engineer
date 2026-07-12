# Semaine 22 — Dashboard BI expert (2/2) : interactivité, perf, accessibilité, storytelling (mission hebdomadaire)

> Phase 3 — module 3.5 (tableau de bord expert) · Durée : ~2 jours · Modalité : solo · Compétences : C16, C17, C18 niv.3

## Contexte (court, retail Nord)

Ta page d'accueil de la S21 a plu, mais la direction de NordRetail veut un outil **réellement exploitable en réunion** : navigation fluide entre vues, performances correctes sur l'année complète, lisible par tous (dont un membre du comité daltonien), et qui **raconte une histoire** plutôt que d'aligner des graphiques. Tu finalises ton dashboard expert.

## Objectif de la mission

Finaliser le tableau de bord démarré en S21 en y ajoutant **interactivité, optimisation des performances, accessibilité et storytelling**, jusqu'à un livrable présentable au comité.

> **Progressivité S21 → S22.** En S21 tu as posé les fondations en autonomie (cadrage, modèle étoile, page 1 avec KPI). Cette semaine, on monte d'un cran : passer d'un dashboard *correct* à un dashboard *réellement exploitable en réunion*. Le **nouveau** par rapport à S21 = (1) plusieurs pages cohérentes et navigables, (2) interactivité avancée (drill-down, segments synchronisés, signets), (3) optimisation des performances du modèle, (4) accessibilité (daltoniens, contrastes) et (5) storytelling. Tu ne repars pas de zéro : tu enrichis ton `.pbix`/projet Looker de la S21.
>
> **Rappel — critères de niveau 3 (autonomie experte).** À ce niveau, on n'évalue plus seulement « est-ce que ça marche », mais ta capacité à :
> - **Transposer** : adapter à un contexte nouveau (plusieurs publics, contrainte d'accessibilité, réunion comité) des techniques déjà connues, sans modèle à recopier.
> - **Justifier tes choix** : pour chaque décision (palette, type de visuel, optimisation, parcours de lecture), être capable d'expliquer *pourquoi* — c'est ce qui distingue le niveau 3 d'une simple exécution.

## Consignes (étapes)

1. **Pages thématiques.** Ajoute 2-3 pages : *Magasins* (comparaison régionale), *Produits/Catégories* (mix et marge), *Objectifs* (atteinte vs réel). Cohérence visuelle entre pages.
2. **Interactivité.** Mets en place segments synchronisés, drill-down (catégorie → produit), info-bulles enrichies, et navigation entre pages (boutons/signets). L'utilisateur doit pouvoir explorer sans toi.
3. **Performance.** Optimise le modèle : retire les colonnes inutiles, privilégie les mesures aux colonnes calculées, vérifie la granularité de la table de faits. Note 2-3 actions d'optimisation faites.
4. **Accessibilité.** Applique une palette **safe daltoniens**, contrastes suffisants, titres explicites, ordre de tabulation et textes alternatifs. Évite la couleur comme seul vecteur d'information.
5. **Storytelling.** Structure la lecture (du général au détail), ajoute titres porteurs de sens et 2-3 annotations/insights clés. Le dashboard doit délivrer un message, pas juste des chiffres.
6. **Note finale.** Rédige une fiche utilisateur (½ page) : à quoi sert chaque page, comment naviguer.

## Données (fichier réel)

Mêmes sources qu'en S21 : `Dim_*.csv` + `Faits_Ventes.csv` + `objectifs_2024.xlsx` (tu repars de ton `.pbix`/projet Looker de la S21).

## Livrable attendu

Le fichier `.pbix` final (ou lien Looker partagé), la fiche utilisateur, et une note d'optimisation/accessibilité. Déposé sur la plateforme. **Ce dashboard t'entraîne aux compétences mobilisées dans le projet certificatif BC06 (S26-28, voir `briefs/brief-3-projet-certificatif-bc06.md`). Ce projet repose sur d'autres sources (Kaggle + API + référentiel data.gouv) : tu ne réutiliseras pas ce livrable NordRetail tel quel, mais tu transposeras sur ces nouvelles données la démarche de dashboard expert travaillée ici — transposition volontaire et attendue au niveau RNCP.**

## Critères de réussite (OUI/NON)

- [ ] Le dashboard compte **3-4 pages cohérentes** et navigables ?
- [ ] L'**interactivité** (segments synchronisés, drill-down, navigation) fonctionne sans aide ?
- [ ] Au moins **2 optimisations de performance** sont réalisées et documentées ?
- [ ] L'**accessibilité** est traitée (palette daltoniens, contrastes, titres) ?
- [ ] Le **storytelling** est présent (parcours de lecture + insights annotés) ?
- [ ] La fiche utilisateur explique l'usage et la navigation ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.5-dashboard-expert/`.
- Power BI : signets, drill-down, Performance Analyzer, thèmes accessibles.
- Référentiel BC06 — compétences C16, C17, C18 (niv.3).
