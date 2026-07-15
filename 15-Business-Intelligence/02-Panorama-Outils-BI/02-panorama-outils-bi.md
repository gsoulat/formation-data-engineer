# 02 — Panorama des outils BI

> **Ton premier contact concret avec les outils du métier.** Avant de plonger dans la technique, tu vas découvrir le paysage des logiciels de Business Intelligence (BI), comprendre lequel choisir selon le contexte, puis **construire ton tout premier tableau de bord** dans un outil 100 % gratuit et web — sans rien installer.

| | |
|---|---|
| **Phase** | 0 — La Prairie (S1–S2) |
| **Durée** | ≈ 18 h |
| **Objectif** | Créer des tableaux de bord avec des outils de BI — **niveau 1 (découverte)** |
| **Pré-requis** | le module « le métier & le référentiel » · savoir naviguer sur le web · avoir (ou créer) un **compte Google** · notions de tableur (lignes/colonnes, somme, moyenne) |
| **Outils** | Navigateur web · **Looker Studio** (gratuit) · **Google Sheets** · un compte Google |

---

## Objectifs pédagogiques

À la fin de ce module, tu sauras :

1. **Expliquer ce qu'est un outil de Business Intelligence** et à quoi il sert dans le quotidien d'un Data Analyst.
2. **Citer et différencier** les 5 grands outils du marché : Power BI, Tableau, Looker Studio, Apache Superset, Metabase.
3. **Comparer** ces outils selon 3 critères clés : système d'exploitation (OS) supporté, coût, type d'usage.
4. **Comprendre la contrainte Mac** autour de Power BI Desktop et connaître les contournements.
5. **Expliquer pourquoi le Nord de la France privilégie Power BI** (tissu économique retail + Microsoft).
6. **Réaliser un premier tableau de bord** dans Looker Studio : connexion à une source Google Sheets, création de 2-3 graphiques, ajout d'un filtre, partage.

---

## Pourquoi c'est utile au Data Analyst

Un Data Analyst passe une grande partie de son temps à **restituer** : transformer des chiffres bruts en quelque chose qu'un décideur comprend en 10 secondes. Cette restitution se fait presque toujours dans un **outil de BI**.

Trois raisons de maîtriser ce panorama dès maintenant :

- **À l'embauche, on te demandera « Tu connais Power BI ? Tableau ? »** Savoir te situer, comparer, et avoir déjà construit un dashboard te donne une longueur d'avance, même débutant.
- **Le bon outil dépend du contexte** (budget, OS, équipe, source de données). Un Data Analyst n'est pas « le gars de Power BI » : il sait **choisir** l'outil adapté au besoin.
- **Tu es sur Mac ? Tu n'es pas bloqué.** Beaucoup d'apprenants paniquent en découvrant que Power BI Desktop n'existe pas sur Mac. Ce module te montre que tu peux apprendre la BI **dès aujourd'hui**, gratuitement, avec Looker Studio — et contourner la contrainte Power BI quand le moment viendra.

> 🧭 **Image à retenir.** Les données brutes, c'est de la farine, des œufs, du sucre. L'outil de BI, c'est **le four et le moule** : il transforme les ingrédients en un gâteau présentable. Le Data Analyst est le pâtissier — il doit savoir quel four utiliser selon ce qu'il veut cuire.

---

## C'est quoi, la Business Intelligence ?

### Définition simple

La **Business Intelligence** (BI), ou *informatique décisionnelle* en français, désigne **l'ensemble des outils et méthodes qui transforment des données brutes en informations utiles pour décider**.

Concrètement, un outil de BI sait :

1. **Se connecter** à des sources de données (fichier Excel, Google Sheets, base de données SQL, API…).
2. **Nettoyer et transformer** ces données (filtrer, calculer, agréger).
3. **Visualiser** : courbes, barres, cartes, indicateurs (KPI).
4. **Partager** le résultat sous forme de **tableau de bord** (dashboard) interactif.

> 📌 **Le mot clé : tableau de bord.** Comme dans une voiture, un dashboard rassemble en un coup d'œil les **indicateurs essentiels** : chiffre d'affaires du mois, nombre de clients, panier moyen, évolution… Le décideur regarde, comprend, agit.

### Données brutes → décision : la chaîne

