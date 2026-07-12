# 01 — Accompagner une équipe métier

| | |
|---|---|
| **Phase** | Phase 2 — Mettre en place une solution de BI pour un traitement analytique avancé |
| **Durée indicative** | ~25 h |
| **Compétences visées** | **C11 niv.2** (formaliser une problématique métier dans un cahier des charges) · **C15 niv.2** (présenter et argumenter les résultats auprès d'une équipe métier) |
| **Pré-requis** | Avoir construit au moins un tableau de bord (modules 2.3 et 2.4), connaître les bases de la restitution (Phase 1), maîtriser les notions de KPI et d'indicateur |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Rédiger un cahier des charges** d'un projet data : objectifs, périmètre, livrables, parties prenantes, indicateurs de succès, contraintes.
2. **Préparer et animer un atelier de cadrage** avec une équipe métier : ordre du jour, techniques de questionnement, gestion du temps et de la parole.
3. **Reformuler et valider un besoin** exprimé par un métier, pour éviter le « malentendu fondateur » d'un projet data.
4. **Accompagner l'appropriation d'un tableau de bord** : former les utilisateurs, produire une documentation utile, organiser le support.
5. **Présenter des résultats de façon argumentée et adaptée** à ton public : justifier le choix des indicateurs, expliciter les décisions que le dashboard permet de prendre.
6. **Formuler des recommandations actionnables** et **gérer les désaccords** et le feedback avec une posture de conseil.

---

## Pourquoi c'est utile au Data Analyst

Un Data Analyst ne travaille jamais seul dans son coin. Tu produis des analyses **pour quelqu'un** : un responsable de magasin, une équipe marketing, une direction. Ta valeur ne se mesure pas à la beauté de tes graphiques, mais à **la décision qu'ils déclenchent**.

Or, la première cause d'échec d'un projet data n'est pas technique, c'est **un besoin mal compris**. On construit un tableau de bord magnifique… qui répond à une question que personne ne se posait. Le travail de cadrage (cahier des charges + atelier) est donc le moment où tu sécurises 80 % de la réussite du projet.

De la même façon, un dashboard que personne ne sait lire ou n'ose ouvrir est un dashboard mort. Savoir **accompagner l'appropriation** et **restituer de façon argumentée** transforme une livraison technique en outil réellement adopté.

> En entretien, on te demandera rarement « écris-moi du DAX ». On te demandera souvent « raconte-moi un projet où tu as travaillé avec une équipe métier ». **C'est ce module qui te prépare à ça.**

C'est exactement le niveau 2 attendu par la certification : tu ne te contentes plus d'exécuter une demande (niv.1), tu **co-construis** le besoin et tu **défends** tes choix.

---

## Contenu

### Le cahier des charges d'un projet data

Le cahier des charges (CdC) est le **contrat moral** entre toi et le métier. Il dit *ce qu'on va faire, pour qui, jusqu'où, et comment on saura que c'est réussi*. Il n'a pas besoin d'être un pavé de 40 pages : 3 à 6 pages bien faites valent mieux qu'un document que personne ne lit.

#### Les 7 rubriques d'un cahier des charges data

| Rubrique | Question à laquelle elle répond | Exemple (retail Nord) |
|---|---|---|
| **1. Contexte & enjeu** | Pourquoi ce projet maintenant ? | « Les ventes du rayon textile de nos 12 magasins des Hauts-de-France stagnent ; la direction veut comprendre où agir. » |
| **2. Objectifs** | Qu'est-ce qu'on veut obtenir ? (formulés en verbe d'action) | « Identifier les 3 magasins et les 5 familles de produits les plus en retard, et suivre l'effet des promos. » |
| **3. Périmètre (et hors-périmètre)** | Jusqu'où va-t-on, et où s'arrête-t-on ? | Inclus : ventes 2023-2025, 12 magasins, rayon textile. Exclu : e-commerce, prévision de la demande. |
| **4. Parties prenantes** | Qui décide, qui utilise, qui fournit la donnée ? | Sponsor : DG. Utilisateurs : 12 responsables magasin. Source : service informatique (export caisse). |
| **5. Livrables** | Qu'est-ce qu'on remet concrètement ? | 1 tableau de bord Power BI, 1 doc utilisateur, 1 session de formation 1 h. |
| **6. Indicateurs de succès** | Comment saura-t-on que c'est réussi ? | Dashboard utilisé par ≥ 10 des 12 responsables, décision de réassort prise au comité mensuel. |
| **7. Contraintes & planning** | Délais, budget, outils, RGPD, jalons | Livraison sous 4 semaines, outil imposé Power BI, pas de données nominatives client. |

> **Astuce — la règle SMART pour les objectifs.** Un bon objectif est **S**pécifique, **M**esurable, **A**tteignable, **R**éaliste, **T**emporel. « Améliorer les ventes » n'est pas un objectif, c'est un vœu. « Identifier d'ici fin mars les 5 produits textiles en sous-performance dans les 12 magasins » en est un.

> ⚠️ **Erreur courante n°1 — confondre le besoin et la solution.**
> Le métier dit souvent « je veux un graphique en camembert des ventes par magasin ». Ça, c'est une **solution** qu'il imagine. Ton job est de remonter au **besoin** : « pour décider quoi exactement ? ». Peut-être qu'un classement (top/flop) répond mieux qu'un camembert. **Note la demande, mais cadre toujours sur le besoin.**

> ⚠️ **Erreur courante n°2 — oublier le hors-périmètre.**
> Ne lister que ce qui est inclus laisse la porte ouverte au *scope creep* (« puisque tu y es, tu pourrais aussi ajouter… »). Écrire explicitement ce qui est **exclu** protège ton planning et ta crédibilité.

#### Mini-modèle de cahier des charges (à réutiliser)

```
CAHIER DES CHARGES — [Nom du projet]
Auteur : [toi]   Date : [jj/mm/aaaa]   Version : 1.0

1. CONTEXTE & ENJEU
   - Situation actuelle :
   - Problème / opportunité :

2. OBJECTIFS (SMART)
   - Objectif principal :
   - Objectifs secondaires :

3. PÉRIMÈTRE
   - Inclus :
   - Hors-périmètre :

4. PARTIES PRENANTES
   | Rôle | Nom | Attente principale |

5. LIVRABLES
   - [ ] ...

6. INDICATEURS DE SUCCÈS
   - ...

7. CONTRAINTES & PLANNING
   - Délais / jalons :
   - Outils / données / RGPD :

VALIDATION : signé/validé par [sponsor] le [date]
```

---

### Animer un atelier de cadrage

L'atelier de cadrage, c'est la réunion où tu **remplis le cahier des charges avec le métier**, pas tout seul devant ton écran. Bien mené, il dure 1 h à 2 h et fait gagner des semaines.

#### Avant l'atelier — la préparation (le vrai travail)

- **Identifie les bons participants** : le sponsor (qui décide), 2-3 utilisateurs finaux, la personne qui connaît la donnée. Trop de monde tue l'atelier.
- **Prépare un ordre du jour** envoyé à l'avance, avec une durée par point.
- **Prépare tes questions ouvertes** (voir plus bas). Tu n'arrives jamais les mains vides.
- **Définis un objectif de sortie clair** : « à la fin, on aura validé les objectifs et la liste des KPI. »

#### Pendant l'atelier — le déroulé type

| Temps | Étape | Ce que tu fais |
|---|---|---|
| 5 min | **Cadrage** | Rappeler l'objectif de l'atelier, les règles (« on note tout, on tranche à la fin »). |
| 15 min | **Écoute du besoin** | Laisser le métier raconter ses irritants. Tu écoutes, tu notes, tu ne juges pas. |
| 20 min | **Questionnement & approfondissement** | Creuser avec des questions ouvertes pour passer de la solution au besoin réel. |
| 15 min | **Reformulation & validation** | Tu reformules, le métier corrige. On valide objectifs et périmètre. |
| 15 min | **Priorisation** | Que veut-on en V1 ? Qu'est-ce qui peut attendre ? |
| 10 min | **Synthèse & suite** | Récapituler les décisions, qui fait quoi, prochaine étape. |

#### La boîte à outils du questionnement

La compétence centrale ici, c'est **savoir poser des questions**. Quelques techniques :

- **Questions ouvertes** : « Qu'est-ce qui vous empêche aujourd'hui de décider du réassort ? » (vs question fermée oui/non).
- **Les 5 pourquoi** : remonter à la cause racine. « Pourquoi voulez-vous ce graphique ? — Pour voir les ventes. — Pourquoi ? — Pour repérer les baisses. — Pourquoi ? — Pour réagir avant la fin du mois. » → le vrai besoin est une **alerte mensuelle**, pas un graphique.
- **La reformulation** : « Si je comprends bien, votre priorité c'est X plutôt que Y, c'est ça ? » → fait verbaliser l'accord ou le désaccord.
- **Le QQOQCP** (Quoi, Qui, Où, Quand, Comment, Pourquoi) pour ne rien oublier.

> ⚠️ **Erreur courante n°3 — parler technique en atelier.**
> « On fera une jointure sur la table fait_ventes avec une mesure DAX en time intelligence » : le métier décroche. En atelier, **zéro jargon technique**. Tu parles besoin, décision, indicateur — pas implémentation.

> ⚠️ **Erreur courante n°4 — ne pas écrire la synthèse.**
> Un atelier sans compte-rendu écrit, c'est un atelier dont les conclusions seront contestées dans 3 semaines. Envoie un **compte-rendu** sous 48 h : décisions prises, points en suspens, prochaines actions.

---

### Reformuler et valider le besoin

Entre « ce que le métier dit », « ce qu'il veut dire » et « ce dont il a besoin », il y a souvent un gouffre. Ton rôle de conseil est de **réduire cet écart** avant d'écrire la moindre requête.

La technique de base : **reformuler puis faire valider**.

1. Tu écoutes le besoin brut.
2. Tu le **reformules avec tes mots** : « Donc l'objectif, c'est de repérer chaque mois les magasins qui décrochent pour décider d'une action commerciale, exact ? »
3. Le métier **confirme ou corrige**. Chaque correction est une information précieuse.
4. Tu **écris** la formulation validée dans le cahier des charges.

> **Astuce.** La phrase magique : *« Pour être sûr d'avoir bien compris… »* suivie de ta reformulation. Elle désamorce les malentendus sans donner l'impression de remettre en cause l'interlocuteur.

---

### Accompagner l'appropriation d'un tableau de bord

Livrer un dashboard ≠ projet terminé. Sans accompagnement, l'adoption chute. Trois leviers :

#### a) Former les utilisateurs

- **Session courte (30-60 min)**, en montrant les **cas d'usage réels** (« voici comment trouver tes 3 produits en baisse »), pas chaque bouton.
- Pars de **leurs questions métier**, pas de la structure technique.
- Fais-les **manipuler** eux-mêmes pendant la session (apprentissage actif).

#### b) Documenter

Une bonne doc utilisateur tient en 1-2 pages et contient :

- **À quoi sert ce tableau de bord** (en une phrase).
- **Définition de chaque KPI** : formule en langage simple + source + maille de calcul. (« Taux de marge = (CA − coût d'achat) / CA, calculé par magasin et par mois. »).
- **Comment lire** les filtres principaux.
- **Qui contacter** en cas de souci, et **à quelle fréquence** les données se rafraîchissent.

> **Astuce — le dictionnaire des indicateurs.** C'est LE livrable qui évite 90 % des disputes futures (« ton CA ne correspond pas au mien ! »). Définir noir sur blanc chaque indicateur, c'est définir une vérité commune.

#### c) Organiser le support et le suivi

- Prévois un **point à J+15 / J+30** : « est-ce que vous l'utilisez ? qu'est-ce qui bloque ? ».
- Mets en place un canal de questions (mail, Teams).
- Accepte que le dashboard **évolue** : la V1 n'est jamais la dernière.

> ⚠️ **Erreur courante n°5 — la formation « visite guidée ».**
> Cliquer sur tous les boutons en récitant les fonctionnalités endort la salle. Forme par **scénario d'usage** : une vraie question métier → comment le dashboard y répond.

---

### Restituer de façon argumentée (niv.2)

Au niveau 2, tu ne te contentes pas de **montrer** un résultat, tu le **défends**. Présenter, c'est répondre à trois questions dans la tête de ton auditoire : *Est-ce que je comprends ? Est-ce que j'y crois ? Qu'est-ce que je fais maintenant ?*

#### Structure d'une restitution efficace

1. **Le message d'abord** (pyramide inversée) : commence par la conclusion. « Le magasin de Lille décroche de 18 % sur le textile, je recommande de revoir l'assortiment. » Puis tu déroules les preuves.
2. **Justifie le choix des indicateurs.** « J'ai retenu le taux de marge plutôt que le CA seul, parce qu'un magasin peut faire beaucoup de CA en cassant ses prix. » → tu montres que tes KPI ne sont pas arbitraires.
3. **Explicite les décisions possibles.** Un bon dashboard ne dit pas seulement *quoi*, il prépare le *et alors ?*. « Ce que cet écran permet : repérer en 10 secondes les 3 rayons à réapprovisionner en priorité. »
4. **Adapte au public.** Une direction veut le *quoi décider* en 3 minutes ; une équipe opérationnelle veut le *comment* en détail. Même analyse, deux niveaux de profondeur.

#### Justifier un indicateur — la grille

Pour chaque KPI présenté, sois prêt à répondre :
- **Pourquoi celui-ci** et pas un autre ?
- **Comment** est-il calculé (source, maille, période) ?
- **Quelle décision** il éclaire ?

> **Astuce.** Prépare toujours la question piège : *« Et ce chiffre, il vient d'où ? »*. Connaître la source et le calcul de chacun de tes indicateurs, c'est la base de ta crédibilité.

---

### Formuler des recommandations actionnables

Une analyse sans recommandation, c'est un diagnostic sans ordonnance. Une recommandation **actionnable** répond à : *qui fait quoi, quand, et quel résultat attendu ?*

| Recommandation faible | Recommandation actionnable |
|---|---|
| « Il faut améliorer les ventes textile. » | « Réduire le stock du rayon textile homme de Roubaix de 20 % d'ici juin et redéployer la surface au rayon enfant, qui surperforme de 15 %. » |
| « Le magasin de Lille a un problème. » | « Programmer une visite terrain à Lille en avril pour comprendre la baisse de fréquentation observée le week-end. » |

**Le format recommandé** : *Constat → Cause probable → Action proposée → Impact attendu*.

> Exemple complet (retail Nord) :
> - **Constat** : le panier moyen baisse de 7 % le samedi à Dunkerque.
> - **Cause probable** : ruptures de stock sur les produits d'appel en fin de semaine.
> - **Action** : ajuster la commande du jeudi (+15 % sur le top 10).
> - **Impact attendu** : +3 à 5 % de panier moyen le week-end sous 1 mois.

> ⚠️ **Erreur courante n°6 — recommander au-delà de tes données.**
> Si ta donnée montre une corrélation, ne conclus pas à une cause certaine. Dis « cause probable », propose une vérification. Une recommandation crédible **assume ses limites**.

---

### Gérer les désaccords et le feedback (posture de conseil)

Le désaccord n'est pas un échec : c'est de l'information. La posture de conseil consiste à **écouter sans te braquer** et à ramener la discussion sur les faits.

Quelques réflexes :

- **« Ton chiffre est faux. »** → « Intéressant, regardons ensemble la source et le calcul. » (tu ne défends pas ton ego, tu vérifies ensemble la donnée).
- **« Ça ne sert à rien. »** → « Quel serait pour vous l'usage qui le rendrait utile ? » (tu transformes la critique en besoin).
- **Désaccord entre deux métiers** → tu reviens au cahier des charges et aux objectifs validés ensemble.
- **Feedback négatif** → remercie, reformule, note, ne promets pas tout de suite. « Merci, je note. Je regarde la faisabilité et je reviens vers vous. »

> **Posture clé.** Tu n'es ni un simple exécutant, ni le détenteur de la vérité. Tu es un **conseiller** : tu apportes l'éclairage de la donnée, le métier garde la décision. Cette posture « je propose, tu décides » désamorce la plupart des tensions.

---

## Exercices

> Travaille de préférence sur le contexte fil rouge : une **enseigne de prêt-à-porter de 12 magasins dans les Hauts-de-France** dont les ventes textile stagnent.

### Exercice 1 — Rédiger un cahier des charges

À partir de la demande brute ci-dessous, rédige un cahier des charges complet (les 7 rubriques) en réutilisant le mini-modèle de la section 3.1.

> *Demande brute du directeur régional :* « Je veux un truc qui me montre quels magasins marchent et lesquels marchent pas, pour le prochain comité dans un mois. Et faut que ce soit dans Power BI, on n'a que ça. On ne touche pas aux données clients, c'est sensible. »

<details>
<summary>Voir un corrigé possible</summary>

**1. Contexte & enjeu** — Les ventes textile des 12 magasins des Hauts-de-France stagnent. La direction régionale doit décider, au comité mensuel, où concentrer les actions commerciales.

**2. Objectifs (SMART)** — Objectif principal : *identifier d'ici 4 semaines les 3 magasins les plus en retard sur le textile et les familles de produits concernées, en vue du comité mensuel.* Secondaires : suivre l'évolution mois par mois ; comparer chaque magasin à la moyenne régionale.

**3. Périmètre** — Inclus : ventes textile, 12 magasins, données 2023-2025 mensuelles. Hors-périmètre : e-commerce, prévision de la demande, données nominatives clients.

**4. Parties prenantes** — Sponsor/décideur : directeur régional. Utilisateurs : 12 responsables magasin + direction régionale. Fournisseur de données : service informatique (export caisse).

**5. Livrables** — 1 tableau de bord Power BI (vue région + vue magasin) ; 1 dictionnaire des indicateurs ; 1 session de formation 45 min ; 1 doc utilisateur 2 pages.

**6. Indicateurs de succès** — Dashboard présenté et utilisé au comité mensuel ; au moins une décision d'action commerciale prise sur sa base ; ≥ 10/12 responsables y accèdent.

**7. Contraintes & planning** — Livraison sous 4 semaines (jalons : CdC validé S1, V1 S3, formation S4). Outil imposé : Power BI. RGPD : **aucune donnée nominative client**.

*Points d'attention du correcteur :* avoir traduit « un truc qui montre » en objectif SMART, avoir explicité le hors-périmètre, avoir transformé « on ne touche pas aux données clients » en contrainte RGPD.
</details>

---

### Exercice 2 — Préparer un atelier de cadrage

Tu vas animer l'atelier de cadrage de 1 h 30 avec le directeur régional, deux responsables de magasin et une personne du service informatique. Prépare :
1. un ordre du jour minuté,
2. cinq questions ouvertes que tu poseras,
3. l'objectif de sortie de l'atelier.

<details>
<summary>Voir un corrigé possible</summary>

**Ordre du jour (1 h 30)**
- 0-10 min : accueil, objectif de l'atelier, règles.
- 10-30 min : écoute du besoin (chaque responsable raconte ses irritants).
- 30-55 min : approfondissement par questions ouvertes.
- 55-75 min : reformulation + validation des objectifs et du périmètre.
- 75-85 min : priorisation V1 / plus tard.
- 85-90 min : synthèse, qui fait quoi, prochaine étape.

**Cinq questions ouvertes**
1. « Aujourd'hui, comment décidez-vous des actions commerciales sur un magasin en retard ? »
2. « Qu'est-ce qui vous manque pour décider plus vite ou mieux ? »
3. « Quand vous dites "un magasin qui marche", vous le mesurez comment : CA, marge, fréquentation ? »
4. « À quelle fréquence avez-vous besoin de regarder ces chiffres ? »
5. « Si vous ne deviez avoir qu'un seul écran à ouvrir le lundi matin, il montrerait quoi ? »

**Objectif de sortie** — Sortir avec les objectifs validés, la liste des 4-5 indicateurs prioritaires et le périmètre confirmé (12 magasins, textile, hors données clients).

*Note :* la question 3 sert à révéler l'indicateur réel (souvent la marge, pas le CA) ; la question 5 force la priorisation.
</details>

---

### Exercice 3 — Formuler des recommandations actionnables

Voici trois constats issus de ton analyse. Transforme chacun en recommandation **actionnable** au format *Constat → Cause probable → Action → Impact attendu*.

- a) Le magasin de Valenciennes fait −22 % sur le rayon textile femme depuis 6 mois.
- b) Les promos « -30 % » génèrent du volume mais font chuter la marge globale de 4 points.
- c) Le rayon enfant surperforme de +15 % partout, mais occupe une petite surface.

<details>
<summary>Voir un corrigé possible</summary>

**a)** *Constat* : −22 % textile femme à Valenciennes sur 6 mois. *Cause probable* : assortiment inadapté ou concurrence locale nouvelle. *Action* : audit terrain de l'assortiment femme à Valenciennes en avril + comparaison avec un magasin comparable performant. *Impact attendu* : plan de réassort sous 6 semaines visant à réduire l'écart de moitié.

