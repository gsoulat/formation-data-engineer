# Brief S12 — Doter le modèle NordRetail d'indicateurs fiables avec DAX

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S12 — Phase 2 : Une solution BI pour l'analyse avancée |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Power BI Desktop, langage DAX, modèle en étoile, Git/GitHub · pandas ou Excel (validation croisée) |
| **Prérequis** | [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/) · [DAX & mesures avancées](../../../15-Business-Intelligence/10-DAX/) · [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'équipe data, encore naissante, a franchi plusieurs étapes ces dernières semaines : les données de ventes ont été auditées, un modèle en étoile propre a été assemblé la semaine passée (table de faits `Faits_Ventes` reliée à ses dimensions `Dim_Date`, `Dim_Magasin`, `Dim_Produit`, `Dim_Client`). Le tableau de bord de pilotage prend forme, brique après brique.

### Le problème

Le modèle est en place, mais il ne **calcule** rien de lui-même. Glisser le champ `montant` dans un visuel donne une somme brute, et rien de plus. Or la direction commerciale ne veut pas des additions : elle veut des **indicateurs de pilotage** — chiffre d'affaires, marge, panier moyen, évolution par rapport à l'année précédente — qui donnent **toujours le même résultat** d'une réunion à l'autre, et qui **réagissent** quand on filtre sur une ville, un mois ou une catégorie.

Aujourd'hui, ces chiffres circulent dans des colonnes Excel recopiées à la main : une source d'erreurs, de versions divergentes et de temps perdu. La contrôleuse de gestion a déjà relevé deux réunions où le « CA du mois » ne concordait pas d'un fichier à l'autre. Il faut faire vivre ces calculs **dans le modèle**, une bonne fois, sous forme de mesures réutilisables et documentées.

### La question centrale

Toute la semaine, chaque mesure que vous construisez doit contribuer à répondre à la demande que la direction vous a adressée :

> **« Peut-on obtenir des indicateurs de pilotage fiables, cohérents et comparables dans le temps, directement depuis le modèle NordRetail ? »**

### Les données

Vous repartez du **modèle en étoile** assemblé la semaine dernière. Les fichiers sources vivent dans le dépôt :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — table de faits. Colonnes : `vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`.
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — dimension temps. Colonnes : `date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour`, `jour_semaine`, `est_weekend`.
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — dimension point de vente (`magasin_id`, `ville`, `type`, `surface_m2`, `date_ouverture`).
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — dimension produit (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Client.csv`](../data/Dim_Client.csv) — dimension client (`client_id`, `prenom`, `nom`, `ville`, `segment`, `date_inscription`, `email`).

Les données couvrent **2023 et 2024** : la comparaison à l'année précédente (N-1) est donc possible. En appui, [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) fournit les objectifs de CA mensuels par magasin (`magasin_id`, `annee`, `mois`, `objectif_ca`) pour ceux qui veulent aller plus loin.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Distinguer une mesure d'une colonne calculée** et choisir la bonne au bon moment, en comprenant le rôle du **contexte de filtre**.
- **Écrire des mesures DAX d'agrégation** (`SUM`, `DISTINCTCOUNT`) et des ratios métier (marge %, panier moyen) formatés pour la lecture directe.
- **Construire une mesure d'évolution temporelle** (N-1 / YoY) à l'aide de la *time intelligence* (`CALCULATE`, `SAMEPERIODLASTYEAR`) en vous appuyant sur la table de dates.
- **Valider un indicateur** par recoupement avec un calcul indépendant (pandas ou Excel) sur un sous-ensemble connu.
- **Documenter un jeu de mesures** dans un tableau de référence lisible par un décideur (nom, formule, format, résultat vérifié).

## Données fournies

Le modèle en étoile et ses fichiers sources sont déjà dans le dépôt, dans [`99-Brief/Data-Analyst/data/`](../data/). Aucune donnée n'est à télécharger. Vous travaillez à partir du fichier `.pbix` produit la semaine dernière (ou vous rechargez les CSV et rétablissez les relations si besoin). On ne modifie jamais les fichiers sources : vos calculs vivent dans les **mesures**, pas dans les CSV.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre fichier `.pbix` et sa propre documentation de mesures. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et lecture métier, SANS écrire de DAX (J1)

Avant de taper la moindre formule, appropriez-vous le besoin. Reprenez la demande de la direction et traduisez-la en une **liste d'indicateurs** attendus : que veut dire exactement « CA », « marge », « panier moyen » pour cette enseigne ? Le panier moyen se calcule-t-il par ligne de vente, par ticket, par client ? Une évolution « par rapport à l'an dernier » compare-t-elle mois à mois, ou année entière à année entière ? Écrivez pour chaque indicateur une **définition en une phrase** et le **résultat qu'un décideur attend** (un ordre de grandeur, une unité, un format d'affichage). Vérifiez que votre modèle de la semaine passée est sain : la relation `Faits_Ventes[date_id]` → `Dim_Date` est-elle active ? La table de dates est-elle bien marquée comme telle ? Sans ce socle, aucune *time intelligence* ne fonctionnera. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Mesures de base : CA, marge, quantités (J1-J2)

Créez une **table de mesures dédiée** (une table vide qui héberge tous vos calculs, pour ne pas les noyer dans les colonnes des faits). Construisez d'abord les mesures d'agrégation simples : **CA total** (`SUM` du `montant`), **Marge totale** (`SUM` de la `marge`), **Quantité vendue** (`SUM` de la `quantite`), **Nombre de ventes** (`DISTINCTCOUNT` de `vente_id`). Nommez-les clairement et sans ambiguïté. Interrogez-vous : pourquoi une *mesure* plutôt qu'une *colonne calculée* pour ces agrégats ? Que se passe-t-il quand l'utilisateur filtrera sur une ville — la mesure doit-elle suivre le filtre ?

### Phase 3 — Ratios métier et évolution temporelle (J2-J3)

Passez aux calculs qui font la valeur d'un tableau de bord. Dérivez le **Taux de marge %** (Marge totale ÷ CA total, formaté en pourcentage) et le **Panier moyen** (CA total ÷ Nombre de ventes, formaté en euros). Attention aux divisions par zéro : comment votre mesure se comporte-t-elle quand un filtre ne renvoie aucune vente ? Construisez ensuite l'indicateur le plus attendu par la direction : le **CA N-1** (le CA de la même période l'année précédente, via `CALCULATE` + `SAMEPERIODLASTYEAR` sur `Dim_Date[date]`) puis l'**Évolution CA YoY %** ((CA − CA N-1) ÷ CA N-1). Testez-la : sur 2024, retrouvez-vous une progression cohérente par rapport à 2023 ? Sur 2023, le N-1 est-il vide (pas d'année antérieure) et cela vous paraît-il correct ?

### Phase 4 — Formatage, mise à l'épreuve et validation croisée (J3-J4)

Un indicateur mal formaté est un indicateur qui ment. Soignez le **formatage** de chaque mesure : euros avec séparateur de milliers pour les montants, pourcentage à une décimale pour les taux. Construisez ensuite une **matrice de validation** qui croise vos mesures (CA, marge %, panier moyen, YoY %) par `ville` et par `annee` : vérifiez que chaque chiffre change bien quand vous filtrez, et qu'un total se recompose logiquement. Enfin, **recoupez** au moins deux mesures (le CA total et le taux de marge) avec un calcul **indépendant** — un `groupby` pandas ou un tableau croisé Excel — sur un sous-ensemble maîtrisé (par exemple Roubaix, janvier 2024). Les deux résultats concordent-ils au centime près ? Si non, où est l'écart, et vient-il du modèle, d'un filtre implicite, ou de votre calcul de contrôle ?

### Phase 5 — Documentation, capture et mise en ligne (J5)

Rédigez un **catalogue de mesures** (une page) : pour chaque mesure, son nom, sa formule DAX, son format, et le résultat vérifié lors de la validation croisée. Ajoutez une **capture de la matrice de validation** qui montre les indicateurs réagissant aux filtres. Rédigez enfin une courte **note de fiabilité** (8 à 15 lignes) qui répond frontalement à la question centrale : oui/non, sous quelles réserves, les indicateurs du modèle sont-ils fiables et comparables dans le temps ? Cette note s'adresse à la direction : pas de jargon DAX, des phrases actionnables. Soignez le README et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : au moins **6 mesures DAX** nommées et formatées (dont **une mesure d'évolution N-1 / YoY** fonctionnelle), matrice de validation, recoupement croisé documenté, catalogue de mesures, note de fiabilité, dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez une mesure **YTD** (cumul annuel à date) avec `TOTALYTD` et comparez-la au CA N-1.
- Croisez vos mesures avec [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) : créez un **taux d'atteinte de l'objectif** (CA réel ÷ objectif de CA) par magasin et par mois.
- Rendez vos mesures robustes avec des **variables** (`VAR` / `RETURN`) et gérez explicitement le cas « aucune donnée » avec `DIVIDE`.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le fichier **`.pbix`** enrichi de la table de mesures (ou un export documenté si le `.pbix` est trop volumineux : formules DAX + captures) ;
  - un **catalogue de mesures** (`MESURES.md` ou PDF) : nom, formule DAX, format, résultat vérifié ;
  - la **capture de la matrice de validation** (CA, marge %, panier moyen, YoY % par ville et année) ;
  - un **`README.md`** : description du projet, technologies, instructions d'ouverture, auteur(s).
- Une **note de fiabilité** (8 à 15 lignes) rédigée pour un lecteur métier — dans le catalogue ou le README.

## Modalités d'évaluation

Évaluation en deux volets :

- **Modèle et documentation (60 %)** : justesse des mesures, correction du formatage, fonctionnement de la *time intelligence*, rigueur de la validation croisée, clarté du catalogue de mesures.
- **Restitution orale (40 %)** : 10 minutes pour présenter les indicateurs à un « comité de direction » (le formateur et un autre binôme) en démontrant en direct la réactivité aux filtres + 5 minutes de questions.

**Validation partielle** : un binôme dont les mesures d'évolution ne sont pas toutes finalisées mais dont les mesures de base sont correctes, formatées et **validées par recoupement** peut valider partiellement les compétences travaillées.

## Critères de performance

**Concevoir des mesures DAX**
- Une table de mesures dédiée est créée et au moins 6 mesures y sont nommées sans ambiguïté.
- CA, marge % et panier moyen sont calculés correctement et bien formatés (€, %, séparateurs de milliers).
- La distinction mesure / colonne calculée est comprise et justifiée pour au moins un cas.

**Maîtriser la time intelligence**
- Au moins une mesure d'évolution N-1 / YoY est construite et s'appuie sur `Dim_Date`.
- La mesure d'évolution donne un résultat cohérent sur 2024 vs 2023.
- Le comportement aux bornes (année sans N-1, division par zéro) est identifié.

**Valider et fiabiliser**
- Au moins 2 mesures sont recoupées avec un calcul indépendant (pandas / Excel) sur un sous-ensemble.
- Les mesures réagissent correctement aux filtres dans une matrice ville × année.
- Tout écart de validation est expliqué ou l'absence d'écart est démontrée.

**Restituer**
- Le catalogue de mesures documente nom, formule, format et résultat vérifié pour chaque mesure.
- La note de fiabilité répond explicitement à la question centrale, sans jargon.
- Le dépôt GitHub public est complet (modèle/mesures + README + captures).

## Ressources

- Module de cours — [DAX & mesures avancées](../../../15-Business-Intelligence/10-DAX/)
- Rappels — [Modélisation en étoile & Power Query](../../../15-Business-Intelligence/09-Modelisation-Etoile-PowerQuery/)
- Cadrage — [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/)
- Documentation officielle DAX : https://learn.microsoft.com/fr-fr/dax/
- Time intelligence Power BI : https://learn.microsoft.com/fr-fr/dax/time-intelligence-functions-dax
- Étape suivante du parcours — projet de fin de phase : [BRIEF_2 — Solution BI avancée](../BRIEF_2_SOLUTION_BI_AVANCEE.md)
