# 01 — Construire un tableau de bord BI

> **Le moment où ton analyse devient un produit.** Jusqu'ici tu as extrait des données (1.1), tu les as explorées et nettoyées (1.2), tu as repéré des tendances (1.3) et tu as défini les bons KPI (1.4). Maintenant, tu **assembles tout ça dans un écran** que ton responsable de magasin pourra lire en 30 secondes, le café à la main.

| | |
|---|---|
| **Phase** | Phase 1 — Ajuster et analyser un tableau de bord métier |
| **Durée** | ≈ 30 h (≈ 4 jours) |
| **Objectifs** | Réaliser des représentations visuelles · Construire un tableau de bord |
| **Pré-requis** | Modules **1.1** (SQL) · **1.2** (pandas/EDA) · **1.3** (tendances) · **1.4** (KPI & arborescence du dashboard) |
| **Outils** | **Power BI Desktop** (Windows / VM / Service web) + **Looker Studio** (navigateur, tout OS) |

---

## Objectifs pédagogiques

À la fin de ce module, tu sauras :

1. **Importer des données** dans un outil BI (fichier CSV/Excel) et comprendre le rôle d'un **modèle de données**.
2. **Nettoyer légèrement** une source avec **Power Query** (types de colonnes, suppression de lignes vides, renommage) — l'équivalent GUI de ce que tu faisais en pandas.
3. **Créer les visuels de base** : cartes KPI, graphiques à barres, courbes d'évolution, tableaux.
4. **Ajouter de l'interactivité** : segments (slicers), contrôles de filtre, filtres de page.
5. **Mettre en page** un dashboard lisible (titre, alignement, couleurs cohérentes).
6. **Publier et partager** : Power BI Service / lien Looker Studio.
7. **Choisir le bon type de graphique** selon le message (rappel du chapitre dataviz).
8. Réaliser **le même dashboard dans deux outils** et comprendre quand utiliser l'un ou l'autre.

---

## Pourquoi c'est utile au Data Analyst (cœur du métier)

Le cœur du métier, c'est *« analyser des données et en restituer les résultats »*. La **restitution**, c'est exactement ce module. Un Data Analyst peut produire l'analyse la plus juste du monde : si personne ne la comprend, elle ne sert à rien.

Concrètement, dans ton futur poste :

- Le **directeur régional** d'une enseigne ne va jamais ouvrir ton notebook Python. Il veut **un écran**, avec **3 chiffres clés** et **2 graphiques**, qu'il peut filtrer par magasin et par mois.
- L'outil BI est ce qui transforme un `df.groupby(...)` en **objet de décision**. C'est le livrable qui « sort » du service data et arrive sur le bureau d'un métier.
- Maîtriser **deux outils** (un payant standard du marché, Power BI ; un gratuit cross-OS, Looker Studio) te rend employable partout : la plupart des offres Data Analyst exigent « Power BI **ou** Looker/Tableau ».

> 🧭 **Image à retenir.** Ton analyse Python, c'est la cuisine. Le dashboard BI, c'est **l'assiette dressée** qu'on apporte au client. Même plat, mais c'est l'assiette qui décide si on a envie d'y goûter.

**Fil rouge du module — Retail Nord.** On reprend le jeu de ventes d'une enseigne de magasins dans les Hauts-de-France (Lille, Roubaix, Valenciennes, Dunkerque…). Colonnes typiques : `date_vente`, `magasin`, `categorie_produit`, `produit`, `quantite`, `prix_unitaire`, `montant`, `client_id`. On construira le même tableau de bord « Suivi des ventes Retail Nord » dans Power BI puis dans Looker Studio.

---

# PARTIE A — Power BI Desktop pas à pas 🟡

## A.0 ⚠️ Contrainte Mac — à lire AVANT de commencer

**Power BI Desktop n'existe PAS sur macOS ni sur Linux.** Microsoft ne fournit qu'une version **Windows**. Si tu es sur Mac (ou Linux), tu as **trois options** :

