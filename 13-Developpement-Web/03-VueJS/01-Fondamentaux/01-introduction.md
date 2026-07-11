# Vue 3 — Introduction et mise en place

## Qu'est-ce que Vue.js ?

Vue.js est un framework JavaScript progressif pour construire des interfaces utilisateur. Créé par Evan You en 2014, il est conçu pour être adopté de manière incrémentale : on peut l'utiliser pour enrichir une page HTML existante ou construire une Single Page Application (SPA) complète.

**Vue 3** est la version majeure actuelle, sortie en septembre 2020. Elle apporte :

- La **Composition API** (nouvelle façon d'écrire la logique)
- De meilleures performances (Virtual DOM réécrit)
- Un meilleur support TypeScript natif
- Les **Composants à Fragment** (plusieurs nœuds racine)
- `<Teleport>` et `<Suspense>` (composants built-in avancés)

## Pourquoi Vue 3 ?

### Points forts

- **Courbe d'apprentissage douce** — la syntaxe de template est proche du HTML natif
- **Réactivité fine** — le système de réactivité est précis et performant
- **Taille légère** — environ 34 Ko minifié+gzippé
- **Documentation excellente** — l'une des meilleures du monde JavaScript
- **Flexibilité** — Options API pour les débutants, Composition API pour les projets complexes

### Cas d'usage typiques

- Applications web interactives (SPAs)
- Intégration progressive dans des sites existants
- Applications mobiles avec Ionic ou Capacitor
- Applications desktop avec Electron + Vue
- Micro-frontends

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir https://vuejs.org dans le navigateur et montrer la page d'accueil officielle
> **Expliquer :** Naviguer dans la documentation, montrer le "Quick Start", insister sur le fait que Vue a une des meilleures docs du monde JavaScript. Montrer aussi le playground interactif en ligne (https://play.vuejs.org)
---

## Options API vs Composition API

Vue 3 propose deux façons d'écrire un composant. Il est essentiel de comprendre la différence.

### Options API — l'ancienne façon (Vue 2 style)

```vue
<!-- CounterOptions.vue -->
<template>
  <div>
    <p>Compteur : {{ count }}</p>
    <p>Double : {{ double }}</p>
    <button @click="increment">Incrémenter</button>
    <button @click="reset">Réinitialiser</button>
  </div>
</template>

<script>
export default {
  name: 'CounterOptions',

  // État local
  data() {
    return {
      count: 0,
    }
  },

  // Propriétés calculées
  computed: {
    double() {
      return this.count * 2
    },
  },

  // Méthodes
  methods: {
    increment() {
      this.count++
    },
    reset() {
      this.count = 0
    },
  },

  // Cycle de vie
  mounted() {
    console.log('Composant monté, count =', this.count)
  },
}
</script>
```

### Composition API — la façon moderne (Vue 3)

```vue
<!-- CounterComposition.vue -->
<template>
  <div>
    <p>Compteur : {{ count }}</p>
    <p>Double : {{ double }}</p>
    <button @click="increment">Incrémenter</button>
    <button @click="reset">Réinitialiser</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// État local
const count = ref(0)

// Propriété calculée
const double = computed(() => count.value * 2)

// Méthodes
function increment() {
  count.value++
}

function reset() {
  count.value = 0
}

// Cycle de vie
onMounted(() => {
  console.log('Composant monté, count =', count.value)
})
</script>
```

### Quelle API choisir ?

| Critère | Options API | Composition API |
|---|---|---|
| Lisibilité pour débutants | Meilleure | Moins évidente au début |
| Organisation du code | Par type (data/methods/computed) | Par fonctionnalité |
| Réutilisabilité | Mixins (problématiques) | Composables (élégants) |
| TypeScript | Support limité | Support excellent |
| Performances | Identiques | Identiques |
| Tendance 2024+ | Legacy, toujours supporté | Recommandé |

**Dans ce cours, nous utilisons la Composition API avec `<script setup>`**, qui est la syntaxe recommandée pour tout nouveau projet Vue 3.

> **Note :** Les deux APIs sont entièrement compatibles — on peut les mélanger dans un même projet, voire dans un même composant.

## Créer un projet Vue 3 avec Vite

### Pourquoi Vite ?

Vite est l'outil de build officiel recommandé par l'équipe Vue. Il offre :

- **Démarrage instantané** — pas de bundling à froid, utilise les ES modules natifs
- **Hot Module Replacement (HMR)** ultra-rapide
- **Build optimisé** avec Rollup pour la production
- **Configuration minimale** — fonctionne out-of-the-box

### Création du projet

```bash
# Option 1 — Template Vue simple (JavaScript)
npm create vite@latest mon-app-vue -- --template vue

# Option 2 — Template Vue avec TypeScript (recommandé)
npm create vite@latest mon-app-vue -- --template vue-ts

# Option 3 — Utiliser create-vue (plus d'options)
npm create vue@latest
# Interactif : choisir TypeScript, Vue Router, Pinia, ESLint...
```

### Résultat de `npm create vue@latest`

```
✔ Project name: … mon-app-vue
✔ Add TypeScript? … Yes
✔ Add JSX Support? … No
✔ Add Vue Router for Single Page Application development? … Yes
✔ Add Pinia for state management? … Yes
✔ Add Vitest for Unit Testing? … No
✔ Add an End-to-End Testing Solution? … No
✔ Add ESLint for code quality? … Yes
✔ Add Prettier for code formatting? … Yes
```

### Lancer le projet

```bash
cd mon-app-vue
npm install
npm run dev
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec l'exécution de `npm create vue@latest`, répondre aux questions de manière interactive, puis `npm install` et `npm run dev`
> **Expliquer :** Montrer le serveur qui démarre sur http://localhost:5173, ouvrir dans le navigateur. Insister sur la vitesse de démarrage comparée à webpack. Montrer le message "VITE vX.X.X  ready" dans le terminal.
---

## Structure d'un projet Vue 3

```
mon-app-vue/
├── public/                  # Fichiers statiques servis tels quels
│   └── favicon.ico
├── src/
│   ├── assets/              # Images, CSS globaux
│   │   └── main.css
│   ├── components/          # Composants réutilisables
│   │   └── HelloWorld.vue
│   ├── views/               # Pages (utilisées avec Vue Router)
│   │   ├── HomeView.vue
│   │   └── AboutView.vue
│   ├── router/              # Configuration Vue Router
│   │   └── index.ts
│   ├── stores/              # Stores Pinia
│   │   └── counter.ts
│   ├── App.vue              # Composant racine
│   └── main.ts              # Point d'entrée de l'application
├── index.html               # Template HTML principal
├── package.json
├── tsconfig.json            # Configuration TypeScript
└── vite.config.ts           # Configuration Vite
```

### Le fichier `main.ts`

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())  // Activer Pinia
app.use(router)          // Activer Vue Router

app.mount('#app')        // Monter sur <div id="app"> dans index.html
```

### Le fichier `App.vue` (composant racine)

```vue
<!-- src/App.vue -->
<template>
  <!-- RouterView affiche le composant de la route active -->
  <header>
    <nav>
      <RouterLink to="/">Accueil</RouterLink>
      <RouterLink to="/about">À propos</RouterLink>
    </nav>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
header {
  background-color: #42b883;
  padding: 1rem;
}

nav a {
  color: white;
  text-decoration: none;
  margin: 0 1rem;
}
</style>
```

### Anatomie d'un fichier `.vue`

Un fichier Single File Component (SFC) Vue a trois sections :

```vue
<!-- MonComposant.vue -->

<!-- 1. TEMPLATE — La vue (HTML enrichi) -->
<template>
  <div class="mon-composant">
    <h1>{{ titre }}</h1>
  </div>
</template>

<!-- 2. SCRIPT — La logique -->
<script setup lang="ts">
// Tout le code JavaScript/TypeScript ici
const titre = 'Bonjour Vue 3 !'
</script>

<!-- 3. STYLE — Le CSS (scoped = limité à ce composant) -->
<style scoped>
.mon-composant {
  color: #42b883;
}
</style>
```

## Le système de réactivité en bref

Vue 3 utilise des **Proxies JavaScript** pour détecter automatiquement les changements de données et mettre à jour le DOM :

```vue
<template>
  <!-- Le DOM se met à jour automatiquement quand `message` change -->
  <p>{{ message }}</p>
  <input v-model="message" />
</template>

<script setup>
import { ref } from 'vue'

// ref() rend la valeur "réactive"
const message = ref('Bonjour Vue !')

// Quand on modifie message.value, Vue re-render automatiquement
setTimeout(() => {
  message.value = 'Message mis à jour après 2 secondes'
}, 2000)
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Modifier le message dans `src/App.vue` ou dans un composant pendant que le navigateur est ouvert
> **Expliquer :** Montrer le Hot Module Replacement (HMR) en action — la page se met à jour immédiatement sans rechargement complet, l'état est préservé. C'est une des grandes forces de Vite + Vue.
---

## Configuration Vite avancée

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      // Permet d'importer avec '@/components/...' au lieu de '../../components/...'
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    port: 3000,          // Changer le port de dev
    proxy: {
      // Proxy les appels API vers le backend pour éviter les problèmes CORS en dev
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## Extensions VSCode recommandées

```json
// .vscode/extensions.json
{
  "recommendations": [
    "Vue.volar",              // Extension officielle Vue (Volar)
    "Vue.vscode-typescript-vue-plugin",  // Support TypeScript dans .vue
    "esbenp.prettier-vscode", // Formatage automatique
    "dbaeumer.vscode-eslint"  // Linting
  ]
}
```

> **Important :** Si vous avez l'ancienne extension **Vetur** installée, désactivez-la. Elle est incompatible avec Volar (l'extension officielle Vue 3).

## Résumé

- Vue 3 est un framework progressif, léger et performant
- La **Composition API** avec `<script setup>` est la façon moderne d'écrire des composants
- **Vite** remplace webpack pour un développement ultra-rapide
- Un fichier `.vue` contient `<template>`, `<script setup>` et `<style scoped>`
- Le système de réactivité de Vue met à jour le DOM automatiquement

**Prochaine étape :** La syntaxe de template et les directives Vue →
