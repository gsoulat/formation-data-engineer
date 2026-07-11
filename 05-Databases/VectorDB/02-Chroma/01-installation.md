# Chroma — Installation et démarrage

## Présentation

[Chroma](https://www.trychroma.com/) est une base de données vectorielle **open source** conçue pour être simple à utiliser et parfaite pour le développement local et les prototypes. Elle est écrite en Python/Rust et peut fonctionner entièrement in-memory ou avec persistance sur disque.

**Pourquoi Chroma est populaire :**
- Installation en une commande `pip install chromadb`
- Aucun service externe requis (pas de Docker obligatoire)
- Intégration native avec LangChain et LlamaIndex
- API Python intuitive
- Mode serveur disponible pour les déploiements partagés

---

## 1. Installation

```bash
pip install chromadb
```

Pour les intégrations LangChain :
```bash
pip install langchain langchain-community langchain-chroma openai
```

Vérification :
```python
import chromadb
print(chromadb.__version__)  # ex: 0.5.x
```

---

## 2. Modes de fonctionnement

### 2.1 Mode In-Memory (éphémère)

Les données sont perdues à la fin du programme. Idéal pour les tests et démonstrations.

```python
import chromadb

# Client in-memory
client = chromadb.Client()

# Vérifier que ça fonctionne
print(client.heartbeat())  # timestamp en nanoseconds
```

### 2.2 Mode Persistant (recommandé pour le dev)

Les données sont sauvegardées sur disque et rechargées automatiquement.

```python
import chromadb

# Client persistant — créera un dossier ./chroma_db si inexistant
client = chromadb.PersistentClient(path="./chroma_db")

# Les données survivent aux redémarrages du programme
print(client.heartbeat())
```

### 2.3 Mode Serveur HTTP (pour partager entre processus)

```bash
# Démarrer le serveur Chroma
chroma run --path ./chroma_db --port 8000
```

```python
import chromadb

# Se connecter au serveur
client = chromadb.HttpClient(host="localhost", port=8000)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir un terminal, lancer `chroma run --path ./chroma_db`, montrer le serveur qui démarre sur le port 8000, puis ouvrir un second terminal et se connecter avec `HttpClient` en Python.
> **Expliquer :** "Chroma peut tourner comme un serveur HTTP, ce qui permet à plusieurs processus ou même plusieurs machines de partager la même vector database. Pour du développement solo, on utilise PersistentClient directement sans serveur."

---

## 3. Collections

Une **collection** dans Chroma est l'équivalent d'une table dans PostgreSQL. Elle stocke des vecteurs de même dimension avec leurs métadonnées.

### 3.1 Créer une collection

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

# Créer une collection avec la fonction de distance par défaut (l2)
collection = client.create_collection(
    name="mes_documents",
    metadata={"hnsw:space": "cosine"}  # "l2" (défaut), "cosine", ou "ip" (inner product)
)

print(f"Collection créée : {collection.name}")
print(f"Nombre de documents : {collection.count()}")  # 0
```

### 3.2 Obtenir ou créer une collection (idempotent)

```python
# get_or_create : si la collection existe → la récupère, sinon → la crée
collection = client.get_or_create_collection(
    name="mes_documents",
    metadata={"hnsw:space": "cosine"}
)
```

### 3.3 Lister et supprimer des collections

```python
# Lister toutes les collections
collections = client.list_collections()
for col in collections:
    print(f"- {col.name}")

# Supprimer une collection
client.delete_collection("mes_documents")

# Supprimer et recréer (utile en développement)
client.delete_collection("mes_documents")
collection = client.create_collection("mes_documents", metadata={"hnsw:space": "cosine"})
```
