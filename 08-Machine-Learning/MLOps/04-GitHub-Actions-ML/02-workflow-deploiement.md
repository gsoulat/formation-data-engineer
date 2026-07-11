# GitHub Actions — Workflow de déploiement ML

## CD pour le Machine Learning

Le workflow de déploiement (Continuous Deployment) prend le modèle validé par le CI et le pousse en production de façon automatisée et sécurisée.

```
Merge sur main (après validation CI)
              │
              ▼
    Build image Docker
              │
              ▼
    Push vers registry
              │
              ▼
    Tests d'intégration
              │
         ┌────┴────┐
         │ Staging │────────────────▶ Tests smoke
         └────┬────┘                      │
              │ approbation manuelle       │
              │ (environment protection)   │
              ▼                           │
         Production ◀─────────────────────┘
              │
              ▼
    Health check + smoke test
              │
         ┌────┴────┐
      OK  │         │  KO
         ▼         ▼
    Terminé     Rollback auto
```

---

## Workflow de déploiement complet

```yaml
# .github/workflows/deploy.yml
name: Deploy ML Model

on:
  workflow_run:
    workflows: ["ML Training Pipeline"]
    types: [completed]
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environnement cible'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      model_version:
        description: 'Version du modèle MLflow (laisser vide = Production)'
        required: false
        type: string

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/prix-immobilier-api
  PYTHON_VERSION: '3.11'

jobs:
  # ── Job 1 : Vérifier que le CI a réussi ──────────────────────
  check-ci:
    name: Check CI Status
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch'
    steps:
      - name: CI passed
        run: echo "CI pipeline succeeded, proceeding to deploy"

  # ── Job 2 : Build et push de l'image Docker ──────────────────
  build-and-push:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: check-ci
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
      image_digest: ${{ steps.build.outputs.digest }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Download training artifacts
        uses: actions/download-artifact@v4
        with:
          name: model-${{ github.sha }}
          path: ./artifacts/
        continue-on-error: true  # Si pas d'artifact (deploy manuel)

      # Authentification au registry GitHub Container Registry
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Extraire les métadonnées pour le tag de l'image
      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      # Build multi-platform avec cache
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GIT_COMMIT=${{ github.sha }}
            BUILD_DATE=${{ github.event.head_commit.timestamp }}

      - name: Image digest
        run: echo "Image digest: ${{ steps.build.outputs.digest }}"

  # ── Job 3 : Tests de l'image Docker ──────────────────────────
  test-image:
    name: Test Docker Image
    runs-on: ubuntu-latest
    needs: build-and-push

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Pull image
        run: |
          docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}

      - name: Start container
        run: |
          docker run -d \
            --name test-api \
            -p 8000:8000 \
            -e MLFLOW_TRACKING_URI=${{ secrets.MLFLOW_TRACKING_URI }} \
            -e MODEL_NAME=prix-immobilier-rf \
            -e MODEL_STAGE=Production \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}

          # Attendre que l'API soit prête
          timeout 60 bash -c 'until curl -sf http://localhost:8000/health; do sleep 2; done'

      - name: Run smoke tests
        run: |
          # Test health endpoint
          curl -f http://localhost:8000/health

          # Test prediction endpoint
          curl -f -X POST http://localhost:8000/predict \
            -H "Content-Type: application/json" \
            -d '{
              "MedInc": 8.3252,
              "HouseAge": 41.0,
              "AveRooms": 6.984,
              "AveBedrms": 1.024,
              "Population": 322.0,
              "AveOccup": 2.556,
              "Latitude": 37.88,
              "Longitude": -122.23
            }' | python -c "
          import json, sys
          data = json.load(sys.stdin)
          assert 'prix_predit' in data, 'Champ prix_predit manquant'
          assert data['prix_predit'] > 0, 'Prix négatif'
          print(f'Prix prédit: {data[\"prix_predit\"]}')
          "

      - name: Stop and remove container
        if: always()
        run: docker stop test-api && docker rm test-api

  # ── Job 4 : Déploiement en Staging ───────────────────────────
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: test-image
    environment:
      name: staging
      url: https://staging.mon-api.com

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to staging
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG_STAGING }}
        run: |
          # Exemple avec kubectl
          echo "$KUBE_CONFIG" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

          kubectl set image deployment/prix-immobilier-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }} \
            --namespace=staging

          kubectl rollout status deployment/prix-immobilier-api \
            --namespace=staging \
            --timeout=5m

      - name: Smoke test staging
        run: |
          sleep 10  # Attendre le démarrage
          curl -f https://staging.mon-api.com/health

      - name: Notify Slack (staging deployed)
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "✅ Modèle déployé en staging: sha-${{ github.sha }}\nhttps://staging.mon-api.com"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        continue-on-error: true

  # ── Job 5 : Déploiement en Production (avec approbation) ─────
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production   # Environnement protégé → approbation requise
      url: https://api.mon-api.com

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to production
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG_PROD }}
        run: |
          echo "$KUBE_CONFIG" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

          # Stratégie Blue-Green : mettre à jour le déploiement green
          kubectl set image deployment/prix-immobilier-api-green \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }} \
            --namespace=production

          kubectl rollout status deployment/prix-immobilier-api-green \
            --namespace=production \
            --timeout=10m

      - name: Switch traffic to new version
        run: |
          # Basculer le service de blue vers green
          kubectl patch service prix-immobilier-api \
            -p '{"spec":{"selector":{"version":"green"}}}' \
            --namespace=production

      - name: Production smoke test
        run: |
          sleep 5
          curl -f https://api.mon-api.com/health

      - name: Promote model in MLflow Registry
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python scripts/promote_to_production.py \
            --git-sha ${{ github.sha }}

      - name: Update deployment tag in registry
        run: |
          docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }} \
                     ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:stable
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:stable

  # ── Job 6 : Rollback automatique si échec ────────────────────
  rollback:
    name: Rollback on Failure
    runs-on: ubuntu-latest
    needs: deploy-production
    if: failure()

    steps:
      - name: Rollback production deployment
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG_PROD }}
        run: |
          echo "$KUBE_CONFIG" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

          # Revenir à la version stable précédente
          kubectl rollout undo deployment/prix-immobilier-api-green \
            --namespace=production

          # Rebascule le trafic vers blue
          kubectl patch service prix-immobilier-api \
            -p '{"spec":{"selector":{"version":"blue"}}}' \
            --namespace=production

          echo "Rollback effectué"

      - name: Notify team
        uses: slackapi/slack-github-action@v1.26.0
        with:
          payload: |
            {
              "text": "🚨 ROLLBACK effectué en production!\nCommit: ${{ github.sha }}\nRaison: Échec du déploiement"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        continue-on-error: true
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans GitHub, montrer la page Environments (Settings → Environments → production) avec les "Required reviewers" configurés. Puis montrer un workflow en attente d'approbation avec le bouton "Review deployments".
> **Expliquer :** "C'est un garde-fou crucial : personne ne peut déployer en production sans qu'un humain approuve. Même si tous les tests passent, un data scientist senior ou un tech lead doit valider avant que le code parte en prod. GitHub notifie automatiquement les reviewers."

---

## Dockerfile optimisé pour ML

```dockerfile
# Dockerfile
# ── Stage 1 : Builder ─────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Installer les outils de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Stage 2 : Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Métadonnées
LABEL org.opencontainers.image.source=https://github.com/mon-org/mon-projet
LABEL org.opencontainers.image.description="API de prédiction prix immobilier"