| Option | Comment | Pour qui |
|---|---|---|
| **A. Power BI Service (web)** | Va sur [app.powerbi.com](https://app.powerbi.com), connecte-toi avec un compte Microsoft, tu peux **importer un fichier et créer des rapports directement dans le navigateur**. Fonctionnel mais Power Query y est plus limité. | Mac/Linux sans VM, usage simple |
| **B. Machine virtuelle Windows** | Windows dans **Parallels / UTM / VMware** (Mac Intel ou Apple Silicon avec Windows ARM), puis on installe Power BI Desktop dedans. | Mac qui veut l'expérience complète |
| **C. Faire le TP en Looker Studio** | Looker Studio (Partie B) tourne dans **n'importe quel navigateur**. C'est le **plan par défaut** de ce module : **le TP noté se fait en Looker Studio**, Power BI est une variante. | Tout le monde — accessible à 100 % de la classe |

> 💡 **Décision pédagogique du module.** Le **TP principal est en Looker Studio** (accessible à tous, gratuit, sans installation). La Partie A Power BI est essentielle à **connaître** (c'est l'outil le plus demandé en entreprise), tu la suis en démonstration et la refais si tu es sur Windows ou en VM. **Personne n'est bloqué.**

---

## A.1 Découvrir l'interface

Quand tu ouvres **Power BI Desktop** (Windows), repère les zones :

- **Le ruban** (en haut) : onglets *Accueil, Insertion, Modélisation, Affichage*.
- **Le canevas** (au centre) : la page blanche où tu déposes tes visuels.
- **Le volet `Visualisations`** (à droite) : la galerie d'icônes de graphiques + les « puits de champs » (Axe, Valeurs, Légende…).
- **Le volet `Données`** (tout à droite) : la liste de tes tables et colonnes après import.
- **Les 3 vues** (icônes à gauche) : *Rapport* (📊 les visuels), *Données* (le tableau brut), *Modèle* (les relations entre tables).

## A.2 Importer les données

1. Onglet **Accueil** → bouton **`Obtenir les données`**.
2. Choisis la source : **`Texte/CSV`** (pour `ventes_retail_nord.csv`) ou **`Classeur Excel`**.
3. Sélectionne le fichier → une fenêtre d'**aperçu** s'ouvre.
4. Ne clique PAS encore sur *Charger*. Clique sur **`Transformer les données`** → ça ouvre **Power Query**.

> 📌 *Charger* met les données telles quelles dans le rapport. *Transformer les données* ouvre l'éditeur de nettoyage. **Prends toujours l'habitude de passer par Transformer**, même pour vérifier.

## A.3 Aperçu de Power Query — le nettoyage simple

Power Query, c'est **le pandas en mode boutons**. Chaque action que tu fais est enregistrée comme une **étape** (volet *Étapes appliquées*, à droite). Si tu te trompes, tu supprimes l'étape. Et surtout : **ça se rejoue automatiquement** à chaque rafraîchissement des données.

Manipulations de base à connaître :

| Besoin | Manipulation Power Query |
|---|---|
| **Vérifier/corriger un type** | Clic sur l'icône à gauche du nom de colonne (ABC = texte, 123 = nombre, 📅 = date) → choisir le bon type. Mets `montant` et `prix_unitaire` en **Nombre décimal**, `date_vente` en **Date**. |
| **Supprimer les lignes vides** | Onglet *Accueil* → *Supprimer les lignes* → *Supprimer les lignes vides*. |
| **Renommer une colonne** | Double-clic sur l'en-tête → tape le nouveau nom (`montant` → `Chiffre d'affaires`). |
| **Filtrer des valeurs** | Flèche ▼ à droite de l'en-tête → décocher les valeurs à exclure (ex. retirer un magasin de test). |
| **Première ligne = en-têtes** | *Accueil* → *Utiliser la première ligne comme en-tête* (si le CSV est décalé). |
| **Supprimer une colonne inutile** | Clic droit sur l'en-tête → *Supprimer*. |

Quand c'est propre : **Accueil → `Fermer et appliquer`**. Tu reviens au rapport, les données sont chargées.

> 📎 **Lien avec le module 1.2.** Power Query ne remplace PAS pandas — il fait le **nettoyage léger** (types, doublons, colonnes). Le nettoyage lourd (logique métier complexe, imputation) reste souvent en Python en amont. En entreprise, on enchaîne souvent : **SQL/Python pour préparer → BI pour restituer**.

## A.4 Créer les visuels

### a) Une carte KPI (le chiffre clé)

1. Dans le volet *Visualisations*, clique sur l'icône **`Carte`** (un seul grand chiffre).
2. Depuis le volet *Données*, **glisse `Chiffre d'affaires`** dans le puits **`Champs`**.
3. Power BI affiche la **somme** → ton CA total. Renomme-le via le volet *Format* → *Étiquette de catégorie*.
4. Duplique pour créer d'autres cartes : **Nombre de ventes** (glisse `produit` en *Champs* puis change l'agrégat en *Nombre*), **Panier moyen** (`Chiffre d'affaires` → agrégat *Moyenne*).

