# Chapitre 1 : Introduction au Deep Learning

## 🎯 Objectifs

- Comprendre ce qu'est le Deep Learning et pourquoi il dépasse le ML classique
- Connaître l'histoire et les percées majeures du domaine
- Comprendre le neurone artificiel et le perceptron
- Identifier les architectures fondamentales (MLP, CNN, RNN, Transformers)
- Savoir quand utiliser le Deep Learning vs le Machine Learning classique
- Choisir le bon framework (PyTorch vs TensorFlow)

---

## 1. 🧠 Du Machine Learning au Deep Learning

### 1.1 Les limites du Machine Learning classique

Le Machine Learning classique (scikit-learn, XGBoost) fonctionne remarquablement bien sur les **données tabulaires structurées**. Mais il se heurte à un mur dès que les données deviennent complexes :

**Le problème du Feature Engineering manuel :**

```
Données brutes (image) → Feature Engineering MANUEL → Modèle ML → Prédiction
                         ├─ Détection de contours
                         ├─ Histogrammes de couleurs
                         ├─ HOG (Histogram of Oriented Gradients)
                         └─ SIFT descriptors
```

Un ingénieur ML devait **concevoir manuellement** les features pertinentes pour chaque problème. Pour reconnaître un chat dans une image, il fallait décider quelles caractéristiques extraire : contours, textures, couleurs... Un processus long, coûteux, et spécifique à chaque domaine.

### 1.2 Le Deep Learning apprend ses propres features

Le Deep Learning élimine cette étape manuelle :

```
Données brutes (image) → Réseau de neurones profond → Prédiction
                         ├─ Couche 1 : détecte les bords
                         ├─ Couche 2 : détecte les textures
                         ├─ Couche 3 : détecte les formes
                         └─ Couche N : détecte les objets
```

Le réseau apprend **automatiquement** la hiérarchie de features optimale pour la tâche. C'est la révolution fondamentale du Deep Learning.

### 1.3 Comparaison ML classique vs Deep Learning

| Critère | ML classique (sklearn, XGBoost) | Deep Learning (PyTorch, TF) |
|---------|--------------------------------|----------------------------|
| **Feature Engineering** | Manuel, expert requis | Automatique |
| **Données nécessaires** | 100 - 10 000 samples | 10 000 - 10 000 000+ samples |
| **Interprétabilité** | Bonne (feature importance) | Faible (boîte noire) |
| **Données tabulaires** | Excellent | Correct |
| **Images, texte, audio** | Limité | Excellent |
| **Temps d'entraînement** | Minutes | Heures à jours |
| **GPU requis** | Non | Oui (fortement recommandé) |
| **Complexité du code** | Faible | Moyenne à élevée |
| **Performance sur peu de données** | Souvent meilleur | Risque d'overfitting |
| **Performance sur beaucoup de données** | Plafonne | Continue de progresser |

> 💡 **Conseil** : Le Deep Learning n'est **PAS** toujours meilleur que le ML classique. Avec peu de données (<5 000 samples) et des features tabulaires, un Random Forest ou un XGBoost gagne souvent. Ne sortez pas PyTorch par réflexe !

---

## 2. 📜 Histoire et percées majeures

### 2.1 Timeline du Deep Learning

