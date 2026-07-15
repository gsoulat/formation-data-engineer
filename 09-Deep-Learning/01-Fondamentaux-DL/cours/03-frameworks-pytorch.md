# Chapitre 3 : PyTorch – Votre Framework Deep Learning

## 🎯 Objectifs

- Maîtriser les tensors PyTorch et leurs opérations
- Comprendre autograd (calcul automatique des gradients)
- Construire un réseau de neurones avec `nn.Module`
- Charger et préparer les données avec `DataLoader`
- Écrire une boucle d'entraînement complète et réutilisable
- Sauvegarder et charger un modèle
- Visualiser l'entraînement (loss curves, TensorBoard)

---

## 1. 🚀 Installation et premiers pas

### 1.1 Installation

```python
# Installation PyTorch (CPU uniquement)
# uv add torch torchvision torchaudio

# Installation PyTorch avec CUDA 12.1 (GPU NVIDIA)
# uv add torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Sur Google Colab : PyTorch est pré-installé !
```

### 1.2 Vérification de l'environnement

```python
import torch
import torchvision
import sys

print(f"Python       : {sys.version}")
print(f"PyTorch      : {torch.__version__}")
print(f"TorchVision  : {torchvision.__version__}")
print(f"CUDA dispo   : {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU          : {torch.cuda.get_device_name(0)}")
    print(f"VRAM         : {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} Go")
```

### 1.3 Gestion du device (CPU / GPU)

```python
import torch

# Détection automatique du meilleur device
def obtenir_device():
    """Retourne le meilleur device disponible"""
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"✅ Utilisation du GPU : {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = torch.device('mps')
        print("✅ Utilisation du GPU Apple Silicon (MPS)")
    else:
        device = torch.device('cpu')
        print("⚠️ Utilisation du CPU (pas de GPU détecté)")
    return device

device = obtenir_device()
```

> 💡 **Conseil** : Utilisez **toujours** une variable `device` et `.to(device)` sur vos modèles et tensors. Cela rend votre code portable entre CPU et GPU sans modification.

---

## 2. 🧱 Tensors : la brique fondamentale

Les tensors sont les structures de données centrales de PyTorch. Ils sont similaires aux arrays NumPy, mais avec le support GPU et le calcul automatique des gradients.

### 2.1 Création de tensors

```python
import torch

# --- Depuis des données Python ---
# Vecteur (1D)
vecteur = torch.tensor([1, 2, 3, 4])
print(f"Vecteur : {vecteur}, shape : {vecteur.shape}")
# Vecteur : tensor([1, 2, 3, 4]), shape : torch.Size([4])

# Matrice (2D)
matrice = torch.tensor([[1, 2, 3],
                         [4, 5, 6]])
print(f"Matrice : shape {matrice.shape}")
# Matrice : shape torch.Size([2, 3])

# Tensor 3D (ex: batch d'images en niveaux de gris)
tensor_3d = torch.tensor([[[1, 2], [3, 4]],
                           [[5, 6], [7, 8]]])
print(f"Tensor 3D : shape {tensor_3d.shape}")
# Tensor 3D : shape torch.Size([2, 2, 2])

# --- Tensors spéciaux ---
zeros = torch.zeros(3, 4)          # Matrice de zéros (3×4)
ones = torch.ones(2, 3)            # Matrice de uns (2×3)
aleatoire = torch.randn(3, 3)     # Matrice aléatoire (distribution normale)
identite = torch.eye(4)            # Matrice identité (4×4)
sequence = torch.arange(0, 10, 2)  # Séquence [0, 2, 4, 6, 8]

# --- Avec un type spécifique ---
entiers = torch.tensor([1, 2, 3], dtype=torch.int32)
flottants = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)
# float32 est le type standard pour le Deep Learning
```

### 2.2 Opérations sur les tensors

