# Exercice 2 — Dashboard avec API REST

## Objectif

Construire un dashboard complet avec appels API, Vue Router, Pinia, et un design professionnel. Cet exercice simule un projet professionnel réel.

**Durée estimée :** 3h à 4h

## API utilisée

On utilise [JSONPlaceholder](https://jsonplaceholder.typicode.com/) — une API REST de test gratuite.

Endpoints disponibles :
- `GET /users` — liste des utilisateurs
- `GET /users/:id` — un utilisateur
- `GET /posts` — liste des posts
- `GET /posts/:id` — un post
- `GET /posts/:id/comments` — commentaires d'un post
- `GET /albums` — liste des albums
- `GET /todos` — liste des todos

## Fonctionnalités à implémenter

- [ ] Page d'accueil avec statistiques globales (nb users, posts, etc.)
- [ ] Liste des utilisateurs avec recherche
- [ ] Page détail d'un utilisateur avec ses posts
- [ ] Liste des posts avec pagination côté client
- [ ] Page détail d'un post avec commentaires
- [ ] Navigation avec Vue Router
- [ ] State management avec Pinia (cache des données)
- [ ] Gestion des états loading / error
- [ ] Composant réutilisable pour les cartes statistiques

## Structure du projet

```
src/
├── components/
│   ├── ui/
│   │   ├── CarteStats.vue      # Carte statistique réutilisable
│   │   ├── ChargementSpinner.vue
│   │   ├── MessageErreur.vue
│   │   └── BagrePagination.vue
│   ├── layout/
│   │   ├── AppNavbar.vue
│   │   └── AppSidebar.vue
│   ├── users/
│   │   ├── UserCard.vue
│   │   └── UsersList.vue
│   └── posts/
│       ├── PostCard.vue
│       └── PostsList.vue
├── views/
│   ├── DashboardView.vue       # Page d'accueil avec stats
│   ├── UsersView.vue           # Liste des utilisateurs
│   ├── UserDetailView.vue      # Profil + posts d'un user
│   ├── PostsView.vue           # Liste des posts
│   └── PostDetailView.vue      # Post + commentaires
├── stores/
│   ├── users.ts
│   └── posts.ts
├── composables/
│   └── useFetch.ts
├── types/
│   └── jsonplaceholder.ts      # Types de l'API
└── router/
    └── index.ts
```

## Étape 1 — Types de l'API

```typescript
// src/types/jsonplaceholder.ts
export interface User {
  id: number
  name: string
  username: string
  email: string
  address: {
    street: string
    suite: string
    city: string
    zipcode: string
    geo: { lat: string; lng: string }
  }
  phone: string
  website: string
  company: {
    name: string
    catchPhrase: string
    bs: string
  }
}

export interface Post {
  id: number
  userId: number
  title: string
  body: string
}

export interface Comment {
  id: number
  postId: number
  name: string
  email: string
  body: string
}

export interface Todo {
  id: number
  userId: number
  title: string
  completed: boolean
}
```

## Étape 2 — Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { title: 'Tableau de bord' },
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('@/views/UsersView.vue'),
      meta: { title: 'Utilisateurs' },
    },
    {
      path: '/users/:id',
      name: 'user-detail',
      component: () => import('@/views/UserDetailView.vue'),
      props: true,
      meta: { title: 'Profil utilisateur' },
    },
    {
      path: '/posts',
      name: 'posts',
      component: () => import('@/views/PostsView.vue'),
      meta: { title: 'Articles' },
    },
    {
      path: '/posts/:id',
      name: 'post-detail',
      component: () => import('@/views/PostDetailView.vue'),
      props: true,
      meta: { title: 'Article' },
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
```

## Étape 3 — Stores

```typescript
// src/stores/users.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Post, Todo } from '@/types/jsonplaceholder'

const BASE_URL = 'https://jsonplaceholder.typicode.com'

export const useUsersStore = defineStore('users', () => {
  // Cache — stocker les données pour éviter les requêtes répétées
  const usersCache = ref<Map<number, User>>(new Map())
  const postsParUser = ref<Map<number, Post[]>>(new Map())
  const todosParUser = ref<Map<number, Todo[]>>(new Map())
  const chargement = ref(false)
  const erreur = ref<string | null>(null)

  const users = computed(() => Array.from(usersCache.value.values()))

  async function chargerTous(): Promise<void> {
    if (usersCache.value.size > 0) return // Déjà en cache

    chargement.value = true
    erreur.value = null
    try {
      const response = await fetch(`${BASE_URL}/users`)
      const data: User[] = await response.json()
      data.forEach((u) => usersCache.value.set(u.id, u))
    } catch (e) {
      erreur.value = 'Impossible de charger les utilisateurs'
    } finally {
      chargement.value = false
    }
  }

  async function chargerParId(id: number): Promise<User | null> {
    if (usersCache.value.has(id)) return usersCache.value.get(id)!

    chargement.value = true
    erreur.value = null
    try {
      const response = await fetch(`${BASE_URL}/users/${id}`)
      const data: User = await response.json()
      usersCache.value.set(data.id, data)
      return data
    } catch (e) {
      erreur.value = `Utilisateur ${id} introuvable`
      return null
    } finally {
      chargement.value = false
    }
  }

  async function chargerPostsUser(userId: number): Promise<Post[]> {
    if (postsParUser.value.has(userId)) return postsParUser.value.get(userId)!

    const response = await fetch(`${BASE_URL}/users/${userId}/posts`)
    const data: Post[] = await response.json()
    postsParUser.value.set(userId, data)
    return data
  }

  function getUser(id: number): User | undefined {
    return usersCache.value.get(id)
  }

  return {
    users,
    chargement,
    erreur,
    chargerTous,
    chargerParId,
    chargerPostsUser,
    getUser,
  }
})
```

## Étape 4 — Composant CarteStats

```vue
<!-- src/components/ui/CarteStats.vue -->
<template>
  <div class="carte-stats" :class="`carte-stats--${couleur}`">
    <div class="carte-stats__icone">{{ icone }}</div>
    <div class="carte-stats__contenu">
      <div class="carte-stats__valeur">
        <span v-if="chargement" class="skeleton">—</span>
        <span v-else>{{ valeurFormatee }}</span>
      </div>
      <div class="carte-stats__label">{{ label }}</div>
    </div>
    <div class="carte-stats__tendance" v-if="tendance">
      <span :class="tendance > 0 ? 'hausse' : 'baisse'">
        {{ tendance > 0 ? '↑' : '↓' }} {{ Math.abs(tendance) }}%
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    valeur: number
    label: string
    icone?: string
    couleur?: 'bleu' | 'vert' | 'orange' | 'rouge'
    tendance?: number
    chargement?: boolean
  }>(),
  {
    icone: '📊',
    couleur: 'bleu',
    chargement: false,
  }
)

