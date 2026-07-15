# Chapitre 4 : Entraînement Pratique – Les Secrets d'un Bon Modèle

## 🎯 Objectifs

- Maîtriser les hyperparamètres d'entraînement (learning rate, batch size, epochs)
- Détecter et combattre l'overfitting (Dropout, Weight Decay, Data Augmentation, Early Stopping)
- Utiliser le Transfer Learning pour des résultats rapides avec peu de données
- Monitorer les gradients et diagnostiquer les problèmes avancés
- Développer une méthodologie rigoureuse et reproductible
- Éviter les erreurs courantes des débutants

---

## 1. ⚙️ Hyperparamètres d'entraînement

### 1.1 Learning Rate : l'hyperparamètre #1

Le learning rate (taux d'apprentissage) contrôle la **taille des pas** lors de la descente de gradient. C'est de loin l'hyperparamètre le plus important.

```
Trop grand (lr=0.1)         Correct (lr=0.001)        Trop petit (lr=0.000001)

Loss                        Loss                       Loss
 │ ╱╲  ╱╲  ╱╲              │╲                          │╲
 │╱  ╲╱  ╲╱  ╲             │ ╲                         │ ╲
 │         ╲  → NaN!        │  ╲                        │  ╲─────────────────
 │                          │   ╲───── minimum           │   (descente ultra lente)
 └────── Epochs             └────── Epochs              └────────── Epochs

 Diverge ou oscille         Converge bien              Converge mais beaucoup
                                                       trop lentement
```

**Règles pratiques :**

| Learning Rate | Quand l'utiliser |
|--------------|------------------|
| `1e-2` (0.01) | SGD sur modèles simples |
| `1e-3` (0.001) | Adam, baseline universelle |
| `1e-4` (0.0001) | Fine-tuning de modèles pré-entraînés |
| `1e-5` (0.00001) | Fine-tuning de grands Transformers (BERT, GPT) |

> 💡 **Conseil de pro** : Le learning rate est l'hyperparamètre #1. Passez plus de temps à le tuner qu'à changer l'architecture. Un bon lr peut transformer un modèle médiocre en bon modèle.

### 1.2 La technique du Learning Rate Finder

Plutôt que de deviner le learning rate, on peut le trouver automatiquement :

```python
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np

def trouver_learning_rate(model, train_loader, device,
                           lr_min=1e-7, lr_max=1.0, num_steps=100):
    """
    Technique du Learning Rate Finder (Smith, 2017).
    Augmente progressivement le lr et observe la loss.
    Le meilleur lr est juste avant que la loss remonte.
    """
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr_min)

    # Augmentation exponentielle du lr
    facteur = (lr_max / lr_min) ** (1 / num_steps)

    lrs = []
    losses = []
    lr_actuel = lr_min

    for step, (batch_X, batch_y) in enumerate(train_loader):
        if step >= num_steps:
            break

        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        # Forward + backward
        optimizer.zero_grad()
        pred = model(batch_X)
        loss = criterion(pred, batch_y)
        loss.backward()
        optimizer.step()

        # Logger
        lrs.append(lr_actuel)
        losses.append(loss.item())

        # Augmenter le lr
        lr_actuel *= facteur
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr_actuel

        # Arrêter si la loss explose
        if loss.item() > losses[0] * 10:
            break

    # Tracer la courbe
    plt.figure(figsize=(10, 6))
    plt.semilogx(lrs, losses)
    plt.xlabel('Learning Rate')
    plt.ylabel('Loss')
    plt.title('Learning Rate Finder')
    plt.grid(True, alpha=0.3)

    # Trouver le lr optimal (point de descente la plus raide)
    gradients = np.gradient(losses)
    lr_optimal = lrs[np.argmin(gradients)]
    plt.axvline(x=lr_optimal, color='red', linestyle='--',
                label=f'LR optimal ≈ {lr_optimal:.2e}')
    plt.legend()
    plt.savefig('lr_finder.png', dpi=150, bbox_inches='tight')
    plt.show()

    print(f"Learning Rate recommandé : {lr_optimal:.2e}")
    return lr_optimal
```

> 💡 **Conseil** : Le learning rate optimal se situe généralement là où la loss **descend le plus vite**, pas au minimum. Prenez un lr légèrement inférieur au point de descente maximale.

### 1.3 Batch Size : impact sur mémoire et convergence

| Batch Size | Mémoire GPU | Convergence | Régularisation |
|------------|-------------|-------------|----------------|
| **8-16** (petit) | Faible | Bruitée mais explore bien | Implicite (bruit agit comme régularisation) |
| **32-64** (moyen) | Modérée | Bon compromis | Modérée |
| **128-256** (grand) | Élevée | Stable mais risque de minima plats | Faible |
| **512+** (très grand) | Très élevée | Très stable, converge vite | Quasi nulle |

```python
# Adapter le batch_size selon votre GPU
# Technique : commencer grand, réduire si "CUDA Out of Memory"

batch_sizes_a_tester = [256, 128, 64, 32]

for bs in batch_sizes_a_tester:
    try:
        loader = DataLoader(train_dataset, batch_size=bs, shuffle=True)
        batch_X, batch_y = next(iter(loader))
        batch_X = batch_X.to(device)
        output = model(batch_X)
        loss = criterion(output, batch_y.to(device))
        loss.backward()
        print(f"✅ batch_size={bs} fonctionne")
        break
    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"❌ batch_size={bs} : VRAM insuffisante")
            torch.cuda.empty_cache()
        else:
            raise e
```

> 💡 **Conseil** : 32 ou 64 est un bon `batch_size` de départ. Augmentez si vous avez assez de VRAM. Si vous augmentez le batch_size, pensez à augmenter proportionnellement le learning rate (règle du scaling linéaire).

### 1.4 Nombre d'Epochs et Early Stopping

Le nombre d'epochs détermine **combien de fois** le modèle voit l'intégralité des données.

**Le problème :** Trop peu d'epochs → underfitting. Trop d'epochs → overfitting.

**La solution :** Early Stopping — arrêter automatiquement quand le modèle ne s'améliore plus.

```python
class EarlyStopping:
    """
    Arrête l'entraînement si la val_loss ne s'améliore pas
    pendant 'patience' epochs consécutives.
    """
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience       # Nombre d'epochs sans amélioration
        self.min_delta = min_delta     # Amélioration minimale considérée
        self.compteur = 0
        self.meilleure_loss = float('inf')
        self.stop = False

    def __call__(self, val_loss):
        if val_loss < self.meilleure_loss - self.min_delta:
            # Amélioration → reset du compteur
            self.meilleure_loss = val_loss
            self.compteur = 0
        else:
            # Pas d'amélioration
            self.compteur += 1
            if self.compteur >= self.patience:
                self.stop = True
                print(f"\n⛔ Early Stopping ! Pas d'amélioration depuis "
                      f"{self.patience} epochs.")
                print(f"   Meilleure val_loss : {self.meilleure_loss:.4f}")

# Utilisation dans la boucle d'entraînement
early_stopping = EarlyStopping(patience=10, min_delta=0.001)

for epoch in range(max_epochs):
    # ... entraînement + validation ...

    early_stopping(val_loss)
    if early_stopping.stop:
        break
```

---

## 2. 📊 Overfitting : le détecter et le combattre

L'overfitting est le **problème #1** en Deep Learning. Le modèle mémorise les données d'entraînement au lieu d'apprendre des patterns généralisables.

### 2.1 Diagnostic par les courbes d'apprentissage

```
CAS 1 : UNDERFITTING               CAS 2 : BON FIT                CAS 3 : OVERFITTING

Loss                               Loss                            Loss
 │                                  │╲                              │
 │── Train (haute)                  │ ╲── Train                     │     ╱── Val (remonte)
 │── Val (haute)                    │  ╲── Val (proche)             │   ╱
 │                                  │   ╲────                       │  ╱
 │ Les deux stagnent               │    ╲──── convergent           │╲╱
 └────── Epochs                    └────── Epochs                  │╲──── Train (baisse)
                                                                   └────── Epochs
Solutions :                         Parfait !
→ Réseau plus grand                                                Solutions :
→ Plus d'epochs                                                    → Dropout
→ LR plus élevé                                                    → Weight Decay
→ Vérifier les données                                             → Data Augmentation
                                                                   → Early Stopping
                                                                   → Moins de paramètres
```

**Indicateurs quantitatifs d'overfitting :**

| Métrique | Valeur seuil | Action |
|----------|-------------|--------|
| `val_loss - train_loss` | > 0.5 | Alerte overfitting |
| `train_acc - val_acc` | > 10% | Alerte overfitting |
| `val_loss` remonte pendant 5+ epochs | - | Early stopping |
| `train_loss` = 0 | - | Overfitting sévère |

### 2.2 Dropout

Le Dropout désactive **aléatoirement** des neurones pendant l'entraînement. Cela force le réseau à ne pas dépendre d'un seul neurone et à apprendre des représentations redondantes.

```
Réseau normal :                  Avec Dropout (p=0.5) :

[n1] ─── [h1] ─── [o1]         [n1] ─── [h1] ─── [o1]
[n2] ─── [h2] ─── [o2]         [n2] ─── [  ] ─── [o2]  ← h2 désactivé
[n3] ─── [h3]                   [  ] ─── [h3]           ← n3 désactivé
[n4] ─── [h4]                   [n4] ─── [h4]

Chaque neurone est               Des neurones différents
toujours actif                   sont désactivés à chaque batch
```

```python
import torch.nn as nn

class ReseauAvecDropout(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 512)
        self.dropout1 = nn.Dropout(p=0.3)   # 30% des neurones désactivés
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(p=0.5)   # 50% des neurones désactivés
        self.fc3 = nn.Linear(256, 10)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout1(x)          # Dropout après l'activation
        x = torch.relu(self.fc2(x))
        x = self.dropout2(x)          # Plus de dropout dans les couches profondes
        x = self.fc3(x)               # PAS de dropout en sortie
        return x
```

**Règles pratiques pour le Dropout :**

| Position | Taux recommandé | Notes |
|----------|----------------|-------|
| Après les premières couches | 0.2 - 0.3 | Garder la plupart des features d'entrée |
| Couches intermédiaires | 0.3 - 0.5 | Standard |
| Avant la dernière couche | 0.5 | Régularisation maximale |
| Couche de sortie | 0 (jamais) | Ne jamais mettre de dropout en sortie |

> 💡 **Conseil** : Dropout 0.2-0.5 est standard. Plus le réseau est grand et plus vous avez peu de données, plus le dropout doit être élevé.

### 2.3 Régularisation L2 (Weight Decay)

Le Weight Decay pénalise les poids trop grands, forçant le réseau à trouver des solutions simples.

```python
import torch.optim as optim

# Weight Decay intégré à l'optimizer
# Ajoute une pénalité L2 : Loss_totale = Loss_data + λ × Σ(wi²)
optimizer = optim.Adam(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-4    # λ = 0.0001 (valeur standard)
)

# Ou avec AdamW (implémentation plus correcte du weight decay)
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-2    # AdamW utilise des valeurs plus élevées (0.01)
)
```

**Valeurs de Weight Decay recommandées :**

| Optimizer | Weight Decay | Notes |
|-----------|-------------|-------|
| Adam | `1e-4` à `1e-3` | Valeurs classiques |
| AdamW | `1e-2` à `1e-1` | Décorrélé du lr, valeurs plus élevées |
| SGD | `1e-4` à `5e-4` | Standard pour CNN |

### 2.4 Data Augmentation

La Data Augmentation crée des **versions modifiées** des données d'entraînement. C'est la technique anti-overfitting la plus puissante quand vous avez peu de données.

```python
from torchvision import transforms

# Data Augmentation pour les images
train_transform = transforms.Compose([
    # --- Augmentations géométriques ---
    transforms.RandomHorizontalFlip(p=0.5),        # Miroir horizontal
    transforms.RandomVerticalFlip(p=0.1),           # Miroir vertical (rare)
    transforms.RandomRotation(degrees=15),           # Rotation ±15°
    transforms.RandomResizedCrop(                    # Crop + resize aléatoire
        size=224,
        scale=(0.8, 1.0),
        ratio=(0.9, 1.1)
    ),
    transforms.RandomAffine(                         # Transformations affines
        degrees=10,
        translate=(0.1, 0.1),
        shear=5
    ),

    # --- Augmentations photométriques ---
    transforms.ColorJitter(
        brightness=0.2,     # Variation de luminosité ±20%
        contrast=0.2,       # Variation de contraste ±20%
        saturation=0.2,     # Variation de saturation ±20%
        hue=0.05            # Variation de teinte ±5%
    ),
    transforms.RandomGrayscale(p=0.1),              # Passage en gris (10%)

    # --- Conversion et normalisation ---
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],                 # Moyenne ImageNet
        std=[0.229, 0.224, 0.225]                    # Écart-type ImageNet
    ),

    # --- Augmentation avancée ---
    transforms.RandomErasing(p=0.1),                # Masquer une zone aléatoire
])

# ⚠️ PAS de data augmentation pour la validation/test
val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])
```

> 💡 **Conseil de pro** : La Data Augmentation est la technique anti-overfitting **la plus puissante** quand vous avez peu de données. Elle est gratuite en termes de collecte de données et très efficace.

### 2.5 Batch Normalization

La Batch Normalization normalise les activations entre les couches, ce qui :
- **Accélère** l'entraînement (gradient plus stable)
- **Régularise** légèrement (bruit dû aux statistiques du batch)
- Permet des **learning rates plus élevés**

```python
import torch.nn as nn

class ReseauAvecBatchNorm(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.bn1 = nn.BatchNorm1d(256)    # BatchNorm après la couche linéaire
        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.fc3 = nn.Linear(128, 10)

    def forward(self, x):
        x = x.view(x.size(0), -1)

        # Pattern : Linear → BatchNorm → Activation
        x = self.fc1(x)
        x = self.bn1(x)          # Normalise les activations
        x = torch.relu(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = torch.relu(x)

        x = self.fc3(x)          # Pas de BatchNorm en sortie
        return x
```

> 💡 **Conseil** : L'ordre standard est **Linear → BatchNorm → Activation**. Certains placent BatchNorm après l'activation, les deux fonctionnent. L'important est d'être cohérent.

### 2.6 Résumé des techniques anti-overfitting

| Technique | Efficacité | Coût | Quand l'utiliser |
|-----------|-----------|------|------------------|
| **Data Augmentation** | Très élevée | Nul (gratuit) | Toujours (images) |
| **Dropout** | Élevée | Nul | Toujours |
| **Weight Decay** | Moyenne | Nul | Toujours (1e-4 par défaut) |
| **Early Stopping** | Élevée | Nul | Toujours |
| **Batch Normalization** | Moyenne | Faible | Réseaux profonds |
| **Plus de données** | Très élevée | Élevé | Si possible |
| **Réduire le réseau** | Moyenne | Nul | Dernier recours |

---

## 3. 🚀 Transfer Learning

### 3.1 Le principe

Le Transfer Learning consiste à **réutiliser un modèle pré-entraîné** sur un grand dataset (ex: ImageNet, 14M d'images) et à l'adapter à votre tâche spécifique.

```
Modèle pré-entraîné (ImageNet)       Votre tâche (ex: chats vs chiens)
┌───────────────────────────────┐     ┌──────────────────────────┐
│ Conv1 : détecte les bords     │ ──→ │ Garde tel quel (gelé)    │
│ Conv2 : détecte les textures  │ ──→ │ Garde tel quel (gelé)    │
│ Conv3 : détecte les formes    │ ──→ │ Garde tel quel (gelé)    │
│ Conv4 : détecte les objets    │ ──→ │ Optionnel : fine-tune    │
│ FC : classifie (1000 classes) │ ──→ │ REMPLACER (2 classes)    │
└───────────────────────────────┘     └──────────────────────────┘
```

**Pourquoi c'est si puissant :**
- Les premières couches apprennent des features **universelles** (bords, textures)
- Seules les dernières couches sont spécifiques au dataset
- Vous réutilisez des millions de paramètres déjà optimisés

### 3.2 Feature Extraction vs Fine-Tuning

| Approche | Couches gelées | Couches entraînées | Données nécessaires | Quand |
|----------|---------------|-------------------|---------------------|-------|
| **Feature Extraction** | Toutes sauf la dernière | Dernière couche seulement | Très peu (100-1000) | Peu de données |
| **Fine-tuning partiel** | Premières couches | Dernières couches + nouvelle tête | Moyen (1000-10000) | Cas standard |
| **Fine-tuning complet** | Aucune | Tout le réseau | Beaucoup (10000+) | Beaucoup de données |

### 3.3 Code complet : Transfer Learning avec ResNet

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

def creer_modele_transfer(n_classes, mode='fine_tuning'):
    """
    Crée un modèle basé sur ResNet-18 pré-entraîné.

    Args:
        n_classes: nombre de classes de votre problème
        mode: 'feature_extraction' ou 'fine_tuning'
    """
    # 1. Charger le modèle pré-entraîné
    model = models.resnet18(weights='IMAGENET1K_V1')
    print(f"ResNet-18 chargé ({sum(p.numel() for p in model.parameters()):,} paramètres)")

    # 2. Geler les couches selon le mode
    if mode == 'feature_extraction':
        # Geler TOUTES les couches
        for param in model.parameters():
            param.requires_grad = False
        print("Mode Feature Extraction : toutes les couches gelées")

    elif mode == 'fine_tuning':
        # Geler les premières couches, laisser les dernières entraînables
        for name, param in model.named_parameters():
            if 'layer4' not in name and 'fc' not in name:
                param.requires_grad = False
        print("Mode Fine-tuning : seuls layer4 et fc sont entraînables")

    # 3. Remplacer la couche de classification
    n_features = model.fc.in_features  # 512 pour ResNet-18
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(n_features, n_classes)
    )

    # Compter les paramètres entraînables
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    print(f"Paramètres entraînables : {n_trainable:,} / {n_total:,} "
          f"({n_trainable/n_total:.1%})")

    return model

# Exemple : classification chats vs chiens (2 classes)
model = creer_modele_transfer(n_classes=2, mode='fine_tuning')

# Optimizer avec learning rate différencié
# (lr plus faible pour les couches pré-entraînées)
optimizer = optim.Adam([
    {'params': model.layer4.parameters(), 'lr': 1e-4},    # Couches pré-entraînées
    {'params': model.fc.parameters(), 'lr': 1e-3},        # Nouvelle couche
])
```

### 3.4 Modèles pré-entraînés courants

| Modèle | Paramètres | Top-1 ImageNet | Usage |
|--------|-----------|----------------|-------|
| **ResNet-18** | 11M | 69.8% | Prototypage rapide, petits datasets |
| **ResNet-50** | 25M | 76.1% | Standard industriel |
| **EfficientNet-B0** | 5M | 77.1% | Meilleur ratio performance/taille |
| **EfficientNet-B4** | 19M | 82.9% | Haute performance |
| **ViT-B/16** | 86M | 81.8% | Vision Transformer |
| **ConvNeXt-Base** | 89M | 83.8% | CNN moderne (comparable aux ViT) |

```python
# Charger différents modèles pré-entraînés
from torchvision import models

resnet50 = models.resnet50(weights='IMAGENET1K_V2')
efficientnet = models.efficientnet_b0(weights='IMAGENET1K_V1')
vit = models.vit_b_16(weights='IMAGENET1K_V1')
```

> 💡 **Conseil de pro** : En 2024, commencez **TOUJOURS** par le Transfer Learning. Entraîner from scratch est rarement nécessaire et presque toujours moins performant. Même avec 500 images, un ResNet fine-tuné battrait un réseau entraîné de zéro.

---

## 4. 📊 Métriques avancées pour le Deep Learning

### 4.1 Analyse détaillée des Loss Curves

| Observation | Diagnostic | Action |
|-------------|-----------|--------|
| Train loss descend, val loss **stable** | Début d'overfitting | Commencer à régulariser |
| Train loss descend, val loss **remonte** | Overfitting confirmé | Dropout, WD, Data Aug, Early Stop |
| Les deux **stagnent** haut | Underfitting | Plus de capacité, meilleur lr |
| Les deux **oscillent** | lr trop élevé | Réduire le lr |
| Train loss → **NaN** | Exploding gradients | lr ÷ 10, gradient clipping |
| Train loss **ne bouge pas** | lr trop faible ou bug | Vérifier le code, augmenter lr |
| Val loss **beaucoup plus haute** dès le début | Erreur de preprocessing | Vérifier train_transform vs val_transform |

### 4.2 Gradient Monitoring

```python
import torch

def surveiller_gradients(model):
    """
    Surveille les gradients pendant l'entraînement.
    Détecte vanishing et exploding gradients.
    """
    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.norm().item()
            grad_mean = param.grad.mean().item()
            grad_max = param.grad.max().item()

            # Alerte vanishing gradient
            if grad_norm < 1e-7:
                print(f"⚠️  VANISHING gradient dans {name} "
                      f"(norm={grad_norm:.2e})")

            # Alerte exploding gradient
            if grad_norm > 100:
                print(f"⚠️  EXPLODING gradient dans {name} "
                      f"(norm={grad_norm:.2e})")

# Gradient Clipping : limiter la norme des gradients
def entrainer_avec_clipping(model, train_loader, criterion, optimizer,
                             device, max_grad_norm=1.0):
    """Entraînement avec gradient clipping"""
    model.train()
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()

        # Clipper les gradients AVANT optimizer.step()
        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=max_grad_norm
        )

        optimizer.step()