```python
import torch

a = torch.tensor([[1.0, 2.0],
                   [3.0, 4.0]])

b = torch.tensor([[5.0, 6.0],
                   [7.0, 8.0]])

# --- Opérations élément par élément ---
print(f"Addition     : {a + b}")        # ou torch.add(a, b)
print(f"Soustraction : {a - b}")        # ou torch.sub(a, b)
print(f"Multiplication : {a * b}")      # ELEMENT par ELEMENT (pas matricielle !)
print(f"Division     : {a / b}")

# --- Multiplication matricielle ---
produit = a @ b                          # ou torch.matmul(a, b)
print(f"Produit matriciel :\n{produit}")
# tensor([[19., 22.],
#         [43., 50.]])

# --- Redimensionnement ---
x = torch.arange(12)                    # tensor([0, 1, 2, ..., 11])
x_2d = x.view(3, 4)                     # Redimensionner en 3×4
x_2d_bis = x.reshape(3, 4)              # Même résultat (plus flexible)
x_aplati = x_2d.flatten()               # Retour à 1D

print(f"Original  : {x.shape}")          # torch.Size([12])
print(f"Reshape   : {x_2d.shape}")       # torch.Size([3, 4])
print(f"Flatten   : {x_aplati.shape}")   # torch.Size([12])

# --- Agrégations ---
t = torch.tensor([[1.0, 2.0, 3.0],
                   [4.0, 5.0, 6.0]])

print(f"Somme totale    : {t.sum()}")             # 21
print(f"Somme par ligne : {t.sum(dim=1)}")        # [6, 15]
print(f"Somme par colonne : {t.sum(dim=0)}")      # [5, 7, 9]
print(f"Moyenne         : {t.mean()}")             # 3.5
print(f"Max             : {t.max()}")              # 6
print(f"Argmax          : {t.argmax()}")           # 5 (index du max)
```

### 2.3 NumPy <-> Tensor

```python
import torch
import numpy as np

# NumPy → Tensor
array_np = np.array([1.0, 2.0, 3.0])
tensor_torch = torch.from_numpy(array_np)
print(f"NumPy → Tensor : {tensor_torch}")

# Tensor → NumPy
tensor = torch.tensor([4.0, 5.0, 6.0])
array = tensor.numpy()
print(f"Tensor → NumPy : {array}")

# ⚠️ Attention : ils partagent la mémoire !
array_np[0] = 999
print(f"Tensor modifié aussi : {tensor_torch}")  # tensor([999., 2., 3.])

# Pour copier sans partage de mémoire :
tensor_copie = torch.from_numpy(array_np.copy())
```

### 2.4 Tensors sur GPU

```python
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Créer un tensor directement sur GPU
x_gpu = torch.randn(1000, 1000, device=device)

# Déplacer un tensor existant sur GPU
x_cpu = torch.randn(1000, 1000)
x_gpu = x_cpu.to(device)

# Vérifier le device
print(f"Device : {x_gpu.device}")  # cuda:0

# ⚠️ Opération entre CPU et GPU = ERREUR
# x_cpu + x_gpu  # RuntimeError: Expected all tensors to be on the same device
# Solution : tout mettre sur le même device
resultat = x_gpu + x_cpu.to(device)  # OK

# Ramener sur CPU (nécessaire pour NumPy, matplotlib, etc.)
x_retour_cpu = x_gpu.cpu()
array_np = x_retour_cpu.numpy()
# Ou en une ligne :
array_np = x_gpu.cpu().numpy()
```

> ⚠️ **Attention** : Un calcul entre un tensor CPU et un tensor GPU provoquera une erreur. Vérifiez toujours que tous vos tensors sont sur le même device.

---

## 3. 🔧 Autograd : calcul automatique des gradients

Autograd est le moteur de différentiation automatique de PyTorch. Il calcule automatiquement les gradients pour la backpropagation.

### 3.1 Concept de base

```python
import torch

# Créer un tensor qui nécessite des gradients
x = torch.tensor(3.0, requires_grad=True)

# Opération forward
y = x ** 2 + 2 * x + 1   # y = x² + 2x + 1

# Calcul automatique du gradient
y.backward()               # dy/dx = 2x + 2

print(f"x = {x.item()}")
print(f"y = {y.item()}")
print(f"dy/dx = {x.grad.item()}")  # 2*3 + 2 = 8
```

