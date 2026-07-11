# Exercice 02 — Consommer une API Publique avec fetch()

## Objectif

Construire une application qui affiche des données depuis une API publique réelle, en gérant le chargement, les erreurs, la pagination et le filtrage côté client.

**API utilisée :** [https://jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com) (données fictives) et [https://pokeapi.co](https://pokeapi.co) (données Pokémon).

---

## Partie 1 — Explorateur de Posts (JSONPlaceholder)

### Résultat attendu

Une page qui :
1. Charge tous les posts au démarrage
2. Affiche les posts avec auteur, titre et extrait
3. Permet de filtrer par auteur
4. Affiche les détails d'un post avec ses commentaires
5. Gère le chargement (skeleton loader) et les erreurs

---

### Structure du projet

```
exercice-02/
├── index.html
├── style.css
├── src/
│   ├── api.js         ← Service API
│   ├── ui.js          ← Fonctions de rendu
│   └── app.js         ← Logique principale
```

---

### Le service API (`src/api.js`)

```javascript
const BASE_URL = "https://jsonplaceholder.typicode.com";

// Fonction utilitaire
async function get(endpoint) {
  const response = await fetch(`${BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

// API
export const api = {
  // Récupérer tous les posts
  getPosts() {
    return get("/posts");
  },

  // Récupérer un post spécifique
  getPost(id) {
    return get(`/posts/${id}`);
  },

  // Récupérer les commentaires d'un post
  getCommentaires(postId) {
    return get(`/posts/${postId}/comments`);
  },

  // Récupérer tous les utilisateurs
  getUtilisateurs() {
    return get("/users");
  },

  // Récupérer un utilisateur
  getUtilisateur(id) {
    return get(`/users/${id}`);
  },

  // Charger un post + ses commentaires en parallèle
  async getPostAvecCommentaires(postId) {
    const [post, commentaires] = await Promise.all([
      get(`/posts/${postId}`),
      get(`/posts/${postId}/comments`),
    ]);
    return { post, commentaires };
  },

  // Charger les posts + les utilisateurs en parallèle
  async getPostsAvecAuteurs() {
    const [posts, utilisateurs] = await Promise.all([
      get("/posts"),
      get("/users"),
    ]);

    // Joindre les données
    const mapUtilisateurs = new Map(utilisateurs.map(u => [u.id, u]));

    return posts.map(post => ({
      ...post,
      auteur: mapUtilisateurs.get(post.userId),
    }));
  },
};
```

---

### La gestion de l'UI (`src/ui.js`)

```javascript
// Créer un skeleton loader
export function creerSkeleton(nombre = 6) {
  return Array.from({ length: nombre }, () => `
    <article class="post-card skeleton">
      <div class="skeleton-line skeleton-titre"></div>
      <div class="skeleton-line skeleton-texte"></div>
      <div class="skeleton-line skeleton-texte court"></div>
      <div class="skeleton-line skeleton-auteur"></div>
    </article>
  `).join("");
}

// Rendre un post sous forme de carte
export function renduCarte(post) {
  const extrait = post.body.length > 100
    ? post.body.substring(0, 100) + "..."
    : post.body;

  return `
    <article class="post-card" data-post-id="${post.id}" tabindex="0" role="button">
      <div class="post-meta">
        <span class="post-auteur">${post.auteur?.name ?? "Auteur inconnu"}</span>
        <span class="post-badge">Post #${post.id}</span>
      </div>
      <h2 class="post-titre">${post.title}</h2>
      <p class="post-extrait">${extrait}</p>
      <div class="post-actions">
        <button class="btn-lire-plus" data-post-id="${post.id}">
          Lire la suite →
        </button>
      </div>
    </article>
  `;
}

// Rendre une modal avec le détail du post
export function renduModalPost({ post, commentaires }) {
  const commentsHTML = commentaires.map(c => `
    <div class="commentaire">
      <div class="commentaire-header">
        <strong>${c.name}</strong>
        <a href="mailto:${c.email}" class="commentaire-email">${c.email}</a>
      </div>
      <p>${c.body}</p>
    </div>
  `).join("");

  return `
    <div class="modal-overlay" id="modal">
      <div class="modal-contenu" role="dialog" aria-modal="true">
        <button class="modal-fermer" id="fermer-modal" aria-label="Fermer">×</button>

        <div class="modal-post">
          <span class="post-badge">Post #${post.id}</span>
          <h2>${post.title}</h2>
          <p class="post-body">${post.body}</p>
        </div>

        <div class="modal-commentaires">
          <h3>💬 Commentaires (${commentaires.length})</h3>
          ${commentaires.length > 0 ? commentsHTML : "<p>Aucun commentaire</p>"}
        </div>
      </div>
    </div>
  `;
}

// Afficher un message d'erreur
export function renduErreur(message) {
  return `
    <div class="erreur-bloc">
      <span class="erreur-icone">⚠️</span>
      <p class="erreur-message">${message}</p>
      <button class="btn btn-primary" onclick="window.location.reload()">
        Réessayer
      </button>
    </div>
  `;
}

// Créer un sélecteur d'auteurs
export function renduFiltreAuteurs(auteurs) {
  const options = auteurs
    .map(a => `<option value="${a.id}">${a.name}</option>`)
    .join("");

  return `
    <select id="filtre-auteur" class="filtre-select">
      <option value="">Tous les auteurs</option>
      ${options}
    </select>
  `;
}
```

---

### La logique principale (`src/app.js`)

```javascript
import { api } from "./api.js";
import { creerSkeleton, renduCarte, renduModalPost, renduErreur, renduFiltreAuteurs } from "./ui.js";

class App {
  #posts = [];
  #postsFiltres = [];
  #conteneur;
  #barreRecherche;

  constructor() {
    this.#conteneur = document.querySelector("#grille-posts");
    this.#barreRecherche = document.querySelector("#recherche");
    this.#initialiser();
  }

  async #initialiser() {
    this.#afficherChargement();

    try {
      // Charger les données
      const posts = await api.getPostsAvecAuteurs();
      this.#posts = posts;
      this.#postsFiltres = posts;

      // Extraire les auteurs uniques pour le filtre
      const auteurs = [...new Map(
        posts.map(p => [p.userId, p.auteur])
      ).values()].filter(Boolean);

      // Rendre le filtre
      document.querySelector("#conteneur-filtre").innerHTML =
        renduFiltreAuteurs(auteurs);

      // Attacher les événements du filtre
      this.#attacherEvenements();

      // Afficher les posts
      this.#afficherPosts();

    } catch (erreur) {
      this.#conteneur.innerHTML = renduErreur(erreur.message);
      console.error("Erreur de chargement:", erreur);
    }
  }

  #attacherEvenements() {
    // Recherche textuelle
    this.#barreRecherche?.addEventListener("input", (e) => {
      this.#filtrer(e.target.value, document.querySelector("#filtre-auteur")?.value);
    });

    // Filtre par auteur
    document.querySelector("#filtre-auteur")?.addEventListener("change", (e) => {
      this.#filtrer(this.#barreRecherche?.value ?? "", e.target.value);
    });

    // Délégation pour ouvrir les posts
    this.#conteneur.addEventListener("click", (e) => {
      const btnLire = e.target.closest(".btn-lire-plus");
      const carte = e.target.closest(".post-card");

      const postId = (btnLire ?? carte)?.dataset?.postId;
      if (postId) this.#ouvrirPost(Number(postId));
    });

    // Fermer la modal avec Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.#fermerModal();
    });
  }

  #filtrer(recherche, auteurId) {
    const rechercheMin = recherche.toLowerCase().trim();

    this.#postsFiltres = this.#posts.filter(post => {
      const correspondRecherche = !rechercheMin || [
        post.title,
        post.body,
        post.auteur?.name ?? "",
      ].some(texte => texte.toLowerCase().includes(rechercheMin));

      const correspondAuteur = !auteurId || post.userId === Number(auteurId);

      return correspondRecherche && correspondAuteur;
    });

    this.#afficherPosts();
  }

  #afficherPosts() {
    if (this.#postsFiltres.length === 0) {
      this.#conteneur.innerHTML = `
        <div class="message-vide">
          <p>Aucun post ne correspond à votre recherche</p>
        </div>
      `;
      return;
    }

    this.#conteneur.innerHTML = this.#postsFiltres.map(renduCarte).join("");

    // Mettre à jour le compteur
    document.querySelector("#compteur-posts").textContent =
      `${this.#postsFiltres.length} post${this.#postsFiltres.length > 1 ? "s" : ""}`;
  }

  async #ouvrirPost(postId) {
    // Afficher la modal avec un loader
    document.body.insertAdjacentHTML("beforeend", `
      <div class="modal-overlay" id="modal">
        <div class="modal-contenu">
          <div class="modal-loading">Chargement...</div>
        </div>
      </div>
    `);

    document.querySelector("#modal")?.addEventListener("click", (e) => {
      if (e.target.id === "modal") this.#fermerModal();
    });

    try {
      const donnees = await api.getPostAvecCommentaires(postId);
      const modal = document.querySelector("#modal");
      if (modal) {
        modal.outerHTML = renduModalPost(donnees);
        // Re-attacher le bouton fermer
        document.querySelector("#fermer-modal")?.addEventListener("click", () => {
          this.#fermerModal();
        });
        document.querySelector("#modal")?.addEventListener("click", (e) => {
          if (e.target.id === "modal") this.#fermerModal();
        });
      }
    } catch (erreur) {
      this.#fermerModal();
      alert(`Impossible de charger le post: ${erreur.message}`);
    }
  }

  #fermerModal() {
    document.querySelector("#modal")?.remove();
  }

  #afficherChargement() {
    this.#conteneur.innerHTML = creerSkeleton(9);
  }
}

