# Brief S14 — Auditer la conformité RGPD et les biais des données clients de NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S14 — Phase 2 : Sécuriser & fiabiliser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, Jupyter Notebook, Markdown, Git/GitHub |
| **Prérequis** | [Éthique, biais & RGPD](../../../15-Business-Intelligence/12-Ethique-Biais-RGPD/) · [Collecte de données (RGPD by design)](../../../15-Business-Intelligence/14-Collecte-Donnees/) · [Analyse exploratoire (EDA)](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Depuis vos premiers audits de qualité, l'équipe data a grandi : le tableau de bord de pilotage se construit semaine après semaine, et l'enseigne commence à exploiter finement sa base clients. Vous y travaillez aux côtés du responsable BI, de la contrôleuse de gestion et, désormais, d'une déléguée à la protection des données récemment nommée.

### Le problème

La direction marketing veut passer à l'action. Forte des premières analyses, elle prépare une **campagne de fidélisation ciblée** : exporter la liste des « meilleurs clients » (les plus récents, fréquents et dépensiers) avec leur e-mail, pour un envoi promotionnel. Dans le même mouvement, la direction souhaite **élargir l'accès aux tableaux de bord** au-delà de la cellule data.

Deux signaux d'alerte remontent. D'abord, la déléguée à la protection des données rappelle que la base contient des **données personnelles** (noms, e-mails, villes, historiques d'achat) et qu'aucun export marketing ne peut se faire sans un contrôle de conformité. Ensuite, le responsable BI s'interroge : et si les analyses qui désignent les « meilleurs clients » **reproduisaient des biais injustes** — en survalorisant toujours les mêmes profils, les mêmes territoires, et en oubliant discrètement une partie de la clientèle ?

Lancer une campagne sur des données non conformes, ou sur des analyses biaisées, exposerait NordRetail à un risque réglementaire **et** à une erreur stratégique. Votre mission de la semaine intervient donc **avant** l'export : produire un **audit de conformité et d'équité** sur l'usage envisagé des données clients.

### La question centrale

Toute la semaine, chaque vérification que vous menez doit contribuer à répondre à la question que la direction vous a posée :

> **« Peut-on lancer cette campagne ciblée sur nos clients en toute conformité — et sans reproduire de biais injustes envers une partie d'entre eux ? »**

### Les données

Deux tables issues du modèle de données de l'enseigne, plus une table de contexte territorial :

- [`../data/Dim_Client.csv`](../data/Dim_Client.csv) — la **fiche client** : `client_id`, `prenom`, `nom`, `ville`, `segment` (Particulier / Premium / Professionnel), `date_inscription`, `email`.
- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — les **ventes détaillées** rattachées à chaque client : `vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`.
- [`../data/Dim_Magasin.csv`](../data/Dim_Magasin.csv) — le **référentiel des points de vente** (`ville`, `type`, `surface_m2`…) pour situer la répartition territoriale.

Ces fichiers ne sont pas anonymisés : c'est précisément l'objet de votre audit. Vous travaillez en **lecture seule** — on ne modifie jamais la source.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Cartographier les données personnelles** d'un jeu de données réel : distinguer données personnelles, données sensibles et données non personnelles, et qualifier leur niveau de sensibilité.
- **Conduire un audit de conformité** d'un cas d'usage au regard des grands principes de protection des données : base légale, finalité, minimisation, durée de conservation, droits des personnes.
- **Proposer des mesures de mise en conformité** concrètes et réalistes (anonymisation, pseudonymisation, agrégation, contrôle d'accès, information des personnes, registre de traitement).
- **Détecter et objectiver des biais** dans un jeu de données et une méthode d'analyse : représentativité, données manquantes, effet de renforcement d'un ciblage.
- **Formuler des correctifs d'équité** et restituer l'ensemble dans une note d'audit exploitable par un lecteur non spécialiste.

## Données fournies

Les trois fichiers sont déjà présents dans le dépôt (dossier [`99-Brief/Data-Analyst/data/`](../data/)). Aucune donnée n'est à télécharger. Toute manipulation (jointure, agrégation, pseudonymisation d'exemple) reste dans votre notebook : la source demeure intacte.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit sa propre note d'audit. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage du cas d'usage, SANS analyse chiffrée (J1)

Avant de coder, appropriez-vous le cas. Reformulez avec vos mots ce que la direction marketing veut faire : quelles personnes sont concernées, quelles données sont mobilisées, dans quel but ? Ouvrez `Dim_Client.csv` dans un tableur pour un premier regard : parmi les colonnes présentes, lesquelles permettent d'**identifier une personne**, directement ou indirectement ? Un `client_id` seul identifie-t-il quelqu'un ? Et combiné à la `ville` et au `segment` ? Interrogez-vous sur la finalité annoncée : envoyer un e-mail promotionnel à un client fidèle, est-ce une raison suffisante pour exporter son identité complète, ou pourrait-on faire autrement ? Notez ces questions ouvertes — elles structureront votre audit. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Cartographie des données personnelles (J1-J2)

Chargez `Dim_Client.csv` et `Faits_Ventes.csv` avec pandas. Passez chaque colonne en revue et classez-la : **donnée personnelle directe** (permet d'identifier seule, ex. `nom`, `email`), **donnée personnelle indirecte** (identifie par recoupement, ex. `ville` + `date_inscription`), ou **donnée non personnelle** (ex. `quantite`, `montant`). Pour chacune, notez un niveau de sensibilité. Produisez un **tableau de cartographie** clair. Combien de clients uniques la base contient-elle ? Un identifiant technique comme `client_id` reste-t-il une donnée personnelle dès lors qu'il pointe vers une personne réelle ? Justifiez.

### Phase 3 — Audit de conformité du cas « export marketing » (J2-J3)

Instruisez le cas précis : *la direction veut exporter la liste des meilleurs clients (récence, fréquence, montant dépensé) avec leur e-mail pour une campagne promotionnelle*. Passez cinq points clés au crible, preuves chiffrées à l'appui quand c'est possible :

- **Base légale** : sur quel fondement peut-on envoyer ce message (consentement ? intérêt légitime ?) ? A-t-on trace d'un accord des clients ?
- **Finalité** : l'usage envisagé correspond-il à ce pour quoi les données ont été collectées ?
- **Minimisation** : a-t-on besoin du `nom` **et** du `prenom` **et** de l'`email` pour cette campagne, ou de moins ?
- **Durée de conservation** : depuis quand certains clients sont-ils inscrits (regardez `date_inscription`) ? Des comptes inactifs très anciens devraient-ils encore figurer ?
- **Droits des personnes** : comment un client exercerait-il ses droits d'accès, d'opposition ou d'effacement ?

Concluez sans ambiguïté : le cas est-il **conforme** ou **non conforme** en l'état, et pourquoi ?

### Phase 4 — Détection des biais et correctifs (J3-J4)

Analysez maintenant l'**équité** de l'analyse qui désigne les « meilleurs clients ». Identifiez **au moins deux biais** et étayez-les par des chiffres tirés des données :

- **Biais de représentativité** : la répartition des clients par `ville` ou par `segment` est-elle équilibrée ? Certains territoires ou segments (Premium vs Particulier) sont-ils sur- ou sous-représentés ? Croisez avec `Dim_Magasin.csv`.
- **Biais des exclus** : les clients sans achat récent, ou absents de `Faits_Ventes.csv`, sortent-ils mécaniquement du ciblage ? Combien sont-ils ?
- **Effet de renforcement** : cibler toujours les mêmes « champions » creuse-t-il l'écart avec le reste de la clientèle campagne après campagne ?

Pour chaque biais retenu, proposez une **parade réaliste** : rééquilibrage, segment de contrôle, indicateur de couverture, vigilance sur les clients exclus.

### Phase 5 — Note d'audit, correctifs et mise en ligne (J5)

Assemblez une **note d'audit** structurée qui répond frontalement à la question centrale. Rassemblez vos correctifs en un **plan d'action** distinguant les mesures de mise en conformité (pseudonymisation ou anonymisation de `nom`/`email`, agrégation, contrôle d'accès au rapport, mention d'information, registre de traitement) et les correctifs d'équité. Illustrez au moins une mesure par un exemple de pseudonymisation dans le notebook (sans jamais republier de données réelles identifiantes). Nettoyez votre notebook (il doit s'exécuter de haut en bas sans erreur), soignez le README, et poussez le tout sur GitHub. La note s'adresse à la direction et à la déléguée à la protection des données : claire, argumentée, exploitable par un non-spécialiste.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : cartographie des données personnelles, audit des cinq points de conformité avec conclusion argumentée, au moins deux biais objectivés par des chiffres, plan de correctifs conformité + équité, note d'audit et dépôt public à jour.

### Pour aller plus loin (bonus)

- Implémentez une **pseudonymisation réversible** (table de correspondance séparée) et une **anonymisation** (agrégation ou suppression) sur un extrait, et comparez ce que chacune permet encore d'analyser.
- Calculez un **indicateur de couverture** de la campagne : quelle part de la clientèle, par ville et par segment, serait effectivement touchée par le ciblage « meilleurs clients » ?
- Esquissez une **fiche de registre de traitement** pour la campagne (finalité, données, base légale, durée, destinataires).

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `audit_rgpd_biais.ipynb` — notebook exécuté de bout en bout (cartographie, chiffres à l'appui de l'audit, détection des biais, exemple de pseudonymisation) ;
  - une **note d'audit** (`NOTE_AUDIT.md` ou PDF, 2 à 3 pages) structurée en quatre parties : cartographie des données personnelles · audit de conformité (conforme / non conforme + justification) · biais identifiés avec preuves chiffrées · plan de correctifs ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Un **tableau de cartographie des données personnelles** (colonne, type de donnée, sensibilité) — dans le notebook ou la note.

## Modalités d'évaluation

Évaluation en deux volets :

- **Note d'audit et notebook (60 %)** : rigueur de la cartographie, complétude de l'audit de conformité et justesse de la conclusion, solidité des biais démontrés par les chiffres, réalisme des correctifs.
- **Restitution orale (40 %)** : 10 minutes de présentation de l'audit à un « comité » (le formateur et un autre binôme jouant direction + déléguée à la protection des données) + 5 minutes de questions.

**Validation partielle** : un binôme dont la note n'est pas complètement finalisée mais dont la cartographie et l'audit de conformité sont structurés et argumentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Cartographier les données personnelles**
- Les données personnelles du jeu (directes et indirectes) sont identifiées et qualifiées.
- Chaque colonne est classée avec un niveau de sensibilité justifié.
- Le statut d'un identifiant technique rattaché à une personne est correctement discuté.

**Auditer la conformité**
- Les cinq points sont couverts : base légale, finalité, minimisation, durée de conservation, droits des personnes.
- Une conclusion claire (conforme / non conforme) est argumentée.
- Des mesures de mise en conformité concrètes et réalistes sont proposées.

**Détecter et corriger les biais**
- Au moins deux biais sont identifiés et étayés par des chiffres tirés des données.
- Chaque biais est rattaché à un risque métier ou éthique explicite.
- Une parade réaliste est proposée pour chaque biais.

**Restituer**
- La note d'audit répond explicitement à la question centrale.
- Elle est rédigée sans jargon, exploitable par un lecteur non spécialiste.
- Le dépôt GitHub public est complet (notebook exécutable + README).

## Ressources

- Module de cours — [Éthique, biais & RGPD](../../../15-Business-Intelligence/12-Ethique-Biais-RGPD/)
- Rappels — [Collecte de données (RGPD by design)](../../../15-Business-Intelligence/14-Collecte-Donnees/)
- Rappels — [Analyse exploratoire (EDA)](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/)
- CNIL — Les principes clés du RGPD : https://www.cnil.fr/fr/reglement-europeen-protection-donnees
- CNIL — Anonymisation & pseudonymisation : https://www.cnil.fr/fr/lanonymisation-de-donnees-personnelles
- Étape précédente du parcours — [Brief S06 — Audit & EDA des ventes](semaine-06-eda-ventes-nordretail.md)
</content>
</invoke>