### 3.2 Gradient Descent avec Autograd

```python
import torch

# Problème : trouver x qui minimise f(x) = (x - 5)²
x = torch.tensor(0.0, requires_grad=True)
learning_rate = 0.1

print("Descente de gradient pour minimiser f(x) = (x - 5)²")
for step in range(20):
    # Forward : calculer la loss
    loss = (x - 5) ** 2

    # Backward : calculer le gradient
    loss.backward()

    # Mise à jour des paramètres (sans tracking du gradient)
    with torch.no_grad():
        x -= learning_rate * x.grad

    # Remettre le gradient à zéro (ESSENTIEL !)
    x.grad.zero_()

    if step % 5 == 0:
        print(f"  Step {step:2d} : x = {x.item():.4f}, loss = {loss.item():.4f}")

print(f"  Résultat final : x = {x.item():.4f} (attendu : 5.0)")
```

### 3.3 `torch.no_grad()` : désactiver le tracking

```python
import torch

# Pendant l'inférence, pas besoin de calculer les gradients
# → Économie de mémoire et de temps

model = torch.nn.Linear(10, 1)
x = torch.randn(5, 10)

# Mode entraînement (avec gradients)
y_train = model(x)
print(f"Avec grad : {y_train.requires_grad}")  # True

# Mode inférence (sans gradients)
with torch.no_grad():
    y_eval = model(x)
    print(f"Sans grad : {y_eval.requires_grad}")  # False
```

> 💡 **Conseil de pro** : Utilisez **toujours** `torch.no_grad()` pendant l'évaluation et l'inférence. Cela réduit la consommation mémoire de ~50% et accélère le calcul.

---

## 4. 🏗️ nn.Module : construire un réseau

### 4.1 La classe de base

`nn.Module` est la classe mère de tous les réseaux de neurones en PyTorch. Chaque modèle hérite de cette classe.

```python
import torch
import torch.nn as nn

class MonPremierReseau(nn.Module):
    def __init__(self, n_entrees, n_cachees, n_sorties):
        super().__init__()
        # Définir les couches
        self.couche1 = nn.Linear(n_entrees, n_cachees)   # Couche dense
        self.activation = nn.ReLU()                        # Activation ReLU
        self.couche2 = nn.Linear(n_cachees, n_sorties)    # Couche de sortie

    def forward(self, x):
        """Définir le flux de données (forward propagation)"""
        x = self.couche1(x)      # Couche 1 : linéaire
        x = self.activation(x)   # Activation ReLU
        x = self.couche2(x)      # Couche 2 : linéaire (sortie)
        return x

# Créer le réseau
model = MonPremierReseau(n_entrees=784, n_cachees=128, n_sorties=10)
print(model)
# MonPremierReseau(
#   (couche1): Linear(in_features=784, out_features=128, bias=True)
#   (activation): ReLU()
#   (couche2): Linear(in_features=128, out_features=10, bias=True)
# )

# Nombre de paramètres
n_params = sum(p.numel() for p in model.parameters())
print(f"Paramètres : {n_params:,}")
# Paramètres : 101,770 (784×128 + 128 + 128×10 + 10)
```

### 4.2 Réseau pour MNIST (classification de chiffres)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class ReseauMNIST(nn.Module):
    """Réseau pour classifier les chiffres manuscrits (0-9)"""

    def __init__(self):
        super().__init__()
        # Image MNIST : 28×28 = 784 pixels → 10 classes
        self.fc1 = nn.Linear(784, 256)       # Couche cachée 1
        self.dropout1 = nn.Dropout(0.3)       # Régularisation
        self.fc2 = nn.Linear(256, 128)        # Couche cachée 2
        self.dropout2 = nn.Dropout(0.3)       # Régularisation
        self.fc3 = nn.Linear(128, 10)         # Couche de sortie (10 chiffres)

    def forward(self, x):
        # Aplatir l'image 28×28 en vecteur 784
        x = x.view(x.size(0), -1)  # (batch, 28, 28) → (batch, 784)

        # Couche 1
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)

        # Couche 2
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)

        # Couche de sortie (pas de softmax : CrossEntropyLoss le fait)
        x = self.fc3(x)
        return x