```
   SOURCES              OUTIL DE BI                 RESTITUTION
┌────────────┐      ┌─────────────────┐         ┌──────────────┐
│  Excel     │      │  1. Connecter   │         │  Tableau de  │
│  Sheets    │ ───► │  2. Transformer │  ────►  │  bord        │
│  Base SQL  │      │  3. Visualiser  │         │  interactif  │
│  API       │      │  4. Partager    │         │  + KPI       │
└────────────┘      └─────────────────┘         └──────────────┘
   (le « quoi »)      (le travail du DA)          (la décision)
```

### BI ≠ tableur

Un tableur (Excel, Sheets) peut faire des graphiques, alors pourquoi un outil dédié ?

| | Tableur (Excel/Sheets) | Outil de BI |
|---|---|---|
| **Volume** | Quelques milliers de lignes | Millions de lignes sans ralentir |
| **Rafraîchissement** | Manuel (copier-coller) | Automatique (connexion permanente) |
| **Interactivité** | Limitée | Filtres, zoom, clics dynamiques |
| **Partage** | Envoi d'un fichier | Lien web mis à jour en temps réel |
| **Plusieurs sources** | Difficile | Croisement natif de sources |

> Le tableur reste excellent pour explorer vite un petit fichier. L'outil de BI prend le relais dès qu'il faut **automatiser, croiser, partager et présenter joliment**.

---

## Tour d'horizon comparatif des 5 outils

Voici les cinq outils que tu croiseras le plus souvent en entreprise.

### Tableau comparatif

| Outil | OS (poste de travail) | Coût | Type d'usage | Connexion typique |
|---|---|---|---|---|
| **Power BI** (Microsoft) | **Windows uniquement** (Desktop) · Service web tous OS | Gratuit (Desktop) ; **Pro ≈ 10 €/utilisateur/mois** pour partager | Standard entreprise, surtout en France | Excel, SQL Server, Azure, des centaines de connecteurs |
| **Tableau** (Salesforce) | **Mac + Windows** (natif) | **Payant et cher** (≈ 70 €/utilisateur/mois Creator) ; version gratuite « Public » | Data viz avancée, esthétique, gros volumes | Fichiers, bases SQL, cloud |
| **Looker Studio** (Google) | **Web — tous OS** | **100 % gratuit** | Reporting marketing/web, dashboards partagés | Google Sheets, BigQuery, Google Analytics, SQL |
| **Apache Superset** | **Web — tous OS** (à héberger) | **Gratuit (open source)** mais à installer/maintenir soi-même | BI technique, équipes data avec un serveur | Bases SQL (Postgres, MySQL…) |
| **Metabase** | **Web — tous OS** (cloud ou auto-hébergé) | **Open source gratuit** ; offre cloud payante | BI simple « pour tous », questions en langage quasi naturel | Bases SQL, data warehouses |

### Forces et faiblesses

**Power BI** 🟦
- ✅ Standard du marché français, intégration parfaite avec Excel/Office 365, langage DAX puissant, Desktop gratuit, énorme communauté.
- ❌ **Desktop = Windows uniquement** (gros frein pour les Mac), partage payant (licence Pro), courbe DAX un peu raide.

**Tableau** 🟧
- ✅ Reine de la **data visualisation** (rendu très soigné), performante sur gros volumes, fonctionne nativement sur **Mac et Windows**.
- ❌ **Coût élevé**, moins répandu que Power BI dans les PME françaises.

**Looker Studio** 🟩
- ✅ **Gratuit, web, zéro installation, tous OS**, prise en main rapide, parfait pour débuter et pour le marketing.
- ❌ Moins puissant sur les très gros volumes et les calculs complexes, dépend de l'écosystème Google.

**Apache Superset** 🟪
- ✅ Open source, gratuit, très flexible, idéal pour des équipes techniques branchées sur du SQL.
- ❌ **Il faut l'installer et le maintenir** (serveur, Docker…), courbe d'apprentissage plus technique.

**Metabase** 🟫
- ✅ Open source, **très simple**, permet de poser des questions sans coder, bon pour démocratiser la data.
- ❌ Moins de finesse graphique, fonctionnalités avancées dans l'offre payante.

> 🎯 **Ce qu'on attend de toi (niveau 1).** On ne te demande pas d'être expert des cinq. On te demande de **savoir les situer** : « Looker Studio = gratuit/web ; Power BI = standard France mais Windows ; Tableau = beau mais cher ; Superset/Metabase = open source à héberger. »

---

## Focus : la contrainte Mac ⚠️