```

### 4.3 Vanishing vs Exploding Gradients

```
Vanishing Gradients                    Exploding Gradients
─────────────────                      ────────────────────

Symptômes :                            Symptômes :
- Premières couches n'apprennent pas   - Loss explose ou NaN
- Poids restent proches de l'init      - Poids deviennent très grands
- Loss stagne après quelques epochs    - Instabilité d'entraînement

Causes :                               Causes :
- Sigmoid/Tanh en couches cachées      - Learning rate trop élevé
- Réseau trop profond sans skip conn.  - Mauvaise initialisation
- Mauvaise initialisation              - Absence de normalisation

Solutions :                            Solutions :
- ReLU / Leaky ReLU                    - Gradient Clipping
- Skip connections (ResNet)            - Réduire le learning rate
- Batch Normalization                  - Batch Normalization
- Xavier/He initialisation             - Gradient Clipping (max_norm=1.0)
```

### 4.4 Top-K Accuracy

Pour la classification multi-classes, le Top-K Accuracy mesure si la bonne classe est parmi les K prédictions les plus probables.

```python
import torch

def topk_accuracy(output, target, topk=(1, 5)):
    """
    Calcule Top-1 et Top-5 accuracy.

    Args:
        output: logits du modèle (batch_size, n_classes)
        target: vrais labels (batch_size,)
        topk: tuple des K à calculer
    """
    with torch.no_grad():
        maxk = max(topk)
        batch_size = target.size(0)

        # Top-K prédictions
        _, pred = output.topk(maxk, dim=1, largest=True, sorted=True)
        pred = pred.t()  # Transposer pour faciliter la comparaison

        correct = pred.eq(target.view(1, -1).expand_as(pred))

        resultats = {}
        for k in topk:
            correct_k = correct[:k].reshape(-1).float().sum(0)
            resultats[f'top{k}'] = (correct_k / batch_size).item()

        return resultats

