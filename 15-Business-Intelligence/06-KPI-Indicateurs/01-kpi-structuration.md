# 01 — KPI & structuration du tableau de bord

| | |
|---|---|
| **Phase** | Phase 1 — Concevoir un tableau de bord |
| **Durée** | ~20 heures |
| **Compétences visées** | **C16** (niveau 1 → 2) : Identifier et formaliser les indicateurs de performance répondant à un besoin métier · **C11** : Traduire un besoin métier en spécifications fonctionnelles |
| **Pré-requis** | Module 0.3 (analyse de besoin en Prairie), 1.2 (Python & pandas pour l'EDA), 1.3 (Identifier les tendances). Savoir lire un tableau de chiffres simple. Aucune compétence technique BI n'est requise pour ce module. |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Définir** ce qu'est un KPI (indicateur clé de performance) et le distinguer d'une simple métrique.
2. **Construire** un KPI selon la méthode SMART : formule de calcul, granularité, fréquence de mesure, cible.
3. **Différencier** un indicateur de résultat (*lagging*) d'un indicateur d'activité (*leading*) et expliquer pourquoi tu as besoin des deux.
4. **Sélectionner** les KPI usuels pertinents selon un domaine métier (ventes, marketing, RH, logistique).
5. **Structurer** l'arborescence d'un tableau de bord, de la vue direction synthétique à la vue opérationnelle détaillée.
6. **Maquetter** un tableau de bord (zoning, hiérarchie visuelle) *avant* de le construire dans un outil.

---

## Pourquoi c'est utile au Data Analyst

Un Data Analyst ne « fait pas des graphiques ». Il **transforme une question métier en décision**. Entre les deux, il y a un objet central : le **KPI**.

Concrètement, dans ta future mission :

- Le **commanditaire** (un directeur, un responsable rayon, un chef de produit) ne sait presque jamais quel indicateur il veut. Il sait quel **problème** il a (« mes ventes baissent », « on perd des clients »). Ton premier travail, c'est de traduire ce problème flou en **KPI mesurables et actionnables**.
- Si tu choisis les **mauvais KPI**, tout le reste de ton travail (collecte, nettoyage, dashboard) est inutile : tu auras produit un bel objet qui ne répond pas à la question.
- Un tableau de bord mal **structuré** noie l'information : le décideur ne trouve pas ce qu'il cherche en 5 secondes et n'utilise plus l'outil. Savoir hiérarchiser (synthèse → détail) est aussi important que savoir calculer.
- **Maquetter avant de construire** te fait gagner des heures : tu valides le besoin avec le métier sur une esquisse papier au lieu de refaire trois fois un dashboard Power BI complet.

> C16 et C11 sont au cœur du métier : elles sont évaluées dans **chaque** brief de la certification. Ce module est la fondation de toute la Phase 1.

---

## Qu'est-ce qu'un KPI ?

### Définition

Un **KPI** (*Key Performance Indicator*, indicateur clé de performance) est une **mesure quantifiée, suivie dans le temps, qui exprime le niveau d'atteinte d'un objectif métier**.

Trois mots comptent :

- **clé** : ce n'est PAS toutes les mesures possibles. Un KPI est *sélectionné* parce qu'il est lié à un objectif. Une entreprise peut mesurer 500 choses ; elle n'a que 5 à 10 *vrais* KPI par responsable.
- **performance** : il mesure si on **réussit** quelque chose, donc il est relié à une **cible**. Une mesure sans cible n'est qu'un chiffre.
- **indicateur** : il *indique* une direction, il déclenche une **décision** ou une **action**. S'il ne change aucune décision, ce n'est pas un KPI utile.

### Métrique ≠ KPI

| | Métrique | KPI |
|---|---|---|
| Définition | Une mesure brute, neutre | Une mesure **reliée à un objectif et à une cible** |
| Exemple | « 12 400 visites sur le site cette semaine » | « Taux de conversion = 2,1 %, cible 2,5 % » |
| Question posée | « Combien ? » | « Est-ce qu'on atteint l'objectif ? » |
| Déclenche | Rien en soi | Une action si l'écart à la cible est trop grand |

**Tout KPI est une métrique, mais toute métrique n'est pas un KPI.** Le KPI est une métrique *promue* parce qu'on a décidé qu'elle pilotait une décision.

### Les composantes d'un bon KPI

Un KPI complet, exploitable par un Data Analyst, se décrit toujours par **5 éléments** :

1. **Le nom** — clair et compris du métier (« Panier moyen », pas « AVG_BASKET_V2 »).
2. **La formule de calcul** — sans ambiguïté (voir SMART ci-dessous).
3. **La granularité** — à quel niveau de détail on le regarde (par magasin ? par jour ? par catégorie de produit ?).
4. **La fréquence** — à quel rythme on le rafraîchit et on le lit (temps réel, quotidien, hebdo, mensuel).
5. **La cible (et un seuil d'alerte)** — la valeur visée, et le niveau à partir duquel on s'inquiète.

---

## La méthode SMART appliquée aux KPI

SMART est une grille classique de définition d'objectif. Appliquée à un KPI, elle garantit qu'il est **exploitable** et pas juste une intention vague.

| Lettre | Signification pour un KPI | Mauvais exemple | Bon exemple |
|---|---|---|---|
| **S** — Spécifique | On sait exactement quoi on mesure et sur quel périmètre | « Augmenter les ventes » | « CA hebdo du rayon textile du magasin de Lille » |
| **M** — Mesurable | Formule de calcul explicite, à partir de données disponibles | « La satisfaction des clients » | « % de tickets SAV résolus en < 48 h = tickets clos < 48h / tickets ouverts » |
| **A** — Atteignable | La cible est ambitieuse mais réaliste | « 0 % d'invendus » | « Taux d'invendus < 4 % » |
| **R** — Relevant (pertinent) | Le KPI est relié à un objectif métier réel | « Nombre de couleurs sur le site » | « Taux de conversion du tunnel d'achat » |
| **T** — Temporel | Une fréquence de mesure ET un horizon de cible | « Améliorer la marge » | « Marge brute mensuelle ≥ 32 % d'ici fin Q3 » |

### La formule de calcul : le cœur du KPI

Sans formule explicite, deux personnes calculeront le même KPI différemment et se disputeront sur les chiffres. **Toujours écrire la formule.**

Quelques formules incontournables (retail / e-commerce) :

| KPI | Formule |
|---|---|
| Chiffre d'affaires (CA) | Σ (quantité vendue × prix de vente) |
| Marge brute | CA − coût des marchandises vendues |
| Taux de marge | Marge brute / CA × 100 |
| Panier moyen | CA / nombre de transactions |
| Taux de conversion | Nombre de commandes / nombre de visiteurs × 100 |
| Taux d'invendus | Quantité invendue / quantité en stock × 100 |

### Granularité

La **granularité** = le niveau de détail le plus fin auquel on peut découper le KPI.

Exemple pour le CA : *total entreprise → région → magasin → rayon → produit → ticket de caisse*.

> Règle d'or : on **stocke** la donnée à la granularité la plus fine possible, mais on **affiche** au niveau adapté à la personne qui regarde. Un directeur régional veut le CA par magasin ; un chef de rayon veut le CA par produit.

### Fréquence

À quel rythme le KPI a-t-il un sens ?

- **Temps réel / horaire** : flux de caisse un jour de soldes, trafic site pendant une campagne.
- **Quotidien** : CA du jour, ruptures de stock.
- **Hebdomadaire** : performance d'un rayon, taux de conversion.
- **Mensuel** : marge, CAC, turnover RH.

Mesurer un KPI plus souvent que nécessaire crée du bruit et de la fausse urgence. Le turnover RH lu chaque heure n'a aucun sens.

### Cible et seuil d'alerte

Un KPI sans cible n'est qu'une mesure. La **cible** donne le sens (vert = on y est, rouge = on agit).

Exemple : Taux de conversion — **cible 2,5 %**, **seuil d'alerte < 1,8 %** (en dessous, on déclenche une analyse).

---

## Indicateurs de résultat (*lagging*) vs d'activité (*leading*)

C'est l'une des distinctions les plus importantes — et les plus mal comprises — du métier.

| | **Lagging** (de résultat) | **Leading** (d'activité / avancé) |
|---|---|---|
| Mesure… | Un **résultat déjà arrivé** | Un **comportement qui prépare** le résultat |
| Répond à | « Est-ce que ça a marché ? » | « Est-ce que c'est en train de marcher ? » |
| Quand on le lit | **Après** | **Avant / pendant** |
| Avantage | Fiable, factuel | Permet d'**agir à temps** |
| Inconvénient | Trop tard pour corriger | Plus difficile à définir, parfois indirect |

**Exemples retail / e-commerce :**

| Objectif | Indicateur lagging (résultat) | Indicateur leading (activité) |
|---|---|---|
| Augmenter le CA mensuel | CA du mois (connu en fin de mois) | Nombre de visiteurs/jour, taux de conversion, panier moyen |
| Réduire le churn (clients perdus) | Taux d'attrition trimestriel | Fréquence de connexion, nombre de paniers abandonnés |
| Réussir une campagne promo | CA généré par la promo | Taux de clics sur l'emailing, trafic en magasin |

> **Idée clé :** un bon tableau de bord mêle les deux. Les *lagging* prouvent où tu en es ; les *leading* te disent quoi faire **maintenant** pour changer le résultat de demain. Piloter uniquement avec des lagging, c'est conduire en ne regardant que le rétroviseur.

---

## Catalogue de KPI usuels par domaine

> Ce catalogue est une **boîte à outils**, pas une liste à copier en entier. Tu en choisis toujours quelques-uns selon le besoin.

### Ventes / Retail / E-commerce

| KPI | Formule | Type | Granularité fréquente | Fréquence |
|---|---|---|---|---|
| Chiffre d'affaires (CA) | Σ (qté × prix) | Lagging | Magasin / rayon / jour | Quotidien |
| Marge brute | CA − coût des ventes | Lagging | Rayon / produit | Mensuel |
| Taux de marge | Marge / CA × 100 | Lagging | Produit | Mensuel |
| Panier moyen | CA / nb transactions | Lagging | Magasin / canal | Hebdo |
| Taux de conversion | Commandes / visiteurs × 100 | Leading | Site / page | Quotidien |
| Taux d'invendus | Invendus / stock × 100 | Lagging | Produit | Hebdo |
| Nombre de transactions | Comptage des tickets | Leading | Magasin / jour | Quotidien |

### Marketing

| KPI | Formule | Type | Fréquence |
|---|---|---|---|
| CAC (coût d'acquisition client) | Dépenses marketing / nb nouveaux clients | Lagging | Mensuel |
| Taux d'ouverture (emailing) | Emails ouverts / emails délivrés × 100 | Leading | Par campagne |
| Taux de clic (CTR) | Clics / impressions × 100 | Leading | Par campagne |
| ROAS (retour sur dépense pub) | CA généré / dépense pub | Lagging | Mensuel |
| LTV (valeur vie client) | Panier moyen × fréquence d'achat × durée de vie | Lagging | Trimestriel |
| Taux de désabonnement (newsletter) | Désabos / abonnés × 100 | Leading | Par campagne |

> **Ratio à connaître :** LTV / CAC. En dessous de 3, l'acquisition coûte trop cher par rapport à ce que rapporte un client.

### RH

| KPI | Formule | Type | Fréquence |
|---|---|---|---|
| Turnover (rotation du personnel) | Nb départs / effectif moyen × 100 | Lagging | Trimestriel |
| Taux d'absentéisme | Jours d'absence / jours travaillés théoriques × 100 | Lagging | Mensuel |
| Délai de recrutement | Date d'embauche − date d'ouverture du poste | Lagging | Par poste |
| Taux de satisfaction interne (eNPS) | % promoteurs − % détracteurs | Leading | Semestriel |
| Heures de formation / salarié | Σ heures formation / effectif | Leading | Annuel |

### Logistique / Supply chain

| KPI | Formule | Type | Fréquence |
|---|---|---|---|
| Taux de service (OTIF) | Commandes livrées complètes & à l'heure / total × 100 | Lagging | Hebdo |
| Taux de rupture de stock | Références en rupture / total références × 100 | Leading | Quotidien |
| Délai de livraison moyen | Σ (date réception − date commande) / nb commandes | Lagging | Hebdo |
| Rotation des stocks | CA (au coût) / stock moyen | Lagging | Mensuel |
| Taux de retour | Produits retournés / produits expédiés × 100 | Lagging | Mensuel |

---

## Du besoin métier au tableau de bord : structurer l'arborescence

Un tableau de bord n'est pas un tas de graphiques. C'est une **arborescence** qui suit la logique de décision de l'organisation.

### Le principe « synthèse → détail »

On structure en **niveaux**, du plus synthétique au plus détaillé. C'est le principe de la **pyramide de pilotage** :

```
            ┌─────────────────────────────┐
            │   VUE DIRECTION (stratégique)│   5-7 KPI max, très synthétiques
            │   CA global, marge, NPS      │   « Est-ce qu'on va bien ? »
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   VUE MANAGER (tactique)     │   KPI par région / par canal
            │   CA par magasin, conversion │   « Où est le problème ? »
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   VUE OPÉRATIONNELLE         │   Détail par produit / par jour
            │   Ventes par produit, stock  │   « Que fait-on concrètement ? »
            └─────────────────────────────┘
```

- **Vue direction** : ouvre le dashboard. Quelques chiffres clés, des comparaisons (vs cible, vs N-1), peu de détail. Lecture en 5 secondes.
- **Vue manager / tactique** : on descend d'un cran. Le décideur voit *où* ça se passe (quel magasin, quelle région, quel canal).
- **Vue opérationnelle** : le maximum de détail, pour celui qui agit (chef de rayon, gestionnaire de stock).

> Cette logique « du général au particulier » est exactement ce que fait le **drill-down** dans Power BI / Looker Studio : on clique sur une barre de la vue direction pour descendre vers le détail.

### De la question métier aux KPI : la démarche

1. **Recueillir l'objectif métier** (« je veux augmenter la rentabilité de mes magasins du Nord »).
2. **Le décomposer en sous-questions** (« quels magasins sont rentables ? quels rayons plombent la marge ? »).
3. **Associer un KPI à chaque sous-question** (marge par magasin, taux d'invendus par rayon…).
4. **Vérifier que chaque KPI est SMART et actionnable.**
5. **Répartir les KPI dans les niveaux** de l'arborescence (synthèse vs détail).

> **Test final d'un KPI : « Et si ce chiffre devient rouge, qu'est-ce que je fais ? »** Si tu n'as pas de réponse, le KPI n'a pas sa place dans le dashboard.

---

## Maquetter un tableau de bord avant de le construire

Avant d'ouvrir Power BI, tu dessines une **maquette** (sur papier, sur un tableau blanc ou un outil comme Figma/Excel). Cela force à réfléchir au message **avant** la technique.

### Le zoning

Le **zoning** = découper l'écran en zones et décider *quoi va où*, sans encore mettre les vrais graphiques (de simples rectangles annotés).

On exploite le **sens de lecture occidental en Z / en F** : l'œil va d'abord **en haut à gauche**, puis vers la droite, puis descend.

```
┌───────────────────────────────────────────────────────┐
│  TITRE + filtres (période, magasin)                    │
├───────────────┬───────────────┬───────────────────────┤
│  KPI clé 1    │  KPI clé 2    │  KPI clé 3            │  ← « cartes » de synthèse
│  (CA + écart) │  (Marge)      │  (Conversion)        │     (zone la + lue)
├───────────────┴───────────────┴───────────────────────┤
│  Graphique principal (évolution du CA dans le temps)   │  ← le message n°1
├───────────────────────────┬───────────────────────────┤
│  Répartition par magasin   │  Top / Flop produits     │  ← détails de support
└───────────────────────────┴───────────────────────────┘
```

### La hiérarchie visuelle

Le lecteur doit comprendre **dans quel ordre regarder** sans réfléchir. On guide l'œil par :

- **La taille** : l'élément le plus important est le plus gros.
- **La position** : le plus important en haut à gauche.
- **La couleur** : on réserve la couleur vive (rouge/vert) aux alertes, le reste reste neutre. La couleur partout = plus aucune couleur ne ressort.
- **Le regroupement** : ce qui va ensemble est physiquement proche (les KPI de vente d'un côté, les KPI de stock de l'autre).

### Pourquoi maquetter d'abord ?

- Tu valides le besoin avec le métier sur un dessin de 10 minutes plutôt qu'un dashboard de 2 jours.
- Tu repères les manques de données *avant* de te lancer.
- Tu sépares la réflexion (« que doit-on montrer ? ») de la technique (« comment le faire dans l'outil ? »).

---

> ### ⚠️ Encadré — Erreur courante n°1 : trop de KPI
> Le réflexe du débutant est d'ajouter « au cas où ». Un dashboard avec 25 indicateurs ne dit **rien** : le décideur ne sait pas où regarder. La règle largement admise (Tableau, Qlik) : **pas plus de 5 à 9 vues par écran**, et **5 à 7 KPI clés** pour une vue direction. Si tu hésites à enlever un KPI, demande-toi : « quelle décision change-t-il ? » Si aucune, supprime-le.

> ### ⚠️ Encadré — Erreur courante n°2 : les vanity metrics
> Une **vanity metric** (métrique de vanité) est un chiffre qui **flatte mais ne pilote rien** : nombre total de visites, nombre de followers, nombre de pages vues cumulées depuis le lancement. Ils montent toujours, font plaisir, mais ne disent pas si l'entreprise **réussit**. Le contraire = une **actionable metric** : taux de conversion, marge par client, taux de rétention — des chiffres dont la variation déclenche une décision. Question test : *« Si ce chiffre double, est-ce que je gagne plus d'argent / résous mon problème ? »* Si la réponse est floue, c'est une vanity metric.

> ### ⚠️ Encadré — Erreur courante n°3 : le KPI non actionnable
> Un KPI peut être SMART **et** inutile s'il ne mène à aucune action que tu maîtrises. Mesurer « la météo des jours de promo » est précis et mesurable, mais tu ne peux rien y faire. Un bon KPI porte sur un levier que l'organisation **contrôle**.

---

## Exercices

> Fais l'exercice **avant** d'ouvrir le corrigé. Le corrigé propose *une* bonne réponse, pas *la seule*.

### Exercice 1 — Définir 3 KPI SMART

Pour chacun des 3 besoins métier ci-dessous, rédige **un KPI complet** : nom, formule, type (leading/lagging), granularité, fréquence, cible. Vérifie qu'il est SMART.

- **Besoin A** — Une enseigne de prêt-à-porter du Nord (5 magasins) constate que « certains magasins vendent bien mais ne gagnent pas d'argent ».
- **Besoin B** — Un site e-commerce de matériel de jardin dépense beaucoup en publicité et veut savoir « si ça vaut le coup ».
- **Besoin C** — Un entrepôt logistique près de Lille reçoit des plaintes clients sur des retards de livraison.

<details>
<summary>👉 Voir le corrigé de l'exercice 1</summary>

**Besoin A — le vrai problème est la rentabilité, pas le volume.**

| Élément | Valeur |
|---|---|
| Nom | Taux de marge brute par magasin |
| Formule | (CA − coût des marchandises vendues) / CA × 100 |
| Type | Lagging (résultat) |
| Granularité | Par magasin (puis par rayon en détail) |
| Fréquence | Mensuelle |
| Cible | ≥ 32 %, seuil d'alerte < 28 % |

*Pourquoi :* « vendre bien » = CA élevé, mais la rentabilité dépend de la **marge**. On compare la marge entre magasins pour repérer ceux qui bradent. SMART : spécifique (par magasin), mesurable (formule), atteignable (32 % réaliste en textile), pertinent (répond à « ne gagnent pas d'argent »), temporel (mensuel).

**Besoin B — « ça vaut le coup » = rentabilité de l'acquisition.**

| Élément | Valeur |
|---|---|
| Nom | Ratio LTV / CAC |
| Formule | (panier moyen × fréquence d'achat × durée de vie client) / (dépenses marketing / nb nouveaux clients) |
| Type | Lagging |
| Granularité | Par canal d'acquisition (Google Ads, Facebook…) |
| Fréquence | Mensuelle |
| Cible | ≥ 3 |

*Pourquoi :* le CAC seul ne suffit pas (« cher » n'est mauvais que si le client ne rapporte pas assez). Le ratio LTV/CAC répond directement à « est-ce que ça vaut le coup ». On peut aussi proposer un **leading** complémentaire : le **CTR des campagnes**, pour agir avant la fin du mois.

**Besoin C — la plainte = retard, donc fiabilité de livraison.**

| Élément | Valeur |
|---|---|
| Nom | Taux de service OTIF (livré complet et à l'heure) |
| Formule | Commandes livrées complètes ET dans les délais / total commandes × 100 |
| Type | Lagging |
| Granularité | Par jour / par transporteur |
| Fréquence | Hebdomadaire (suivi quotidien possible) |
| Cible | ≥ 95 % |

*Leading complémentaire :* taux de rupture de stock (une rupture cause un retard → indicateur avancé du futur OTIF).

</details>

### Exercice 2 — Maquetter un tableau de bord

Une directrice régionale d'une enseigne de bricolage (8 magasins dans les Hauts-de-France) te demande un tableau de bord pour son **point hebdomadaire**. Elle veut « voir d'un coup d'œil comment vont les magasins et où agir ».

1. Liste **5 à 7 KPI** pertinents et range-les en 2 niveaux (vue direction / vue détail).
2. Dessine le **zoning** de la page (en ASCII ou sur papier) en respectant la hiérarchie visuelle.

<details>
<summary>👉 Voir le corrigé de l'exercice 2</summary>

**1. Sélection et niveaux**

*Vue direction (en haut, synthèse) :*
- CA régional de la semaine + écart vs semaine N-1 (lagging)
- Taux de marge brute régional (lagging)
- Panier moyen régional (lagging)

*Vue détail (en bas) :*
- CA par magasin (barres) — pour voir *où* ça se passe
- Évolution du CA régional sur 8 semaines (courbe)
- Top 5 / Flop 5 produits
- Taux de rupture de stock par magasin (leading — où il faut réagir)

On reste à 7 KPI : on résiste à l'envie d'ajouter le turnover, la météo, etc. (hors besoin).

**2. Zoning proposé**

```
┌────────────────────────────────────────────────────────────┐
│  Tableau de bord régional — Hauts-de-France   [Semaine ▼]   │
├──────────────────┬──────────────────┬──────────────────────┤
│  CA semaine      │  Taux de marge   │  Panier moyen        │
│  312 k€  ▲ +4 %  │  31,2 %  ▼ -1pt  │  47 €   ▲ +2 €      │
├──────────────────┴──────────────────┴──────────────────────┤
│  Évolution du CA régional (8 dernières semaines)            │
│      ╱╲      ╱                                              │
│     ╱  ╲___╱                                                │
├───────────────────────────┬────────────────────────────────┤
│  CA par magasin (barres)   │  Ruptures de stock / magasin   │
│  Lille  ████████           │  Roubaix  🔴 8 %               │
│  Lens   ██████             │  Lille    🟢 2 %               │
│  …                         │  …                             │
├───────────────────────────┴────────────────────────────────┤
│  Top 5 / Flop 5 produits de la semaine                     │
└────────────────────────────────────────────────────────────┘
```

*Justification :* les 3 cartes de synthèse en haut (zone la plus lue) répondent à « comment vont les magasins ». La courbe donne la tendance. Les barres par magasin + ruptures répondent à « où agir ». Couleur réservée aux alertes (rouge sur Roubaix). Lecture en Z respectée.

</details>

---

## Vidéos d'auto-formation

> Toutes les vidéos ci-dessous ont été vérifiées. En cas de lien mort, utilise le titre dans la recherche YouTube.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| C'est quoi un KPI ? Key Performance Indicator — Définition | Market Academy | 🇫🇷 FR | ~6 min | [Regarder](https://www.youtube.com/watch?v=Da_nZwIDWLk) | La définition d'un KPI et comment le distinguer d'une simple statistique, avec exemples web/e-commerce. |
| Comprendre les KPI ou indicateurs clés de performance | Philippe Gattet (Xerfi Canal) | 🇫🇷 FR | ~9 min | [Regarder](https://www.youtube.com/watch?v=44U0pr9CczM) | Le rôle stratégique des KPI dans le pilotage d'entreprise et les pièges du « tout mesurer ». |
| KPI — Comment utiliser stratégiquement les indicateurs clés de performance | Recherche YouTube | 🇫🇷 FR | ~10 min | [Regarder](https://www.youtube.com/watch?v=WN-mQ6p3bvw) | Comment choisir et relier les KPI aux objectifs métier plutôt qu'empiler des chiffres. |
| Leading vs Lagging Indicators Explained | Recherche YouTube | 🇬🇧 EN | court | [Regarder](https://www.youtube.com/shorts/YoFX0kVEYwE) | La différence concrète entre indicateurs d'activité (avancés) et de résultat. |
| Tableau KPI Dashboard Design tutorial for Business | Recherche YouTube | 🇬🇧 EN | ~20 min | [Regarder](https://www.youtube.com/watch?v=I1fctnqk8Dk) | Concevoir un dashboard KPI étape par étape : choix des KPI, zoning, hiérarchie visuelle. |

*Si un lien ne fonctionne pas :* [recherche YouTube « KPI dashboard design best practices »](https://www.youtube.com/results?search_query=KPI+dashboard+design+best+practices) · [recherche « c'est quoi un KPI »](https://www.youtube.com/results?search_query=c%27est+quoi+un+kpi).

---

## Quiz — 5 QCM

**Q1.** Quelle affirmation distingue le mieux un KPI d'une métrique ?
- a) Un KPI est toujours un pourcentage
- b) Un KPI est une métrique reliée à un objectif et à une cible
- c) Une métrique se calcule, un KPI non
- d) Un KPI est forcément affiché dans un graphique

**Q2.** Dans la méthode SMART, que garantit le « M » pour un KPI ?
- a) Qu'il est motivant
- b) Qu'il existe une formule de calcul explicite à partir de données disponibles
- c) Qu'il est mensuel
- d) Qu'il est multidimensionnel

**Q3.** Lequel de ces indicateurs est un indicateur **leading** (d'activité) ?
- a) Le chiffre d'affaires du mois écoulé
- b) Le taux de turnover annuel
- c) Le taux de clic sur un emailing de campagne
- d) La marge brute trimestrielle

**Q4.** Lequel est une **vanity metric** typique ?
- a) Le taux de conversion
- b) Le nombre total de pages vues cumulées depuis le lancement
- c) La marge par client
- d) Le taux de rétention