model = ReseauMNIST()
print(f"Architecture : {model}")
print(f"Paramètres   : {sum(p.numel() for p in model.parameters()):,}")
```

### 4.3 `nn.Sequential` : pour les prototypes rapides

```python
import torch.nn as nn

# Version rapide avec nn.Sequential (pas de classe custom)
model_rapide = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(128, 10)
)

print(model_rapide)
```

> 💡 **Conseil de pro** : Utilisez `nn.Sequential` uniquement pour les **prototypes rapides**. Pour tout projet sérieux, créez une classe héritant de `nn.Module`. Cela vous donne plus de contrôle (skip connections, branches multiples, etc.).

---

## 5. 📦 DataLoader et Dataset

### 5.1 Charger un dataset standard (MNIST)

```python
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Définir les transformations
transform = transforms.Compose([
    transforms.ToTensor(),                              # Image PIL → Tensor [0, 1]
    transforms.Normalize((0.1307,), (0.3081,))         # Normalisation MNIST
])

# Télécharger et charger MNIST
train_dataset = datasets.MNIST(
    root='./data',       # Dossier de téléchargement
    train=True,          # Données d'entraînement
    download=True,       # Télécharger si nécessaire
    transform=transform  # Appliquer les transformations
)

test_dataset = datasets.MNIST(
    root='./data',
    train=False,
    download=True,
    transform=transform
)

print(f"Train : {len(train_dataset)} images")  # 60 000
print(f"Test  : {len(test_dataset)} images")   # 10 000

# Examiner un sample
image, label = train_dataset[0]
print(f"Image shape : {image.shape}")  # torch.Size([1, 28, 28])
print(f"Label       : {label}")        # 5 (le chiffre sur l'image)
```

### 5.2 DataLoader : charger par batches

```python
# Créer les DataLoaders
train_loader = DataLoader(
    train_dataset,
    batch_size=64,       # 64 images par batch
    shuffle=True,        # Mélanger à chaque epoch (ESSENTIEL pour le train)
    num_workers=2,       # Chargement parallèle des données
    pin_memory=True      # Accélère le transfert CPU → GPU
)

test_loader = DataLoader(
    test_dataset,
    batch_size=256,      # Plus grand batch pour l'évaluation (pas de gradients)
    shuffle=False,       # Pas besoin de mélanger pour le test
    num_workers=2,
    pin_memory=True
)

# Itérer sur un batch
for images, labels in train_loader:
    print(f"Batch images : {images.shape}")  # torch.Size([64, 1, 28, 28])
    print(f"Batch labels : {labels.shape}")  # torch.Size([64])
    break  # Juste le premier batch pour l'exemple
```

### 5.3 Dataset personnalisé

```python
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

class MonDataset(Dataset):
    """Dataset personnalisé pour des données tabulaires"""

    def __init__(self, X, y):
        # Convertir en tensors
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)

    def __len__(self):
        """Nombre de samples"""
        return len(self.X)

    def __getitem__(self, idx):
        """Retourner un sample (features, label)"""
        return self.X[idx], self.y[idx]

# Exemple : données synthétiques
X_numpy = np.random.randn(1000, 20)          # 1000 samples, 20 features
y_numpy = np.random.randint(0, 3, size=1000)  # 3 classes

dataset = MonDataset(X_numpy, y_numpy)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Vérification
for batch_X, batch_y in loader:
    print(f"Features : {batch_X.shape}")  # torch.Size([32, 20])
    print(f"Labels   : {batch_y.shape}")  # torch.Size([32])
    break
```

### 5.4 Transforms courants pour les images

```python
from torchvision import transforms

# Transformations d'entraînement (avec data augmentation)
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),       # Flip horizontal aléatoire
    transforms.RandomRotation(degrees=10),          # Rotation aléatoire ±10°
    transforms.RandomCrop(32, padding=4),           # Crop aléatoire avec padding
    transforms.ColorJitter(brightness=0.2,          # Variation de luminosité
                           contrast=0.2),
    transforms.ToTensor(),                          # Conversion en tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # Normalisation ImageNet
                         std=[0.229, 0.224, 0.225])
])

