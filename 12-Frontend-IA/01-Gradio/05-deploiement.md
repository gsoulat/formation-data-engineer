# 05 — Déploiement d'une application Gradio

## Vue d'ensemble

Une application Gradio développée localement doit être déployée pour être accessible aux autres. Ce chapitre couvre trois stratégies de déploiement, du plus simple au plus robuste :

1. **`share=True`** — lien temporaire Gradio, idéal pour les démos rapides
2. **Hugging Face Spaces** — hébergement gratuit, adapté au partage communautaire
3. **Docker** — déploiement sur n'importe quel serveur, pour la production

## `share=True` — Partage rapide temporaire

La manière la plus simple de partager une application :

```python
demo.launch(share=True)
```

Gradio crée un tunnel sécurisé et vous donne une URL publique du type `https://abcd1234.gradio.live`. Ce lien est valable **72 heures**.

Quand utiliser `share=True` :
- Démo rapide à un client ou un collègue
- Test depuis un autre appareil ou réseau
- Présentation en formation

Quand ne pas l'utiliser :
- Application en production permanente
- Données sensibles (le trafic transite par les serveurs Gradio)
- Besoin de haute disponibilité

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancement avec `share=True`, affichage de l'URL temporaire dans le terminal, ouverture de l'URL depuis un autre appareil (smartphone ou autre ordinateur)
> **Expliquer :** Montrer que l'URL est accessible depuis n'importe où sur internet. Préciser la limitation de 72h. Expliquer que c'est parfait pour "je veux montrer mon modèle maintenant" mais pas pour une mise en production sérieuse.
---

## Authentification basique

Pour protéger l'accès à une interface :

```python
# Un seul utilisateur
demo.launch(auth=("admin", "motdepasse123"))

# Plusieurs utilisateurs
demo.launch(auth=[
    ("alice", "pass1"),
    ("bob", "pass2"),
    ("formateur", "demo2024"),
])

# Avec une fonction d'authentification personnalisée
def verifier_auth(username, password):
    # Peut faire une requête DB, vérifier un fichier, etc.
    utilisateurs_autorises = {
        "alice": "hash_du_mot_de_passe",
        "bob": "autre_hash",
    }
    return utilisateurs_autorises.get(username) == password

demo.launch(auth=verifier_auth, auth_message="Accès réservé aux stagiaires de la formation.")
```

## Hugging Face Spaces

Hugging Face Spaces est une plateforme d'hébergement gratuite pour les applications ML. C'est la destination naturelle pour les démonstrations Gradio.

### Créer un Space

1. Créez un compte sur https://huggingface.co
2. Cliquez sur **New Space**
3. Choisissez **Gradio** comme SDK
4. Choisissez la visibilité (Public ou Private)

### Structure du projet pour Hugging Face Spaces

```
mon-space/
├── app.py           # point d'entrée (obligatoire)
├── requirements.txt # dépendances (obligatoire)
├── README.md        # métadonnées du Space (optionnel mais recommandé)
└── model.pkl        # votre modèle (si applicable)
```

Le fichier `README.md` doit contenir les métadonnées en en-tête YAML :

```markdown
---
title: Mon Assistant Data Engineering
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
---

# Mon Assistant Data Engineering

Description de l'application...
```

### `requirements.txt`

```text
gradio>=4.44.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
```

> **Attention :** Ne pas inclure `openai` ou d'autres clients API dans le `requirements.txt` si vous utilisez des secrets — gérez-les via les **Secrets** du Space sur Hugging Face.

### Gestion des secrets sur Hugging Face

```python
import os
import gradio as gr
from openai import OpenAI

# Hugging Face injecte les secrets comme variables d'environnement
# Les définir dans Settings > Variables and Secrets de votre Space
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def repondre(message, historique):
    if not client.api_key:
        return "", historique + [
            {"role": "assistant", "content": "Erreur : clé API non configurée."}
        ]
    # ... reste de la logique
```

### Déploiement via Git

```bash
# Cloner le Space (remplacer par votre username et nom de space)
git clone https://huggingface.co/spaces/votre-username/mon-space

# Copier vos fichiers
cp app.py mon-space/
cp requirements.txt mon-space/

# Pousser
cd mon-space
git add .
git commit -m "Initial deployment"
git push
```

Hugging Face rebuild automatiquement le Space à chaque push. Le build prend quelques minutes.

### Déploiement via l'interface web

Pour les débutants, il est plus simple d'uploader les fichiers directement via l'interface web de Hugging Face Spaces (Files > Add file > Upload files).

