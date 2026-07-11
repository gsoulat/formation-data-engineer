# Modèles locaux — Download, exécution offline et quantization

## Pourquoi exécuter en local ?

- **Confidentialité** : les données ne quittent pas votre infrastructure
- **Latence** : pas de réseau, réponse plus rapide
- **Coût** : pas d'API payante (après achat initial du matériel)
- **Offline** : fonctionne sans connexion internet
- **Contrôle** : personnalisation complète du modèle et du prompt

---

## Télécharger un modèle manuellement

### Méthode 1 : `snapshot_download` (recommandé)

```python
from huggingface_hub import snapshot_download

# Télécharge tout le repository dans un dossier local
model_path = snapshot_download(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    local_dir="./models/mistral-7b-instruct/",
    ignore_patterns=["*.msgpack", "*.h5", "flax_model*"],  # Exclure les fichiers TF/JAX
    token="hf_votre_token",  # Pour les modèles restreints
)

print(f"Modèle téléchargé dans : {model_path}")
```

### Méthode 2 : Via la CLI

```bash
# Installer le CLI si nécessaire
pip install huggingface_hub

# Télécharger un modèle complet
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2 \
    --local-dir ./models/mistral-7b/ \
    --exclude "*.msgpack" "flax*"

# Télécharger un fichier spécifique
huggingface-cli download bert-base-uncased config.json \
    --local-dir ./models/bert/

# Voir la progression
huggingface-cli download gpt2 --local-dir ./models/gpt2/ --local-dir-use-symlinks False
```

### Méthode 3 : `from_pretrained` avec `local_dir`

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Premier appel : télécharge et met en cache
model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    cache_dir="./models/cache/"
)

# Appels suivants : utilise le cache (même sans internet)
import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Désactive les requêtes réseau

model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    cache_dir="./models/cache/"  # Doit être le même dossier
)
```

---

## Structure des fichiers d'un modèle

```bash
./models/gpt2/
├── config.json              # Architecture et hyperparamètres
├── tokenizer.json           # Vocabulaire et règles de tokenisation (fast tokenizer)
├── tokenizer_config.json    # Métadonnées du tokenizer
├── vocab.json               # Vocabulaire BPE (GPT-2 spécifique)
├── merges.txt               # Règles de fusion BPE (GPT-2 spécifique)
├── special_tokens_map.json  # Mapping des tokens spéciaux
├── generation_config.json   # Configuration de génération par défaut
└── model.safetensors        # Poids du modèle (format sécurisé, remplace .bin)
```

Pour les grands modèles, les poids sont fragmentés :
```bash
./models/llama-7b/
├── config.json
├── model-00001-of-00006.safetensors  # Shard 1/6
├── model-00002-of-00006.safetensors  # Shard 2/6
...
├── model-00006-of-00006.safetensors  # Shard 6/6
└── model.safetensors.index.json      # Index des shards
```

---

## Quantization avec `bitsandbytes`

La quantization réduit la précision des poids pour **économiser de la VRAM** avec une perte de qualité minimale.

| Précision | Bits/paramètre | 7B params VRAM | Qualité |
|-----------|---------------|----------------|---------|
| FP32      | 32 bits       | ~28 GB         | Maximale |
| FP16/BF16 | 16 bits       | ~14 GB         | Quasi-identique |
| INT8      | 8 bits        | ~7 GB          | Très bonne |
| NF4       | 4 bits        | ~3.5 GB        | Bonne |

### Installation

```bash
# Linux + CUDA uniquement (pas de support macOS/Windows natif)
pip install bitsandbytes accelerate

# Vérifier l'installation
python -c "import bitsandbytes as bnb; print(bnb.__version__)"
```

### Quantization 8-bit (INT8)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Configuration 8-bit
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,       # Seuil pour les valeurs aberrantes
    llm_int8_skip_modules=None,   # Couches à ne PAS quantifier
)

MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    quantization_config=quantization_config,
    device_map="auto",
)

# Vérifier l'utilisation mémoire
if torch.cuda.is_available():
    mem = torch.cuda.memory_allocated() / 1e9
    print(f"VRAM utilisée : {mem:.2f} GB")
```

