# La fonction `pipeline()` — Inférence en une ligne

## Qu'est-ce qu'un pipeline ?

La fonction `pipeline()` est l'abstraction de **plus haut niveau** de la bibliothèque `transformers`. Elle encapsule en un seul objet :

1. Le chargement du tokenizer
2. Le chargement du modèle
3. Le pré-traitement des entrées
4. L'inférence (forward pass)
5. Le post-traitement des sorties

**Objectif** : utiliser un modèle pré-entraîné sans se soucier des détails techniques.

---

## Syntaxe générale

```python
from transformers import pipeline

pipe = pipeline(
    task="<nom-de-la-tâche>",
    model="<nom-ou-chemin-du-modèle>",  # optionnel, sinon modèle par défaut
    device=0,                            # 0 = premier GPU, -1 = CPU
    # device_map="auto",                 # pour les grands modèles
)

résultat = pipe(entrée)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution dans un terminal du premier pipeline (text-classification) avec la barre de téléchargement du modèle visible, puis le résultat JSON affiché
> **Expliquer :** Ce qui se passe lors du premier appel (téléchargement depuis le Hub, mise en cache), pourquoi le deuxième appel est instantané, et comment lire la sortie (label + score de confiance)

---

## Tâche 1 : Classification de texte (`text-classification`)

Attribue un label à un texte parmi des classes prédéfinies.

```python
from transformers import pipeline

