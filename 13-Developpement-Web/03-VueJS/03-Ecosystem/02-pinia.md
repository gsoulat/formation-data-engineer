# Pinia — Gestion d'état global

## Qu'est-ce que Pinia ?

Pinia est le gestionnaire d'état officiel de Vue 3. Il remplace Vuex (Vue 2) avec une API plus simple, un meilleur support TypeScript, et une intégration native avec les Vue Devtools.

**Pourquoi un state manager ?**

Dans une application, plusieurs composants distants peuvent avoir besoin des mêmes données (ex: l'utilisateur connecté, le panier, les préférences). Passer ces données par props sur des dizaines de niveaux est pénible ("prop drilling"). Pinia résout ce problème en créant un état global accessible depuis n'importe quel composant.

```
Sans Pinia:                    Avec Pinia:
App.vue                        App.vue ← useCartStore()
└── Layout.vue                 └── Layout.vue ← useCartStore()
    └── Header.vue                 └── Header.vue ← useCartStore()
        └── CartIcon.vue           CartIcon.vue ← useCartStore()
            (reçoit props          (accède directement)
             de App → Layout
             → Header → CartIcon)
```

## Installation

```bash
npm install pinia

# Si vous utilisez npm create vue@latest, Pinia est proposé à l'installation
```

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia) // Avant app.mount()
app.mount('#app')
```

## `defineStore` — Créer un store

```typescript
// src/stores/counter.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Syntax 1 : Setup Store (recommandé — proche de la Composition API)
export const useCounterStore = defineStore('counter', () => {
  // STATE — données réactives
  const count = ref(0)
  const step = ref(1)

  // GETTERS — propriétés calculées
  const doubled = computed(() => count.value * 2)
  const isPositive = computed(() => count.value > 0)

  // ACTIONS — méthodes qui modifient l'état
  function increment() {
    count.value += step.value
  }

  function decrement() {
    count.value -= step.value
  }

  function reset() {
    count.value = 0
  }

  function setStep(newStep: number) {
    step.value = newStep
  }

  // Retourner tout ce qui doit être accessible depuis l'extérieur
  return { count, step, doubled, isPositive, increment, decrement, reset, setStep }
})
```

```typescript
// Syntax 2 : Options Store (plus proche de Vue 2 Vuex)
export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    step: 1,
  }),

  getters: {
    doubled: (state) => state.count * 2,
    isPositive: (state) => state.count > 0,
  },

  actions: {
    increment() {
      this.count += this.step
    },
    async fetchInitialCount() {
      const response = await fetch('/api/counter')
      this.count = await response.json()
    },
  },
})
```

## Utiliser un store dans un composant

```vue
<template>
  <div>
    <p>Compteur : {{ counter.count }}</p>
    <p>Double : {{ counter.doubled }}</p>
    <p>Positif : {{ counter.isPositive }}</p>

    <button @click="counter.increment()">+{{ counter.step }}</button>
    <button @click="counter.decrement()">-{{ counter.step }}</button>
    <button @click="counter.reset()">Reset</button>

    <input type="number" v-model.number="counter.step" />
  </div>
</template>

<script setup lang="ts">
import { useCounterStore } from '@/stores/counter'

// Appeler le composable — retourne l'instance du store
const counter = useCounterStore()

// ATTENTION : ne pas destructurer directement — perd la réactivité
// const { count, increment } = counter  // ❌ count n'est plus réactif

// Pour destructurer en préservant la réactivité → storeToRefs
import { storeToRefs } from 'pinia'
const { count, doubled } = storeToRefs(counter)
// Les méthodes/actions peuvent être destructurées directement (pas besoin de storeToRefs)
const { increment, reset } = counter
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Vue Devtools ouvert sur l'onglet "Pinia" avec le store visible
> **Expliquer :** Ouvrir Vue Devtools → onglet Pinia. Montrer le store avec son état actuel. Cliquer sur un bouton dans l'app et observer l'état se mettre à jour en temps réel dans Devtools. Montrer aussi qu'on peut modifier l'état directement depuis Devtools (double-cliquer sur une valeur) — extrêmement utile pour le débogage.
---

## Store d'authentification — exemple réaliste

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Utilisateur {
  id: number
  email: string
  prenom: string
  nom: string
  role: 'admin' | 'user'
}

interface LoginPayload {
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  // STATE
  const utilisateur = ref<Utilisateur | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const chargement = ref(false)
  const erreur = ref<string | null>(null)

