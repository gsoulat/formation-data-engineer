# 04 — Déploiements progressifs avec Argo Rollouts (canary & blue/green)

> **Niveau** : avancé · **Prérequis** : [GitOps avec ArgoCD](README.md), [Kubernetes](../../02-Containerisation/Kubernetes/) (Deployments, Services, Probes), [Monitoring Prometheus](../02-Monitoring/).
> **Objectif** : remplacer le `RollingUpdate` « aveugle » par un déploiement **canary** ou **blue/green**
> qui **mesure les métriques** et **annule automatiquement** (rollback) si la nouvelle version dégrade le service.

---

## 1. 🧠 Pourquoi le `RollingUpdate` ne suffit pas

Le `Deployment` standard fait un **RollingUpdate** : il remplace les vieux Pods par les nouveaux, un
par un. Problème : **il ne regarde aucune métrique**. Si la v2 renvoie 30 % d'erreurs 500, Kubernetes
continue quand même à dérouler — il voit juste des Pods « Running ». Tu découvres la panne… par les
plaintes des utilisateurs.

> **Analogie** — Le RollingUpdate, c'est verser toute la nouvelle sauce dans le plat sans goûter. Le
> **canary**, c'est en faire goûter une cuillère à quelques clients, **vérifier qu'ils ne grimacent
> pas**, puis servir tout le monde. Sinon, on jette la cuillère (rollback) — pas le plat entier.

**Argo Rollouts** (de la famille Argo, comme ArgoCD) introduit une ressource **`Rollout`** qui
remplace le `Deployment` et sait faire du **canary** et du **blue/green** avec **analyse automatique**.

---

## 2. ⚙️ Installation

```bash
# Le contrôleur dans le cluster
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# Le plugin kubectl (visualiser et piloter les rollouts)
# macOS : brew install argoproj/tap/kubectl-argo-rollouts
kubectl argo rollouts version
```

---

## 3. 🐤 Stratégie canary

Un `Rollout` ressemble à un `Deployment`, mais avec une `strategy.canary` qui décrit une **montée
progressive** entrecoupée de **pauses** (manuelles ou minutées) :

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: boutique-api
spec:
  replicas: 5
  selector: { matchLabels: { app: boutique-api } }
  template:                      # identique au template d'un Deployment
    metadata: { labels: { app: boutique-api } }
    spec:
      containers:
      - name: api
        image: mon-org/boutique-api:1.5.0
        ports: [ { containerPort: 8000 } ]
        readinessProbe:
          httpGet: { path: /readyz, port: 8000 }
  strategy:
    canary:
      steps:
      - setWeight: 20            # 20 % du trafic vers la v2
      - pause: { duration: 2m }  # observe 2 min
      - setWeight: 50
      - pause: {}                # pause INFINIE → validation manuelle (promote)
      - setWeight: 80
      - pause: { duration: 2m }
      # puis 100 % automatiquement
```

Piloter le déploiement :

```bash
kubectl argo rollouts get rollout boutique-api --watch   # vue en direct des étapes
kubectl argo rollouts promote boutique-api               # franchir une pause manuelle
kubectl argo rollouts abort boutique-api                 # tout annuler → retour v1
kubectl argo rollouts undo boutique-api                  # rollback vers la révision précédente
```

---

## 4. 🔵🟢 Stratégie blue/green

Deux versions coexistent : **blue** (active, sert le trafic) et **green** (nouvelle, testable en
privé). On bascule le trafic **d'un coup** une fois la green validée — rollback = re-bascule instantanée.

```yaml
  strategy:
    blueGreen:
      activeService: boutique-active      # Service qui reçoit le trafic public
      previewService: boutique-preview    # Service privé pour tester la green
      autoPromotionEnabled: false         # bascule MANUELLE après validation
      prePromotionAnalysis:               # (voir §5) valider AVANT de basculer
        templates: [ { templateName: taux-succes } ]
```

> **Blue/green vs canary** — *blue/green* bascule 0 %→100 % d'un coup (rollback instantané, mais double
> l'infra le temps du switch) ; *canary* monte progressivement (moins de ressources, exposition
> graduelle du risque). Canary pour une API à fort trafic ; blue/green quand on veut un switch net.

---

## 5. 📊 Analyse automatique & rollback (le vrai « niveau prod »)

C'est **ici** que le progressif prend tout son sens : une `AnalysisTemplate` interroge **Prometheus**
et **annule le rollout** si une métrique décroche.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: taux-succes }
spec:
  metrics:
  - name: success-rate
    interval: 30s
    count: 5
    successCondition: result[0] >= 0.95     # ≥ 95 % de succès requis
    failureLimit: 2                          # 2 échecs → abort automatique
    provider:
      prometheus:
        address: http://prometheus.monitoring:9090
        query: |
          sum(rate(http_requests_total{app="boutique-api",code!~"5.."}[2m]))
          /
          sum(rate(http_requests_total{app="boutique-api"}[2m]))
```

On la branche dans les steps du canary :

```yaml
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: { duration: 1m }
      - analysis:                      # ← mesure automatique
          templates: [ { templateName: taux-succes } ]
      - setWeight: 60
      - analysis:
          templates: [ { templateName: taux-succes } ]
```

Résultat : si la v2 fait chuter le taux de succès sous 95 %, Argo Rollouts **stoppe et revient en v1
tout seul** — sans réveiller personne à 3 h du matin.

---

## 6. 🔗 Le lien avec GitOps

Un `Rollout` est un manifest YAML **comme un autre** : on le versionne dans le dépôt de manifests, et
**ArgoCD** le déploie (chapitre précédent). Déployer la v2 = changer le tag d'image **dans Git** →
ArgoCD synchronise le `Rollout` → Argo Rollouts déroule le canary **avec analyse**. GitOps répond au
*« quel état désiré ? »*, Argo Rollouts au *« comment y arriver sans casser ? »*.

## 7. 🧪 Lab

1. Installe Argo Rollouts + le plugin kubectl.
2. Déploie le `Rollout` canary ci-dessus (image `:1.5.0`) et les Services associés.
3. Pousse une « v2 » cassée (`image: …:broken`) : `kubectl argo rollouts set image boutique-api api=mon-org/boutique-api:broken`.
4. Observe `kubectl argo rollouts get rollout boutique-api --watch` : la readiness échoue, le canary **ne progresse pas**.
5. `abort` puis corrige. Rejoue avec une bonne image et `promote` étape par étape.

## ✅ Checklist de validation

- [ ] Contrôleur Argo Rollouts installé + plugin `kubectl argo rollouts` fonctionnel
- [ ] Un `Rollout` canary déployé, montée progressive visible dans `get rollout --watch`
- [ ] Une pause manuelle franchie avec `promote`
- [ ] Une version fautive **bloquée** (readiness/analyse) puis **abort/undo** démontré
- [ ] (Bonus) `AnalysisTemplate` Prometheus qui provoque un **rollback automatique**

## 🔗 Ressources

- Argo Rollouts : https://argoproj.github.io/rollouts/
- Analyse & métriques : https://argo-rollouts.readthedocs.io/en/stable/features/analysis/
- Stratégies canary/blueGreen : https://argo-rollouts.readthedocs.io/en/stable/concepts/

---

[← GitOps avec ArgoCD](README.md) | [🏠 DevOps](../README.md)
