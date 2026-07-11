# FAISS

[FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) est une bibliothèque Python/C++ de Meta pour la recherche efficace de voisins proches dans de grands ensembles de vecteurs.

## Contenu de ce dossier

| Fichier | Description |
|---------|-------------|
| `01-utilisation.md` | Installation, types d'index, ajout de vecteurs, recherche, gestion des métadonnées, intégration LangChain |

## Installation rapide

```bash
pip install faiss-cpu           # Version CPU
pip install faiss-gpu           # Version GPU (nécessite CUDA)
```

## Quand utiliser FAISS ?

- Performance maximale en mémoire vive
- Recherche offline sur de très grands corpus (centaines de millions de vecteurs)
- Équipe ML/recherche qui contrôle finement l'index
- Pas besoin de persistance ou d'API REST
- Budget zéro (100% open source, pas de serveur)

## Ressources

- [Documentation officielle FAISS](https://faiss.ai/)
- [GitHub FAISS](https://github.com/facebookresearch/faiss)
- [LangChain + FAISS](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