# Utilisation
# output = model(images)           # (batch, 1000) pour ImageNet
# acc = topk_accuracy(output, labels, topk=(1, 5))
# print(f"Top-1: {acc['top1']:.2%}, Top-5: {acc['top5']:.2%}")
```

### 4.5 Matrice de confusion

```python
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import torch

def evaluer_modele(model, test_loader, device, noms_classes):
    """Évaluation complète avec matrice de confusion et rapport"""
    model.eval()
    toutes_predictions = []
    tous_labels = []

    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X = batch_X.to(device)
            output = model(batch_X)
            _, predicted = output.max(1)
            toutes_predictions.extend(predicted.cpu().numpy())
            tous_labels.extend(batch_y.numpy())

    # Matrice de confusion
    cm = confusion_matrix(tous_labels, toutes_predictions)
    print("Matrice de confusion :")
    print(cm)

    # Rapport de classification
    print("\nRapport de classification :")
    print(classification_report(
        tous_labels,
        toutes_predictions,
        target_names=noms_classes
    ))
```

---

## 5. 📈 Méthodologie complète

### 5.1 Checklist pour un projet Deep Learning

```
┌─────────────────────────────────────────────────────────────┐
│            MÉTHODOLOGIE DEEP LEARNING                       │
│                                                             │
│  1. 🔍 BASELINE                                            │
│     → Commencer par un modèle SIMPLE (MLP, petit CNN)      │
│     → Établir une performance de référence                  │
│                                                             │
│  2. 🐛 SANITY CHECK                                        │
│     → Overfitter un petit batch (10-100 samples)            │
│     → Si train_loss → 0, le code est correct                │
│     → Si non, il y a un BUG !                               │
│                                                             │
│  3. 📊 DONNÉES COMPLÈTES                                   │
│     → Charger toutes les données                            │
│     → Train/Val/Test split                                  │
│                                                             │
│  4. 🎯 LEARNING RATE                                       │
│     → LR Finder ou commencer à 1e-3 (Adam)                 │
│     → Tuner avant tout le reste                             │
│                                                             │
│  5. 🛡️ RÉGULARISATION                                      │
│     → Dropout (0.2-0.5)                                     │
│     → Weight Decay (1e-4)                                   │
│     → Data Augmentation                                     │
│                                                             │
│  6. ⏹️ EARLY STOPPING                                      │
│     → patience=10-20 epochs                                 │
│     → Sauvegarder le meilleur modèle                        │
│                                                             │
│  7. 🚀 TRANSFER LEARNING                                   │
│     → Si applicable (images, NLP)                           │
│     → ResNet, EfficientNet, BERT...                         │
│                                                             │
│  8. 🔧 HYPERPARAMETER SEARCH                               │
│     → Grid Search ou Optuna                                 │
│     → lr, batch_size, architecture, dropout                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Le Sanity Check : l'étape CRUCIALE

