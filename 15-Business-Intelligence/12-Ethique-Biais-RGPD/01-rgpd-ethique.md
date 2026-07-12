# 01 — RGPD, éthique & biais des données

| | |
|---|---|
| **Phase** | Phase 2 — BI avancée |
| **Durée estimée** | ~20 h |
| **Compétence visée** | **C12 — Garantir la conformité juridique et éthique d'un projet data** (niveau 1) |
| **Pré-requis** | Module 1.x (manipulation d'un fichier clients, SQL de base), notions de tableur, savoir décrire une source de données |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Expliquer** ce qu'est une donnée personnelle et reconnaître quand le RGPD s'applique à un jeu de données.
2. **Identifier** la base légale, la finalité et la durée de conservation d'un traitement, et repérer ce qui est interdit.
3. **Distinguer** anonymisation et pseudonymisation, et savoir laquelle te sort (ou non) du RGPD.
4. **Détecter** les principaux biais (sélection/représentativité, confirmation, biais algorithmique) dans un jeu de données ou une analyse.
5. **Auditer** un mini-projet data sous l'angle conformité + éthique, et proposer des corrections.
6. **Intégrer** une démarche de sobriété numérique dans tes analyses.

---

## Pourquoi c'est vital pour le Data Analyst

Tu vas passer ta vie professionnelle les mains dans des fichiers clients : noms, e-mails, historiques d'achat, adresses de livraison, paniers abandonnés. **Ces données ne t'appartiennent pas** : elles appartiennent aux personnes concernées, et l'entreprise n'en est que la gardienne.

Concrètement, en tant que DA :

- **Tu manipules les données les plus sensibles de l'entreprise.** Une requête trop large, un export envoyé au mauvais destinataire, un dashboard public qui laisse fuiter des e-mails → c'est une violation de données.
- **Tu produis des analyses qui orientent des décisions** (qui on cible, à qui on refuse une promo, quels clients on « score »). Un biais dans tes données = une décision injuste à grande échelle.
- **La sanction est réelle.** La CNIL peut infliger jusqu'à **20 millions d'euros ou 4 % du chiffre d'affaires mondial annuel**, et elle publie régulièrement des sanctions (y compris contre des PME du retail).
- **C'est un argument d'embauche.** Un DA qui sait dire « attention, là on n'a pas la base légale pour faire ça » ou « cet échantillon n'est pas représentatif » vaut beaucoup plus cher qu'un DA qui sort un joli graphique faux.

> **À retenir d'emblée :** la conformité n'est PAS le travail du seul DPO ou du juriste. Le DA est en **première ligne** parce que c'est lui qui touche la donnée brute.

---

## Le RGPD expliqué simplement

Le **RGPD** (Règlement Général sur la Protection des Données, *GDPR* en anglais) est un règlement européen en vigueur depuis le **25 mai 2018**. En France, c'est la **CNIL** (Commission Nationale de l'Informatique et des Libertés) qui le contrôle.

### Qu'est-ce qu'une donnée personnelle ?

Une **donnée personnelle** = toute information qui permet d'identifier une personne physique, **directement ou indirectement**.

| Directement identifiant | Indirectement identifiant |
|---|---|
| Nom, prénom | Numéro client |
| Adresse e-mail | Adresse IP |
| Numéro de téléphone | Identifiant de cookie |
| Numéro de sécurité sociale | Plaque d'immatriculation |
| Photo du visage | Combinaison « code postal + âge + sexe » |

> **Point clé qui piège tout le monde :** même sans nom, **un croisement de plusieurs colonnes peut ré-identifier quelqu'un**. Un fichier « code postal 59820 + femme + née en 1991 + a acheté 14 fois » peut ne désigner qu'une seule personne. Donc supprimer la colonne « nom » ne suffit JAMAIS à rendre un fichier anonyme.

Certaines données sont dites **sensibles** et bénéficient d'une protection renforcée (en principe interdites de traitement, sauf exceptions) : **origine ethnique, opinions politiques, religion, santé, orientation sexuelle, données biométriques, appartenance syndicale.**

