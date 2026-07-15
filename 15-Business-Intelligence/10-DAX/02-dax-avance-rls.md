# 02 — DAX avancé & sécurité (RLS)

### 🎥 En vidéo

▶️ *Comprendre RELATED, SUMX et le contexte en DAX* — cherche
« [dax related sumx context transition français](https://www.youtube.com/results?search_query=dax+related+sumx+context+transition+fran%C3%A7ais) »
et « [power bi row level security rls tutoriel](https://www.youtube.com/results?search_query=power+bi+row+level+security+rls+tutoriel+fran%C3%A7ais) » sur YouTube.

| | |
|---|---|
| **Titre** | DAX avancé & Row-Level Security |
| **Phase** | Phase 2 — BI avancée |
| **Durée** | ~30 h |
| **Objectif** | Écrire du DAX qui traverse les relations, itère ligne à ligne et sécurise l'accès aux données selon l'utilisateur connecté |
| **Pré-requis** | [01 — DAX & mesures](01-dax-mesures.md) (mesure vs colonne, `CALCULATE`, contexte de filtre) |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

- Rapatrier une colonne d'une table liée avec **`RELATED`** / **`RELATEDTABLE`**.
- Écrire un calcul **ligne à ligne** avec les **itérateurs** `SUMX`, `AVERAGEX`, `RANKX`.
- Expliquer et utiliser la **transition de contexte** (ce que `CALCULATE` fait *vraiment*).
- Activer une relation inactive avec **`USERELATIONSHIP`**.
- Mettre en place une **Row-Level Security (RLS)** statique **et** dynamique.
- **Déboguer** une mesure DAX qui donne un résultat faux.

---

## 1. `RELATED` : suivre le fil de la relation

Ton modèle en étoile relie `Faits_Ventes` à `Dim_Produit` (via `produit_id`). Depuis la table de
faits, tu ne « vois » pas directement la colonne `categorie` : elle vit dans la dimension.
`RELATED` va la chercher **de l'autre côté de la relation**.

> **Analogie** — `RELATED`, c'est tirer sur le fil qui relie deux tables pour ramener à toi une
> information rangée ailleurs. Le fil, c'est la relation (`produit_id`). Sans fil, pas de `RELATED`.

```dax
-- Colonne calculée dans Faits_Ventes : ramener la catégorie du produit vendu
Categorie = RELATED ( Dim_Produit[categorie] )
```

`RELATED` va **du côté « plusieurs » vers le côté « un »** (de la table de faits vers la dimension).
Dans l'autre sens (d'une dimension vers ses nombreuses ventes), on utilise **`RELATEDTABLE`**, qui
renvoie *un paquet de lignes* :

```dax
-- Mesure/colonne dans Dim_Produit : nombre de ventes de ce produit
Nb_ventes_produit = COUNTROWS ( RELATEDTABLE ( Faits_Ventes ) )
```

> 🛑 **Erreur courante** — utiliser `RELATED` sans relation active entre les deux tables : Power BI
> renvoie une erreur *« La colonne … ne peut pas être trouvée »*. Vérifie d'abord ta relation dans
> la vue Modèle.

---

## 2. Les itérateurs : calculer ligne à ligne (`SUMX`, `AVERAGEX`, `RANKX`)

`SUM ( Faits_Ventes[montant] )` additionne une colonne **déjà calculée**. Mais si le calcul doit se
faire **ligne par ligne avant d'additionner**, il faut un **itérateur** (les fonctions en `X`).

> **Analogie** — `SUM` lit une colonne déjà remplie. `SUMX` prend un cahier vierge, calcule le
> résultat sur *chaque ligne*, puis fait le total. Les `X` = « eXécute une formule par ligne ».

```dax
-- CA recalculé à la ligne : quantité × prix, remise déduite, PUIS on somme
CA_net = SUMX (
    Faits_Ventes,
    Faits_Ventes[quantite] * Faits_Ventes[prix_unitaire] * ( 1 - Faits_Ventes[remise] )
)
```

Pourquoi ne pas faire `SUM(quantite) * SUM(prix_unitaire)` ? Parce que ce serait
`(total des quantités) × (total des prix)` = un chiffre **absurde**. La multiplication doit se faire
**dans chaque vente**, pas sur les totaux. C'est *la* raison d'être des itérateurs.

`RANKX` classe un élément par rapport aux autres :

```dax
-- Classement des magasins par CA (1 = meilleur)
Rang_magasin =
RANKX (
    ALL ( Dim_Magasin[ville] ),   -- l'univers du classement = tous les magasins
    [CA_net],                     -- le critère
    ,
    DESC
)
```

> 🛑 **Erreur courante** — oublier `ALL(...)` dans `RANKX` : chaque magasin se compare alors à
> lui-même seul → tout le monde est classé **1er**. L'itérateur a besoin de voir *tout l'univers*.

---

## 3. La transition de contexte : le concept qui piège tout le monde

Rappel du module 01 : il existe deux contextes — le **contexte de ligne** (« je suis sur une ligne
précise ») et le **contexte de filtre** (« quels filtres s'appliquent au calcul »). La question qui
piège 90 % des débutants : *que se passe-t-il quand on met un `SUM` à l'intérieur d'un itérateur ?*

> **Analogie** — Le contexte de ligne, c'est « je regarde **cette** vente ». Le contexte de filtre,
> c'est « je calcule pour **ce** sous-total ». La **transition de contexte**, c'est le moment magique
> où `CALCULATE` transforme *« je suis sur cette ligne »* en *« filtre le calcul sur cette ligne »*.

`CALCULATE` (et l'appel d'une **mesure**, qui contient un `CALCULATE` implicite) déclenche cette
transition. Exemple : la part de chaque vente dans le total de son client.

```dax
Part_dans_client =
DIVIDE (
    Faits_Ventes[montant],                              -- montant de la ligne
    CALCULATE (                                         -- transition de contexte :
        SUM ( Faits_Ventes[montant] ),                 -- total…
        ALLEXCEPT ( Faits_Ventes, Faits_Ventes[client_id] )  -- …du client de cette ligne
    )
)
```

Sans `CALCULATE`, le `SUM` ignorerait la ligne courante et renverrait le total général → un ratio
faux. **`CALCULATE` = le déclencheur de la transition de contexte.** Garde cette phrase en tête.

---

## 4. `USERELATIONSHIP` : activer une relation inactive

Entre deux tables, Power BI n'autorise **qu'une seule relation active**. Si ta table de faits a
plusieurs dates (ex. une `date de commande` **et** une `date de livraison`), une seule pilote les
calculs temporels ; l'autre est *inactive* (trait pointillé dans la vue Modèle).

`USERELATIONSHIP` réveille la relation inactive **le temps d'un calcul** :

```dax
-- CA basé sur la date de LIVRAISON (relation inactive), sans toucher au reste du modèle
CA_par_livraison =
CALCULATE (
    [CA_net],
    USERELATIONSHIP ( Faits_Ventes[date_livraison_id], Dim_Date[date_id] )
)
```

> 💡 Utile pour comparer « ventes commandées » vs « ventes livrées » dans le même rapport, sans
> dupliquer la table de dates.

---

## 5. Row-Level Security (RLS) : chacun ne voit que SES données

En entreprise, un tableau de bord unique sert plusieurs personnes — mais **le responsable du
magasin de Lille ne doit pas voir les chiffres de Dunkerque**. La **RLS** filtre les données selon
l'utilisateur connecté, côté serveur : impossible à contourner.

> **Analogie** — La RLS, c'est le videur à l'entrée : tout le monde regarde le même rapport, mais
> chacun ne reçoit que les lignes qui le concernent. Le filtre est appliqué *avant* que la donnée
> n'arrive à l'écran.

### RLS statique (un rôle par périmètre)

Dans Power BI Desktop : **Modélisation → Gérer les rôles**. On crée un rôle et on écrit un filtre DAX
sur une table :

```dax
-- Rôle "Manager Lille" : filtre sur Dim_Magasin
[ville] = "Lille"
```

On teste avec **« Voir en tant que rôle »**. Problème : un rôle par ville = ingérable à 50 magasins.

### RLS dynamique (un seul rôle, piloté par une table de sécurité)

On ajoute une table `Securite` qui mappe **email → périmètre** :

| email | ville |
|---|---|
| manager.lille@nordretail.fr | Lille |
| manager.dk@nordretail.fr | Dunkerque |

Puis **un seul** rôle dynamique, qui lit l'utilisateur connecté avec `USERPRINCIPALNAME()` :

```dax
-- Rôle "Manager" (dynamique) : filtre sur Dim_Magasin
[ville] IN
CALCULATETABLE (
    VALUES ( Securite[ville] ),
    Securite[email] = USERPRINCIPALNAME ()   -- l'email de la personne connectée
)
```

Résultat : **un seul rôle** pour toute l'entreprise, et chacun voit automatiquement son périmètre.
Ajouter un magasin = ajouter une ligne dans `Securite`, aucune modification du modèle.

> 🛑 **Erreur courante** — tester la RLS uniquement dans Desktop et croire que c'est fini. La RLS ne
> s'applique réellement qu'une fois le rapport **publié** et les utilisateurs **affectés aux rôles**
> dans le Service Power BI. Les comptes *Admin/Membre* de l'espace de travail contournent la RLS.

---

## 🧪 Travaux pratiques — déboguer une mesure fausse

Ici, on ne construit pas : on **répare**. C'est la compétence qui fait la différence en entreprise.

### TP 1 — « Mon % du total affiche 100 % partout »

Un collègue a écrit cette mesure pour obtenir la part de chaque catégorie dans le CA. Dans un visuel
par catégorie, elle affiche **100 %** sur chaque ligne. Trouve et corrige le bug.

```dax
Part_categorie =
DIVIDE (
    [CA_net],
    CALCULATE ( [CA_net] )   -- censé être le total toutes catégories
)
```

<details>
<summary>💡 Corrigé</summary>

Le `CALCULATE([CA_net])` au dénominateur **ne retire aucun filtre** : dans le contexte « catégorie =
Sport », il recalcule le CA… de Sport. On divise donc Sport par Sport = 100 %. Il faut **enlever le
filtre de catégorie** au dénominateur avec `ALL` :

```dax
Part_categorie =
DIVIDE (
    [CA_net],
    CALCULATE ( [CA_net], ALL ( Dim_Produit[categorie] ) )   -- total toutes catégories
)
```

Règle : un « % du total » a **presque toujours** un `ALL(...)` (ou `ALLSELECTED`) au dénominateur.
</details>

### TP 2 — « Mon évolution N-1 est vide »

Cette mesure d'évolution annuelle renvoie `(vide)` sur toutes les années sauf, parfois, des valeurs
incohérentes. Diagnostique.

```dax
CA_N_1 = CALCULATE ( [CA_net], DATEADD ( Dim_Date[date], -1, YEAR ) )
Evolution = [CA_net] - [CA_N_1]
```

<details>
<summary>💡 Corrigé</summary>

`DATEADD` (comme toute *time intelligence*) exige une **table de dates marquée comme telle**
(*« Marquer comme table de dates »*) et une **colonne de dates continue, sans trous**. Deux causes
fréquentes :

1. `Dim_Date` n'est pas marquée comme table de dates → `DATEADD` échoue silencieusement → `(vide)`.
2. La colonne `date` a des jours manquants (elle n'est pas continue) → le décalage tombe dans le vide.

Correctifs : marquer `Dim_Date` comme table de dates, garantir une plage **continue** de dates, et
sécuriser l'affichage avec `DIVIDE`/`IF` pour ne pas afficher une évolution quand `CA_N_1` est vide.
</details>

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [RELATED & RELATEDTABLE](https://www.youtube.com/results?search_query=dax+related+relatedtable+tutorial) | SQLBI | EN | Traverser les relations proprement |
| [Itérateurs SUMX / AVERAGEX](https://www.youtube.com/results?search_query=dax+sumx+iterator+sqlbi) | SQLBI | EN | Quand et pourquoi itérer ligne à ligne |
| [Context transition expliqué](https://www.youtube.com/results?search_query=dax+context+transition+expliqu%C3%A9) | Guy in a Cube / SQLBI | EN | LE concept qui piège tout le monde |
| [Row-Level Security pas à pas](https://www.youtube.com/results?search_query=power+bi+rls+dynamique+userprincipalname+fran%C3%A7ais) | Power BI France | FR | RLS statique et dynamique |
| [USERELATIONSHIP](https://www.youtube.com/results?search_query=dax+userelationship+role+playing+dimension) | Guy in a Cube | EN | Gérer plusieurs dates (commande/livraison) |

---

## À retenir

- **`RELATED`** ramène une colonne d'une dimension liée ; **`RELATEDTABLE`** ramène ses lignes.
- Les **itérateurs `…X`** calculent **ligne à ligne** puis agrègent : indispensables dès qu'un calcul
  se fait *dans* la ligne (quantité × prix).
- **`CALCULATE` déclenche la transition de contexte** : « je suis sur cette ligne » → « filtre le
  calcul sur cette ligne ».
- **`USERELATIONSHIP`** active une relation inactive le temps d'un calcul.
- La **RLS** sécurise l'accès **côté serveur** ; la version **dynamique** (`USERPRINCIPALNAME()` +
  table de sécurité) est celle qu'on déploie en entreprise.
- Savoir **déboguer** une mesure (% du total à 100 %, N-1 vide) vaut plus qu'en écrire dix.
