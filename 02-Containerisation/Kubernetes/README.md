# Formation Kubernetes : De Zéro à Expert pour Data Engineers

Bienvenue dans cette formation complète sur Kubernetes (K8s). L'orchestration de conteneurs est devenue le standard pour déployer des applications scalables, résilientes et portables dans le cloud.

## 🎯 Objectifs Pédagogiques

- Comprendre les concepts fondamentaux de l'orchestration.
- Maîtriser l'architecture de Kubernetes (Control Plane vs Worker Nodes).
- Apprendre à déployer et scaler des applications via les Pods et Deployments.
- Gérer le networking, la configuration et le stockage persistant.
- Mettre en production sur un service managé comme Azure Kubernetes Service (AKS).

## 📚 Programme de la Formation

### [01 - Introduction et Concepts](01-introduction-concepts.md)
Découvrez Kubernetes, ses avantages et la différence avec Docker.

### [02 - Architecture de Kubernetes](02-architecture-k8s.md)
Explorez les composants internes du cluster (Control Plane, Nodes, etcd).

### [03 - Installation et Premiers Pas](03-installation-minikube.md)
Installez Minikube et kubectl pour lancer votre première application localement.

### [04 - Pods et Deployments](04-pods-deployments.md)
Maîtrisez les unités de base et les stratégies de déploiement (RollingUpdate).

### [05 - Services et Networking](05-services-networking.md)
Exposez vos applications via ClusterIP, NodePort et LoadBalancer.

### [06 - ConfigMaps et Secrets](06-configmaps-secrets.md)
Gérez la configuration et les données sensibles de manière sécurisée.

### [07 - Volumes et Persistance](07-volumes-persistence.md)
Comprendre le stockage avec les PV, PVC et StorageClasses.

### [08 - Ingress et Exposition Externe](08-ingress-exposition.md)
Configurez le routage HTTP/HTTPS avancé et le SSL/TLS.

### [09 - Déploiement sur Azure (AKS)](09-azure-aks.md)
Mise en situation réelle sur Azure Kubernetes Service.

### [10 - Sondes de santé (Probes)](10-probes-sante.md)
Fiabilisez vos Pods : liveness, readiness et startup probes.

### [11 - Autoscaling (HPA)](11-autoscaling-hpa.md)
Ajustez automatiquement le nombre de Pods selon la charge (CPU, métriques métier).

### [12 - RBAC & sécurité](12-rbac-securite.md)
Contrôlez qui peut faire quoi (ServiceAccounts, Roles, moindre privilège).

### [13 - Helm](13-helm.md)
Empaquetez et déployez vos applications avec le gestionnaire de paquets de Kubernetes.

> 🚀 **Suite production** : déploiements progressifs (canary / blue-green) avec
> [Argo Rollouts](../../07-DevOps/03-GitOps/04-argo-rollouts-canary-bluegreen.md).

---
**Academy** - Formation Data Engineer
