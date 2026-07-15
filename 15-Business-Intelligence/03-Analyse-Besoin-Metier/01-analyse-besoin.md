# 01 — Analyse du besoin métier

| | |
|---|---|
| **Phase** | 0 — La Prairie (mise à niveau / découverte) |
| **Durée** | ~20 heures |
| **Objectifs** | *Identifier les indicateurs clés (KPI)* · *Choisir des visualisations pertinentes* · *Élaborer la problématique métier* |
| **Pré-requis** | le module « découverte du métier de Data Analyst ». Savoir lire un tableau de chiffres simple. Aucun outil technique requis. |
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
- **C'est le cœur du métier** : formaliser la problématique, définir les KPI et choisir les visualisations sont des gestes centraux. Tu les retrouveras dans **tous** tes projets et à la certification.

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

## Approfondissement — cadrer un besoin en autonomie (niveau 3)

Jusqu'ici, tu as appris à **imiter** (suivre une grille) et à **adapter** (ajuster les questions à un cas). Ici, on monte d'un cran : **transposer**. Tu dois être capable, **seul(e) et face à un commanditaire pressé et flou**, de repartir avec une **note de cadrage** propre — le document qui protège ton travail et celui du métier. C'est ce niveau qu'on attend d'un Data Analyst en poste et à la certification (niveau *transposer*).

> 🧭 **Notre fil rouge : NordRetail.** *NordRetail* est une enseigne de distribution fictive des Hauts-de-France : 42 magasins (Lille, Roubaix, Amiens, Dunkerque, Valenciennes…), un site e-commerce, un programme de fidélité et un rayon « produits régionaux ». On va s'en servir dans tout cet approfondissement, puis dans les exercices. Retiens-la : elle revient dans les modules suivants.

### 1. Le cadre d'entretien de recueil (version « autonome »)

La grille de la section précédente était un aide-mémoire. Voici la version **décisionnelle** : sept questions qui, si tu obtiens une réponse claire à chacune, te suffisent pour cadrer n'importe quel besoin. Si **une seule** reste vide, ton cadrage n'est pas terminé.

| # | Question à obtenir | Pourquoi elle est cruciale | Ce qu'une bonne réponse ressemble |
|---|---|---|---|
| 1 | **Qui décide ?** Qui est le *vrai* commanditaire, celui qui agira ? | Sans décideur identifié, tu produis pour personne. Le demandeur n'est pas toujours le décideur. | « La directrice commerciale régionale, Mme Dubois. » |
| 2 | **Quelle décision précise** sera prise avec l'analyse ? | C'est la règle d'or : pas de décision = pas de besoin mûr. | « Décider dans quels magasins ouvrir le dimanche. » |
| 3 | **À quelle fréquence** cette décision est-elle prise ? | Une décision annuelle ≠ un pilotage quotidien. Ça change tout (livrable, fraîcheur des données). | « Chaque trimestre, en comité régional. » |
| 4 | **Quelles données existent** déjà, et sont-elles fiables ? | Un besoin sans donnée disponible n'est pas réalisable *à court terme*. Il faut le savoir tôt. | « Ventes en caisse par magasin/jour, fiables depuis 2 ans. » |
| 5 | **Quel délai / quelle cible** de valeur ? Par rapport à quoi juge-t-on « bien » ? | Un chiffre sans comparaison ni cible ne pilote rien. | « Livré sous 3 semaines ; cible = +5 % de CA/magasin. » |
| 6 | **Qu'est-ce qui est hors périmètre ?** | Le périmètre non-borné est la cause n°1 de projets qui débordent. Écris ce que tu NE feras PAS. | « Hors périmètre : le e-commerce, les prévisions, la RH. » |
| 7 | **À quoi ressemble le succès ?** Comment saura-t-on que ça a servi ? | Critère de recette. Sans lui, tu ne pourras jamais « clôturer ». | « La direction a tranché sur les ouvertures dominicales grâce au tableau. » |

