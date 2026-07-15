# 10 - Sondes de santé (Probes)

[← 09 - AKS](09-azure-aks.md) | [🏠 Accueil](README.md) | [11 - Autoscaling →](11-autoscaling-hpa.md)

---

## 10. Rendre une application vraiment résiliente

Un conteneur qui **tourne** n'est pas forcément un conteneur qui **marche** : le processus peut être
vivant mais bloqué (deadlock), ou encore en train de démarrer et pas prêt à répondre. Kubernetes ne
le devine pas — il faut le lui **dire** avec des **sondes** (*probes*).

> **Analogie** — Imagine un restaurant. La **liveness probe**, c'est prendre le pouls du cuisinier :
> s'il est évanoui, on le remplace (redémarrage du conteneur). La **readiness probe**, c'est vérifier
> que les portes sont ouvertes et la cuisine prête : sinon, on **n'envoie pas de clients** (on retire
> le Pod du service), mais on ne remplace personne.

### Les 3 sondes

| Sonde | Question posée | Si elle échoue |
|---|---|---|
| **liveness** | « Le conteneur est-il encore vivant ? » | Kubernetes **redémarre** le conteneur |
| **readiness** | « Est-il prêt à recevoir du trafic ? » | Le Pod est **retiré des endpoints** du Service (plus de trafic), sans redémarrage |
| **startup** | « A-t-il fini de démarrer ? » | Protège un démarrage lent : tant qu'elle n'a pas réussi, liveness/readiness sont suspendues |

### Trois façons de sonder

```yaml
# httpGet : appelle une URL (le plus courant pour une API/web)
livenessProbe:
  httpGet: { path: /healthz, port: 8000 }

# exec : lance une commande dans le conteneur (code retour 0 = OK)
readinessProbe:
  exec: { command: ["cat", "/tmp/ready"] }

# tcpSocket : vérifie qu'un port accepte les connexions (utile pour une base)
livenessProbe:
  tcpSocket: { port: 5432 }
```

### Exemple complet — une API de données (FastAPI)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: boutique-api
spec:
  replicas: 3
  selector: { matchLabels: { app: boutique-api } }
  template:
    metadata: { labels: { app: boutique-api } }
    spec:
      containers:
      - name: api
        image: mon-org/boutique-api:1.4.0
        ports: [ { containerPort: 8000 } ]
        # Démarrage lent (chargement d'un modèle, migrations…) : on laisse jusqu'à 30×2s = 60s
        startupProbe:
          httpGet: { path: /healthz, port: 8000 }
          failureThreshold: 30
          periodSeconds: 2
        # Vivant ? Sinon on redémarre
        livenessProbe:
          httpGet: { path: /healthz, port: 8000 }
          periodSeconds: 10
          failureThreshold: 3
        # Prêt à servir ? Sinon on coupe le trafic (ex. la base n'est pas encore joignable)
        readinessProbe:
          httpGet: { path: /readyz, port: 8000 }
          periodSeconds: 5
          failureThreshold: 3
```

Côté application, on expose deux routes distinctes :

```python
# /healthz : le process répond (liveness) — ultra léger, ne teste PAS les dépendances
@app.get("/healthz")
def healthz(): return {"status": "ok"}

# /readyz : les dépendances sont OK (readiness) — teste la base, le cache…
@app.get("/readyz")
def readyz():
    check_database()          # lève une exception si la base est injoignable
    return {"status": "ready"}
```

### Les paramètres qui comptent

- `initialDelaySeconds` : délai avant la 1ʳᵉ sonde (souvent remplacé par une `startupProbe`).
- `periodSeconds` : fréquence de la sonde.
- `timeoutSeconds` : au-delà, la sonde est considérée en échec.
- `failureThreshold` / `successThreshold` : nombre d'échecs/succès consécutifs avant de basculer.

> 🛑 **Erreur courante n°1** — mettre les **dépendances** (base, API tierce) dans la **liveness**. Si la
> base a un hoquet, la liveness échoue → Kubernetes redémarre tous les Pods → tempête de redémarrages
> qui aggrave la panne. Les dépendances vont dans la **readiness**, jamais dans la liveness.

> 🛑 **Erreur courante n°2** — une liveness trop agressive (`periodSeconds` court + `failureThreshold`
> bas) sur une app à démarrage lent → **CrashLoopBackOff**. Solution : une `startupProbe` généreuse.

### Vérifier

```bash
kubectl describe pod <pod>          # section "Liveness/Readiness" + événements
kubectl get pod <pod> -o wide       # READY 1/1 = readiness OK ; RESTARTS élevé = liveness qui tue
```

## ✅ À retenir

- **liveness = redémarrer** ; **readiness = couper le trafic** ; **startup = protéger le démarrage lent**.
- Les **dépendances** (base, cache) se testent en **readiness**, jamais en liveness.
- Sans readiness correcte, un `RollingUpdate` envoie du trafic à des Pods **pas encore prêts** → erreurs 5xx pendant les déploiements.

[← 09 - AKS](09-azure-aks.md) | [🏠 Accueil](README.md) | [11 - Autoscaling →](11-autoscaling-hpa.md)
