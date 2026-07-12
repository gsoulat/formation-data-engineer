# 01 — Restituer & présenter les résultats

| | |
|---|---|
| **Phase** | Phase 1 — Le tableau de bord |
| **Durée** | ~15 heures |
| **Compétence** | C15 (niveau 1) — Restituer les résultats d'une analyse de données à un public donné, en adaptant le discours, les supports et la forme de visualisation au commanditaire |
| **Pré-requis** | Modules 1.1 à 1.5 (cadrage du besoin, collecte, nettoyage, analyse exploratoire, premier tableau de bord). Savoir lire un graphique simple et avoir produit au moins une analyse chiffrée. |

> Tu as collecté, nettoyé, analysé. Tu as un tableau de bord qui marche. Et maintenant ? Si personne ne comprend ton travail, ou pire, si tout le monde l'a compris de travers, alors tout le reste n'a servi à rien. Ce module, c'est le « dernier kilomètre » du métier : transformer des chiffres en décision.

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

- **Structurer** un message data selon le schéma **contexte → analyse → recommandation**.
- **Adapter** ton discours et tes supports à trois types de public : direction, métier, technique.
- **Construire** une présentation claire avec une hiérarchie de l'information lisible (slides, titres, un message par slide).
- **Appliquer** les règles d'**accessibilité WCAG** à tes visualisations (contraste, daltonisme, titres explicites, alternatives textuelles).
- **Anticiper et gérer** les questions du commanditaire pendant une restitution.
- **Repérer et éviter** les erreurs de restitution les plus fréquentes (jargon, surcharge, graphiques trompeurs).

---

## Pourquoi c'est utile au Data Analyst

Un Data Analyst passe environ 80 % de son temps à collecter, nettoyer et analyser. Mais c'est sur les 20 % restants — la **restitution** — que se joue toute la valeur perçue de son travail. Une vérité dure du métier :

> **Une analyse non comprise = une analyse inutile.**

Concrètement, savoir restituer te sert à :

- **Faire prendre des décisions.** Un directeur ne lit pas une requête SQL ; il agit sur une recommandation claire.
- **Gagner en crédibilité.** Une présentation nette inspire confiance dans tes chiffres (même imparfaits).
- **Éviter les contresens coûteux.** Un graphique trompeur peut pousser à fermer le bon magasin.
- **Respecter la loi et l'éthique.** L'accessibilité n'est pas optionnelle : un dashboard public d'une collectivité ou d'une grande enseigne doit être lisible par tous, y compris les personnes daltoniennes ou malvoyantes (RGAA en France, dérivé des WCAG).
- **Valider ta certification.** La compétence C15 est évaluée à la **soutenance** du brief de phase. Ce module te prépare directement à ce passage.

---

## Contenu

### Le storytelling data : structurer un message

Le **data storytelling** est l'art de transformer des données brutes en un récit clair, structuré et compréhensible pour un public donné. Il combine **trois ingrédients** :

1. **Les données** — la base factuelle, tes chiffres vérifiés.
2. **La visualisation** — graphiques, indicateurs, qui rendent l'info lisible.
3. **La narration** — le fil qui donne du sens aux chiffres et guide l'interprétation.

Un tableau de chiffres seul ne raconte rien. Une jolie courbe sans message ne décide de rien. C'est la combinaison des trois qui fait agir.

#### La structure de base : contexte → analyse → recommandation

C'est le squelette de toute restitution réussie. Apprends-le par cœur.

| Étape | Question à laquelle tu réponds | Exemple retail Nord |
|---|---|---|
| **1. Contexte** | De quoi parle-t-on ? Pourquoi est-ce important maintenant ? | « Le chiffre d'affaires du magasin de Roubaix a baissé de 12 % au 1er trimestre 2026. » |
| **2. Analyse** | Qu'est-ce que les données révèlent ? | « La baisse vient à 80 % du rayon textile, concentrée le samedi, depuis l'ouverture d'un concurrent à 500 m. » |
| **3. Recommandation** | Que faut-il faire ? | « Tester une animation textile le samedi sur 6 semaines, et mesurer l'impact. » |

> **Le piège classique du débutant** : commencer par « voici comment j'ai fait » (la méthode), au lieu de « voici ce que j'ai trouvé » (le résultat). Le commanditaire veut le résultat d'abord. La méthode, c'est en annexe ou si on te le demande.

#### Le principe de la pyramide inversée

Comme un journaliste : **l'information la plus importante en premier.** Si ton auditoire ne retient qu'**une seule phrase**, laquelle veux-tu que ce soit ? Mets-la au début, répète-la à la fin.