> 💡 **Le réflexe de niveau 3** : après l'entretien, tu ne repars pas avec « des notes ». Tu repars avec une **note de cadrage écrite** que tu renvoies au commanditaire *avant* de commencer. Ce simple aller-retour élimine la moitié des malentendus.

**Comment on enchaîne les 7 questions concrètement.** Tu ne les poses pas dans l'ordre du tableau comme un formulaire. Tu ouvres large (« racontez-moi le problème »), puis tu **coches mentalement** chacune des 7 au fil de l'échange. À la fin, tu regardes ta grille : les cases vides sont exactement les questions qu'il te reste à poser. C'est ta *checklist de sortie* d'entretien.

> ⚠️ **Erreur courante n°8 — Confondre « le demandeur » et « le décideur ».** La personne qui t'envoie la demande (souvent un chef de projet, un assistant, un manager intermédiaire) n'est pas toujours celle qui **agira** avec ton analyse. Remonte toujours jusqu'à la question 1 : *« qui prendra la décision ? »*. Si tu produis pour le demandeur alors que le décideur voulait autre chose, ton travail sera refait.

### 2. Transformer un besoin flou en questions analytiques mesurables — méthode

Un besoin flou (« nos ventes stagnent, aidez-nous ») ne se traite pas d'un bloc. On le **décompose** en questions qui, chacune, ont trois propriétés :

- **Elles sont fermées** au sens data : elles appellent un chiffre ou une liste, pas une opinion.
- **Elles portent une dimension** (par magasin ? par mois ? par catégorie ?).
- **Elles portent une comparaison** (vs N-1 ? vs objectif ? vs les autres magasins ?).

La recette : pour chaque hypothèse de cause possible du symptôme, tu écris **la question qui la confirme ou l'infirme**. Une bonne décomposition couvre les grandes causes plausibles sans partir dans tous les sens.

#### Exemple entièrement déroulé — NordRetail

> **Ce que dit la direction (besoin exprimé)** : *« Nos ventes stagnent depuis quelques mois, aidez-nous à comprendre. »*

C'est le cas typique : un symptôme (« stagnent »), une émotion (inquiétude), aucune dimension, aucune comparaison, aucune décision. On déroule.

**Étape A — Clarifier le symptôme.** « Stagner », c'est quoi, chiffré ? Après entretien : le **CA total régional est plat (≈ 0 %) sur les 6 derniers mois**, alors qu'il progressait de +4 %/an avant. On tient un fait mesurable.

**Étape B — Identifier la décision.** Question magique : *« Si vous saviez exactement d'où vient la stagnation, que feriez-vous ? »* Réponse de Mme Dubois : *« Je réallouerais le budget d'animation commerciale (promos, réagencement, effectifs) vers les zones qui peuvent redécoller. »* → **Décision = où concentrer le budget d'animation du prochain trimestre.**

**Étape C — Décomposer en questions analytiques.** Le CA global plat peut cacher des mouvements opposés. On formule les questions qui testent chaque grande cause :

| # | Hypothèse testée | Question analytique (mesurable) | Comparaison |
|---|---|---|---|
| Q1 | La stagnation est **globale ou localisée** ? | Quelle est l'évolution du CA **par magasin** sur 12 mois ? | vs même mois N-1 |
| Q2 | Un **type de produit** décroche ? | Quelle est l'évolution du CA **par catégorie de rayon** ? | vs N-1 |
| Q3 | Est-ce un problème de **trafic** ou de **panier** ? | Le nb de tickets et le **panier moyen** évoluent-ils ? | vs N-1, par magasin |
| Q4 | Perd-on des **clients fidèles** ? | Le **taux de rétention** des porteurs de carte baisse-t-il ? | vs trimestre précédent |
| Q5 | Le **e-commerce cannibalise-t-il** le magasin ? *(à confirmer si dans le périmètre)* | Le CA web progresse-t-il quand le magasin de la même zone recule ? | corrélation zone par zone |

