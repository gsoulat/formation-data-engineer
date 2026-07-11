# Réactivité — ref, reactive, computed, watch

## Le système de réactivité de Vue 3

Vue 3 utilise des **Proxies JavaScript ES6** pour détecter automatiquement les lectures et écritures sur des objets. Quand une donnée réactive change, Vue sait exactement quels composants doivent être re-rendus.

## `ref` — Rendre une valeur réactive

`ref()` crée une valeur réactive autour de n'importe quel type (primitif ou objet).

```vue
<template>
  <div>
    <!-- Dans le template, Vue déréférence automatiquement → pas de .value -->
    <p>Compteur : {{ compteur }}</p>
    <p>Nom : {{ nom }}</p>
    <p>Actif : {{ actif }}</p>
    <p>Total items : {{ items.length }}</p>

    <button @click="compteur++">Incrémenter</button>
    <button @click="nom = 'Bob'">Changer nom</button>
    <button @click="items.push('Nouvel item')">Ajouter item</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Valeurs primitives
const compteur = ref(0)
const nom = ref('Alice')
const actif = ref(true)

// Tableaux et objets — ref() fonctionne aussi
const items = ref(['item 1', 'item 2'])
const utilisateur = ref({ id: 1, email: 'alice@example.com' })

// Dans le script, on doit utiliser .value pour lire/écrire
console.log(compteur.value)   // 0
compteur.value = 5            // modifier
compteur.value++              // incrémenter

console.log(utilisateur.value.email)
utilisateur.value.email = 'nouveau@example.com'
utilisateur.value = { id: 2, email: 'bob@example.com' } // remplacement complet

// Avec TypeScript — typage explicite
const score = ref<number>(0)
const messages = ref<string[]>([])
const config = ref<{ theme: string; lang: string } | null>(null)
</script>
```

### Quand `ref` se déréférence automatiquement

```vue
<script setup>
import { ref, reactive } from 'vue'

const compteur = ref(0)

// DANS le template → déréférence automatique (pas de .value)
// DANS le script → .value obligatoire

// Dans un objet reactive, le ref est déréférencé automatiquement aussi
const etat = reactive({
  compteur,      // ref "unwrappée" dans reactive
  nom: 'Alice',
})

etat.compteur++  // fonctionne directement (pas de .value ici)
console.log(etat.compteur) // 1 — pas besoin de .value
</script>
```

## `reactive` — Réactivité pour les objets

`reactive()` rend un objet entier réactif. Contrairement à `ref`, pas besoin de `.value`.

```vue
<template>
  <div>
    <p>{{ etat.utilisateur.prenom }} {{ etat.utilisateur.nom }}</p>
    <p>Statut : {{ etat.statut }}</p>
    <p>Score : {{ etat.score }}</p>

    <button @click="incrementerScore">+10 points</button>
    <button @click="reinitialiser">Reset</button>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

// reactive() pour un état complexe — pas de .value
const etat = reactive({
  utilisateur: {
    prenom: 'Alice',
    nom: 'Dupont',
    age: 28,
  },
  statut: 'connecté',
  score: 0,
  historique: [],
})

function incrementerScore() {
  etat.score += 10
  etat.historique.push({
    date: new Date().toISOString(),
    points: 10,
  })
}

function reinitialiser() {
  // Modifier les propriétés directement
  etat.score = 0
  etat.historique = []
  etat.statut = 'réinitialisé'

  // ATTENTION : ne JAMAIS réassigner l'objet reactive lui-même !
  // etat = { ... }  // ❌ Perd la réactivité !
}
</script>
```

### `ref` vs `reactive` — Quand utiliser lequel ?

```typescript
// Règle générale recommandée par l'équipe Vue :
// → Utilisez ref() pour tout (primitifs ET objets)
// → Utilisez reactive() si vous préférez la syntaxe sans .value pour les gros objets

// Avec ref()
const nom = ref('Alice')
const utilisateur = ref({ id: 1, nom: 'Alice' })
nom.value = 'Bob'
utilisateur.value.nom = 'Bob'

// Avec reactive()
const utilisateur = reactive({ id: 1, nom: 'Alice' })
utilisateur.nom = 'Bob'  // plus concis pour les objets
// Mais on ne peut pas utiliser reactive() pour les primitifs
// const compteur = reactive(0)  // ❌ Ne fonctionne pas
```