# Analyse de sentiment
classifier = pipeline(
    task="text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

# Entrée unique
result = classifier("Ce film est vraiment fantastique !")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Entrées multiples (batch)
texts = [
    "J'adore cette formation, très bien expliquée.",
    "Le service client était désastreux, jamais vu ça.",
    "La livraison était dans les délais prévus.",
]
results = classifier(texts)
for text, res in zip(texts, results):
    print(f"{res['label']:8s} ({res['score']:.1%}) → {text}")
```

### Modèle francophone

```python
# Modèle entraîné sur du français
fr_classifier = pipeline(
    task="text-classification",
    model="tblard/tf-allocine"  # Sentiment sur des critiques de films français
)

print(fr_classifier("Ce film m'a laissé une impression mitigée."))
```

---

## Tâche 2 : Reconnaissance d'entités nommées (`ner` / `token-classification`)

Identifie et catégorise les entités dans un texte (personnes, lieux, organisations...).

```python
from transformers import pipeline

ner = pipeline(
    task="ner",
    model="Jean-Baptiste/roberta-large-ner-english",
    aggregation_strategy="simple"  # Regroupe les tokens d'une même entité
)

text = "Emmanuel Macron visited Paris and met with Ursula von der Leyen at the Élysée Palace."
entities = ner(text)

for entity in entities:
    print(f"{entity['word']:30s} → {entity['entity_group']:4s} (score: {entity['score']:.2%})")
```

Sortie attendue :
```
Emmanuel Macron                → PER  (score: 99.87%)
Paris                          → LOC  (score: 99.91%)
Ursula von der Leyen           → PER  (score: 99.45%)
Élysée Palace                  → LOC  (score: 98.73%)
```

### Options d'aggregation

```python
# "none"    : un résultat par token (B-PER, I-PER, etc.)
# "simple"  : regroupe les tokens consécutifs
# "first"   : garde le label du premier token du groupe
# "average" : moyenne des scores pour le groupe
# "max"     : garde le token avec le score le plus élevé

ner_detailed = pipeline("ner", aggregation_strategy="none")
```

---

## Tâche 3 : Question Answering (`question-answering`)

Extrait une réponse depuis un contexte donné.

```python
from transformers import pipeline

qa = pipeline(
    task="question-answering",
    model="deepset/roberta-base-squad2"
)

context = """
Hugging Face est une entreprise américaine fondée en 2016 par Clément Delangue,
Julien Chaumond et Thomas Wolf. Son siège est à New York. Elle est connue pour
sa bibliothèque open-source Transformers, utilisée par des millions de développeurs
dans le monde entier pour des tâches de traitement du langage naturel.
"""

questions = [
    "Qui a fondé Hugging Face ?",
    "Quand a été fondée Hugging Face ?",
    "Où est le siège d'Hugging Face ?",
    "Pour quoi Hugging Face est-elle connue ?",
]

for question in questions:
    result = qa(question=question, context=context)
    print(f"Q: {question}")
    print(f"R: {result['answer']} (score: {result['score']:.2%}, positions {result['start']}-{result['end']})")
    print()
```

---

## Tâche 4 : Génération de texte (`text-generation`)

Génère du texte en continuant une amorce (prompt).

```python
from transformers import pipeline

generator = pipeline(
    task="text-generation",
    model="gpt2",  # Modèle léger pour démo
    device=-1      # CPU pour éviter les problèmes de VRAM
)

# Génération simple
result = generator(
    "In the future, artificial intelligence will",
    max_new_tokens=50,
    num_return_sequences=1,
)
print(result[0]["generated_text"])
```

### Stratégies d'échantillonnage

```python
# Greedy decoding (déterministe, mais répétitif)
generator_greedy = pipeline("text-generation", model="gpt2")
result = generator_greedy(
    "Once upon a time",
    max_new_tokens=60,
    do_sample=False  # Greedy
)

# Sampling avec température
result = generator_greedy(
    "Once upon a time",
    max_new_tokens=60,
    do_sample=True,
    temperature=0.8,   # < 1 = plus concentré, > 1 = plus créatif
    top_k=50,          # Limiter aux 50 tokens les plus probables
    top_p=0.92,        # Nucleus sampling : top 92% de la masse de probabilité
)

# Beam search (meilleur compromis qualité/vitesse)
result = generator_greedy(
    "Once upon a time",
    max_new_tokens=60,
    num_beams=5,
    early_stopping=True,
)

print(result[0]["generated_text"])
```

### Modèle francophone de génération

```python
# CamemBERT-based ou modèles français
fr_generator = pipeline(
    "text-generation",
    model="asi/gpt-fr-cased-small"  # GPT-2 entraîné en français
)

result = fr_generator(
    "La révolution française a",
    max_new_tokens=80,
    do_sample=True,
    temperature=0.7,
)
print(result[0]["generated_text"])
```

---

## Tâche 5 : Résumé automatique (`summarization`)

Condense un texte long en un résumé court.

```python
from transformers import pipeline

summarizer = pipeline(
    task="summarization",
    model="facebook/bart-large-cnn"
)

article = """
The Amazon rainforest, often referred to as the "lungs of the Earth," plays a crucial
role in regulating the global climate by absorbing vast amounts of carbon dioxide.
Spanning over 5.5 million square kilometers across nine countries in South America,
it is home to approximately 10% of all species on Earth. However, deforestation driven
by agriculture, logging, and infrastructure development has dramatically reduced its size.
Scientists warn that if current trends continue, the Amazon could reach a tipping point
where it transitions from a carbon sink to a carbon source, accelerating climate change.
International efforts to protect and restore the rainforest are ongoing, with many
countries pledging to reduce deforestation rates and support indigenous communities
who are its most effective guardians.
"""

summary = summarizer(
    article,
    max_length=100,   # Longueur max du résumé en tokens
    min_length=30,    # Longueur min
    do_sample=False,  # Résumé déterministe
)

print(summary[0]["summary_text"])
```

Sortie attendue :
```
The Amazon rainforest is home to approximately 10% of all species on Earth.
Deforestation driven by agriculture, logging and infrastructure development
has dramatically reduced its size. Scientists warn that the Amazon could reach
a tipping point where it transitions from a carbon sink to a carbon source.
```

---

## Tâche 6 : Traduction (`translation`)

Traduit du texte d'une langue à une autre.

```python
from transformers import pipeline

# Français → Anglais
fr_en = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-fr-en"
)

texts_fr = [
    "Bonjour, comment allez-vous aujourd'hui ?",
    "L'intelligence artificielle transforme le monde du travail.",
    "La formation est terminée, merci de votre attention.",
]

