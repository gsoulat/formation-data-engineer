# Vue Router 4 — Navigation SPA

## Qu'est-ce que Vue Router ?

Vue Router est le routeur officiel de Vue.js. Dans une Single Page Application (SPA), il n'y a pas de rechargement de page entre les vues : Vue Router gère la navigation côté client en synchronisant l'URL du navigateur avec les composants affichés.

## Installation et configuration

```bash
npm install vue-router@4
# ou si créé avec npm create vue@latest, Vue Router est déjà configuré
```

### Configuration de base

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

// Importation statique (le composant est chargé immédiatement)
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  // createWebHistory → URLs propres (/about)
  // createWebHashHistory → URLs avec hash (/#/about)
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // Lazy loading — le composant n'est chargé que quand la route est visitée
      component: () => import('@/views/AboutView.vue'),
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('@/views/UsersView.vue'),
    },
    {
      path: '/users/:id',
      name: 'user-detail',
      component: () => import('@/views/UserDetailView.vue'),
      // Props automatiques — :id est passé comme prop au composant
      props: true,
    },
    // Route 404 — attrape toutes les URLs non définies
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],

  // Comportement du scroll lors de la navigation
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      // Retour au scroll précédent (bouton Précédent du navigateur)
      return savedPosition
    }
    if (to.hash) {
      // Navigation vers une ancre
      return { el: to.hash, behavior: 'smooth' }
    }
    // Retour en haut de la page
    return { top: 0, behavior: 'smooth' }
  },
})

export default router
```

### Enregistrer le router dans l'application

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router) // Doit être après Pinia
app.mount('#app')
```

## RouterView et RouterLink

```vue
<!-- src/App.vue — structure de base avec navigation -->
<template>
  <nav class="navbar">
    <!-- RouterLink génère une balise <a> qui ne recharge pas la page -->
    <RouterLink to="/">Accueil</RouterLink>

    <!-- Navigation par nom de route (recommandé — robuste aux changements d'URL) -->
    <RouterLink :to="{ name: 'about' }">À propos</RouterLink>
    <RouterLink :to="{ name: 'users' }">Utilisateurs</RouterLink>

    <!-- active-class est ajoutée automatiquement sur le lien actif -->
    <!-- exact-active-class seulement si la route correspond exactement -->
  </nav>

  <main>
    <!-- RouterView affiche le composant de la route active -->
    <!-- Transition optionnelle autour de RouterView -->
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
</template>

<style>
/* Classe appliquée automatiquement sur les liens actifs */
.router-link-active {
  font-weight: bold;
  color: #42b883;
}

/* Transition entre les pages */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur avec l'application ouverte, cliquer sur les liens de navigation
> **Expliquer :** Montrer que l'URL change dans la barre d'adresse SANS rechargement de la page (onglet Network de DevTools vide). Montrer la classe `router-link-active` qui s'applique sur le lien actif dans l'inspecteur d'éléments. Utiliser aussi les boutons Précédent/Suivant du navigateur pour montrer l'historique.
---

## Paramètres de route

### Paramètres dynamiques `:param`

```typescript
// Dans le router
{
  path: '/produits/:categorie/:id',
  name: 'produit-detail',
  component: () => import('@/views/ProduitDetailView.vue'),
  props: true,
}
```

```vue
<!-- src/views/ProduitDetailView.vue -->
<template>
  <div>
    <h1>Produit {{ id }} — {{ categorie }}</h1>
    <p>Route complète : {{ $route.path }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

// Option 1 : via useRoute()
const route = useRoute()
const id = computed(() => route.params.id)
const categorie = computed(() => route.params.categorie)

// Option 2 : via props (si props: true dans la route) — plus propre
// defineProps<{ id: string; categorie: string }>()
</script>
```

### Navigation programmatique

```vue
<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Navigation programmatique
function allerAAccueil() {
  router.push('/')
}

function allerAUtilisateur(id: number) {
  router.push({ name: 'user-detail', params: { id } })
}

function allerAResultatsRecherche(terme: string) {
  router.push({
    name: 'recherche',
    query: { q: terme, page: '1' }, // ajoute ?q=terme&page=1
  })
}

// Lire les query params
const page = computed(() => Number(route.query.page) || 1)
const terme = computed(() => route.query.q as string || '')

// Remplacer sans ajouter à l'historique
function remplacerRoute() {
  router.replace({ name: 'home' }) // pas de Précédent disponible
}

// Naviguer dans l'historique
function retour() {
  router.back()
  // ou router.go(-1)
}

function avancer() {
  router.forward()
  // ou router.go(1)
}
</script>
```

## Routes imbriquées (Nested Routes)

```typescript
// src/router/index.ts — routes imbriquées
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/layouts/DashboardLayout.vue'),
    // children définit les sous-routes
    children: [
      {
        path: '',           // /dashboard (sans slash supplémentaire)
        name: 'dashboard',
        component: () => import('@/views/DashboardHome.vue'),
      },
      {
        path: 'profil',     // /dashboard/profil
        name: 'dashboard-profil',
        component: () => import('@/views/DashboardProfil.vue'),
      },
      {
        path: 'parametres', // /dashboard/parametres
        name: 'dashboard-parametres',
        component: () => import('@/views/DashboardParametres.vue'),
      },
    ],
  },
]
```

```vue
<!-- src/layouts/DashboardLayout.vue — layout parent -->
<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <nav>
        <RouterLink :to="{ name: 'dashboard' }">Tableau de bord</RouterLink>
        <RouterLink :to="{ name: 'dashboard-profil' }">Mon profil</RouterLink>
        <RouterLink :to="{ name: 'dashboard-parametres' }">Paramètres</RouterLink>
      </nav>
    </aside>

    <main class="contenu">
      <!-- RouterView imbriqué — affiche les composants enfants -->
      <RouterView />
    </main>
  </div>