### Quantization 4-bit (NF4) — QLoRA

```python
from transformers import BitsAndBytesConfig
import torch

# Configuration 4-bit NF4 (recommandée pour le fine-tuning QLoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NormalFloat4 : meilleure qualité
    bnb_4bit_use_double_quant=True,      # Double quantization (économise encore ~0.4 bits/param)
    bnb_4bit_compute_dtype=torch.bfloat16,  # Type de calcul (bfloat16 = bon compromis)
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    quantization_config=bnb_config,
    device_map="auto",
)

print(f"Type des poids : {model.dtype}")
# torch.uint8 pour les couches quantifiées
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La comparaison `nvidia-smi` side-by-side : modèle chargé en FP16 (gauche) vs INT8 (milieu) vs NF4 (droite), montrant la différence de VRAM consommée pour le même modèle 7B
> **Expliquer :** Le principe de la quantization (mapper les flottants sur une grille entière), pourquoi NF4 est meilleur que INT4 (distribution normale des poids), et pourquoi les premières et dernières couches sont souvent exclues de la quantization (plus sensibles à la perte de précision)

---

## GGUF et llama.cpp

**GGUF** (GPT-Generated Unified Format) est un format optimisé pour l'inférence sur CPU développé par le projet `llama.cpp`. Il est massivement utilisé sur des machines sans GPU.

### Installation de `llama-cpp-python`

```bash
# CPU uniquement
pip install llama-cpp-python

# Avec support CUDA (compilation nécessaire)
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall

# Avec support Metal (Apple Silicon)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall
```

### Télécharger un modèle GGUF

```bash
# Chercher sur le Hub : TheBloke ou bartowski publient des GGUF
# Exemple : Mistral 7B en différentes quantizations
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
    mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --local-dir ./models/gguf/

# Niveaux de quantization GGUF courants :
# Q2_K  : 2.5 bits/param — très compressé, qualité réduite
# Q4_0  : 4 bits/param   — basique, rapide
# Q4_K_M: 4 bits/param   — meilleure qualité (K-quant)
# Q5_K_M: 5 bits/param   — très bonne qualité
# Q8_0  : 8 bits/param   — quasi-parfait, gros fichier
```

### Utiliser un modèle GGUF

```python
from llama_cpp import Llama

# Charger le modèle GGUF
llm = Llama(
    model_path="./models/gguf/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    n_ctx=4096,        # Taille du contexte
    n_threads=8,       # Nombre de threads CPU
    n_gpu_layers=35,   # Nombre de couches sur GPU (0 = tout sur CPU)
    verbose=False,
)

# Complétion simple
output = llm(
    "Q: What is the capital of France?\nA:",
    max_tokens=32,
    stop=["\n", "Q:"],
    echo=True
)
print(output["choices"][0]["text"])

# Chat avec template
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."},
]

response = llm.create_chat_completion(
    messages=messages,
    max_tokens=256,
    temperature=0.7,
)
print(response["choices"][0]["message"]["content"])
```

### Intégration HuggingFace + llama.cpp

```python
# llama-cpp-python peut être utilisé via le pipeline HF (expérimental)
from transformers import AutoTokenizer
from llama_cpp import Llama

MODEL_PATH = "./models/gguf/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
TOKENIZER_ID = "mistralai/Mistral-7B-Instruct-v0.2"

# Utiliser le tokenizer HF pour les templates de chat
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID)
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)

messages = [{"role": "user", "content": "Qu'est-ce que le machine learning ?"}]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

output = llm(prompt, max_tokens=200, temperature=0.7, stop=["</s>", "[/INST]"])
print(output["choices"][0]["text"])
```

---

## Benchmarking des modèles locaux

```python
import time
from llama_cpp import Llama

