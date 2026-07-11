# 02 — Fetch API : Requêtes HTTP, JSON, Headers, Gestion d'Erreurs

## Introduction

La Fetch API est l'interface native du navigateur pour effectuer des requêtes HTTP. Elle remplace l'ancienne `XMLHttpRequest` avec une syntaxe basée sur les Promises, beaucoup plus élégante.

---

## 1. Première requête avec fetch()

```javascript
// fetch() retourne une Promise qui se résout avec un objet Response
fetch("https://jsonplaceholder.typicode.com/users/1")
  .then(response => {
    console.log(response);           // Response { status: 200, ok: true, ... }
    console.log(response.status);    // 200
    console.log(response.ok);        // true (status entre 200 et 299)
    console.log(response.statusText); // "OK"
    console.log(response.headers.get("content-type")); // "application/json; charset=utf-8"

    // IMPORTANT : le corps de la réponse doit être lu séparément
    return response.json(); // Retourne une Promise qui parse le JSON
  })
  .then(utilisateur => {
    console.log(utilisateur.name);  // "Leanne Graham"
    console.log(utilisateur);
  })
  .catch(erreur => {
    console.error("Erreur réseau:", erreur);
  });
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de DevTools — exécuter un fetch() dans la console, puis dans l'onglet Network montrer la requête apparaître en temps réel : URL, méthode, status, headers request/response, body de la réponse
> **Expliquer :** L'onglet Network est l'outil indispensable pour déboguer les appels API. On peut voir exactement ce qui est envoyé et reçu, les temps de réponse, et rejouer les requêtes.

---

## 2. Piège important : fetch() ne rejette pas sur les erreurs HTTP

```javascript
// ⚠️ fetch() résout la Promise même pour les codes d'erreur (404, 500, etc.)
// Il rejette UNIQUEMENT en cas d'erreur réseau (pas de connexion, etc.)

fetch("https://jsonplaceholder.typicode.com/users/999999")
  .then(response => {
    console.log(response.status); // 404
    console.log(response.ok);     // false — mais la Promise est RÉSOLUE, pas rejetée !

    // Il faut vérifier response.ok manuellement
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
    }
    return response.json();
  })
  .catch(erreur => {
    console.error(erreur.message); // "Erreur HTTP: 404 Not Found"
  });

// ✅ Pattern robuste pour fetch
async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const erreurTexte = await response.text(); // Lire le message d'erreur du serveur
    throw new Error(`HTTP ${response.status}: ${erreurTexte}`);
  }

  // Vérifier si la réponse contient du JSON
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

// Utilisation
async function chargerUtilisateur(id) {
  try {
    const user = await fetchJSON(`https://jsonplaceholder.typicode.com/users/${id}`);
    console.log(user.name);
  } catch (erreur) {
    console.error("Impossible de charger l'utilisateur:", erreur.message);
  }
}
```

---

## 3. Méthodes HTTP : GET, POST, PUT, DELETE

### GET (défaut)

```javascript
// Requête GET simple
const utilisateurs = await fetchJSON("https://jsonplaceholder.typicode.com/users");
console.log(utilisateurs.length); // 10

// GET avec paramètres de query string
const params = new URLSearchParams({
  page: 1,
  limite: 10,
  recherche: "alice",
  actif: true,
});

const url = `https://api.example.com/utilisateurs?${params}`;
console.log(url); // "https://api.example.com/utilisateurs?page=1&limite=10&recherche=alice&actif=true"

const resultats = await fetchJSON(url);
```

### POST — Créer une ressource

```javascript
async function creerPost(titre, corps, userId) {
  const response = await fetch("https://jsonplaceholder.typicode.com/posts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",  // Obligatoire pour envoyer du JSON
      "Accept": "application/json",
    },
    body: JSON.stringify({
      title: titre,
      body: corps,
      userId,
    }),
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  const nouveauPost = await response.json();
  console.log("Créé:", nouveauPost); // { id: 101, title: "...", body: "...", userId: 1 }
  return nouveauPost;
}

