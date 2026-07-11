# Vue 3 + TypeScript

## Pourquoi TypeScript avec Vue 3 ?

Vue 3 a été réécrit entièrement en TypeScript, ce qui lui confère un support natif exceptionnel. TypeScript apporte :

- **Autocomplétion** précise dans VSCode
- **Détection d'erreurs** à la compilation (avant le navigateur)
- **Refactoring sûr** — renommer une prop met à jour tous les usages
- **Documentation vivante** — les types servent de documentation
- **Maintenabilité** accrue sur les grands projets

## Configuration du projet

```bash
# Créer un projet Vue 3 + TypeScript
npm create vue@latest
# Répondre "Yes" à "Add TypeScript?"

# Ou avec Vite directement
npm create vite@latest mon-app -- --template vue-ts
```

```json
// tsconfig.json généré par create-vue
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "include": ["env.d.ts", "src/**/*", "src/**/*.vue"],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Typage des composants avec `<script setup lang="ts">`

### `defineProps` avec TypeScript

```vue
<!-- src/components/ProfilUtilisateur.vue -->
<template>
  <div class="profil">
    <img :src="avatar ?? '/images/default.png'" :alt="`Avatar de ${prenom}`" />
    <h2>{{ prenom }} {{ nom }}</h2>
    <p class="role">{{ role }}</p>
    <p v-if="bio" class="bio">{{ bio }}</p>
    <div class="stats">
      <span>{{ score }} pts</span>
      <span>Inscrit le {{ dateInscriptionFormatee }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Syntaxe TypeScript pour defineProps — SANS valeur de retour
// Les types sont directement dans le générique
interface Props {
  prenom: string
  nom: string
  role: 'admin' | 'moderateur' | 'utilisateur'
  score: number
  avatar?: string          // ? = optionnel
  bio?: string | null
  dateInscription: string
}

const props = defineProps<Props>()

// Valeurs par défaut avec withDefaults
// ATTENTION : withDefaults est nécessaire car les défauts ne peuvent pas
// être déclarés directement dans l'interface TypeScript
const propsAvecDefauts = withDefaults(defineProps<Props>(), {
  role: 'utilisateur',
  score: 0,
  avatar: undefined,
  bio: null,
})

const dateInscriptionFormatee = computed(() =>
  new Date(props.dateInscription).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
)
</script>
```

### `defineEmits` avec TypeScript

```vue
<script setup lang="ts">
import { ref } from 'vue'

// Typage des événements émis
const emit = defineEmits<{
  // Syntaxe: nomEvenement: [type1, type2, ...]
  update: [valeur: string]
  supprimer: [id: number]
  enregistrer: [donnees: { nom: string; age: number }]
  annuler: []  // événement sans payload
}>()

const saisie = ref('')

function enregistrer() {
  emit('enregistrer', { nom: saisie.value, age: 25 })
}

// emit('update', 42) // ❌ TypeScript erreur — string attendu
emit('update', 'nouvelle valeur') // ✅
</script>
```

## Typage des composables

```typescript
// src/composables/useApi.ts
import { ref, shallowRef } from 'vue'

// Interface générique pour les réponses paginées
interface ReponsePagee<T> {
  data: T[]
  total: number
  page: number
  perPage: number
  totalPages: number
}

// Composable générique typé
export function useApiPaginee<T>(endpoint: string) {
  const items = shallowRef<T[]>([])
  const chargement = ref(false)
  const erreur = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    perPage: 10,
    total: 0,
    totalPages: 0,
  })

  async function charger(page = 1, filtres?: Record<string, string>) {
    chargement.value = true
    erreur.value = null

    try {
      const params = new URLSearchParams({
        page: String(page),
        per_page: String(pagination.value.perPage),
        ...filtres,
      })

      const response = await fetch(`${endpoint}?${params}`)
      if (!response.ok) throw new Error(`Erreur ${response.status}`)

      const data: ReponsePagee<T> = await response.json()
      items.value = data.data
      pagination.value = {
        page: data.page,
        perPage: data.perPage,
        total: data.total,
        totalPages: data.totalPages,
      }
    } catch (e) {
      erreur.value = e instanceof Error ? e.message : 'Erreur inconnue'
    } finally {
      chargement.value = false
    }
  }

  return { items, chargement, erreur, pagination, charger }
}
```

```vue
<!-- Utilisation typée du composable -->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useApiPaginee } from '@/composables/useApi'

interface Produit {
  id: number
  nom: string
  prix: number
  stock: number
  categorie: string
}

const {
  items: produits,
  chargement,
  erreur,
  pagination,
  charger,
} = useApiPaginee<Produit>('/api/produits')