### b) Un graphique à barres (comparer des catégories)

1. Clique sur **`Histogramme groupé`** (barres verticales) ou **`Graphique à barres groupées`** (horizontales).
2. **Axe Y / Axe** → glisse `magasin`.
3. **Valeurs** → glisse `Chiffre d'affaires`.
4. Tu obtiens le CA par magasin. Trie : `…` (en haut à droite du visuel) → *Trier l'axe* → par CA décroissant.

### c) Une courbe (évolution dans le temps)

1. Clique sur **`Graphique en courbes`**.
2. **Axe** → glisse `date_vente` (Power BI propose une **hiérarchie de date** Année/Trimestre/Mois/Jour — clique sur *Mois* pour agréger par mois).
3. **Valeurs** → `Chiffre d'affaires`.
4. Tu vois l'évolution mensuelle du CA — exactement le module 1.3 (tendances) rendu visuel.

### d) Un tableau (le détail)

1. Clique sur **`Tableau`**.
2. Glisse plusieurs colonnes dans **Colonnes** : `categorie_produit`, `produit`, `Chiffre d'affaires`, `quantite`.
3. Le tableau s'agrège tout seul. Active le tri en cliquant sur un en-tête.

## A.5 Ajouter des segments / filtres (l'interactivité)

- **Segment (slicer)** : clique sur l'icône **`Segment`**, puis glisse `magasin` dedans → une liste de cases à cocher apparaît sur le canevas. Quand l'utilisateur coche « Lille », **tous les visuels de la page se filtrent**.
- Ajoute un segment **`date_vente`** → il devient un sélecteur de période (curseur de dates).
- **Volet Filtres** (à droite) : tu peux poser des filtres au niveau d'**un visuel**, d'**une page** ou de **tout le rapport** en glissant un champ dans la bonne zone.
- **Interactivité croisée** : clique sur une barre du graphique « CA par magasin » → les autres visuels se filtrent automatiquement sur ce magasin. C'est gratuit, c'est natif.

## A.6 Mettre en page

- **Titre** : onglet *Insertion* → *Zone de texte* → « Suivi des ventes — Retail Nord ».
- **Disposition** : KPI en haut (alignés), graphiques au milieu, tableau en bas. Utilise *Affichage → Quadrillage* + *Aligner* pour un rendu propre.
- **Couleurs** : *Affichage → Thèmes* → choisis un thème sobre. **Une couleur d'accent maximum** pour les chiffres importants.
- **Cohérence** : même police, mêmes formats de nombre (€, séparateur de milliers via *Format des données*).

## A.7 Publier sur Power BI Service

