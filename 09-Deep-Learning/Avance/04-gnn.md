# 04 — Graph Neural Networks (GNN)

[← 03 — Self-supervised](03-self-supervised.md) | [🏠 Accueil](README.md)

### 🎥 En vidéo
▶️ Cherche « [graph neural networks explained](https://www.youtube.com/results?search_query=graph+neural+networks+explained) ».

## 🎯 Objectifs
- Comprendre pourquoi certaines données sont des **graphes**, pas des tableaux ni des images.
- Saisir l'idée du **passage de messages** entre voisins.

## 🧠 Intuition & analogie

Toutes les données ne sont pas des tableaux (ML classique) ni des grilles de pixels (CNN). Un **réseau
social**, une **molécule**, un **réseau routier** sont des **graphes** : des **nœuds** (personnes,
atomes) reliés par des **arêtes** (amitiés, liaisons). Les **GNN** apprennent sur ces structures.

Le mécanisme central : le **passage de messages**. Chaque nœud **met à jour sa représentation** en
**agrégeant l'information de ses voisins**, plusieurs fois de suite.

> **Analogie** — Une **rumeur dans un village** : chaque personne écoute ses voisins directs, met à
> jour ce qu'elle sait, et répète. Après quelques tours, une information s'est propagée à travers le
> réseau. Un GNN fait « circuler » l'information le long des arêtes : après *k* tours, chaque nœud
> « connaît » son voisinage à distance *k*.

## 📐 Une couche de GNN

```
Pour chaque nœud v :
   messages = agréger( représentations des voisins de v )   # somme / moyenne / max
   h(v) = mise_à_jour( h(v), messages )                     # un petit réseau
# On répète sur K couches → chaque nœud voit K sauts plus loin
```

## 🛠️ À quoi ça sert
- **Chimie / pharma** : prédire les propriétés d'une **molécule** (le graphe des atomes).
- **Réseaux sociaux** : détection de fraude, recommandation (« amis d'amis »).
- **Cartes / logistique** : ETA, routage (Google Maps utilise des GNN).
- Variantes : **GCN** (convolution sur graphe), **GraphSAGE** (grands graphes), **GAT** (attention sur voisins).

## ✅ À retenir
- Un **graphe** = nœuds + arêtes ; c'est la bonne structure pour molécules, réseaux sociaux, cartes.
- Un **GNN** apprend par **passage de messages** : chaque nœud agrège ses **voisins**, en boucle.
- Domaines phares : chimie, fraude, recommandation, logistique.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [GNN expliqué](https://www.youtube.com/results?search_query=graph+neural+networks+explained+message+passing) | EN | EN | Le passage de messages |
| [À quoi servent les GNN](https://www.youtube.com/results?search_query=graph+neural+networks+applications+molecules) | EN | EN | Molécules, réseaux, reco |
