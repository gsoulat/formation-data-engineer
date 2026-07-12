# 01 — Analyse du besoin métier

| | |
|---|---|
| **Phase** | 0 — La Prairie (mise à niveau / découverte) |
| **Durée** | ~20 heures |
| **Compétences visées** | **C16** *Identifier les indicateurs clés (KPI)* — niveau 1 · **C17** *Choisir des visualisations pertinentes* — niveau 1 · **C11** *Élaborer la problématique métier* — introduction |
| **Pré-requis** | Module 0.1 (découverte du métier de Data Analyst), Module 0.2 (vocabulaire de la donnée). Savoir lire un tableau de chiffres simple. Aucun outil technique requis. |
| **Type** | **Initiation.** Le niveau 2 (adapter / transposer) sera travaillé en Phase 1. Ici, on découvre et on imite. |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Expliquer ce qu'est un besoin métier** et pourquoi il est presque toujours flou au départ.
2. **Conduire un mini-entretien de recueil de besoin** : poser les bonnes questions, pratiquer l'écoute active, reformuler.
3. **Traduire un besoin flou en questions analytiques mesurables** (de « je veux mieux comprendre mes ventes » à « quel est le CA par magasin et par mois sur 12 mois ? »).
4. **Définir des indicateurs de performance (KPI) simples** et reconnaître un bon KPI d'un mauvais.
5. **Choisir un type de visualisation** en fonction de l'intention (comparaison, évolution, répartition, relation).
6. **Comprendre et employer le vocabulaire métier de base** du retail et de l'e-commerce (CA, marge, panier moyen, taux de conversion, churn…).

> Ce module ne demande aucun code ni aucun logiciel. C'est de la **réflexion, de la communication et du bon sens métier**. C'est pourtant la compétence la plus sous-estimée — et la plus différenciante — d'un Data Analyst.

---

## Pourquoi c'est utile au Data Analyst

Beaucoup de gens pensent que le métier de Data Analyst, c'est « faire des graphiques » ou « écrire du SQL ». C'est faux. Le vrai métier commence **avant** : comprendre ce qu'on te demande réellement.

> Un Data Analyst qui ne sait pas recueillir un besoin, c'est un cuisinier qui prépare un plat magnifique… mais qui n'est pas celui que le client avait commandé.

Trois raisons très concrètes :

- **80 % des dashboards inutiles le sont parce que le besoin a été mal compris**, pas parce que la technique était mauvaise. Un graphique techniquement parfait qui répond à la mauvaise question ne sert à rien.
- **Le commanditaire ne sait presque jamais formuler son besoin en termes de données.** Il te dira « je veux savoir si ça va bien ». À toi de transformer ça en KPI mesurables. C'est ton expertise.
- **C'est le cœur du référentiel RNCP-38616** : les compétences C11 (problématique), C16 (KPI) et C17 (visualisation) sont au centre du bloc BC06. Tu les retrouveras dans **tous** tes projets et à la certification.

Dans la vraie vie d'un analyste chez Auchan, Decathlon ou La Redoute, **la moitié de la valeur que tu apportes se joue dans la première réunion** avec le métier.

---

## Contenu détaillé

### Qu'est-ce qu'un besoin métier ?

Un **besoin métier**, c'est un **problème ou une question qu'une personne de l'entreprise se pose pour prendre une décision**. Ce n'est PAS une demande technique.

| Ce que dit le commanditaire (besoin métier) | Ce que ce N'EST PAS |
|---|---|
| « Je ne sais pas quels produits font vraiment marcher la boutique. » | « Fais-moi un graphique en barres. » |
| « J'ai l'impression qu'on perd des clients mais je n'en suis pas sûr. » | « Calcule le churn avec une jointure SQL. » |
| « Mon reporting me prend deux jours par mois. » | « Installe Power BI. » |

