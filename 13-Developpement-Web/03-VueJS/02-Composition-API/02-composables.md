# Composables Vue 3 — Réutiliser la logique

## Qu'est-ce qu'un composable ?

Un composable est une fonction qui utilise la Composition API de Vue pour encapsuler et réutiliser de la logique avec état. C'est la réponse Vue 3 aux problèmes des mixins Vue 2 (conflits de noms, origine opaque des données, couplage fort).

**Convention :** Les composables sont des fonctions préfixées par `use` (ex: `useCounter`, `useFetch`, `useWindowSize`).

```
src/
├── composables/
│   ├── useCounter.ts
│   ├── useFetch.ts
│   ├── useLocalStorage.ts
│   ├── useWindowSize.ts
│   └── useForm.ts
└── components/
    └── ...
```

## Composable basique — `useCounter`

```typescript
// src/composables/useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0, step = 1) {
  const count = ref(initialValue)

  const doubled = computed(() => count.value * 2)
  const isPositive = computed(() => count.value > 0)

  function increment() {
    count.value += step
  }

  function decrement() {
    count.value -= step
  }

  function reset() {
    count.value = initialValue
  }

  function set(value: number) {
    count.value = value
  }

  return {
    count,
    doubled,
    isPositive,
    increment,
    decrement,
    reset,
    set,
  }
}
```

```vue
<!-- Utilisation dans un composant -->
<template>
  <div>
    <p>Compteur A : {{ countA }} (double: {{ doubledA }})</p>
    <button @click="incrementA">+{{ step }}</button>
    <button @click="decrementA">-{{ step }}</button>
    <button @click="resetA">Reset</button>

    <hr />

    <!-- Chaque appel crée une instance INDÉPENDANTE -->
    <p>Compteur B : {{ countB }}</p>
    <button @click="incrementB">+10</button>
  </div>
</template>

<script setup>
import { useCounter } from '@/composables/useCounter'

// Instance A avec step=1 (défaut)
const {
  count: countA,
  doubled: doubledA,
  increment: incrementA,
  decrement: decrementA,
  reset: resetA,
} = useCounter(0)

const step = 1

// Instance B avec step=10
const { count: countB, increment: incrementB } = useCounter(100, 10)
</script>
```

## Composable avec état partagé

Pour partager l'état entre plusieurs composants (sans Pinia), on peut déclarer les données hors de la fonction :

```typescript
// src/composables/useTheme.ts
import { ref, computed, watch } from 'vue'

// État déclaré EN DEHORS de la fonction → partagé entre tous les appelants
const isDark = ref(
  window.matchMedia('(prefers-color-scheme: dark)').matches
)

export function useTheme() {
  const theme = computed(() => (isDark.value ? 'dark' : 'light'))

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  function setDark(value: boolean) {
    isDark.value = value
  }

  // Synchroniser avec la classe CSS sur <html>
  watch(isDark, (dark) => {
    document.documentElement.classList.toggle('dark', dark)
  }, { immediate: true })

  return { isDark, theme, toggleTheme, setDark }
}
```

## `useFetch` — Appels HTTP réutilisables

```typescript
// src/composables/useFetch.ts
import { ref, shallowRef, watchEffect, toValue } from 'vue'

// MaybeRefOrGetter est un type utilitaire Vue 3 (ref, getter ou valeur directe)
type MaybeRef<T> = T | Ref<T> | (() => T)

export function useFetch<T>(url: MaybeRef<string>) {
  const data = shallowRef<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute() {
    data.value = null
    error.value = null
    loading.value = true

    try {
      const resolvedUrl = toValue(url) // déréférence ref/getter/valeur
      const response = await fetch(resolvedUrl)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      data.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e : new Error('Erreur inconnue')
    } finally {
      loading.value = false
    }
  }

  // watchEffect détecte automatiquement que url est une dépendance
  // et re-exécute quand url change
  watchEffect(() => {
    execute()
  })

  return { data, loading, error, refetch: execute }
}
```

```vue
<!-- Utilisation simple -->
<template>
  <div>
    <div v-if="loading">Chargement en cours...</div>
    <div v-else-if="error" class="erreur">
      Erreur : {{ error.message }}
      <button @click="refetch">Réessayer</button>
    </div>
    <div v-else-if="data">
      <h2>{{ data.name }}</h2>
      <p>Email : {{ data.email }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useFetch } from '@/composables/useFetch'
import { useRoute } from 'vue-router'

const route = useRoute()
// L'URL est un getter réactif — se met à jour quand l'ID de route change
const url = computed(() => `/api/users/${route.params.id}`)

const { data, loading, error, refetch } = useFetch(url)
</script>
```

## `useFetch` avancé avec Axios et annulation