```
1958 ──── Perceptron (Frank Rosenblatt)
│         Premier neurone artificiel. Enthousiasme énorme.
│
1969 ──── "Perceptrons" (Minsky & Papert)
│         Montrent les limites du perceptron → premier "hiver de l'IA"
│
1986 ──── Backpropagation (Rumelhart, Hinton, Williams)
│         Algorithme pour entraîner des réseaux multicouches
│
1998 ──── LeNet-5 (Yann LeCun)
│         Premier CNN pour reconnaissance de chiffres manuscrits
│
2006 ──── Deep Belief Networks (Geoffrey Hinton)
│         Renaissance du Deep Learning
│
2012 ──── AlexNet → Victoire ImageNet
│         ⚡ LE moment fondateur. Erreur réduite de 26% à 16%
│         Le monde découvre la puissance des CNN + GPU
│
2014 ──── GANs (Ian Goodfellow)
│         Génération d'images réalistes
│
2015 ──── ResNet (152 couches !)
│         Les réseaux très profonds deviennent possibles
│
2017 ──── Transformers (Vaswani et al.)
│         "Attention Is All You Need" → révolution NLP
│
2018 ──── BERT (Google)
│         Transfer learning pour le NLP
│
2020 ──── GPT-3 (OpenAI)
│         175 milliards de paramètres, few-shot learning
│
2022 ──── ChatGPT (OpenAI)
│         L'IA générative devient grand public
│
2023 ──── GPT-4, LLaMA (Meta), Mistral
│         Modèles multimodaux, open-source
│
2024 ──── Claude 3, Gemini, LLaMA 3
│         Course à la performance et à l'efficacité
```

### 2.2 Les trois pères fondateurs

| Chercheur | Contribution clé | Prix Turing 2018 |
|-----------|------------------|-------------------|
| **Geoffrey Hinton** | Backpropagation, Deep Belief Networks | Oui |
| **Yann LeCun** | CNN (LeNet), apprentissage auto-supervisé | Oui |
| **Yoshua Bengio** | RNN, attention, représentations | Oui |

### 2.3 Pourquoi le DL a explosé en 2012

Trois facteurs convergents :

