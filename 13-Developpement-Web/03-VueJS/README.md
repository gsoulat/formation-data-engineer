# Formation Vue 3 — Guide Complet

## Objectifs pédagogiques

À l'issue de cette formation, les apprenants seront capables de :

- Comprendre l'architecture et la philosophie de Vue 3
- Créer des composants réactifs avec la Composition API
- Gérer la navigation avec Vue Router 4
- Gérer l'état global avec Pinia
- Structurer une application Vue 3 professionnelle avec TypeScript

## Prérequis

- HTML / CSS solide
- JavaScript ES6+ (destructuring, arrow functions, modules, async/await)
- Notions de base en TypeScript (recommandé)
- Node.js 18+ installé

## Plan de la formation

### Module 1 — Fondamentaux (3h)

| Fichier | Contenu |
|---|---|
| `Fondamentaux/01-introduction.md` | Vue 3, Options API vs Composition API, setup Vite |
| `Fondamentaux/02-template-syntax.md` | v-bind, v-model, v-if, v-for, v-on, template refs |
| `Fondamentaux/03-composants.md` | defineComponent, props, emits, slots, cycle de vie |

### Module 2 — Composition API (2h)

| Fichier | Contenu |
|---|---|
| `Composition-API/01-reactivity.md` | ref, reactive, computed, watch, watchEffect |
| `Composition-API/02-composables.md` | Composables personnalisés, useFetch, useCounter |

### Module 3 — Écosystème (2h)

| Fichier | Contenu |
|---|---|
| `Ecosystem/01-vue-router.md` | Vue Router 4, routes, navigation guards, lazy loading |
| `Ecosystem/02-pinia.md` | Pinia, defineStore, state/getters/actions |

### Module 4 — Avancé (1h)

| Fichier | Contenu |
|---|---|
| `Avance/01-typescript-vue.md` | Vue 3 + TypeScript, typage des props, useTemplateRef |

### Exercices pratiques

| Fichier | Contenu |
|---|---|
| `exercices/exercice-01-todo-vue.md` | Application Todo complète |
| `exercices/exercice-02-dashboard.md` | Dashboard avec API REST |

## Installation rapide

```bash
# Créer un projet Vue 3 avec Vite
npm create vite@latest mon-projet -- --template vue

# Avec TypeScript
npm create vite@latest mon-projet -- --template vue-ts

cd mon-projet
npm install
npm run dev
```

## Ressources officielles

- Documentation Vue 3 : https://vuejs.org
- Vue Router 4 : https://router.vuejs.org
- Pinia : https://pinia.vuejs.org
- Vite : https://vitejs.dev
- Vue Devtools : https://devtools.vuejs.org

## Comparaison rapide des frameworks

| Critère | Vue 3 | React | Angular |
|---|---|---|---|
| Courbe d'apprentissage | Douce | Moyenne | Raide |
| Taille du bundle | Petite | Petite | Moyenne |
| TypeScript | Optionnel | Optionnel | Natif |
| State management | Pinia | Redux/Zustand | NgRx/Services |
| Routing | Vue Router | React Router | Angular Router |
| Popularité | Haute | Très haute | Haute |

## Convention de code utilisée dans ce cours

- Composition API avec `<script setup>` (syntaxe moderne)
- TypeScript activé
- ESLint + Prettier
- Nommage des composants en PascalCase
- Nommage des composables en camelCase préfixé par `use`