translations = fr_en(texts_fr)
for original, trans in zip(texts_fr, translations):
    print(f"FR: {original}")
    print(f"EN: {trans['translation_text']}")
    print()

# Anglais → Français
en_fr = pipeline(
    "translation_en_to_fr",
    model="Helsinki-NLP/opus-mt-en-fr"
)

print(en_fr("Machine learning is revolutionizing every industry.")[0]["translation_text"])
```

---

## Tâche 7 : Complétion de masque (`fill-mask`)

Prédit le(s) token(s) masqué(s) dans une phrase (tâche d'entraînement de BERT).

```python
from transformers import pipeline

# Modèle anglais
unmasker = pipeline("fill-mask", model="bert-base-uncased")

results = unmasker("Paris is the [MASK] of France.")
for r in results:
    print(f"{r['score']:.2%} → {r['token_str']:15s} : {r['sequence']}")

print()

# Modèle francophone (CamemBERT)
camembert = pipeline("fill-mask", model="camembert-base")

results = camembert("Le chat mange une <mask> dans la cuisine.")
for r in results[:5]:
    print(f"{r['score']:.2%} → {r['token_str']:15s} : {r['sequence']}")
```

Sortie pour CamemBERT :
```
34.27% → souris          : Le chat mange une souris dans la cuisine.
12.83% → pomme           : Le chat mange une pomme dans la cuisine.
 8.41% → carotte         : Le chat mange une carotte dans la cuisine.
 6.12% → pizza           : Le chat mange une pizza dans la cuisine.
 4.98% → pâtisserie      : Le chat mange une pâtisserie dans la cuisine.
```

---

## Tâche 8 : Similarité de phrases (`sentence-similarity` / `feature-extraction`)

Calcule des vecteurs d'embedding pour comparer des phrases.

```python
from transformers import pipeline
import torch
import torch.nn.functional as F

# Extraction de features (embeddings)
feature_extractor = pipeline(
    "feature-extraction",
    model="sentence-transformers/all-MiniLM-L6-v2",
    return_tensors=True
)

sentences = [
    "Je cherche un restaurant italien à Paris.",
    "Où trouver une bonne pizzeria dans la capitale ?",
    "Comment préparer une tarte aux pommes ?",
]

# Obtenir les embeddings (moyenne sur les tokens)
embeddings = []
for sentence in sentences:
    output = feature_extractor(sentence)
    # Shape: [1, seq_len, hidden_size] → moyenne sur seq_len
    embedding = output[0].mean(dim=1)
    embeddings.append(embedding)

# Calculer les similarités cosinus
for i in range(len(sentences)):
    for j in range(i+1, len(sentences)):
        sim = F.cosine_similarity(embeddings[i], embeddings[j])
        print(f"Sim({i+1},{j+1}) = {sim.item():.4f} | {sentences[i][:30]:30s} ↔ {sentences[j][:30]}")
```

---

## Tâche 9 : Classification zéro-shot (`zero-shot-classification`)

Classifie un texte dans des catégories **sans jamais avoir vu ces catégories** pendant l'entraînement.

```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

text = "Le gouvernement annonce une réforme majeure du système éducatif national."

# Les labels peuvent être n'importe quoi !
labels = ["politique", "économie", "éducation", "sport", "technologie", "santé"]

result = classifier(text, candidate_labels=labels)

print(f"Texte : {text}\n")
for label, score in zip(result["labels"], result["scores"]):
    bar = "█" * int(score * 30)
    print(f"{label:15s} {score:.2%} {bar}")
```

### Multi-label classification

```python
# multi_label=True : plusieurs labels peuvent être vrais simultanément
result = classifier(
    "Ce film d'action inclut des scènes de comédie et une romance.",
    candidate_labels=["action", "comédie", "romance", "horreur", "documentaire"],
    multi_label=True
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La sortie dans le terminal du pipeline zero-shot-classification avec la barre de progression des scores pour chaque label
> **Expliquer :** Pourquoi c'est "zéro-shot" (le modèle n'a jamais été entraîné sur ces labels), comment le modèle utilise l'inférence de langage naturel (NLI) pour décider si le texte "implique" chaque label, et les cas d'usage (prototypage rapide sans données labellisées)

