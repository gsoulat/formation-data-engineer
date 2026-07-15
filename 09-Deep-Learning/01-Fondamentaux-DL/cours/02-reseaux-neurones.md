# Chapitre 2 : Réseaux de Neurones – Le Moteur du Deep Learning

## 🎯 Objectifs

- Comprendre la forward propagation (flux de données dans le réseau)
- Maîtriser les fonctions d'activation et savoir quand les utiliser
- Comprendre les fonctions de coût (loss functions) et leur importance
- Comprendre la backpropagation et le gradient descent
- Savoir choisir un optimizer et monitorer l'entraînement
- Diagnostiquer les problèmes d'entraînement (overfitting, underfitting, oscillations)

---

## 1. 🔄 Forward Propagation

### 1.1 Le flux de données

La forward propagation est le processus par lequel les données traversent le réseau de l'entrée vers la sortie :

```
Entrée (X)     Couche 1        Couche 2        Sortie
  [x1]    →   [h1]   →       [h1']   →       [y1]
  [x2]    →   [h2]   →       [h2']   →       [y2]
  [x3]    →   [h3]   →       [h3']
  [x4]    →   [h4]

         Z1 = W1·X + b1    Z2 = W2·A1 + b2
         A1 = f(Z1)        A2 = f(Z2)         ŷ = A2
```

### 1.2 Calcul matriciel

Pour chaque couche, le calcul est :

```
Z = W · X + b       ← combinaison linéaire
A = activation(Z)   ← transformation non-linéaire
```

