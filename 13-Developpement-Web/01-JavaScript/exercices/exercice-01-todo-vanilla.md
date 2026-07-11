# Exercice 01 — Application Todo en Vanilla JavaScript

## Objectif

Construire une application Todo complète sans framework, en utilisant uniquement HTML, CSS et JavaScript. Cet exercice met en pratique la manipulation du DOM, la gestion d'événements, le localStorage et les classes ES6.

---

## Résultat attendu

Une application web avec les fonctionnalités suivantes :

- Ajouter une tâche (via bouton ou touche Enter)
- Afficher la liste des tâches
- Marquer une tâche comme terminée (clic sur la tâche)
- Supprimer une tâche
- Filtrer les tâches (Toutes / En cours / Terminées)
- Compter les tâches restantes
- Effacer toutes les tâches terminées
- Persister les données dans localStorage

---

## Partie 1 — Structure HTML

Créez le fichier `index.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todo App — Vanilla JS</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="app">
    <header class="app-header">
      <h1>📝 Ma Todo List</h1>
    </header>

    <main class="app-main">
      <!-- Formulaire d'ajout -->
      <div class="todo-form">
        <input
          type="text"
          id="input-todo"
          class="todo-input"
          placeholder="Quelle est votre prochaine tâche ?"
          maxlength="200"
          autocomplete="off"
        >
        <button id="btn-ajouter" class="btn btn-primary">Ajouter</button>
      </div>

      <!-- Barre d'actions -->
      <div class="todo-actions" id="todo-actions" hidden>
        <span id="compteur"></span>

        <div class="filtres" role="group" aria-label="Filtrer les tâches">
          <button class="filtre actif" data-filtre="tous">Toutes</button>
          <button class="filtre" data-filtre="en-cours">En cours</button>
          <button class="filtre" data-filtre="terminees">Terminées</button>
        </div>

        <button id="btn-nettoyer" class="btn btn-ghost">Nettoyer terminées</button>
      </div>

      <!-- Liste des todos -->
      <ul id="liste-todos" class="todo-list" role="list"></ul>

      <!-- Message si vide -->
      <div id="message-vide" class="message-vide" hidden>
        <p>🎉 Aucune tâche à afficher</p>
      </div>
    </main>
  </div>

  <script type="module" src="app.js"></script>
</body>
</html>
```

---

## Partie 2 — Styles CSS

Créez le fichier `style.css` :

```css
/* Variables */
:root {
  --couleur-primaire: #4f46e5;
  --couleur-primaire-hover: #4338ca;
  --couleur-fond: #f1f5f9;
  --couleur-surface: #ffffff;
  --couleur-texte: #1e293b;
  --couleur-texte-clair: #64748b;
  --couleur-terminee: #94a3b8;
  --couleur-danger: #ef4444;
  --ombre: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --rayon: 8px;
  --transition: 150ms ease;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--couleur-fond);
  color: var(--couleur-texte);
  min-height: 100vh;
  padding: 2rem 1rem;
}

.app {
  max-width: 600px;
  margin: 0 auto;
}

.app-header h1 {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: var(--couleur-primaire);
}

/* Formulaire */
.todo-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.todo-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: var(--rayon);
  font-size: 1rem;
  transition: border-color var(--transition);
  background: var(--couleur-surface);
}

.todo-input:focus {
  outline: none;
  border-color: var(--couleur-primaire);
}

/* Boutons */
.btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: var(--rayon);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.btn-primary {
  background: var(--couleur-primaire);
  color: white;
}

.btn-primary:hover {
  background: var(--couleur-primaire-hover);
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  color: var(--couleur-danger);
  border: 1px solid var(--couleur-danger);
  font-size: 0.8rem;
  padding: 0.4rem 0.75rem;
}

.btn-ghost:hover {
  background: #fee2e2;
}

/* Actions et filtres */
.todo-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--couleur-surface);
  border-radius: var(--rayon);
  margin-bottom: 1rem;
  box-shadow: var(--ombre);
  flex-wrap: wrap;
  gap: 0.5rem;
}

#compteur {
  font-size: 0.85rem;
  color: var(--couleur-texte-clair);
  white-space: nowrap;
}

.filtres {
  display: flex;
  gap: 0.25rem;
}

.filtre {
  padding: 0.35rem 0.75rem;
  border: 1px solid #e2e8f0;
  background: transparent;
  border-radius: 20px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--transition);
  color: var(--couleur-texte-clair);
}

.filtre:hover, .filtre.actif {
  background: var(--couleur-primaire);
  color: white;
  border-color: var(--couleur-primaire);
}

/* Liste */
.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Item todo */
.todo-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--couleur-surface);
  border-radius: var(--rayon);
  box-shadow: var(--ombre);
  transition: all var(--transition);
  animation: glisserEntree 200ms ease forwards;
}

@keyframes glisserEntree {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}

.todo-item.terminee .todo-texte {
  text-decoration: line-through;
  color: var(--couleur-terminee);
}

.todo-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.todo-item.terminee .todo-checkbox {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}

.todo-texte {
  flex: 1;
  font-size: 0.95rem;
  cursor: pointer;
  word-break: break-word;
}

.todo-date {
  font-size: 0.75rem;
  color: var(--couleur-texte-clair);
  white-space: nowrap;
}

.btn-supprimer {
  background: none;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color var(--transition);
  line-height: 1;
}

.btn-supprimer:hover {
  color: var(--couleur-danger);
}

/* Message vide */
.message-vide {
  text-align: center;
  padding: 3rem;
  color: var(--couleur-texte-clair);
}

[hidden] { display: none !important; }
```