await creerPost("Mon titre", "Contenu du post", 1);
```

### PUT et PATCH — Mettre à jour

```javascript
// PUT — Remplace TOUTE la ressource
async function remplacerPost(id, donnees) {
  const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(donnees),
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

// PATCH — Met à jour PARTIELLEMENT la ressource
async function mettreAJourPost(id, modifications) {
  const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(modifications), // Seulement les champs à modifier
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

await mettreAJourPost(1, { title: "Nouveau titre" }); // Seul le titre change
```

### DELETE — Supprimer

```javascript
async function supprimerPost(id) {
  const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  // DELETE retourne souvent un body vide (204 No Content)
  console.log(`Post ${id} supprimé avec succès`);
  return true;
}

await supprimerPost(1);
```

---

## 4. Headers HTTP

```javascript
// En-têtes de requête courants
const headersCommuns = new Headers({
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": "Bearer mon-token-jwt",
  "X-Request-ID": crypto.randomUUID(),
  "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
});

// Lire les headers de réponse
const response = await fetch("/api/data");
console.log(response.headers.get("Content-Type"));
console.log(response.headers.get("X-Rate-Limit-Remaining"));
console.log(response.headers.get("Cache-Control"));

// Itérer sur tous les headers de réponse
for (const [nom, valeur] of response.headers) {
  console.log(`${nom}: ${valeur}`);
}

// Authentification par token
async function fetchAuthentifie(url, options = {}) {
  const token = localStorage.getItem("auth_token"); // Ou depuis un store

  return fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { "Authorization": `Bearer ${token}` }),
      ...options.headers, // Permet de surcharger
    },
  });
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans l'onglet Network de DevTools, cliquer sur une requête et montrer les onglets "Headers" (request headers et response headers), "Preview" (JSON formaté), "Response" (JSON brut), "Timing" (durée de chaque phase)
> **Expliquer :** Le header `Authorization: Bearer ...` est le mécanisme standard d'authentification JWT. Le header `Content-Type: application/json` est obligatoire pour que le serveur sache comment parser le body.

---

## 5. Envoyer différents types de données

### FormData — Formulaires et upload de fichiers

```javascript
// Envoyer des données de formulaire
const formulaire = document.querySelector("#mon-formulaire");
const formData = new FormData(formulaire); // Capture automatiquement tous les champs

// Ajouter des champs manuellement
formData.append("categorie", "profil");
formData.append("timestamp", Date.now());

const response = await fetch("/api/upload", {
  method: "POST",
  body: formData,
  // NE PAS ajouter Content-Type — le navigateur le fait automatiquement
  // avec le bon boundary pour multipart/form-data
});

// Upload de fichier
const inputFichier = document.querySelector("input[type='file']");
inputFichier.addEventListener("change", async (event) => {
  const fichier = event.target.files[0];
  if (!fichier) return;

  const formData = new FormData();
  formData.append("fichier", fichier, fichier.name);
  formData.append("userId", "123");

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const resultat = await response.json();
    console.log("Upload réussi:", resultat.url);
  } catch (erreur) {
    console.error("Erreur upload:", erreur.message);
  }
});

// Upload avec progression
async function uploadAvecProgression(fichier, onProgression) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest(); // fetch() ne supporte pas les événements de progression
    const formData = new FormData();
    formData.append("fichier", fichier);

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        const pourcentage = Math.round((event.loaded / event.total) * 100);
        onProgression(pourcentage);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`HTTP ${xhr.status}`));
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Erreur réseau")));

    xhr.open("POST", "/api/upload");
    xhr.send(formData);
  });
}
```

---

## 6. Gestion robuste des erreurs

```javascript
// Classes d'erreurs personnalisées pour fetch
class ErreurHTTP extends Error {
  constructor(status, statusText, url) {
    super(`HTTP ${status} ${statusText} — ${url}`);
    this.name = "ErreurHTTP";
    this.status = status;
    this.statusText = statusText;
    this.url = url;
  }
}

class ErreurReseau extends Error {
  constructor(url, cause) {
    super(`Erreur réseau pour ${url}`);
    this.name = "ErreurReseau";
    this.url = url;
    this.cause = cause;
  }
}

// Client HTTP complet
class HTTPClient {
  #baseUrl;
  #defaultHeaders;
  #tokenGetter;

  constructor(baseUrl, options = {}) {
    this.#baseUrl = baseUrl;
    this.#defaultHeaders = options.headers || {};
    this.#tokenGetter = options.tokenGetter || (() => null);
  }

  async #request(endpoint, options = {}) {
    const url = `${this.#baseUrl}${endpoint}`;
    const token = this.#tokenGetter();

    const config = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        ...this.#defaultHeaders,
        ...(token && { "Authorization": `Bearer ${token}` }),
        ...options.headers,
      },
    };

    if (options.body && typeof options.body === "object") {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const erreurBody = await response.text().catch(() => "");
        throw new ErreurHTTP(response.status, response.statusText, url);
      }

      // Réponse vide (204 No Content)
      if (response.status === 204) return null;

      return response.json();
    } catch (erreur) {
      if (erreur instanceof ErreurHTTP) throw erreur;
      throw new ErreurReseau(url, erreur);
    }
  }

  get(endpoint, params = {}) {
    const queryString = Object.keys(params).length
      ? "?" + new URLSearchParams(params)
      : "";
    return this.#request(`${endpoint}${queryString}`);
  }

  post(endpoint, body) {
    return this.#request(endpoint, { method: "POST", body });
  }

  put(endpoint, body) {
    return this.#request(endpoint, { method: "PUT", body });
  }

  patch(endpoint, body) {
    return this.#request(endpoint, { method: "PATCH", body });
  }

  delete(endpoint) {
    return this.#request(endpoint, { method: "DELETE" });
  }
}

