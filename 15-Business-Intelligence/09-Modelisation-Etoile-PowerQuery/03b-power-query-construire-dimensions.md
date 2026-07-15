# 03b — Construire les dimensions dans Power Query

### 🎥 En vidéo

▶️ *Power Query : dépivoter, regrouper, extraire une dimension* — cherche
« [power query unpivot regrouper français](https://www.youtube.com/results?search_query=power+query+unpivot+regrouper+fran%C3%A7ais) »
et « [power query construire dimension table étoile](https://www.youtube.com/results?search_query=power+query+construire+dimension+mod%C3%A8le+%C3%A9toile) » sur YouTube.

| | |
|---|---|
| **Titre** | Construire les dimensions dans Power Query |
| **Phase** | Phase 2 — BI avancée |
| **Durée** | ~10 h |
| **Objectif** | Transformer un fichier plat en tables de dimensions et de faits **dans l'outil**, de façon rejouable |
| **Pré-requis** | [01 — Du fichier plat au modèle en étoile](01-du-fichier-plat-au-modele-en-etoile.md) · [02 — Granularité, clés et flocon](02-granularite-cles-flocon.md) |

---

## Objectifs pédagogiques

À la fin de cette leçon, tu seras capable de :

- Comprendre l'éditeur Power Query et la logique des **étapes appliquées**.
- **Extraire une dimension** d'un fichier plat (sélection + suppression des doublons).
- Créer une **clé de substitution** (colonne d'index).
- **Dépivoter (Unpivot)** un export « en colonnes » pour le rendre analysable.
- **Regrouper (Group By)** pour agréger.
- Choisir entre **Fusionner (Merge)** et **Ajouter (Append)**.
- Lire et retoucher le **code M** généré.

---

## Le problème : les modules 01-03 modélisent « sur le papier »

Tu sais dessiner un modèle en étoile (une table de faits, des dimensions). Mais tes données arrivent
**à plat** : un seul fichier `ventes_retail_nord.csv` où chaque ligne mélange la vente, le produit,
le magasin et le client. Personne ne te livre `Dim_Produit` toute prête. **C'est à toi de la
fabriquer** — et l'outil pour ça, c'est **Power Query** (l'éditeur de requêtes de Power BI / Excel).

```text
ventes_retail_nord.csv (à plat)
date | ville | type | categorie | produit | quantite | prix_unitaire | remise | montant | marge | client_id
```

Objectif : en tirer `Dim_Produit`, `Dim_Magasin`, `Dim_Client` + une table de faits `Faits_Ventes`
qui ne garde que des **clés** et des **mesures**.

> **Analogie** — Power Query, c'est une **recette** : tu enchaînes des étapes (nettoyer, découper,
> regrouper) et Power BI **rejoue la recette à chaque actualisation**. Tu ne modifies jamais le
> fichier source à la main : tu écris la recette une fois, elle tourne toute seule ensuite.

---

## 1. L'éditeur et les étapes appliquées

`Accueil → Transformer les données` ouvre l'éditeur Power Query. À droite, le volet **Étapes
appliquées** journalise **chaque** transformation. C'est ton historique rejouable : tu peux revenir
en arrière, insérer une étape, la supprimer.

Premiers réflexes sur un CSV :

1. **Utiliser la première ligne comme en-têtes** (`Transformer → Utiliser la première ligne pour les en-têtes`).
2. **Typer les colonnes** (`date` en Date, `montant`/`marge` en Nombre décimal, `quantite` en Nombre entier).

> 🛑 **Erreur courante** — laisser Power BI « détecter les types » tout seul en début de requête. S'il
> détecte mal une colonne, chaque actualisation risque de casser. Type **explicitement**, c'est une
> étape que tu contrôles.

---

## 2. Extraire une dimension (le geste central)

Une dimension = les valeurs **uniques** d'un « sujet ». Pour `Dim_Produit` :

1. **Dupliquer** la requête (clic droit sur la requête → *Dupliquer*) : on ne touche pas à l'original.
2. Ne **garder que les colonnes produit** : `produit`, `categorie`, `prix_unitaire`
   (`Accueil → Choisir les colonnes`).
3. **Supprimer les doublons** (`Accueil → Supprimer les lignes → Supprimer les doublons`).

Tu obtiens la liste unique des produits. En code M, ces trois étapes ressemblent à :

```powerquery
let
    Source = ventes_retail_nord,
    Colonnes = Table.SelectColumns(Source, {"produit", "categorie", "prix_unitaire"}),
    Uniques = Table.Distinct(Colonnes)
in
    Uniques
```

### La clé de substitution

Une dimension a besoin d'une **clé technique** stable (un identifiant numérique), indépendante du
libellé. On ajoute une **colonne d'index** :

`Ajouter une colonne → Colonne d'index → À partir de 1` → renomme-la `produit_id`.

> **Analogie** — La clé de substitution, c'est le **numéro de vestiaire** : peu importe le nom du
> manteau, le ticket `42` le retrouve. Si un produit est renommé, sa clé ne bouge pas.

Répète pour `Dim_Magasin` (colonnes `ville`, `type`) et `Dim_Client` (`client_id` existe déjà : il
sert de clé, inutile d'en recréer une).

---

## 3. Dépivoter (Unpivot) : l'arme secrète

Beaucoup d'exports arrivent **« en largeur »** : une colonne par mois. Illisible pour l'analyse.

```text
produit    | jan | fev | mar
Perceuse   | 120 | 90  | 150
```

Power Query **dépivote** ça en un tableau « long », le seul format qu'aime la BI :
sélectionne les colonnes de mois → clic droit → **Supprimer le pivot des colonnes** (*Unpivot*).

```text
produit    | mois | ventes
Perceuse   | jan  | 120
Perceuse   | fev  | 90
Perceuse   | mar  | 150
```

> **Analogie** — Dépivoter, c'est **déplier un tableau Excel** fait pour l'œil humain (large) en un
> tableau fait pour la machine (long). Retiens : *un fait = une ligne*.

> 🛑 **Erreur courante** — utiliser *« Supprimer le pivot des colonnes **sélectionnées** »* au lieu de
> *« … des **autres** colonnes »*. Si de nouveaux mois arrivent, la seconde option les inclut
> automatiquement ; la première les oublie.

---

## 4. Regrouper (Group By)

Pour agréger à une granularité voulue : `Transformer → Regrouper par`. Exemple — CA par ville :

```powerquery
Table.Group(Source, {"ville"}, {{"CA", each List.Sum([montant]), type number}})
```

Utile pour bâtir une table de faits **agrégée** ou vérifier des totaux avant modélisation.

---

## 5. Fusionner (Merge) vs Ajouter (Append)

Deux opérations que les débutants confondent :

| Opération | Ce qu'elle fait | Analogie | Cas d'usage |
|---|---|---|---|
| **Ajouter (Append)** | Empile des lignes (même structure) | Mettre bout à bout | Consolider `ventes_lille.csv` + `ventes_roubaix.csv` + … |
| **Fusionner (Merge)** | Colle des colonnes via une clé commune | Jointure SQL | Rapatrier `produit_id` dans la table de faits |

Pour finaliser la **table de faits**, on **fusionne** le fichier plat avec chaque dimension sur le
libellé, on récupère la **clé** (`produit_id`, `magasin_id`), puis on **supprime les colonnes de
libellé** : la table de faits ne garde que des clés + les mesures (`quantite`, `montant`, `marge`).

```text
Faits_Ventes final :
date_id | magasin_id | produit_id | client_id | quantite | montant | marge
```

> 🛑 **Erreur courante** — garder les libellés (`produit`, `ville`) dans la table de faits « au cas
> où ». C'est exactement ce qu'on veut éviter : les libellés vivent dans les dimensions, la table de
> faits reste étroite et rapide.

---

## 6. Actualisation

La force de Power Query : la recette se **rejoue**. `Accueil → Actualiser` relance toutes les étapes
sur les nouvelles données. En production, on programme un **rafraîchissement planifié** via une
**passerelle** (*gateway*) — détaillé dans [module 15 — ETL & automatisation](../15-ETL-Automatisation/).

---

## 🧪 Mini-TP

### TP 1 — Construire `Dim_Produit`

À partir de `ventes_retail_nord.csv`, produis une table `Dim_Produit` à 4 colonnes :
`produit_id` (clé), `produit`, `categorie`, `prix_unitaire`.

<details>
<summary>💡 Corrigé (étapes attendues)</summary>

1. Dupliquer la requête source.
2. `Choisir les colonnes` → `produit`, `categorie`, `prix_unitaire`.
3. `Supprimer les doublons`.
4. `Ajouter une colonne → Colonne d'index → À partir de 1` → renommer `produit_id`.
5. Réordonner : `produit_id` en tête. Vérifier les types.

```powerquery
let
    Source = ventes_retail_nord,
    Cols = Table.SelectColumns(Source, {"produit","categorie","prix_unitaire"}),
    Uniques = Table.Distinct(Cols),
    Indexee = Table.AddIndexColumn(Uniques, "produit_id", 1, 1, Int64.Type)
in
    Indexee
```
</details>

### TP 2 — Consolider trois magasins

On te livre `ventes_lille.csv`, `ventes_roubaix.csv`, `ventes_tourcoing.csv`. Objectif : une seule
table propre.

<details>
<summary>💡 Corrigé</summary>

C'est un **Append** (même structure, on empile) : `Accueil → Ajouter des requêtes → Ajouter en tant
que nouvelle requête`, sélectionner les trois. Puis typer, dédoublonner si besoin. **Merge serait une
erreur** ici : on n'ajoute pas de colonnes, on ajoute des lignes.
</details>

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Dépivoter des colonnes](https://www.youtube.com/results?search_query=power+query+unpivot+d%C3%A9pivoter+fran%C3%A7ais) | Power BI France | FR | Passer d'un tableau large à long |
| [Extraire une table de dimension](https://www.youtube.com/results?search_query=power+query+create+dimension+table+from+flat+file) | Guy in a Cube | EN | Le geste « distinct + index » |
| [Merge vs Append](https://www.youtube.com/results?search_query=power+query+merge+vs+append+fran%C3%A7ais) | Enterprise DNA | EN/FR | Ne plus jamais les confondre |
| [Group By dans Power Query](https://www.youtube.com/results?search_query=power+query+group+by+regrouper) | Curbal | EN | Agréger sans quitter l'éditeur |

---

## À retenir

- Une **dimension** se fabrique : *garder les colonnes du sujet → supprimer les doublons → ajouter un
  index (clé)*.
- **Dépivoter** transforme un export « en largeur » (une colonne par mois) en tableau analysable
  (*un fait = une ligne*).
- **Append** empile des lignes ; **Merge** rapproche des colonnes via une clé.
- La **table de faits** finale ne garde que des **clés + mesures** ; les libellés restent dans les
  dimensions.
- Tout est **rejouable** : Power Query enregistre la recette et la relance à chaque actualisation.