C'est **le point qui pose problème à beaucoup d'apprenants Apple.** Lis-le attentivement.

### Le problème

> **Power BI Desktop n'existe PAS sur macOS.** C'est un logiciel **Windows uniquement.** Microsoft ne propose aucune version Mac.

Si tu es sur Mac, tu ne peux donc pas simplement « télécharger Power BI Desktop ». Mais tu as **trois contournements**.

### Les contournements (du plus simple au plus lourd)

| Solution | Comment | Avantages | Limites |
|---|---|---|---|
| **1. Power BI Service (web)** | Va sur `app.powerbi.com` dans Safari/Chrome. Tout se passe dans le navigateur. | Aucune installation, gratuit pour démarrer, fonctionne sur Apple Silicon (M1/M2/M3/M4) | Édition moins complète que Desktop (pas tout le Power Query / modélisation) ; partage nécessite une licence Pro |
| **2. Machine virtuelle (VM)** | Installer **Parallels Desktop** + Windows (ARM) sur le Mac, puis Power BI Desktop dedans | Power BI Desktop **complet** | Parallels est payant, Windows ARM à configurer, consomme RAM/disque |
| **3. Looker Studio à la place** | Apprendre la BI directement sur un outil web | Gratuit, immédiat, multi-OS, idéal pour débuter | Ce n'est pas Power BI (mais les **concepts** sont transférables) |

> 💡 **Stratégie conseillée pour la formation.** On apprend **les concepts** de la BI (sources, graphiques, filtres, KPI, partage) sur **Looker Studio** — qui marche pour tout le monde, Mac comme Windows, sans installation. Power BI viendra plus tard dans les phases avancées, et tu seras déjà à l'aise avec la logique.

### Et les autres outils sur Mac ?

- **Tableau** : ✅ natif Mac, aucun souci.
- **Looker Studio, Metabase, Superset** : ✅ web, fonctionnent sur n'importe quel OS via le navigateur.
- **Power BI Desktop** : ❌ le seul cas problématique → voir les contournements ci-dessus.

---

## Pourquoi le Nord de la France privilégie Power BI 🗺️

Tu es en formation dans les **Hauts-de-France**. Voici un fait à connaître pour tes entretiens locaux.

- Le Nord est une terre de **grande distribution / retail** : sièges et back-offices d'**Auchan, Decathlon, Leroy Merlin, Boulanger, Adeo, Kiabi, Cora**… La région concentre une densité rare d'entreprises orientées commerce et logistique.
- Ces entreprises sont massivement équipées de **l'écosystème Microsoft** (Windows, Office 365, Excel, Azure, SharePoint, Teams).
- **Power BI s'intègre nativement** dans cet écosystème : il lit Excel sans effort, se branche sur SQL Server / Azure, se partage via Teams. C'est le prolongement naturel d'Excel.
- Résultat : **la majorité des offres « Data Analyst » dans le Nord demandent Power BI.** C'est un réflexe d'employeur local.

> 🎯 **À retenir pour ta recherche d'emploi.** Dans le Nord, **Power BI est la compétence la plus demandée**. Tu apprendras les concepts sur Looker Studio (cross-OS, gratuit), puis tu transféreras vers Power BI — la logique est la même : sources → transformation → visuels → filtres → partage.

---

## TP guidé — Ton premier tableau de bord dans Looker Studio 🧪

**Objectif :** répliquer un tableau de bord de ventes simple à partir d'un Google Sheets. À la fin, tu auras un dashboard partageable contenant **un KPI, 2-3 graphiques et un filtre**.

> ⏱️ Compter **1 h 30 à 2 h**. Va lentement, lis chaque menu. C'est ton premier dashboard : savoure-le.

### Étape 0 — Préparer les données (Google Sheets)

