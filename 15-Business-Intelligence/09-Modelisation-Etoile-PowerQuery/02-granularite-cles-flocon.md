# 02 — Granularité, clés et flocon

## La granularité (le grain)

La **granularité**, c'est **ce que représente une ligne** de la table de faits. C'est la décision la plus importante du modèle.

Exemples de grains possibles pour des ventes :

- **Grain fin** : une ligne = un article d'un ticket de caisse (le plus détaillé).
- **Grain moyen** : une ligne = un ticket (total du ticket).
- **Grain grossier** : une ligne = total des ventes par magasin et par jour.

Règles :

- Choisis le grain **le plus fin dont tu as besoin** : tu peux toujours agréger vers le haut, jamais redescendre vers le détail.
- **Toutes les lignes** de la table de faits doivent avoir **le même grain** (ne mélange pas des lignes « par article » et des lignes « par jour »).
- Le grain détermine **quelles dimensions** tu peux relier (si le grain est « par jour et par magasin », tu n'as pas de dimension Client ni Produit).

> Exemple Nord : pour analyser quels **produits** se vendent le mieux par **magasin**, il faut un grain « **un article vendu** » → tu gardes ProduitID, MagasinID, ClientID, DateID sur chaque ligne.

---

## Clés primaires, clés étrangères et relations 1-à-plusieurs

- **Clé primaire (PK)** : colonne qui identifie **de façon unique** une ligne d'une dimension (`ProduitID` dans `Dim_Produit`). Pas de doublon, pas de valeur vide.
- **Clé étrangère (FK)** : colonne de la table de faits qui **pointe** vers la PK d'une dimension (`ProduitID` dans `Faits_Ventes`).
- **Relation 1-à-plusieurs (1 : \*)** : du côté **1** = la dimension (chaque valeur unique), du côté **plusieurs** = les faits (la valeur se répète).

```
Dim_Produit (côté 1)            Faits_Ventes (côté *)
ProduitID  Nom                  ... ProduitID  Montant
   P001    Café 1kg     1 ────── *      P001     13.80
   P002    Thé vert                     P001      6.90
   P003    Sucre                        P002      4.50
                                        P003      2.10
```

Une PK doit être **stable** et **technique** de préférence (un `ProduitID` plutôt que le nom du produit, qui peut changer ou contenir des fautes).

---

## Le modèle en flocon (snowflake) — et pourquoi souvent l'éviter

Le **flocon** apparaît quand une dimension est **éclatée en plusieurs tables reliées entre elles** au lieu d'être aplatie. Exemple : au lieu de mettre la catégorie directement dans `Dim_Produit`, on crée une table `Dim_Catégorie` séparée.

```
ÉTOILE (recommandé)                 FLOCON (à éviter le plus souvent)

 Faits_Ventes                        Faits_Ventes
      |                                   |
      | *                                 | *
      | 1                                 | 1
 Dim_Produit                         Dim_Produit
 (Nom, Catégorie,                    (Nom, CatégorieID) ──*──1── Dim_Catégorie
  Rayon dedans)                                                  (Catégorie, RayonID) ──*──1── Dim_Rayon
```

Pourquoi **préférer l'étoile** dans Power BI :

- Modèle **plus simple** à comprendre et à expliquer au commanditaire.
- **Moins de relations** → filtres plus rapides, moins de pièges.
- Le moteur de Power BI (VertiPaq) **compresse très bien** les dimensions aplaties : la redondance ne coûte quasiment rien.
- DAX plus simple à écrire.

Quand le flocon peut se justifier (rare) : dimension **énorme** et fortement réutilisée, ou contrainte forte de gouvernance. **Par défaut, tu aplatis → étoile.**

---

## Pour aller plus loin

- Suite du module : [03 — Table de dates et relations dans Power BI](03-table-de-dates-relations-power-bi.md)