const valeurFormatee = computed(() =>
  new Intl.NumberFormat('fr-FR').format(props.valeur)
)
</script>

<style scoped>
.carte-stats {
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.carte-stats--bleu { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.carte-stats--vert { background: linear-gradient(135deg, #56ab2f, #a8e063); color: white; }
.carte-stats--orange { background: linear-gradient(135deg, #f7971e, #ffd200); color: white; }
.carte-stats--rouge { background: linear-gradient(135deg, #f953c6, #b91d73); color: white; }
.carte-stats__icone { font-size: 2.5rem; }
.carte-stats__valeur { font-size: 2rem; font-weight: 700; }
.carte-stats__label { font-size: 0.9rem; opacity: 0.9; }
</style>
```

## Étape 5 — Vue DashboardView

```vue
<!-- src/views/DashboardView.vue -->
<template>
  <div class="dashboard">
    <h1>Tableau de bord</h1>

    <div class="stats-grid">
      <CarteStats
        :valeur="usersStore.users.length"
        label="Utilisateurs"
        icone="👥"
        couleur="bleu"
        :chargement="usersStore.chargement"
      />
      <CarteStats
        :valeur="postsStore.posts.length"
        label="Articles"
        icone="📝"
        couleur="vert"
        :chargement="postsStore.chargement"
      />
      <CarteStats
        :valeur="totalCommentaires"
        label="Commentaires"
        icone="💬"
        couleur="orange"
      />
      <CarteStats
        :valeur="tauxCompletion"
        label="Taux completion %"
        icone="✅"
        couleur="rouge"
      />
    </div>

    <!-- Posts récents -->
    <section class="section">
      <div class="section-header">
        <h2>Articles récents</h2>
        <RouterLink :to="{ name: 'posts' }">Voir tous →</RouterLink>
      </div>
      <div class="posts-recents">
        <div
          v-for="post in postsRecents"
          :key="post.id"
          class="post-mini"
          @click="$router.push({ name: 'post-detail', params: { id: post.id } })"
        >
          <h4>{{ post.title }}</h4>
          <p>{{ post.body.substring(0, 80) }}...</p>
        </div>
      </div>
    </section>

    <!-- Top utilisateurs -->
    <section class="section">
      <div class="section-header">
        <h2>Utilisateurs actifs</h2>
        <RouterLink :to="{ name: 'users' }">Voir tous →</RouterLink>
      </div>
      <div class="users-grid">
        <div
          v-for="user in usersStore.users.slice(0, 6)"
          :key="user.id"
          class="user-mini"
          @click="$router.push({ name: 'user-detail', params: { id: user.id } })"
        >
          <div class="avatar-initiales">
            {{ user.name.split(' ').map(n => n[0]).join('').substring(0, 2) }}
          </div>
          <div>
            <strong>{{ user.name }}</strong>
            <small>{{ user.email }}</small>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'
import { usePostsStore } from '@/stores/posts'
import CarteStats from '@/components/ui/CarteStats.vue'

const usersStore = useUsersStore()
const postsStore = usePostsStore()

const postsRecents = computed(() => postsStore.posts.slice(0, 5))
const totalCommentaires = computed(() => postsStore.posts.length * 5) // estimé
const tauxCompletion = computed(() => 68) // simulé

onMounted(async () => {
  await Promise.all([
    usersStore.chargerTous(),
    postsStore.chargerTous(),
  ])
})
</script>
```

## Étape 6 — Pagination côté client

```typescript
// src/composables/usePagination.ts
import { ref, computed } from 'vue'

export function usePagination<T>(items: ComputedRef<T[]>, parPage = 10) {
  const pageCourante = ref(1)

  const totalPages = computed(() => Math.ceil(items.value.length / parPage))

  const itemsPage = computed(() => {
    const debut = (pageCourante.value - 1) * parPage
    return items.value.slice(debut, debut + parPage)
  })

  function allerPage(page: number) {
    pageCourante.value = Math.max(1, Math.min(page, totalPages.value))
  }

  function precedent() { allerPage(pageCourante.value - 1) }
  function suivant() { allerPage(pageCourante.value + 1) }

  const pagesVisibles = computed(() => {
    const pages = []
    const debut = Math.max(1, pageCourante.value - 2)
    const fin = Math.min(totalPages.value, pageCourante.value + 2)
    for (let i = debut; i <= fin; i++) pages.push(i)
    return pages
  })

  return {
    pageCourante,
    totalPages,
    itemsPage,
    allerPage,
    precedent,
    suivant,
    pagesVisibles,
  }
}
```

## Critères d'évaluation

| Fonctionnalité | Points |
|---|---|
| Navigation Vue Router (5 routes) | 3 |
| Appels API avec états loading/error | 3 |
| Store Pinia avec cache | 3 |
| Composant CarteStats réutilisable | 2 |
| Pagination côté client | 2 |
| Page détail utilisateur avec ses posts | 2 |
| Page détail post avec commentaires | 2 |
| TypeScript (pas de any) | 2 |
| Design cohérent | 1 |
| **Total** | **20** |

## Défi bonus

Ajouter une fonctionnalité de recherche globale qui cherche simultanément dans les utilisateurs et les posts, avec mise en avant des termes trouvés.
