# Tokenizers — Du texte aux nombres

## Pourquoi la tokenisation ?

Les modèles de deep learning ne comprennent pas le texte brut. Ils travaillent avec des nombres. La **tokenisation** est le processus qui convertit du texte en une séquence d'entiers que le modèle peut traiter.

```
"Bonjour le monde !" → [101, 9753, 2571, 6252, 106, 102]
```

Ce n'est pas aussi simple que de découper par espaces : les tokenizers modernes utilisent des algorithmes sophistiqués pour gérer les mots rares, les morphologies complexes et les langues sans espaces.

---

## Les trois grands algorithmes de tokenisation

### 1. BPE — Byte Pair Encoding (GPT, GPT-2, RoBERTa)

BPE part des caractères individuels et **fusionne itérativement** les paires les plus fréquentes.

**Principe :**

```
Corpus d'entraînement : "low low low lower lowest newest"

Etape 0 (caractères) : l o w | l o w e r | n e w e s t
Etape 1 (paire "lo" la plus fréquente) : lo w | lo w e r | n e w e s t
Etape 2 (paire "low" la plus fréquente) : low | low e r | n e w e s t
Etape 3 (paire "ne" la plus fréquente) : low | lowe r | ne we s t
...
```

**Vocabulaire final** : contient des sous-mots fréquents (`low`, `est`, `ing`, `##er`...)

```python
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

text = "Tokenization is fascinating!"
tokens = tokenizer.tokenize(text)
ids = tokenizer.encode(text)

print(f"Tokens : {tokens}")
print(f"IDs    : {ids}")
# Tokens : ['Token', 'ization', 'Ġis', 'Ġfasc', 'inating', '!']
# IDs    : [30642, 1634, 318, 40481, 803, 0]
```

Note : le préfixe `Ġ` représente un espace avant le token dans GPT-2.

### 2. WordPiece (BERT, DistilBERT, CamemBERT)

Similaire à BPE mais utilise une **vraisemblance** au lieu d'une fréquence de paires. Les sous-mots non-initiaux sont préfixés par `##`.

```python
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

text = "Tokenization is fascinating!"
tokens = tokenizer.tokenize(text)
print(f"Tokens : {tokens}")
# Tokens : ['token', '##ization', 'is', 'fas', '##cin', '##ating', '!']
```

Le `##` signifie "ce sous-mot fait suite au précédent sans espace".

### 3. SentencePiece + Unigram (T5, LLaMA, Mistral, mBART)

SentencePiece traite le texte comme une **séquence d'octets** (pas de pré-tokenisation par espace), ce qui le rend universellement applicable à toutes les langues (y compris le japonais, le chinois, etc.).

```python
from transformers import T5Tokenizer

tokenizer = T5Tokenizer.from_pretrained("t5-base")

text = "Tokenization is fascinating!"
tokens = tokenizer.tokenize(text)
print(f"Tokens : {tokens}")
# Tokens : ['▁Token', 'ization', '▁is', '▁fasci', 'nating', '!']
```