Le besoin métier est presque **toujours flou, parfois contradictoire, et exprimé dans le langage du métier**, pas dans celui des données. Ton premier travail est de **clarifier**, pas d'exécuter.

#### Les 3 niveaux d'un besoin

1. **Le besoin exprimé** : ce que la personne dit (« je veux un tableau de bord »).
2. **Le besoin réel** : ce qu'elle veut vraiment (« je veux repérer les magasins en difficulté avant qu'il soit trop tard »).
3. **Le besoin décisionnel** : la décision qu'elle prendra (« décider où envoyer un renfort commercial »).

> 🎯 **Règle d'or** : tant que tu ne connais pas la **décision** que ton analyse va permettre de prendre, tu n'as pas fini de recueillir le besoin.

> ⚠️ **Erreur courante n°1 — Foncer sur l'outil.** Dès qu'on entend « tableau de bord », on ouvre Power BI. STOP. Tu ne sais pas encore quelle question on te pose. L'outil vient en dernier.

---

### Conduire un entretien de recueil de besoin

L'entretien de recueil de besoin est une **conversation structurée** avec le commanditaire (le « métier », le « client interne », le « stakeholder »). Objectif : repartir avec une compréhension claire du problème et de ce qu'il faut produire.

#### Les 4 phases d'un entretien

1. **Cadrer** — Se présenter, expliquer le but de l'échange, rassurer. *« Je suis là pour comprendre votre besoin, pas pour vous vendre une solution. »*
2. **Explorer** — Poser des questions ouvertes, laisser parler, ne pas couper. C'est 70 % de l'entretien.
3. **Approfondir** — Creuser les zones floues, demander des exemples concrets, des chiffres.
4. **Reformuler et valider** — Résumer ce que tu as compris et faire confirmer. *« Si je résume, vous voulez… C'est bien ça ? »*

#### L'écoute active : 4 réflexes

- **Questions ouvertes** : commence par *Comment, Pourquoi, Qu'est-ce que, Décrivez-moi…* plutôt que par des questions fermées (oui/non).
- **Reformulation** : *« Donc si je comprends bien, … »* — ça montre que tu écoutes ET ça corrige les malentendus tout de suite.
- **Silence** : après une question, **tais-toi**. Le silence pousse l'autre à développer. C'est inconfortable, c'est normal, c'est efficace.
- **Creuser avec « pourquoi »** : la technique des **5 Pourquoi** permet de passer du symptôme à la cause. *« Pourquoi voulez-vous ce chiffre ? — Pour décider quoi ? — Et si vous l'aviez, que feriez-vous ? »*

> ⚠️ **Erreur courante n°2 — Proposer des solutions trop tôt.** Si tu dis « ah, je vais vous faire un camembert » à la 3e minute, tu arrêtes de comprendre le besoin. Garde tes idées de solution pour la fin.

> ⚠️ **Erreur courante n°3 — Le jargon.** Ne parle pas de « jointures », « granularité » ou « série temporelle » au commanditaire. Parle SON langage (magasins, rayons, clients, mois).

#### Grille d'entretien réutilisable

Voici une grille que tu peux emporter à chaque entretien. Adapte-la, ne la récite pas mécaniquement.

| Thème | Questions à poser |
|---|---|
| **Contexte & rôle** | Quel est votre rôle ? De quoi êtes-vous responsable au quotidien ? |
| **Le problème** | Quel problème cherchez-vous à résoudre ? Depuis quand ? Qu'est-ce qui a déclenché cette demande ? |
| **La décision** | Quelle décision allez-vous prendre grâce à cette analyse ? Que feriez-vous si vous aviez la réponse ? |
| **Le « bien » et le « mal »** | Comment savez-vous aujourd'hui que ça va bien ou mal ? À quoi le voyez-vous ? |
| **Les chiffres clés** | Y a-t-il des chiffres que vous regardez déjà ? Lesquels comptent le plus pour vous ? |
| **Le périmètre** | Sur quoi ça porte ? (quels magasins, quels produits, quelle période) Qu'est-ce qu'on EXCLUT ? |
| **Le détail (granularité)** | Vous voulez voir ça par jour, par mois ? Par magasin, par région ? |
| **Comparaison & cible** | Par rapport à quoi voulez-vous comparer ? (mois précédent, année dernière, objectif, autres magasins) |
| **Les utilisateurs** | Qui va consulter le résultat ? La direction ? Les chefs de rayon ? À quelle fréquence ? |
| **Le format & l'urgence** | Sous quelle forme ? (un écran à regarder en 30 s, un fichier détaillé…) Pour quand ? |
| **Les données** | D'où viennent les données aujourd'hui ? Sont-elles fiables ? Qui les saisit ? |