### Problème courant avec `reactive` : la destructuration

```typescript
import { reactive, toRefs } from 'vue'

const etat = reactive({
  compteur: 0,
  nom: 'Alice',
})

// ❌ MAUVAIS — la réactivité est perdue après destructuration
const { compteur, nom } = etat
compteur++ // ne déclenche PAS de mise à jour

// ✅ BON — toRefs() convertit chaque propriété en ref()
const { compteur, nom } = toRefs(etat)
compteur.value++ // fonctionne — la réactivité est préservée
```

## `computed` — Propriétés calculées

`computed()` crée une valeur dérivée d'autres données réactives. Elle est mise en cache et ne se recalcule que si ses dépendances changent.

```vue
<template>
  <div>
    <input v-model="recherche" placeholder="Rechercher..." />
    <p>{{ produitsFiltres.length }} résultat(s) sur {{ produits.length }}</p>

    <div v-for="produit in produitsFiltres" :key="produit.id">
      <h3>{{ produit.nom }}</h3>
      <p>{{ produit.prix }}€ → avec remise : {{ produit.prixAvecRemise }}€</p>
    </div>

    <hr />
    <p>Total panier : {{ totalPanier }}€</p>
    <p>Nombre d'articles : {{ nombreArticles }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const recherche = ref('')
const remise = ref(10) // 10%

const produits = ref([
  { id: 1, nom: 'Clavier', prix: 89, categorie: 'Périphérique' },
  { id: 2, nom: 'Souris', prix: 49, categorie: 'Périphérique' },
  { id: 3, nom: 'Écran', prix: 299, categorie: 'Moniteur' },
  { id: 4, nom: 'Webcam', prix: 79, categorie: 'Périphérique' },
])

const panier = ref([
  { produitId: 1, quantite: 2, prix: 89 },
  { produitId: 3, quantite: 1, prix: 299 },
])

// computed simple — se recalcule quand recherche ou produits change
const produitsFiltres = computed(() => {
  const terme = recherche.value.toLowerCase().trim()
  if (!terme) return produits.value

  return produits.value.filter(
    (p) =>
      p.nom.toLowerCase().includes(terme) ||
      p.categorie.toLowerCase().includes(terme),
  )
})

// computed avec transformation
const produitsAvecRemise = computed(() =>
  produits.value.map((p) => ({
    ...p,
    prixAvecRemise: (p.prix * (1 - remise.value / 100)).toFixed(2),
  }))
)

// computed pour le panier
const totalPanier = computed(() =>
  panier.value
    .reduce((total, item) => total + item.prix * item.quantite, 0)
    .toFixed(2)
)

const nombreArticles = computed(() =>
  panier.value.reduce((total, item) => total + item.quantite, 0)
)
</script>
```

### `computed` modifiable (getter + setter)

```typescript
import { ref, computed } from 'vue'

const prenom = ref('Alice')
const nom = ref('Dupont')

// computed avec getter ET setter
const nomComplet = computed({
  get() {
    return `${prenom.value} ${nom.value}`
  },
  set(valeur: string) {
    const parties = valeur.split(' ')
    prenom.value = parties[0]
    nom.value = parties.slice(1).join(' ')
  },
})

// Lecture
console.log(nomComplet.value)          // "Alice Dupont"

// Écriture — déclenche le setter
nomComplet.value = 'Bob Martin'
console.log(prenom.value) // "Bob"
console.log(nom.value)    // "Martin"
```

### Computed vs Méthode — quelle différence ?