1. Va sur **[sheets.google.com](https://sheets.google.com)** (connecte-toi avec ton compte Google).
2. Crée une nouvelle feuille, nomme-la **`ventes-demo`**.
3. Colle ce petit jeu de données (copie-colle directement, Sheets répartit les colonnes) :

| Date | Region | Categorie | Ventes | Quantite |
|---|---|---|---|---|
| 2026-01-05 | Nord | Sport | 1200 | 30 |
| 2026-01-12 | Nord | Maison | 800 | 15 |
| 2026-01-20 | Sud | Sport | 450 | 12 |
| 2026-02-03 | Nord | Sport | 1500 | 38 |
| 2026-02-10 | Sud | Maison | 620 | 10 |
| 2026-02-18 | Est | Sport | 900 | 22 |
| 2026-03-04 | Nord | Maison | 1100 | 20 |
| 2026-03-15 | Sud | Sport | 700 | 18 |
| 2026-03-22 | Est | Maison | 540 | 9 |

4. Vérifie que la **première ligne contient bien les noms de colonnes** (Looker Studio s'en sert comme champs).

> 🔑 **Règle d'or BI :** une bonne source = **une ligne par observation, une colonne par variable, des en-têtes clairs.** Pas de cellules fusionnées, pas de lignes vides.

### Étape 1 — Créer le rapport et connecter la source

1. Va sur **[lookerstudio.google.com](https://lookerstudio.google.com)** et connecte-toi.
2. Clique sur **« Créer » → « Rapport »** (ou le grand **« + Rapport vierge »**).
3. Une fenêtre **« Ajouter des données au rapport »** s'ouvre. Choisis le connecteur **« Google Sheets »**.
4. Sélectionne ton fichier **`ventes-demo`**, puis la feuille, puis clique **« Ajouter »**.
5. Si une fenêtre demande l'autorisation d'accéder à tes Sheets, **autorise**.
6. Looker Studio insère automatiquement un premier tableau de démonstration. **Clique dessus et supprime-le** (touche `Suppr`) — on repart de zéro.

> 👀 À gauche/droite, repère le panneau **« Données »** : tu y vois tes champs. Les **dimensions** (texte/date, en vert) = `Date, Region, Categorie`. Les **mesures** (nombres, en bleu) = `Ventes, Quantite`.

### Étape 2 — Ajouter un indicateur (KPI) : total des ventes

1. Menu du haut : **« Ajouter un graphique »**.
2. Choisis le type **« Carte de pointage »** (*Scorecard* / grand chiffre).
3. Clique sur le canevas pour le poser.
4. Dans le panneau de droite, vérifie que la **Métrique = `Ventes`** et que l'agrégation est **« Somme »**.
5. 🎉 Tu vois un grand chiffre : le **total des ventes**. Renomme le bloc « CA total » via l'onglet **Style** si tu veux.

### Étape 3 — Graphique 1 : ventes par catégorie (barres)

1. **« Ajouter un graphique » → « Graphique à barres »**.
2. Pose-le sous le KPI.
3. Dans le panneau de droite :
   - **Dimension** = `Categorie`
   - **Métrique** = `Ventes` (Somme)
4. Tu obtiens des barres comparant **Sport vs Maison**.

### Étape 4 — Graphique 2 : évolution dans le temps (courbe)

1. **« Ajouter un graphique » → « Graphique en courbes »** (*Time series*).
2. Pose-le à côté.
3. Panneau de droite :
   - **Dimension de date** = `Date`
   - **Métrique** = `Ventes`
4. Tu visualises l'**évolution des ventes** de janvier à mars.

### Étape 5 — (Bonus) Graphique 3 : répartition par région (camembert)

1. **« Ajouter un graphique » → « Graphique à secteurs »** (camembert).
2. **Dimension** = `Region`, **Métrique** = `Ventes`.
3. Tu vois la **part de chaque région** dans le total.

### Étape 6 — Ajouter un filtre interactif

1. Menu du haut : **« Ajouter une commande » → « Liste déroulante »** (*Drop-down list*).
2. Pose-la **en haut** du rapport.
3. Dans le panneau de droite, **Champ de contrôle = `Region`**.
4. Bascule en mode **« Affichage »** (bouton **« Afficher »** en haut à droite) et **teste** : choisis « Nord » → **tous les graphiques se filtrent en même temps.** 🎉

> 💡 C'est ça, l'**interactivité** d'un dashboard : un seul filtre pilote tous les visuels. Impossible (ou très pénible) dans un simple tableur.

### Étape 7 — Mettre en forme et titrer

1. Repasse en mode **« Modifier »**.
2. **« Ajouter un graphique » → « Texte »** : écris un titre, p. ex. **« Tableau de bord des ventes — démo »**.
3. Onglet **« Thème et mise en page »** (en haut) : choisis un thème propre. Aligne tes blocs.

### Étape 8 — Partager le rapport

1. Bouton **« Partager »** (en haut à droite).
2. Deux options :
   - **Inviter des personnes** par e-mail (Lecteur ou Éditeur).
   - **« Obtenir le lien du rapport »** → règle l'accès (ex. *toute personne disposant du lien*) → copie le lien.
3. Colle ce lien dans ton rendu de TP. **Bravo, ton premier dashboard est en ligne !** 🥳

---

### ⚠️ Encadré — Erreurs courantes dans le TP

| Symptôme | Cause probable | Solution |
|---|---|---|
| Mes champs `Ventes`/`Quantite` apparaissent en **texte** (vert) au lieu de nombres (bleu) | Dans Sheets, les nombres sont stockés comme texte (espaces, virgules) | Corrige le format dans Sheets (nombres), puis dans Looker : champ → **type → Nombre** |
| Le **graphique en courbes est vide ou bizarre** | Le champ `Date` n'est pas reconnu comme date | Vérifie le format `AAAA-MM-JJ` dans Sheets ; dans Looker, mets le type du champ sur **Date** |
| Le **filtre ne filtre rien** | Tu es resté en mode **« Modifier »** | Passe en mode **« Affichage »** pour interagir |
| « **Je ne vois pas mon Sheets** » à la connexion | Mauvais compte Google ou autorisation refusée | Vérifie le compte connecté ; réautorise l'accès Google Sheets |
| Les chiffres sont **trop gros / mal arrondis** | Agrégation ou format par défaut | Panneau **Style** → format du nombre (devise €, décimales) |
| « Tout est **en anglais** » | Langue de l'interface | Paramètres Looker → langue → Français (les noms de menus peuvent légèrement varier) |

---

## Exercices

### Exercice 1 — Situer les outils
Pour chacun de ces besoins, propose **l'outil le plus adapté** (et justifie en une phrase) :
a) Une équipe marketing veut un rapport gratuit, partagé par lien, branché sur Google Analytics.
b) Une grande enseigne de retail du Nord, full Microsoft, veut un standard d'entreprise.
c) Un apprenant sur Mac veut commencer la BI **aujourd'hui** sans rien installer.

