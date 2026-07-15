# 12 - RBAC & sécurité

[← 11 - Autoscaling](11-autoscaling-hpa.md) | [🏠 Accueil](README.md) | [13 - Helm →](13-helm.md)

---

## 12. Contrôler qui peut faire quoi

En production, **tout le monde ne doit pas pouvoir tout faire** sur le cluster. Le **RBAC**
(*Role-Based Access Control*) répond à trois questions : **qui** (identité) peut faire **quoi** (verbe)
sur **quelles ressources** ?

> **Analogie** — Un immeuble avec des **badges**. Un badge n'ouvre que certaines portes (ressources)
> pour certaines actions (entrer / juste regarder). Un stagiaire n'a pas le badge de la salle des
> serveurs. Le RBAC, c'est le système de badges de Kubernetes.

### Les 4 briques

| Objet | Rôle |
|---|---|
| **ServiceAccount** | l'**identité** d'un Pod (ou d'un humain/robot) |
| **Role** | un ensemble de permissions **dans un namespace** |
| **ClusterRole** | un ensemble de permissions **sur tout le cluster** |
| **RoleBinding** / **ClusterRoleBinding** | **attribue** un (Cluster)Role à une identité |

Le principe directeur : **le moindre privilège** (*least privilege*) — on n'accorde que le strict
nécessaire.

### Exemple — un pipeline de données en lecture seule

Un Pod qui lit des ConfigMaps et liste des Pods, **sans rien pouvoir modifier**.

```yaml
# 1) Une identité pour le pipeline
apiVersion: v1
kind: ServiceAccount
metadata: { name: pipeline-data, namespace: data }
---
# 2) Un rôle : lecture seule sur pods et configmaps (dans le namespace "data")
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: lecteur, namespace: data }
rules:
- apiGroups: [""]                       # "" = le groupe core
  resources: ["pods", "configmaps"]
  verbs: ["get", "list", "watch"]       # AUCUN create/update/delete
---
# 3) On attribue le rôle à l'identité
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: pipeline-lecteur, namespace: data }
subjects:
- kind: ServiceAccount
  name: pipeline-data
  namespace: data
roleRef:
  kind: Role
  name: lecteur
  apiGroup: rbac.authorization.k8s.io
```

On rattache ensuite l'identité au Pod :

```yaml
spec:
  serviceAccountName: pipeline-data     # le Pod hérite des permissions du SA
```

### Vérifier les permissions (indispensable)

```bash
# Est-ce que ce ServiceAccount peut supprimer des pods ? (doit répondre "no")
kubectl auth can-i delete pods \
  --as=system:serviceaccount:data:pipeline-data -n data

# Lister ce qu'une identité peut faire
kubectl auth can-i --list --as=system:serviceaccount:data:pipeline-data -n data
```

> 🛑 **Erreur courante** — donner le ClusterRole `cluster-admin` « pour que ça marche ». C'est la
> faille n°1 : un Pod compromis = cluster compromis. Commence **fermé**, ouvre au besoin (`auth can-i`
> pour trouver la permission exacte manquante).

> 💡 **Namespaced vs Cluster** — utilise un **Role** (namespacé) par défaut. Le **ClusterRole** ne sert
> que pour les ressources non-namespacées (nodes, PersistentVolumes) ou une permission transverse.

## ✅ À retenir

- Le RBAC répond à **qui / quoi / sur quelles ressources**.
- **ServiceAccount** = identité ; **Role/ClusterRole** = permissions ; **(Cluster)RoleBinding** = attribution.
- Applique le **moindre privilège** ; vérifie avec `kubectl auth can-i`.
- Jamais de `cluster-admin` par confort.

[← 11 - Autoscaling](11-autoscaling-hpa.md) | [🏠 Accueil](README.md) | [13 - Helm →](13-helm.md)