def benchmark_llama(model_path, prompt, max_tokens=100, n_runs=3):
    """Benchmark de génération avec llama.cpp"""
    llm = Llama(model_path=model_path, n_ctx=512, verbose=False)

    # Warmup
    llm(prompt, max_tokens=10)

    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        output = llm(prompt, max_tokens=max_tokens, echo=False)
        end = time.perf_counter()
        times.append(end - start)

    n_tokens = output["usage"]["completion_tokens"]
    avg_time = sum(times) / len(times)
    tps = n_tokens / avg_time

    print(f"Modèle       : {model_path.split('/')[-1]}")
    print(f"Tokens gen.  : {n_tokens}")
    print(f"Temps moyen  : {avg_time:.2f}s")
    print(f"Tokens/sec   : {tps:.1f}")
    return tps

# Comparer Q4 vs Q8
prompt = "Once upon a time in a magical kingdom,"
tps_q4 = benchmark_llama("./models/gguf/model.Q4_K_M.gguf", prompt)
tps_q8 = benchmark_llama("./models/gguf/model.Q8_0.gguf", prompt)
print(f"\nQ4 est {tps_q4/tps_q8:.1f}x plus rapide que Q8")
```

---

## Choisir le bon modèle selon le matériel

```
Matériel disponible → Recommandation

RAM 8GB  + pas de GPU  → GGUF Q4_K_M 3B-7B (llama.cpp)
RAM 16GB + pas de GPU  → GGUF Q4_K_M 7B-13B (llama.cpp)
GPU 8GB VRAM           → HF 7B en 4-bit NF4 (bitsandbytes)
GPU 16GB VRAM          → HF 7B en 8-bit ou 13B en 4-bit
GPU 24GB VRAM          → HF 13B FP16 ou 30B en 4-bit
GPU 80GB VRAM (A100)   → HF 70B en FP16
Multi-GPU              → device_map="auto" + accelerate
```

---

## Ollama — Alternative simplifiée

Ollama est un outil qui encapsule llama.cpp dans un serveur REST local.

```bash
# Installation (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Lancer un modèle
ollama run mistral        # Mistral 7B
ollama run llama3         # LLaMA 3 8B
ollama run phi3:mini      # Phi-3 3.8B (léger)
ollama run nomic-embed-text  # Modèle d'embeddings

# Lister les modèles installés
ollama list
```

Utiliser Ollama depuis Python :

```python
import requests
import json

def chat_with_ollama(model: str, prompt: str, system: str = "") -> str:
    """Chat avec un modèle Ollama local via l'API REST"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system} if system else None,
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    # Retirer les messages None
    payload["messages"] = [m for m in payload["messages"] if m]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json=payload
    )
    return response.json()["message"]["content"]

# Exemple d'utilisation
answer = chat_with_ollama(
    model="mistral",
    system="Tu es un assistant expert en Python.",
    prompt="Explique les list comprehensions avec 3 exemples."
)
print(answer)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal montrant `ollama run mistral` avec le modèle qui se télécharge, puis une conversation interactive dans le CLI, et enfin la consommation mémoire avec `ollama ps`
> **Expliquer :** La différence entre Ollama (serveur local complet, gestion automatique du modèle) et llama-cpp-python (bibliothèque Python directe), quand utiliser l'un ou l'autre, et comment Ollama peut être utilisé comme backend pour des outils comme LangChain ou LlamaIndex via son API OpenAI-compatible

---

## Résumé des options

| Approche | Lib | GPU requis | Facilité | Performance |
|----------|-----|-----------|----------|-------------|
| Pipeline HF (FP16) | `transformers` | Oui | Très facile | Maximale |
| HF + INT8 | `transformers` + `bitsandbytes` | Oui (Linux) | Facile | Très bonne |
| HF + NF4 | `transformers` + `bitsandbytes` | Oui (Linux) | Facile | Bonne |
| GGUF CPU | `llama-cpp-python` | Non | Moyen | Correcte |
| GGUF GPU | `llama-cpp-python` | Partiel | Moyen | Bonne |
| Ollama | REST API | Non | Très facile | Bonne |

---

## Suite du cours

Le module suivant ([../Datasets/01-charger-dataset.md](../Datasets/01-charger-dataset.md)) explique comment charger et explorer des datasets avec la bibliothèque `datasets` pour préparer les données d'entraînement.
