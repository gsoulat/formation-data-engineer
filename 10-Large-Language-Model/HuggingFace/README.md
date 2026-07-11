# Formation Hugging Face Transformers

## Objectifs du module

Ce module forme les apprenants à l'utilisation de l'écosystème **Hugging Face** pour :

- Comprendre l'architecture des modèles Transformers
- Utiliser les pipelines prêts à l'emploi pour des tâches NLP courantes
- Charger, exécuter et affiner des modèles pré-entraînés
- Préparer des datasets pour l'entraînement
- Appliquer des techniques de fine-tuning efficaces (LoRA, QLoRA)
- Construire des applications basées sur les embeddings et la recherche sémantique

---

## Prérequis

- Python 3.9+
- Notions de base en machine learning (classification, régression)
- Familiarité avec PyTorch (tensors, autograd)
- Connaissance des concepts NLP de base (tokens, embeddings)

---

## Installation de l'environnement

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Installer les dépendances principales
pip install transformers datasets evaluate accelerate
pip install torch torchvision torchaudio  # CPU uniquement
# pip install torch --index-url https://download.pytorch.org/whl/cu121  # CUDA 12.1

# Outils additionnels
pip install sentence-transformers
pip install peft bitsandbytes  # Pour fine-tuning efficace
pip install huggingface_hub    # CLI et utilitaires Hub

# Se connecter au Hub (nécessite un compte HuggingFace)
huggingface-cli login
```

---

## Structure du cours

```
HuggingFace/
├── README.md                          ← Ce fichier
│
├── Fondamentaux/
│   ├── 01-introduction.md             ← Ecosystème HF, Hub, installation
│   ├── 02-pipeline.md                 ← pipeline() et toutes les tâches
│   └── 03-tokenizers.md               ← Tokenisation, BPE, WordPiece
│
├── Models/
│   ├── 01-charger-modele.md           ← AutoModel, AutoTokenizer
│   ├── 02-inference.md                ← Forward pass, génération de texte
│   └── 03-modeles-locaux.md           ← Exécution locale, quantization
│
├── Datasets/
│   ├── 01-charger-dataset.md          ← load_dataset, splits, features
│   └── 02-preparer-dataset.md         ← map(), filter(), DataCollator
│
├── Fine-Tuning/
│   ├── 01-introduction.md             ← Stratégies de fine-tuning
│   ├── 02-trainer.md                  ← Trainer API complète
│   └── 03-peft-lora.md                ← LoRA et QLoRA
│
├── Embeddings/
│   └── 01-sentence-transformers.md    ← Similarité sémantique, recherche
│
└── exercices/
    ├── exercice-01-classification.md  ← Fine-tune un classifieur
    └── exercice-02-rag-hf.md          ← RAG avec HF
```

---

## Progression recommandée

| Session | Contenu | Durée estimée |
|---------|---------|---------------|
| 1 | Fondamentaux (01 + 02) | 2h |
| 2 | Fondamentaux (03) + Models (01 + 02) | 2h30 |
| 3 | Models (03) + Datasets (01 + 02) | 2h |
| 4 | Fine-Tuning (01 + 02) | 2h30 |
| 5 | Fine-Tuning (03) + Embeddings | 2h |
| 6 | Exercices guidés | 3h |

---

## Ressources officielles

- [Documentation Transformers](https://huggingface.co/docs/transformers)
- [Hugging Face Hub](https://huggingface.co/models)
- [Hugging Face Course (EN)](https://huggingface.co/learn/nlp-course)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [Datasets Documentation](https://huggingface.co/docs/datasets)
- [Forums Hugging Face](https://discuss.huggingface.co/)

---

## Conventions utilisées dans ce cours

> **Note** : Les blocs de code sont testés avec `transformers>=4.40` et `torch>=2.1`.

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE** apparait à chaque point où une démonstration live ou une capture d'écran est nécessaire pour les supports de cours.

Les exemples de code sont auto-suffisants : chaque fichier peut être exécuté de manière indépendante après installation des dépendances.
