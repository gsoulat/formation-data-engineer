# 02 — État Global : Context API, useReducer, Zustand

## Introduction

Quand plusieurs composants non directement liés ont besoin du même état, le "prop drilling" (passer les props à travers de multiples niveaux) devient problématique. Les solutions d'état global permettent à n'importe quel composant d'accéder aux données partagées.

---

## 1. Le problème du Prop Drilling

```jsx
// ❌ Prop drilling — theme doit traverser tous les composants intermédiaires
function App() {
  const [theme, setTheme] = useState("clair");
  return <PageLayout theme={theme} setTheme={setTheme} />;
}

function PageLayout({ theme, setTheme }) {
  return <Header theme={theme} setTheme={setTheme} />;
  // PageLayout n'utilise pas theme, mais doit le transmettre
}

function Header({ theme, setTheme }) {
  return <BoutonTheme theme={theme} setTheme={setTheme} />;
  // Header n'utilise pas theme non plus...
}

function BoutonTheme({ theme, setTheme }) {
  // Enfin, le composant qui en a besoin
  return (
    <button onClick={() => setTheme(t => t === "clair" ? "sombre" : "clair")}>
      {theme === "clair" ? "🌙" : "☀️"}
    </button>
  );
}
```

---

## 2. Context API — Solution native React

```jsx
// src/contexts/ThemeContext.jsx
import { createContext, useContext, useState } from "react";

// 1. Créer le contexte
const ThemeContext = createContext(null);

// 2. Créer le Provider (composant qui enveloppe l'arbre)
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("clair");

  const toggleTheme = () => setTheme(t => t === "clair" ? "sombre" : "clair");

  const valeur = { theme, setTheme, toggleTheme };

  return (
    <ThemeContext.Provider value={valeur}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Hook personnalisé pour consommer le contexte
function useTheme() {
  const contexte = useContext(ThemeContext);
  if (!contexte) {
    throw new Error("useTheme doit être utilisé à l'intérieur de ThemeProvider");
  }
  return contexte;
}

export { ThemeProvider, useTheme };
```

```jsx
// src/main.jsx — Envelopper l'app avec le Provider
import { ThemeProvider } from "./contexts/ThemeContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>
);

// N'importe quel composant peut maintenant accéder au thème
function BoutonTheme() {
  const { theme, toggleTheme } = useTheme(); // ✅ Pas de prop drilling !
  return (
    <button onClick={toggleTheme}>
      {theme === "clair" ? "🌙 Mode sombre" : "☀️ Mode clair"}
    </button>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** React DevTools → onglet Components → cliquer sur le Provider dans l'arbre → montrer la valeur du contexte dans le panneau. Puis cliquer sur un composant enfant profond qui consomme le contexte — montrer dans "Hooks" que le contexte est accessible directement.
> **Expliquer :** Le Context API résout le prop drilling en créant un "bus de données" accessible depuis n'importe quel composant dans l'arbre. Mais attention : à chaque changement de valeur du contexte, TOUS les composants consommateurs se re-rendent.

---

## 3. useReducer — État complexe

`useReducer` est une alternative à `useState` pour gérer des états complexes avec plusieurs transitions.

```jsx
import { useReducer } from "react";

// Le reducer — une fonction pure qui détermine le nouvel état
function todoReducer(etat, action) {
  switch (action.type) {
    case "AJOUTER": {
      const nouveau = {
        id: Date.now(),
        texte: action.payload,
        fait: false,
      };
      return { ...etat, todos: [...etat.todos, nouveau] };
    }

    case "TOGGLER": {
      return {
        ...etat,
        todos: etat.todos.map(t =>
          t.id === action.payload ? { ...t, fait: !t.fait } : t
        ),
      };
    }

    case "SUPPRIMER": {
      return {
        ...etat,
        todos: etat.todos.filter(t => t.id !== action.payload),
      };
    }

    case "CHANGER_FILTRE": {
      return { ...etat, filtre: action.payload };
    }

    case "NETTOYER_FAITS": {
      return { ...etat, todos: etat.todos.filter(t => !t.fait) };
    }

    default:
      throw new Error(`Action inconnue: ${action.type}`);
  }
}

const ETAT_INITIAL = {
  todos: [],
  filtre: "tous", // "tous" | "actifs" | "faits"
};

