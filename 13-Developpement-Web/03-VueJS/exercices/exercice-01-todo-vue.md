# Exercice 1 — Application Todo Vue 3

## Objectif

Construire une application Todo complète en Vue 3 avec la Composition API, TypeScript, et Pinia. Cet exercice couvre tous les fondamentaux vus en cours.

**Durée estimée :** 2h à 3h

## Fonctionnalités à implémenter

- [ ] Ajouter une tâche avec titre et priorité
- [ ] Marquer une tâche comme terminée (toggle)
- [ ] Supprimer une tâche
- [ ] Modifier le texte d'une tâche (double-clic pour éditer)
- [ ] Filtrer par statut : Toutes / En cours / Terminées
- [ ] Filtrer par priorité : Toutes / Haute / Moyenne / Basse
- [ ] Compteur de tâches restantes
- [ ] Supprimer toutes les tâches terminées
- [ ] Persistance dans localStorage (les tâches survivent au rechargement)
- [ ] Animation à l'ajout/suppression

## Étape 1 — Setup du projet

```bash
npm create vue@latest todo-vue
# TypeScript: Yes
# Vue Router: No (pas nécessaire pour cet exercice)
# Pinia: Yes
# ESLint: Yes
# Prettier: Yes

cd todo-vue
npm install
npm run dev
```

## Étape 2 — Définir les types

```typescript
// src/types/todo.ts
export type Priorite = 'haute' | 'moyenne' | 'basse'
export type Filtre = 'toutes' | 'en_cours' | 'terminees'

export interface Todo {
  id: number
  texte: string
  termine: boolean
  priorite: Priorite
  createdAt: string
}

export interface NouveauTodo {
  texte: string
  priorite: Priorite
}
```

## Étape 3 — Store Pinia

```typescript
// src/stores/todos.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Todo, NouveauTodo, Filtre, Priorite } from '@/types/todo'

export const useTodosStore = defineStore('todos', () => {
  // Charger depuis localStorage au démarrage
  const todosStockes = localStorage.getItem('todos')
  const todos = ref<Todo[]>(todosStockes ? JSON.parse(todosStockes) : [])
  const filtre = ref<Filtre>('toutes')
  const filtrePriorite = ref<Priorite | 'toutes'>('toutes')

  // Sauvegarder automatiquement dans localStorage
  watch(
    todos,
    (valeur) => {
      localStorage.setItem('todos', JSON.stringify(valeur))
    },
    { deep: true }
  )

  // Getters
  const todosFiltres = computed(() => {
    let resultat = todos.value

    // Filtre par statut
    if (filtre.value === 'en_cours') {
      resultat = resultat.filter((t) => !t.termine)
    } else if (filtre.value === 'terminees') {
      resultat = resultat.filter((t) => t.termine)
    }

    // Filtre par priorité
    if (filtrePriorite.value !== 'toutes') {
      resultat = resultat.filter((t) => t.priorite === filtrePriorite.value)
    }

    // Tri : haute priorité en premier, puis non terminées en premier
    return resultat.sort((a, b) => {
      const priorites = { haute: 0, moyenne: 1, basse: 2 }
      if (a.termine !== b.termine) return a.termine ? 1 : -1
      return priorites[a.priorite] - priorites[b.priorite]
    })
  })

  const nombreRestants = computed(
    () => todos.value.filter((t) => !t.termine).length
  )

  const aToutesTerminees = computed(
    () => todos.value.length > 0 && todos.value.every((t) => t.termine)
  )

  // Actions
  function ajouter(nouveau: NouveauTodo) {
    if (!nouveau.texte.trim()) return

    todos.value.push({
      id: Date.now(),
      texte: nouveau.texte.trim(),
      termine: false,
      priorite: nouveau.priorite,
      createdAt: new Date().toISOString(),
    })
  }

  function toggleTermine(id: number) {
    const todo = todos.value.find((t) => t.id === id)
    if (todo) todo.termine = !todo.termine
  }

  function supprimer(id: number) {
    todos.value = todos.value.filter((t) => t.id !== id)
  }

  function modifier(id: number, nouveauTexte: string) {
    const todo = todos.value.find((t) => t.id === id)
    if (todo && nouveauTexte.trim()) {
      todo.texte = nouveauTexte.trim()
    }
  }

  function supprimerTerminees() {
    todos.value = todos.value.filter((t) => !t.termine)
  }

  function toggleToutes() {
    const toutesTerminees = aToutesTerminees.value
    todos.value.forEach((t) => {
      t.termine = !toutesTerminees
    })
  }

  return {
    todos,
    filtre,
    filtrePriorite,
    todosFiltres,
    nombreRestants,
    aToutesTerminees,
    ajouter,
    toggleTermine,
    supprimer,
    modifier,
    supprimerTerminees,
    toggleToutes,
  }
})
```