Où :
- **W** : matrice de poids (shape: [neurones_sortie, neurones_entrée])
- **X** : vecteur d'entrée (ou matrice pour un batch)
- **b** : vecteur de biais
- **Z** : pré-activation (avant la fonction d'activation)
- **A** : activation (sortie de la couche)

### 1.3 Implémentation from scratch

```python
import numpy as np

class ReseauSimple:
    """Réseau de neurones à 2 couches, implémenté from scratch"""

    def __init__(self, n_entrees, n_cachees, n_sorties):
        # Initialisation des poids (Xavier initialization)
        self.W1 = np.random.randn(n_cachees, n_entrees) * np.sqrt(2.0 / n_entrees)
        self.b1 = np.zeros((n_cachees, 1))
        self.W2 = np.random.randn(n_sorties, n_cachees) * np.sqrt(2.0 / n_cachees)
        self.b2 = np.zeros((n_sorties, 1))

    def relu(self, z):
        """Fonction d'activation ReLU"""
        return np.maximum(0, z)

    def sigmoid(self, z):
        """Fonction d'activation Sigmoid"""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    def forward(self, X):
        """Forward propagation à travers le réseau"""
        # Couche 1 : entrée → couche cachée
        self.Z1 = self.W1 @ X + self.b1      # Combinaison linéaire
        self.A1 = self.relu(self.Z1)           # Activation ReLU

        # Couche 2 : couche cachée → sortie
        self.Z2 = self.W2 @ self.A1 + self.b2  # Combinaison linéaire
        self.A2 = self.sigmoid(self.Z2)         # Activation Sigmoid (sortie)

        return self.A2

# Exemple : réseau pour classification binaire
reseau = ReseauSimple(n_entrees=4, n_cachees=8, n_sorties=1)

# Données d'entrée (4 features, 1 sample)
X = np.array([[0.5], [0.3], [-0.1], [0.8]])
prediction = reseau.forward(X)
print(f"Prédiction : {prediction[0, 0]:.4f}")  # Probabilité entre 0 et 1
```

> 💡 **Conseil** : Ce code est pédagogique. En pratique, PyTorch fait tout cela en quelques lignes. Mais comprendre le calcul matriciel sous-jacent est essentiel pour diagnostiquer les problèmes.

---

## 2. ⚡ Fonctions d'activation

Les fonctions d'activation introduisent la **non-linéarité** dans le réseau. Sans elles, un réseau multicouche serait équivalent à un seul neurone linéaire (composition de fonctions linéaires = fonction linéaire).

### 2.1 Sigmoid (σ)

```
σ(z) = 1 / (1 + e^(-z))

Sortie : [0, 1]

        1 |          ___________
          |        /
     0.5 |------/
          |    /
        0 |___/
          └──────────────────
           -6    0    6
```

**Propriétés :**
- Sortie bornée entre 0 et 1 → interprétable comme une probabilité
- Gradient max = 0.25 (en z=0)
- Utilisée principalement en **couche de sortie** pour la classification binaire

**Problème majeur : Vanishing Gradient**
- Pour |z| > 5, le gradient est quasiment nul (~0)
- Les couches profondes reçoivent un signal d'apprentissage très faible
- Le réseau arrête d'apprendre dans ses premières couches

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_derivee(z):
    s = sigmoid(z)
    return s * (1 - s)

# Démonstration du vanishing gradient
print(f"Gradient en z=0  : {sigmoid_derivee(0):.4f}")   # 0.25
print(f"Gradient en z=5  : {sigmoid_derivee(5):.6f}")   # 0.0066
print(f"Gradient en z=10 : {sigmoid_derivee(10):.8f}")  # 0.0000454
# → Le gradient "disparaît" pour les grandes valeurs
```

### 2.2 Tanh (Tangente hyperbolique)

```
tanh(z) = (e^z - e^(-z)) / (e^z + e^(-z))

Sortie : [-1, 1]

        1 |          ___________
          |        /
        0 |------/──────────────
          |    /
       -1 |___/
          └──────────────────
           -6    0    6
```

**Propriétés :**
- Sortie centrée sur 0 (contrairement à sigmoid)
- Gradient max = 1 (en z=0), meilleur que sigmoid
- Souffre aussi du vanishing gradient mais moins que sigmoid
- Utilisée dans certaines architectures (LSTM, normalisation)

### 2.3 ReLU (Rectified Linear Unit)

```
ReLU(z) = max(0, z)

Sortie : [0, +∞)

          |       /
          |      /
          |     /
          |    /
        0 |___/──────────────
          └──────────────────
           -4    0    4
```

**Propriétés :**
- Extrêmement simple et rapide à calculer
- Pas de vanishing gradient pour z > 0
- **Standard de facto** pour les couches cachées depuis 2012
- Gradient = 1 pour z > 0, gradient = 0 pour z < 0

**Problème : Dying ReLU**
- Si z < 0, le gradient est exactement 0
- Un neurone "mort" ne peut plus jamais se réactiver
- Peut arriver avec un learning rate trop élevé

```python
import numpy as np

def relu(z):
    return np.maximum(0, z)

def relu_derivee(z):
    return (z > 0).astype(float)

# Démonstration
z = np.array([-3, -1, 0, 1, 3])
print(f"ReLU({z})    = {relu(z)}")          # [0, 0, 0, 1, 3]
print(f"ReLU'({z})   = {relu_derivee(z)}")  # [0, 0, 0, 1, 1]
```

### 2.4 Leaky ReLU

```
LeakyReLU(z) = z     si z > 0
               α·z   si z ≤ 0   (α = 0.01 typiquement)

Sortie : (-∞, +∞)

          |       /
          |      /
          |     /
          |    /
        0 |___/──────────────
          └─/────────────────
          (pente très faible pour z < 0)
```

**Propriétés :**
- Résout le problème du dying ReLU
- Permet un petit gradient même pour z < 0
- Variante : **Parametric ReLU (PReLU)** où α est appris

### 2.5 Softmax

```
Softmax(zi) = e^zi / Σ(e^zj)

Entrée : vecteur de scores → Sortie : vecteur de probabilités (somme = 1)
```

**Propriétés :**
- Transforme des scores en **distribution de probabilités**
- Utilisée exclusivement en **couche de sortie** pour la classification multi-classes
- Chaque sortie ∈ [0, 1] et la somme = 1

```python
import numpy as np

def softmax(z):
    # Trick de stabilité numérique : soustraire le max
    z_stable = z - np.max(z)
    exp_z = np.exp(z_stable)
    return exp_z / np.sum(exp_z)

# Exemple : classification en 3 classes
scores = np.array([2.0, 1.0, 0.1])
probabilites = softmax(scores)
print(f"Scores  : {scores}")
print(f"Probas  : {probabilites.round(4)}")
# [0.6590, 0.2424, 0.0986] → somme = 1.0
print(f"Somme   : {probabilites.sum():.4f}")
print(f"Classe prédite : {np.argmax(probabilites)}")  # Classe 0
```

### 2.6 Table récapitulative

| Activation | Range | Usage | Avantages | Inconvénients |
|-----------|-------|-------|-----------|---------------|
| **Sigmoid** | [0, 1] | Sortie (binaire) | Probabilité | Vanishing gradient |
| **Tanh** | [-1, 1] | Couches cachées (rare) | Centrée sur 0 | Vanishing gradient |
| **ReLU** | [0, +∞) | Couches cachées | Simple, rapide, pas de vanishing | Dying ReLU |
| **Leaky ReLU** | (-∞, +∞) | Couches cachées | Pas de dying ReLU | Un hyperparamètre (α) |
| **Softmax** | [0, 1] (somme=1) | Sortie (multi-classes) | Probabilités | Seulement en sortie |

### 2.7 Règles de choix

```
Couches cachées → ReLU (par défaut)
                  Leaky ReLU (si problème de dying ReLU)

Couche de sortie → Sigmoid    (classification binaire)
                   Softmax    (classification multi-classes)
                   Linéaire   (régression, pas d'activation)
                   Tanh       (sortie bornée [-1, 1])
```

> 💡 **Conseil de pro** : En 2024, utilisez **ReLU par défaut** pour les couches cachées et **Softmax** pour la sortie en classification multi-classes. Ne cherchez pas à optimiser la fonction d'activation avant d'avoir optimisé le learning rate et l'architecture.

---

## 3. 📊 Fonctions de coût (Loss Functions)

La fonction de coût (loss function) mesure l'**écart entre la prédiction du modèle et la réalité**. C'est la métrique que le modèle cherche à minimiser pendant l'entraînement.

> 💡 **Conseil de pro** : La loss function est votre **boussole**. Si elle ne reflète pas le problème métier, le modèle apprendra la mauvaise chose. Choisissez-la avec soin.

### 3.1 MSE – Mean Squared Error (Régression)

```
MSE = (1/n) × Σ(yi - ŷi)²

yi = valeur réelle
ŷi = prédiction du modèle
```

**Propriétés :**
- Pénalise fortement les grandes erreurs (erreur au carré)
- Toujours positive, minimum = 0 (prédiction parfaite)
- Sensible aux outliers (une erreur de 10 → pénalité de 100)

```python
import numpy as np

def mse(y_vrai, y_pred):
    """Mean Squared Error"""
    return np.mean((y_vrai - y_pred) ** 2)

# Exemple
y_vrai = np.array([3.0, 5.0, 2.5, 7.0])
y_pred = np.array([2.8, 5.2, 2.3, 6.5])
print(f"MSE : {mse(y_vrai, y_pred):.4f}")  # 0.0850

# Impact d'un outlier
y_pred_outlier = np.array([2.8, 5.2, 2.3, 2.0])  # Erreur de 5 sur la dernière
print(f"MSE avec outlier : {mse(y_vrai, y_pred_outlier):.4f}")  # 6.3325
# → L'outlier fait exploser la MSE !
```

**Variantes :**
- **MAE** (Mean Absolute Error) : `(1/n) × Σ|yi - ŷi|` — moins sensible aux outliers
- **Huber Loss** : combinaison MSE/MAE, robuste aux outliers
- **RMSE** : racine de la MSE, même unité que les données

### 3.2 Binary Cross-Entropy (Classification binaire)

```
BCE = -(1/n) × Σ[yi·log(ŷi) + (1-yi)·log(1-ŷi)]

yi ∈ {0, 1}     → classe réelle
ŷi ∈ (0, 1)     → probabilité prédite
```

**Intuition :**
- Si la classe réelle est 1, on veut que ŷ soit proche de 1 → `log(ŷ)` est maximisé
- Si la classe réelle est 0, on veut que ŷ soit proche de 0 → `log(1-ŷ)` est maximisé
- La loss pénalise exponentiellement les **prédictions confiantes mais fausses**

```python
import numpy as np

def binary_cross_entropy(y_vrai, y_pred):
    """Binary Cross-Entropy Loss"""
    # Clip pour éviter log(0)
    y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
    return -np.mean(
        y_vrai * np.log(y_pred) + (1 - y_vrai) * np.log(1 - y_pred)
    )

# Bonnes prédictions
y_vrai = np.array([1, 0, 1, 1])
y_pred_bon = np.array([0.9, 0.1, 0.8, 0.95])
print(f"BCE (bon modèle)    : {binary_cross_entropy(y_vrai, y_pred_bon):.4f}")

# Mauvaises prédictions
y_pred_mauvais = np.array([0.2, 0.8, 0.3, 0.4])
print(f"BCE (mauvais modèle): {binary_cross_entropy(y_vrai, y_pred_mauvais):.4f}")

# Prédiction confiante et FAUSSE (la pire situation)
y_pred_confiant_faux = np.array([0.01, 0.99, 0.01, 0.01])
print(f"BCE (confiant faux) : {binary_cross_entropy(y_vrai, y_pred_confiant_faux):.4f}")
# → Loss très élevée ! Le modèle est pénalisé pour être confiant et faux
```

### 3.3 Categorical Cross-Entropy (Classification multi-classes)

```
CCE = -(1/n) × Σ Σ(yij · log(ŷij))

yij = 1 si le sample i appartient à la classe j (one-hot)
ŷij = probabilité prédite pour la classe j (sortie softmax)
```

```python
import numpy as np

def categorical_cross_entropy(y_vrai_onehot, y_pred):
    """Categorical Cross-Entropy Loss"""
    y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
    return -np.mean(np.sum(y_vrai_onehot * np.log(y_pred), axis=1))

# 3 classes, 2 samples
y_vrai = np.array([[1, 0, 0],   # Classe 0
                    [0, 0, 1]])  # Classe 2

y_pred_bon = np.array([[0.8, 0.1, 0.1],   # Bonne prédiction classe 0
                        [0.1, 0.1, 0.8]])  # Bonne prédiction classe 2

y_pred_mauvais = np.array([[0.2, 0.5, 0.3],   # Mauvaise prédiction
                            [0.5, 0.3, 0.2]])  # Mauvaise prédiction

print(f"CCE (bon)     : {categorical_cross_entropy(y_vrai, y_pred_bon):.4f}")
print(f"CCE (mauvais) : {categorical_cross_entropy(y_vrai, y_pred_mauvais):.4f}")
```

### 3.4 Comment choisir sa loss function

| Problème | Loss Function | Activation de sortie | PyTorch |
|----------|---------------|---------------------|---------|
| **Régression** | MSE | Linéaire (aucune) | `nn.MSELoss()` |
| **Régression robuste** | Huber / L1 | Linéaire | `nn.HuberLoss()` |
| **Classification binaire** | Binary Cross-Entropy | Sigmoid | `nn.BCEWithLogitsLoss()` |
| **Classification multi-classes** | Categorical Cross-Entropy | Softmax | `nn.CrossEntropyLoss()` |
| **Multi-label** | Binary Cross-Entropy | Sigmoid (par label) | `nn.BCEWithLogitsLoss()` |
| **Segmentation** | Dice Loss + CE | Softmax | Custom |

> ⚠️ **Attention** : En PyTorch, `nn.CrossEntropyLoss()` **inclut déjà le Softmax**. Ne mettez PAS de Softmax dans votre réseau si vous utilisez cette loss. C'est une erreur très courante chez les débutants.

---

## 4. 🔙 Backpropagation

### 4.1 Le principe

La backpropagation (rétropropagation) est l'algorithme qui permet au réseau d'**apprendre**. Il propage l'erreur de la sortie vers l'entrée pour ajuster les poids :

```
Forward (→) : Données → Couche 1 → Couche 2 → ... → Prédiction → Loss
Backward (←): ∂Loss/∂W ← Couche 1 ← Couche 2 ← ... ← ∂Loss/∂ŷ ← Loss

1. Forward : calculer la prédiction
2. Calculer la loss (écart prédiction vs réalité)
3. Backward : calculer les gradients (∂Loss/∂Wi pour chaque poids)
4. Mettre à jour les poids : Wi = Wi - lr × ∂Loss/∂Wi
```

### 4.2 La règle de la chaîne (Chain Rule)

Le coeur mathématique de la backpropagation est la **règle de la chaîne** :

```
Si y = f(g(x)), alors dy/dx = f'(g(x)) × g'(x)

Pour un réseau :
∂Loss/∂W1 = ∂Loss/∂A2 × ∂A2/∂Z2 × ∂Z2/∂A1 × ∂A1/∂Z1 × ∂Z1/∂W1
```

Chaque couche multiplie son gradient local par le gradient reçu de la couche suivante.

### 4.3 Exemple pas à pas

Prenons un réseau minimal : 1 neurone, 1 entrée, MSE loss.

```python
import numpy as np

# Réseau : 1 neurone (1 poids, 1 biais, sigmoid)
# Forward : ŷ = sigmoid(w·x + b)
# Loss : L = (y - ŷ)²

# Données
x = 1.0       # Entrée
y = 0.0       # Cible (classe 0)
w = 0.5       # Poids initial
b = 0.1       # Biais initial
lr = 0.1      # Learning rate

print("=== Entraînement pas à pas ===")
for step in range(5):
    # --- FORWARD ---
    z = w * x + b                        # Pré-activation
    y_pred = 1 / (1 + np.exp(-z))       # Sigmoid
    loss = (y - y_pred) ** 2             # MSE

    # --- BACKWARD (calcul des gradients) ---
    # ∂L/∂ŷ = 2(ŷ - y)
    dL_dy_pred = 2 * (y_pred - y)

    # ∂ŷ/∂z = sigmoid(z) × (1 - sigmoid(z))
    dy_pred_dz = y_pred * (1 - y_pred)

    # ∂z/∂w = x,  ∂z/∂b = 1
    dz_dw = x
    dz_db = 1

    # Chain rule : ∂L/∂w = ∂L/∂ŷ × ∂ŷ/∂z × ∂z/∂w
    dL_dw = dL_dy_pred * dy_pred_dz * dz_dw
    dL_db = dL_dy_pred * dy_pred_dz * dz_db

    # --- MISE A JOUR ---
    w = w - lr * dL_dw
    b = b - lr * dL_db

    print(f"Step {step}: loss={loss:.4f}, ŷ={y_pred:.4f}, w={w:.4f}, b={b:.4f}")
```

### 4.4 Schéma du flux Forward / Backward

```
         FORWARD →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→
         ┌─────┐     ┌─────────┐     ┌─────────┐     ┌──────┐
  X ───→ │ W·X │ ──→ │  + bias │ ──→ │  ReLU   │ ──→ │ Loss │
         │ +b  │     │         │     │         │     │      │
         └─────┘     └─────────┘     └─────────┘     └──────┘
         │ ∂Z/∂W│     │         │     │ ∂A/∂Z   │     │∂L/∂A │
         ←←←←←←←     ←←←←←←←←←←     ←←←←←←←←←←     ←←←←←←←
         ←←←←←← BACKWARD ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

> 💡 **Conseil** : Vous n'avez **pas besoin** de calculer les gradients à la main. PyTorch le fait automatiquement avec **autograd**. Mais comprendre le principe est essentiel pour diagnostiquer les problèmes (vanishing gradients, exploding gradients).

---

## 5. 📉 Gradient Descent et variantes

### 5.1 Le principe du Gradient Descent

Le gradient descent (descente de gradient) est l'algorithme d'optimisation qui met à jour les poids :

```
Nouveau poids = Ancien poids - learning_rate × gradient

W = W - η × ∂Loss/∂W
```

**Analogie :** Imaginez descendre une montagne dans le brouillard. Le gradient vous indique la direction de la pente la plus raide. Le learning rate est la taille de vos pas.

```
        Loss
     ╱╲
    ╱  ╲         ← lr trop grand : on oscille
   ╱    ╲  ╱╲
  ╱      ╲╱  ╲
 ╱    ●→→→→→→→●  ← lr correct : on converge
╱               ╲
                 minimum
```

### 5.2 Batch GD vs SGD vs Mini-batch

| Variante | Données par mise à jour | Avantages | Inconvénients |
|----------|------------------------|-----------|---------------|
| **Batch GD** | Toutes les données | Stable, convergence garantie | Lent, mémoire énorme |
| **SGD** | 1 sample | Rapide, peut sortir des minima locaux | Très bruité |
| **Mini-batch SGD** | 32-256 samples | Bon compromis | Hyperparamètre (batch_size) |

> 💡 **Conseil** : En pratique, on utilise toujours le **mini-batch SGD** avec un batch_size entre 32 et 256. Le terme "SGD" dans les frameworks désigne en réalité le mini-batch SGD.

### 5.3 SGD avec Momentum

Le momentum accélère la convergence en ajoutant une "inertie" au mouvement :

```
v = β × v_precedent + ∂Loss/∂W    (accumulation du moment)
W = W - η × v                      (mise à jour avec moment)
```

Comme une bille qui roule : elle accumule de la vitesse dans les directions cohérentes et amortit les oscillations.

```python
# SGD avec Momentum en PyTorch
import torch.optim as optim

optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
```

### 5.4 Adam (Adaptive Moment Estimation)

Adam est le **standard actuel** pour l'entraînement de réseaux de neurones. Il combine :
- **Momentum** (moyenne mobile des gradients)
- **RMSprop** (adaptation du learning rate par paramètre)

```
m = β1 × m + (1-β1) × gradient          ← Moment 1 (direction)
v = β2 × v + (1-β2) × gradient²         ← Moment 2 (magnitude)
W = W - η × m / (√v + ε)                ← Mise à jour adaptative
```

**Pourquoi Adam est populaire :**
- Learning rate adaptatif pour chaque paramètre
- Fonctionne bien "out of the box" avec les hyperparamètres par défaut
- Converge généralement plus vite que SGD

```python
# Adam en PyTorch — le standard
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Variante : AdamW (Adam avec Weight Decay correct)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
```

> 💡 **Conseil de pro** : Commencez **TOUJOURS** avec Adam et `lr=1e-3`. C'est la baseline universelle. Ne passez à SGD+Momentum que si vous avez le temps de tuner et que vous visez les derniers % de performance.

### 5.5 Learning Rate Scheduling

Le learning rate peut varier pendant l'entraînement pour améliorer la convergence :

| Scheduler | Principe | PyTorch | Quand l'utiliser |
|-----------|----------|---------|------------------|
| **StepLR** | Divise le lr tous les N epochs | `StepLR(optimizer, step_size=30, gamma=0.1)` | Baseline simple |
| **CosineAnnealing** | Décroissance en cosinus | `CosineAnnealingLR(optimizer, T_max=100)` | Entraînement long |
| **ReduceLROnPlateau** | Réduit si la métrique stagne | `ReduceLROnPlateau(optimizer, patience=10)` | Choix le plus sûr |
| **OneCycleLR** | Augmente puis diminue | `OneCycleLR(optimizer, max_lr=0.01)` | Performance maximale |
| **Warmup** | Commence petit puis augmente | Custom ou transformers | Transformers |

```python
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Réduire le lr si la val_loss ne s'améliore pas pendant 5 epochs
scheduler = ReduceLROnPlateau(
    optimizer,
    mode='min',        # On minimise la loss
    factor=0.5,        # Diviser le lr par 2
    patience=5,        # Attendre 5 epochs sans amélioration
    verbose=True       # Afficher quand le lr change
)

# Dans la boucle d'entraînement :
# scheduler.step(val_loss)
```

### 5.6 Table comparative des optimizers

| Optimizer | Learning Rate | Convergence | Mémoire | Usage recommandé |
|-----------|--------------|-------------|---------|-------------------|
| **SGD** | Fixe | Lent mais précis | Faible | Fine-tuning final |
| **SGD + Momentum** | Fixe | Plus rapide | Faible | CNN classiques |
| **Adam** | Adaptatif | Rapide | 2× SGD | Baseline universelle |
| **AdamW** | Adaptatif + WD | Rapide | 2× SGD | Standard actuel |
| **LAMB** | Adaptatif | Très rapide | 2× SGD | Grands batch sizes |

---

## 6. 📊 Métriques et monitoring de l'entraînement

### 6.1 Les courbes de loss : votre tableau de bord

Les courbes de loss (train vs validation) sont le **diagnostic principal** de votre entraînement.

### 6.2 Cas 1 : Underfitting

```
Loss
  │
  │ ──── Train loss (haute, ne descend plus)
  │ ──── Val loss (haute, ne descend plus)
  │
  └─────────────────── Epochs

Diagnostic : le modèle est trop simple ou le lr trop faible
Solutions :
  → Augmenter la capacité du réseau (plus de couches/neurones)
  → Augmenter le learning rate
  → Entraîner plus longtemps
  → Vérifier les données
```

### 6.3 Cas 2 : Bon fit

```
Loss
  │╲
  │ ╲──── Train loss (descend)
  │  ╲─── Val loss (descend, proche du train)
  │   ╲──
  │    ╲─── Les deux convergent vers un plateau bas
  └─────────────────── Epochs

Diagnostic : le modèle apprend bien et généralise
Action : tout va bien ! Continuez l'entraînement jusqu'au plateau
```

### 6.4 Cas 3 : Overfitting

```
Loss
  │
  │     ╱── Val loss (remonte !)
  │   ╱
  │  ╱────── Val loss plateau
  │ ╱
  │╲──────── Train loss (continue de baisser)
  │ ╲
  └─────────────────── Epochs

Diagnostic : le modèle mémorise les données d'entraînement
Solutions :
  → Dropout, Weight Decay (régularisation)
  → Data Augmentation
  → Early Stopping
  → Réduire la capacité du réseau
  → Plus de données
```

### 6.5 Cas 4 : Oscillations / Instabilité

```
Loss
  │
  │  ╱╲  ╱╲  ╱╲
  │ ╱  ╲╱  ╲╱  ╲  ← Oscillations violentes
  │╱              ╲
  │
  └─────────────────── Epochs

Diagnostic : learning rate trop élevé
Solutions :
  → Diviser le learning rate par 10
  → Utiliser un scheduler (ReduceLROnPlateau)
  → Gradient clipping
```

### 6.6 Cas 5 : Loss explose (NaN)

```
Loss
  │           ╱
  │          ╱ → NaN !
  │         ╱
  │        ╱
  │───────╱
  └─────────────────── Epochs

Diagnostic : exploding gradients
Solutions :
  → Réduire drastiquement le learning rate
  → Gradient clipping : torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
  → Vérifier les données (valeurs aberrantes ?)
  → Vérifier l'initialisation des poids
```

> 💡 **Conseil** : Si la loss de validation remonte alors que la loss d'entraînement continue de baisser, c'est de l'**overfitting**. Il est temps d'appliquer de la régularisation (dropout, weight decay, early stopping).

### 6.7 Métriques complémentaires à surveiller

| Métrique | Ce qu'elle mesure | Quand la surveiller |
|----------|-------------------|---------------------|
| **Train Loss** | Capacité d'apprentissage | Toujours |
| **Val Loss** | Capacité de généralisation | Toujours |
| **Train Accuracy** | Performance sur le train | Classification |
| **Val Accuracy** | Performance réelle | Classification |
| **Learning Rate** | Vitesse d'apprentissage actuelle | Si scheduler actif |
| **Gradient Norm** | Magnitude des gradients | Si instabilité |
| **Poids** | Distribution des paramètres | Debug avancé |

```python
# Template de logging minimal pour chaque epoch
def afficher_metriques(epoch, train_loss, val_loss, train_acc, val_acc):
    ecart = val_loss - train_loss
    status = ""
    if ecart > 0.5:
        status = "⚠️ OVERFITTING"
    elif train_loss > 1.0 and epoch > 20:
        status = "⚠️ UNDERFITTING"
    else:
        status = "✅ OK"

    print(f"Epoch {epoch:3d} | "
          f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
          f"Train Acc: {train_acc:.2%} | Val Acc: {val_acc:.2%} | "
          f"Écart: {ecart:.4f} | {status}")
```

---

## 📝 Points clés à retenir

- La **forward propagation** calcule la sortie : Z = W·X + b, A = activation(Z)
- Les **fonctions d'activation** apportent la non-linéarité : ReLU (couches cachées), Sigmoid/Softmax (sortie)
- La **loss function** mesure l'erreur : MSE (régression), Cross-Entropy (classification)
- La **backpropagation** calcule les gradients via la règle de la chaîne
- Le **gradient descent** met à jour les poids : W = W - lr × gradient
- **Adam** est l'optimizer standard (lr=1e-3 comme point de départ)
- Les **courbes de loss** (train vs val) sont votre outil de diagnostic principal

## ✅ Checklist de validation

- [ ] Je peux expliquer le flux forward propagation (Z → A)
- [ ] Je sais choisir la bonne activation pour chaque couche
- [ ] Je connais le problème du vanishing gradient et comment l'éviter
- [ ] Je sais choisir la bonne loss function selon le type de problème
- [ ] Je comprends la backpropagation (intuitivement, pas le calcul exact)
- [ ] Je connais la différence entre SGD, Momentum et Adam
- [ ] Je sais diagnostiquer overfitting / underfitting sur les courbes de loss
- [ ] `nn.CrossEntropyLoss()` en PyTorch inclut déjà le Softmax

---

**Chapitre précédent :** [01 - Introduction au Deep Learning](./01-introduction-deep-learning.md)
**Prochain chapitre :** [03 - PyTorch](./03-frameworks-pytorch.md)

[Retour au sommaire](../README.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Gradient descent, how networks learn](https://www.youtube.com/results?search_query=3blue1brown+gradient+descent+how+neural+networks+learn) | 3Blue1Brown | EN | La descente de gradient visualisée |
| [Backpropagation, intuitively](https://www.youtube.com/results?search_query=3blue1brown+backpropagation) | 3Blue1Brown | EN | La backpropagation rendue intuitive |
| [La backpropagation expliquée](https://www.youtube.com/results?search_query=machine+learnia+backpropagation+francais) | Machine Learnia | FR | Le calcul des gradients en français |

> 💡 Concepts durs de ce chapitre (gradient, backprop) : leurs analogies sont au [chapitre 0](00-intuition-analogies.md) §6-7.