---

## Partie 3 — JavaScript

Créez le fichier `app.js` :

### Étape 1 : Le modèle Todo

```javascript
// todo.js — Le modèle de données
export class Todo {
  constructor(texte) {
    this.id = Date.now() + Math.random(); // ID unique
    this.texte = texte.trim();
    this.terminee = false;
    this.createdAt = new Date();
  }

  toggle() {
    this.terminee = !this.terminee;
    return this;
  }

  static depuis(objet) {
    // Recréer une instance depuis un objet plain (ex: localStorage)
    const todo = new Todo(objet.texte);
    todo.id = objet.id;
    todo.terminee = objet.terminee;
    todo.createdAt = new Date(objet.createdAt);
    return todo;
  }
}
```

### Étape 2 : Le store (gestion d'état)

```javascript
// store.js — Gestion de l'état
import { Todo } from "./todo.js";

const CLE_STORAGE = "todos-vanilla-js";

export class TodoStore {
  #todos = [];
  #filtre = "tous"; // "tous" | "en-cours" | "terminees"
  #listeners = new Set();

  constructor() {
    this.#chargerDepuisStorage();
  }

  // ---- Lecture ----

  get todos() {
    return this.#filtrer();
  }

  get tousLesTodos() {
    return [...this.#todos];
  }

  get filtre() {
    return this.#filtre;
  }

  get nombreRestants() {
    return this.#todos.filter(t => !t.terminee).length;
  }

  get nombreTermines() {
    return this.#todos.filter(t => t.terminee).length;
  }

  get total() {
    return this.#todos.length;
  }

  // ---- Actions ----

  ajouter(texte) {
    if (!texte.trim()) return null;
    const todo = new Todo(texte);
    this.#todos.push(todo);
    this.#sauvegarder();
    this.#notifier();
    return todo;
  }

  toggler(id) {
    const todo = this.#todos.find(t => t.id === id);
    if (todo) {
      todo.toggle();
      this.#sauvegarder();
      this.#notifier();
    }
  }

  supprimer(id) {
    const avant = this.#todos.length;
    this.#todos = this.#todos.filter(t => t.id !== id);
    if (this.#todos.length !== avant) {
      this.#sauvegarder();
      this.#notifier();
    }
  }

  nettoyerTerminees() {
    this.#todos = this.#todos.filter(t => !t.terminee);
    this.#sauvegarder();
    this.#notifier();
  }

  changerFiltre(filtre) {
    if (this.#filtre !== filtre) {
      this.#filtre = filtre;
      this.#notifier();
    }
  }

  // ---- Réactivité ----

  abonner(listener) {
    this.#listeners.add(listener);
    return () => this.#listeners.delete(listener); // Retourne une fonction de désabonnement
  }

  // ---- Privé ----

  #filtrer() {
    switch (this.#filtre) {
      case "en-cours":
        return this.#todos.filter(t => !t.terminee);
      case "terminees":
        return this.#todos.filter(t => t.terminee);
      default:
        return [...this.#todos];
    }
  }

  #sauvegarder() {
    localStorage.setItem(CLE_STORAGE, JSON.stringify(this.#todos));
  }

  #chargerDepuisStorage() {
    try {
      const donnees = localStorage.getItem(CLE_STORAGE);
      if (donnees) {
        this.#todos = JSON.parse(donnees).map(Todo.depuis);
      }
    } catch (erreur) {
      console.warn("Impossible de charger les todos:", erreur);
      this.#todos = [];
    }
  }

  #notifier() {
    this.#listeners.forEach(fn => fn());
  }
}
```

### Étape 3 : La vue (manipulation DOM)

