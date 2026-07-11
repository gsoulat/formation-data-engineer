# Exercice 01 — Application Todo avec React

## Objectif

Reconstruire l'application Todo de l'exercice JavaScript en utilisant React. Mettre en pratique les composants, useState, les événements, et la persistance localStorage.

---

## Setup

```bash
npm create vite@latest todo-react -- --template react
cd todo-react
npm install
npm run dev
```

---

## Architecture des composants

```
App
├── TodoForm            ← Input + bouton d'ajout
├── TodoFilters         ← Boutons de filtre (Tous/En cours/Terminées)
├── TodoList            ← Liste des todos
│   └── TodoItem (×n)  ← Un todo individuel
└── TodoFooter          ← Compteur + bouton nettoyer
```

---

## Partie 1 — Les composants

### `TodoItem.jsx`

```jsx
function TodoItem({ todo, onToggle, onDelete }) {
  const date = new Date(todo.createdAt).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <li className={`todo-item${todo.done ? " done" : ""}`}>
      <button
        className="todo-check"
        onClick={() => onToggle(todo.id)}
        aria-label={todo.done ? "Marquer comme non fait" : "Marquer comme fait"}
        aria-checked={todo.done}
        role="checkbox"
      >
        {todo.done ? "✓" : ""}
      </button>

      <span className="todo-text" onClick={() => onToggle(todo.id)}>
        {todo.text}
      </span>

      <span className="todo-date">{date}</span>

      <button
        className="todo-delete"
        onClick={() => onDelete(todo.id)}
        aria-label="Supprimer la tâche"
      >
        ×
      </button>
    </li>
  );
}

export default TodoItem;
```

### `TodoList.jsx`

```jsx
import TodoItem from "./TodoItem";

function TodoList({ todos, onToggle, onDelete }) {
  if (todos.length === 0) {
    return (
      <div className="todo-empty">
        <p>🎉 Aucune tâche à afficher</p>
      </div>
    );
  }

  return (
    <ul className="todo-list">
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}

export default TodoList;
```

### `TodoForm.jsx`

```jsx
import { useState } from "react";

function TodoForm({ onAdd }) {
  const [texte, setTexte] = useState("");
  const [erreur, setErreur] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = texte.trim();

    if (!trimmed) {
      setErreur("La tâche ne peut pas être vide");
      return;
    }

    if (trimmed.length > 200) {
      setErreur("La tâche est trop longue (max 200 caractères)");
      return;
    }

    onAdd(trimmed);
    setTexte("");
    setErreur("");
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className={`todo-input${erreur ? " input-error" : ""}`}
        value={texte}
        onChange={e => {
          setTexte(e.target.value);
          if (erreur) setErreur("");
        }}
        placeholder="Quelle est votre prochaine tâche ?"
        maxLength={200}
        autoFocus
      />
      <button type="submit" className="btn btn-primary">
        Ajouter
      </button>
      {erreur && <span className="error-message">{erreur}</span>}
    </form>
  );
}

export default TodoForm;
```

### `TodoFilters.jsx`

```jsx
const FILTRES = [
  { id: "all", label: "Toutes" },
  { id: "active", label: "En cours" },
  { id: "done", label: "Terminées" },
];

function TodoFilters({ filtreCourant, onChange }) {
  return (
    <div className="todo-filters" role="group" aria-label="Filtres">
      {FILTRES.map(filtre => (
        <button
          key={filtre.id}
          className={`filter-btn${filtreCourant === filtre.id ? " active" : ""}`}
          onClick={() => onChange(filtre.id)}
        >
          {filtre.label}
        </button>
      ))}
    </div>
  );
}

export default TodoFilters;
```

### `TodoFooter.jsx`

```jsx
function TodoFooter({ totalActifs, totalTermines, filtre, onClearDone }) {
  return (
    <footer className="todo-footer">
      <span className="todo-count">
        {totalActifs} tâche{totalActifs !== 1 ? "s" : ""} restante{totalActifs !== 1 ? "s" : ""}
      </span>

      {totalTermines > 0 && (
        <button className="btn btn-ghost" onClick={onClearDone}>
          Nettoyer terminées ({totalTermines})
        </button>
      )}
    </footer>
  );
}

export default TodoFooter;
```

---

## Partie 2 — Le hook useLocalStorage

```jsx
// src/hooks/useLocalStorage.js
import { useState, useEffect } from "react";

export function useLocalStorage(cle, valeurInitiale) {
  const [valeur, setValeur] = useState(() => {
    try {
      const item = localStorage.getItem(cle);
      return item ? JSON.parse(item) : valeurInitiale;
    } catch {
      return valeurInitiale;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(cle, JSON.stringify(valeur));
    } catch (err) {
      console.warn("localStorage write failed:", err);
    }
  }, [cle, valeur]);

  return [valeur, setValeur];
}
```