**Q5.** Dans un tableau de bord bien structuré, la vue **direction** doit :
- a) Contenir le maximum de détail par produit
- b) Afficher 5 à 7 KPI synthétiques, lisibles en quelques secondes
- c) Être réservée aux opérationnels
- d) Empiler tous les KPI disponibles « au cas où »

<details>
<summary>👉 Voir les réponses</summary>

1. **b** — un KPI est une métrique *promue* parce que reliée à un objectif et une cible.
2. **b** — Mesurable = formule explicite sur des données disponibles.
3. **c** — le taux de clic se lit *avant* le résultat final ; les autres sont des résultats (lagging).
4. **b** — un cumul qui ne fait que monter et ne pilote aucune décision.
5. **b** — synthèse, lecture rapide, principe « synthèse → détail ».

</details>

---

## À retenir

- Un **KPI** = une **métrique reliée à un objectif et à une cible**, qui **déclenche une décision**. Sinon, ce n'est qu'un chiffre.
- Tout KPI se décrit par **5 éléments** : nom, **formule**, granularité, fréquence, cible (+ seuil d'alerte).
- **SMART** : Spécifique, Mesurable (la formule !), Atteignable, Relevant, Temporel.
- **Lagging** = résultat (« ça a marché ? »), **leading** = activité (« ça marche ? »). Un bon dashboard mêle les deux ; piloter avec les seuls lagging = conduire au rétroviseur.
- Connais les **KPI usuels par domaine** (ventes, marketing, RH, logistique) comme une boîte à outils — tu en choisis quelques-uns, tu ne les empiles pas.
- Structure ton dashboard en **pyramide** : vue direction (synthèse) → manager (tactique) → opérationnelle (détail).
- **Maquette d'abord** (zoning + hiérarchie visuelle), construis ensuite. Le sens de lecture en Z place l'essentiel en haut à gauche.
- Évite les 3 pièges : **trop de KPI**, les **vanity metrics**, les **KPI non actionnables**. Test ultime : *« si ce chiffre devient rouge, qu'est-ce que je fais ? »*
