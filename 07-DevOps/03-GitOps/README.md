# 03 — GitOps avec ArgoCD

> **Niveau** : intermédiaire → avancé · **Prérequis** : [Kubernetes](../../02-Containerisation/Kubernetes/), [CI/CD](../01-CI-CD/), Git.
> **Objectif** : comprendre le GitOps, déployer **ArgoCD**, et faire déployer une application **automatiquement depuis un dépôt Git** — avec auto-réparation de la dérive.

---

## 1. 🧠 Le problème que le GitOps résout

En CI/CD « classique » (push), c'est ton **pipeline** qui pousse vers le cluster :

```
git push → pipeline CI/CD → `kubectl apply` / `helm upgrade` → cluster
```

Trois soucis en production :
- **Le cluster peut dériver.** Quelqu'un fait un `kubectl edit` à la main un vendredi soir → l'état réel ne correspond plus à ce qui est écrit quelque part. Personne ne le sait.
- **Le pipeline a les clés du cluster.** Tes runners CI ont des droits d'admin sur la prod — grosse surface d'attaque.
- **Pas de source de vérité.** « Qu'est-ce qui tourne réellement en prod, exactement ? » n'a pas de réponse fiable.

**GitOps inverse le sens :** l'état désiré du cluster est **décrit dans Git** (la source de vérité unique), et un **agent dans le cluster** tire (pull) cet état et le fait converger en continu.

```
git push → (Git = état désiré) ← ArgoCD (agent dans le cluster) → applique & surveille
```

## 2. 📐 Les 4 principes du GitOps

1. **Déclaratif** : tout l'état du système est décrit en YAML (pas de commandes impératives).
2. **Versionné dans Git** : Git est la **source de vérité unique**. Un rollback = un `git revert`.
3. **Tiré automatiquement (pull)** : un agent applique l'état de Git — le cluster n'a pas besoin de donner ses accès au pipeline.
4. **Réconciliation continue** : l'agent compare en boucle l'état réel à l'état désiré et **corrige la dérive** (self-healing).

### Push vs Pull

| | CI/CD classique (push) | GitOps (pull) |
|---|---|---|
| Qui applique ? | le pipeline, de l'extérieur | un agent **dans** le cluster |
| Accès cluster | donné au CI | reste dans le cluster |
| Dérive manuelle | non détectée | **détectée & corrigée** |
| Rollback | relancer un vieux pipeline | `git revert` |
| Source de vérité | floue | **le dépôt Git** |

## 3. ⚙️ ArgoCD

**ArgoCD** est le contrôleur GitOps le plus répandu (alternative : Flux). Il tourne dans le cluster et introduit une ressource personnalisée : l'**`Application`**.

Une `Application` dit : *« surveille CE dépôt Git / CE chemin, et fais correspondre CE cluster / CE namespace. »*

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: boutique-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/mon-org/mon-repo-manifests.git
    targetRevision: main          # la branche/tag suivi
    path: k8s/boutique-api        # le dossier de manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: boutique
  syncPolicy:
    automated:
      prune: true      # supprime ce qui n'est plus dans Git
      selfHeal: true   # corrige toute dérive manuelle
    syncOptions:
      - CreateNamespace=true
```

Trois notions clés qu'ArgoCD affiche en permanence :
- **Sync status** : `Synced` (le cluster = Git) ou `OutOfSync` (dérive détectée).
- **Health status** : `Healthy` / `Progressing` / `Degraded` (l'app tourne-t-elle vraiment ?).
- **Self-heal** : si `selfHeal: true`, une modif manuelle est **automatiquement annulée**.

> 💡 **Le déclic** : tu ne fais plus `kubectl apply`. Tu fais `git push` sur ton dépôt de manifests, et ArgoCD synchronise. Pour déployer la v2 : tu changes le tag d'image dans Git. Pour revenir en arrière : `git revert`.

## 4. 🧪 Lab — déployer une app depuis Git avec ArgoCD

**Pré-requis** : un cluster local ([kind](https://kind.sigs.k8s.io/) ou [minikube](https://minikube.sigs.k8s.io/)) et `kubectl`.

### Étape 1 — Installer ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd rollout status deploy/argocd-server   # attendre que ce soit prêt
```

### Étape 2 — Ouvrir l'interface

```bash
# mot de passe admin initial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
# accès local
kubectl -n argocd port-forward svc/argocd-server 8080:443
# → https://localhost:8080  (user: admin)
```

### Étape 3 — Déclarer une Application

Prépare un dépôt Git (public pour ce lab) contenant un manifest simple, par ex. `guestbook/` (l'exemple officiel `https://github.com/argoproj/argocd-example-apps`). Puis applique l'`Application` (adapte `repoURL`) :

```bash
kubectl apply -n argocd -f - <<'YAML'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: guestbook, namespace: argocd }
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination: { server: https://kubernetes.default.svc, namespace: guestbook }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
YAML
```

Dans l'UI, l'app passe `OutOfSync` → `Synced` → `Healthy`. Vérifie :

```bash
kubectl -n guestbook get pods
```

### Étape 4 — 🎯 À toi de jouer : provoque une dérive

Modifie l'app **à la main** (ce qu'on ne devrait JAMAIS faire) et observe ArgoCD la corriger :

```bash
kubectl -n guestbook scale deploy guestbook-ui --replicas=5
# regarde l'UI ArgoCD : OutOfSync détecté, puis selfHeal remet à la valeur de Git
kubectl -n guestbook get deploy guestbook-ui   # revenu à la valeur du dépôt
```

Puis fais un **vrai** changement : modifie le nombre de replicas **dans Git**, `git push`, et regarde ArgoCD synchroniser tout seul.

## 5. 🏗️ Aller plus loin

- **App of Apps** : une `Application` racine qui pointe vers un dossier d'autres `Application`s → tu gères des dizaines d'apps de façon déclarative.
- **Déploiements progressifs** : [**Argo Rollouts — canary & blue/green**](04-argo-rollouts-canary-bluegreen.md) remplace le `Deployment` par un `Rollout` qui fait du **canary** (20% → 50% → 100%) ou du **blue/green**, avec **analyse automatique des métriques Prometheus** et **rollback** si les SLO se dégradent. → leçon complète avec manifests et lab.
- **Secrets** : ne mets jamais de secret en clair dans Git → **Sealed Secrets** (Bitnami) ou **External Secrets Operator** (référence un coffre : Vault, AWS Secrets Manager, Key Vault).
- **Structure de dépôts** : sépare le dépôt *applicatif* (code) du dépôt *manifests* (état désiré) ; le pipeline CI construit l'image et met à jour le tag dans le dépôt manifests → ArgoCD déploie.

## ✅ Checklist de validation

- [ ] ArgoCD installé et accessible via l'UI
- [ ] Une `Application` déclarée qui suit un dépôt Git
- [ ] L'app passe `Synced` / `Healthy`
- [ ] Une dérive manuelle est **corrigée automatiquement** (selfHeal démontré)
- [ ] Un changement poussé dans Git est déployé sans `kubectl apply`

## 🔗 Ressources

- Documentation ArgoCD : https://argo-cd.readthedocs.io/
- Exemples officiels : https://github.com/argoproj/argocd-example-apps
- Argo Rollouts (déploiements progressifs) : https://argoproj.github.io/rollouts/
- Principes GitOps (OpenGitOps) : https://opengitops.dev/