```typescript
// src/composables/useApi.ts
import { ref, shallowRef, watch, onUnmounted } from 'vue'
import axios, { type AxiosRequestConfig, type CancelTokenSource } from 'axios'

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(config: AxiosRequestConfig) {
  const state = ref<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  let cancelSource: CancelTokenSource | null = null

  async function execute(overrideConfig?: Partial<AxiosRequestConfig>) {
    // Annuler la requête précédente si elle est encore en cours
    if (cancelSource) {
      cancelSource.cancel('Nouvelle requête déclenchée')
    }

    cancelSource = axios.CancelToken.source()
    state.value.loading = true
    state.value.error = null

    try {
      const response = await axios({
        ...config,
        ...overrideConfig,
        cancelToken: cancelSource.token,
      })
      state.value.data = response.data
    } catch (e) {
      if (!axios.isCancel(e)) {
        state.value.error = axios.isAxiosError(e)
          ? e.response?.data?.message ?? e.message
          : 'Erreur inconnue'
      }
    } finally {
      state.value.loading = false
      cancelSource = null
    }
  }

  // Nettoyage : annuler toute requête en cours quand le composant est démonté
  onUnmounted(() => {
    cancelSource?.cancel('Composant démonté')
  })

  return {
    ...state.value,
    state,
    execute,
  }
}
```

## `useLocalStorage` — Persistance locale

```typescript
// src/composables/useLocalStorage.ts
import { ref, watch } from 'vue'

export function useLocalStorage<T>(cle: string, valeurDefaut: T) {
  // Lire la valeur initiale depuis localStorage
  const valeurStockee = localStorage.getItem(cle)

  const data = ref<T>(
    valeurStockee !== null
      ? JSON.parse(valeurStockee)
      : valeurDefaut
  )

  // Synchroniser vers localStorage à chaque changement
  watch(
    data,
    (nouvelleValeur) => {
      if (nouvelleValeur === null || nouvelleValeur === undefined) {
        localStorage.removeItem(cle)
      } else {
        localStorage.setItem(cle, JSON.stringify(nouvelleValeur))
      }
    },
    { deep: true }
  )

  function remove() {
    localStorage.removeItem(cle)
    data.value = valeurDefaut
  }

  return { data, remove }
}
```

```vue
<template>
  <div>
    <label>Thème préféré :</label>
    <select v-model="preferences.theme">
      <option value="light">Clair</option>
      <option value="dark">Sombre</option>
    </select>

    <label>Langue :</label>
    <select v-model="preferences.langue">
      <option value="fr">Français</option>
      <option value="en">English</option>
    </select>

    <button @click="remove">Réinitialiser les préférences</button>
  </div>
</template>

<script setup>
import { useLocalStorage } from '@/composables/useLocalStorage'

const { data: preferences, remove } = useLocalStorage('user-prefs', {
  theme: 'light',
  langue: 'fr',
  notifications: true,
})
</script>
```

## `useWindowSize` — Dimensions de la fenêtre

```typescript
// src/composables/useWindowSize.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useWindowSize() {
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  const isMobile = computed(() => width.value < 768)
  const isTablet = computed(() => width.value >= 768 && width.value < 1024)
  const isDesktop = computed(() => width.value >= 1024)

  function onResize() {
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => {
    window.addEventListener('resize', onResize)
  })

  onUnmounted(() => {
    // Nettoyage important — évite les fuites mémoire
    window.removeEventListener('resize', onResize)
  })

  return { width, height, isMobile, isTablet, isDesktop }
}
```

```vue
<template>
  <div>
    <p>Fenêtre : {{ width }}px × {{ height }}px</p>
    <p>Appareil : {{ isMobile ? 'Mobile' : isTablet ? 'Tablette' : 'Desktop' }}</p>
    <MobileNav v-if="isMobile" />
    <DesktopNav v-else />
  </div>
</template>

<script setup>
import { useWindowSize } from '@/composables/useWindowSize'

const { width, height, isMobile, isTablet } = useWindowSize()
</script>
```

## `useForm` — Gestion de formulaires

```typescript
// src/composables/useForm.ts
import { reactive, ref, computed } from 'vue'

type ValidationRule<T> = (value: T) => string | true

interface FieldConfig<T> {
  valeurInitiale: T
  regles?: ValidationRule<T>[]
}

type FormConfig<T extends Record<string, unknown>> = {
  [K in keyof T]: FieldConfig<T[K]>
}

export function useForm<T extends Record<string, unknown>>(config: FormConfig<T>) {
  const fields = reactive({} as T)
  const errors = reactive({} as Record<keyof T, string[]>)
  const touched = reactive({} as Record<keyof T, boolean>)
  const isSubmitting = ref(false)

  // Initialiser les valeurs et erreurs
  for (const cle in config) {
    ;(fields as Record<string, unknown>)[cle] = config[cle].valeurInitiale
    ;(errors as Record<string, string[]>)[cle] = []
    ;(touched as Record<string, boolean>)[cle] = false
  }

  function validateField(cle: keyof T): boolean {
    const fieldConfig = config[cle]
    if (!fieldConfig.regles) return true

    const fieldErrors: string[] = []
    for (const regle of fieldConfig.regles) {
      const resultat = regle((fields as Record<string, unknown>)[cle as string] as T[typeof cle])
      if (resultat !== true) {
        fieldErrors.push(resultat)
      }
    }

    ;(errors as Record<string, string[]>)[cle as string] = fieldErrors
    return fieldErrors.length === 0
  }

  function validateAll(): boolean {
    let valid = true
    for (const cle in config) {
      ;(touched as Record<string, boolean>)[cle] = true
      if (!validateField(cle)) valid = false
    }
    return valid
  }

  function reset() {
    for (const cle in config) {
      ;(fields as Record<string, unknown>)[cle] = config[cle].valeurInitiale
      ;(errors as Record<string, string[]>)[cle] = []
      ;(touched as Record<string, boolean>)[cle] = false
    }
  }

  const isValid = computed(() => {
    return Object.values(errors).every(
      (fieldErrors) => (fieldErrors as string[]).length === 0
    )
  })

  return {
    fields,
    errors,
    touched,
    isSubmitting,
    isValid,
    validateField,
    validateAll,
    reset,
  }
}
```