<details><summary>✅ Corrigé</summary>

- a) **Looker Studio** — gratuit, partage par lien, connecteur Google Analytics natif.
- b) **Power BI** — standard du marché, intégration Microsoft (Excel, Azure, Teams) parfaite.
- c) **Looker Studio** — web, gratuit, multi-OS, zéro installation (Power BI Desktop n'existe pas sur Mac).
</details>

### Exercice 2 — La contrainte Mac
Vrai ou faux, et corrige si nécessaire :
a) « Power BI Desktop fonctionne sur Mac comme sur Windows. »
b) « Sur Mac, on peut quand même utiliser Power BI via le navigateur. »
c) « Tableau ne fonctionne pas sur Mac. »

<details><summary>✅ Corrigé</summary>

- a) **FAUX.** Power BI **Desktop** est **Windows uniquement**.
- b) **VRAI.** Via **Power BI Service** (`app.powerbi.com`) dans le navigateur (ou une VM Parallels pour le Desktop complet).
- c) **FAUX.** **Tableau fonctionne nativement sur Mac et Windows.**
</details>

### Exercice 3 — Réflexion BI vs tableur
Cite **deux situations** où un outil de BI est nettement supérieur à Excel/Sheets, et explique pourquoi.

<details><summary>✅ Corrigé (exemples)</summary>

1. **Partage en temps réel** : un dashboard BI se diffuse par lien et se met à jour automatiquement ; avec un tableur, il faut renvoyer un fichier à chaque mise à jour.
2. **Gros volumes / croisement de sources** : la BI gère des millions de lignes et croise plusieurs sources (SQL + Excel + API) sans ralentir, là où le tableur sature et devient ingérable.

(Autres réponses valables : interactivité par filtres, automatisation du rafraîchissement.)
</details>

### Exercice 4 — TP appliqué
Sur **ton** dashboard Looker Studio du TP :
a) Ajoute un **deuxième KPI** affichant le total des **quantités vendues**.
b) Ajoute un filtre **par catégorie** en plus du filtre région.
c) Mets le KPI des ventes au **format devise €**.

<details><summary>✅ Corrigé (méthode)</summary>

- a) **Ajouter un graphique → Carte de pointage** ; Métrique = `Quantite` (Somme).
- b) **Ajouter une commande → Liste déroulante** ; Champ de contrôle = `Categorie`. En mode Affichage, les deux filtres se combinent.
- c) Sélectionne le KPI Ventes → panneau **Style** (ou clic sur la métrique → format) → **Devise → EUR €**.
</details>