> 💡 **Astuce** : la question la plus puissante est *« Que feriez-vous si vous aviez la réponse ? »*. Si le commanditaire ne sait pas répondre, c'est que le besoin n'est pas mûr — ou que le KPI demandé ne sert à rien.

---

### Du besoin flou au KPI mesurable

C'est le cœur du module. On part d'une phrase vague et on la transforme en **questions analytiques** puis en **indicateurs mesurables**.

#### La méthode en 4 étapes

1. **Reformuler le besoin** en une phrase claire.
2. **Découper en questions analytiques** précises (qui, quoi, quand, comparé à quoi).
3. **Associer un ou plusieurs KPI** à chaque question.
4. **Vérifier que chaque KPI est mesurable** (on a la donnée, on a une formule).

#### Exemple complet

> **Besoin exprimé** : « J'aimerais mieux comprendre comment marche ma boutique en ligne. »

**Étape 1 — Reformulation** : Le responsable e-commerce veut identifier ce qui freine les ventes du site pour décider où agir.

**Étape 2 — Questions analytiques** :
- Combien de visiteurs viennent sur le site chaque mois, et combien achètent ?
- Quel est le montant moyen d'une commande ?
- Quelles catégories de produits génèrent le plus de chiffre d'affaires ?
- Le chiffre d'affaires progresse-t-il ou recule-t-il sur 12 mois ?

**Étape 3 & 4 — KPI mesurables** :

| Question | KPI | Formule | Donnée nécessaire |
|---|---|---|---|
| Combien achètent ? | **Taux de conversion** | (commandes ÷ visiteurs) × 100 | nb visiteurs, nb commandes |
| Montant moyen ? | **Panier moyen** | CA ÷ nb de commandes | CA, nb commandes |
| Quelles catégories ? | **CA par catégorie** | somme des ventes par catégorie | ventes, catégorie produit |
| Ça progresse ? | **Évolution du CA mensuel** | CA du mois N vs N-1 (en %) | ventes datées |

#### Qu'est-ce qu'un bon KPI ? La méthode SMART

Un bon indicateur est **SMART** :

- **S**pécifique — il mesure une chose précise (pas « la performance », mais « le panier moyen »).
- **M**esurable — on a la donnée et une formule claire.
- **A**tteignable / actionnable — on peut agir dessus.
- **R**elevant (pertinent) — il aide vraiment à la décision.
- **T**emporel — il a une période et une fréquence (mensuel, hebdomadaire…).

Un KPI sans **cible** et sans **comparaison** ne veut rien dire. « Le CA est de 120 000 € » : et alors ? Bien ou mal ? Il faut « 120 000 €, soit +8 % vs le même mois l'an dernier, au-dessus de l'objectif de 110 000 € ».

#### Indicateurs d'activité vs indicateurs de résultat

| Type | Aussi appelé | Mesure | Exemple retail |
|---|---|---|---|
| **Indicateur d'activité** | *leading* (avancé) | Une action en cours, prédictive | nb de visiteurs, nb de devis envoyés |
| **Indicateur de résultat** | *lagging* (retard) | Le résultat final, constaté | CA, marge, nb de clients perdus |