```python
import torch

def sanity_check(model, train_loader, criterion, optimizer, device, n_steps=100):
    """
    Vérifie que le modèle peut overfitter un petit batch.
    Si oui → le code est correct.
    Si non → il y a un bug !
    """
    model.train()
    model.to(device)

    # Prendre un seul batch
    batch_X, batch_y = next(iter(train_loader))
    batch_X, batch_y = batch_X.to(device), batch_y.to(device)

    print(f"Sanity check sur {batch_X.size(0)} samples...")

    for step in range(n_steps):
        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()

        if step % 20 == 0:
            _, predicted = output.max(1)
            acc = (predicted == batch_y).float().mean()
            print(f"  Step {step:3d} | Loss: {loss.item():.4f} | Acc: {acc:.2%}")

    # Vérification finale
    _, predicted = output.max(1)
    acc_finale = (predicted == batch_y).float().mean()

    if acc_finale > 0.95:
        print(f"\n✅ SANITY CHECK PASSÉ : le modèle peut overfitter "
              f"(acc={acc_finale:.2%})")
    else:
        print(f"\n❌ SANITY CHECK ÉCHOUÉ : le modèle n'arrive pas à overfitter "
              f"(acc={acc_finale:.2%})")
        print("   → Vérifiez : architecture, loss function, données, lr")
```