function TodoApp() {
  const [etat, dispatch] = useReducer(todoReducer, ETAT_INITIAL);

  const { todos, filtre } = etat;

  const todosFiltres = todos.filter(t => {
    if (filtre === "actifs") return !t.fait;
    if (filtre === "faits") return t.fait;
    return true;
  });

  return (
    <div>
      <input
        onKeyDown={e => {
          if (e.key === "Enter" && e.target.value.trim()) {
            dispatch({ type: "AJOUTER", payload: e.target.value.trim() });
            e.target.value = "";
          }
        }}
      />

      <ul>
        {todosFiltres.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.fait}
              onChange={() => dispatch({ type: "TOGGLER", payload: todo.id })}
            />
            <span>{todo.texte}</span>
            <button onClick={() => dispatch({ type: "SUPPRIMER", payload: todo.id })}>
              ×
            </button>
          </li>
        ))}
      </ul>

      <div>
        {["tous", "actifs", "faits"].map(f => (
          <button
            key={f}
            onClick={() => dispatch({ type: "CHANGER_FILTRE", payload: f })}
            className={filtre === f ? "actif" : ""}
          >
            {f}
          </button>
        ))}
        <button onClick={() => dispatch({ type: "NETTOYER_FAITS" })}>
          Nettoyer
        </button>
      </div>
    </div>
  );
}
```

---

## 4. Context API + useReducer — Pattern complet

```jsx
// src/contexts/PanierContext.jsx
import { createContext, useContext, useReducer } from "react";

// Actions typées (en TS ce serait une union discriminée)
const ActionTypes = {
  AJOUTER: "AJOUTER",
  RETIRER: "RETIRER",
  MODIFIER_QUANTITE: "MODIFIER_QUANTITE",
  VIDER: "VIDER",
};

function panierReducer(etat, action) {
  switch (action.type) {
    case ActionTypes.AJOUTER: {
      const existant = etat.items.find(i => i.produit.id === action.payload.id);
      if (existant) {
        return {
          ...etat,
          items: etat.items.map(item =>
            item.produit.id === action.payload.id
              ? { ...item, quantite: item.quantite + 1 }
              : item
          ),
        };
      }
      return {
        ...etat,
        items: [...etat.items, { produit: action.payload, quantite: 1 }],
      };
    }

    case ActionTypes.RETIRER:
      return {
        ...etat,
        items: etat.items.filter(i => i.produit.id !== action.payload),
      };

    case ActionTypes.MODIFIER_QUANTITE: {
      const { id, quantite } = action.payload;
      if (quantite <= 0) {
        return { ...etat, items: etat.items.filter(i => i.produit.id !== id) };
      }
      return {
        ...etat,
        items: etat.items.map(i =>
          i.produit.id === id ? { ...i, quantite } : i
        ),
      };
    }

    case ActionTypes.VIDER:
      return { ...etat, items: [] };

    default:
      return etat;
  }
}

const PanierContext = createContext(null);

function PanierProvider({ children }) {
  const [etat, dispatch] = useReducer(panierReducer, { items: [] });

  // Actions helper — éviter d'exposer dispatch directement
  const actions = {
    ajouterProduit: (produit) => dispatch({ type: ActionTypes.AJOUTER, payload: produit }),
    retirerProduit: (id) => dispatch({ type: ActionTypes.RETIRER, payload: id }),
    modifierQuantite: (id, qt) => dispatch({ type: ActionTypes.MODIFIER_QUANTITE, payload: { id, quantite: qt } }),
    viderPanier: () => dispatch({ type: ActionTypes.VIDER }),
  };

  // Valeurs dérivées
  const total = etat.items.reduce((sum, i) => sum + i.produit.prix * i.quantite, 0);
  const nbItems = etat.items.reduce((sum, i) => sum + i.quantite, 0);

  return (
    <PanierContext.Provider value={{ ...etat, ...actions, total, nbItems }}>
      {children}
    </PanierContext.Provider>
  );
}

function usePanier() {
  const ctx = useContext(PanierContext);
  if (!ctx) throw new Error("usePanier doit être dans PanierProvider");
  return ctx;
}

export { PanierProvider, usePanier };

// Utilisation dans n'importe quel composant
function BoutonAjouterPanier({ produit }) {
  const { ajouterProduit, nbItems } = usePanier();

  return (
    <button onClick={() => ajouterProduit(produit)}>
      Ajouter au panier ({nbItems})
    </button>
  );
}

function ResumePanier() {
  const { items, total, retirerProduit, viderPanier } = usePanier();
  return (
    <div>
      {items.map(({ produit, quantite }) => (
        <div key={produit.id}>
          {produit.nom} × {quantite} = {(produit.prix * quantite).toFixed(2)}€
          <button onClick={() => retirerProduit(produit.id)}>×</button>
        </div>
      ))}
      <strong>Total : {total.toFixed(2)}€</strong>
      <button onClick={viderPanier}>Vider</button>
    </div>
  );
}
```

---

## 5. Zustand — Gestion d'état simple et performante

Zustand est une bibliothèque d'état minimaliste qui évite les inconvénients du Context (re-renders sur tout l'arbre).

```bash
npm install zustand
```

```jsx
// src/store/panierStore.js
import { create } from "zustand";
import { persist } from "zustand/middleware"; // Persistance localStorage

