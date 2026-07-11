# Cheatsheet Vue 3

## Setup rapide

```bash
npm create vue@latest mon-app   # Avec options (Router, Pinia, TS...)
npm create vite@latest mon-app -- --template vue-ts
```

## Structure d'un SFC

```vue
<template>                          <!-- HTML enrichi -->
  <div>{{ message }}</div>
</template>

<script setup lang="ts">            <!-- Composition API -->
import { ref } from 'vue'
const message = ref('Bonjour')
</script>

<style scoped>                      <!-- CSS limité au composant -->
div { color: green; }
</style>
```

## Réactivité

```typescript
import { ref, reactive, computed, watch, watchEffect } from 'vue'

const n = ref(0)             // primitif réactif → n.value
const obj = reactive({})    // objet réactif → obj.prop (pas de .value)
const double = computed(() => n.value * 2)   // valeur dérivée (cachée)

watch(n, (nouveau, ancien) => { ... })        // observer une source
watch(() => obj.prop, (v) => { ... })         // observer une propriété
watchEffect(() => { /* dépendances auto */ }) // effet immédiat
```

## Template — Directives

```vue
<!-- Affichage -->
{{ expression }}
<div v-html="htmlBrut"></div>

<!-- Liaison d'attributs -->
<img :src="url" :class="{ active: isOn }" :style="{ color: c }">
<div v-bind="objetAttributs"></div>

<!-- Conditions -->
<div v-if="a">A</div>
<div v-else-if="b">B</div>
<div v-else>C</div>
<div v-show="visible">Toujours dans le DOM</div>

<!-- Listes -->
<li v-for="(item, i) in items" :key="item.id">{{ i }}: {{ item.nom }}</li>
<li v-for="(val, cle) in objet" :key="cle">{{ cle }}: {{ val }}</li>

<!-- Événements -->
<button @click="handler">Clic</button>
<input @keyup.enter="submit" @keyup.esc="cancel">
<form @submit.prevent="submit">

<!-- Modificateurs -->
@click.stop   @click.prevent   @click.once   @click.self
@keyup.ctrl.z   v-model.lazy   v-model.trim   v-model.number

<!-- Liaison bidirectionnelle -->
<input v-model="texte">
<select v-model="choix">
<input type="checkbox" v-model="tableauChoix" :value="val">
```

## Composants

```vue
<!-- Enfant -->
<script setup lang="ts">
const props = defineProps<{ titre: string; compte?: number }>()
const props2 = withDefaults(defineProps<Props>(), { compte: 0 })

const emit = defineEmits<{
  changer: [valeur: string]
  fermer: []
}>()

defineExpose({ methodePublique })  // exposer aux parents via ref
</script>

<!-- Parent -->
<MonComposant
  titre="Titre"
  :compte="42"
  @changer="handler"
  @fermer="() => {}"
/>

<!-- Slots -->
<slot />                     <!-- slot par défaut -->
<slot name="header" />       <!-- slot nommé -->
<slot :item="item" />        <!-- scoped slot -->

<!-- Utilisation slots -->
<Comp>Contenu par défaut</Comp>
<Comp><template #header>Titre</template></Comp>
<Comp #default="{ item }">{{ item.nom }}</Comp>
```

## Cycle de vie

```typescript
import { onMounted, onUnmounted, onUpdated, onBeforeUnmount } from 'vue'

onMounted(() => { /* DOM disponible — faire les appels API ici */ })
onBeforeUnmount(() => { /* nettoyer listeners, intervals */ })
onUnmounted(() => { /* composant détruit */ })
onUpdated(() => { /* après chaque re-render */ })
```

## Template Refs

```vue
<input ref="monInput" />
<!-- ou avec useTemplateRef (Vue 3.5+) -->

<script setup lang="ts">
import { useTemplateRef, onMounted } from 'vue'
const monInput = useTemplateRef<HTMLInputElement>('monInput')
onMounted(() => monInput.value?.focus())
</script>
```

## Composables

