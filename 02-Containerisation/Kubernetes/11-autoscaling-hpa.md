# 11 - Autoscaling (HPA)

[← 10 - Probes](10-probes-sante.md) | [🏠 Accueil](README.md) | [12 - RBAC →](12-rbac-securite.md)

---

## 11. Scaler automatiquement selon la charge

Fixer `replicas: 3` en dur, c'est payer pour 3 Pods même la nuit, et saturer aux heures de pointe.
Le **HorizontalPodAutoscaler (HPA)** ajuste **automatiquement le nombre de replicas** selon une
métrique (CPU, mémoire, ou métrique métier).

> **Analogie** — Un **centre d'appels** qui ouvre des postes quand la file d'attente s'allonge et en
> ferme quand ça se calme. Le HPA fait pareil avec tes Pods : il regarde la « file d'attente »
> (l'usage CPU) et ajuste les effectifs.

### Les 3 niveaux d'autoscaling

| Type | Ce qu'il ajuste | Ressource |
|---|---|---|
| **HPA** (horizontal) | le **nombre de Pods** | `HorizontalPodAutoscaler` |
| **VPA** (vertical) | les **ressources d'un Pod** (CPU/RAM demandés) | `VerticalPodAutoscaler` |
| **Cluster Autoscaler** | le **nombre de nœuds** de la machine | au niveau du cloud (AKS/EKS/GKE) |

Le HPA est le plus utilisé au quotidien.

### Pré-requis indispensables

1. **`metrics-server`** installé (fournit l'usage CPU/mémoire). Sur minikube : `minikube addons enable metrics-server`.
2. Des **`resources.requests`** définis sur le conteneur — le HPA calcule un **pourcentage de la
   requête**. Sans requête, pas de HPA CPU possible.

```yaml
resources:
  requests: { cpu: "250m", memory: "256Mi" }   # référence pour le calcul du %
  limits:   { cpu: "500m", memory: "512Mi" }
```

### Le HPA (API `autoscaling/v2`)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: boutique-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: boutique-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70      # vise 70 % de la requête CPU en moyenne
  behavior:                          # (optionnel) lisser les à-coups
    scaleDown:
      stabilizationWindowSeconds: 300   # attend 5 min avant de réduire (évite le yo-yo)
    scaleUp:
      stabilizationWindowSeconds: 0     # monte immédiatement
```

Traduction : « garde l'usage CPU moyen autour de 70 % ; si ça monte, ajoute des Pods (jusqu'à 10) ;
si ça descend, retire-en (jusqu'à 2 minimum), mais attends 5 min pour éviter les oscillations. »

### En pratique

```bash
# Version rapide en une commande
kubectl autoscale deployment boutique-api --cpu-percent=70 --min=2 --max=10

# Observer
kubectl get hpa
# NAME           REFERENCE             TARGETS   MINPODS   MAXPODS   REPLICAS
# boutique-api   Deployment/...        45%/70%   2         10        3

# Tester la montée en charge (générer du CPU)
kubectl run -it --rm charge --image=busybox -- /bin/sh -c \
  "while true; do wget -q -O- http://boutique-api; done"
kubectl get hpa -w      # regarde REPLICAS grimper
```

> 🛑 **Erreur courante** — créer un HPA sans `resources.requests` : `TARGETS` affiche `<unknown>/70%`
> et rien ne scale. Le HPA a besoin d'une **référence** pour calculer le pourcentage.

> 💡 **Métriques métier** — au-delà du CPU, on peut scaler sur une **métrique custom** (longueur d'une
> file, requêtes/seconde) via `type: Pods`/`External` + Prometheus Adapter. Idéal pour un *worker* qui
> dépile une file de messages.

## ✅ À retenir

- Le **HPA** ajuste le **nombre de Pods** selon une métrique (souvent CPU %).
- Il exige **`metrics-server`** + des **`requests`** définies.
- `behavior.stabilizationWindow` évite l'**effet yo-yo** (scale up/down permanent).
- **VPA** (taille des Pods) et **Cluster Autoscaler** (nœuds) complètent le HPA.

[← 10 - Probes](10-probes-sante.md) | [🏠 Accueil](README.md) | [12 - RBAC →](12-rbac-securite.md)