onMounted(() => charger(1))
</script>
```

## `useTemplateRef` — Template refs typées

Depuis Vue 3.5, `useTemplateRef` offre un typage plus précis que la méthode `ref(null)` :

```vue
<template>
  <div>
    <!-- L'attribut ref doit correspondre au nom passé à useTemplateRef -->
    <input ref="champEmail" type="email" v-model="email" />
    <canvas ref="monCanvas" width="400" height="200"></canvas>
    <MonComposant ref="monComposant" />
  </div>
</template>

<script setup lang="ts">
import { useTemplateRef, onMounted } from 'vue'
import MonComposant from './MonComposant.vue'

// Type automatiquement inféré depuis l'élément DOM
const champEmail = useTemplateRef<HTMLInputElement>('champEmail')
const monCanvas = useTemplateRef<HTMLCanvasElement>('monCanvas')

// Type inféré depuis le composant (accès aux méthodes exposées)
const monComposant = useTemplateRef<InstanceType<typeof MonComposant>>('monComposant')

onMounted(() => {
  // TypeScript sait que c'est un HTMLInputElement
  champEmail.value?.focus()
  champEmail.value?.select()

  // TypeScript connaît les méthodes de MonComposant
  monComposant.value?.methodeExposee()

  // Canvas API typée correctement
  const ctx = monCanvas.value?.getContext('2d')
  ctx?.fillRect(0, 0, 400, 200)
})
</script>
```

## Types utilitaires pour les stores Pinia

```typescript
// src/stores/utilisateurs.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Définir les types dans le même fichier ou dans src/types/
export interface Utilisateur {
  id: number
  email: string
  prenom: string
  nom: string
  role: RoleUtilisateur
  createdAt: string
  updatedAt: string
}

export type RoleUtilisateur = 'admin' | 'moderateur' | 'utilisateur'

export interface CreateUtilisateurDTO {
  email: string
  prenom: string
  nom: string
  password: string
  role?: RoleUtilisateur
}

export interface UpdateUtilisateurDTO extends Partial<Omit<CreateUtilisateurDTO, 'password'>> {
  id: number
}

export const useUtilisateursStore = defineStore('utilisateurs', () => {
  const utilisateurs = ref<Utilisateur[]>([])
  const utilisateurActif = ref<Utilisateur | null>(null)
  const chargement = ref(false)
  const erreurs = ref<Record<string, string>>({})

  const parRole = computed(() => {
    return (role: RoleUtilisateur) =>
      utilisateurs.value.filter((u) => u.role === role)
  })

  const admins = computed(() => parRole.value('admin'))

  async function creer(dto: CreateUtilisateurDTO): Promise<Utilisateur> {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dto),
    })
    const nouvel = await response.json() as Utilisateur
    utilisateurs.value.push(nouvel)
    return nouvel
  }

  async function modifier(dto: UpdateUtilisateurDTO): Promise<Utilisateur> {
    const { id, ...donnees } = dto
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(donnees),
    })
    const modifie = await response.json() as Utilisateur
    const index = utilisateurs.value.findIndex((u) => u.id === id)
    if (index !== -1) utilisateurs.value[index] = modifie
    return modifie
  }

  async function supprimer(id: number): Promise<void> {
    await fetch(`/api/users/${id}`, { method: 'DELETE' })
    utilisateurs.value = utilisateurs.value.filter((u) => u.id !== id)
  }

  return {
    utilisateurs,
    utilisateurActif,
    chargement,
    erreurs,
    admins,
    parRole,
    creer,
    modifier,
    supprimer,
  }
})
```

## Typage des routes Vue Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

// Extension du type RouteMeta pour ajouter des propriétés personnalisées
declare module 'vue-router' {
  interface RouteMeta {
    title: string
    requiresAuth: boolean
    roles?: RoleUtilisateur[]
    layout?: 'default' | 'auth' | 'admin'
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: {
        title: 'Accueil',
        requiresAuth: false,
        layout: 'default',
      },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/UsersView.vue'),
      meta: {
        title: 'Gestion utilisateurs',
        requiresAuth: true,
        roles: ['admin'],     // TypeScript vérifie que 'admin' est un RoleUtilisateur valide
        layout: 'admin',
      },
    },
  ],
})
```

```vue
<!-- Utilisation typée de useRoute -->
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

const route = useRoute()
const router = useRouter()

// route.meta est maintenant typé avec notre interface RouteMeta
console.log(route.meta.title)        // string
console.log(route.meta.requiresAuth) // boolean
console.log(route.meta.roles)        // RoleUtilisateur[] | undefined

// Navigation typée
const destination: RouteLocationRaw = { name: 'admin-users' }
router.push(destination)
</script>
```