```vue
<!-- Utilisation du composable useForm -->
<template>
  <form @submit.prevent="soumettre">
    <div>
      <label>Email</label>
      <input
        v-model="fields.email"
        @blur="touched.email = true; validateField('email')"
        type="email"
      />
      <span v-if="touched.email && errors.email.length" class="erreur">
        {{ errors.email[0] }}
      </span>
    </div>

    <div>
      <label>Mot de passe</label>
      <input
        v-model="fields.password"
        @blur="touched.password = true; validateField('password')"
        type="password"
      />
      <span v-if="touched.password && errors.password.length" class="erreur">
        {{ errors.password[0] }}
      </span>
    </div>

    <button type="submit" :disabled="isSubmitting">
      {{ isSubmitting ? 'Connexion...' : 'Se connecter' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { useForm } from '@/composables/useForm'
import { useRouter } from 'vue-router'

const router = useRouter()

const { fields, errors, touched, isSubmitting, isValid, validateField, validateAll, reset } = useForm({
  email: {
    valeurInitiale: '',
    regles: [
      (v) => !!v || 'L\'email est requis',
      (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Email invalide',
    ],
  },
  password: {
    valeurInitiale: '',
    regles: [
      (v) => !!v || 'Le mot de passe est requis',
      (v) => v.length >= 8 || 'Minimum 8 caractères',
    ],
  },
})

async function soumettre() {
  if (!validateAll()) return

  isSubmitting.value = true
  try {
    await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fields),
    })
    router.push('/dashboard')
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Créer un composable `useCounter` dans le terminal, puis l'utiliser dans deux composants différents côte à côte dans le navigateur
> **Expliquer :** Montrer que chaque appel à `useCounter()` crée une instance indépendante. Puis créer une version avec l'état partagé (déclaré en dehors) et montrer que deux composants partagent le même état. Comparer avec les mixins Vue 2 — les composables sont plus explicites sur l'origine des données.
---

## `useIntersectionObserver` — Chargement lazy

```typescript
// src/composables/useIntersectionObserver.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useIntersectionObserver(
  threshold = 0.1
) {
  const target = ref<HTMLElement | null>(null)
  const isVisible = ref(false)
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        isVisible.value = entries[0].isIntersecting
      },
      { threshold }
    )

    if (target.value) {
      observer.observe(target.value)
    }
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  return { target, isVisible }
}
```

```vue
<template>
  <!-- Chaque image se charge seulement quand elle devient visible -->
  <div v-for="image in images" :key="image.id">
    <div ref="target" style="min-height: 200px">
      <img v-if="isVisible" :src="image.url" :alt="image.alt" />
      <div v-else class="placeholder">Chargement...</div>
    </div>
  </div>
</template>

<script setup>
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'

const { target, isVisible } = useIntersectionObserver(0.2)
</script>
```

## Bonnes pratiques des composables

```typescript
// ✅ BON — retourner des refs, pas des valeurs brutes
export function useComposable() {
  const count = ref(0)
  return { count } // ref retournée → réactif dans le template
}

// ❌ MAUVAIS — valeur brute perdue la réactivité
export function useComposable() {
  const count = ref(0)
  return { count: count.value } // valeur fixe, non réactive
}

// ✅ BON — accepter ref OU valeur via MaybeRef
import { toValue } from 'vue'
export function useProcessing(input: MaybeRef<string>) {
  return computed(() => toValue(input).toUpperCase())
}

// ✅ BON — nettoyer les effets de bord dans onUnmounted
export function useTimer() {
  const seconds = ref(0)
  const timer = setInterval(() => seconds.value++, 1000)

  onUnmounted(() => clearInterval(timer)) // TOUJOURS nettoyer

  return { seconds }
}

// ✅ BON — nommage explicite en camelCase préfixé use
export function useUserPreferences() { ... }
export function useProductSearch() { ... }
export function usePaymentForm() { ... }
```

## Résumé

| Composable | Rôle |
|---|---|
| `useCounter` | Compteur réutilisable |
| `useFetch` | Requêtes HTTP avec état loading/error |
| `useLocalStorage` | Persistance dans localStorage |
| `useWindowSize` | Dimensions réactives de la fenêtre |
| `useForm` | Gestion complète de formulaires |
| `useIntersectionObserver` | Détection de visibilité DOM |

**Prochaine étape :** Vue Router 4 — navigation et routing →