</template>
```

## Navigation Guards (Gardes de navigation)

Les navigation guards permettent de contrôler les accès aux routes.

### Guard global — `router.beforeEach`

```typescript
// src/router/index.ts
import { useAuthStore } from '@/stores/auth'

const router = createRouter({ ... })

// Exécuté avant CHAQUE navigation
router.beforeEach(async (to, from) => {
  const authStore = useAuthStore()

  // Vérifier si la route nécessite une authentification
  const requiresAuth = to.meta.requiresAuth as boolean

  if (requiresAuth && !authStore.isLoggedIn) {
    // Rediriger vers la page de connexion
    // Mémoriser la route demandée pour y revenir après connexion
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  // Vérification des rôles
  const requiredRole = to.meta.role as string
  if (requiredRole && !authStore.hasRole(requiredRole)) {
    return { name: 'forbidden' }
  }

  // Retourner true ou rien pour laisser passer la navigation
  return true
})

// Exécuté après chaque navigation (pour analytics, etc.)
router.afterEach((to, from) => {
  // Google Analytics, Matomo, etc.
  document.title = to.meta.title as string || 'Mon Application'
})
```

### Métadonnées de route (`meta`)

```typescript
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'Accueil',
      requiresAuth: false,
    },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminView.vue'),
    meta: {
      title: 'Administration',
      requiresAuth: true,
      role: 'admin',    // nécessite le rôle admin
    },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      title: 'Tableau de bord',
      requiresAuth: true,
      role: 'user',
    },
  },
]

// Typage des méta-données avec TypeScript
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    role?: 'admin' | 'user' | 'guest'
  }
}
```

### Guard de composant — `onBeforeRouteLeave`

```vue
<!-- Empêcher la perte de données non sauvegardées -->
<script setup lang="ts">
import { ref } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

const formModifie = ref(false)

// Avant de quitter ce composant
onBeforeRouteLeave((to, from) => {
  if (formModifie.value) {
    const confirmer = confirm(
      'Vous avez des modifications non sauvegardées. Quitter quand même ?'
    )
    if (!confirmer) return false // Annuler la navigation
  }
})