**Étape D — Périmètre in / out.**

- **Dans le périmètre** : les 42 magasins physiques ; CA, tickets, panier moyen, catégories de rayon ; 13 mois d'historique ; données de fidélité.
- **Hors périmètre (validé avec la direction)** : le e-commerce détaillé (on garde juste Q5 comme signal, pas d'analyse web complète) ; les **prévisions** de ventes futures (c'est un autre projet) ; les causes RH/managériales (non mesurables dans les données disponibles) ; les données concurrents.

**Étape E — Livrable attendu.** Un **tableau de bord de diagnostic** en une page : une carte des 42 magasins colorée par évolution de CA, un classement des rayons gagnants/perdants, et l'évolution trafic vs panier. Objectif : que Mme Dubois **pointe en 30 secondes** les 5-6 magasins et 2-3 rayons où concentrer le budget. Fréquence : rafraîchi mensuellement, décision prise en comité trimestriel.

> 🎯 **Ce qui vient de se passer** : on est parti d'une phrase d'humeur et on a produit **5 questions data précises, un périmètre borné et un livrable actionnable** — sans avoir ouvert le moindre outil. C'est ça, cadrer en autonomie.

### 3. Gabarit de note de cadrage

La **note de cadrage** est le livrable de fin d'entretien. Une page, huit rubriques, à faire valider par le commanditaire **avant** de produire quoi que ce soit. Voici le gabarit vierge à réutiliser.

| Rubrique | Ce qu'on y écrit |
|---|---|
| **1. Problématique** | Le problème métier en 1-2 phrases, du point de vue du commanditaire. |
| **2. Parties prenantes** | Qui décide, qui demande, qui consulte le résultat, qui fournit la donnée. |
| **3. Questions analytiques** | La liste numérotée des questions mesurables (avec leur comparaison). |
| **4. KPI pressentis** | Les indicateurs associés, avec formule. *Pressentis* = à confirmer, pas gravés. |
| **5. Périmètre (in / out)** | Ce qui est dans le scope ET, explicitement, ce qui en est exclu. |
| **6. Données** | Sources, disponibilité, fiabilité, granularité, profondeur d'historique. |
| **7. Délais & jalons** | Date de livraison cible, fréquence de rafraîchissement, points d'étape. |
| **8. Critères de succès** | Comment on saura que le livrable a servi (recette + décision effectivement prise). |

#### Exemple rempli — NordRetail

> **Note de cadrage — Diagnostic de la stagnation des ventes régionales**
> *Rédigée par : [toi, Data Analyst] · Validée par : Mme Dubois, directrice commerciale régionale · Date : 12/07/2026*

| Rubrique | Contenu |
|---|---|
| **1. Problématique** | Le CA régional de NordRetail est plat (≈ 0 %) sur 6 mois alors qu'il progressait de +4 %/an. La direction ne sait pas si la stagnation est globale ou concentrée sur certains magasins / rayons, et où agir. |
| **2. Parties prenantes** | *Décide* : Mme Dubois (dir. commerciale). *Demande* : idem. *Consulte le résultat* : comité régional trimestriel + directeurs de magasin. *Fournit la donnée* : service caisse (ventes) et service fidélité (cartes). |
| **3. Questions analytiques** | Q1 — évolution du CA par magasin vs N-1. Q2 — évolution du CA par catégorie de rayon vs N-1. Q3 — évolution du nb de tickets et du panier moyen par magasin vs N-1. Q4 — évolution du taux de rétention des porteurs de carte vs trimestre précédent. |
| **4. KPI pressentis** | CA par magasin (Σ ventes) ; variation CA % = (CA N − CA N-1) ÷ CA N-1 × 100 ; panier moyen = CA ÷ nb tickets ; taux de rétention = 100 − churn ; CA par catégorie de rayon. |
| **5. Périmètre (in / out)** | **In** : 42 magasins physiques, 13 mois d'historique, données caisse + fidélité. **Out** : e-commerce détaillé, prévisions futures, causes RH/managériales, données concurrents. |
| **6. Données** | Ventes caisse par magasin/jour/rayon (fiables, 2 ans d'historique) ; base fidélité (porteurs de carte, dates d'achat). Granularité disponible : jour, magasin, rayon. À vérifier : complétude des rayons sur les 3 nouveaux magasins ouverts en 2025. |
| **7. Délais & jalons** | Note de cadrage validée : S0. Premier tableau de bord de diagnostic : S+3. Rafraîchissement : mensuel. Décision : comité trimestriel de septembre. |
| **8. Critères de succès** | Le comité identifie sans ambiguïté les 5-6 magasins et 2-3 rayons prioritaires **et** décide de l'allocation du budget d'animation. Le tableau est lisible en < 1 min par un non-analyste. |