> Les indicateurs d'activité te disent ce qui **va arriver** ; les indicateurs de résultat te disent ce qui **est arrivé**. Un bon tableau de bord mélange les deux.

> ⚠️ **Erreur courante n°4 — Le KPI « vanity ».** Certains chiffres flattent l'ego mais n'aident à aucune décision (ex. « nombre total de pages vues depuis le début »). Si personne ne peut agir dessus, ce n'est pas un KPI utile.

---

### Glossaire métier (retail & e-commerce)

À maîtriser absolument. Tu les croiseras dans tous tes projets Phase 1.

| Terme | Définition simple | Calcul / exemple |
|---|---|---|
| **CA (Chiffre d'affaires)** | Total des ventes (hors taxes en général) sur une période | Σ (prix de vente × quantités) |
| **Marge brute** | Ce qui reste après avoir retiré le coût d'achat des produits vendus | CA − coût d'achat des marchandises |
| **Taux de marge** | La marge exprimée en % du CA | (marge ÷ CA) × 100 |
| **Panier moyen** | Montant moyen dépensé par commande | CA ÷ nombre de commandes |
| **Taux de conversion** | Part des visiteurs qui achètent | (commandes ÷ visiteurs) × 100 |
| **Taux de transformation** | Synonyme courant de taux de conversion en magasin | (tickets ÷ visiteurs) × 100 |
| **Churn (taux d'attrition)** | Part des clients perdus sur une période | (clients perdus ÷ clients début de période) × 100 |
| **Taux de rétention** | Part des clients conservés (l'inverse du churn) | 100 − churn |
| **Taux de retour** | Part des produits renvoyés (clé en e-commerce / VAD) | (produits retournés ÷ produits vendus) × 100 |
| **LTV / Customer Lifetime Value** | Valeur totale générée par un client sur toute sa relation | panier moyen × fréquence × durée de vie |
| **Coût d'acquisition (CAC)** | Combien coûte le recrutement d'un nouveau client | dépenses marketing ÷ nb nouveaux clients |
| **Fréquence d'achat** | Combien de fois un client achète sur une période | nb commandes ÷ nb clients |
| **Rotation des stocks** | Vitesse à laquelle le stock se vend et se renouvelle | coût des ventes ÷ stock moyen |
| **Ticket moyen** | Équivalent du panier moyen en magasin physique | CA ÷ nombre de tickets de caisse |

> 💡 Pour t'entraîner : prends chaque terme et demande-toi *« quelle décision ce chiffre aide-t-il à prendre ? »*. Si tu sais répondre, tu as compris.

---

### Premiers choix de visualisation (intention → graphique)

Une fois le KPI défini, il faut le **montrer**. Le bon graphique dépend de **ce que tu veux faire dire aux données** : ton **intention**.

> 🎯 **Le principe** : tu ne choisis pas un graphique parce qu'il est « joli », mais parce qu'il correspond à une intention. Demande-toi toujours : *« Qu'est-ce que je veux que le lecteur voie en 3 secondes ? »*

| Intention (ce que tu veux montrer) | Graphique recommandé | Exemple retail/e-commerce |
|---|---|---|
| **Comparer** des catégories entre elles | **Barres** (horizontales si les noms sont longs) | CA par magasin, ventes par rayon |
| **Montrer une évolution** dans le temps | **Courbe** (line chart), ou aire | CA mensuel sur 12 mois |
| **Montrer une répartition** (part d'un tout) | **Barres empilées 100 %** ou **treemap** ; camembert seulement si ≤ 4-5 parts | Répartition du CA par famille de produits |
| **Montrer une relation** entre 2 variables | **Nuage de points** (scatter plot) | Lien entre prix et nombre de ventes |
| **Montrer une distribution** d'une variable | **Histogramme** ou **boxplot** | Répartition des montants de panier |
| **Mettre en avant 1 KPI clé vs sa cible** | **Carte / big number** (+ jauge simple) | « CA du mois : 120 k€ (+8 %) » |
| **Donnée géographique** | **Carte choroplèthe** | CA par région des Hauts-de-France |

#### Les 4 intentions à retenir absolument (niveau 1)

| Mot-clé | Question type | Graphique réflexe |
|---|---|---|
| **Comparaison** | « Qui fait le plus / le moins ? » | **Barres** |
| **Évolution** | « Ça monte ou ça descend ? » | **Courbe** |
| **Répartition** | « Quelle part représente chaque morceau ? » | **Barres empilées / treemap** |
| **Relation** | « Est-ce que X et Y bougent ensemble ? » | **Nuage de points** |

> ⚠️ **Erreur courante n°5 — Le camembert à 10 parts.** L'œil humain est incapable de comparer 10 angles. Au-delà de 4-5 parts, passe aux barres. Et JAMAIS deux camemberts côte à côte pour comparer.

> ⚠️ **Erreur courante n°6 — L'axe tronqué.** Commencer l'axe vertical à 95 au lieu de 0 exagère visuellement les écarts et trompe le lecteur. Pour des barres, l'axe doit partir de 0.

> ⚠️ **Erreur courante n°7 — La 3D et les fioritures.** La 3D déforme les proportions et n'apporte aucune information. Reste en 2D, sobre, lisible.

> 💡 **Accessibilité (à connaître dès maintenant)** : pense aux personnes daltoniennes — n'utilise jamais la couleur SEULE pour distinguer deux séries, ajoute des étiquettes. Donne toujours un **titre explicite** à ton graphique (pas « Graphique 1 » mais « Le CA recule depuis mars »).

---

## Exercices

### Exercice 1 — Jeu de rôle : entretien de recueil de besoin

**En binôme.** L'un joue le **commanditaire**, l'autre le **Data Analyst**. Durée : 10 min d'entretien, puis on inverse.

**Carte de rôle commanditaire (à ne pas montrer au binôme analyste)** :
> *Tu es responsable d'un magasin Decathlon à Villeneuve-d'Ascq. Tu trouves que « le magasin tourne moins bien en ce moment » mais tu ne sais pas pourquoi. Tu aimerais « un truc pour suivre ça ». Si on te creuse, tu finis par admettre : tu veux savoir quels rayons décrochent pour réorganiser tes équipes. Tu regardes déjà le CA quotidien sur un Excel. Tu veux comparer au même mois l'an dernier.*

**Consigne pour l'analyste** : mène l'entretien avec la grille (section 3.2). Repars avec : le besoin reformulé, la décision visée, 2-3 KPI, le périmètre, la granularité.

<details>
<summary>Corrigé — déroulé attendu de l'entretien</summary>

Un bon analyste devrait :

1. **Cadrer** : « Je suis là pour comprendre ce dont vous avez besoin, on parlera outils après. »
2. **Explorer** avec des questions ouvertes : « Qu'est-ce qui vous fait dire que le magasin tourne moins bien ? »
3. **Creuser la décision** : « Si vous saviez exactement quels rayons décrochent, que feriez-vous ? » → *réorganiser les équipes*. **C'est le besoin réel.**
4. **Périmètre & granularité** : un seul magasin, vue par rayon, par mois.
5. **Comparaison** : vs même mois N-1 (le commanditaire l'a dit spontanément).
6. **Reformuler** : « Si je résume : vous voulez repérer chaque mois les rayons dont le CA recule par rapport à l'an dernier, pour décider où renforcer vos équipes. C'est ça ? »

**Livrable attendu de l'analyste :**
- *Besoin reformulé* : identifier les rayons en recul de CA pour réaffecter les équipes.
- *Décision* : où mettre les renforts humains.
- *KPI* : CA par rayon (mensuel) ; évolution du CA par rayon vs N-1 (%).
- *Périmètre* : 1 magasin, tous rayons, 13 derniers mois.
- *Visualisation pressentie* : barres (comparaison rayons) + courbe ou variation % (évolution).

**Pièges à éviter** (et à débriefer) : proposer Power BI trop tôt, ne pas demander la décision, accepter « je veux suivre ça » sans creuser, oublier de reformuler à la fin.
</details>

---

### Exercice 2 — Traduire 3 besoins flous en KPI

Pour chacun des 3 besoins ci-dessous : (a) reformule en 1 phrase, (b) écris 2 questions analytiques, (c) propose 1 à 2 KPI avec leur formule, (d) indique le graphique adapté.

1. **Besoin A** (e-commerce, La Redoute) : *« On a beaucoup de visiteurs mais j'ai l'impression qu'ils n'achètent pas assez. »*
2. **Besoin B** (retail, Auchan) : *« Je veux savoir si nos clients fidèles reviennent ou s'ils nous quittent. »*
3. **Besoin C** (grande distribution) : *« Quels produits rapportent vraiment de l'argent, pas juste ceux qui se vendent beaucoup ? »*

<details>
<summary>Corrigé Exercice 2</summary>

**Besoin A — Conversion**
- (a) *Reformulation* : le responsable e-commerce veut comprendre pourquoi le trafic ne se transforme pas en ventes.
- (b) *Questions* : Quel est le taux de conversion global ? Évolue-t-il dans le temps / diffère-t-il selon les catégories ?
- (c) *KPI* : **Taux de conversion** = (commandes ÷ visiteurs) × 100 ; **Panier moyen** = CA ÷ commandes.
- (d) *Graphique* : courbe du taux de conversion dans le temps (évolution) ; barres par catégorie (comparaison).

**Besoin B — Fidélité / churn**
- (a) *Reformulation* : mesurer si la base de clients fidèles se maintient ou s'érode.
- (b) *Questions* : Quel est le taux de churn mensuel ? Combien de clients reviennent d'un mois sur l'autre ?
- (c) *KPI* : **Churn** = (clients perdus ÷ clients début période) × 100 ; **Taux de rétention** = 100 − churn.
- (d) *Graphique* : courbe du churn / rétention dans le temps (évolution).

**Besoin C — Rentabilité vs volume**
- (a) *Reformulation* : distinguer les produits rentables (marge) des produits à fort volume mais faible marge.
- (b) *Questions* : Quelle est la marge par produit ? Quels produits ont un fort CA mais une faible marge ?
- (c) *KPI* : **Marge brute par produit** = CA produit − coût d'achat ; **Taux de marge** = (marge ÷ CA) × 100.
- (d) *Graphique* : barres de la marge par produit (comparaison) ; ou nuage de points volume vs marge (relation) pour repérer les « faux best-sellers ».

> Le piège du Besoin C : confondre « se vend beaucoup » (volume / CA) et « rapporte » (marge). Un produit best-seller à marge nulle ne rapporte rien.
</details>

---

## Vidéos d'auto-formation

> ⚠️ Les liens marqués 🔎 ouvrent une **recherche YouTube** (la vidéo exacte évolue) ; les liens directs ont été vérifiés. Privilégie toujours une vidéo récente et bien notée.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Comprendre les KPI ou indicateurs clés de performance | Xerfi Canal (Philippe Gattet) | 🇫🇷 FR | ~10 min | [Voir](https://www.youtube.com/watch?v=44U0pr9CczM) | Définition claire d'un KPI, à quoi il sert, comment bien le choisir |
| Réussir ton entretien / case study de Data Analyst | (chaîne FR data) | 🇫🇷 FR | ~15 min | [Voir](https://www.youtube.com/watch?v=IpV4JgmXKEs) | Comment cadrer un problème métier et le traduire en analyse |
| Recueil du besoin / requirements gathering (business analysis) | recherche | 🇫🇷 FR | varie | [🔎 Rechercher](https://www.youtube.com/results?search_query=recueil+du+besoin+business+analyst+entretien) | Conduite d'entretien, questions à poser, écoute active |
| Data Visualization: How to choose the right chart | recherche | 🇬🇧 EN | varie | [🔎 Rechercher](https://www.youtube.com/results?search_query=how+to+choose+the+right+chart+data+visualization) | Associer le bon graphique à l'intention (comparaison/évolution/etc.) |
| KPIs explained: how to define good metrics | recherche | 🇬🇧 EN | varie | [🔎 Rechercher](https://www.youtube.com/results?search_query=how+to+define+good+KPI+metrics+data+analyst) | Définir des KPI SMART, éviter les vanity metrics |

---

## Quiz (5 QCM)

**Q1.** Un besoin métier, c'est avant tout…
- a) une demande technique précise (« fais un graphique en barres »)
- b) un problème ou une question liée à une décision
- c) le choix d'un logiciel de BI
- d) une requête SQL

**Q2.** Pendant un entretien de recueil de besoin, le meilleur réflexe est de…
- a) proposer une solution dès la première minute
- b) parler le plus possible pour montrer ton expertise
- c) poser des questions ouvertes, reformuler et laisser des silences
- d) utiliser un maximum de vocabulaire technique

**Q3.** Lequel de ces KPI est correctement « SMART » ?
- a) « la performance du magasin »
- b) « beaucoup de visiteurs »
- c) « le taux de conversion mensuel, avec une cible de 3 % »
- d) « le succès global de la boutique »