**b)** *Constat* : les promos -30 % font +volume mais -4 pts de marge. *Cause probable* : promotions trop profondes sur des produits déjà demandés. *Action* : tester une promo -15 % ciblée sur les seuls produits à rotation faible le mois prochain. *Impact attendu* : maintien du volume avec érosion de marge limitée à -1 pt.

**c)** *Constat* : rayon enfant +15 %, faible surface. *Cause probable* : offre sous-dimensionnée par rapport à la demande. *Action* : étendre la surface du rayon enfant de 20 % dans les 3 magasins où il surperforme le plus, dès le réagencement de juin. *Impact attendu* : +8 à 10 % de CA enfant sur ces magasins en un trimestre.

*Critère de réussite :* chaque reco contient une action datée et un impact chiffré ; les causes sont annoncées comme « probables », pas comme certitudes.
</details>

---

### Exercice 4 — Justifier le choix d'un indicateur

Lors de la restitution, un responsable te demande : *« Pourquoi tu nous montres le taux de marge et pas simplement le chiffre d'affaires ? Le CA, c'est plus parlant pour nous. »* Rédige ta réponse argumentée (4-6 phrases).

<details>
<summary>Voir un corrigé possible</summary>

« Bonne remarque, le CA reste affiché dans la vue détaillée. J'ai mis le taux de marge en indicateur principal parce que deux magasins peuvent faire le même chiffre d'affaires tout en gagnant très différemment : l'un peut gonfler son CA en cassant ses prix, l'autre vendre moins mais plus rentable. Si on pilote seulement au CA, on risque de récompenser un magasin qui détruit sa marge. Le taux de marge montre la santé réelle du rayon et oriente mieux la décision de réassort. Cela dit, on regarde toujours les deux ensemble : un magasin à forte marge mais petit CA peut juste être trop petit. »