# Transformations de test (PAS de data augmentation)
test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
```

> ⚠️ **Attention** : N'appliquez JAMAIS de data augmentation sur les données de test/validation. La data augmentation est une technique de régularisation pour l'entraînement uniquement.

---

## 6. 🔄 Boucle d'entraînement standard

### 6.1 Le template complet

C'est le code le plus important de ce chapitre. Cette boucle d'entraînement est **réutilisable pour tous vos projets PyTorch**.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

def entrainer(model, train_loader, val_loader, epochs, device):
    """
    Boucle d'entraînement standard PyTorch.
    Réutilisable pour tous les projets.
    """
    # Déplacer le modèle sur le device (GPU si disponible)
    model = model.to(device)

    # Définir la loss function et l'optimizer
    criterion = nn.CrossEntropyLoss()                        # Classification
    optimizer = optim.Adam(model.parameters(), lr=1e-3)      # Optimizer standard

    # Historique pour les courbes
    historique = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [], 'val_acc': []
    }

    for epoch in range(epochs):
        # ==========================================
        # PHASE D'ENTRAÎNEMENT
        # ==========================================
        model.train()  # Mode entraînement (active Dropout, BatchNorm)
        train_loss_total = 0.0
        train_correct = 0
        train_total = 0

        for batch_X, batch_y in train_loader:
            # 1. Envoyer les données sur le device
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            # 2. Forward : calculer la prédiction
            predictions = model(batch_X)

            # 3. Calculer la loss
            loss = criterion(predictions, batch_y)

            # 4. Backward : calculer les gradients
            optimizer.zero_grad()   # Remettre les gradients à zéro
            loss.backward()         # Backpropagation

            # 5. Mettre à jour les poids
            optimizer.step()

            # Accumuler les métriques
            train_loss_total += loss.item() * batch_X.size(0)
            _, predicted = predictions.max(1)
            train_total += batch_y.size(0)
            train_correct += predicted.eq(batch_y).sum().item()

        # Moyennes sur l'epoch
        train_loss = train_loss_total / train_total
        train_acc = train_correct / train_total

        # ==========================================
        # PHASE DE VALIDATION
        # ==========================================
        model.eval()  # Mode évaluation (désactive Dropout, BatchNorm)
        val_loss_total = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():  # Pas de calcul de gradients
            for batch_X, batch_y in val_loader:
                batch_X = batch_X.to(device)
                batch_y = batch_y.to(device)

                predictions = model(batch_X)
                loss = criterion(predictions, batch_y)

                val_loss_total += loss.item() * batch_X.size(0)
                _, predicted = predictions.max(1)
                val_total += batch_y.size(0)
                val_correct += predicted.eq(batch_y).sum().item()

        val_loss = val_loss_total / val_total
        val_acc = val_correct / val_total

        # Sauvegarder l'historique
        historique['train_loss'].append(train_loss)
        historique['val_loss'].append(val_loss)
        historique['train_acc'].append(train_acc)
        historique['val_acc'].append(val_acc)

        # Affichage
        print(f"Epoch {epoch+1:3d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2%} | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2%}")

    return historique
```

> 💡 **Conseil de pro** : Copiez-collez ce template comme **point de départ** pour TOUS vos projets PyTorch. Il contient les bonnes pratiques : `model.train()` / `model.eval()`, `torch.no_grad()`, `optimizer.zero_grad()`.

### 6.2 Les 5 étapes critiques de chaque batch

```
Pour chaque batch :

1. optimizer.zero_grad()     ← Remettre les gradients à zéro
                               (sinon ils s'accumulent !)
2. predictions = model(x)   ← Forward pass
3. loss = criterion(pred, y) ← Calculer la loss
4. loss.backward()           ← Backpropagation (calcul des gradients)
5. optimizer.step()          ← Mise à jour des poids
```