> 💡 **Conseil de pro** : L'étape 2 (Sanity Check) est **CRUCIALE**. Si votre modèle ne peut pas overfitter 10-100 samples, il y a un bug dans votre code. Inutile de continuer avant d'avoir résolu ce problème.

### 5.3 Hyperparameter Search avec Optuna

```python
# uv add optuna
import optuna
import torch
import torch.nn as nn
import torch.optim as optim

def objectif(trial):
    """Fonction objectif pour Optuna"""
    # Suggérer des hyperparamètres
    n_couches = trial.suggest_int('n_couches', 1, 4)
    lr = trial.suggest_float('lr', 1e-5, 1e-2, log=True)
    dropout = trial.suggest_float('dropout', 0.1, 0.5)
    batch_size = trial.suggest_categorical('batch_size', [32, 64, 128])

    # Construire le modèle dynamiquement
    couches = []
    taille_entree = 784
    for i in range(n_couches):
        taille_sortie = trial.suggest_int(f'n_units_{i}', 64, 512, step=64)
        couches.extend([
            nn.Linear(taille_entree, taille_sortie),
            nn.ReLU(),
            nn.Dropout(dropout),
        ])
        taille_entree = taille_sortie
    couches.append(nn.Linear(taille_entree, 10))

    model = nn.Sequential(*couches).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Entraîner et évaluer (simplifié)
    # ... (boucle d'entraînement standard)

    return val_accuracy  # Optuna maximise cette valeur

# Lancer la recherche
etude = optuna.create_study(direction='maximize')
etude.optimize(objectif, n_trials=50)

print(f"Meilleurs hyperparamètres : {etude.best_params}")
print(f"Meilleure val_accuracy : {etude.best_value:.2%}")
```