*Ce qu'on valorise :* tu justifies le choix par la décision qu'il éclaire, tu ne dénigres pas la demande du métier, tu proposes de garder les deux indicateurs.
</details>

---

### Exercice 5 — Gérer un désaccord en restitution

En plein comité, le directeur d'un magasin pointé en baisse réagit : *« Tes chiffres sont faux, mon magasin se porte très bien, tu racontes n'importe quoi. »* Rédige ta réponse (posture de conseil) et explique en une phrase ta stratégie.

<details>
<summary>Voir un corrigé possible</summary>

**Réponse :** « Je comprends que ça surprenne. Regardons ensemble : ces chiffres viennent de l'export caisse sur janvier-mars, calculés en marge par rayon. Si vous avez une autre source ou si une période vous semble manquante, je veux bien la croiser avec vous après le comité — l'objectif n'est pas de pointer un magasin, c'est de repérer où on peut aider. »

**Stratégie :** ne pas défendre mon ego mais ramener au fait (source + calcul), transformer l'attaque en vérification commune et rappeler l'objectif collectif du projet.
</details>

---

## Vidéos d'auto-formation

> Les liens marqués *(recherche)* ouvrent une **recherche YouTube** : choisis la vidéo la plus récente et la mieux notée. Cette précaution évite tout lien mort.