---

## Partie 3 — App.jsx — Assemblage

```jsx
// src/App.jsx
import { useState } from "react";
import { useLocalStorage } from "./hooks/useLocalStorage";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";
import TodoFilters from "./components/TodoFilters";
import TodoFooter from "./components/TodoFooter";
import "./App.css";

function App() {
  const [todos, setTodos] = useLocalStorage("react-todos", []);
  const [filtre, setFiltre] = useState("all");

  // Actions
  const ajouterTodo = (texte) => {
    const nouveau = {
      id: Date.now(),
      text: texte,
      done: false,
      createdAt: new Date().toISOString(),
    };
    setTodos(prev => [...prev, nouveau]);
  };

  const toggleTodo = (id) => {
    setTodos(prev =>
      prev.map(t => t.id === id ? { ...t, done: !t.done } : t)
    );
  };

  const supprimerTodo = (id) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  };

  const nettoyerTerminees = () => {
    setTodos(prev => prev.filter(t => !t.done));
  };

  // Filtrage
  const todosFiltres = todos.filter(t => {
    if (filtre === "active") return !t.done;
    if (filtre === "done") return t.done;
    return true;
  });

  const totalActifs = todos.filter(t => !t.done).length;
  const totalTermines = todos.filter(t => t.done).length;

  return (
    <div className="app">
      <header className="app-header">
        <h1>📝 Todo React</h1>
      </header>

      <main className="app-main">
        <TodoForm onAdd={ajouterTodo} />

        {todos.length > 0 && (
          <>
            <div className="todo-actions">
              <TodoFilters filtreCourant={filtre} onChange={setFiltre} />
            </div>

            <TodoList
              todos={todosFiltres}
              onToggle={toggleTodo}
              onDelete={supprimerTodo}
            />

            <TodoFooter
              totalActifs={totalActifs}
              totalTermines={totalTermines}
              filtre={filtre}
              onClearDone={nettoyerTerminees}
            />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React DevTools → Components → montrer l'arbre complet App > TodoList > TodoItem. Sélectionner un TodoItem, modifier son état `done` directement dans les hooks, et montrer que le composant se met à jour visuellement.
> **Expliquer :** React DevTools permet de "simuler" des interactions sans toucher l'UI. C'est très utile pour tester différents états d'un composant (done/undone, texte long, etc.) sans avoir à naviguer dans l'app.

---

## Partie 4 — Améliorations (bonus)

### Niveau 1 : Drag and Drop

```jsx
// npm install @dnd-kit/core @dnd-kit/sortable
import { DndContext } from "@dnd-kit/core";
import { SortableContext, useSortable, arrayMove } from "@dnd-kit/sortable";

function TodoListSortable({ todos, onReorder, onToggle, onDelete }) {
  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const ancienIndex = todos.findIndex(t => t.id === active.id);
      const nouvelIndex = todos.findIndex(t => t.id === over.id);
      onReorder(arrayMove(todos, ancienIndex, nouvelIndex));
    }
  };

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <SortableContext items={todos.map(t => t.id)}>
        <ul className="todo-list">
          {todos.map(todo => (
            <TodoItemSortable key={todo.id} todo={todo} onToggle={onToggle} onDelete={onDelete} />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  );
}
```

### Niveau 2 : Édition inline

```jsx
function TodoItemEditable({ todo, onToggle, onDelete, onEdit }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(todo.text);
  const inputRef = useRef(null);

  const startEdit = () => {
    setEditing(true);
    setDraft(todo.text);
  };

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  const saveEdit = () => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== todo.text) {
      onEdit(todo.id, trimmed);
    }
    setEditing(false);
  };

  return (
    <li className={`todo-item${todo.done ? " done" : ""}`}>
      {editing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={e => setDraft(e.target.value)}
          onBlur={saveEdit}
          onKeyDown={e => {
            if (e.key === "Enter") saveEdit();
            if (e.key === "Escape") setEditing(false);
          }}
        />
      ) : (
        <span onDoubleClick={startEdit}>{todo.text}</span>
      )}
      {/* ... autres boutons */}
    </li>
  );
}
```

---

## Critères de validation

| Critère | Obligatoire |
|---|---|
| Ajouter une tâche | Oui |
| Supprimer une tâche | Oui |
| Marquer comme terminée | Oui |
| Filtrer | Oui |
| Persistance localStorage | Oui |
| Découpage en composants | Oui |
| Lifting state up | Oui |
| Animations CSS | Non |
| Drag & drop | Non |
| Édition inline | Non |