---

## 6. 🚫 Les erreurs courantes en Deep Learning

### 6.1 Table des erreurs et solutions

| # | Erreur | Symptôme | Solution |
|---|--------|----------|----------|
| 1 | **Pas de normalisation des données** | Loss ne descend pas ou très lentement | `transforms.Normalize()` (mean=0, std=1) |
| 2 | **Learning rate trop élevé** | Loss explose ou NaN | Diviser le lr par 10 |
| 3 | **Learning rate trop faible** | Loss descend très lentement | Multiplier le lr par 10 |
| 4 | **Pas de shuffle** | Convergence bizarre, biais | `DataLoader(shuffle=True)` sur le train |
| 5 | **Mauvaise loss function** | Modèle ne converge pas | Vérifier le match loss ↔ activation |
| 6 | **Softmax + CrossEntropyLoss** | Performance dégradée | Enlever le Softmax (CE l'inclut) |
| 7 | **GPU pas utilisé** | Entraînement très lent | `.to(device)` sur modèle ET données |
| 8 | **Oublier zero_grad()** | Gradients accumulent, instabilité | `optimizer.zero_grad()` à chaque batch |
| 9 | **Oublier model.eval()** | Métriques val instables | `model.eval()` + `torch.no_grad()` |
| 10 | **Train/Val transforms différents** | Val loss très haute dès le début | Même normalisation, pas d'augmentation en val |
| 11 | **Data leakage** | Val performance trop bonne | Vérifier le split train/val/test |
| 12 | **Mauvais dtype** | Erreur de type | `torch.FloatTensor` pour les features |
| 13 | **Tensors sur devices différents** | RuntimeError | Tout sur le même device |
| 14 | **Pas de seed** | Résultats non reproductibles | `torch.manual_seed(42)` |

### 6.2 Debugging rapide

```python
import torch

def debug_modele(model, train_loader, device):
    """Script de diagnostic rapide pour un modèle PyTorch"""
    print("=" * 60)
    print("DIAGNOSTIC DU MODÈLE")
    print("=" * 60)

    # 1. Architecture
    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n📐 Architecture :")
    print(f"   Paramètres totaux     : {n_params:,}")
    print(f"   Paramètres entraînables : {n_trainable:,}")

    # 2. Données
    batch_X, batch_y = next(iter(train_loader))
    print(f"\n📊 Données :")
    print(f"   Batch X shape : {batch_X.shape}")
    print(f"   Batch Y shape : {batch_y.shape}")
    print(f"   X dtype       : {batch_X.dtype}")
    print(f"   Y dtype       : {batch_y.dtype}")
    print(f"   X range       : [{batch_X.min():.4f}, {batch_X.max():.4f}]")
    print(f"   Y unique      : {batch_y.unique().tolist()}")

    # 3. Forward pass
    model.to(device)
    model.eval()
    with torch.no_grad():
        try:
            output = model(batch_X.to(device))
            print(f"\n✅ Forward pass OK :")
            print(f"   Output shape : {output.shape}")
            print(f"   Output range : [{output.min():.4f}, {output.max():.4f}]")
        except Exception as e:
            print(f"\n❌ Forward pass ERREUR : {e}")

    # 4. Vérifier les NaN
    has_nan = False
    for name, param in model.named_parameters():
        if torch.isnan(param).any():
            print(f"❌ NaN détecté dans {name}")
            has_nan = True
    if not has_nan:
        print(f"\n✅ Pas de NaN dans les poids")

    print("=" * 60)

# Utilisation :
# debug_modele(model, train_loader, device)
```

### 6.3 Reproductibilité

```python
import torch
import numpy as np
import random

def fixer_seed(seed=42):
    """Fixer toutes les sources d'aléatoire pour la reproductibilité"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"Seed fixée à {seed} pour reproductibilité")

# Appeler au début de chaque script
fixer_seed(42)
```

> ⚠️ **Attention** : `torch.backends.cudnn.deterministic = True` ralentit l'entraînement de ~10-20%. Utilisez-le pour le debugging et les résultats finaux, pas pendant l'exploration.

---

## 📝 Points clés à retenir

- Le **Learning Rate** est l'hyperparamètre #1 (commencer avec lr=1e-3 pour Adam)
- L'**overfitting** se détecte quand `val_loss` remonte alors que `train_loss` baisse
- Les techniques anti-overfitting : **Dropout**, **Weight Decay**, **Data Augmentation**, **Early Stopping**
- Le **Transfer Learning** est presque toujours meilleur que d'entraîner from scratch
- Le **Sanity Check** (overfitter un petit batch) est l'étape de debug la plus importante
- Surveillez les **gradients** (vanishing, exploding) pour les réseaux profonds
- La **méthodologie** est plus importante que l'architecture : baseline → sanity check → tune lr → régulariser

## ✅ Checklist de validation

- [ ] Je sais utiliser le Learning Rate Finder
- [ ] Je connais l'impact du batch_size sur la convergence et la mémoire
- [ ] Je sais implémenter l'Early Stopping
- [ ] Je maîtrise les 5 techniques anti-overfitting (Dropout, WD, DA, BN, ES)
- [ ] Je sais faire du Transfer Learning avec ResNet/EfficientNet
- [ ] Je peux diagnostiquer vanishing/exploding gradients
- [ ] J'applique la méthodologie en 8 étapes pour tout nouveau projet
- [ ] Je fais TOUJOURS un sanity check avant d'entraîner sur les données complètes
- [ ] Je sais debugger un modèle qui ne converge pas

---

**Chapitre précédent :** [03 - PyTorch](./03-frameworks-pytorch.md)

[Retour au sommaire](../README.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Overfitting & regularization](https://www.youtube.com/results?search_query=statquest+regularization+ridge+lasso) | StatQuest | EN | Pourquoi et comment régulariser |
| [Transfer learning expliqué](https://www.youtube.com/results?search_query=transfer+learning+deep+learning+explained) | EN | EN | Réutiliser un réseau pré-entraîné |
| [Bien régler le learning rate](https://www.youtube.com/results?search_query=learning+rate+tuning+deep+learning) | EN | EN | L'hyperparamètre n°1 |