## Patterns avancés TypeScript + Vue

### Props complexes avec slots typés

```vue
<script setup lang="ts" generic="T extends { id: number }">
// Vue 3.3+ — Props génériques
const props = defineProps<{
  items: T[]
  champNom: keyof T
}>()

const emit = defineEmits<{
  selectionner: [item: T]
}>()
</script>
```

### Typage des `provide/inject`

```typescript
// src/composables/useThemeContext.ts
import { provide, inject, ref } from 'vue'
import type { InjectionKey, Ref } from 'vue'

// Créer une clé d'injection typée — garantit la cohérence entre provide et inject
export const CleTheme: InjectionKey<Ref<'dark' | 'light'>> = Symbol('theme')

// Dans le composant parent (Provider)
export function fournirTheme() {
  const theme = ref<'dark' | 'light'>('light')
  provide(CleTheme, theme)
  return theme
}

// Dans les composants enfants (Consumers)
export function utiliserTheme() {
  const theme = inject(CleTheme)
  if (!theme) {
    throw new Error('utiliserTheme() doit être utilisé dans un composant enfant de ThemeProvider')
  }
  return theme
}
```

```vue
<!-- Composant Provider -->
<script setup lang="ts">
import { fournirTheme } from '@/composables/useThemeContext'

const theme = fournirTheme()
</script>
```

```vue
<!-- Composant Consumer (n'importe où dans l'arbre) -->
<template>
  <div :class="`theme-${theme}`">
    Thème actuel : {{ theme }}
  </div>
</template>

<script setup lang="ts">
import { utiliserTheme } from '@/composables/useThemeContext'

const theme = utiliserTheme() // TypeScript sait que c'est Ref<'dark' | 'light'>
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** VSCode avec autocomplétion TypeScript dans un composant Vue (survol d'une prop, erreur TypeScript soulignée)
> **Expliquer :** Taper une prop qui n'existe pas et montrer l'erreur TypeScript en rouge dans l'éditeur avant même d'ouvrir le navigateur. Montrer l'autocomplétion (Ctrl+Espace) dans `defineProps`. Renommer une prop et montrer que TypeScript signale toutes les utilisations à corriger. C'est la valeur ajoutée principale de TypeScript.
---

## Organiser les types dans un projet

```
src/
├── types/
│   ├── index.ts         # Réexporte tous les types
│   ├── api.ts           # Types des réponses API
│   ├── models.ts        # Modèles métier (Utilisateur, Produit, etc.)
│   └── store.ts         # Types spécifiques aux stores
├── stores/
├── composables/
└── components/
```

```typescript
// src/types/models.ts
export interface Utilisateur {
  id: number
  email: string
  prenom: string
  nom: string
  role: 'admin' | 'user'
  createdAt: string
}

export interface Produit {
  id: number
  nom: string
  description: string
  prix: number
  stock: number
  categorieId: number
}

export interface Commande {
  id: number
  utilisateurId: number
  produits: Array<{ produit: Produit; quantite: number }>
  total: number
  statut: 'en_attente' | 'en_cours' | 'livree' | 'annulee'
  createdAt: string
}
```

```typescript
// src/types/api.ts
import type { Produit, Utilisateur } from './models'

export interface ReponseApi<T> {
  data: T
  message?: string
  success: boolean
}

export interface ReponsePagee<T> {
  data: T[]
  pagination: {
    page: number
    perPage: number
    total: number
    totalPages: number
  }
}

// Types des payloads de requête (DTOs)
export type CreateProduitDTO = Omit<Produit, 'id'>
export type UpdateProduitDTO = Partial<CreateProduitDTO> & { id: number }
export type CreateUtilisateurDTO = Omit<Utilisateur, 'id' | 'createdAt'> & { password: string }
```

## Résumé

| Concept | Syntaxe TypeScript Vue 3 |
|---|---|
| Props typées | `defineProps<{ nom: string; age?: number }>()` |
| Props avec défauts | `withDefaults(defineProps<Props>(), { age: 0 })` |
| Emits typés | `defineEmits<{ update: [v: string] }>()` |
| Template ref typée | `useTemplateRef<HTMLInputElement>('ref')` |
| Store typé | `ref<Utilisateur | null>(null)` |
| Clé d'injection | `InjectionKey<Ref<string>>` |
| Route meta | `declare module 'vue-router' { interface RouteMeta { ... } }` |

**Félicitations — vous avez complété le cours Vue 3 !**
Passez aux exercices pratiques pour consolider vos acquis →