> 💡 **Pourquoi ça marche** : cette note tient sur une page, elle est signée des deux côtés, et surtout la rubrique 5 (périmètre *out*) et la rubrique 8 (critères de succès) sont écrites **noir sur blanc**. Ce sont elles qui t'éviteront le « ah mais j'aurais aussi voulu le e-commerce » trois semaines plus tard.

### 4. Les pièges du cadrage — et comment arbitrer

> ⚠️ **Piège n°1 — La demande contradictoire.** Le commanditaire veut « une vue simple d'une page » ET « pouvoir filtrer par magasin, par rayon, par vendeur, par jour et par mode de paiement ». Les deux ne tiennent pas ensemble.
> **Arbitrage** : rends l'arbitrage explicite et fais-le trancher par le décideur. *« Une page ultra-lisible OU un outil d'exploration complet, on ne peut pas maximiser les deux. Pour votre décision trimestrielle, je recommande la vue synthétique ; on garde l'exploration détaillée en second écran. »* Tu proposes, il décide, tu l'écris dans la note.

> ⚠️ **Piège n°2 — Le commanditaire absent.** La demande arrive par un intermédiaire (« la direction voudrait… ») et tu n'as jamais accès au vrai décideur.
> **Arbitrage** : n'avance pas à l'aveugle. Formule tes hypothèses de cadrage **par écrit** et demande une validation, même par mail, du décideur réel. Tant que la rubrique 2 (parties prenantes) n'a pas de décideur identifié et joignable, signale le **risque** au chef de projet plutôt que de produire dans le vide.

> ⚠️ **Piège n°3 — Le périmètre qui gonfle (*scope creep*).** Au fil des échanges, on ajoute « et tant qu'à faire, le e-commerce », « et les prévisions », « et l'année dernière aussi »… Le projet triple sans que le délai bouge.
> **Arbitrage** : reviens systématiquement à la **note de cadrage validée**. Chaque ajout est une **demande de changement** : *« Bonne idée. C'est hors du périmètre qu'on a validé le 12/07. On peut l'ajouter, mais ça décale la livraison de X ou ça remplace une autre question. Que préférez-vous ? »* Tout ajout a un coût, et c'est le décideur qui paie ce coût, pas toi.

> 🎯 **Le principe commun aux trois pièges** : tu n'es **pas** là pour dire non. Tu es là pour **rendre les arbitrages visibles** et les faire trancher par celui qui décide — puis les **tracer** dans la note. Un bon cadrage ne supprime pas les tensions, il les met sur la table.

### 5. Checklist « mon cadrage est-il terminé ? »

Avant de lancer la moindre analyse, passe cette liste. Si tu réponds « non » ou « je ne sais pas » à **une seule** ligne, retourne voir le commanditaire — tu n'es pas prêt.

- [ ] Je peux nommer **le décideur** (pas seulement le demandeur).
- [ ] Je sais **quelle décision précise** sera prise avec mon analyse.
- [ ] Chaque question analytique a une **dimension** et une **comparaison**.
- [ ] Chaque KPI pressenti a une **formule** et une **donnée disponible**.
- [ ] J'ai écrit ce qui est **hors périmètre**, noir sur blanc.
- [ ] Je connais le **délai** et la **fréquence** de rafraîchissement attendus.
- [ ] J'ai défini **à quoi ressemble le succès** (critère de recette).
- [ ] La **note de cadrage** est écrite et **validée** par le commanditaire.