// Avant une navigation vers le MÊME composant avec des params différents
// (ex: /users/1 → /users/2 — le composant est réutilisé)
onBeforeRouteUpdate(async (to, from) => {
  // Recharger les données avec le nouvel ID
  await chargerUtilisateur(to.params.id as string)
})
</script>
```

## Lazy Loading et Code Splitting

```typescript
// Sans lazy loading — tout chargé au démarrage
import DashboardView from '@/views/DashboardView.vue'
import ReportsView from '@/views/ReportsView.vue'

// Avec lazy loading — chargé à la demande
const DashboardView = () => import('@/views/DashboardView.vue')
const ReportsView = () => import('@/views/ReportsView.vue')

// Avec nommage du chunk (pour l'organisation du build)
const AdminView = () => import(/* webpackChunkName: "admin" */ '@/views/AdminView.vue')

// Grouper plusieurs routes dans le même chunk
const AdminUsers = () => import(/* webpackChunkName: "admin" */ '@/views/admin/UsersView.vue')
const AdminSettings = () => import(/* webpackChunkName: "admin" */ '@/views/admin/SettingsView.vue')
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de Chrome DevTools pendant la navigation vers une route lazy-loadée
> **Expliquer :** Naviguer vers une page avec lazy loading et montrer dans l'onglet Network qu'un nouveau fichier JavaScript est chargé à ce moment précis. Montrer que la première fois le fichier est téléchargé, la deuxième fois il vient du cache (from disk cache). C'est le code splitting en action.
---

## Routes avec paramètres optionnels et regex

```typescript
const routes = [
  // Paramètre optionnel avec ?
  {
    path: '/users/:id?',
    component: () => import('@/views/UserView.vue'),
    // Correspond à /users et /users/42
  },

  // Paramètre avec contrainte regex
  {
    path: '/articles/:id(\\d+)',
    // :id(\\d+) → id doit être un nombre
    component: () => import('@/views/ArticleView.vue'),
  },

  // Paramètre répété (tableau)
  {
    path: '/tags/:tags+',
    // /tags/vue /tags/vue/3/composition
    component: () => import('@/views/TagsView.vue'),
  },

  // Toute sous-URL d'un chemin
  {
    path: '/legacy/:path(.*)',
    redirect: (to) => {
      // Redirection dynamique
      return '/nouveau/' + to.params.path
    },
  },
]
```

## Exemple complet — Application avec auth

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Routes publiques
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue') },

    // Routes protégées (authentification requise)
    {
      path: '/dashboard',
      component: () => import('@/layouts/AuthLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'profil', name: 'profil', component: () => import('@/views/ProfilView.vue') },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/AdminView.vue'),
          meta: { requiresAuth: true, role: 'admin' },
        },
      ],
    },

    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})

// Guard d'authentification global
router.beforeEach((to) => {
  const token = localStorage.getItem('auth_token')
  const isLoggedIn = !!token

  if (to.meta.requiresAuth && !isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Éviter la boucle de redirection
  if (to.name === 'login' && isLoggedIn) {
    return { name: 'dashboard' }
  }
})

export default router
```

## Résumé

| Concept | Description | API |
|---|---|---|
| `createRouter` | Créer le routeur | `createRouter({ history, routes })` |
| `RouterView` | Afficher la vue active | `<RouterView />` |
| `RouterLink` | Lien de navigation | `<RouterLink :to="{ name }" />` |
| `useRoute` | Lire la route actuelle | `route.params`, `route.query` |
| `useRouter` | Navigation programmatique | `router.push()`, `router.replace()` |
| Navigation guards | Contrôle d'accès | `router.beforeEach()` |
| Lazy loading | Chargement différé | `() => import('./View.vue')` |
| Routes imbriquées | Layouts partagés | `children: [...]` |

**Prochaine étape :** Pinia — gestion d'état global →