# Arguments de build
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_DATE=${BUILD_DATE}

# Variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MLFLOW_TRACKING_URI=http://mlflow:5000 \
    MODEL_NAME=prix-immobilier-rf \
    MODEL_STAGE=Production \
    PORT=8000

WORKDIR /app

# Copier les dépendances installées depuis le builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copier le code de l'application
COPY api/ ./api/

# Utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Script de promotion MLflow

```python
# scripts/promote_to_production.py
"""Promeut le modèle MLflow correspondant au commit en production."""
import argparse
import mlflow
import os
import sys

def promote_model(git_sha: str):
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    client = mlflow.tracking.MlflowClient()

    model_name = "prix-immobilier-rf"

    # Chercher le run correspondant au commit Git
    runs = client.search_runs(
        experiment_ids=[
            client.get_experiment_by_name("prix-immobilier-dvc").experiment_id
        ],
        filter_string=f"tags.git_commit = '{git_sha[:8]}'",
        order_by=["start_time DESC"],
        max_results=1
    )

    if not runs:
        print(f"Aucun run MLflow trouvé pour le commit {git_sha[:8]}")
        print("Utilisation de la version Staging existante...")
        staging = client.get_latest_versions(model_name, stages=["Staging"])
        if not staging:
            print("Aucune version en Staging non plus. Abandon.")
            sys.exit(1)
        version = staging[0].version
    else:
        run_id = runs[0].info.run_id
        # Trouver la version du modèle associée à ce run
        versions = client.search_model_versions(
            f"name='{model_name}' and run_id='{run_id}'"
        )
        if not versions:
            print(f"Aucune version du modèle pour le run {run_id}")
            sys.exit(1)
        version = versions[0].version

    # Promouvoir en production
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production",
        archive_existing_versions=True
    )

    client.set_model_version_tag(
        name=model_name,
        version=version,
        key="deployed_by",
        value="github_actions"
    )
    client.set_model_version_tag(
        name=model_name,
        version=version,
        key="git_sha",
        value=git_sha
    )

    print(f"Version {version} du modèle '{model_name}' promue en Production")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-sha", required=True)
    args = parser.parse_args()
    promote_model(args.git_sha)
```

---

## Workflow simplifié pour Heroku / Render / Railway

Pour des projets plus simples sans Kubernetes :

```yaml
# .github/workflows/deploy-simple.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true
```

---

## Résumé des patterns CI/CD ML

| Pattern | Avantage | Quand utiliser |
|---|---|---|
| **Build on push** | Simple | Toutes les équipes |
| **Environment protection** | Approbation manuelle | Production critique |
| **Blue-Green** | Zero downtime | APIs haute dispo |
| **Canary release** | Risque progressif | A/B testing modèle |
| **Rollback auto** | Résilience | Toujours recommandé |
| **Smoke tests** | Validation rapide | Toujours recommandé |