> 🎯 **En une phrase** : cadrer en autonomie, c'est transformer une conversation floue en un document d'une page que le commanditaire signe — et qui te protège autant qu'il le sert.

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

### Exercice 3 — Rédiger une note de cadrage à partir d'un mail

Tu reçois ce mail d'un commanditaire de NordRetail. Tu n'as **pas** de réunion prévue : tu dois cadrer avec ce que tu as, quitte à lister les questions à poser en retour.

> **De :** Karim Benali, responsable du programme fidélité — NordRetail
> **Objet :** Besoin urgent avant le comité
> *« Bonjour, on lance bientôt notre nouvelle carte de fidélité et la direction me demande si l'ancienne « marchait » vraiment. J'ai l'impression qu'on a plein de porteurs de carte mais que beaucoup ne s'en servent jamais. J'aimerais un truc clair à montrer au comité dans 3 semaines pour décider si on garde le même système d'avantages ou si on change tout. Le e-commerce, on verra plus tard. Merci ! »*

**Consigne** : rédige la **note de cadrage** (les 8 rubriques du gabarit) pour ce besoin. Marque explicitement les rubriques où il te manque une info (`À confirmer avec Karim : …`).

<details>
<summary>Corrigé Exercice 3 — note de cadrage proposée</summary>

| Rubrique | Contenu proposé |
|---|---|
| **1. Problématique** | NordRetail veut savoir si l'actuel programme de fidélité est réellement utilisé (beaucoup de porteurs supposés inactifs) afin de décider s'il faut reconduire ou refondre le système d'avantages avant le lancement de la nouvelle carte. |
| **2. Parties prenantes** | *Demande* : Karim Benali (resp. fidélité). *Décide* : le comité (à préciser). *Consulte* : comité de direction. *Fournit la donnée* : service fidélité + caisse. **À confirmer avec Karim : qui tranche exactement au comité ?** |
| **3. Questions analytiques** | Q1 — combien de porteurs de carte au total et combien ont **utilisé** la carte au moins une fois sur les 12 derniers mois ? Q2 — quelle part du CA magasin est réalisée avec une carte fidélité (vs sans) ? Q3 — les porteurs actifs ont-ils un panier moyen / une fréquence d'achat supérieurs aux non-porteurs ? |
| **4. KPI pressentis** | Taux d'activation carte = (porteurs actifs ÷ porteurs total) × 100 ; part de CA « encarté » = (CA avec carte ÷ CA total) × 100 ; panier moyen porteur vs non-porteur ; fréquence d'achat porteur. |
| **5. Périmètre (in / out)** | **In** : programme fidélité actuel, magasins physiques, 12 mois d'historique. **Out** : e-commerce (« on verra plus tard »), la conception de la future carte, les prévisions. |
| **6. Données** | Base fidélité (porteurs, dates d'usage), tickets de caisse rattachés ou non à une carte. **À confirmer : peut-on relier un ticket à un porteur de carte de façon fiable ?** (sans ça, Q2 et Q3 sont impossibles). |
| **7. Délais & jalons** | Livraison **avant le comité, dans 3 semaines**. Jalon : note validée par Karim sous 2 jours, sinon le délai de 3 semaines est menacé. |
| **8. Critères de succès** | Le comité décide de **reconduire ou refondre** le système d'avantages sur la base des chiffres. Le support est lisible en séance sans commentaire technique. |

> Points clés du corrigé : (1) on **borne le périmètre** grâce à l'indice du mail (« le e-commerce, on verra plus tard ») ; (2) on identifie le **risque data majeur** — pouvoir relier un ticket à un porteur — car sans lui, la moitié des questions tombent ; (3) on note que le **vrai décideur** (« le comité ») reste flou : à clarifier avant de lancer.
</details>

---

### Exercice 4 — Reformuler 3 demandes floues en questions mesurables

Voici trois phrases entendues chez NordRetail. Pour chacune, écris **une question analytique mesurable** (avec dimension **et** comparaison) et le **KPI** associé. Repère au passage la « fausse » demande, celle qui n'aide à aucune décision.

1. *« Je veux savoir si notre rayon produits régionaux, ça marche. »*
2. *« On dépense beaucoup en promos, est-ce que ça vaut le coup ? »*
3. *« Montre-moi le nombre total de visiteurs qu'on a eus depuis l'ouverture du magasin de Lille. »*

<details>
<summary>Corrigé Exercice 4</summary>

1. **Rayon régional** — *Question* : quelle est l'évolution du CA et du taux de marge du rayon « produits régionaux » sur 12 mois, **par magasin, vs N-1** ? *KPI* : CA rayon, taux de marge du rayon. (« ça marche » = ça vend **et** ça rapporte : on garde les deux.)
2. **Promos** — *Question* : quelle est l'évolution du CA et de la marge **pendant vs hors périodes de promo**, par catégorie ? *KPI* : uplift de CA en promo, **marge nette de promo** = marge générée − coût de la promo. (Le piège : une promo qui augmente le CA mais détruit la marge ne « vaut pas le coup ».)
3. **Visiteurs cumulés** — *Reformulation* : c'est un **vanity metric**. Le total depuis l'ouverture n'aide aucune décision. *Question utile à la place* : le nb de visiteurs **mensuel** du magasin de Lille progresse-t-il ou recule-t-il **vs N-1** ? *KPI* : visiteurs mensuels, variation %. **C'est la « fausse » demande à requalifier poliment.**

> Le réflexe transversal : une demande sans **dimension** (par quoi ?) ni **comparaison** (vs quoi ?) n'est pas encore une question analytique. Et un cumul « depuis le début » est presque toujours un vanity metric.
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

## Quiz (7 QCM)

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

**Q6.** La direction de NordRetail dit *« nos ventes stagnent, aidez-nous »*. Dans une **note de cadrage**, quelle rubrique est la plus efficace pour éviter que le projet gonfle (*scope creep*) ?
- a) les KPI pressentis
- b) le périmètre, en écrivant explicitement ce qui est **hors** périmètre
- c) la liste des vidéos d'auto-formation
- d) le choix du logiciel de BI