```vue
<template>
  <!-- computed — mis en cache, recalculé seulement si dépendances changent -->
  <p>{{ nomComplet }}</p>           <!-- si prenom/nom changent → recalcul -->
  <p>{{ nomComplet }}</p>           <!-- MÊME résultat mis en cache — pas de recalcul -->

  <!-- méthode — recalculée à CHAQUE rendu -->
  <p>{{ getNomComplet() }}</p>      <!-- recalculé à chaque rendu -->
  <p>{{ getNomComplet() }}</p>      <!-- recalculé une 2ème fois -->
  <p>{{ Date.now() }}</p>           <!-- computed(()=>Date.now()) serait toujours le même ! -->
</template>

<script setup>
import { ref, computed } from 'vue'

const prenom = ref('Alice')
const nom = ref('Dupont')

// Utiliser computed quand la valeur peut être mise en cache
const nomComplet = computed(() => {
  console.log('computed recalculé')
  return `${prenom.value} ${nom.value}`
})

// Utiliser une méthode si la valeur ne doit PAS être mise en cache
function getNomComplet() {
  console.log('méthode appelée')
  return `${prenom.value} ${nom.value}`
}
</script>
```

## `watch` — Observer des changements

`watch()` exécute une fonction quand une donnée spécifique change. Idéal pour les effets de bord (appels API, log, validation, etc.).

```vue
<template>
  <div>
    <input v-model="recherche" placeholder="Rechercher un utilisateur..." />
    <p v-if="chargement">Chargement...</p>
    <p v-if="erreur" style="color:red">{{ erreur }}</p>
    <ul>
      <li v-for="u in resultats" :key="u.id">{{ u.name }}</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const recherche = ref('')
const resultats = ref([])
const chargement = ref(false)
const erreur = ref(null)

// watch simple — observe une ref
watch(recherche, async (nouvelleValeur, ancienneValeur) => {
  console.log(`Recherche changée: "${ancienneValeur}" → "${nouvelleValeur}"`)

  if (!nouvelleValeur.trim()) {
    resultats.value = []
    return
  }

  chargement.value = true
  erreur.value = null

  try {
    const response = await fetch(
      `https://jsonplaceholder.typicode.com/users?name_like=${nouvelleValeur}`
    )
    resultats.value = await response.json()
  } catch (e) {
    erreur.value = 'Erreur lors de la recherche'
  } finally {
    chargement.value = false
  }
})
</script>
```

### Options de `watch`

```typescript
import { ref, watch } from 'vue'

const config = ref({
  theme: 'dark',
  langue: 'fr',
  notifications: true,
})

const compteur = ref(0)

// immediate: true — exécuté immédiatement au démarrage (pas seulement au changement)
watch(
  compteur,
  (valeur) => {
    console.log('Compteur :', valeur)
  },
  { immediate: true }
)

// deep: true — observer les changements profonds dans un objet
watch(
  config,
  (nouvelleConfig) => {
    console.log('Config changée :', nouvelleConfig)
    // Sauvegarder dans localStorage par exemple
    localStorage.setItem('config', JSON.stringify(nouvelleConfig))
  },
  { deep: true }
)

// Observer une propriété spécifique d'un objet — utiliser un getter
watch(
  () => config.value.theme, // getter
  (nouveauTheme) => {
    document.body.classList.toggle('dark', nouveauTheme === 'dark')
  }
)

// Observer plusieurs sources à la fois
const prenom = ref('Alice')
const nom = ref('Dupont')

watch(
  [prenom, nom],
  ([nouveauPrenom, nouveauNom], [ancienPrenom, ancienNom]) => {
    console.log(`Nom changé: ${ancienPrenom} ${ancienNom} → ${nouveauPrenom} ${nouveauNom}`)
  }
)

