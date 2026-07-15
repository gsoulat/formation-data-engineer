# 13 - Helm

[← 12 - RBAC](12-rbac-securite.md) | [🏠 Accueil](README.md) | [GitOps →](../../07-DevOps/03-GitOps/README.md)

---

## 13. Packager et déployer avec Helm

Une application réelle, c'est une dizaine de YAML (Deployment, Service, Ingress, ConfigMap, HPA…)
**dupliqués** pour chaque environnement (dev/staging/prod) avec juste quelques valeurs qui changent.
**Helm** est le **gestionnaire de paquets** de Kubernetes : il empaquette tous ces manifests en un
**chart** paramétrable.

> **Analogie** — Helm est à Kubernetes ce que `apt` ou `npm` est à ton système : au lieu d'installer 12
> fichiers à la main, tu fais `helm install`. Un **chart**, c'est un **gabarit** : le même moule, des
> valeurs différentes selon l'environnement.

### Vocabulaire

| Terme | Sens |
|---|---|
| **Chart** | le paquet (templates + valeurs par défaut) |
| **Values** | les paramètres (`values.yaml`) qui remplissent les templates |
| **Release** | une **instance installée** d'un chart (ex. `boutique-prod`) |
| **Repository** | un dépôt de charts publics (ex. Bitnami) |

### Structure d'un chart

```
boutique-api/
├── Chart.yaml            # nom, version du chart
├── values.yaml           # valeurs par défaut
└── templates/
    ├── deployment.yaml   # manifests "templatés" avec {{ .Values.xxx }}
    ├── service.yaml
    └── _helpers.tpl       # fonctions réutilisables
```

Le cœur : un manifest devient un **template**.

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-api
spec:
  replicas: {{ .Values.replicaCount }}          # ← valeur injectée
  template:
    spec:
      containers:
      - name: api
        image: "{{ .Values.image.repo }}:{{ .Values.image.tag }}"
```

```yaml
# values.yaml (les valeurs par défaut, surchargées par environnement)
replicaCount: 2
image:
  repo: mon-org/boutique-api
  tag: "1.4.0"
```

### Les commandes essentielles

```bash
# Créer un chart de départ
helm create boutique-api

# Installer (créer une release)
helm install boutique-prod ./boutique-api -n prod --create-namespace

# Surcharger des valeurs pour la prod
helm install boutique-prod ./boutique-api -f values-prod.yaml
helm install boutique-prod ./boutique-api --set replicaCount=5

# Mettre à jour (déployer la v2 = juste changer image.tag)
helm upgrade boutique-prod ./boutique-api --set image.tag=1.5.0

# Revenir en arrière (LE gros avantage : rollback atomique)
helm history boutique-prod
helm rollback boutique-prod 1        # revenir à la révision 1

# Voir le rendu SANS déployer (débogage)
helm template ./boutique-api -f values-prod.yaml

# Désinstaller
helm uninstall boutique-prod -n prod
```

### Installer un chart public

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install ma-base bitnami/postgresql      # PostgreSQL en une commande
```

> 💡 **Un chart, plusieurs environnements** — le même chart + `values-dev.yaml` / `values-prod.yaml`
> = zéro duplication. C'est exactement ce qu'on versionne dans un dépôt GitOps (voir chapitre suivant).

> 🛑 **Erreur courante** — mettre des **secrets en clair** dans `values.yaml` poussé sur Git. Utilise
> `--set` en CI depuis un coffre, ou des outils comme *Sealed Secrets* / *External Secrets*.

## ✅ À retenir

- Helm **empaquette** des manifests en un **chart** paramétrable par des **values**.
- Une **release** = une instance installée ; `helm upgrade`/`rollback` gèrent les versions **atomiquement**.
- Un chart + un fichier de valeurs par environnement = **zéro duplication** dev/staging/prod.
- Helm est le pont naturel vers le **GitOps** : on versionne le chart et les values.

[← 12 - RBAC](12-rbac-securite.md) | [🏠 Accueil](README.md) | [GitOps →](../../07-DevOps/03-GitOps/README.md)