### Les grands principes (à connaître par cœur)

| Principe | Ce que ça veut dire pour toi, DA | Exemple retail |
|---|---|---|
| **Finalité** | On collecte pour un but **précis, explicite et légitime**, défini à l'avance. | On a collecté les e-mails « pour la livraison ». On ne peut pas s'en servir « pour de la pub » sans nouvelle base. |
| **Minimisation** | On ne garde que les données **strictement nécessaires** à la finalité. | Pour analyser le panier moyen par magasin, tu n'as PAS besoin du nom du client. N'extrais pas ce dont tu n'as pas besoin. |
| **Exactitude** | Les données doivent être justes et à jour. | Un client qui s'est désabonné doit être réellement retiré de la liste de ciblage. |
| **Limitation de conservation** | On fixe une **durée**, après quoi on supprime ou on anonymise. | Données de prospects non clients : souvent **3 ans** après le dernier contact (recommandation CNIL). |
| **Intégrité & confidentialité** | Données sécurisées (accès restreint, chiffrement). | Pas de fichier clients en clair sur un Drive partagé ouvert à tous. |
| **Licéité, loyauté, transparence** | La personne sait ce qu'on fait de ses données. | Mention claire au moment de la collecte, pas de collecte cachée. |
| **Responsabilité (*accountability*)** | On doit pouvoir **prouver** qu'on respecte tout ça. | Registre des traitements, documentation de tes exports. |

### La base légale : as-tu le DROIT de traiter ?

Tout traitement doit reposer sur **au moins une** des 6 bases légales du RGPD. Les 3 qui reviennent le plus en retail :

