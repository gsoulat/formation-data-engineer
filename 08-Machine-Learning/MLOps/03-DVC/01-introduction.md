# DVC — Data Version Control

## Pourquoi versionner les données ?

Git gère le code source, mais il n'est pas conçu pour les fichiers lourds (CSV de plusieurs Go, images, modèles). DVC comble ce manque en ajoutant le versioning de données par-dessus Git.

```
Problème classique sans DVC :
─────────────────────────────
"Le modèle de janvier donnait 92% d'accuracy.
 Depuis, les données ont changé.
 Impossible de reproduire les résultats."

Solution avec DVC :
──────────────────
Git commit abc123 ←──────────────────────────────────────┐
  code/train.py (v2)                                      │
  data.dvc  ───────────▶  S3/GCS/Azure  ──▶  data_v2.csv │
                                                          │
git checkout abc123 + dvc pull  ──────────────────────────┘
= reproduction exacte garantie
```

---

## Architecture DVC

```
Votre projet Git
├── .git/                    ← Git normal
├── .dvc/                    ← Configuration DVC
│   ├── config               ← Remote storage, paramètres
│   └── cache/               ← Cache local des fichiers versionnés
├── data/
│   ├── raw.csv.dvc          ← Pointeur DVC (texte, commité dans Git)
│   └── .gitignore           ← Ignore les vrais fichiers data
├── models/
│   ├── model.pkl.dvc        ← Pointeur vers le modèle
│   └── .gitignore
├── dvc.yaml                 ← Définition des pipelines
├── dvc.lock                 ← Lock des étapes du pipeline
└── params.yaml              ← Paramètres du pipeline
```

Les fichiers `.dvc` sont de petits fichiers texte qui pointent vers le vrai contenu stocké ailleurs :

```yaml
# data/raw.csv.dvc
outs:
- md5: a1b2c3d4e5f6...
  size: 52428800
  path: raw.csv
```

---

## Installation et initialisation

```bash
pip install dvc dvc-s3 dvc-gs dvc-azure  # selon votre remote

# Dans un projet Git existant
git init  # si pas encore fait
dvc init

# Vérifier l'initialisation
ls .dvc/
# config  .gitignore

git status
# Nouveaux fichiers : .dvc/.gitignore, .dvcignore, .dvc/config

git commit -m "feat: initialiser DVC"
```

---

## Configurer un remote storage

Le remote est l'espace de stockage distant où DVC pousse les fichiers volumineux.

```bash
# ── Option 1 : Local (pour les tests) ─────────────────────────
mkdir /tmp/dvc-remote
dvc remote add -d myremote /tmp/dvc-remote

# ── Option 2 : Amazon S3 ────────────────────────────────────────
dvc remote add -d myremote s3://mon-bucket/dvc-store
dvc remote modify myremote region eu-west-1

# ── Option 3 : Google Cloud Storage ────────────────────────────
dvc remote add -d myremote gs://mon-bucket/dvc-store

# ── Option 4 : Azure Blob Storage ──────────────────────────────
dvc remote add -d myremote azure://mon-container/dvc-store

# ── Option 5 : Serveur SSH ───────────────────────────────────────
dvc remote add -d myremote ssh://user@server/path/to/dvc-store

# Voir la configuration
cat .dvc/config
# [core]
#     remote = myremote
# ['remote "myremote"']
#     url = s3://mon-bucket/dvc-store

git add .dvc/config
git commit -m "config: ajouter remote DVC S3"
```

---

## Tracker des fichiers de données

```bash
# ── Ajouter un fichier sous contrôle DVC ────────────────────────
dvc add data/raw/housing.csv

# DVC a créé :
# - data/raw/housing.csv.dvc   ← pointeur à committer
# - data/raw/.gitignore        ← ignore housing.csv dans Git

cat data/raw/housing.csv.dvc
# outs:
# - md5: 5d41402abc4b2a76b9719d911017c592
#   size: 1857200
#   nfiles: null
#   path: housing.csv

# Committer le pointeur dans Git (PAS le vrai fichier)
git add data/raw/housing.csv.dvc data/raw/.gitignore
git commit -m "data: ajouter housing.csv v1"

# Pousser les données vers le remote
dvc push
# Uploading 1 file to s3://mon-bucket/dvc-store

# ── Ajouter un répertoire entier ─────────────────────────────────
dvc add data/images/
git add data/images.dvc data/.gitignore
git commit -m "data: ajouter dataset images"
dvc push
```

---

## Workflow quotidien avec DVC

