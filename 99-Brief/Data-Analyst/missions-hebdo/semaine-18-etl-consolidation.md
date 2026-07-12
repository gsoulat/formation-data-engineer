# Semaine 18 — Construire un ETL de consolidation multi-magasins (mission hebdomadaire)

> Phase 3 — module 3.2 (transformation & consolidation) · Durée : ~1-2 jours · Modalité : binôme · Compétence : C2 (extraire, transformer et consolider des données hétérogènes) niv.1

## Contexte (court, retail Nord)

Chaque magasin de NordRetail exporte ses ventes 2023… mais personne ne s'est mis d'accord sur le format. Lille utilise des points-virgules, Roubaix a renommé ses colonnes (`qte`, `CA`), Tourcoing et Valenciennes sont propres mais sans colonne ville. Résultat : impossible d'empiler les fichiers tels quels. La direction veut **un seul fichier consolidé** pour démarrer le reporting régional.

## Objectif de la mission

Construire un **ETL reproductible** (Power Query OU Python/pandas) qui extrait les 4 fichiers magasins, harmonise leurs formats hétérogènes, ajoute la ville, et produit un fichier consolidé unique — vérifié contre le fichier de référence.

## Consignes (étapes)

1. **Extract.** Charge les 4 sources : `ventes_lille.csv` (séparateur `;`), `ventes_roubaix.csv` (colonnes `date,categorie,produit,qte,CA`), `ventes_tourcoing.csv` et `ventes_valenciennes.csv` (`date,categorie,produit,quantite,montant`).
2. **Transform.** Harmonise vers un schéma cible commun : `date, ville, categorie, produit, quantite, montant`.
   - Renomme `qte → quantite` et `CA → montant` pour Roubaix.
   - Ajoute une colonne `ville` codée en dur par fichier (Lille, Roubaix, Tourcoing, Valenciennes).
   - Force les types : `date` en date ISO `YYYY-MM-DD`, `quantite` entier, `montant` décimal.
3. **Load.** Empile (union) les 4 sources et exporte `ventes_consolidees_<binome>.csv` en `,` avec en-têtes.
4. **Vérification.** Compare ton résultat à `ventes_consolidees.csv` (référence) : nombre de lignes, colonnes, somme de `montant` par ville. Note les écarts éventuels et explique-les (attention : la référence contient aussi Dunkerque/Amiens — concentre la comparaison sur tes 4 villes).
5. **Documentation.** Rédige 10 lignes décrivant le pipeline (étapes, transformations, comment le relancer).

## Données (fichier réel)

`../data/ventes_lille.csv`, `ventes_roubaix.csv`, `ventes_tourcoing.csv`, `ventes_valenciennes.csv`. Référence de contrôle : `ventes_consolidees.csv`.

## Livrable attendu

Le script `.py` (ou fichier `.pqx`/classeur Power Query), le CSV consolidé produit, et une courte note de documentation (Markdown). Déposé sur la plateforme (dépôt Git apprécié).

## Critères de réussite (OUI/NON)

- [ ] Les **4 fichiers** sont chargés malgré séparateurs et noms de colonnes différents ?
- [ ] Le schéma cible `date, ville, categorie, produit, quantite, montant` est respecté ?
- [ ] La colonne **ville** est correctement ajoutée pour chaque source ?
- [ ] Les **types** (date ISO, quantité entière, montant décimal) sont corrects ?
- [ ] La somme des `montant` par ville **correspond** aux lignes équivalentes de la référence ?
- [ ] Le pipeline est **documenté et rejouable** (relance sans intervention manuelle) ?

## Ressources (renvoi au cours)

- Cours : `cours/03-flux-bi/3.2-etl-consolidation/`.
- pandas : `read_csv(sep=...)`, `rename`, `assign`, `concat`. Power Query : Append Queries, Replace/Rename, Change Type.
- Référentiel BC06 — compétence C2.