document.addEventListener("DOMContentLoaded", () => new App());
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de DevTools pendant le chargement de l'app — montrer les deux requêtes GET (posts + users) partir en parallèle au même moment dans la timeline, puis la requête POST lorsqu'on ouvre un post
> **Expliquer :** Promise.all() déclenche les deux requêtes simultanément. On peut clairement voir dans l'onglet Network que les deux requêtes partent au même moment (même heure dans la colonne "Waterfall"). C'est pourquoi le chargement est deux fois plus rapide.

---

## Partie 2 — Pokédex (PokeAPI)

### Exercice complémentaire

Construire un Pokédex simple qui :
1. Charge les 151 premiers Pokémon
2. Affiche leurs cartes avec image et types
3. Permet de rechercher par nom
4. Affiche les détails au clic

```javascript
// src/pokeapi.js
const BASE = "https://pokeapi.co/api/v2";

// Cache simple en mémoire
const cache = new Map();

async function fetchAvecCache(url) {
  if (cache.has(url)) return cache.get(url);
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  cache.set(url, data);
  return data;
}

export async function chargerListePokemon(limite = 151) {
  const liste = await fetchAvecCache(`${BASE}/pokemon?limit=${limite}`);
  return liste.results;
}

export async function chargerDetailsPokemon(nomOuId) {
  return fetchAvecCache(`${BASE}/pokemon/${nomOuId}`);
}

// Charger les détails de plusieurs Pokémon en parallèle (par lots)
export async function chargerPokemonParLots(noms, tailleLot = 20, onProgression) {
  const resultats = [];

  for (let i = 0; i < noms.length; i += tailleLot) {
    const lot = noms.slice(i, i + tailleLot);
    const detailsLot = await Promise.all(lot.map(n => chargerDetailsPokemon(n.name)));
    resultats.push(...detailsLot);

    if (onProgression) {
      onProgression(Math.min(i + tailleLot, noms.length), noms.length);
    }
  }

  return resultats;
}

// Couleurs par type
export const couleurType = {
  fire: "#EF4444", water: "#3B82F6", grass: "#22C55E",
  electric: "#F59E0B", psychic: "#EC4899", ice: "#06B6D4",
  dragon: "#8B5CF6", dark: "#1F2937", fairy: "#F9A8D4",
  normal: "#9CA3AF", fighting: "#D97706", flying: "#60A5FA",
  poison: "#A855F7", ground: "#D97706", rock: "#6B7280",
  bug: "#65A30D", ghost: "#6D28D9", steel: "#9CA3AF",
};

// Rendre une carte Pokémon
export function renduCarte(pokemon) {
  const types = pokemon.types
    .map(t => `<span class="type-badge" style="background:${couleurType[t.type.name] || "#6B7280"}">${t.type.name}</span>`)
    .join("");

  const sprite = pokemon.sprites.other?.["official-artwork"]?.front_default
    ?? pokemon.sprites.front_default;

  return `
    <article class="pokemon-card" data-pokemon="${pokemon.name}" tabindex="0">
      <div class="pokemon-id">#${String(pokemon.id).padStart(3, "0")}</div>
      <img
        src="${sprite}"
        alt="${pokemon.name}"
        loading="lazy"
        class="pokemon-sprite"
      >
      <h3 class="pokemon-nom">${pokemon.name}</h3>
      <div class="pokemon-types">${types}</div>
    </article>
  `;
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'application Pokédex en fonctionnement — montrer la barre de progression pendant le chargement, puis l'affichage progressif des cartes, et dans Network le chargement par lots de 20 requêtes
> **Expliquer :** Charger 151 Pokémon en parallèle total serait une attaque DDoS involontaire contre l'API (151 requêtes simultanées). Le chargement par lots de 20 est un bon compromis : assez parallèle pour être rapide, assez raisonnable pour ne pas surcharger l'API.

---

## Critères de validation

### Partie 1 — Posts
| Critère | Obligatoire |
|---|---|
| Chargement avec skeleton loader | Oui |
| Affichage des posts avec auteur | Oui |
| Filtre par auteur | Oui |
| Recherche textuelle | Oui |
| Modal avec commentaires | Oui |
| Gestion d'erreur réseau | Oui |
| Requêtes parallèles (Promise.all) | Oui |

### Partie 2 — Pokédex (bonus)
| Critère | Obligatoire |
|---|---|
| Chargement par lots | Oui |
| Barre de progression | Non |
| Recherche par nom | Oui |
| Filtre par type | Non |
| Cache des requêtes | Non |

---

## Pour aller plus loin

1. Ajouter de la **pagination** côté client (afficher 20 posts par page)
2. Implémenter un **debounce** sur la recherche pour éviter les requêtes à chaque touche
3. Ajouter un **AbortController** pour annuler les requêtes en cours quand l'utilisateur change rapidement de filtre
4. Stocker les résultats dans **sessionStorage** pour éviter de recharger à chaque visite