1. **Données** : ImageNet (14M d'images labellisées), internet massif
2. **Calcul** : GPU NVIDIA (CUDA), parallélisme massif
3. **Algorithmes** : ReLU, Dropout, Batch Normalization

> 💡 **Conseil** : Comprendre l'histoire aide à comprendre pourquoi certaines architectures existent. Le Transformer n'a pas remplacé les CNN par hasard : il résout des limites fondamentales des RNN.

---

## 3. 🔬 Le neurone artificiel

### 3.1 Analogie biologique

Le neurone artificiel s'inspire (de manière simplifiée) du neurone biologique :

```
Neurone biologique :
   Dendrites (entrées) → Corps cellulaire (traitement) → Axone (sortie)

Neurone artificiel :
   Inputs × Weights + Bias → Fonction d'activation → Output
```

### 3.2 Fonctionnement mathématique

Un neurone artificiel effectue le calcul suivant :

```
         x1 ──w1──┐
         x2 ──w2──┤
         x3 ──w3──┼──→ Σ (somme pondérée) + b ──→ f(z) ──→ y
         ...      │
         xn ──wn──┘

z = w1·x1 + w2·x2 + ... + wn·xn + b
z = Σ(wi·xi) + b
y = f(z)  ← fonction d'activation
```

Où :
- **x** = vecteur d'entrées (features)
- **w** = vecteur de poids (weights) — ce que le réseau **apprend**
- **b** = biais (bias) — un offset
- **f** = fonction d'activation (sigmoid, ReLU, etc.)
- **y** = sortie du neurone

### 3.3 Implémentation Python from scratch

```python
import numpy as np

# Un neurone artificiel en 10 lignes
class Neurone:
    def __init__(self, n_entrees):
        # Initialisation aléatoire des poids et du biais
        self.poids = np.random.randn(n_entrees)
        self.biais = np.random.randn()

    def sigmoid(self, z):
        """Fonction d'activation sigmoid"""
        return 1 / (1 + np.exp(-z))

    def forward(self, x):
        """Propagation avant : calcul de la sortie"""
        # Somme pondérée + biais
        z = np.dot(self.poids, x) + self.biais
        # Application de la fonction d'activation
        return self.sigmoid(z)

# Exemple d'utilisation
neurone = Neurone(n_entrees=3)
entree = np.array([0.5, 0.3, 0.8])
sortie = neurone.forward(entree)
print(f"Sortie du neurone : {sortie:.4f}")  # Valeur entre 0 et 1
```

> 💡 **Conseil** : Ce code n'est PAS comment on fait du Deep Learning en pratique. C'est pour **comprendre** le mécanisme. En vrai, PyTorch gère tout cela automatiquement.

---

## 4. 🧩 Le Perceptron et ses limites

### 4.1 Le Perceptron (1958)

Le perceptron est le plus simple des neurones artificiels : un **classifieur linéaire binaire**.

```python
import numpy as np

class Perceptron:
    def __init__(self, n_entrees, learning_rate=0.01):
        self.poids = np.zeros(n_entrees)
        self.biais = 0
        self.lr = learning_rate

    def predire(self, x):
        """Prédiction : 1 si somme pondérée > 0, sinon 0"""
        z = np.dot(self.poids, x) + self.biais
        return 1 if z > 0 else 0

    def entrainer(self, X, y, epochs=100):
        """Entraînement par correction d'erreur"""
        for _ in range(epochs):
            for xi, yi in zip(X, y):
                prediction = self.predire(xi)
                erreur = yi - prediction
                # Mise à jour des poids
                self.poids += self.lr * erreur * xi
                self.biais += self.lr * erreur

# Entraînement sur AND logique
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_and = np.array([0, 0, 0, 1])

perceptron = Perceptron(n_entrees=2)
perceptron.entrainer(X, y_and)

# Test
for xi in X:
    print(f"{xi} → {perceptron.predire(xi)}")
```

### 4.2 Le problème XOR

Le perceptron ne peut résoudre que des problèmes **linéairement séparables**. Le XOR est le contre-exemple célèbre :

```
AND (séparable ✅)          XOR (NON séparable ❌)

  1 │ ○   ●                  1 │ ●   ○
    │                           │
  0 │ ○   ○                  0 │ ○   ●
    └──────                     └──────
      0   1                       0   1

On peut tracer une droite          Impossible de tracer UNE
séparant ○ et ●                    droite séparant ○ et ●
```

### 4.3 La solution : le Perceptron Multi-Couches (MLP)

En empilant plusieurs couches de neurones, on peut résoudre des problèmes non linéaires :

```
Entrée        Couche cachée       Sortie
  x1 ──────→ [n1] ──────┐
       ╲   ╱              ├──→ [n3] ──→ y
        ╲ ╱               │
       ╱ ╲               ├──→
  x2 ──────→ [n2] ──────┘
```

C'est le **Multi-Layer Perceptron (MLP)**, aussi appelé réseau **Fully Connected** ou **Dense**. C'est le fondement de tout le Deep Learning.

> ⚠️ **Attention** : Un réseau "profond" (deep) signifie qu'il a **plusieurs couches cachées**. C'est le "Deep" dans Deep Learning.

---

## 5. 🏗️ Architectures fondamentales

### 5.1 Vue d'ensemble

```
                    Deep Learning
                         │
        ┌────────────────┼────────────────┐
        │                │                │
       MLP              CNN              Séquentiel
  (Fully Connected)  (Convolutions)       │
        │                │           ┌────┴────┐
  Données tabulaires  Images        RNN/LSTM  Transformers
  Baseline simple     Vidéo         (ancien)  (moderne)
                      Médical                  │
                                          ┌────┴────┐
                                         NLP     Vision
                                         Audio   Multimodal
```

### 5.2 MLP (Multi-Layer Perceptron)

```
[x1] ──→ [h1] ──→ [h1'] ──→ [y1]
[x2] ──→ [h2] ──→ [h2'] ──→ [y2]
[x3] ──→ [h3] ──→ [h3']
[x4] ──→ [h4]

Entrée   Couche 1   Couche 2   Sortie
```

- **Architecture** : couches entièrement connectées (chaque neurone connecté à tous ceux de la couche suivante)
- **Usage** : données tabulaires, baseline, couches finales d'autres architectures
- **Limite** : pas de notion de structure spatiale ou temporelle

### 5.3 CNN (Convolutional Neural Networks)

```
Image ──→ [Conv] ──→ [Pool] ──→ [Conv] ──→ [Pool] ──→ [FC] ──→ Classe
          Détecte     Réduit     Détecte     Réduit    Classification
          les bords   la taille  les formes
```

- **Architecture** : filtres convolutifs qui glissent sur l'image
- **Usage** : images, vidéo, imagerie médicale
- **Avantage** : capture la structure spatiale (pixels voisins)
- **Modèles célèbres** : AlexNet, VGG, ResNet, EfficientNet

### 5.4 RNN / LSTM (Recurrent Neural Networks)

```
x1 ──→ [h] ──→ x2 ──→ [h] ──→ x3 ──→ [h] ──→ sortie
        │               │               │
        └───état─────→ └───état─────→ └───état
```

- **Architecture** : boucle de rétroaction (mémoire des étapes précédentes)
- **Usage** : séries temporelles, texte (historiquement)
- **Limite** : difficulté avec les longues séquences (vanishing gradient)
- **LSTM** : version améliorée avec mécanisme de portes (forget, input, output)

> ⚠️ **Attention** : Les RNN/LSTM sont aujourd'hui largement remplacés par les Transformers pour le NLP. Ils restent utiles pour certaines séries temporelles.

### 5.5 Transformers

```
Entrée ──→ [Self-Attention] ──→ [Feed-Forward] ──→ Sortie
           "Quels mots sont      Transformation
            importants pour       non-linéaire
            comprendre ce mot ?"
```

- **Architecture** : mécanisme d'attention (chaque élément regarde tous les autres)
- **Usage** : NLP (BERT, GPT), vision (ViT), audio, multimodal
- **Avantage** : parallélisable (contrairement aux RNN), capture les dépendances longues
- **Modèles célèbres** : BERT, GPT-4, Claude, LLaMA, Mistral

### 5.6 Table comparative

| Architecture | Données typiques | Forces | Faiblesses | Exemple de modèle |
|-------------|------------------|--------|------------|-------------------|
| **MLP** | Tabulaires | Simple, baseline | Pas de structure | Réseau dense |
| **CNN** | Images, vidéo | Structure spatiale | Pas de séquences | ResNet, EfficientNet |
| **RNN/LSTM** | Séquences | Mémoire temporelle | Lent, séq. longues | LSTM, GRU |
| **Transformer** | Tout (texte, image, audio) | Parallèle, long-range | Coûteux en mémoire | GPT, BERT, ViT |

---

## 6. ✅ Quand utiliser le Deep Learning ?

### 6.1 Le DL est adapté quand...

- ✅ **Images** : classification, détection d'objets, segmentation
- ✅ **Texte** : NLP, traduction, résumé, chatbots
- ✅ **Audio** : reconnaissance vocale, musique, sons
- ✅ **Vidéo** : action recognition, tracking
- ✅ **Données non structurées** en général
- ✅ **Grandes quantités de données** (>10 000 samples)
- ✅ **Features complexes** que l'humain ne sait pas concevoir

### 6.2 Le DL n'est PAS adapté quand...

- ❌ **Données tabulaires simples** → scikit-learn ou XGBoost suffisent
- ❌ **Besoin d'interprétabilité complète** → régression logistique, arbre de décision
- ❌ **Peu de données** (<1 000 samples) → risque d'overfitting massif
- ❌ **Contraintes de latence extrêmes** (modèle doit tourner en <1ms)
- ❌ **Pas de GPU disponible** → l'entraînement sera très lent
- ❌ **Budget limité** → le coût GPU peut être significatif

### 6.3 Arbre de décision : ML ou DL ?

```
Votre problème
     │
     ├── Données tabulaires structurées ?
     │   ├── Oui → XGBoost / Random Forest (ML classique)
     │   └── Non ↓
     │
     ├── Images, texte, audio, vidéo ?
     │   ├── Oui → Deep Learning ✅
     │   └── Non ↓
     │
     ├── Plus de 10 000 samples ?
     │   ├── Oui → Deep Learning peut aider
     │   └── Non → ML classique probablement meilleur
     │
     └── Besoin d'interprétabilité ?
         ├── Oui → ML classique (SHAP, LIME si DL nécessaire)
         └── Non → Deep Learning ✅
```

> 💡 **Conseil de pro** : Avant de sortir PyTorch, demandez-vous toujours : "Est-ce qu'un XGBoost ne ferait pas le travail ?" Dans une compétition Kaggle sur données tabulaires, XGBoost/LightGBM battent encore souvent le DL.

---

## 7. 🛠️ Les frameworks Deep Learning

### 7.1 PyTorch vs TensorFlow

| Critère | PyTorch | TensorFlow |
|---------|---------|------------|
| **Développeur** | Meta (Facebook AI) | Google Brain |
| **Approche** | Define-by-run (dynamique) | Define-and-run → Define-by-run (TF 2.x) |
| **Debugging** | Facile (Python natif) | Plus complexe |
| **Recherche** | Standard de facto (~80% des publications) | En déclin |
| **Production** | TorchServe, ONNX | TF Serving, TFLite (plus mature) |
| **Communauté** | En forte croissance | Grande mais stagnante |
| **Documentation** | Excellente | Bonne mais dispersée |
| **API haut niveau** | torch.nn | Keras (intégré) |
| **Mobile** | PyTorch Mobile | TFLite (plus mature) |
| **Courbe d'apprentissage** | Plus douce | Plus raide |

### 7.2 Pourquoi ce cours utilise PyTorch

1. **Standard en recherche** : 80%+ des publications NeurIPS/ICML utilisent PyTorch
2. **Pythonic** : le code PyTorch ressemble à du Python standard
3. **Debug facile** : breakpoints, print() fonctionnent naturellement
4. **Communauté active** : plus de ressources, tutoriels, modèles pré-entraînés
5. **Hugging Face** : l'écosystème HF (Transformers, Datasets) est natif PyTorch

### 7.3 Autres frameworks

| Framework | Usage principal | Notes |
|-----------|----------------|-------|
| **Keras** | API haut niveau (intégré à TF) | Excellent pour débuter, limité pour la recherche |
| **JAX** | Recherche avancée (Google DeepMind) | Fonctionnel, JIT compilation, très performant |
| **ONNX** | Interopérabilité | Format d'échange entre frameworks |
| **Hugging Face** | NLP, modèles pré-entraînés | Basé sur PyTorch, incontournable |

> 💡 **Conseil** : PyTorch est le standard en recherche et de plus en plus en production. TensorFlow reste fort en déploiement mobile (TFLite). Apprenez PyTorch en premier, c'est le choix le plus polyvalent en 2024.

### 7.4 Installation rapide

```python
# Installation PyTorch (CPU)
# uv add torch torchvision torchaudio

# Installation PyTorch (GPU CUDA)
# uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Vérification de l'installation
import torch

print(f"PyTorch version : {torch.__version__}")
print(f"CUDA disponible : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU : {torch.cuda.get_device_name(0)}")
    print(f"Mémoire GPU : {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} Go")
else:
    print("Mode CPU uniquement (OK pour débuter)")
```

---

## 8. ⚡ GPU et calcul

### 8.1 Pourquoi le GPU est essentiel

Le Deep Learning repose sur des **multiplications matricielles massives**. Le GPU excelle dans ce domaine grâce à son **parallélisme massif** :

| Critère | CPU | GPU |
|---------|-----|-----|
| **Coeurs** | 8-32 coeurs puissants | 1 000 - 16 000 coeurs simples |
| **Optimisé pour** | Tâches séquentielles complexes | Calcul parallèle massif |
| **Deep Learning** | Lent (heures → jours) | Rapide (minutes → heures) |
| **Multiplication matricielle** | Séquentielle | Massivement parallèle |

```
CPU (séquentiel) :          GPU (parallèle) :
[A×B] → [C×D] → [E×F]     [A×B] [C×D] [E×F] ← tous en même temps !
    Temps : 3 unités             Temps : 1 unité
```

### 8.2 L'écosystème GPU

- **NVIDIA CUDA** : plateforme de calcul GPU (standard de facto pour le DL)
- **cuDNN** : bibliothèque optimisée pour les réseaux de neurones
- **NVIDIA A100, H100** : GPU de datacenter pour l'entraînement
- **RTX 4090** : GPU grand public utilisable pour le DL
- **Apple Silicon (M1/M2/M3)** : Metal Performance Shaders (MPS) via PyTorch

### 8.3 Options pour démarrer sans investir

| Solution | GPU | Coût | Durée |
|----------|-----|------|-------|
| **Google Colab** | T4 (gratuit), A100 (payant) | Gratuit / 10€/mois | Sessions limitées |
| **Kaggle Notebooks** | T4 ou P100 | Gratuit | 30h GPU/semaine |
| **Lightning AI** | GPU variés | Gratuit (limité) | Sessions |
| **AWS/GCP/Azure** | A100, H100 | ~2-10€/h | Illimité |
| **Lambda Labs** | A100, H100 | ~1-3€/h | Illimité |

> 💡 **Conseil** : Pour débuter, Google Colab suffit largement. Pas besoin d'acheter un GPU ! Vous pouvez entraîner un CNN sur MNIST en quelques minutes avec un GPU gratuit.

### 8.4 Vérifier et utiliser le GPU avec PyTorch

```python
import torch

# Détecter le device disponible
if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f"Utilisation du GPU : {torch.cuda.get_device_name(0)}")
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = torch.device('mps')  # Apple Silicon
    print("Utilisation du GPU Apple Silicon (MPS)")
else:
    device = torch.device('cpu')
    print("Utilisation du CPU")

# Envoyer un tensor sur le GPU
x = torch.randn(1000, 1000).to(device)
y = torch.randn(1000, 1000).to(device)

# Le calcul s'effectue sur le GPU automatiquement
z = x @ y  # Multiplication matricielle sur GPU
print(f"Résultat sur : {z.device}")
```

> ⚠️ **Attention** : Tous les tensors d'un calcul doivent être sur le **même device**. Si le modèle est sur GPU mais les données sur CPU, vous aurez une erreur. Pensez toujours à `.to(device)`.

---

## 📝 Points clés à retenir

- Le Deep Learning **apprend automatiquement ses features**, contrairement au ML classique
- Un neurone artificiel calcule une **somme pondérée + activation**
- Le perceptron est limité aux problèmes linéaires ; le MLP résout cette limitation
- **4 architectures fondamentales** : MLP, CNN, RNN/LSTM, Transformers
- Le DL excelle sur les données **non structurées** (images, texte, audio)
- Pour les données **tabulaires**, le ML classique (XGBoost) reste souvent meilleur
- **PyTorch** est le framework standard (recherche + production)
- Le **GPU** est essentiel pour l'entraînement (Google Colab pour débuter)

## ✅ Checklist de validation

- [ ] Je sais expliquer la différence entre ML classique et Deep Learning
- [ ] Je comprends le fonctionnement d'un neurone artificiel (weights, bias, activation)
- [ ] Je connais le problème XOR et pourquoi il nécessite un MLP
- [ ] Je peux nommer les 4 architectures fondamentales et leurs cas d'usage
- [ ] Je sais quand utiliser le DL vs le ML classique
- [ ] J'ai installé PyTorch et vérifié la disponibilité GPU
- [ ] Je comprends pourquoi le GPU est important pour le Deep Learning

---

**Prochain chapitre :** [02 - Réseaux de neurones](./02-reseaux-neurones.md)

[Retour au sommaire](../README.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [But what is a neural network?](https://www.youtube.com/results?search_query=3blue1brown+but+what+is+a+neural+network) | 3Blue1Brown | EN | L'intuition visuelle d'un réseau (la référence absolue) |
| [Introduction au Deep Learning](https://www.youtube.com/results?search_query=machine+learnia+deep+learning+introduction) | Machine Learnia | FR | ML vs DL, à quoi sert un réseau |
| [Neural Networks explained](https://www.youtube.com/results?search_query=statquest+neural+networks+part+1) | StatQuest | EN | Le neurone et les couches, pas à pas |

> 🧭 Rappel : garde le [chapitre 0 — intuition & analogies](00-intuition-analogies.md) sous les yeux.