---

## Tâche 10 : Reconnaissance vocale (`automatic-speech-recognition`)

Transcrit un fichier audio en texte (speech-to-text).

```python
from transformers import pipeline

# Whisper : modèle state-of-the-art d'OpenAI
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    generate_kwargs={"language": "french"}
)

# Depuis un fichier local
result = asr("audio_sample.wav")
print(result["text"])

# Depuis une URL
result = asr("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/mlk.flac")
print(result["text"])
```

---

## Configurer le device et les performances

```python
import torch
from transformers import pipeline

# Détection automatique du device
device = 0 if torch.cuda.is_available() else -1
print(f"Utilisation du device : {'GPU' if device == 0 else 'CPU'}")

# Pour les grands modèles : device_map="auto" distribue sur plusieurs GPU
large_pipe = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.2",
    device_map="auto",          # Distribution automatique sur GPU(s) disponibles
    torch_dtype=torch.float16,  # Réduction de la précision (économise la VRAM)
)

# Batch processing pour l'efficacité
pipe = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
texts = ["text1", "text2", "text3"] * 100  # 300 textes

# Traitement en batch (plus rapide que boucle)
results = pipe(texts, batch_size=32)
print(f"Traité {len(results)} textes")
```

---

## Tableau récapitulatif des tâches

| Tâche | `task=` | Entrée | Sortie |
|-------|---------|--------|--------|
| Classification de sentiment | `"text-classification"` | `str` | `label`, `score` |
| NER | `"ner"` | `str` | liste d'entités |
| QA extractif | `"question-answering"` | `question + context` | `answer`, `score` |
| Génération | `"text-generation"` | `str` (prompt) | texte généré |
| Résumé | `"summarization"` | `str` (long texte) | `summary_text` |
| Traduction | `"translation"` | `str` | `translation_text` |
| Fill-mask | `"fill-mask"` | `str` avec `[MASK]` | tokens candidats |
| Zero-shot | `"zero-shot-classification"` | `str` + labels | scores par label |
| ASR | `"automatic-speech-recognition"` | chemin audio | `text` |
| Image classification | `"image-classification"` | image | `label`, `score` |

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un notebook Jupyter avec plusieurs cellules montrant différents pipelines s'exécuter, avec les sorties visibles pour au moins 3 tâches différentes (text-classification, NER, zero-shot)
> **Expliquer :** La cohérence de l'API (toujours `pipeline(task, model)`), pourquoi les modèles par défaut changent avec les versions de `transformers`, et comment choisir un bon modèle pour sa langue et sa tâche en consultant le Hub

---

## Bonnes pratiques

```python
# 1. Toujours spécifier le modèle explicitement (reproductibilité)
#    BAD:  pipeline("text-classification")  # modèle par défaut peut changer
#    GOOD: pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

# 2. Réutiliser le pipeline (ne pas recréer à chaque appel)
#    BAD:
def classify_bad(text):
    pipe = pipeline("text-classification")  # Recharge le modèle à chaque appel !
    return pipe(text)

#    GOOD:
classifier = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

def classify_good(text):
    return classifier(text)  # Réutilise le modèle déjà chargé

# 3. Gérer les textes longs (truncation)
classifier_trunc = pipeline(
    "text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,   # Tronque automatiquement si trop long
    max_length=512     # Limite de BERT
)

# 4. Utiliser torch_dtype=torch.float16 sur GPU pour économiser la VRAM
import torch
pipe_fp16 = pipeline(
    "text-generation",
    model="gpt2-medium",
    torch_dtype=torch.float16,
    device=0
)
```

---

## Suite du cours

Le prochain module ([03-tokenizers.md](./03-tokenizers.md)) explore le mécanisme de tokenisation en détail, essentiel pour comprendre pourquoi certains textes posent problème et comment préparer correctement les données pour le fine-tuning.