> **Note :** Il manque l'import de `watch` dans le store — ajoutez-le !

## Étape 4 — Composant FormulaireAjout

```vue
<!-- src/components/FormulaireAjout.vue -->
<template>
  <form @submit.prevent="soumettre" class="formulaire">
    <div class="saisie-group">
      <input
        ref="inputRef"
        v-model="saisie.texte"
        type="text"
        placeholder="Nouvelle tâche..."
        maxlength="200"
        class="input-texte"
      />
      <select v-model="saisie.priorite" class="select-priorite">
        <option value="haute">🔴 Haute</option>
        <option value="moyenne">🟡 Moyenne</option>
        <option value="basse">🟢 Basse</option>
      </select>
      <button type="submit" :disabled="!saisie.texte.trim()" class="btn-ajouter">
        Ajouter
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, useTemplateRef } from 'vue'
import { useTodosStore } from '@/stores/todos'
import type { Priorite } from '@/types/todo'

const store = useTodosStore()
const inputRef = useTemplateRef<HTMLInputElement>('inputRef')

const saisie = reactive({
  texte: '',
  priorite: 'moyenne' as Priorite,
})

function soumettre() {
  store.ajouter({ texte: saisie.texte, priorite: saisie.priorite })
  saisie.texte = ''
  inputRef.value?.focus()
}
</script>
```

## Étape 5 — Composant TodoItem

```vue
<!-- src/components/TodoItem.vue -->
<template>
  <div class="todo-item" :class="{ termine: todo.termine }">
    <input
      type="checkbox"
      :checked="todo.termine"
      @change="store.toggleTermine(todo.id)"
      class="checkbox"
    />

    <!-- Mode affichage -->
    <span
      v-if="!enEdition"
      class="texte"
      :class="`priorite-${todo.priorite}`"
      @dblclick="commencerEdition"
    >
      {{ todo.texte }}
    </span>

    <!-- Mode édition -->
    <input
      v-else
      ref="inputEdition"
      v-model="texteEdition"
      @blur="sauvegarderEdition"
      @keyup.enter="sauvegarderEdition"
      @keyup.escape="annulerEdition"
      class="input-edition"
    />

    <span class="badge-priorite" :class="`badge-${todo.priorite}`">
      {{ todo.priorite }}
    </span>

    <button @click="store.supprimer(todo.id)" class="btn-supprimer" title="Supprimer">
      ×
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, useTemplateRef } from 'vue'
import { useTodosStore } from '@/stores/todos'
import type { Todo } from '@/types/todo'

const props = defineProps<{ todo: Todo }>()
const store = useTodosStore()
const inputEdition = useTemplateRef<HTMLInputElement>('inputEdition')

const enEdition = ref(false)
const texteEdition = ref('')

async function commencerEdition() {
  texteEdition.value = props.todo.texte
  enEdition.value = true
  // Attendre que Vue mette à jour le DOM avant de focus
  await nextTick()
  inputEdition.value?.focus()
  inputEdition.value?.select()
}

function sauvegarderEdition() {
  if (texteEdition.value.trim()) {
    store.modifier(props.todo.id, texteEdition.value)
  }
  enEdition.value = false
}

function annulerEdition() {
  enEdition.value = false
}
</script>

<style scoped>
.todo-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}
.todo-item:hover { background: #f9f9f9; }
.todo-item.termine .texte {
  text-decoration: line-through;
  opacity: 0.5;
}
.priorite-haute { border-left: 3px solid #e53e3e; padding-left: 0.5rem; }
.priorite-moyenne { border-left: 3px solid #f6ad55; padding-left: 0.5rem; }
.priorite-basse { border-left: 3px solid #68d391; padding-left: 0.5rem; }
.badge-priorite {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 12px;
  margin-left: auto;
}
.badge-haute { background: #fed7d7; color: #c53030; }
.badge-moyenne { background: #fefcbf; color: #744210; }
.badge-basse { background: #c6f6d5; color: #276749; }
.btn-supprimer {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.25rem;
}
.btn-supprimer:hover { color: #e53e3e; }
</style>
```

## Étape 6 — Composant principal App.vue