```javascript
// vue.js — Rendu et événements DOM
export class TodoVue {
  #store;
  #elements;

  constructor(store) {
    this.#store = store;
    this.#elements = {
      input: document.querySelector("#input-todo"),
      btnAjouter: document.querySelector("#btn-ajouter"),
      liste: document.querySelector("#liste-todos"),
      actions: document.querySelector("#todo-actions"),
      compteur: document.querySelector("#compteur"),
      filtres: document.querySelectorAll(".filtre"),
      btnNettoyer: document.querySelector("#btn-nettoyer"),
      messageVide: document.querySelector("#message-vide"),
    };

    this.#attacherEvenements();
    this.#store.abonner(() => this.#rendu());
    this.#rendu(); // Rendu initial
  }

  #attacherEvenements() {
    const { input, btnAjouter, filtres, btnNettoyer, liste } = this.#elements;

    // Ajouter une tâche
    const ajouterTodo = () => {
      const texte = input.value.trim();
      if (!texte) {
        input.classList.add("erreur");
        setTimeout(() => input.classList.remove("erreur"), 500);
        return;
      }
      this.#store.ajouter(texte);
      input.value = "";
      input.focus();
    };

    btnAjouter.addEventListener("click", ajouterTodo);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") ajouterTodo();
    });

    // Filtres
    filtres.forEach(btn => {
      btn.addEventListener("click", () => {
        this.#store.changerFiltre(btn.dataset.filtre);
      });
    });

    // Nettoyer terminées
    btnNettoyer.addEventListener("click", () => {
      if (this.#store.nombreTermines > 0) {
        this.#store.nettoyerTerminees();
      }
    });

    // Délégation sur la liste (toggle + supprimer)
    liste.addEventListener("click", (e) => {
      const li = e.target.closest(".todo-item");
      if (!li) return;

      const id = Number(li.dataset.id);

      if (e.target.closest(".btn-supprimer")) {
        this.#supprimerAvecAnimation(li, id);
      } else if (e.target.closest(".todo-checkbox") || e.target.closest(".todo-texte")) {
        this.#store.toggler(id);
      }
    });
  }

  #supprimerAvecAnimation(element, id) {
    element.style.transition = "all 200ms ease";
    element.style.opacity = "0";
    element.style.transform = "translateX(20px)";

    setTimeout(() => {
      this.#store.supprimer(id);
    }, 200);
  }

  #rendu() {
    const todos = this.#store.todos;
    const { liste, actions, compteur, filtres, btnNettoyer, messageVide } = this.#elements;

    // Afficher/masquer la barre d'actions
    actions.hidden = this.#store.total === 0;

    // Compteur
    const n = this.#store.nombreRestants;
    compteur.textContent = `${n} tâche${n > 1 ? "s" : ""} restante${n > 1 ? "s" : ""}`;

    // Filtres actifs
    filtres.forEach(btn => {
      btn.classList.toggle("actif", btn.dataset.filtre === this.#store.filtre);
    });

    // Bouton nettoyer
    btnNettoyer.hidden = this.#store.nombreTermines === 0;

    // Liste des todos
    if (todos.length === 0) {
      liste.innerHTML = "";
      messageVide.hidden = false;
    } else {
      messageVide.hidden = true;
      liste.innerHTML = todos.map(todo => this.#renduItem(todo)).join("");
    }
  }

  #renduItem(todo) {
    const date = todo.createdAt.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });

    return `
      <li class="todo-item${todo.terminee ? " terminee" : ""}" data-id="${todo.id}">
        <div class="todo-checkbox" role="checkbox" aria-checked="${todo.terminee}" tabindex="0">
          ${todo.terminee ? "✓" : ""}
        </div>
        <span class="todo-texte">${this.#echapperHTML(todo.texte)}</span>
        <span class="todo-date">${date}</span>
        <button class="btn-supprimer" aria-label="Supprimer la tâche" title="Supprimer">×</button>
      </li>
    `;
  }

  #echapperHTML(texte) {
    // Prévenir les injections XSS
    return texte
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}
```

### Étape 4 : Le point d'entrée

```javascript
// app.js
import { TodoStore } from "./store.js";
import { TodoVue } from "./vue.js";

// Initialisation au chargement du DOM
document.addEventListener("DOMContentLoaded", () => {
  const store = new TodoStore();
  const vue = new TodoVue(store);

  console.log("Todo App initialisée");
});
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration live de l'application — ajouter des todos, les cocher, les filtrer, recharger la page (montrer la persistance localStorage), puis ouvrir DevTools → Application → Local Storage pour voir les données JSON
> **Expliquer :** C'est le pattern MVC (Modèle-Vue-Contrôleur) adapté au vanilla JS. Le Store est le modèle, la Vue s'occupe du DOM. Le Store notifie la Vue à chaque changement. React et Vue.js reprennent exactement ce principe avec un flux de données unidirectionnel.

---

## Partie 4 — Améliorations possibles

### Niveau 1 (facile)
- Ajouter un champ priorité (basse/moyenne/haute) avec un badge coloré
- Permettre l'édition inline d'une tâche (double-clic sur le texte)
- Ajouter un drag-and-drop pour réordonner les tâches

### Niveau 2 (intermédiaire)
- Synchroniser avec un backend (API REST)
- Ajouter des catégories/tags
- Implémenter un système d'annulation (Ctrl+Z)

### Niveau 3 (avancé)
- Synchronisation en temps réel avec WebSocket
- Trier par date, priorité, alphabétique
- Export en JSON, CSV ou PDF

---

## Critères de validation

| Critère | Obligatoire |
|---|---|
| Ajouter une tâche via Enter et le bouton | Oui |
| Marquer une tâche comme terminée | Oui |
| Supprimer une tâche | Oui |
| Filtrer les tâches (Toutes/En cours/Terminées) | Oui |
| Persister les données dans localStorage | Oui |
| Pas d'injection XSS possible | Oui |
| Animations sur ajout/suppression | Non (bonus) |
| Accessibilité (aria-*, rôles) | Non (bonus) |