1. Onglet **Accueil** → **`Publier`** (nécessite un compte Power BI / Microsoft 365).
2. Choisis un **espace de travail** (workspace) de destination.
3. Une fois publié, va sur [app.powerbi.com](https://app.powerbi.com) → ton rapport y est, **interactif dans le navigateur**.
4. **Partage** : bouton *Partager* (souvent limité aux comptes pro/licence Pro) ou *Publier sur le web* (lien public — ⚠️ attention aux données sensibles, à ne jamais utiliser avec de vraies données client).

> 🔒 **Sécurité / RGPD.** « Publier sur le web » rend le rapport **public, indexable par Google**. Ne l'utilise **jamais** avec des données réelles d'entreprise ou personnelles. Pour ce module : données fictives Retail Nord uniquement.

---

### 🚨 Encadré — Erreurs courantes Power BI

- **« Mes montants s'affichent en texte / ne s'additionnent pas »** → le type de colonne est resté *Texte* dans Power Query. Repasse-la en *Nombre décimal*.
- **« Mon graphique affiche un nombre énorme et bizarre »** → tu as laissé l'agrégat *Somme* sur un identifiant (`client_id`). Change l'agrégat en *Nombre (distinct)* ou retire le champ.
- **« Mes dates ne se trient pas dans l'ordre »** → la colonne est en *Texte*, pas en *Date*. Corrige le type ; sinon « avril » vient avant « janvier » (ordre alphabétique).
- **« J'ai 4 fois le même magasin »** → espaces ou casse différents (« Lille » / « lille  »). Nettoie dans Power Query (*Transformer → Format → Supprimer les espaces / Mettre en majuscules*).
- **« Le bouton Publier est grisé »** → tu n'es pas connecté à un compte Power BI. Connecte-toi (en haut à droite).

---

# PARTIE B — Looker Studio pas à pas 🟢 (cross-OS, le TP officiel)

**Looker Studio** (ex-Google Data Studio) est **gratuit**, tourne dans **n'importe quel navigateur**, sur **n'importe quel OS**. Il te faut juste un **compte Google**. C'est l'outil sur lequel **tout le monde** fait le TP noté.

## B.0 Préparer la source

Looker Studio se connecte le plus simplement à un **Google Sheet**. Donc :

1. Ouvre **Google Sheets** → *Fichier → Importer* → dépose `ventes_retail_nord.csv`.
2. Vérifie que la **première ligne** contient les en-têtes et que `date_vente` est bien reconnue comme date (Format → Nombre → Date) et `montant` comme nombre.
3. Note le nom du fichier Sheet.

## B.1 Créer le rapport et connecter la source

1. Va sur [lookerstudio.google.com](https://lookerstudio.google.com).
2. Clique **`Créer`** → **`Rapport`** (ou pars d'un *Rapport vierge*).
3. Le sélecteur de **connecteur** s'ouvre → choisis **`Google Sheets`** → sélectionne ton fichier et l'onglet.
4. Clique **`Ajouter`** → confirme *Ajouter au rapport*.
5. Looker Studio devine les types de chaque champ : à gauche les **dimensions** (texte, en bleu : `magasin`, `categorie_produit`), à droite les **statistiques/mesures** (chiffres, en vert : `montant`, `quantite`).

> 📌 **Dimension vs mesure** = la distinction fondamentale du module 1.4. **Dimension** = ce par quoi on découpe (magasin, mois, catégorie). **Mesure** = ce qu'on calcule (CA, quantité). Si un champ est mal classé, clique dessus dans le volet *Données* (à droite) et change son type/agrégation.

## B.2 Créer les graphiques

### a) Les cartes KPI (« Graphique à statistiques » / Scorecard)

1. Barre du haut → **`Ajouter un graphique`** → choisis **`Graphique à statistiques`** (la grande vignette à un chiffre).
2. Clique-dépose-le sur la page.
3. Dans le volet *Configuration* (à droite) → **Statistique** = `montant`, **Agrégation** = *Somme* → c'est ton **CA total**.
4. Duplique (Ctrl/Cmd+C, Ctrl/Cmd+V) pour : **Quantité totale** (`quantite`, Somme), **Panier moyen** (`montant`, Moyenne), **Nb de transactions** (`montant`, Nombre).

### b) Le graphique à barres (CA par magasin)

1. *Ajouter un graphique* → **`Graphique à barres`**.
2. *Configuration* → **Dimension** = `magasin`, **Statistique** = `montant` (Somme).
3. *Tri* → par `montant` décroissant. Limite à 10 si besoin.

### c) La courbe (évolution mensuelle)

1. *Ajouter un graphique* → **`Graphique en courbes`** (série temporelle).
2. **Dimension de période** = `date_vente`. Clique dessus → règle la granularité sur **Mois**.
3. **Statistique** = `montant` (Somme).

### d) Le tableau de détail

1. *Ajouter un graphique* → **`Tableau`**.
2. **Dimensions** = `categorie_produit`, `produit`. **Statistiques** = `montant`, `quantite`.
3. Active les **barres de données** (onglet *Style*) pour un mini-bar-chart dans le tableau.

## B.3 Ajouter des contrôles de filtre

1. Barre du haut → **`Ajouter une commande`** (ou *Ajouter un contrôle*).
2. Choisis **`Liste déroulante`** → glisse-la sur la page → **Champ de contrôle** = `magasin`. L'utilisateur pourra filtrer tout le rapport par magasin.
3. Ajoute une **`Plage de dates`** (date range control) → elle se câble automatiquement sur `date_vente`.
4. Optionnel : un **`Curseur`** sur `montant` pour ne voir que les grosses ventes.

> 📌 Comme dans Power BI, **cliquer sur une barre** filtre les autres visuels (« interactions entre graphiques » — à activer dans *Configuration → Filtrage croisé* du graphique).

## B.4 Mettre en page

- **Titre** : *Ajouter un texte* → « Suivi des ventes — Retail Nord ».
- **Thème** : volet *Thème et mise en page* (en haut à droite) → choisis un thème, ou *Extraire le thème d'une image* (logo).
- Aligne les KPI en haut, place les contrôles juste en dessous du titre. Utilise les **repères d'alignement** (lignes roses) qui apparaissent au déplacement.
- Ajoute le **logo** / une bande de couleur d'en-tête pour l'identité.

## B.5 Partager

1. Bouton **`Partager`** (en haut à droite).
2. Options : inviter des personnes par e-mail (*Lecteur* / *Éditeur*), ou **`Obtenir le lien`** → règle l'accès (*Toute personne disposant du lien*).
3. **`Planifier l'envoi par e-mail`** : Looker Studio peut envoyer le rapport en PDF automatiquement (utile pour un reporting hebdo).
4. Pour figer une version : *Fichier → Télécharger en PDF*.

> 💡 **Différence clé avec Power BI.** Le partage Looker Studio est **gratuit et immédiat** (un lien suffit). Power BI demande souvent une **licence Pro** pour partager à d'autres. C'est l'argument n°1 de Looker Studio en petite structure.

---

### 🚨 Encadré — Erreurs courantes Looker Studio

- **« Mes ventes apparaissent comme du texte »** → dans le Google Sheet, la colonne `montant` contient des virgules françaises ou un symbole €. Mets-la en *Format → Nombre* propre côté Sheet, ou change le type côté Looker Studio.
- **« Mon graphique affiche "Aucune donnée" »** → la source n'est pas rafraîchie. Clique sur *Actualiser les données* (icône en haut), ou vérifie que la plage du Sheet inclut bien toutes les lignes.
- **« Je vois la somme des `client_id` »** → un identifiant n'est pas une mesure à sommer. Mets-le en dimension ou compte les valeurs distinctes (`Nombre distinct`).
- **« Ma plage de dates ne marche pas »** → le champ `date_vente` est typé *Texte*. Change-le en *Date* dans le volet Données.
- **« Le rapport est vide pour mes collègues »** → tu as partagé le **rapport** mais pas donné accès au **Google Sheet** source. Partage aussi la source (ou utilise un accès propriétaire).

---

## Choisir le bon visuel (rappel dataviz) 🎯

Tu connais déjà les graphiques (chapitre dataviz du module maths). Voici la **table de décision** spéciale BI :

| Ton message / ta question | Le bon visuel | À éviter |
|---|---|---|
| **Un seul chiffre clé** (CA total, panier moyen) | **Carte KPI / Scorecard** | Un graphique pour un seul chiffre |
| **Comparer des catégories** (CA par magasin) | **Barres** (horizontales si noms longs) | Camembert avec 8 parts |
| **Évolution dans le temps** | **Courbe** (ou aires) | Barres si beaucoup de points |
| **Part d'un tout** (≤ 5 catégories) | **Camembert / Anneau**, avec parcimonie | Camembert > 5 parts |
| **Relation entre 2 mesures** | **Nuage de points** | — |
| **Beaucoup de détail chiffré** | **Tableau** (avec barres de données) | Graphique illisible |
| **Composition + total dans le temps** | **Barres empilées** | — |
| **Localisation géographique** | **Carte** (par ville/région) | Tableau de coordonnées |

> ⚠️ **Les 4 règles d'or du dashboard.** (1) **Un visuel = un message.** (2) **Le plus important en haut à gauche** (sens de lecture). (3) **Pas plus de 5–7 visuels par page** sinon surcharge. (4) **Toujours un titre qui dit la conclusion**, pas juste « CA par magasin » mais « Lille concentre 38 % du CA ».

---

## Travaux pratiques 🛠️

> **Données** : `ventes_retail_nord.csv` (colonnes : `date_vente`, `magasin`, `categorie_produit`, `produit`, `quantite`, `prix_unitaire`, `montant`, `client_id`). Si le fichier n'est pas fourni, ton formateur te donne un Google Sheet partagé.
> **Outil principal : Looker Studio** (tout le monde). **Variante Power BI** pour ceux qui sont sur Windows/VM.

### TP 1 — Connecter la source et créer les 4 KPI *(45 min)*

Importe le CSV dans Google Sheets, connecte-le à Looker Studio, et crée **4 cartes KPI** : CA total, Quantité totale vendue, Panier moyen, Nombre de transactions.

<details>
<summary>✅ Attendu / corrigé</summary>

- Sheet importé, `date_vente` en Date, `montant` en Nombre.
- Rapport Looker Studio connecté au Sheet (connecteur Google Sheets).
- 4 Graphiques à statistiques :
  - **CA total** = `montant` / agrégation **Somme**.
  - **Quantité totale** = `quantite` / **Somme**.
  - **Panier moyen** = `montant` / **Moyenne** (format € 2 décimales).
  - **Nb transactions** = `montant` (ou `client_id`) / **Nombre** (pas Somme !).
- Erreur typique attrapée : agrégat *Somme* laissé sur `client_id` → corrigé en *Nombre*.
</details>

### TP 2 — Les 3 graphiques + interactivité *(1 h)*

Ajoute : un **barres CA par magasin** (trié décroissant), une **courbe d'évolution mensuelle du CA**, un **tableau** détaillant CA et quantité par catégorie de produit. Puis ajoute une **liste déroulante `magasin`** et une **plage de dates**.

<details>
<summary>✅ Attendu / corrigé</summary>

- **Barres** : dimension `magasin`, mesure `montant` (Somme), tri décroissant. Lille/Roubaix probablement en tête.
- **Courbe** : dimension de période `date_vente` en granularité **Mois**, mesure `montant`. On lit la saisonnalité (pic décembre attendu en retail).
- **Tableau** : dimension `categorie_produit`, mesures `montant` + `quantite`, barres de données activées.
- **Contrôles** : liste déroulante `magasin` + plage de dates `date_vente`. Test : sélectionner « Lille » → les 3 visuels + les KPI se mettent à jour.
- Vérifié : cliquer sur une barre filtre bien le reste (filtrage croisé).
</details>

### TP 3 — Mise en page, partage et titre « conclusion » *(45 min)*

Mets en page proprement (titre, KPI alignés en haut, contrôles sous le titre, graphiques au milieu, tableau en bas), applique un thème, puis **partage par lien** en lecture seule. **Renomme** au moins un graphique avec un titre qui dit la conclusion.

<details>
<summary>✅ Attendu / corrigé</summary>

- Titre « Suivi des ventes — Retail Nord ».
- KPI alignés en haut, contrôles visibles, hiérarchie de lecture respectée (important en haut à gauche).
- Thème cohérent, une seule couleur d'accent.
- Titre-conclusion, ex. « Lille génère 38 % du CA régional » au lieu de « CA par magasin ».
- Lien de partage généré (*Toute personne disposant du lien · Lecteur*). Le Sheet source est accessible (sinon rapport vide pour les autres).
- Export PDF réalisé.
</details>

### TP 4 (variante avancée / Windows) — Refaire le dashboard dans Power BI *(1 h 30)*

Sur Windows ou en VM : importe le CSV, **nettoie dans Power Query** (types, espaces sur `magasin`, colonne inutile retirée), recrée les **4 KPI + 3 graphiques + segments**, mets en page, et **publie sur Power BI Service**. Compare l'expérience aux deux outils.

<details>
<summary>✅ Attendu / corrigé</summary>

- Import via *Obtenir les données → Texte/CSV → Transformer les données*.
- Power Query : `montant`/`prix_unitaire` en Nombre décimal, `date_vente` en Date, *Supprimer les espaces* sur `magasin`, lignes vides supprimées, colonne inutile retirée. Étapes appliquées visibles.
- Cartes (Somme/Moyenne/Nombre), histogramme groupé CA/magasin, courbe par hiérarchie de date (niveau Mois), tableau.
- Segments `magasin` + `date_vente`, interactions croisées testées.
- *Publier* → espace de travail → rapport visible sur app.powerbi.com.
- **Comparaison attendue (réflexion)** : Power BI = plus puissant (Power Query, DAX, modèle relationnel) mais Windows + licence Pro pour partager ; Looker Studio = gratuit, cross-OS, partage par lien immédiat, moins puissant sur la transfo. Pas de « meilleur » dans l'absolu : ça dépend du contexte.
</details>

---

## Vidéos d'auto-formation 🎥

> Liens vérifiés issus d'une recherche web. Quand un lien direct est incertain, on donne une **recherche YouTube** que tu lances toi-même (jamais d'URL inventée).

| Titre | Chaîne | Langue | Durée approx. | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Looker Studio : Créer un tableau de bord étape par étape (ex Data Studio) | (FR) | FR | ~30 min | https://www.youtube.com/watch?v=BVBvo9eKK40 | Connexion source, premiers graphiques, filtres — le cœur du TP en français |
| Tuto Looker Studio, les bases de création de rapports | (FR) | FR | ~25 min | https://www.youtube.com/watch?v=L1YrBhnIS-0 | Bases d'un rapport Looker Studio : dimensions/mesures, mise en page |
| Power BI : créer un tableau de bord | (FR) | FR | ~15–20 min | https://www.youtube.com/watch?v=6O01So6hypo | Premier dashboard Power BI en français, visuels et filtres |
| ULTIMATE Power BI Tutorial — Beginner to Pro (2024) | (EN) | EN | ~2–3 h | https://www.youtube.com/watch?v=Dk25lwdTKow | Cours complet : import, Power Query, visuels, publication |
| Power BI Tutorial For Beginners — Create Your First Dashboard | (EN) | EN | ~1 h | https://www.youtube.com/watch?v=c7LrqSxjJQQ | Premier dashboard pas à pas, fichiers d'exercice fournis |
| Learn Looker Studio — Beginner Course (MeasureSchool) | MeasureSchool (EN) | EN | ~46 min | https://www.youtube.com/watch?v=-FWszJyX8JM | Connexions, visuels, filtres, thèmes — version anglaise concise |

> 🔎 Si un lien est cassé, lance ces recherches : [« Power BI tableau de bord débutant français »](https://www.youtube.com/results?search_query=power+bi+tableau+de+bord+débutant+français) · [« Looker Studio tutoriel français débutant »](https://www.youtube.com/results?search_query=looker+studio+tutoriel+français+débutant) · ressource officielle : [Microsoft Learn — Prise en main du service Power BI](https://learn.microsoft.com/fr-fr/power-bi/fundamentals/service-get-started) · [Google — Tutoriel : créer un rapport Looker Studio](https://docs.cloud.google.com/looker/docs/studio/tutorial-create-a-new-report?hl=fr).

---

## Quiz — 5 QCM ✍️

**Q1.** Tu es sur un Mac. Quelle affirmation est vraie ?
- A) Power BI Desktop s'installe normalement sur macOS
- B) Power BI Desktop n'existe que sur Windows ; sur Mac on utilise le Service web, une VM, ou Looker Studio
- C) Looker Studio ne marche que sur Windows
- D) Aucun outil BI ne fonctionne sur Mac