```vue
<!-- src/App.vue -->
<template>
  <div class="app">
    <h1 class="titre">
      ✅ Todo Vue 3
      <span v-if="store.nombreRestants > 0" class="badge-compteur">
        {{ store.nombreRestants }}
      </span>
    </h1>

    <FormulaireAjout />

    <!-- Barre de filtres -->
    <div class="filtres">
      <div class="filtres-statut">
        <button
          v-for="f in filtresStatut"
          :key="f.valeur"
          @click="store.filtre = f.valeur"
          :class="{ actif: store.filtre === f.valeur }"
          class="btn-filtre"
        >
          {{ f.label }}
        </button>
      </div>

      <div class="filtres-priorite">
        <select v-model="store.filtrePriorite">
          <option value="toutes">Toutes priorités</option>
          <option value="haute">Haute</option>
          <option value="moyenne">Moyenne</option>
          <option value="basse">Basse</option>
        </select>
      </div>
    </div>

    <!-- Toggle toutes + supprimer terminées -->
    <div v-if="store.todos.length > 0" class="actions-globales">
      <label class="toggle-toutes">
        <input
          type="checkbox"
          :checked="store.aToutesTerminees"
          @change="store.toggleToutes"
        />
        Tout cocher/décocher
      </label>
      <button
        v-if="store.todos.some(t => t.termine)"
        @click="store.supprimerTerminees"
        class="btn-supprimer-terminees"
      >
        Supprimer les terminées
      </button>
    </div>

    <!-- Liste des todos avec animation -->
    <TransitionGroup name="liste" tag="div" class="liste">
      <TodoItem
        v-for="todo in store.todosFiltres"
        :key="todo.id"
        :todo="todo"
      />
    </TransitionGroup>

    <!-- État vide -->
    <div v-if="store.todosFiltres.length === 0" class="etat-vide">
      <p v-if="store.todos.length === 0">
        Aucune tâche — ajoutez-en une ci-dessus !
      </p>
      <p v-else>Aucune tâche correspondant aux filtres.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTodosStore } from '@/stores/todos'
import FormulaireAjout from '@/components/FormulaireAjout.vue'
import TodoItem from '@/components/TodoItem.vue'

const store = useTodosStore()

const filtresStatut = [
  { valeur: 'toutes', label: 'Toutes' },
  { valeur: 'en_cours', label: 'En cours' },
  { valeur: 'terminees', label: 'Terminées' },
] as const
</script>

<style>
/* Animations TransitionGroup */
.liste-enter-active,
.liste-leave-active {
  transition: all 0.3s ease;
}
.liste-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.liste-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
.liste-move {
  transition: transform 0.3s ease;
}
</style>
```

## Bonus — Fonctionnalités avancées

### Drag & drop pour réordonner

```bash
npm install vuedraggable@next
```

```vue
<script setup>
import draggable from 'vuedraggable'
import { storeToRefs } from 'pinia'
import { useTodosStore } from '@/stores/todos'

const store = useTodosStore()
const { todos } = storeToRefs(store)
</script>

<template>
  <draggable v-model="todos" item-key="id" handle=".poignee">
    <template #item="{ element }">
      <div class="todo-item">
        <span class="poignee">⠿</span>
        <TodoItem :todo="element" />
      </div>
    </template>
  </draggable>
</template>
```

### Recherche plein texte

```typescript
// Ajouter dans le store
const recherche = ref('')

const todosFiltres = computed(() => {
  let resultat = todos.value

  // Filtre de recherche
  if (recherche.value.trim()) {
    const terme = recherche.value.toLowerCase()
    resultat = resultat.filter((t) =>
      t.texte.toLowerCase().includes(terme)
    )
  }

  // ... autres filtres
  return resultat
})
```

## Critères d'évaluation

| Fonctionnalité | Points |
|---|---|
| Ajouter / supprimer une tâche | 2 |
| Toggle terminée | 2 |
| Édition inline (double-clic) | 2 |
| Filtres statut + priorité | 2 |
| Persistance localStorage | 2 |
| TypeScript correct (pas de `any`) | 2 |
| Pinia (store bien structuré) | 2 |
| Code propre et lisible | 2 |
| Bonus : animations | 1 |
| Bonus : drag & drop | 1 |
| **Total** | **20** |

## Ressources

- [Vue 3 Docs](https://vuejs.org/guide/essentials/forms)
- [Pinia Docs](https://pinia.vuejs.org)
- [TransitionGroup](https://vuejs.org/guide/built-ins/transition-group)
- [VueDraggable](https://github.com/SortableJS/vue.draggable.next)