- **Le consentement** — la personne a dit « oui » de façon libre, spécifique, éclairée et univoque (case à cocher NON pré-cochée). C'est la base de la **prospection commerciale par e-mail** vers des particuliers.
- **L'exécution d'un contrat** — nécessaire pour livrer une commande, gérer un compte client. (On a le droit de garder l'adresse de livraison parce que sans elle, pas de colis.)
- **L'intérêt légitime** — l'entreprise a un intérêt réel, mis en balance avec les droits des personnes (ex. mesure d'audience non intrusive, lutte contre la fraude). À justifier et documenter.

Les 3 autres : **obligation légale** (ex. facturation), **mission d'intérêt public**, **sauvegarde des intérêts vitaux**.

> **Encadré — Erreur courante n°1**
> « On a les e-mails des clients, donc on peut leur envoyer notre newsletter promo. »
> **FAUX** dans le cas général. L'e-mail collecté pour la **livraison** (base : contrat) ne donne pas le droit de faire de la **prospection** (base : consentement, en B2C). Mauvaise finalité = traitement illicite. (Exception : produits/services *analogues* à un client existant, sous conditions strictes et avec opt-out à chaque envoi.)

### Les droits des personnes

Toute personne peut exercer ces droits, et l'entreprise doit répondre (en principe **sous 1 mois**) :

- **Droit d'accès** — « quelles données avez-vous sur moi ? »
- **Droit de rectification** — corriger une info erronée.
- **Droit à l'effacement** (« droit à l'oubli ») — faire supprimer ses données.
- **Droit d'opposition** — refuser un traitement (ex. la prospection).
- **Droit à la limitation** — geler le traitement le temps d'une contestation.
- **Droit à la portabilité** — récupérer ses données dans un format réutilisable.

> **Pour toi, DA :** quand un client exerce son droit à l'effacement, il faut le retirer de **TOUS** tes jeux de données, y compris tes exports « de travail », tes fichiers Excel locaux et tes tableaux de bord. C'est souvent là que ça coince.

### Anonymisation vs pseudonymisation (LE piège du DA)

| | **Pseudonymisation** | **Anonymisation** |
|---|---|---|
| Principe | On remplace les identifiants par un code, mais une **table de correspondance** permet de revenir en arrière. | On rend la ré-identification **impossible**, même en croisant avec d'autres données. |
| Réversible ? | **Oui** (avec la clé). | **Non**, jamais. |
| Toujours du RGPD ? | **OUI** — reste une donnée personnelle. | **NON** — sort du champ du RGPD. |
| Exemple | `client_4827` au lieu de « Marie Dubois », avec un fichier liant 4827 ↔ Marie. | Statistiques agrégées : « 312 clients du magasin de Lille, panier moyen 47 € ». |

> **Encadré — Erreur courante n°2**
> « J'ai remplacé les noms par des numéros, donc le fichier est anonyme et je peux en faire ce que je veux. »
> **FAUX.** C'est de la **pseudonymisation** : tant qu'une table de correspondance existe (ou qu'on peut ré-identifier par croisement), c'est **toujours** une donnée personnelle soumise au RGPD. L'anonymisation vraie est **techniquement difficile** : il faut résister aux attaques par individualisation, corrélation et inférence (critères du G29/CEPD).

---

## L'éthique des données

Le RGPD dit ce qui est **légal**. L'éthique dit ce qui est **acceptable et juste**. Les deux ne se recouvrent pas toujours : on peut être 100 % conforme au RGPD et faire quelque chose de moralement douteux (ex. exploiter une faille psychologique pour pousser à l'achat).

Trois piliers à garder en tête :

- **Consentement réel** — pas de cases pré-cochées, pas de *dark patterns* (boutons « Tout accepter » en gros vert, « Refuser » caché en gris). La CNIL sanctionne ces pratiques.
- **Transparence** — la personne comprend ce qu'on fait. Si tu dois cacher ton analyse à tes clients par peur de leur réaction, c'est un signal d'alerte éthique.
- **Loyauté & non-discrimination** — ne pas se servir des données pour défavoriser un groupe (ex. afficher des prix plus élevés selon le quartier ou le type d'appareil).

> **Le test du « titre de presse » :** demande-toi « est-ce que je serais à l'aise si mon analyse faisait la une du journal local ? ». Si la réponse est non, repense ton approche.

---

## Les biais des données

Un **biais** est une distorsion systématique qui fait que tes données ou ton analyse ne reflètent pas la réalité. Le danger : un biais ne se voit pas dans un beau graphique. Il faut le chercher activement.

### Biais de sélection / représentativité

L'échantillon analysé n'est **pas représentatif** de la population sur laquelle on veut conclure.

- **Exemple retail :** on lance un sondage de satisfaction par **e-mail**. Réponses majoritairement de clients jeunes, connectés et plutôt contents. On en conclut « nos clients sont satisfaits à 90 % ». **Faux** : les mécontents et les clients âgés/peu connectés n'ont pas répondu (**biais de non-réponse** + **biais de couverture**).
- **Exemple e-commerce :** on analyse les ventes du seul site web et on décide la stratégie de TOUS les magasins, alors que la clientèle en magasin physique a un profil très différent.
- **Survivorship bias (biais du survivant) :** on analyse uniquement les clients **actifs** pour comprendre la fidélité, en oubliant tous ceux qui sont déjà partis — c'est-à-dire exactement ceux qui auraient expliqué le churn.

### Biais de confirmation

On (in)consciemment cherche, sélectionne ou interprète les données qui **confirment ce qu'on croyait déjà**.

- **Exemple :** le directeur marketing est convaincu que « la promo du Black Friday est un succès ». L'analyste filtre les KPIs qui le montrent (chiffre d'affaires brut en hausse) et passe sous silence ceux qui dérangent (marge en chute, retours produits en explosion, cannibalisation des ventes de décembre).
- **Mécanisme :** on s'arrête de creuser dès qu'un chiffre va dans notre sens, et on creuse à l'infini quand il nous contredit.

### Biais algorithmique

Quand un modèle ou un système automatisé reproduit, voire **amplifie**, une discrimination présente dans les données d'entraînement.

- **Exemple historique célèbre :** un outil de tri de CV entraîné sur 10 ans de recrutements majoritairement masculins a appris à **pénaliser** les CV contenant le mot « féminin » ou des écoles de filles. Le modèle n'était pas « méchant » : il a juste reproduit le passé.
- **Exemple retail :** un score d'attribution de réductions entraîné sur l'historique finit par ne jamais cibler certains quartiers (parce qu'ils achetaient historiquement moins) → on prive durablement ces clients d'offres → cercle vicieux.
- **Règle d'or :** *garbage in, garbage out* — un algorithme entraîné sur des données biaisées produira des décisions biaisées, avec en plus un vernis de « neutralité mathématique » qui les rend plus difficiles à contester.

> **Encadré — Erreur courante n°3**
> « C'est l'algorithme qui a décidé, ce n'est pas de notre faute / c'est objectif. »
> **FAUX.** Un algorithme n'est jamais neutre : il hérite des biais de ses données et des choix de ceux qui l'ont conçu. La responsabilité reste **humaine**.

> **Encadré — Erreur courante n°4**
> Confondre **corrélation** et **causalité**. « Les clients qui ont la carte fidélité dépensent plus, donc la carte fait dépenser plus. » Peut-être que les gros acheteurs prennent juste plus souvent la carte. Un biais classique qui fausse les recommandations.

---

## Méthode : auditer un projet data

Une checklist simple à dérouler sur n'importe quel projet d'analyse. Pose-toi ces questions **dans l'ordre** :

**A. Côté conformité (RGPD)**
1. **Y a-t-il des données personnelles ?** (Attention aux identifiants indirects et aux croisements.)
2. **Quelle est la finalité ?** Est-elle compatible avec celle de la collecte initiale ?
3. **Quelle base légale ?** (consentement, contrat, intérêt légitime…)
4. **Minimisation :** ai-je extrait uniquement les colonnes nécessaires ? Puis-je travailler sur des données pseudonymisées/agrégées ?
5. **Conservation :** la durée est-elle respectée ? Y a-t-il des vieux exports à supprimer ?
6. **Sécurité :** qui a accès à mon fichier de travail ? Est-il chiffré / dans un espace restreint ?
7. **Droits :** si quelqu'un demande l'effacement, suis-je capable de le retirer de mes jeux ?

**B. Côté éthique & biais**
8. **Représentativité :** mon échantillon couvre-t-il bien la population sur laquelle je vais conclure ?
9. **Biais de confirmation :** ai-je cherché aussi les chiffres qui me **contredisent** ?
10. **Impact :** mon analyse peut-elle défavoriser un groupe de personnes ? Passerait-elle le « test du titre de presse » ?
11. **Transparence :** mes hypothèses et les limites de mes données sont-elles documentées dans le rendu ?

> **Bonne pratique :** documente ces réponses dans une petite section « Limites et conformité » de ton rapport ou de ton dashboard. Ça te protège et ça inspire confiance.

---

## L'impact environnemental des données (sobriété numérique)

Les données ont un **coût écologique réel** : stockage permanent, transferts réseau, calculs sur serveurs (refroidissement, électricité). Le numérique représente une part croissante des émissions mondiales de gaz à effet de serre.

Le réflexe **« je collecte tout, on verra plus tard »** est à la fois un risque RGPD (contraire à la minimisation) ET un gouffre environnemental.

Gestes concrets de DA sobre :

- **Ne collecter et ne stocker que l'utile** (la minimisation RGPD sert aussi la planète : deux victoires d'un coup).
- **Supprimer les données et les exports périmés** (les « data sombres » dorment sur les serveurs et consomment pour rien).
- **Limiter les requêtes lourdes inutiles** : éviter de recalculer un dashboard énorme toutes les 5 minutes si une fois par jour suffit.
- **Privilégier l'agrégation** : un tableau de stats agrégées pèse mille fois moins qu'un export ligne à ligne.
- **Optimiser ses requêtes SQL** (filtrer tôt, sélectionner les colonnes nécessaires) : plus rapide ET moins gourmand.

> **Idée clé :** sobriété, conformité et performance vont dans le **même sens**. Le DA qui minimise ses données est plus rapide, plus conforme et plus écolo.

---

## Exercices et cas pratiques

> Essaie de répondre **avant** d'ouvrir le corrigé. Justifie toujours ta réponse avec un principe du RGPD ou un type de biais.

### Cas 1 — La newsletter détournée

Une enseigne de prêt-à-porter du Nord a collecté les e-mails de ses clients **uniquement pour le suivi de livraison**. Le service marketing veut maintenant envoyer une newsletter promo hebdomadaire à toute cette base, sans rien demander de plus.

**Question :** est-ce conforme au RGPD ? Quel(s) principe(s) sont en jeu ? Que faut-il faire ?

<details>
<summary>Voir le corrigé</summary>

**Non conforme.** Le problème central est la **finalité** : les e-mails ont été collectés pour la **livraison** (base légale : exécution du contrat). Les utiliser pour de la **prospection commerciale** est une **nouvelle finalité incompatible**, qui nécessite en B2C le **consentement** des personnes.

Sont aussi en jeu : la **transparence** (les clients n'ont pas été informés de cet usage) et la **loyauté**.

**À faire :** recueillir un consentement spécifique (campagne d'opt-in, case non pré-cochée), n'envoyer la newsletter qu'aux clients ayant accepté, et inclure un lien de **désinscription** à chaque envoi.
*(Nuance : une exception « produits analogues » existe pour les clients déjà acheteurs, mais elle est encadrée et exige un opt-out clair — la solution propre reste le consentement.)*
</details>

### Cas 2 — Le sondage trop optimiste

Pour mesurer la satisfaction, tu envoies un questionnaire **par e-mail** à ta base clients. Tu obtiens 8 % de réponses, dont 91 % de clients satisfaits. Le directeur veut communiquer « 91 % de clients satisfaits ».

**Question :** quel(s) biais identifies-tu ? La conclusion est-elle valide ?

<details>
<summary>Voir le corrigé</summary>

Plusieurs **biais de sélection / représentativité** :
- **Biais de non-réponse :** seuls 8 % ont répondu. Les mécontents et les indifférents répondent souvent moins (ou plus, selon les cas) — l'échantillon n'est pas représentatif.
- **Biais de couverture :** le canal e-mail exclut les clients sans adresse renseignée, âgés ou peu connectés.
- **Biais d'auto-sélection :** ceux qui prennent le temps de répondre ne sont pas un sous-groupe neutre.

**Conclusion non valide telle quelle.** On ne peut pas dire « 91 % des clients sont satisfaits », au mieux « 91 % **des 8 % de répondants** se déclarent satisfaits ». À corriger : varier les canaux, relancer, comparer le profil des répondants à celui de la base totale, et **afficher la limite** dans le rendu.
</details>

### Cas 3 — Le fichier « anonymisé »

Un collègue te transmet un fichier d'analyse en disant « c'est bon, je l'ai anonymisé, j'ai juste enlevé la colonne Nom ». Le fichier contient : `code_postal`, `date_de_naissance`, `sexe`, `magasin_habituel`, `montant_total_dépensé`.

**Question :** ce fichier est-il vraiment anonyme ? Peux-tu le partager librement ?

<details>
<summary>Voir le corrigé</summary>

**Non, il n'est pas anonyme.** Supprimer le nom ne suffit pas : la combinaison `code_postal + date_de_naissance + sexe` est un **quasi-identifiant** qui permet souvent de **ré-identifier une seule personne** (attaque par individualisation/corrélation).

C'est au mieux de la **pseudonymisation imparfaite** → cela reste une **donnée personnelle soumise au RGPD**. Tu ne peux pas le partager librement.

**Pour le rendre réellement anonyme** ou utilisable : agréger (par tranche d'âge plutôt que date exacte, par grande zone plutôt que code postal précis), supprimer les colonnes inutiles à l'analyse (**minimisation**), et ne le diffuser que sous forme de **statistiques agrégées**.
</details>

### Cas 4 — Le score qui exclut

Tu construis un score pour décider à quels clients envoyer un bon de réduction de bienvenue, entraîné sur l'historique des achats. Tu remarques que le modèle ne propose presque jamais d'offre aux clients de deux quartiers précis.

**Question :** quel biais ? Quels risques ? Que fais-tu ?

<details>
<summary>Voir le corrigé</summary>

C'est un **biais algorithmique** alimenté par un **biais des données historiques** : ces quartiers achetaient historiquement moins → le modèle apprend à les ignorer → ils ne reçoivent jamais d'offre → ils achètent encore moins. **Cercle vicieux auto-réalisateur**, et risque de **discrimination indirecte** (le quartier peut corréler avec l'origine ou le niveau social — données sensibles par ricochet).

**Risques :** discrimination, atteinte à l'image, sanction potentielle, et… mauvaise décision business (on s'interdit de conquérir ces clients).

**À faire :** auditer les écarts entre groupes, retirer ou neutraliser les variables proxy discriminantes, tester l'équité du score, garder un **contrôle humain** sur les décisions, et documenter la démarche.
</details>

### Cas 5 — L'audit express (synthèse)

On te confie cette mission : « Extrais-moi tous les clients qui ont acheté du vin l'an dernier, avec nom, e-mail, adresse et historique de santé renseigné lors du programme fidélité, pour qu'on les recible. Garde le fichier sur ton ordi, on en aura besoin pendant des années. »

**Question :** déroule la checklist d'audit (section 6) et liste tout ce qui cloche.

<details>
<summary>Voir le corrigé</summary>

Au moins **cinq** problèmes :

1. **Donnée sensible (santé)** : l'historique de santé est une catégorie **particulière**, en principe **interdite** de traitement à des fins marketing. À **exclure** absolument.
2. **Minimisation non respectée** : pour un reciblage, le nom + l'adresse postale ne sont pas tous nécessaires (l'e-mail peut suffire). On extrait trop.
3. **Finalité / base légale** : recibler suppose une base (consentement pour la prospection). Pas évoqué → à vérifier.
4. **Sécurité** : « garde le fichier sur ton ordi » = stockage non sécurisé, hors espace contrôlé. À refuser ; travailler dans l'environnement sécurisé de l'entreprise.
5. **Conservation** : « pendant des années » sans durée définie viole la **limitation de conservation**. Il faut fixer une durée et un effacement.

**Posture pro attendue :** ne pas exécuter tel quel, alerter le responsable / DPO, proposer une version conforme (sans santé, minimisée, sécurisée, avec base légale et durée).
</details>

---

## Vidéos d'auto-formation

> Liens vérifiés au moment de la rédaction. Si un lien ne fonctionne plus, utilise le lien de recherche fourni pour retrouver une vidéo équivalente.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| RGPD / GDPR : la FAQ avec la CNIL | Cookie connecté (avec la CNIL) | FR | ~10 min | https://www.youtube.com/watch?v=OUMGp3HHel4 | Les questions concrètes que se posent les entreprises sur le RGPD, répondues avec la CNIL. |
| Comprendre le RGPD (dossier + vidéos officielles) | CNIL | FR | variable | https://www.cnil.fr/fr/comprendre-le-rgpd | La source de référence : principes, droits, bases légales, expliqués par l'autorité elle-même. |
| GDPR Explained Simply — all you need to know in 5 minutes | (voir recherche) | EN | ~5 min | https://www.youtube.com/watch?v=tBEMNcMihl4 | Vue d'ensemble rapide et claire du GDPR/RGPD en anglais. |
| Biais algorithmiques dans l'IA (article + vidéos) | DataBird | FR | lecture | https://www.data-bird.co/blog/biais-algorithimiques-ia | Typologie des biais algorithmiques avec exemples, pensé pour les métiers de la data. |
| Recherche : « biais des données / data bias expliqué » | YouTube (recherche) | FR/EN | — | https://www.youtube.com/results?search_query=biais+des+donn%C3%A9es+data+bias+expliqu%C3%A9 | Pour explorer d'autres vidéos récentes sur les biais des données et des algorithmes. |

---

## Quiz (5 QCM)

**Q1.** Lequel de ces éléments n'est **pas** une donnée personnelle au sens du RGPD ?
- A. Une adresse IP
- B. Un numéro client interne
- C. Le chiffre d'affaires total agrégé d'un magasin
- D. Une combinaison code postal + date de naissance + sexe

**Q2.** Tu remplaces les noms par des codes `client_001`, mais tu gardes une table reliant chaque code à la vraie identité. Tu as fait de la :
- A. Anonymisation (le fichier sort du RGPD)
- B. Pseudonymisation (le fichier reste soumis au RGPD)
- C. Minimisation
- D. Portabilité

**Q3.** Un sondage par e-mail recueille surtout des réponses de clients jeunes et satisfaits. De quel biais s'agit-il principalement ?
- A. Biais de confirmation
- B. Biais algorithmique
- C. Biais de sélection / représentativité
- D. Aucun, c'est un échantillon valide

**Q4.** Quelle base légale est en principe requise pour envoyer une newsletter promotionnelle à des particuliers ?
- A. L'intérêt légitime, toujours
- B. Le consentement
- C. L'exécution du contrat de livraison
- D. Aucune, l'e-mail suffit

**Q5.** Parmi ces gestes, lequel sert **à la fois** le RGPD et la sobriété numérique ?
- A. Tout collecter au cas où
- B. Conserver tous les exports indéfiniment
- C. Minimiser les données et supprimer les exports périmés
- D. Recalculer le dashboard toutes les minutes

<details>
<summary>Voir les réponses</summary>

**Q1 : C.** Une statistique **agrégée** (CA total d'un magasin) n'identifie aucune personne → pas une donnée personnelle. Les trois autres sont des identifiants directs ou indirects.

**Q2 : B.** Tant qu'une table de correspondance existe, c'est de la **pseudonymisation** → toujours une donnée personnelle soumise au RGPD.

**Q3 : C.** C'est un **biais de sélection / représentativité** (couverture + non-réponse + auto-sélection).

**Q4 : B.** En B2C, la prospection par e-mail repose sur le **consentement** (case non pré-cochée). Le contrat de livraison ne couvre pas la prospection.

**Q5 : C.** Minimiser et supprimer l'inutile = **minimisation RGPD** ET **sobriété**. Les autres options vont à l'inverse des deux.
</details>

---

## À retenir

- **Donnée personnelle = tout ce qui identifie quelqu'un, directement ou indirectement** (attention aux croisements). Supprimer le nom ne suffit pas.
- **Tout traitement a besoin d'une finalité, d'une base légale et d'une durée de conservation.** La finalité de collecte n'est pas extensible à volonté.
- **Minimisation** : n'extrais et ne garde que le strict nécessaire — c'est bon pour le RGPD, la sécurité, la performance **et** la planète.
- **Pseudonymisation ≠ anonymisation.** Seule l'anonymisation (irréversible) sort du RGPD ; elle est difficile à atteindre.
- **Les biais ne se voient pas dans un beau graphique** : cherche-les activement (représentativité, confirmation, biais algorithmique).
- **Un algorithme n'est jamais neutre** : il hérite des biais de ses données. La responsabilité reste humaine.
- **Légal ≠ éthique.** Applique le « test du titre de presse ».
- **Le DA est en première ligne.** Savoir dire « attention, là on ne peut pas » fait partie du métier.

---

*Source réglementaire de référence : [CNIL — Comprendre le RGPD](https://www.cnil.fr/fr/comprendre-le-rgpd). Vérifie toujours les recommandations à jour sur le site de la CNIL.*