| Titre / sujet | Chaîne / source | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Rédiger un cahier des charges (projet / data) | Recherche YouTube | FR | ~10-20 min | [Rechercher](https://www.youtube.com/results?search_query=r%C3%A9diger+cahier+des+charges+projet+data) | Structurer objectifs, périmètre, livrables d'un projet |
| Animer un atelier de cadrage / atelier collaboratif | Recherche YouTube | FR | ~10-20 min | [Rechercher](https://www.youtube.com/results?search_query=animer+atelier+de+cadrage+projet+facilitation) | Préparer et faciliter un atelier avec une équipe |
| Recueillir et reformuler le besoin métier | Recherche YouTube | FR | ~10-15 min | [Rechercher](https://www.youtube.com/results?search_query=recueil+du+besoin+m%C3%A9tier+reformulation+chef+de+projet) | Questionnement, reformulation, validation du besoin |
| Communicating data insights / presenting to stakeholders | Recherche YouTube | EN | ~10-20 min | [Rechercher](https://www.youtube.com/results?search_query=data+analyst+presenting+insights+to+stakeholders) | Restituer et argumenter face à un public métier |
| Stakeholder management for data analysts | Recherche YouTube | EN | ~10-15 min | [Rechercher](https://www.youtube.com/results?search_query=stakeholder+management+for+data+analysts) | Gérer les parties prenantes, désaccords, feedback |

---

## Quiz (5 QCM)

**Q1.** Quel élément est **indispensable** dans un cahier des charges pour se protéger du *scope creep* ?
- A) Un diagramme de Gantt détaillé
- B) Le hors-périmètre explicitement écrit
- C) La liste des couleurs du dashboard
- D) Le budget exact en euros

**Q2.** Le métier te dit « je veux un camembert des ventes par magasin ». Quelle est la bonne posture ?
- A) Le construire immédiatement, c'est la demande
- B) Refuser, le camembert est une mauvaise visualisation
- C) Remonter au besoin : « pour décider quoi exactement ? »
- D) Proposer un autre outil que Power BI