> **Astuce du « So what ? »** : après chaque chiffre que tu présentes, demande-toi « et alors ? ». Si tu n'as pas de réponse, le chiffre n'a rien à faire dans ta présentation.

---

### Adapter le discours au public

Le **même résultat** se raconte de **trois façons différentes** selon qui t'écoute. C'est la compétence la plus sous-estimée du métier.

| Public | Ce qu'il veut | Niveau de détail | Vocabulaire | Format idéal |
|---|---|---|---|---|
| **Direction** | Décider vite. Impact business, € et %. | Très synthétique : 1 message, 3 chiffres max | Zéro jargon technique | 1 slide de synthèse, recommandation en haut |
| **Métier** (chef de rayon, marketing) | Comprendre pour agir sur le terrain | Moyen : le « pourquoi » concret | Vocabulaire métier (pas data) | Dashboard interactif, graphiques par rayon |
| **Technique** (autre analyste, DSI) | Vérifier la fiabilité, reproduire | Élevé : méthode, sources, limites | Jargon data OK | Documentation, requêtes, hypothèses |

**Exemple — un même résultat, trois discours (retail Nord) :**

- *À la direction :* « On perd 12 % de CA à Roubaix. Une action ciblée sur le textile peut récupérer la moitié. Budget estimé : 4 000 €. »
- *Au chef de rayon :* « Tes ventes textile chutent surtout le samedi depuis février. Le nouveau concurrent capte la clientèle famille. On teste une animation ? »
- *À l'équipe data :* « Baisse de 12 % du CA, p-value < 0,05 sur la corrélation avec l'ouverture concurrente. Données issues de la table `ventes_2026`, hors retours. Limite : pas de données de fréquentation piéton. »

> **Règle d'or** : tu ne dilues pas la vérité, tu changes le **niveau de zoom** et le **vocabulaire**. Les trois discours disent la même chose.

---

### Construire une présentation claire

#### Hiérarchie de l'information

Sur chaque slide, l'œil doit savoir où regarder en **3 secondes**. Hiérarchie type :

1. **Le titre** = le message (pas le sujet). Mauvais : « Ventes par rayon ». Bon : « Le textile explique 80 % de la baisse ».
2. **Le visuel principal** = un seul graphique qui prouve le titre.
3. **Le détail / la légende** = en plus petit, pour qui veut creuser.

#### Les règles d'une bonne slide

- **Un message par slide.** Si tu as deux idées, fais deux slides.
- **Le titre porte le message**, pas le thème. On doit pouvoir lire uniquement les titres et comprendre toute l'histoire.
- **Moins de texte = plus d'impact.** La slide n'est pas ton script ; c'est l'appui visuel. Le discours, c'est toi qui le portes.
- **Mets en valeur le chiffre clé** (couleur, taille) et grise le reste.
- **Numérote tes slides** et garde un fil narratif (contexte → analyse → reco).

#### Le « slide-titre = histoire » test

Imprime uniquement les titres de tes slides. Tu dois lire une histoire cohérente :
*« Le CA de Roubaix baisse → le textile en est la cause → le samedi est le pic → un concurrent vient d'ouvrir → testons une animation. »*
Si les titres seuls ne racontent rien, ta présentation n'est pas prête.

> **Encadré — Erreur courante n°1 : la surcharge**
> La slide « fourre-tout » avec 4 graphiques, 3 tableaux et un paragraphe. L'auditoire lit au lieu d'écouter, se perd, décroche. **Règle : un graphique, un message.** Le reste va en annexe.

---

### L'accessibilité WCAG appliquée à la dataviz (concret)

Les **WCAG** (Web Content Accessibility Guidelines) sont le standard international d'accessibilité. En France, le **RGAA** en est la déclinaison légale. Pour un Data Analyst, quatre règles concrètes suffisent à couvrir l'essentiel.

#### a) Le contraste de couleur

Le texte et les éléments importants doivent avoir un **ratio de contraste suffisant** avec le fond :

- **4,5:1** minimum pour le texte normal (critère WCAG AA).
- **3:1** pour le gros texte et les éléments graphiques.

Concrètement : du gris clair sur fond blanc, c'est illisible pour beaucoup de gens. **Teste tes contrastes** avec un outil gratuit comme le *WebAIM Contrast Checker* ou *Color Contrast Analyzer*.

#### b) Ne jamais coder l'information par la couleur seule

Environ **1 homme sur 12** (8 %) et 1 femme sur 200 sont daltoniens. La forme la plus courante (deutéranopie) rend difficile la distinction **rouge / vert**. Or le couple rouge/vert est le réflexe n°1 des débutants (rouge = mauvais, vert = bon)... et c'est exactement le pire choix.