**Q4.** Tu veux montrer l'**évolution du chiffre d'affaires mois par mois sur un an**. Quel graphique ?
- a) un camembert
- b) une courbe (line chart)
- c) un nuage de points
- d) un histogramme

**Q5.** Le **panier moyen** se calcule…
- a) CA ÷ nombre de commandes
- b) nombre de commandes ÷ nombre de visiteurs
- c) marge ÷ CA
- d) clients perdus ÷ clients de départ

<details>
<summary>Réponses</summary>

- **Q1 → b.** Un besoin métier est lié à une décision, pas à une technique.
- **Q2 → c.** Questions ouvertes + reformulation + silence = écoute active. Proposer une solution trop tôt est l'erreur classique.
- **Q3 → c.** Spécifique, mesurable, temporel et avec une cible. Les autres sont vagues et non mesurables.
- **Q4 → b.** Évolution dans le temps = courbe.
- **Q5 → a.** Panier moyen = CA ÷ nombre de commandes. (b = taux de conversion, c = taux de marge, d = churn.)
</details>

---

## À retenir

- Un **besoin métier** est flou par nature et lié à une **décision** — ton job est de le clarifier, pas de foncer sur l'outil.
- L'**entretien de recueil** repose sur l'**écoute active** : questions ouvertes, reformulation, silences, et la question magique *« que feriez-vous si vous aviez la réponse ? »*.
- On passe du besoin flou au **KPI mesurable** en 4 étapes : reformuler → questions analytiques → KPI → vérifier la mesurabilité.
- Un bon KPI est **SMART**, avec une **cible** et une **comparaison** ; on distingue indicateurs d'**activité** (leading) et de **résultat** (lagging).
- Le **vocabulaire métier** (CA, marge, panier moyen, taux de conversion, churn…) est ta langue commune avec le métier.
- Le choix de la **visualisation** suit l'**intention** : comparaison → barres, évolution → courbe, répartition → barres empilées/treemap, relation → nuage de points.
- Les pièges classiques : foncer sur l'outil, proposer une solution trop tôt, le jargon, le camembert à 10 parts, l'axe tronqué, la 3D, les vanity metrics.

> 🚀 **La suite (Phase 1, niveau 2)** : tu apprendras à adapter ces méthodes à des cas réels plus complexes, à formaliser un vrai cahier des charges, et à construire les visualisations dans un outil de BI.