## Docker

Docker permet de déployer sur n'importe quel serveur (cloud ou on-premise) avec une reproductibilité totale.

### `Dockerfile` pour Gradio

```dockerfile
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copier les dépendances en premier (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Gradio écoute sur ce port par défaut
EXPOSE 7860

# Variable d'environnement pour écouter sur toutes les interfaces
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# Lancement
CMD ["python", "app.py"]
```

### `app.py` adapté pour Docker

```python
import gradio as gr
import os

def ma_fonction(input_text):
    return f"Résultat : {input_text.upper()}"

demo = gr.Interface(
    fn=ma_fonction,
    inputs=gr.Textbox(label="Entrée"),
    outputs=gr.Textbox(label="Sortie"),
)

# Récupérer les configs depuis les variables d'environnement
demo.launch(
    server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
    server_port=int(os.environ.get("GRADIO_SERVER_PORT", 7860)),
    share=False,
)
```

### `docker-compose.yml`

```yaml
version: "3.8"

services:
  gradio-app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
    volumes:
      - ./models:/app/models  # monter les modèles sans rebuild
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Commandes Docker

```bash
# Builder l'image
docker build -t mon-app-gradio .

# Lancer avec les variables d'environnement
docker run -p 7860:7860 \
  -e OPENAI_API_KEY="sk-..." \
  mon-app-gradio

# Avec docker-compose (les variables viennent du fichier .env)
docker compose up

# En arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f gradio-app

# Arrêter
docker compose down
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Build Docker avec `docker build`, puis `docker run`, puis accès à l'application via `http://localhost:7860`
> **Expliquer :** Montrer chaque étape du Dockerfile pendant le build (téléchargement de l'image Python, installation des dépendances, copie du code). Expliquer pourquoi on copie `requirements.txt` en premier : si le code change mais pas les dépendances, Docker réutilise le cache pour l'étape `pip install`, ce qui accélère les rebuilds. Montrer l'application accessible dans le navigateur.
---

## Déploiement sur un VPS ou serveur cloud

### Avec un reverse proxy Nginx

Pour un déploiement professionnel, Gradio tourne derrière Nginx qui gère le SSL et le nom de domaine :

```nginx
# /etc/nginx/sites-available/mon-app-gradio
server {
    listen 80;
    server_name mon-app.exemple.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name mon-app.exemple.com;

    ssl_certificate /etc/letsencrypt/live/mon-app.exemple.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mon-app.exemple.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # nécessaire pour WebSocket (streaming)
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;  # éviter timeout pendant la génération longue
    }
}
```

> **Important :** La directive `Upgrade` et `Connection "upgrade"` est indispensable pour que le streaming Gradio fonctionne à travers Nginx. Sans elle, le streaming ne marche pas.

### Script de déploiement complet

```bash
#!/bin/bash
# deploy.sh

set -e  # arrêter en cas d'erreur

echo "Déploiement de l'application Gradio..."

# Aller dans le répertoire du projet
cd /opt/mon-app-gradio

# Mettre à jour le code
git pull origin main

# Rebuilder et redémarrer avec docker-compose
docker compose pull
docker compose build
docker compose up -d --no-deps gradio-app

echo "Déploiement terminé. Application disponible sur https://mon-app.exemple.com"
```

## Récapitulatif des options de déploiement

| Option | Coût | Durée | Cas d'usage |
|--------|------|-------|-------------|
| `share=True` | Gratuit | 72h max | Démo rapide, test |
| HF Spaces (CPU) | Gratuit | Permanent | Démo publique, portfolio |
| HF Spaces (GPU) | ~0.05$/h | À la demande | Modèles lourds |
| Docker sur VPS | ~5-10€/mois | Permanent | Production interne |
| Docker sur cloud | Variable | À la demande | Production scalable |

## Résumé du chapitre

- `share=True` est idéal pour les démos rapides mais limité à 72h
- Hugging Face Spaces offre un hébergement gratuit permanent pour les applications publiques
- Les secrets (clés API) se configurent dans les paramètres du Space, jamais dans le code
- Docker garantit la reproductibilité et le déploiement sur n'importe quel serveur
- Derrière Nginx, configurer `Upgrade` et `Connection "upgrade"` pour le streaming WebSocket
- Toujours copier `requirements.txt` avant le code dans le Dockerfile pour optimiser le cache

Ce chapitre conclut le module Gradio. Passez aux exercices pour pratiquer, puis consultez la cheatsheet pour une référence rapide.