  // GETTERS
  const isLoggedIn = computed(() => !!token.value && !!utilisateur.value)
  const isAdmin = computed(() => utilisateur.value?.role === 'admin')
  const nomComplet = computed(() =>
    utilisateur.value
      ? `${utilisateur.value.prenom} ${utilisateur.value.nom}`
      : 'Invité'
  )

  function hasRole(role: string): boolean {
    return utilisateur.value?.role === role
  }

  // ACTIONS
  async function login(payload: LoginPayload): Promise<void> {
    chargement.value = true
    erreur.value = null

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Identifiants incorrects')
      }

      const data = await response.json()
      token.value = data.token
      utilisateur.value = data.user

      // Persister le token
      localStorage.setItem('auth_token', data.token)
    } catch (e) {
      erreur.value = e instanceof Error ? e.message : 'Erreur de connexion'
      throw e // Re-throw pour que le composant puisse gérer l'erreur
    } finally {
      chargement.value = false
    }
  }

  async function chargerProfil(): Promise<void> {
    if (!token.value) return

    try {
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })

      if (!response.ok) {
        // Token invalide ou expiré
        logout()
        return
      }

      utilisateur.value = await response.json()
    } catch {
      logout()
    }
  }

  function logout(): void {
    utilisateur.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    utilisateur,
    token,
    chargement,
    erreur,
    isLoggedIn,
    isAdmin,
    nomComplet,
    hasRole,
    login,
    chargerProfil,
    logout,
  }
})
```

## Store du panier — gestion de liste

```typescript
// src/stores/cart.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Produit {
  id: number
  nom: string
  prix: number
  image: string
}

interface ItemPanier extends Produit {
  quantite: number
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<ItemPanier[]>([])

  // Getters
  const nombreItems = computed(() =>
    items.value.reduce((total, item) => total + item.quantite, 0)
  )

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.prix * item.quantite, 0)
  )

  const totalFormate = computed(() =>
    new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' })
      .format(total.value)
  )

  const estVide = computed(() => items.value.length === 0)

  // Actions
  function ajouter(produit: Produit, quantite = 1) {
    const existant = items.value.find((item) => item.id === produit.id)

    if (existant) {
      existant.quantite += quantite
    } else {
      items.value.push({ ...produit, quantite })
    }
  }

  function retirer(produitId: number) {
    const index = items.value.findIndex((item) => item.id === produitId)
    if (index !== -1) {
      items.value.splice(index, 1)
    }
  }

  function modifierQuantite(produitId: number, quantite: number) {
    const item = items.value.find((item) => item.id === produitId)
    if (!item) return

    if (quantite <= 0) {
      retirer(produitId)
    } else {
      item.quantite = quantite
    }
  }

  function vider() {
    items.value = []
  }

  return {
    items,
    nombreItems,
    total,
    totalFormate,
    estVide,
    ajouter,
    retirer,
    modifierQuantite,
    vider,
  }
})
```

```vue
<!-- src/components/BoutonPanier.vue -->
<template>
  <button class="btn-panier" @click="cart.ajouter(produit)">
    <span>Ajouter au panier</span>
    <span v-if="cart.nombreItems > 0" class="badge">{{ cart.nombreItems }}</span>
  </button>
</template>

<script setup lang="ts">
import { useCartStore } from '@/stores/cart'

const props = defineProps<{
  produit: { id: number; nom: string; prix: number; image: string }
}>()

const cart = useCartStore()
</script>
```

## Persistance du store avec un plugin

```typescript
// src/stores/plugins/persistPlugin.ts
import { PiniaPlugin, PiniaPluginContext } from 'pinia'

// Plugin qui persiste automatiquement les stores dans localStorage
export function persistPlugin(context: PiniaPluginContext) {
  const { store, options } = context

  // Restaurer depuis localStorage au démarrage
  const storedData = localStorage.getItem(store.$id)
  if (storedData) {
    store.$patch(JSON.parse(storedData))
  }

  // Sauvegarder à chaque changement
  store.$subscribe((mutation, state) => {
    localStorage.setItem(store.$id, JSON.stringify(state))
  })
}
```

```typescript
// src/main.ts — enregistrer le plugin
import { createPinia } from 'pinia'
import { persistPlugin } from '@/stores/plugins/persistPlugin'

