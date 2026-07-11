# Inférence manuelle — Forward pass, logits et génération

## Pourquoi faire l'inférence manuellement ?

Le `pipeline()` cache les détails. Pour :
- Comprendre exactement ce que fait le modèle
- Accéder aux représentations intermédiaires (hidden states, attention)
- Implémenter des logiques de post-traitement personnalisées
- Optimiser les performances (batching, cache KV)

...il faut maîtriser le forward pass.

---

## Forward pass — Classification

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Toujours mettre en mode évaluation pour l'inférence
model.eval()

texts = [
    "This movie is absolutely fantastic!",
    "I wasted two hours of my life watching this.",
]

# 1. Tokenisation
inputs = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"  # PyTorch tensors
)

print(f"input_ids shape : {inputs['input_ids'].shape}")  # [2, seq_len]

# 2. Forward pass (sans calcul de gradient pour l'inférence)
with torch.no_grad():
    outputs = model(**inputs)

# 3. Extraire les logits
logits = outputs.logits
print(f"logits shape : {logits.shape}")  # [2, num_labels] = [2, 2]
print(f"logits raw   : {logits}")

# 4. Convertir en probabilités
probs = F.softmax(logits, dim=-1)
print(f"probabilities: {probs}")

# 5. Prédiction finale
predicted_class_ids = logits.argmax(dim=-1)
predictions = [model.config.id2label[class_id.item()] for class_id in predicted_class_ids]

for text, pred, prob in zip(texts, predictions, probs):
    confidence = prob.max().item()
    print(f"[{pred:8s} {confidence:.1%}] {text}")
```

---

## Comprendre la sortie `outputs`

```python
# outputs est un objet de type SequenceClassifierOutput
print(type(outputs))  # SequenceClassifierOutput

# Attributs disponibles (selon la tâche) :
print(outputs.logits.shape)          # [batch, num_labels] — toujours présent

# Si return_dict=True (défaut) :
# outputs.loss             — si les labels sont fournis
# outputs.hidden_states    — si output_hidden_states=True
# outputs.attentions       — si output_attentions=True

# Accéder aux hidden states de toutes les couches
outputs_with_hidden = model(
    **inputs,
    output_hidden_states=True
)
hidden_states = outputs_with_hidden.hidden_states
# Tuple de (num_layers + 1) tensors de shape [batch, seq_len, hidden_size]
print(f"Nombre de couches : {len(hidden_states)}")  # 7 pour DistilBERT (1 embed + 6 layers)
print(f"Shape par couche  : {hidden_states[0].shape}")  # [2, seq_len, 768]
```

---

## Inspecter les poids d'attention

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import matplotlib.pyplot as plt
import numpy as np

MODEL = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.eval()

text = "The movie was surprisingly good despite low expectations."
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs, output_attentions=True)

attentions = outputs.attentions
# Tuple de (num_layers) tensors de shape [batch, num_heads, seq_len, seq_len]

print(f"Nombre de couches     : {len(attentions)}")
print(f"Shape par couche      : {attentions[0].shape}")
# [1, 12, seq_len, seq_len] pour BERT-base

# Visualiser l'attention de la dernière couche, première tête
last_layer_attn = attentions[-1][0]  # [num_heads, seq_len, seq_len]
avg_attn = last_layer_attn.mean(dim=0).numpy()  # Moyenne sur les têtes

tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
print(f"\nTokens : {tokens}")
print(f"\nMatrice d'attention (moyenne des têtes) :")
for i, token_i in enumerate(tokens):
    row = " ".join(f"{avg_attn[i,j]:.2f}" for j in range(len(tokens)))
    print(f"{token_i:12s}: {row}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une heatmap matplotlib de la matrice d'attention (colormap "Blues") avec les tokens en axes X et Y, montrant quels tokens "regardent" quels autres tokens
> **Expliquer :** Comment l'attention croise-encodeur fonctionne (chaque token attend les autres), pourquoi le token [CLS] a souvent les poids les plus élevés (il agrège l'information), et comment les têtes multiples capturent différents types de relations syntaxiques/sémantiques

---

## Génération de texte avec `generate()`

La méthode `generate()` est disponible sur tous les modèles causaux (GPT-style) et seq2seq (T5-style).

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL)
model.eval()

prompt = "The future of artificial intelligence is"
inputs = tokenizer(prompt, return_tensors="pt")

# Génération avec les paramètres par défaut (greedy)
with torch.no_grad():
    output_ids = model.generate(
        inputs["input_ids"],
        max_new_tokens=50,
    )

# Décoder seulement les nouveaux tokens (pas le prompt)
new_tokens = output_ids[0, inputs["input_ids"].shape[1]:]
generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
print(f"Généré : {generated_text}")
```