Le `▁` (underscore spécial) représente un espace précédant le token.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un notebook avec les trois tokenizers côte à côte tokenisant la même phrase "Unbelievable tokenization!", montrant les différences de découpage et de notation
> **Expliquer :** Pourquoi les découpes sont différentes (algorithmes différents, vocabulaires différents), comment `##` et `▁` encodent l'information de position, et pourquoi un LLaMA tokenise le français moins bien qu'un modèle entraîné en français (biais du corpus d'entraînement)

---

## L'API AutoTokenizer

```python
from transformers import AutoTokenizer

# Charge automatiquement le bon tokenizer selon le modèle
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokenisation basique
text = "Hello, my name is John and I live in New York."

# Méthode 1 : tokenize() → liste de strings
tokens = tokenizer.tokenize(text)
print(f"Tokens     : {tokens}")

# Méthode 2 : encode() → liste d'IDs (avec tokens spéciaux)
ids = tokenizer.encode(text)
print(f"IDs        : {ids}")

# Méthode 3 : __call__() → dict complet (recommandé)
encoding = tokenizer(text, return_tensors="pt")
print(f"input_ids  : {encoding['input_ids']}")
print(f"attention_mask: {encoding['attention_mask']}")

# Décodage : IDs → texte
decoded = tokenizer.decode(ids)
print(f"Décodé     : {decoded}")
# [CLS] hello, my name is john and i live in new york. [SEP]
```

---

## Les tokens spéciaux

Chaque modèle ajoute des tokens spéciaux avec des rôles précis.

### Tokens de BERT

```python
from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

print(f"[CLS] id    : {tokenizer.cls_token_id}  → {tokenizer.cls_token}")   # 101
print(f"[SEP] id    : {tokenizer.sep_token_id}  → {tokenizer.sep_token}")   # 102
print(f"[PAD] id    : {tokenizer.pad_token_id}  → {tokenizer.pad_token}")   # 0
print(f"[UNK] id    : {tokenizer.unk_token_id}  → {tokenizer.unk_token}")   # 100
print(f"[MASK] id   : {tokenizer.mask_token_id} → {tokenizer.mask_token}")  # 103

# Rôles :
# [CLS] : Classification token - au début de chaque séquence, représente toute la phrase
# [SEP] : Separator - sépare deux phrases (ex: question + contexte)
# [PAD] : Padding - rembourre les séquences courtes pour uniformiser la longueur
# [UNK] : Unknown - remplace les tokens hors vocabulaire (rare avec BPE/WordPiece)
# [MASK] : Mask - pour la tâche de MLM (Masked Language Modeling)

# Visualiser avec les tokens spéciaux
text_a = "What is the capital of France?"
text_b = "Paris is the capital of France."

# Deux phrases encodées ensemble (pour QA, NLI...)
encoding = tokenizer(text_a, text_b)
decoded_with_special = tokenizer.decode(encoding["input_ids"])
print(decoded_with_special)
# [CLS] what is the capital of france? [SEP] paris is the capital of france. [SEP]
```

### Tokens de GPT-2

```python
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# GPT-2 n'a pas de [PAD] par défaut (modèle autoregressif)
print(f"EOS token   : {tokenizer.eos_token}  id={tokenizer.eos_token_id}")  # <|endoftext|>
print(f"BOS token   : {tokenizer.bos_token}  id={tokenizer.bos_token_id}")  # <|endoftext|>

# Pour le fine-tuning, on doit souvent ajouter un pad token
tokenizer.pad_token = tokenizer.eos_token  # Trick courant
```

---

## Padding et Truncation

Problème : les séquences d'un batch ont des longueurs différentes, mais les modèles requièrent des tenseurs rectangulaires.

### Padding — allonger les séquences courtes

```python
from transformers import AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

sentences = [
    "Short sentence.",
    "This is a medium length sentence with more words.",
    "This is an even longer sentence that has quite a few more tokens than the others do.",
]

# Sans padding : impossible d'avoir un batch (longueurs différentes)
# encodings = tokenizer(sentences)  # input_ids de longueurs différentes

# Padding à la longueur maximale du batch
batch = tokenizer(
    sentences,
    padding=True,        # Ou padding="longest"
    return_tensors="pt"  # PyTorch tensors
)

print(f"Shape : {batch['input_ids'].shape}")  # [3, max_len]
print(f"input_ids :\n{batch['input_ids']}")
print(f"attention_mask :\n{batch['attention_mask']}")
# Les 0 dans attention_mask indiquent les tokens de padding (ignorés par le modèle)
```

### Truncation — raccourcir les séquences trop longues

```python
# BERT max = 512 tokens, GPT-2 max = 1024 tokens
long_text = "word " * 600  # 600 mots → dépasse la limite de BERT

# Sans truncation : erreur ou comportement indéfini
encoding_truncated = tokenizer(
    long_text,
    truncation=True,           # Active la troncature
    max_length=512,            # Limite à 512 tokens (max BERT)
    return_tensors="pt"
)

print(f"Shape après truncation : {encoding_truncated['input_ids'].shape}")
# [1, 512]

# Padding ET truncation simultanés (cas d'usage le plus courant)
batch = tokenizer(
    sentences,
    padding=True,
    truncation=True,
    max_length=128,  # Limite à 128 pour les batches de fine-tuning
    return_tensors="pt"
)
```

### Stratégies de padding

```python
# padding="longest"     : pad jusqu'à la plus longue séquence du batch
# padding="max_length"  : pad jusqu'à max_length (même si batch plus court)
# padding=False          : pas de padding (séquences de longueurs différentes)

# Pour l'inférence : padding="longest" (plus efficace)
# Pour le fine-tuning : padding="max_length" ou utiliser un DataCollator
```

---

## Le `token_type_ids`

Pour BERT, quand deux séquences sont encodées ensemble, `token_type_ids` distingue la première de la seconde :

```python
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

question = "What is machine learning?"
context = "Machine learning is a subset of artificial intelligence."

encoding = tokenizer(question, context, return_tensors="pt")

print(f"input_ids     : {encoding['input_ids']}")
print(f"token_type_ids: {encoding['token_type_ids']}")
# token_type_ids : [0, 0, ..., 0, 1, 1, ..., 1]
#                  ← question (0) →  ← context (1) →

print(f"attention_mask: {encoding['attention_mask']}")
```

---

## Gestion des mots hors vocabulaire (OOV)

Avec BPE/WordPiece, il n'y a **pratiquement plus de tokens OOV** : tout mot inconnu est découpé en sous-mots connus jusqu'au niveau caractère.

```python
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Mot inventé : découpé en sous-mots existants
weird_word = "supercalifragilisticexpialidocious"
tokens = tokenizer.tokenize(weird_word)
print(f"'{weird_word}' → {tokens}")
# ['super', '##cal', '##if', '##rag', '##ili', '##stic', '##ex', '##pia', '##lid', '##oc', '##ious']

# Code source Python
code = "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
tokens = tokenizer.tokenize(code)
print(f"Code tokens : {tokens}")
```

---

## Tokenizer rapide vs lent

Hugging Face propose deux versions des tokenizers :

```python
from transformers import BertTokenizerFast, BertTokenizer

# Tokenizer LENT (Python pur, plus de contrôle)
slow = BertTokenizer.from_pretrained("bert-base-uncased")

# Tokenizer RAPIDE (Rust via tokenizers library, 100x plus rapide)
fast = BertTokenizerFast.from_pretrained("bert-base-uncased")

# AutoTokenizer charge le fast par défaut quand disponible
from transformers import AutoTokenizer
auto = AutoTokenizer.from_pretrained("bert-base-uncased")
print(f"Is fast: {auto.is_fast}")  # True

# Le tokenizer rapide donne accès aux offsets (position dans le texte original)
text = "Hello world, how are you?"
encoding = fast(text, return_offsets_mapping=True)
for token, (start, end) in zip(fast.convert_ids_to_tokens(encoding["input_ids"]), encoding["offset_mapping"]):
    if start != end:  # Ignorer les tokens spéciaux [CLS], [SEP]
        print(f"Token '{token:15s}' → position [{start:2d}:{end:2d}] = '{text[start:end]}'")
```

Les offsets sont essentiels pour la **NER** : on peut retrouver la position exacte des entités dans le texte original.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La visualisation des offsets dans un notebook : un tableau montrant chaque token avec sa position de début/fin et le caractère correspondant dans le texte original pour une phrase NER comme "Apple Inc. is based in Cupertino, California."
> **Expliquer :** Pourquoi les offsets sont critiques pour la NER (localiser les entités dans le texte d'origine), la différence entre tokenizer rapide et lent (la bibliothèque Rust `tokenizers`), et dans quel cas utiliser le tokenizer lent (débogage, contrôle fin)

---

## Sauvegarder et charger un tokenizer

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Sauvegarder localement
tokenizer.save_pretrained("./mon-tokenizer/")
# Crée : tokenizer_config.json, vocab.txt, tokenizer.json, special_tokens_map.json

# Recharger depuis le dossier local
tokenizer_local = AutoTokenizer.from_pretrained("./mon-tokenizer/")

# Vérification
text = "Test de chargement local"
assert tokenizer.encode(text) == tokenizer_local.encode(text)
print("Tokenizers identiques !")
```

---

## Ajouter des tokens au vocabulaire

Utile lors du fine-tuning sur un domaine spécialisé (médecine, droit, code...).

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Tokens spéciaux de domaine
domain_tokens = ["[DRUG]", "[DISEASE]", "[GENE]", "[PROTEIN]"]
tokenizer.add_special_tokens({"additional_special_tokens": domain_tokens})

# Tokens normaux de vocabulaire
new_words = ["covid19", "mrna", "immunoglobulin", "CRISPR"]
tokenizer.add_tokens(new_words)

print(f"Taille vocab avant : 30522")
print(f"Taille vocab après : {len(tokenizer)}")
# 30530

# IMPORTANT : il faut redimensionner les embeddings du modèle !
model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")
model.resize_token_embeddings(len(tokenizer))
print(f"Embedding layer : {model.bert.embeddings.word_embeddings.weight.shape}")
# torch.Size([30530, 768])
```

---

## Récapitulatif des paramètres clés

```python
tokenizer(
    text,                           # str ou list[str]
    text_pair=None,                 # Deuxième séquence (QA, NLI)
    add_special_tokens=True,        # Ajouter [CLS], [SEP], etc.
    padding=False,                  # False / True / "longest" / "max_length"
    truncation=False,               # False / True / "only_first" / "only_second"
    max_length=None,                # Longueur max après truncation
    stride=0,                       # Pour les fenêtres glissantes (long QA)
    return_tensors=None,            # None / "pt" / "tf" / "np"
    return_token_type_ids=None,     # Renvoyer token_type_ids ?
    return_attention_mask=None,     # Renvoyer attention_mask ?
    return_offsets_mapping=False,   # Positions dans le texte original (fast only)
    return_length=False,            # Renvoyer la longueur des séquences
    verbose=True,                   # Afficher les warnings
)
```

---

## Suite du cours

Le module suivant ([../Models/01-charger-modele.md](../Models/01-charger-modele.md)) montre comment charger les modèles complets avec `AutoModel` et utiliser les sorties du tokenizer pour effectuer une inférence manuelle, sans passer par le pipeline.