**Solutions :**
- Ajoute un **second signal** en plus de la couleur : étiquette texte, forme, motif (hachures), icône (▲▼), ou position.
- Utilise une **palette adaptée au daltonisme** : par exemple la palette *Okabe-Ito*, ou les palettes *ColorBrewer* marquées « colorblind safe », ou *viridis*.
- **Teste ta dataviz** avec un simulateur de daltonisme (*Coblis*, ou l'extension *Color Oracle*). Si ton message disparaît en mode daltonien, refais ta palette.

#### c) Des titres et libellés explicites

- Chaque graphique a un **titre qui dit ce qu'il faut comprendre** (cf. 3.3).
- **Axes nommés** avec unités (€, %, nb).
- **Légende lisible**, ou mieux : libellés directement sur le graphique (étiquettes de séries) pour éviter l'aller-retour œil/légende.

#### d) Les alternatives textuelles

Une personne malvoyante utilise un **lecteur d'écran** qui ne « voit » pas ton graphique. Il faut donc :

- Un **texte alternatif** (`alt`) qui résume le message du graphique (« Histogramme montrant que le textile représente 80 % de la baisse du CA »), pas seulement « graphique ».
- Idéalement, le **tableau de données** accessible à côté ou en dessous, pour que l'info soit récupérable autrement que par l'image.

> **Encadré — Erreur courante n°2 : le rouge/vert seul**
> Un tableau de bord magasin « feu tricolore » (rouge/orange/vert) sans aucun autre repère. Pour un client ou un collègue daltonien, tout se ressemble. **Ajoute toujours un texte, un chiffre ou une icône en plus de la couleur.**

---

### Répondre aux questions du commanditaire

La restitution ne s'arrête pas à ton dernier mot. Le moment des questions est souvent **le plus décisif** — c'est là qu'on teste ta maîtrise.

**Avant** la présentation :
- **Anticipe les 5 questions probables.** « D'où viennent les données ? », « Sur quelle période ? », « Es-tu sûr de ce chiffre ? », « Combien ça coûte ? », « Et si on faisait X à la place ? »
- Prépare des **slides d'annexe** (back-up) pour les questions de détail.

**Pendant** :
- **Reformule la question** avant de répondre (tu gagnes du temps et tu vérifies que tu as compris).
- **Réponds court, puis développe** si on te le demande.
- Si tu ne sais pas : **dis-le.** « Je n'ai pas la donnée, je reviens vers vous demain. » C'est mille fois mieux qu'inventer. Ta crédibilité tient à ton honnêteté.
- Distingue **fait** (« le CA a baissé de 12 % ») et **interprétation** (« je pense que c'est dû au concurrent »). Ne présente jamais une hypothèse comme une certitude.

> **Encadré — Erreur courante n°3 : le faux expert**
> Inventer une réponse pour ne pas avoir l'air de ne pas savoir. Le commanditaire connaît son métier mieux que toi : il repérera le flou, et tu perdras toute ta crédibilité. **« Je ne sais pas, je vérifie » est une réponse professionnelle.**

> **Encadré — Erreur courante n°4 : le jargon**
> « J'ai fait un left join sur la dimension produit après avoir géré les NaN par imputation médiane. » → La direction décroche en 2 secondes. **Traduis tout en langage métier.** Garde le jargon pour les annexes techniques.

> **Encadré — Erreur courante n°5 : le graphique trompeur**
> Axe Y qui ne commence pas à zéro pour gonfler une variation, camembert à 12 parts illisible, échelle non linéaire, période choisie pour arranger le message... Même involontaire, c'est une faute. **Un graphique doit montrer la réalité, pas l'argument que tu veux faire passer.**

---

## Exercices

### Exercice 1 — Transformer une analyse en pitch de 3 minutes

**Contexte (retail Nord).** Tu as analysé les ventes d'une enseigne de prêt-à-porter avec 4 magasins (Lille, Roubaix, Tourcoing, Villeneuve-d'Ascq). Tes résultats bruts :

- CA total T1 2026 : 1,2 M€, en baisse de 7 % vs T1 2025.
- Roubaix : −12 %. Les 3 autres : stables (±1 %).
- À Roubaix, la baisse vient à 80 % du rayon textile femme.
- La baisse est concentrée le samedi (−25 % le samedi, stable les autres jours).
- Un concurrent (chaîne low-cost) a ouvert à 500 m de Roubaix en février 2026.
- Données : table `ventes`, hors retours et avoirs. Pas de données de fréquentation.

**Ta mission.** Rédige le **script d'un pitch de 3 minutes destiné à la direction**, structuré en contexte → analyse → recommandation. Puis liste les **3 titres de slides** que tu utiliserais.

<details>
<summary>Voir le corrigé</summary>

**Script de pitch (≈ 3 min, ton direction) :**

> **(Contexte — 30 s)** « Notre chiffre d'affaires du 1er trimestre est en baisse de 7 %, soit environ 90 000 € de moins qu'en 2025. Mais cette baisse n'est pas générale : un seul magasin la porte presque entièrement. »
>
> **(Analyse — 1 min 30)** « C'est Roubaix, qui chute de 12 %, quand les trois autres magasins sont stables. En creusant, deux faits clairs : d'abord, 80 % de cette baisse vient du rayon textile femme. Ensuite, elle est concentrée le samedi — moins 25 % ce jour-là, alors que les autres jours tiennent. Le point déclencheur le plus probable : un concurrent low-cost a ouvert à 500 mètres en février. On capte moins la clientèle famille du week-end. »
>
> **(Recommandation — 1 min)** « Je propose de tester une animation commerciale sur le textile femme, le samedi, pendant 6 semaines à Roubaix. Budget estimé : 4 000 €. On mesure l'effet sur le CA samedi avant/après. Si ça marche, on étend ; sinon, on aura appris à moindre coût. Une réserve d'honnêteté : je n'ai pas les données de fréquentation piétonne, donc le lien avec le concurrent est une hypothèse forte, pas une certitude. »

**3 titres de slides (qui racontent l'histoire seuls) :**
1. « CA en baisse de 7 % — mais un seul magasin en cause »
2. « Roubaix : le textile femme du samedi décroche (-25 %) depuis l'arrivée d'un concurrent »
3. « Recommandation : tester une animation samedi, 6 semaines, 4 000 € »

**Ce qui est évalué :** structure contexte/analyse/reco respectée ; chiffres traduits en € et impact ; recommandation actionnable et mesurable ; honnêteté sur les limites (hypothèse vs fait) ; zéro jargon.

</details>

---

### Exercice 2 — Auditer l'accessibilité d'un graphique

**Contexte.** Un collègue te montre ce graphique pour le comité de direction :

> Un **camembert** avec 9 parts, intitulé « Répartition ». Les parts sont en dégradé de **vert clair à vert foncé**. Aucune étiquette sur le graphique : il faut lire une légende à droite qui associe chaque nuance de vert à un magasin. Pas de pourcentages affichés. Image insérée dans un dashboard web sans texte alternatif.

**Ta mission.** Liste tous les **problèmes d'accessibilité et de lisibilité**, puis propose une **version corrigée**.

<details>
<summary>Voir le corrigé</summary>

**Problèmes identifiés :**

1. **Titre non explicite.** « Répartition » ne dit rien. → Titre qui porte le message (ex. « 3 magasins font 70 % du CA »).
2. **Information codée par la couleur seule** — et en plus 9 nuances d'une **même couleur** (vert) : impossible à distinguer pour tout le monde, catastrophique pour un daltonien. → Ne jamais reposer sur la couleur seule.
3. **Camembert à 9 parts** : l'œil humain compare très mal des angles. Au-delà de 4-5 parts, c'est illisible. → Remplacer par un **diagramme en barres horizontales triées**.
4. **Légende déportée à droite** : aller-retour œil/légende fatigant. → **Étiquettes directes** sur chaque barre.
5. **Pas de valeurs affichées** : on ne peut pas quantifier. → Afficher les **% ou €** au bout de chaque barre.
6. **Pas de texte alternatif** : invisible pour un lecteur d'écran. → Ajouter un `alt` résumant le message + proposer le **tableau de données** sous le graphique.
7. **Contraste** des verts clairs sur fond blanc probablement < 3:1 → vérifier avec un *contrast checker*.

**Version corrigée :**
- Type : **barres horizontales triées** du plus grand au plus petit CA.
- Titre : « 3 magasins concentrent 70 % du chiffre d'affaires ».
- Couleur : une seule couleur sobre, et on **met en avant** (couleur d'accent) le magasin clé ; le reste en gris.
- **Étiquettes** de magasin à gauche, **valeurs en €/%** à droite de chaque barre.
- Axe nommé avec unité. **Texte alternatif** ajouté. **Tableau** des données accessible en dessous.
- Vérification avec un **simulateur de daltonisme** : le message reste lisible.

**Ce qui est évalué :** repérage des 4 piliers WCAG (contraste, couleur seule, titres explicites, alternative textuelle) + lisibilité du choix de graphique.

</details>

---

## Vidéos d'auto-formation

> Les liens directs ci-dessous ont été vérifiés. Pour les sujets sans vidéo unique de référence, un **lien de recherche YouTube** est fourni : choisis la vidéo récente la mieux notée.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Storytelling with Data | Talks at Google (Cole Nussbaumer Knaflic) | EN | ~1 h | https://www.youtube.com/watch?v=8EMW7io4rSI | Les fondamentaux : enlever le superflu, diriger l'attention avec la couleur, raconter une histoire avec un graphique |
| transform: a storytelling with data mini-workshop | storytelling with data | EN | ~30 min | https://www.youtube.com/watch?v=PoGv0dViLAo | Atelier pratique : transformer un graphique brut illisible en visuel clair, étape par étape |
| Data Storytelling : astuces pour bien démarrer | (recherche YouTube FR) | FR | ~10-15 min | https://m.youtube.com/watch?v=QlwwxK3t_4U | Premiers réflexes du data storytelling en français, appliqués à des cas concrets |
| Le pitch / prise de parole pour convaincre | (recherche YouTube FR) | FR | varié | https://www.youtube.com/results?search_query=pitch+convaincre+prise+de+parole+présentation+technique | Structurer un pitch, accrocher l'audience, gérer le trac et la voix |
| Accessible & color-blind friendly data visualization | (recherche YouTube EN) | EN | varié | https://www.youtube.com/results?search_query=accessible+colorblind+friendly+data+visualization+wcag | Choisir des palettes adaptées au daltonisme, contraste, ne pas coder par la couleur seule |

---

## Quiz — 5 QCM

**Q1.** Dans quel ordre structure-t-on un message data ?
- A) Recommandation → contexte → analyse
- B) Contexte → analyse → recommandation
- C) Analyse → méthode → données
- D) Méthode → analyse → contexte