> ⚠️ **Attention** : L'ordre est CRUCIAL. Si vous oubliez `optimizer.zero_grad()`, les gradients s'accumulent d'un batch à l'autre et l'entraînement sera instable. C'est l'erreur #1 des débutants.

### 6.3 `model.train()` vs `model.eval()`

| Mode | Dropout | BatchNorm | Gradients | Quand |
|------|---------|-----------|-----------|-------|
| `model.train()` | Actif (aléatoire) | Statistiques du batch | Calculés | Entraînement |
| `model.eval()` | Désactivé | Statistiques sauvées | Non calculés* | Validation, test, inférence |

*avec `torch.no_grad()` en plus

> ⚠️ **Attention** : Oublier `model.eval()` pendant la validation donnera des résultats incohérents à cause du Dropout aléatoire. C'est l'erreur #2 des débutants.

---

## 7. 💾 Sauvegarder et charger un modèle

### 7.1 Sauvegarder

```python
import torch

# ✅ BONNE PRATIQUE : sauvegarder le state_dict (poids uniquement)
torch.save(model.state_dict(), 'modele_mnist.pth')
print("Modèle sauvegardé !")

# Sauvegarder un checkpoint complet (modèle + optimizer + epoch)
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'train_loss': train_loss,
    'val_loss': val_loss,
    'val_acc': val_acc,
}
torch.save(checkpoint, 'checkpoint_epoch_50.pth')
```

### 7.2 Charger

```python
import torch

# Charger les poids dans un modèle
model = ReseauMNIST()  # Recréer l'architecture
model.load_state_dict(torch.load('modele_mnist.pth', map_location=device))
model.to(device)
model.eval()  # Mode inférence

# Charger un checkpoint complet
checkpoint = torch.load('checkpoint_epoch_50.pth', map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch_reprise = checkpoint['epoch']
print(f"Reprise à l'epoch {epoch_reprise}")
```

> ⚠️ **Attention** : Sauvegardez **TOUJOURS** `state_dict()`, pas le modèle entier avec `torch.save(model, ...)`. Le modèle entier est lié à la structure de fichiers de votre projet et ne sera pas portable.

### 7.3 Sauvegarder le meilleur modèle automatiquement

```python
meilleure_val_loss = float('inf')

for epoch in range(epochs):
    # ... entraînement ...

    # Sauvegarder si c'est le meilleur modèle
    if val_loss < meilleure_val_loss:
        meilleure_val_loss = val_loss
        torch.save(model.state_dict(), 'meilleur_modele.pth')
        print(f"  ✅ Meilleur modèle sauvegardé (val_loss: {val_loss:.4f})")
```

---

## 8. 📊 Visualiser l'entraînement

### 8.1 Courbes de loss avec Matplotlib

```python
import matplotlib.pyplot as plt

def tracer_courbes(historique):
    """Tracer les courbes de loss et d'accuracy"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # --- Courbe de Loss ---
    ax1.plot(historique['train_loss'], label='Train Loss', color='blue')
    ax1.plot(historique['val_loss'], label='Val Loss', color='red')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Courbe de Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Détecter l'overfitting
    if len(historique['val_loss']) > 10:
        min_val = min(historique['val_loss'])
        if historique['val_loss'][-1] > min_val * 1.1:
            ax1.axvline(x=historique['val_loss'].index(min_val),
                        color='orange', linestyle='--',
                        label='Début overfitting')
            ax1.legend()

    # --- Courbe d'Accuracy ---
    ax2.plot(historique['train_acc'], label='Train Acc', color='blue')
    ax2.plot(historique['val_acc'], label='Val Acc', color='red')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title("Courbe d'Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('courbes_entrainement.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Courbes sauvegardées dans courbes_entrainement.png")

# Utilisation après l'entraînement
# tracer_courbes(historique)
```

### 8.2 TensorBoard avec PyTorch

