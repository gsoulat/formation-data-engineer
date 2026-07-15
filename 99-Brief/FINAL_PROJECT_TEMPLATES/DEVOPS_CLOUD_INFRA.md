# Projet Final — DevOps / Cloud Junior
## Sujet : déployer une application de A à Z (IaC → conteneurs → CI/CD → observabilité)

> Projet de synthèse de fin de parcours. Vous reliez **tout l'écosystème DevOps** sur une seule application : infrastructure as code, conteneurisation, orchestration, pipeline automatisé et supervision.

## 📝 Scénario

Une équipe produit a développé une **API** (idéalement l'API de gestion de stock du parcours Développeur, ou toute application conteneurisable de votre choix). Elle tourne aujourd'hui « sur le portable d'un dev » : déploiement manuel, aucune reproductibilité, aucune visibilité si ça tombe. On vous confie la mission DevOps : **rendre le déploiement entièrement automatisé, reproductible, observable et sûr**.

## 🎯 Objectifs (ce que le projet prouve)

- Provisionner une **infrastructure cloud par le code** (aucune ressource créée à la main).
- **Conteneuriser** l'application et l'**orchestrer** sur Kubernetes.
- Automatiser tout le cycle de vie par un **pipeline CI/CD** multi-environnements.
- **Superviser** l'application en production (métriques, logs, alertes).
- Gérer les **secrets** proprement.

## 🏗️ Architecture attendue

```
Git push ──► CI/CD (GitHub Actions)
                │  build + test + scan
                ▼
        Registry d'images (Docker)
                │
   Terraform ──► Infra cloud (réseau, cluster K8s managé, base)
                │
        Kubernetes (Deployment + Service + Ingress)
         │           │
   probes/HPA    ConfigMaps/Secrets
                │
   Observabilité : Prometheus (métriques) + Grafana (dashboards)
                  + logs centralisés + Alertmanager (alertes)
```

- **IaC** : Terraform (state distant + verrouillage, modules, variables par environnement dev/staging/prod). Provider au choix (Azure/AWS/GCP).
- **Conteneurs** : image Docker optimisée (multi-stage, non-root, HEALTHCHECK).
- **Orchestration** : Kubernetes (Deployment, Service, Ingress, ConfigMap/Secret) avec **liveness/readiness probes**, **resource limits** et **HPA** (autoscaling).
- **CI/CD** : pipeline GitHub Actions — lint, tests, build & push d'image, scan de sécurité (Trivy), déploiement **staging automatique** puis **prod sur approbation**.
- **Observabilité** : Prometheus + Grafana (dashboards), **règles d'alerte + Alertmanager** (routing/notification), et **logs centralisés**.
- **Secrets** : jamais en clair (Secrets K8s + coffre : Key Vault / Vault / External Secrets).

> Prérequis couverts par le parcours : [Terraform](../../03-Infrastructure-as-Code/Terraform/), [Docker](../../02-Containerisation/Docker/), [Kubernetes](../../02-Containerisation/Kubernetes/), [CI/CD](../../07-DevOps/01-CI-CD/), [Monitoring](../../07-DevOps/02-Monitoring/).

## 🧭 Travail demandé (par phases)

**Phase 1 — Cadrage & schéma d'architecture (J1).** Choisissez l'application et le cloud. Dessinez l'architecture cible (du `git push` à la prod supervisée). Quelles ressources cloud ? Quels environnements ? Où vivent les secrets ? Posez un tableau Kanban.

**Phase 2 — Infrastructure as Code (J2-J3).** Écrivez le Terraform qui provisionne le réseau, le **cluster Kubernetes managé** et la base de données, avec **state distant verrouillé** et des variables par environnement. Aucune ressource ne doit être créée manuellement dans la console.

**Phase 3 — Conteneur & orchestration (J4-J5).** Conteneurisez l'application (Dockerfile optimisé). Écrivez les manifests Kubernetes : Deployment (avec probes + limites + HPA), Service, Ingress, ConfigMap/Secret. Déployez sur le cluster et vérifiez l'accès public.

**Phase 4 — Pipeline CI/CD (J6-J7).** Automatisez : à chaque push, le pipeline lint + teste + build + scanne (Trivy) + pousse l'image + déploie en **staging** ; la **prod** se déclenche sur approbation manuelle (`environment`). Gérez les secrets du pipeline proprement.

**Phase 5 — Observabilité & résilience (J8-J9).** Déployez Prometheus + Grafana, exposez les métriques de l'app, construisez un dashboard, définissez des **règles d'alerte** (erreurs, latence, pod down) routées via **Alertmanager**. Centralisez les logs. Testez une panne (tuer un pod) et montrez la récupération automatique.

**Phase 6 — Dossier & démonstration (J10).** Documentez l'architecture, les choix (et leurs alternatives), la procédure de déploiement reproductible, et préparez une démo live (déploiement de bout en bout + déclenchement d'une alerte).

## 📦 Livrables

- **Dépôt GitHub public** : code Terraform, manifests Kubernetes, workflows CI/CD, Dockerfile.
- **Schéma d'architecture** (image) du flux complet.
- **Application déployée** avec une **URL publique** fonctionnelle.
- **Dashboard Grafana** + règles d'alerte, capturés dans le dépôt.
- **README** : architecture, prérequis, procédure de déploiement reproductible, runbook (que faire si X tombe).
- **Tableau Kanban** retraçant l'organisation.

## ✅ Critères de validation

- [ ] L'infrastructure est **entièrement provisionnée par Terraform** (aucune ressource créée à la main), state distant verrouillé.
- [ ] L'application tourne sur **Kubernetes** avec probes, resource limits et autoscaling (HPA).
- [ ] Le **pipeline CI/CD** enchaîne lint → tests → build → scan → déploiement staging → prod sur approbation.
- [ ] Les **secrets** ne sont jamais en clair (ni dans le repo, ni dans les manifests).
- [ ] La **supervision** fonctionne : métriques exposées, dashboard, et **au moins une alerte** qui se déclenche réellement (routée par Alertmanager).
- [ ] Une panne simulée (pod tué) est **récupérée automatiquement** (démontré).
- [ ] Le déploiement est **reproductible** depuis zéro en suivant le README.

## 🔗 Bonus (pour aller vers l'expertise)

- **GitOps** : déploiement pull-based avec **ArgoCD** (l'état du cluster suit le Git).
- **Déploiements progressifs** : canary ou blue/green réellement implémentés (Argo Rollouts).
- **Observabilité 3 piliers** : logs (Loki) + traces (Tempo/OpenTelemetry) en plus des métriques.
- Définir des **SLO/SLI** et un error budget.