**Q7.** Un commanditaire te demande « une vue ultra-simple d'une page » **et** « pouvoir tout filtrer en détail ». Face à cette **demande contradictoire**, la bonne attitude est de…
- a) refuser le projet, c'est impossible
- b) choisir toi-même en silence et livrer ce qui te paraît le mieux
- c) rendre l'arbitrage explicite, recommander une option et laisser le **décideur** trancher, puis le tracer dans la note
- d) faire les deux quoi qu'il arrive, en doublant le délai sans prévenir

<details>
<summary>Réponses</summary>

- **Q1 → b.** Un besoin métier est lié à une décision, pas à une technique.
- **Q2 → c.** Questions ouvertes + reformulation + silence = écoute active. Proposer une solution trop tôt est l'erreur classique.
- **Q3 → c.** Spécifique, mesurable, temporel et avec une cible. Les autres sont vagues et non mesurables.
- **Q4 → b.** Évolution dans le temps = courbe.
- **Q5 → a.** Panier moyen = CA ÷ nombre de commandes. (b = taux de conversion, c = taux de marge, d = churn.)
- **Q6 → b.** Écrire noir sur blanc le **hors périmètre** est la meilleure protection contre le scope creep : chaque ajout devient une demande de changement à faire arbitrer.
- **Q7 → c.** On ne dit pas « non », on **rend l'arbitrage visible**, on recommande, et c'est le décideur qui tranche — puis on le trace dans la note de cadrage.
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
