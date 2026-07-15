# Brief — Analyse de sentiments (du TF-IDF au Transformer)

## Contexte

Vous travaillez pour une plateforme de **critiques de films**. La rédaction reçoit des milliers
d'avis par jour et veut un **thermomètre automatique** : cet avis est-il **positif** ou **négatif** ?
Vous allez construire ce classifieur de texte, en **montant en puissance progressivement** : d'abord
une méthode « statistique » simple, puis un vrai **Transformer** pré-entraîné.

> **Analogie** — Comprendre un texte pour une machine, c'est comme apprendre une langue étrangère par
> étapes : d'abord compter les mots-clés (TF-IDF), puis saisir que des mots ont un **sens proche**
> (embeddings), enfin comprendre la **phrase entière et son contexte** (Transformer). Vous allez
> refaire ce chemin.

### Question centrale

**« À partir d'un avis en texte libre, peut-on prédire fiablement s'il est positif ou négatif — et
qu'apporte concrètement un Transformer par rapport à une méthode simple ? »**

### Données

- **Allociné** — ~200 000 critiques de films **en français**, étiquetées positif/négatif. Réel,
  téléchargeable via Hugging Face : `datasets.load_dataset("allocine")`.
  https://huggingface.co/datasets/allocine
- Alternative anglaise : **IMDB** (`load_dataset("imdb")`).

---

## Modalités pédagogiques

Travail **individuel**, ~5 jours. Prérequis : [module NLP](../../../09-Deep-Learning/NLP/) (jusqu'aux
Transformers) et [Fondamentaux DL](../../../09-Deep-Learning/01-Fondamentaux-DL/).

### Phase 1 — Explorer & nettoyer le texte (J1)

Chargez le dataset, **lisez de vrais avis**, regardez l'équilibre positif/négatif et la longueur des
textes. Mettez en place le **preprocessing** (module 2 du cours) : minuscules, ponctuation,
tokenisation. Faut-il retirer les *stopwords* pour du sentiment ? (Attention : « pas bon » — le
« pas » compte !)

### Phase 2 — Baseline TF-IDF (J2)

Construisez une **baseline** honnête : `TfidfVectorizer` + une régression logistique
(`scikit-learn`). Mesurez l'accuracy et le F1. Cette baseline est votre **mètre-étalon** : tout modèle
plus complexe devra la battre pour justifier sa complexité. Quels mots pèsent le plus dans la décision ?

> **Analogie** — Le TF-IDF, c'est **compter les mots qui comptent** : « génial », « chef-d'œuvre »
> tirent vers le positif ; « ennuyeux », « raté » vers le négatif. Simple, mais aveugle au contexte.

### Phase 3 — Fine-tuner un Transformer (J3-J4)

Passez à un **Transformer pré-entraîné** français (ex. `distilcamembert` ou `camembert-base`) via
Hugging Face `transformers`. **Fine-tunez-le** sur vos avis : on part d'un modèle qui « connaît déjà
le français » et on lui apprend **juste** la tâche de sentiment (l'idée du transfer learning). Suivez
la loss, gérez la longueur max des séquences. Que gagne-t-on face à la baseline TF-IDF, et à quel coût
(temps, GPU) ?

### Phase 4 — Évaluer, expliquer & restituer (J5)

Comparez **TF-IDF vs Transformer** sur le jeu de test (accuracy, F1, matrice de confusion). **Lisez
les erreurs** : sur quels avis le modèle se trompe-t-il (ironie, avis nuancés) ? Emballez une petite
**démo** (Gradio) : on saisit un avis, on obtient le sentiment + la confiance. Rédigez un rapport
honnête : quand la simplicité du TF-IDF suffit-elle, quand le Transformer vaut-il son coût ?

---

## Modalités d'évaluation

- **Démonstration technique (60 %)** : la démo prédit correctement sur des avis nouveaux ; les deux
  approches (TF-IDF + Transformer) tournent et sont comparées.
- **Revue de code & analyse (40 %)** : preprocessing justifié, baseline sérieuse, fine-tuning maîtrisé,
  analyse des erreurs et du compromis simplicité/performance.

> **Validation partielle** : une baseline TF-IDF solide + une analyse fine des erreurs, même sans
> Transformer parfaitement fine-tuné, peut valider partiellement.

---

## Livrables

**Repo GitHub public** :

- Le code : preprocessing → TF-IDF → Transformer → évaluation.
- La **comparaison chiffrée** des deux approches (tableau + matrice de confusion).
- L'**analyse des erreurs** (exemples d'avis mal classés + hypothèses).
- La **démo** (Gradio) + instructions.
- Un **README** : approche, résultats, compromis, limites, auteur.

---

## Critères de performance

**Préparer le texte**
- Le preprocessing est adapté au sentiment (le traitement des négations est réfléchi).
- Le split train/validation/test est étanche.

**Modéliser (du simple au complexe)**
- Une **baseline TF-IDF** honnête est construite et mesurée.
- Un **Transformer pré-entraîné** est **fine-tuné** correctement sur la tâche.

**Évaluer et comparer**
- L'évaluation utilise accuracy **et** F1 + matrice de confusion.
- Le compromis **performance vs coût** entre les deux approches est discuté avec des chiffres.

**Restituer**
- La démo fonctionne ; l'analyse des erreurs est concrète ; le code est propre et versionné.

---

## Ressources

- Cours NLP V3 — [attention & Transformers](../../../09-Deep-Learning/NLP/V3/Module6/index.md), [BERT & GPT](../../../09-Deep-Learning/NLP/V3/Module7/index.md)
- Hugging Face — Text classification : https://huggingface.co/docs/transformers/tasks/sequence_classification
- Dataset Allociné : https://huggingface.co/datasets/allocine
- CamemBERT (français) : https://huggingface.co/camembert-base
- scikit-learn — TfidfVectorizer : https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

> 🔎 **Pour aller plus loin** : servir le modèle en API (voir [module NLP 8 — déploiement](../../../09-Deep-Learning/NLP/V3/Module8/index.md)) et le connecter à un pipeline LLM/RAG ([10-LLM](../../../10-Large-Language-Model/)).