**Q2.** Tu présentes à la **direction**. Que dois-tu privilégier ?
- A) Le détail de tes requêtes SQL et tes hypothèses
- B) Un message synthétique, l'impact en € et une recommandation
- C) Tous les graphiques que tu as produits
- D) La liste exhaustive des sources de données

**Q3.** Quel ratio de contraste minimum recommandent les WCAG (AA) pour le texte normal ?
- A) 1,5:1
- B) 2:1
- C) 4,5:1
- D) 10:1

**Q4.** Pourquoi éviter de coder une information uniquement par un couple rouge/vert ?
- A) Parce que le rouge est agressif
- B) Parce que ~8 % des hommes sont daltoniens et distinguent mal rouge/vert
- C) Parce que c'est interdit par la loi dans tous les cas
- D) Parce que ces couleurs ne s'impriment pas

**Q5.** Un commanditaire te pose une question dont tu n'as pas la réponse. Que fais-tu ?
- A) Tu inventes une réponse plausible
- B) Tu changes de sujet
- C) Tu dis que tu ne sais pas et que tu reviendras avec l'information
- D) Tu renvoies la question à quelqu'un d'autre dans la salle

<details>
<summary>Voir les réponses</summary>

- **Q1 : B.** Contexte → analyse → recommandation. On pose le décor, on montre ce que disent les données, on propose une action.
- **Q2 : B.** La direction veut décider vite : synthèse, impact business, recommandation. Le détail technique va en annexe.
- **Q3 : C.** 4,5:1 pour le texte normal (3:1 pour le gros texte et les éléments graphiques).
- **Q4 : B.** La deutéranopie (rouge/vert) est la forme la plus courante de daltonisme. Toujours ajouter un second signal (texte, forme, icône).
- **Q5 : C.** L'honnêteté préserve ta crédibilité. « Je ne sais pas, je vérifie » est une réponse professionnelle.

</details>

---

## À retenir

- **Le « dernier kilomètre » fait toute la valeur.** Une analyse non comprise est une analyse inutile.
- **Structure** tout message en **contexte → analyse → recommandation**, et commence par le résultat, pas la méthode.
- **Adapte le zoom et le vocabulaire** au public : direction (€ et décision), métier (action terrain), technique (méthode et limites). Même vérité, trois discours.
- **Une slide = un message.** Le titre porte le message ; les titres seuls doivent raconter l'histoire.
- **Accessibilité WCAG, 4 réflexes :** contraste suffisant (4,5:1), jamais la couleur seule (pense daltonisme), titres et axes explicites, texte alternatif + tableau de données.
- **Questions :** anticipe, reformule, réponds court, et dis « je ne sais pas » plutôt que d'inventer.
- **Évite les 5 pièges :** surcharge, rouge/vert seul, faux expert, jargon, graphique trompeur.