---

## Stratégies de génération — Comparaison

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

prompt = "In a world where robots have become"
inputs = tokenizer(prompt, return_tensors="pt")

def generate_and_print(strategy_name, **kwargs):
    with torch.no_grad():
        output = model.generate(
            inputs["input_ids"],
            max_new_tokens=60,
            pad_token_id=tokenizer.eos_token_id,
            **kwargs
        )
    new = output[0, inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(new, skip_special_tokens=True)
    print(f"\n--- {strategy_name} ---")
    print(text)

# 1. Greedy Decoding — choisit toujours le token le plus probable
generate_and_print("Greedy (déterministe)", do_sample=False)

# 2. Beam Search — explore plusieurs chemins simultanément
generate_and_print("Beam Search (num_beams=5)", do_sample=False, num_beams=5, early_stopping=True)

# 3. Sampling — échantillonnage aléatoire selon les probabilités
generate_and_print("Sampling (temp=1.0)", do_sample=True, temperature=1.0)

# 4. Temperature Sampling — température basse = plus déterministe
generate_and_print("Sampling (temp=0.5)", do_sample=True, temperature=0.5)

# 5. Top-K Sampling — limiter aux K tokens les plus probables
generate_and_print("Top-K (k=50)", do_sample=True, top_k=50)

# 6. Top-P (Nucleus) Sampling — limiter aux tokens couvrant 90% de la proba
generate_and_print("Top-P (p=0.9)", do_sample=True, top_p=0.9)

# 7. Combinaison recommandée en pratique
generate_and_print(
    "Combinaison optimale",
    do_sample=True,
    temperature=0.8,
    top_k=50,
    top_p=0.92,
    repetition_penalty=1.3,  # Pénalise les répétitions
)
```

---

## `GenerationConfig` — Centraliser la configuration

```python
from transformers import GenerationConfig

# Créer une config de génération réutilisable
gen_config = GenerationConfig(
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
)

with torch.no_grad():
    output = model.generate(inputs["input_ids"], generation_config=gen_config)

# Sauvegarder la config avec le modèle
gen_config.save_pretrained("./mon-modele/")
model.save_pretrained("./mon-modele/")
```

---

## Génération avec modèles Instruction-tuned (Chat)

Les modèles "Instruct" ou "Chat" ont un format de prompt spécifique. Il faut utiliser `apply_chat_template`.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Exemple avec Mistral Instruct
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
# (Nécessite ~14GB VRAM en FP16)

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Format de conversation (messages)
messages = [
    {"role": "user", "content": "Explique le concept d'attention dans les Transformers en 3 phrases simples."}
]

# Appliquer le template de chat
input_text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,           # Retourner le texte brut d'abord
    add_generation_prompt=True  # Ajouter le token de début de réponse
)
print(f"Prompt formaté :\n{input_text}\n")

# Tokeniser et générer
inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(f"Réponse :\n{response}")
```

---

## Génération seq2seq (T5, BART, mBART)

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# T5 pour la traduction
MODEL = "Helsinki-NLP/opus-mt-fr-en"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
model.eval()

texts_fr = [
    "L'intelligence artificielle transforme le monde.",
    "La tokenisation est une étape cruciale du NLP.",
]

inputs = tokenizer(texts_fr, padding=True, truncation=True, return_tensors="pt")

with torch.no_grad():
    translated_ids = model.generate(
        **inputs,
        num_beams=4,          # Beam search pour la traduction
        max_length=128,
        early_stopping=True,
        forced_bos_token_id=None,  # Pour mBART, spécifier la langue cible
    )

translations = tokenizer.batch_decode(translated_ids, skip_special_tokens=True)
for fr, en in zip(texts_fr, translations):
    print(f"FR: {fr}")
    print(f"EN: {en}\n")
```

---

## Mesurer les performances d'inférence

```python
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

prompt = "Once upon a time in a land far away"
inputs = tokenizer(prompt, return_tensors="pt")

# Mesurer le temps et les tokens/seconde
def benchmark_generation(model, inputs, max_new_tokens=100, n_runs=3):
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        end = time.perf_counter()
        times.append(end - start)

    n_generated = output.shape[1] - inputs["input_ids"].shape[1]
    avg_time = sum(times) / len(times)
    tokens_per_sec = n_generated / avg_time
    return avg_time, tokens_per_sec

avg_time, tps = benchmark_generation(model, inputs)
print(f"Temps moyen    : {avg_time:.2f}s")
print(f"Tokens/seconde : {tps:.1f} t/s")

# Comparer CPU vs GPU si disponible
if torch.cuda.is_available():
    model_gpu = model.cuda()
    inputs_gpu = {k: v.cuda() for k, v in inputs.items()}
    avg_gpu, tps_gpu = benchmark_generation(model_gpu, inputs_gpu)
    print(f"\nGPU - Temps moyen    : {avg_gpu:.2f}s")
    print(f"GPU - Tokens/seconde : {tps_gpu:.1f} t/s")
    print(f"Accélération GPU/CPU : {tps_gpu/tps:.1f}x")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La sortie de `nvidia-smi` (ou `watch -n 1 nvidia-smi`) pendant la génération d'un modèle sur GPU, montrant l'utilisation de la VRAM et le pourcentage d'utilisation GPU
> **Expliquer :** Pourquoi la VRAM est un facteur limitant (modèle + activations + KV cache), comment calculer approximativement la VRAM nécessaire (nb_paramètres × 2 bytes pour FP16), et les techniques pour réduire la consommation (batch_size, quantization, attention flash)

---

## KV Cache — Optimisation de la génération

Pour les modèles causaux, la génération naïve recalcule toutes les clés/valeurs à chaque pas. Le KV cache évite cela.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

# La méthode generate() utilise automatiquement le KV cache
# Pour l'accès manuel (pour des implémentations custom) :

prompt = "The sky is"
inputs = tokenizer(prompt, return_tensors="pt")

# Premier forward pass
with torch.no_grad():
    outputs = model(**inputs, use_cache=True)
    past_key_values = outputs.past_key_values  # Cache des K/V

# Générer le token suivant avec le cache
next_token_logits = outputs.logits[:, -1, :]
next_token_id = next_token_logits.argmax(dim=-1, keepdim=True)
next_token = tokenizer.decode(next_token_id[0])
print(f"Token suivant prédit : '{next_token}'")

# Utiliser le cache pour le prochain pas (évite de recalculer les K/V passés)
with torch.no_grad():
    outputs_cached = model(
        input_ids=next_token_id,
        past_key_values=past_key_values,
        use_cache=True
    )
```

---

## Résumé : Forward pass en un schéma

```
Texte brut : "I love Paris"
        ↓ tokenizer()
input_ids : [101, 1045, 2293, 3681, 102]
        ↓ model.embeddings
Embeddings : tenseur [1, 5, 768]
        ↓ model.encoder (12 couches TransformerBlock)
Hidden states : tenseur [1, 5, 768] (contextualisés)
        ↓ model.classifier (pooler + dropout + linear)
Logits : tenseur [1, 2]  ← [score_négatif, score_positif]
        ↓ F.softmax()
Probs : [0.001, 0.999]
        ↓ argmax()
Prédiction : label 1 = "POSITIVE"
```

---

## Suite du cours

Le prochain module ([03-modeles-locaux.md](./03-modeles-locaux.md)) explique comment télécharger et exécuter des modèles en local sans connexion internet, et comment utiliser la quantization pour réduire drastiquement la consommation de VRAM.