```python
from torch.utils.tensorboard import SummaryWriter

# Créer un writer TensorBoard
writer = SummaryWriter('runs/experience_mnist')

# Dans la boucle d'entraînement, logger les métriques
for epoch in range(epochs):
    # ... entraînement ...

    # Logger dans TensorBoard
    writer.add_scalar('Loss/train', train_loss, epoch)
    writer.add_scalar('Loss/val', val_loss, epoch)
    writer.add_scalar('Accuracy/train', train_acc, epoch)
    writer.add_scalar('Accuracy/val', val_acc, epoch)
    writer.add_scalar('LearningRate', optimizer.param_groups[0]['lr'], epoch)

# Fermer le writer
writer.close()

# Lancer TensorBoard dans le terminal :
# tensorboard --logdir=runs
# Ouvrir http://localhost:6006 dans le navigateur
```

> 💡 **Conseil** : Loggez **TOUJOURS** `train_loss` et `val_loss` à chaque epoch. C'est votre tableau de bord. Sans ces courbes, vous entraînez votre modèle à l'aveugle.

### 8.3 Bonnes pratiques de logging

```python
# Template de logging complet pour chaque epoch
def log_epoch(epoch, epochs, train_loss, val_loss, train_acc, val_acc, lr):
    """Affichage formaté avec diagnostic automatique"""
    ecart_loss = val_loss - train_loss
    ecart_acc = train_acc - val_acc

    # Diagnostic automatique
    if ecart_loss > 0.5 or ecart_acc > 0.1:
        diagnostic = "⚠️  OVERFITTING"
    elif train_loss > 1.0 and epoch > 20:
        diagnostic = "⚠️  UNDERFITTING"
    elif val_loss != val_loss:  # NaN check
        diagnostic = "❌ NaN DETECTED"
    else:
        diagnostic = "✅ OK"

    print(f"Epoch [{epoch+1:3d}/{epochs}] | "
          f"LR: {lr:.2e} | "
          f"Train: {train_loss:.4f} ({train_acc:.1%}) | "
          f"Val: {val_loss:.4f} ({val_acc:.1%}) | "
          f"Écart: {ecart_loss:+.4f} | "
          f"{diagnostic}")
```

---

## 📝 Points clés à retenir

- Les **tensors** sont les briques fondamentales de PyTorch (comme NumPy mais avec GPU + autograd)
- **Autograd** calcule automatiquement les gradients (`backward()`)
- Créez vos réseaux en héritant de **`nn.Module`** (pas `nn.Sequential` pour les projets sérieux)
- **DataLoader** gère les batches, le shuffling et le chargement parallèle
- La boucle d'entraînement suit toujours les 5 étapes : zero_grad → forward → loss → backward → step
- **`model.train()`** pour l'entraînement, **`model.eval()`** pour la validation
- Sauvegardez toujours le **`state_dict()`**, jamais le modèle entier
- Loggez **toujours** train_loss et val_loss pour diagnostiquer votre entraînement

## ✅ Checklist de validation

- [ ] Je sais créer, manipuler et déplacer des tensors (CPU/GPU)
- [ ] Je comprends `requires_grad=True` et `backward()`
- [ ] Je sais construire un réseau avec `nn.Module` (__init__ + forward)
- [ ] Je sais utiliser `DataLoader` avec `batch_size` et `shuffle`
- [ ] Je peux écrire une boucle d'entraînement complète de mémoire
- [ ] Je n'oublie jamais `optimizer.zero_grad()` et `model.eval()`
- [ ] Je sais sauvegarder/charger un modèle avec `state_dict()`
- [ ] Je logue train_loss et val_loss à chaque epoch

---

**Chapitre précédent :** [02 - Réseaux de neurones](./02-reseaux-neurones.md)
**Prochain chapitre :** [04 - Entraînement pratique](./04-entrainement-pratique.md)

[Retour au sommaire](../README.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [PyTorch in 100 seconds](https://www.youtube.com/results?search_query=pytorch+in+100+seconds+fireship) | Fireship | EN | Vue d'ensemble ultra-rapide |
| [PyTorch pour débutant](https://www.youtube.com/results?search_query=pytorch+tutoriel+francais+debutant) | FR | FR | Tensors, autograd, nn.Module |
| [PyTorch full course](https://www.youtube.com/results?search_query=pytorch+beginner+full+course+freecodecamp) | freeCodeCamp | EN | Cours complet PyTorch |
