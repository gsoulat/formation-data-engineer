# 04 — Observabilité : alerting, logs & traces

> **Niveau** : intermédiaire → avancé · **Prérequis** : [Monitoring (métriques)](../02-Monitoring/), [Kubernetes](../../02-Containerisation/Kubernetes/) / Docker.
> **Objectif** : compléter les métriques par les **3 piliers de l'observabilité** — routing d'alertes (**Alertmanager**), **logs centralisés** (Loki) et **traces distribuées** (Tempo/OpenTelemetry).

---

## 1. 🧠 Monitoring ≠ Observabilité

Le **monitoring** répond à des questions que tu connais d'avance (« le CPU dépasse-t-il 80 % ? »). L'**observabilité** te permet de répondre à des questions que tu n'avais **pas** anticipées (« pourquoi CETTE requête d'utilisateur a mis 4 s, hier à 14h03 ? »).

Elle repose sur **3 piliers complémentaires** :

| Pilier | Répond à… | Outil type |
|---|---|---|
| **Métriques** | « Y a-t-il un problème ? » (agrégat, tendance) | Prometheus + Grafana ✅ *(module 02)* |
| **Logs** | « Que s'est-il passé exactement ? » (événement) | **Loki** + Promtail |
| **Traces** | « Où, dans la chaîne de services, ça a coincé ? » | **Tempo** + OpenTelemetry |

Le module 02 couvre les **métriques**. Ce module ajoute les **deux autres piliers + l'alerting**, dans la même stack Grafana.

## 2. 🔔 Alerting : de Prometheus à Alertmanager

Le module 02 définit des **règles d'alerte** Prometheus (`alert.rules.yml`). Mais une règle qui passe en `firing` ne prévient personne toute seule : il faut **Alertmanager**, qui reçoit les alertes et gère **routing, regroupement, déduplication, silences et notifications**.

```
Prometheus (évalue les règles) ──► Alertmanager ──► Slack / e-mail / PagerDuty
```

`alertmanager.yml` minimal (regroupement + un receiver Slack) :

```yaml
route:
  receiver: 'equipe-plateforme'
  group_by: ['alertname', 'namespace']   # regroupe les alertes similaires en 1 notif
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [ severity="critical" ]   # les critiques vont ailleurs (astreinte)
      receiver: 'astreinte'

receivers:
  - name: 'equipe-plateforme'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        title: '{{ .CommonLabels.alertname }} ({{ .Status }})'
  - name: 'astreinte'
    # pagerduty_configs / webhook_configs …

inhibit_rules:                            # évite le spam : si un noeud est down,
  - source_matchers: [ alertname="NodeDown" ]   # tais les alertes des pods de ce noeud
    target_matchers: [ severity="warning" ]
    equal: ['node']
```

À brancher dans Prometheus (`prometheus.yml`) :

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

> 💡 **Le geste pro** : une bonne alerte est **actionnable** et **peu bruyante**. `group_by` + `inhibit_rules` + un seuil `for:` (durée avant de déclencher) évitent le « mur d'alertes » que tout le monde finit par ignorer.

## 3. 📜 Logs centralisés avec Loki

Sur 1 serveur, `tail -f` suffit. Sur 20 pods éphémères, il te faut des logs **centralisés et requêtables**. **Loki** (de Grafana) indexe les *labels* (pas le texte entier → léger et pas cher) ; **Promtail** collecte les logs et les pousse.

```
conteneurs/pods → Promtail (collecte + labels) → Loki (stockage) → Grafana (LogQL)
```

Requête **LogQL** (même esprit que PromQL) :

```logql
{namespace="boutique", app="api"} |= "ERROR" | json | status >= 500
```

Ajout à un `docker-compose` de monitoring :

```yaml
  loki:
    image: grafana/loki:3.0.0
    ports: ["3100:3100"]
  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
```

Dans Grafana : ajoute Loki comme **data source** → tu lis métriques ET logs au même endroit.

## 4. 🔗 Traces distribuées avec Tempo & OpenTelemetry

Quand une requête traverse *API → service auth → base → cache*, une métrique dit « c'est lent » mais pas **où**. Une **trace** suit la requête de bout en bout via un **`trace_id`** propagé entre services ; chaque étape est un **span** chronométré.

- **OpenTelemetry (OTel)** : le standard d'instrumentation (SDK pour Python/Node/Java… + collector). On instrumente le code une fois, on exporte vers n'importe quel backend.
- **Tempo** (Grafana) : le backend de stockage des traces, requêté par `trace_id`.

Instrumentation minimale (Python/FastAPI) :

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)   # chaque requête devient une trace exportée vers l'OTel Collector
```

**La vraie valeur = la corrélation.** Avec `trace_id` dans les logs, Grafana relie **métrique → trace → logs** de la même requête : tu passes d'un pic de latence au log d'erreur exact en deux clics.

## 5. 🎯 SLO / SLI / error budget

- **SLI** (indicator) : une mesure de qualité vécue par l'utilisateur (ex. % de requêtes < 300 ms).
- **SLO** (objective) : la cible sur ce SLI (ex. 99,5 % sur 30 jours).
- **Error budget** : `100 % − SLO` (ici 0,5 %). Tant qu'il reste du budget, on livre des features ; s'il est épuisé, on gèle et on fiabilise. C'est ce qui transforme la fiabilité en **décision chiffrée**, pas en ressenti.

## 🧪 Lab

1. Reprends la stack Prometheus/Grafana du [module 02](../02-Monitoring/).
2. Ajoute **Alertmanager** + un receiver (webhook de test ou Slack), déclenche une règle et **reçois la notification**.
3. Ajoute **Loki + Promtail**, branche Loki dans Grafana, retrouve une erreur applicative en LogQL.
4. 🎯 **À toi de jouer** : instrumente une petite API avec OpenTelemetry, exporte vers Tempo, et retrouve une requête lente par son `trace_id`.

## ✅ Checklist de validation

- [ ] Alertmanager reçoit les alertes Prometheus et **notifie** un canal (routing + regroupement)
- [ ] Les logs sont centralisés dans Loki et requêtables en LogQL depuis Grafana
- [ ] Au moins une trace distribuée est visible dans Tempo (via OpenTelemetry)
- [ ] Tu peux corréler métrique ↔ logs ↔ trace d'une même requête
- [ ] Un SLO est défini avec son error budget

## 🔗 Ressources

- Alertmanager : https://prometheus.io/docs/alerting/latest/alertmanager/
- Grafana Loki (logs) : https://grafana.com/docs/loki/latest/
- Grafana Tempo (traces) : https://grafana.com/docs/tempo/latest/
- OpenTelemetry : https://opentelemetry.io/docs/
- Google SRE — SLO : https://sre.google/workbook/implementing-slos/