```typescript
// src/composables/useCounter.ts
import { ref, computed } from 'vue'
export function useCounter(init = 0) {
  const count = ref(init)
  const double = computed(() => count.value * 2)
  const increment = () => count.value++
  return { count, double, increment }
}

// Utilisation
const { count, increment } = useCounter(10)
```

## Vue Router 4

```typescript
// Définir les routes
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/users/:id', name: 'user', component: UserView, props: true },
    { path: '/:path(.*)*', component: NotFoundView },  // 404
    { path: '/admin', component: Layout, children: [...] },
  ]
})

// Guards
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isLoggedIn) return { name: 'login' }
})
```

```vue
<!-- Navigation -->
<RouterLink :to="{ name: 'user', params: { id: 1 } }">Lien</RouterLink>
<RouterView />

<!-- Programmatique -->
<script setup>
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()

router.push({ name: 'home' })
router.replace('/about')
const id = route.params.id        // paramètre de route
const page = route.query.page     // query param (?page=1)
</script>
```

## Pinia

```typescript
// Définir un store
export const useMonStore = defineStore('mon-store', () => {
  const items = ref<Item[]>([])
  const total = computed(() => items.value.length)

  async function charger() {
    items.value = await fetch('/api/items').then(r => r.json())
  }

  return { items, total, charger }
})

// Utiliser dans un composant
const store = useMonStore()
store.charger()
store.items                        // accès direct

// Destructurer sans perdre la réactivité
import { storeToRefs } from 'pinia'
const { items, total } = storeToRefs(store)   // refs → réactifs
const { charger } = store                      // actions → ok directement

// Patch en lot
store.$patch({ prop1: 'val', prop2: 42 })
store.$patch(state => { state.items.push(newItem) })
```

## Transitions

```vue
<Transition name="fondu">
  <div v-if="visible">Contenu animé</div>
</Transition>

<TransitionGroup name="liste" tag="ul">
  <li v-for="item in items" :key="item.id">{{ item }}</li>
</TransitionGroup>

<style>
.fondu-enter-active, .fondu-leave-active { transition: opacity 0.3s; }
.fondu-enter-from, .fondu-leave-to { opacity: 0; }

.liste-move { transition: transform 0.3s; }
.liste-enter-from { opacity: 0; transform: translateX(-20px); }
.liste-leave-to { opacity: 0; transform: translateX(20px); }
</style>
```

## toRef / toRefs

```typescript
import { reactive, toRef, toRefs } from 'vue'

const state = reactive({ count: 0, name: 'Alice' })

const count = toRef(state, 'count')       // ref liée à state.count
const { count, name } = toRefs(state)     // toutes les propriétés en refs
// Modifier count.value modifie state.count
```

## provide / inject

```typescript
// Parent
import { provide, InjectionKey, Ref } from 'vue'
const CleTheme: InjectionKey<Ref<string>> = Symbol('theme')
provide(CleTheme, ref('dark'))

// Enfant (n'importe où dans l'arbre)
const theme = inject(CleTheme, ref('light')) // valeur par défaut
```

## async / Suspense

```vue
<!-- Composant async -->
<script setup>
const data = await fetch('/api/data').then(r => r.json())
</script>

<!-- Parent avec Suspense -->
<Suspense>
  <template #default><MonComposantAsync /></template>
  <template #fallback><p>Chargement...</p></template>
</Suspense>
```

## Raccourcis clés

| Syntaxe longue | Raccourci |
|---|---|
| `v-bind:href="url"` | `:href="url"` |
| `v-on:click="fn"` | `@click="fn"` |
| `v-slot:header` | `#header` |

## Gotchas courants

```typescript
// ❌ Ne pas réassigner un reactive
let state = reactive({ ... })
state = { ... }  // perd la réactivité

// ❌ Ne pas destructurer reactive sans toRefs
const { count } = reactive({ count: 0 })  // count non réactif

// ❌ Modifier une prop directement
props.valeur = 'x'  // erreur Vue — émettre un événement à la place

// ✅ Toujours utiliser :key avec v-for
// ✅ Ne jamais mettre v-if et v-for sur le même élément

// ✅ Nettoyer dans onBeforeUnmount
onBeforeUnmount(() => clearInterval(timer))
```