const pinia = createPinia()
pinia.use(persistPlugin)
```

## Stores multiples et inter-dépendances

```typescript
// src/stores/produits.ts
import { defineStore } from 'pinia'
import { useAuthStore } from './auth' // Import d'un autre store

export const useProduitsStore = defineStore('produits', () => {
  const auth = useAuthStore() // Utiliser un autre store

  const produits = ref([])
  const chargement = ref(false)

  async function charger() {
    chargement.value = true
    try {
      const response = await fetch('/api/produits', {
        headers: {
          // Utiliser les données du store auth
          Authorization: `Bearer ${auth.token}`,
        },
      })
      produits.value = await response.json()
    } finally {
      chargement.value = false
    }
  }

  return { produits, chargement, charger }
})
```

## `$patch` — Mise à jour par lot

```typescript
// Dans un composant ou une action
const store = useMonStore()

// Patcher plusieurs propriétés d'un coup (évite plusieurs mutations séparées)
store.$patch({
  nom: 'Nouveau nom',
  actif: true,
  score: 100,
})

// Patcher avec une fonction (pour les tableaux et opérations complexes)
store.$patch((state) => {
  state.items.push({ id: 4, nom: 'Nouveau produit' })
  state.total += 29.99
  state.derniereMaj = new Date().toISOString()
})

// Reset au state initial (Options Store uniquement)
store.$reset()

// S'abonner aux changements du store
store.$subscribe((mutation, state) => {
  console.log('Store modifié :', mutation.type, state)
})

// S'abonner aux actions
store.$onAction(({ name, args, after, onError }) => {
  console.log(`Action "${name}" appelée avec`, args)
  after((resultat) => console.log('Résultat :', resultat))
  onError((erreur) => console.error('Erreur :', erreur))
})
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Vue Devtools, onglet Pinia, modifier une valeur du store cart (ajouter un produit)
> **Expliquer :** Ajouter un produit au panier depuis l'interface, et montrer dans Pinia Devtools que l'état `items` est mis à jour. Montrer le nombre d'articles dans le badge de navigation qui se met à jour automatiquement car plusieurs composants réagissent au même store. Montrer le "time travel" — revenir à un état précédent dans la timeline Devtools.
---

## Structure recommandée des stores

```
src/stores/
├── auth.ts          # Authentification, token, utilisateur connecté
├── cart.ts          # Panier d'achats
├── notifications.ts # Alertes/toasts globaux
├── ui.ts            # État UI (sidebar open, theme, modal active)
└── produits.ts      # Cache des données produits
```

```typescript
// src/stores/notifications.ts — store utilitaire commun
import { defineStore } from 'pinia'
import { ref } from 'vue'

type TypeNotification = 'success' | 'error' | 'warning' | 'info'

interface Notification {
  id: number
  message: string
  type: TypeNotification
  duree: number
}

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  let nextId = 1

  function ajouter(message: string, type: TypeNotification = 'info', duree = 3000) {
    const id = nextId++
    notifications.value.push({ id, message, type, duree })

    // Auto-suppression après la durée
    setTimeout(() => supprimer(id), duree)
  }

  function succes(message: string) { ajouter(message, 'success') }
  function erreur(message: string) { ajouter(message, 'error', 5000) }
  function avertissement(message: string) { ajouter(message, 'warning') }

  function supprimer(id: number) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index !== -1) notifications.value.splice(index, 1)
  }

  return { notifications, ajouter, succes, erreur, avertissement, supprimer }
})
```

## Résumé — Pinia vs Vuex

| | Pinia | Vuex 4 |
|---|---|---|
| API | `defineStore` | `createStore` |
| TypeScript | Excellent | Limité |
| Mutations | Supprimées | Requises |
| DevTools | Intégrés | Intégrés |
| Taille | ~1.5 KB | ~6 KB |
| Stores multiples | Natif | Module system |
| Composition API | Natif | Non |

## Résumé des concepts Pinia

| Concept | Équivalent Vue | Description |
|---|---|---|
| `defineStore` | — | Créer un store |
| `state` / `ref` | `data()` | Données réactives |
| `getters` / `computed` | `computed` | Valeurs dérivées |
| `actions` / `function` | `methods` | Modifier l'état |
| `storeToRefs` | `toRefs` | Destructurer sans perdre la réactivité |
| `$patch` | — | Mise à jour en lot |
| `$subscribe` | `watch` | Observer les changements |

**Prochaine étape :** Vue 3 + TypeScript →