const usePanierStore = create(
  persist( // Middleware pour sauvegarder dans localStorage
    (set, get) => ({
      // État
      items: [],

      // Actions
      ajouterProduit(produit) {
        set(etat => {
          const existant = etat.items.find(i => i.produit.id === produit.id);
          if (existant) {
            return {
              items: etat.items.map(i =>
                i.produit.id === produit.id
                  ? { ...i, quantite: i.quantite + 1 }
                  : i
              ),
            };
          }
          return { items: [...etat.items, { produit, quantite: 1 }] };
        });
      },

      retirerProduit(id) {
        set(etat => ({
          items: etat.items.filter(i => i.produit.id !== id),
        }));
      },

      modifierQuantite(id, quantite) {
        if (quantite <= 0) {
          get().retirerProduit(id);
          return;
        }
        set(etat => ({
          items: etat.items.map(i =>
            i.produit.id === id ? { ...i, quantite } : i
          ),
        }));
      },

      viderPanier() {
        set({ items: [] });
      },

      // Valeurs dérivées (calculées)
      get total() {
        return get().items.reduce(
          (sum, i) => sum + i.produit.prix * i.quantite,
          0
        );
      },

      get nbItems() {
        return get().items.reduce((sum, i) => sum + i.quantite, 0);
      },
    }),
    {
      name: "panier-storage", // Clé localStorage
      partialize: (etat) => ({ items: etat.items }), // Sauvegarder seulement items
    }
  )
);

export default usePanierStore;
```

```jsx
// Utilisation — AUCUN Provider nécessaire !
import usePanierStore from "../store/panierStore";

function BoutonAjouterPanier({ produit }) {
  // Sélectionner SEULEMENT la fonction nécessaire
  // → Ce composant ne se re-rend pas si d'autres parties du store changent
  const ajouterProduit = usePanierStore(etat => etat.ajouterProduit);

  return <button onClick={() => ajouterProduit(produit)}>Ajouter</button>;
}

function BadgeNbItems() {
  const nbItems = usePanierStore(etat => etat.nbItems);
  return <span>{nbItems}</span>; // Se re-rend seulement quand nbItems change
}

function ResumePanier() {
  // Sélectionner plusieurs valeurs
  const { items, total, retirerProduit } = usePanierStore(etat => ({
    items: etat.items,
    total: etat.total,
    retirerProduit: etat.retirerProduit,
  }));

  return (/* ... */);
}
```

### Store Zustand avec TypeScript

```typescript
// src/store/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface Utilisateur {
  id: number;
  nom: string;
  email: string;
  role: "admin" | "utilisateur";
}

interface AuthState {
  utilisateur: Utilisateur | null;
  token: string | null;
  estAuthentifie: boolean;
  connexion: (email: string, motDePasse: string) => Promise<void>;
  deconnexion: () => void;
}

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      utilisateur: null,
      token: null,
      estAuthentifie: false,

      async connexion(email, motDePasse) {
        const response = await fetch("/api/auth/connexion", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, motDePasse }),
        });

        if (!response.ok) throw new Error("Identifiants incorrects");

        const { utilisateur, token } = await response.json();
        set({ utilisateur, token, estAuthentifie: true });
      },

      deconnexion() {
        set({ utilisateur: null, token: null, estAuthentifie: false });
      },
    }),
    { name: "auth-storage" }
  )
);

export default useAuthStore;
```

---

## 6. Quand utiliser quoi ?

```
└── Local state (useState)
    └── Pour l'état qui ne concerne qu'un seul composant
        Exemples : ouverture d'une modal, valeur d'un input

└── Lifting state up
    └── Pour l'état partagé entre quelques composants proches dans l'arbre
        Exemples : panier simple, filtre d'une liste

└── Context API
    └── Pour l'état global rarement modifié
        Exemples : theme, langue, utilisateur connecté

└── Zustand / Jotai / Recoil
    └── Pour l'état global complexe ou fréquemment modifié
        Exemples : panier e-commerce, état d'une app métier

└── TanStack Query (chapitre suivant)
    └── Pour l'état serveur (données fetchées depuis une API)
        Exemples : listes d'utilisateurs, profils, données en cache
```

---

## Récapitulatif

| Solution | Avantages | Inconvénients |
|---|---|---|
| `useState` | Simple, natif | Local seulement |
| Context API | Natif, bien intégré | Re-renders sur tout le sous-arbre |
| `useReducer` + Context | Transitions d'état prévisibles | Verbeux |
| Zustand | Minimaliste, performant, persist inclus | Dépendance externe |