**Q2.** Dans Power BI, à quoi sert **Power Query** ?
- A) À publier le rapport sur le web
- B) À écrire des formules DAX
- C) À nettoyer/transformer les données avant chargement (types, lignes vides, renommage)
- D) À choisir les couleurs du thème

**Q3.** Tu veux montrer **l'évolution du chiffre d'affaires mois par mois**. Quel visuel ?
- A) Camembert
- B) Tableau
- C) Courbe (série temporelle)
- D) Carte KPI

**Q4.** Dans Looker Studio, ton KPI « Nombre de transactions » affiche un chiffre énorme et faux. Cause la plus probable ?
- A) Le thème est mal réglé
- B) Tu as mis l'agrégation *Somme* au lieu de *Nombre*
- C) La source n'est pas partagée
- D) Le titre est trop long

**Q5.** Quel est l'avantage principal de Looker Studio par rapport à Power BI pour ce module ?
- A) Il est plus puissant pour la modélisation
- B) Il propose le langage DAX
- C) Il est gratuit, tourne dans le navigateur sur tout OS, et le partage par lien est immédiat
- D) Il fonctionne hors ligne

<details>
<summary>✅ Réponses</summary>

**Q1 → B.** Power BI Desktop = Windows uniquement. Mac : Service web / VM / Looker Studio.
**Q2 → C.** Power Query = nettoyage et transformation (l'équivalent GUI de pandas).
**Q3 → C.** Une évolution temporelle se montre avec une courbe.
**Q4 → B.** Un comptage de transactions se fait avec *Nombre*, pas *Somme*.
**Q5 → C.** Gratuit, cross-OS, partage par lien immédiat — d'où le choix comme TP principal.
</details>

---

## À retenir 🧠

- **Restituer fait partie du métier** : le dashboard est le livrable qui rend ton analyse utile à un décideur.
- **Deux outils, une logique commune** : importer une source → (nettoyer) → poser des **dimensions** et des **mesures** → choisir les bons visuels → ajouter des **filtres** → mettre en page → partager.
- **Power BI** : standard du marché, puissant (Power Query, DAX, modèle), mais **Windows uniquement** + licence Pro pour partager. Sur Mac : **Service web / VM**.
- **Looker Studio** : gratuit, **cross-OS**, partage par lien immédiat → c'est l'**outil du TP noté**, personne n'est bloqué.
- **Le bon graphique** dépend du message : carte pour un chiffre, barres pour comparer, courbe pour le temps, tableau pour le détail.
- **Pièges récurrents** : types de colonnes (texte vs nombre/date), sommer un identifiant, partager le rapport sans la source, surcharger la page.
- **Un dashboard réussi** se lit en 30 secondes : titre-conclusion, l'essentiel en haut à gauche, 5–7 visuels max, une couleur d'accent.