**Q3.** Pendant un atelier de cadrage, tu dois éviter :
- A) De poser des questions ouvertes
- B) De reformuler le besoin
- C) D'employer du jargon technique (jointures, DAX…)
- D) D'envoyer un ordre du jour à l'avance

**Q4.** Une recommandation **actionnable** contient typiquement :
- A) Uniquement un constat chiffré
- B) Constat, cause probable, action proposée, impact attendu
- C) La requête SQL utilisée
- D) Une promesse de résultat garanti à 100 %

**Q5.** En restitution, un responsable conteste tes chiffres devant tout le monde. La meilleure réaction est :
- A) Défendre fermement que tes chiffres sont justes
- B) Reconnaître que tu t'es sûrement trompé
- C) Proposer de vérifier ensemble la source et le calcul, et rappeler l'objectif commun
- D) Ignorer la remarque et continuer la présentation

<details>
<summary>Voir les réponses</summary>

1. **B** — Écrire le hors-périmètre cadre les attentes et évite l'ajout incontrôlé de demandes.
2. **C** — Le camembert est une *solution* imaginée ; ton rôle est de cadrer sur le *besoin* (la décision à prendre).
3. **C** — En atelier, on parle besoin/décision/indicateur, jamais implémentation technique.
4. **B** — Le format constat → cause probable → action → impact rend la reco exploitable ; une reco crédible n'offre jamais de garantie à 100 %.
5. **C** — Posture de conseil : ramener au fait (source/calcul), transformer l'attaque en vérification commune, rappeler l'objectif collectif.
</details>

---

## À retenir

- Le **cahier des charges** (7 rubriques) est le contrat moral du projet : objectifs SMART, périmètre **et hors-périmètre**, parties prenantes, livrables, critères de succès.
- L'**atelier de cadrage** se prépare : bons participants, ordre du jour, questions ouvertes, objectif de sortie. En atelier : **zéro jargon**, beaucoup de reformulation, un compte-rendu sous 48 h.
- **Reformuler puis faire valider** est l'outil n°1 pour réduire l'écart entre ce que le métier dit et ce dont il a besoin.
- L'**appropriation** se travaille : former par cas d'usage, documenter (surtout le **dictionnaire des indicateurs**), assurer un suivi.
- **Restituer au niv.2**, c'est argumenter : justifier chaque indicateur (pourquoi / comment / quelle décision) et adapter la profondeur au public.
- Une **recommandation actionnable** dit qui fait quoi, quand, pour quel impact — et assume ses limites (« cause probable »).
- Face au désaccord, garde la **posture de conseil** : tu proposes l'éclairage de la donnée, le métier décide.