// Stopper un watcher manuellement
const stopWatcher = watch(compteur, (val) => {
  console.log('Compteur :', val)
  if (val >= 10) {
    stopWatcher() // arrêter de surveiller après 10
  }
})
```

## `watchEffect` — Réactivité automatique

`watchEffect` s'exécute immédiatement et se ré-exécute automatiquement quand n'importe quelle dépendance réactive utilisée à l'intérieur change (Vue détecte automatiquement les dépendances).

```vue
<template>
  <div>
    <input v-model="userId" type="number" min="1" max="10" />
    <p v-if="chargement">Chargement...</p>
    <div v-if="utilisateur">
      <h2>{{ utilisateur.name }}</h2>
      <p>Email : {{ utilisateur.email }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'

const userId = ref(1)
const utilisateur = ref(null)
const chargement = ref(false)

// watchEffect s'exécute immédiatement et se ré-exécute quand userId change
// Vue détecte automatiquement que userId.value est utilisé ici
watchEffect(async () => {
  chargement.value = true
  try {
    const response = await fetch(
      `https://jsonplaceholder.typicode.com/users/${userId.value}`
    )
    utilisateur.value = await response.json()
  } finally {
    chargement.value = false
  }
})
</script>
```

### Nettoyage dans `watchEffect`

```typescript
import { ref, watchEffect } from 'vue'

const id = ref(1)

watchEffect((onCleanup) => {
  // Créer un AbortController pour annuler la requête précédente
  const controller = new AbortController()

  fetch(`/api/data/${id.value}`, { signal: controller.signal })
    .then(r => r.json())
    .then(data => console.log(data))
    .catch(err => {
      if (err.name !== 'AbortError') console.error(err)
    })

  // onCleanup est appelé avant la prochaine exécution de l'effet
  // ou quand le composant est démonté
  onCleanup(() => {
    controller.abort()
    console.log('Requête précédente annulée')
  })
})
```

### `watch` vs `watchEffect` — Comparaison

| | `watch` | `watchEffect` |
|---|---|---|
| Exécution initiale | Non (par défaut) | Oui (toujours) |
| Sources | Déclarées explicitement | Détectées automatiquement |
| Accès ancienne valeur | Oui | Non |
| Cas d'usage | Observer une source spécifique | Synchroniser des effets |
| Lisibilité | Plus explicite | Plus concis |

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Vue Devtools ouvert sur l'onglet "Timeline" pendant qu'on modifie des données réactives
> **Expliquer :** Montrer dans Vue Devtools l'onglet Timeline — chaque événement de mutation est visible avec son timestamp. Modifier une `ref` ou déclencher un computed et observer la réaction en cascade. Montrer aussi la différence de comportement entre `watch` (lazy par défaut) et `watchEffect` (immédiat) en console.
---

## `toRef` et `toRefs`

```typescript
import { reactive, toRef, toRefs } from 'vue'

const etat = reactive({
  compteur: 0,
  nom: 'Alice',
  age: 28,
})

// toRef — créer une ref liée à une propriété d'un objet reactive
const compteurRef = toRef(etat, 'compteur')
compteurRef.value++
console.log(etat.compteur) // 1 — la modification est synchronisée

// toRefs — convertir toutes les propriétés en refs
// Utile pour destructurer un objet reactive sans perdre la réactivité
const { nom, age } = toRefs(etat)
nom.value = 'Bob'
console.log(etat.nom) // "Bob"
```

## `shallowRef` et `shallowReactive`

Pour les cas de performance avancés :

```typescript
import { shallowRef, shallowReactive, triggerRef } from 'vue'

// shallowRef — seul le .value est réactif, pas les propriétés internes
const config = shallowRef({
  theme: 'dark',
  langue: 'fr',
})

// Ceci NE déclenchera PAS de mise à jour
config.value.theme = 'light' // ❌ pas réactif

// Pour forcer une mise à jour après modification interne
config.value.theme = 'light'
triggerRef(config) // forcer le re-render

// Ou remplacer l'objet entier → déclenche la réactivité
config.value = { ...config.value, theme: 'light' } // ✅

// shallowReactive — seul le premier niveau est réactif
const etat = shallowReactive({
  utilisateur: { nom: 'Alice' }, // les propriétés de utilisateur ne sont PAS réactives
  compteur: 0,                   // compteur EST réactif
})
```

## Résumé

| Primitive | Type | Syntaxe d'accès | Cas d'usage |
|---|---|---|---|
| `ref` | Tout type | `.value` dans le script | Valeurs simples, primitifs |
| `reactive` | Objets seulement | Directement | Gros objets d'état |
| `computed` | Valeur dérivée | `.value` (lecture seule) | Données calculées |
| `watch` | Observateur ciblé | Callback(nouveau, ancien) | Effets de bord ciblés |
| `watchEffect` | Observateur auto | Callback() | Synchronisation d'effets |
| `toRefs` | Conversion | `.value` après | Destructurer reactive |

**Prochaine étape :** Les composables — réutiliser la logique avec la Composition API →
