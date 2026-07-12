# 04 — Travaux pratiques

> Outils : Power BI Desktop. Jeux de données fournis (ou crée des CSV d'exemple). Les solutions sont à déplier **après** avoir essayé.

## TP 1 — Repérer faits et dimensions

On te donne ces colonnes issues d'un export retail :
`Date`, `Magasin`, `Ville_magasin`, `Surface_m2`, `Produit`, `Catégorie`, `Client`, `Ville_client`, `Quantité`, `Montant`, `Remise`.

**Consigne** : classe chaque colonne en **Fait** ou **attribut de Dimension**, et indique pour chaque dimension à quelle table elle appartient.

<details>
<summary>Voir la solution</summary>

| Colonne | Type | Table cible |
|---|---|---|
| Date | Dimension | `Dim_Date` |
| Magasin | Dimension | `Dim_Magasin` |
| Ville_magasin | Dimension | `Dim_Magasin` |
| Surface_m2 | Dimension | `Dim_Magasin` |
| Produit | Dimension | `Dim_Produit` |
| Catégorie | Dimension | `Dim_Produit` (aplati = étoile) |
| Client | Dimension | `Dim_Client` |
| Ville_client | Dimension | `Dim_Client` |
| Quantité | **Fait** | `Faits_Ventes` |
| Montant | **Fait** | `Faits_Ventes` |
| Remise | **Fait** | `Faits_Ventes` |

Note : `Surface_m2` est un **attribut** du magasin (descriptif), pas un fait à sommer.
</details>

---

## TP 2 — Définir la granularité

Le commanditaire (responsable d'une enseigne du Nord) veut pouvoir répondre à :
- « Quel **produit** se vend le mieux dans le magasin de **Roubaix** au mois de **mars** ? »
- « Quel est le **panier moyen par client** ? »

**Consigne** : quel **grain** dois-tu choisir pour `Faits_Ventes` ? Quelles dimensions sont nécessaires ? Justifie.

<details>
<summary>Voir la solution</summary>

**Grain choisi** : **une ligne = un article vendu** (ligne de ticket).

Justification :
- « Quel produit se vend le mieux par magasin et par mois » → il faut **ProduitID, MagasinID, DateID** sur chaque ligne ⇒ grain au moins « par article ».
- « Panier moyen par client » → il faut **ClientID** (et idéalement un identifiant de ticket pour compter les paniers). Le grain fin permet de remonter au client.

Dimensions nécessaires : `Dim_Produit`, `Dim_Magasin`, `Dim_Client`, `Dim_Date`.
Un grain plus grossier (« total par magasin et par jour ») rendrait **impossible** l'analyse par produit et par client. On choisit donc le **grain fin**.
</details>

---

## TP 3 — Dessiner le schéma en étoile

**Consigne** : à partir du TP1/TP2, dessine (sur papier ou en ASCII) le **schéma en étoile** complet : table de faits au centre, 4 dimensions, et indique les **PK**, les **FK** et le **sens des relations (1 : \*)**.

<details>
<summary>Voir la solution</summary>

```
                 Dim_Date                         Dim_Produit
              DateID (PK)                       ProduitID (PK)
              Année, Mois, Trim...              Nom, Catégorie, Rayon
                    | 1                                | 1
                    | *                                | *
                    +-----------+         +------------+
                                |         |
                          +-----v---------v------+
                          |    Faits_Ventes      |
                          |  DateID    (FK)      |
                          |  ProduitID (FK)      |
                          |  MagasinID (FK)      |
                          |  ClientID  (FK)      |
                          |  Quantité (mesure)   |
                          |  Montant  (mesure)   |
                          |  Remise   (mesure)   |
                          +-----^---------^------+
                                |         |
                    +-----------+         +------------+
                    | *                                | *
                    | 1                                | 1
              Dim_Magasin                        Dim_Client
              MagasinID (PK)                     ClientID (PK)
              Nom, Ville, Surface                Nom, Ville_client
```

Toutes les relations sont **\* (faits) : 1 (dimension)**, sens du filtre **unique** (dimension → faits).
</details>

---

## TP 4 — Construire le modèle dans Power BI

**Consigne** :
1. Importe les 4 tables (faits + 3 dimensions) et crée `Dim_Date` en DAX (2023-01-01 → 2025-12-31).
2. Crée les 4 relations en vue Modèle.
3. Vérifie cardinalité **\* : 1** et filtre **unique** sur chacune.
4. Marque `Dim_Date` comme table de dates.
5. Crée un visuel de validation : montant total par ville de magasin, slicer par mois.

<details>
<summary>Voir la solution (étapes + DAX)</summary>

- Vue Modèle → glisser `Faits_Ventes[ProduitID]` sur `Dim_Produit[ProduitID]`, idem pour Magasin, Client, Date.
- Code DAX de la table de dates :

```dax
Dim_Date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2023, 1, 1 ), DATE ( 2025, 12, 31 ) ),
    "Année", YEAR ( [Date] ),
    "NumMois", MONTH ( [Date] ),
    "Mois", FORMAT ( [Date], "MMMM" ),
    "Trimestre", "T" & FORMAT ( [Date], "Q" )
)
```

- Clic droit `Dim_Date` → **Marquer comme table de dates** → colonne `Date`.
- Visuel : graphique en barres, axe = `Dim_Magasin[Ville]`, valeur = `Σ Faits_Ventes[Montant]`, slicer = `Dim_Date[Mois]`.
- Test : sélectionner « mars » doit recalculer les montants par ville → relations OK.
- Pense à désactiver **Options → Chargement des données → Date/heure automatique**.
</details>

---

## TP 5 — Détecter et corriger un many-to-many

**Consigne** : en créant la relation entre `Faits_Ventes[ClientID]` et `Dim_Client[ClientID]`, Power BI affiche une cardinalité **plusieurs-à-plusieurs** au lieu de **\* : 1**. Explique la cause probable et corrige.

<details>
<summary>Voir la solution</summary>

**Cause** : la colonne `ClientID` de `Dim_Client` **n'est pas unique** → il y a des **doublons** (le même client présent plusieurs fois). Power BI ne peut donc pas reconnaître le côté « 1 ».

**À faire** :
1. Dans Power Query, ouvre `Dim_Client`.
2. Vérifie/supprime les doublons sur `ClientID` (clic droit colonne → *Supprimer les doublons*), ou reconstruis la dimension proprement (une ligne par client).
3. Si plusieurs lignes correspondent à de vraies infos différentes pour un même ID → le **grain de la dimension est mauvais**, il faut le redéfinir.
4. Recharge : la relation passe alors en **\* : 1**, filtre **unique**.

Règle d'or : **une dimension a toujours une clé primaire unique**. Un many-to-many « subi » est presque toujours un problème de qualité de données dans la dimension.
</details>

---

## Pour aller plus loin

- Suite du module : [05 — Quiz et ressources](05-quiz-et-ressources.md)
