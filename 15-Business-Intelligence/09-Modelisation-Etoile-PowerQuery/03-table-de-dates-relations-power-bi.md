# 03 — Table de dates et relations dans Power BI

## La table de dates (dimension temps)

C'est la dimension **indispensable** de presque tout modèle BI. Plutôt que d'utiliser la colonne date brute des faits, on crée une **vraie table Date dédiée**.

Pourquoi une table de dates dédiée :

- Elle contient **toutes** les dates en continu (même les jours sans vente).
- Elle porte des attributs prêts à l'emploi : Année, Trimestre, Mois (nom + numéro), Semaine, Jour de semaine, Week-end/jour ouvré…
- Elle active les **fonctions de Time Intelligence** DAX (cumul annuel, comparaison N vs N-1, etc.).
- Elle peut être **partagée** par plusieurs tables de faits (ventes ET objectifs).

Exemple de création en DAX (onglet **Modélisation → Nouvelle table**) :

```dax
Dim_Date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2023, 1, 1 ), DATE ( 2025, 12, 31 ) ),
    "Année", YEAR ( [Date] ),
    "NumMois", MONTH ( [Date] ),
    "Mois", FORMAT ( [Date], "MMMM" ),
    "Trimestre", "T" & FORMAT ( [Date], "Q" ),
    "JourSemaine", FORMAT ( [Date], "dddd" ),
    "EstWeekend", IF ( WEEKDAY ( [Date], 2 ) >= 6, "Oui", "Non" )
)
```

Étape clé : **marquer la table comme table de dates** → clic droit sur `Dim_Date` → *Marquer comme table de dates* → choisir la colonne `Date`. Cela fiabilise le Time Intelligence.

---

## Les relations dans Power BI (vue Modèle)

La **vue Modèle** (icône à gauche, 3e icône représentant des tables reliées) est l'endroit où tu **vois et crées** les relations.

Trois propriétés essentielles d'une relation :

1. **Cardinalité**
   - **Plusieurs-à-un (\* : 1)** ou **Un-à-plusieurs (1 : \*)** = le cas **normal et souhaité** (faits → dimension).
   - **Un-à-un (1 : 1)** = rare (souvent signe qu'il faut fusionner les tables).
   - **Plusieurs-à-plusieurs (\* : \*)** = à **éviter** ; source de totaux faux et de lenteurs (voir encadré erreurs).

2. **Sens du filtre (Cross filter direction)**
   - **Simple (unique)** = le filtre va de la **dimension vers les faits** (recommandé). Sélectionner un produit filtre les ventes.
   - **Bidirectionnel** = le filtre va dans les deux sens. **À utiliser avec parcimonie** : peut créer des ambiguïtés et ralentir.

3. **Relation active / inactive**
   - Une seule relation **active** entre deux tables à la fois (trait plein). Les autres sont **inactives** (trait pointillé) et s'activent à la demande en DAX avec `USERELATIONSHIP`.

---

## Power BI pas à pas — créer le modèle en étoile

> Contexte : tu as importé `Faits_Ventes`, `Dim_Produit`, `Dim_Magasin`, `Dim_Client` et créé `Dim_Date`.

**Étape 1 — Ouvrir la vue Modèle**
Dans le bandeau de gauche, clique sur l'icône **Modèle** (les tables reliées). Tu vois tes tables sous forme de cartes avec leurs colonnes.

**Étape 2 — Vérifier les clés**
Assure-toi que chaque dimension a sa **PK unique** (`ProduitID`, `MagasinID`, `ClientID`, `Date`) et que `Faits_Ventes` contient les **FK** correspondantes.

**Étape 3 — Créer une relation par glisser-déposer**
Depuis `Faits_Ventes`, **fais glisser** `ProduitID` et **dépose-le** sur `ProduitID` de `Dim_Produit`. Power BI crée la relation et la détecte généralement en **\* : 1**.

**Étape 4 — Vérifier la cardinalité et le sens du filtre**
Double-clique sur le trait de relation (ou *Gérer les relations*). Contrôle :
- Cardinalité = **Plusieurs à un (\* : 1)**,
- Direction du filtre croisé = **Unique**,
- Case **Activer cette relation** cochée.

**Étape 5 — Répéter** pour `MagasinID`, `ClientID` et `DateID` (relié à `Dim_Date[Date]`).

**Étape 6 — Marquer la table de dates**
Clic droit sur `Dim_Date` → **Marquer comme table de dates** → colonne `Date`.

**Étape 7 — Soigner la mise en page**
Place la table de faits **au centre** et les dimensions autour → tu dois littéralement voir une **étoile**. Désactive *Auto Date/Time* (Options → Chargement des données) pour t'appuyer sur ta vraie `Dim_Date`.

**Étape 8 — Tester**
Crée un visuel : `Dim_Magasin[Ville]` en axe, `Σ Faits_Ventes[Montant]` en valeur. Ajoute un slicer `Dim_Date[Mois]`. Si filtrer un mois met bien à jour les montants par ville → ton modèle fonctionne.

---

> ### Encadré — Erreurs courantes à éviter
>
> - **Tout dans une seule table** (fichier plat) : pas de modèle, rapports lents et totaux fragiles.
> - **Relations plusieurs-à-plusieurs** non maîtrisées : viennent presque toujours d'une **dimension dont la PK n'est pas unique** (doublons). Nettoie la dimension pour rendre la clé unique.
> - **Filtre bidirectionnel partout** : crée des chemins de filtre ambigus et ralentit. Réserve-le aux cas précis.
> - **Granularité mélangée** : des lignes « par article » et « par jour » dans la même table de faits → agrégations fausses.
> - **Relier sur le libellé** (le nom du produit) au lieu d'un ID : casse à la moindre faute de frappe ou doublon.
> - **Oublier la table de dates** ou laisser l'« Auto Date/Time » : pas de comparaison temporelle propre, modèle gonflé de mini-tables cachées.
> - **Mesures dans la table de faits, attributs ailleurs** : ne mets pas de colonnes descriptives dans les faits si elles servent à filtrer → mets-les en dimension.

---

## Pour aller plus loin

- Suite du module : [04 — Travaux pratiques](04-travaux-pratiques.md)