---

## Vidéos d'auto-formation 🎥

> ⚠️ Les liens marqués **🔎 (recherche)** ouvrent une recherche YouTube : choisis la vidéo la plus récente et la mieux notée. Les liens directs ont été vérifiés mais YouTube évolue — si une vidéo a disparu, utilise la recherche associée.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Looker Studio : créer un tableau de bord étape par étape (ex Data Studio) | (créateur FR) | 🇫🇷 FR | ~20 min | [Voir](https://www.youtube.com/watch?v=BVBvo9eKK40) | Construire un dashboard Looker de A à Z : exactement la logique du TP |
| Install Power BI Desktop on a Mac | (tuto EN) | 🇬🇧 EN | ~10 min | [Voir](https://www.youtube.com/watch?v=vsLGjIp2OUU) | Les options réelles pour faire tourner Power BI sur Mac (VM / web) |
| Power BI vs Tableau : lequel apprendre ? | — | 🇫🇷 FR | varie | [🔎 Recherche](https://www.youtube.com/results?search_query=power+bi+vs+tableau+lequel+choisir+fran%C3%A7ais) | Forces/faiblesses, coût, marché de l'emploi des deux leaders |
| Qu'est-ce que la Business Intelligence ? (expliqué simplement) | — | 🇫🇷 FR | varie | [🔎 Recherche](https://www.youtube.com/results?search_query=qu%27est+ce+que+la+business+intelligence+expliqu%C3%A9+simplement) | La définition et les usages de la BI en clair |
| Looker Studio full tutorial for beginners | — | 🇬🇧 EN | ~30–60 min | [🔎 Recherche](https://www.youtube.com/results?search_query=looker+studio+tutorial+for+beginners+2025) | Approfondir Looker Studio (champs calculés, styles, partage) |

---

## Quiz — 5 QCM

**Q1.** Quel outil de BI **n'a pas de version Desktop sur Mac** ?
- A) Tableau — B) Looker Studio — C) Power BI — D) Metabase

**Q2.** Lequel de ces outils est **100 % gratuit et web, sans installation** ?
- A) Power BI Desktop — B) Looker Studio — C) Tableau Creator — D) Apache Superset (auto-hébergé)

**Q3.** Pourquoi le **Nord de la France** privilégie-t-il Power BI ?
- A) C'est le seul outil gratuit — B) Tissu retail + écosystème Microsoft dominant — C) Power BI marche mieux sur Mac — D) C'est imposé par la loi

**Q4.** Sur Mac, comment utiliser Power BI **sans VM** ?
- A) Impossible — B) Via Power BI Service dans le navigateur — C) En installant le .exe — D) Avec Looker Studio renommé

**Q5.** Dans Looker Studio, quel élément rend un dashboard **interactif** en pilotant tous les graphiques ?
- A) Une carte de pointage — B) Un graphique à secteurs — C) Une commande / liste déroulante (filtre) — D) Un bloc texte

<details><summary>✅ Réponses</summary>

**Q1 : C** (Power BI Desktop = Windows uniquement) · **Q2 : B** (Looker Studio) · **Q3 : B** (retail + Microsoft) · **Q4 : B** (Power BI Service web) · **Q5 : C** (la commande/filtre).
</details>

---

## À retenir 🧠

- La **Business Intelligence** transforme des **données brutes en décisions** via un cycle **connecter → transformer → visualiser → partager**.
- Un **tableau de bord** réunit les KPI essentiels en un coup d'œil ; un outil de BI bat le tableur sur le **volume, l'automatisation, l'interactivité et le partage**.
- Les 5 outils repères : **Power BI** (standard France, Windows), **Tableau** (beau, cher, Mac+Win), **Looker Studio** (gratuit, web, idéal débutant), **Superset & Metabase** (open source à héberger).
- **Contrainte Mac : Power BI Desktop n'existe pas sur macOS.** Contournements : **Power BI Service (web)**, **VM Parallels**, ou apprendre sur **Looker Studio** (cross-OS).
- **Dans le Nord**, Power BI est la compétence la plus demandée (retail + Microsoft) → on apprend les concepts sur Looker Studio, ils se transfèrent.
- Tu sais désormais **construire un dashboard** : source Sheets → KPI + graphiques → filtre → partage. C'est le geste de base du métier. 🚀