```bash
# ── Récupérer une version précédente ────────────────────────────

# 1. Revenir au commit git souhaité
git checkout abc123

# 2. Récupérer les données correspondantes depuis le remote
dvc pull
# Les fichiers de data correspondent maintenant exactement
# à l'état du code au commit abc123

# ── Mettre à jour les données ────────────────────────────────────
# (nouvelles données disponibles)

# Remplacer le fichier
cp nouveau_dataset.csv data/raw/housing.csv

# Ré-ajouter sous DVC
dvc add data/raw/housing.csv

# Committer le pointeur mis à jour
git add data/raw/housing.csv.dvc
git commit -m "data: mise à jour housing.csv - nouvelles données jan 2024"

# Pousser les nouvelles données
dvc push

# ── Partager avec un collègue ─────────────────────────────────────
# Côté collègue :
git clone https://github.com/mon-org/mon-projet.git
cd mon-projet
dvc pull  # Télécharge toutes les données depuis le remote
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans le terminal : (1) `dvc add` qui crée le fichier `.dvc`, (2) `git log --oneline` montrant les commits de données, (3) `git checkout` d'un ancien commit suivi de `dvc pull` qui restaure les anciennes données.
> **Expliquer :** "La clé à comprendre : Git stocke uniquement le petit fichier `.dvc` (quelques lignes de texte), mais DVC sait retrouver exactement quels données correspondaient à ce commit. C'est comme Git LFS mais plus puissant."

---

## Comparer des versions de données

```bash
# Voir la différence entre deux versions d'un fichier DVC
git diff HEAD~1 data/raw/housing.csv.dvc
# - md5: 5d41402abc4b2a76b9719d911017c592
# + md5: 7215ee9c7d9dc229d2921a40e899ec5f
# -   size: 1857200
# +   size: 2456300

# DVC status : voir si les données sont synchronisées
dvc status
# data/raw/housing.csv.dvc:
#         changed outs:
#                 modified: data/raw/housing.csv

# DVC diff : comparer avec le remote
dvc diff HEAD~1 HEAD
# Modified:
#   data/raw/housing.csv
#     (size: 1857200 → 2456300)
```

---

## Gérer le cache DVC

```bash
# Voir l'espace utilisé par le cache local
du -sh .dvc/cache/

# Supprimer les fichiers du cache non référencés
dvc gc --workspace          # Garder uniquement la version actuelle
dvc gc --all-commits        # Garder toutes les versions commitées
dvc gc --cloud              # Nettoyer aussi le remote

# Configurer un cache partagé (équipe)
dvc config cache.dir /shared/dvc-cache
```

---

## DVC avec des credentials AWS

```bash
# Option 1 : Variables d'environnement (recommandé CI/CD)
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=yyy

# Option 2 : Profil AWS configuré
aws configure  # ou ~/.aws/credentials

# Option 3 : Credentials dans DVC config (NON recommandé pour Git)
dvc remote modify myremote access_key_id xxx
dvc remote modify myremote secret_access_key yyy

# Pour GitHub Actions, utiliser les secrets :
# AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY comme secrets repo
```

---

## Exemple complet : projet réel

```bash
# Structure d'un projet ML avec DVC
mkdir ml-project && cd ml-project
git init
dvc init

# Créer la structure
mkdir -p data/raw data/processed models reports

# Script Python de préparation des données
cat > prepare_data.py << 'EOF'
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['target'] = housing.target

train, test = train_test_split(df, test_size=0.2, random_state=42)

train.to_csv("data/processed/train.csv", index=False)
test.to_csv("data/processed/test.csv", index=False)
print(f"Train: {len(train)} lignes, Test: {len(test)} lignes")
EOF

python prepare_data.py

# Versionner les données traitées
dvc add data/processed/train.csv data/processed/test.csv
git add data/processed/.gitignore data/processed/train.csv.dvc data/processed/test.csv.dvc
git commit -m "data: ajouter données train/test v1"

# Configurer le remote et pousser
dvc remote add -d local_remote /tmp/dvc-remote-ml-project
git add .dvc/config
git commit -m "config: DVC remote local"
dvc push

echo "Projet DVC initialisé avec succès !"
```

---

## Bonnes pratiques DVC

```
Structure recommandée :
─────────────────────
data/
├── raw/           ← Données brutes, jamais modifiées
│   └── *.dvc
├── processed/     ← Données transformées
│   └── *.dvc
└── external/      ← Données tierces

models/            ← Modèles entraînés
├── *.pkl.dvc

reports/           ← Rapports de métriques
├── metrics.json.dvc
```

```bash
# Ne JAMAIS faire :
git add data/raw/huge_file.csv   # ← Mauvais ! Utiliser DVC

# Toujours faire :
dvc add data/raw/huge_file.csv
git add data/raw/huge_file.csv.dvc
git commit -m "data: ..."
dvc push

# Pour éviter les erreurs, ajouter dans .gitignore global
echo "*.csv" >> .gitignore  # Puis être plus précis par dossier
```

---

## Résumé des commandes DVC essentielles

```bash
dvc init                    # Initialiser DVC dans un repo Git
dvc remote add -d NAME URL  # Configurer le remote
dvc add FILE                # Tracker un fichier/dossier
dvc push                    # Envoyer vers le remote
dvc pull                    # Récupérer depuis le remote
dvc fetch                   # Télécharger sans extraire
dvc status                  # État de synchronisation
dvc diff                    # Différences entre versions
dvc gc --workspace          # Nettoyer le cache
dvc repro                   # Rejouer le pipeline (voir 02-pipelines.md)
```
