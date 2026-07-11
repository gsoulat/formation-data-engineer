# Formation React — Du Composant à l'Application

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Construire des interfaces utilisateur avec des composants React fonctionnels
- Gérer l'état local avec `useState` et l'état global avec Context API ou Zustand
- Maîtriser les hooks essentiels (`useEffect`, `useRef`, `useMemo`, `useCallback`)
- Créer des hooks personnalisés réutilisables
- Naviguer entre les pages avec React Router v6
- Gérer des formulaires avec React Hook Form et Zod
- Fetcher et mettre en cache des données avec TanStack Query

---

## Prérequis

- JavaScript ES6+ (modules, destructuring, arrow functions, async/await)
- Notions de base en HTML et CSS
- Node.js 18+ installé
- VS Code avec les extensions React/JSX

---

## Structure du cours

```
React/
├── Fondamentaux/
│   ├── 01-introduction.md       ← JSX, Vite, structure d'un composant
│   ├── 02-composants.md         ← Props, children, prop types
│   └── 03-state-events.md       ← useState, événements, formulaires contrôlés
├── Hooks/
│   ├── 01-hooks-base.md         ← useEffect, useRef, useMemo, useCallback
│   └── 02-hooks-custom.md       ← Custom hooks, useFetch, useLocalStorage
├── Routing-State/
│   ├── 01-react-router.md       ← React Router v6, navigation, routes imbriquées
│   └── 02-state-global.md       ← Context API, useReducer, Zustand
├── Avance/
│   ├── 01-formulaires.md        ← React Hook Form, Zod, validation
│   └── 02-fetching-data.md      ← TanStack Query, cache, loading/error
├── exercices/
│   ├── exercice-01-todo-react.md
│   └── exercice-02-dashboard-api.md
└── CHEATSHEET-react.md
```

---

## Mise en place de l'environnement

### Créer un projet avec Vite

```bash
npm create vite@latest mon-projet -- --template react
cd mon-projet
npm install
npm run dev
```

### Ou avec TypeScript

```bash
npm create vite@latest mon-projet -- --template react-ts
```

### Structure d'un projet React Vite

```
mon-projet/
├── src/
│   ├── components/    ← Composants réutilisables
│   ├── pages/         ← Composants de page (avec React Router)
│   ├── hooks/         ← Custom hooks
│   ├── services/      ← Appels API
│   ├── store/         ← État global (Zustand ou Context)
│   ├── utils/         ← Fonctions utilitaires
│   ├── App.jsx        ← Composant racine
│   └── main.jsx       ← Point d'entrée
├── public/            ← Fichiers statiques
├── index.html
├── vite.config.js
└── package.json
```

### Extensions VS Code recommandées

| Extension | Utilité |
|---|---|
| ES7+ React/Redux/React-Native snippets | Raccourcis (rfce, etc.) |
| Simple React Snippets | rfce, useS, etc. |
| Prettier | Formatage |
| ESLint | Détection d'erreurs |
| React Developer Tools (Chrome/Firefox) | Inspecter les composants |
| Auto Rename Tag | Renomme les balises JSX en duo |

---

## Parcours recommandé

### Débutant
1. Fondamentaux 01 → 02 → 03
2. Hooks 01
3. Exercice 01 (Todo React)

### Intermédiaire
1. Hooks 01 → 02
2. Routing-State 01 → 02
3. Exercice 02 (Dashboard)

### Avancé / Production
1. Avancé 01 → 02
2. TypeScript + React
3. Tests avec Vitest + Testing Library

---

## Durée estimée

| Module | Durée |
|---|---|
| Fondamentaux | 5–6 heures |
| Hooks | 4–5 heures |
| Routing & État Global | 4–5 heures |
| Avancé (Forms + Data) | 4–5 heures |
| Exercices | 5–8 heures |
| **Total** | **~22–30 heures** |