// Utilisation
const api = new HTTPClient("https://api.example.com", {
  tokenGetter: () => localStorage.getItem("token"),
});

async function exempleUtilisation() {
  try {
    const users = await api.get("/users", { page: 1, limit: 20 });
    const newUser = await api.post("/users", { nom: "Alice", email: "alice@ex.com" });
    await api.patch(`/users/${newUser.id}`, { age: 31 });
    await api.delete(`/users/${newUser.id}`);
  } catch (erreur) {
    if (erreur instanceof ErreurHTTP) {
      if (erreur.status === 401) {
        // Rediriger vers la connexion
        window.location.href = "/login";
      } else if (erreur.status === 403) {
        alert("Accès refusé");
      } else if (erreur.status === 404) {
        console.log("Ressource non trouvée");
      } else {
        console.error("Erreur serveur:", erreur.message);
      }
    } else if (erreur instanceof ErreurReseau) {
      alert("Impossible de contacter le serveur. Vérifiez votre connexion.");
    }
  }
}
```

---

## 7. Patterns avancés

### Cache manuel

```javascript
const cache = new Map();

async function fetchAvecCache(url, ttlMs = 60000) {
  const maintenant = Date.now();
  const entreeCache = cache.get(url);

  if (entreeCache && maintenant - entreeCache.timestamp < ttlMs) {
    console.log(`Cache HIT: ${url}`);
    return entreeCache.donnees;
  }

  console.log(`Cache MISS: ${url}`);
  const donnees = await fetchJSON(url);
  cache.set(url, { donnees, timestamp: maintenant });
  return donnees;
}

// Requêtes parallèles avec gestion d'erreurs individuelles
async function chargerTableauDeBord() {
  const [users, posts, comments] = await Promise.allSettled([
    fetchJSON("/api/users"),
    fetchJSON("/api/posts"),
    fetchJSON("/api/comments"),
  ]);

  return {
    users: users.status === "fulfilled" ? users.value : [],
    posts: posts.status === "fulfilled" ? posts.value : [],
    comments: comments.status === "fulfilled" ? comments.value : [],
    erreurs: [users, posts, comments]
      .filter(r => r.status === "rejected")
      .map(r => r.reason.message),
  };
}
```

### Server-Sent Events (SSE) — temps réel sans WebSocket

```javascript
// Réception de données en continu du serveur
const source = new EventSource("/api/notifications");

source.addEventListener("message", (event) => {
  const notification = JSON.parse(event.data);
  console.log("Nouvelle notification:", notification);
});

source.addEventListener("error", (event) => {
  console.error("Erreur SSE:", event);
  // Le navigateur tente de se reconnecter automatiquement
});

// Fermer la connexion
source.close();
```

---

## Récapitulatif

| Tâche | Code |
|---|---|
| GET simple | `fetch(url).then(r => r.json())` |
| POST JSON | `fetch(url, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(data) })` |
| Vérifier le statut | `if (!response.ok) throw new Error(...)` |
| Envoyer un formulaire | `fetch(url, { method:"POST", body: new FormData(form) })` |
| Ajouter un token JWT | `headers: { "Authorization": "Bearer " + token }` |
| Paramètres GET | `url + "?" + new URLSearchParams(params)` |
| Annuler une requête | `new AbortController()` + `signal` dans les options |
