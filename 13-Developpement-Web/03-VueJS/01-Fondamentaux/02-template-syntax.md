# Syntaxe de Template Vue 3

## Introduction

Le template Vue est du HTML enrichi avec une syntaxe spéciale. Vue compile ces templates en code JavaScript optimisé. La syntaxe est intentionnellement proche du HTML natif pour faciliter l'apprentissage.

## Interpolation de texte — `{{ }}`

La forme la plus basique d'affichage de données :

```vue
<template>
  <div>
    <!-- Interpolation simple -->
    <p>{{ message }}</p>

    <!-- Expression JavaScript dans les doubles accolades -->
    <p>{{ message.toUpperCase() }}</p>
    <p>{{ 1 + 1 }}</p>
    <p>{{ isConnected ? 'Connecté' : 'Déconnecté' }}</p>
    <p>{{ items.length }} éléments</p>

    <!-- Les objets sont sérialisés en JSON -->
    <pre>{{ utilisateur }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('Bonjour Vue 3 !')
const isConnected = ref(true)
const items = ref(['pomme', 'banane', 'cerise'])
const utilisateur = ref({ nom: 'Dupont', prenom: 'Jean' })
</script>
```

> **Attention :** L'interpolation `{{ }}` échappe automatiquement le HTML pour éviter les attaques XSS. Pour afficher du HTML brut, utilisez `v-html` (avec précaution).

```vue
<template>
  <!-- DANGEREUX si le contenu vient d'un utilisateur ! -->
  <div v-html="contenuHtml"></div>
</template>

<script setup>
const contenuHtml = ref('<strong>Texte en gras</strong>')
</script>
```

## `v-bind` — Liaison d'attributs

`v-bind` lie dynamiquement un attribut HTML à une expression JavaScript.

```vue
<template>
  <!-- Syntaxe longue -->
  <img v-bind:src="imageUrl" v-bind:alt="imageAlt" />

  <!-- Syntaxe courte (recommandée) — le : est un alias de v-bind: -->
  <img :src="imageUrl" :alt="imageAlt" />

  <!-- Liaison de classe dynamique -->
  <div :class="classeActive">Du texte</div>

  <!-- Objet de classes — la clé est la classe, la valeur est le booléen -->
  <button :class="{ 'btn-active': isActive, 'btn-disabled': isDisabled }">
    Cliquez
  </button>

  <!-- Tableau de classes -->
  <div :class="[classeBase, isActive ? 'active' : '']">Contenu</div>

  <!-- Styles inline dynamiques -->
  <p :style="{ color: couleurTexte, fontSize: taillePolice + 'px' }">
    Texte stylisé
  </p>

  <!-- Objet de styles complet -->
  <p :style="stylesObjet">Texte avec objet de styles</p>

  <!-- Lier tous les attributs d'un objet d'un coup -->
  <input v-bind="attributsInput" />
</template>

<script setup>
import { ref } from 'vue'

const imageUrl = ref('https://vuejs.org/logo.svg')
const imageAlt = ref('Logo Vue.js')
const classeActive = ref('surligné')
const isActive = ref(true)
const isDisabled = ref(false)
const couleurTexte = ref('#42b883')
const taillePolice = ref(18)

const stylesObjet = ref({
  backgroundColor: '#f5f5f5',
  padding: '1rem',
  borderRadius: '8px',
})

const attributsInput = ref({
  type: 'email',
  placeholder: 'votre@email.com',
  required: true,
  class: 'input-field',
})
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans le navigateur, montrer Vue Devtools (onglet "Components") avec les données réactives visibles dans le panneau
> **Expliquer :** Ouvrir les Vue Devtools (F12 → onglet Vue), sélectionner un composant, modifier une valeur directement dans le panneau Devtools et voir le DOM se mettre à jour en temps réel. Montrer le lien entre les données du script et leur affichage dans le template.
---

## `v-model` — Liaison bidirectionnelle

`v-model` crée une liaison dans les deux sens entre une donnée et un élément de formulaire.

```vue
<template>
  <div>
    <!-- Input texte -->
    <input v-model="nom" placeholder="Votre nom" />
    <p>Bonjour, {{ nom }} !</p>

    <!-- Textarea -->
    <textarea v-model="description" rows="4"></textarea>

    <!-- Checkbox unique → booléen -->
    <input type="checkbox" v-model="accepteCgu" id="cgu" />
    <label for="cgu">J'accepte les CGU</label>
    <p>CGU acceptées : {{ accepteCgu }}</p>

    <!-- Checkboxes multiples → tableau -->
    <div v-for="fruit in fruitsDisponibles" :key="fruit">
      <input
        type="checkbox"
        :id="fruit"
        :value="fruit"
        v-model="fruitsChoisis"
      />
      <label :for="fruit">{{ fruit }}</label>
    </div>
    <p>Fruits choisis : {{ fruitsChoisis.join(', ') }}</p>

    <!-- Radio buttons -->
    <div v-for="option in tailles" :key="option.value">
      <input
        type="radio"
        :id="option.value"
        :value="option.value"
        v-model="tailleChoisie"
      />
      <label :for="option.value">{{ option.label }}</label>
    </div>
    <p>Taille : {{ tailleChoisie }}</p>

    <!-- Select (liste déroulante) -->
    <select v-model="pays">
      <option value="">-- Choisir un pays --</option>
      <option value="fr">France</option>
      <option value="be">Belgique</option>
      <option value="ch">Suisse</option>
    </select>
    <p>Pays sélectionné : {{ pays }}</p>

    <!-- Select multiple → tableau -->
    <select v-model="langues" multiple>
      <option value="fr">Français</option>
      <option value="en">Anglais</option>
      <option value="es">Espagnol</option>
    </select>
    <p>Langues : {{ langues }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const nom = ref('')
const description = ref('')
const accepteCgu = ref(false)
const fruitsDisponibles = ['Pomme', 'Banane', 'Cerise', 'Mangue']
const fruitsChoisis = ref([])
const tailles = [
  { value: 'xs', label: 'Très petit' },
  { value: 's', label: 'Petit' },
  { value: 'm', label: 'Moyen' },
  { value: 'l', label: 'Grand' },
]
const tailleChoisie = ref('m')
const pays = ref('')
const langues = ref([])
</script>
```

### Modificateurs de `v-model`

```vue
<template>
  <!-- .lazy : met à jour seulement au blur/change, pas à chaque frappe -->
  <input v-model.lazy="texte" />

  <!-- .number : convertit automatiquement en nombre -->
  <input type="number" v-model.number="age" />
  <p>Age (type: {{ typeof age }}) : {{ age }}</p>

  <!-- .trim : supprime les espaces en début et fin -->
  <input v-model.trim="email" />
</template>

<script setup>
import { ref } from 'vue'

const texte = ref('')
const age = ref(0)
const email = ref('')
</script>
```

## `v-if`, `v-else-if`, `v-else` — Rendu conditionnel

```vue
<template>
  <div>
    <!-- v-if retire/ajoute l'élément du DOM -->
    <div v-if="score >= 16">
      <h2>Excellent !</h2>
      <p>Score : {{ score }}/20</p>
    </div>
    <div v-else-if="score >= 10">
      <h2>Passable</h2>
      <p>Score : {{ score }}/20</p>
    </div>
    <div v-else>
      <h2>Insuffisant</h2>
      <p>Score : {{ score }}/20</p>
    </div>

    <!-- v-show garde l'élément dans le DOM mais change display:none -->
    <!-- Préférez v-show pour des éléments qui changent fréquemment -->
    <p v-show="isVisible">Ce texte est visible : {{ isVisible }}</p>

    <button @click="isVisible = !isVisible">Toggle visibilité</button>
    <button @click="score = Math.floor(Math.random() * 21)">
      Score aléatoire
    </button>

    <!-- template v-if — groupe plusieurs éléments sans div wrapper -->
    <template v-if="utilisateur">
      <h3>{{ utilisateur.prenom }} {{ utilisateur.nom }}</h3>
      <p>Email : {{ utilisateur.email }}</p>
    </template>
    <p v-else>Aucun utilisateur connecté</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const score = ref(14)
const isVisible = ref(true)
const utilisateur = ref({
  prenom: 'Marie',
  nom: 'Martin',
  email: 'marie.martin@example.com',
})
</script>
```

### `v-if` vs `v-show`

| | `v-if` | `v-show` |
|---|---|---|
| DOM | Ajoute/retire l'élément | Toujours présent (display:none) |
| Coût initial | Plus élevé si `true` | Toujours rendu |
| Coût des toggles | Élevé | Faible |
| Quand l'utiliser | Condition rarement changeante | Condition fréquemment changeante |

## `v-for` — Rendu de liste

```vue
<template>
  <div>
    <!-- Tableau simple -->
    <ul>
      <li v-for="fruit in fruits" :key="fruit">{{ fruit }}</li>
    </ul>

    <!-- Tableau avec index -->
    <ul>
      <li v-for="(fruit, index) in fruits" :key="fruit">
        {{ index + 1 }}. {{ fruit }}
      </li>
    </ul>

    <!-- Tableau d'objets -->
    <div v-for="produit in produits" :key="produit.id" class="card">
      <h3>{{ produit.nom }}</h3>
      <p>Prix : {{ produit.prix }}€</p>
      <span :class="produit.stock > 0 ? 'en-stock' : 'rupture'">
        {{ produit.stock > 0 ? `${produit.stock} en stock` : 'Rupture' }}
      </span>
    </div>

    <!-- Itérer sur un objet -->
    <dl>
      <template v-for="(valeur, cle) in personne" :key="cle">
        <dt>{{ cle }}</dt>
        <dd>{{ valeur }}</dd>
      </template>
    </dl>

    <!-- v-for avec une plage de nombres (1 à 5) -->
    <div v-for="n in 5" :key="n">Étoile {{ n }}</div>

    <!-- Combinaison v-for + v-if — attention : v-if a la priorité sur v-for -->
    <!-- Mauvaise pratique : v-if et v-for sur le même élément -->
    <!-- Bonne pratique : utiliser computed ou template wrapper -->
    <ul>
      <template v-for="produit in produits" :key="produit.id">
        <li v-if="produit.stock > 0">{{ produit.nom }}</li>
      </template>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fruits = ref(['Pomme', 'Banane', 'Cerise', 'Mangue'])

const produits = ref([
  { id: 1, nom: 'Clavier mécanique', prix: 89.99, stock: 5 },
  { id: 2, nom: 'Souris ergonomique', prix: 49.99, stock: 0 },
  { id: 3, nom: 'Écran 27"', prix: 299.99, stock: 2 },
  { id: 4, nom: 'Casque audio', prix: 129.99, stock: 8 },
])

const personne = ref({
  prenom: 'Thomas',
  nom: 'Bernard',
  age: 32,
  ville: 'Lyon',
})
</script>

<style scoped>
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem 0;
}
.en-stock { color: green; }
.rupture { color: red; }
</style>
```

> **Règle importante :** Toujours utiliser `:key` avec `v-for`. La clé doit être unique et stable (idéalement un ID de base de données). Ne jamais utiliser l'index comme key si la liste peut être réordonnée ou filtrée.

## `v-on` — Gestion des événements

```vue
<template>
  <div>
    <!-- Syntaxe longue -->
    <button v-on:click="incrementer">Syntaxe longue</button>

    <!-- Syntaxe courte @ (recommandée) -->
    <button @click="incrementer">Cliquer : {{ compteur }}</button>

    <!-- Expression inline (simple uniquement) -->
    <button @click="compteur++">Inline</button>

    <!-- Avec l'objet événement $event -->
    <button @click="logEvent">Log l'événement</button>
    <button @click="logEvent($event)">Log explicite</button>

    <!-- Événements clavier -->
    <input
      @keyup.enter="soumettre"
      @keyup.escape="annuler"
      v-model="saisie"
      placeholder="Appuyez sur Entrée"
    />

    <!-- Modificateurs d'événement -->
    <form @submit.prevent="soumettreForme">
      <input type="text" v-model="nomForme" />
      <button type="submit">Envoyer (prevent default)</button>
    </form>

    <!-- .stop — arrête la propagation -->
    <div @click="clickParent">
      Parent cliqué
      <button @click.stop="clickEnfant">Enfant (stop propagation)</button>
    </div>

    <!-- .once — l'handler ne s'exécute qu'une fois -->
    <button @click.once="uneSeuleFois">Une seule fois</button>

    <!-- Événements souris -->
    <div
      @mouseover="survoler"
      @mouseleave="quitterSurvol"
      :class="{ survole: estSurvole }"
      style="padding: 1rem; border: 1px solid #ccc"
    >
      Zone de survol : {{ estSurvole ? 'Survolé' : 'Normal' }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const compteur = ref(0)
const saisie = ref('')
const nomForme = ref('')
const estSurvole = ref(false)

function incrementer() {
  compteur.value++
}

function logEvent(event) {
  console.log('Type :', event.type)
  console.log('Target :', event.target)
}

function soumettre() {
  console.log('Saisie soumise :', saisie.value)
  saisie.value = ''
}

function annuler() {
  saisie.value = ''
}

function soumettreForme() {
  console.log('Formulaire soumis :', nomForme.value)
}

function clickParent() {
  console.log('Parent cliqué')
}

function clickEnfant() {
  console.log('Enfant cliqué (propagation stoppée)')
}

function uneSeuleFois() {
  alert('Cette alerte n\'apparaîtra qu\'une seule fois !')
}

function survoler() {
  estSurvole.value = true
}

function quitterSurvol() {
  estSurvole.value = false
}
</script>
```

### Modificateurs de touches clavier

```vue
<template>
  <!-- Touches spéciales -->
  <input @keyup.enter="onEnter" placeholder="Entrée" />
  <input @keyup.tab="onTab" placeholder="Tab" />
  <input @keyup.delete="onDelete" placeholder="Delete/Backspace" />
  <input @keyup.esc="onEsc" placeholder="Échap" />
  <input @keyup.space="onSpace" placeholder="Espace" />

  <!-- Touches modificatrices (Ctrl, Alt, Shift, Meta) -->
  <input @keyup.ctrl.z="annuler" placeholder="Ctrl+Z pour annuler" />
  <input @keyup.shift.enter="nouvelLigne" placeholder="Shift+Entrée" />
</template>
```

## Template Refs — `ref` sur les éléments DOM

Parfois on a besoin d'accéder directement à un élément DOM :

```vue
<template>
  <div>
    <!-- ref="nomRef" sur un élément DOM -->
    <input ref="champSaisie" type="text" placeholder="Focus automatique" />
    <canvas ref="monCanvas" width="200" height="100"></canvas>

    <button @click="focuserInput">Focus l'input</button>
    <button @click="dessinerSurCanvas">Dessiner</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// La variable doit avoir le même nom que l'attribut ref=""
const champSaisie = ref(null)
const monCanvas = ref(null)

// L'élément DOM n'est disponible qu'après le montage
onMounted(() => {
  // champSaisie.value est maintenant l'élément DOM <input>
  champSaisie.value.focus()

  const ctx = monCanvas.value.getContext('2d')
  ctx.fillStyle = '#42b883'
  ctx.fillRect(10, 10, 180, 80)
})

function focuserInput() {
  champSaisie.value.focus()
}

function dessinerSurCanvas() {
  const ctx = monCanvas.value.getContext('2d')
  ctx.clearRect(0, 0, 200, 100)
  ctx.fillStyle = `hsl(${Math.random() * 360}, 70%, 50%)`
  ctx.fillRect(
    Math.random() * 150,
    Math.random() * 70,
    50,
    30,
  )
}
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur avec Vue Devtools ouvert, modifier une valeur réactive depuis le panneau Devtools
> **Expliquer :** Dans l'onglet Components de Vue Devtools, sélectionner un composant, trouver une variable `ref` dans le panneau de droite, cliquer dessus pour la modifier. Observer la mise à jour instantanée dans le DOM. C'est un outil indispensable pour le débogage.
---

## `v-once` et `v-memo`

```vue
<template>
  <!-- v-once : rendu une seule fois, jamais mis à jour même si les données changent -->
  <p v-once>Valeur initiale (jamais mise à jour) : {{ message }}</p>
  <p>Valeur réactive : {{ message }}</p>

  <!-- v-memo : optimisation de performances — ne re-rend que si les dépendances changent -->
  <div v-memo="[item.id, item.selected]" v-for="item in listeItems" :key="item.id">
    {{ item.nom }} - {{ item.selected ? 'Sélectionné' : 'Normal' }}
  </div>

  <button @click="message = 'Nouveau message'">Changer le message</button>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('Message original')
const listeItems = ref([
  { id: 1, nom: 'Item A', selected: false },
  { id: 2, nom: 'Item B', selected: true },
  { id: 3, nom: 'Item C', selected: false },
])
</script>
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Code en direct dans l'éditeur avec le résultat visible dans le navigateur côte à côte
> **Expliquer :** Taper du code dans `<template>`, sauvegarder, et montrer la mise à jour en temps réel dans le navigateur grâce au HMR de Vite. Insister sur le fait qu'il n'y a PAS de rechargement de page.
---

## Résumé des directives fondamentales

| Directive | Utilisation | Exemple |
|---|---|---|
| `{{ }}` | Affichage de texte | `{{ nom }}` |
| `v-bind:` / `:` | Attributs dynamiques | `:href="url"` |
| `v-model` | Liaison bidirectionnelle | `v-model="email"` |
| `v-if` / `v-else-if` / `v-else` | Rendu conditionnel | `v-if="isAdmin"` |
| `v-show` | Affichage/masquage CSS | `v-show="isVisible"` |
| `v-for` | Rendu de liste | `v-for="item in items"` |
| `v-on:` / `@` | Écoute d'événements | `@click="handler"` |
| `v-html` | HTML brut (dangereux) | `v-html="htmlString"` |
| `v-once` | Rendu unique | `v-once` |
| `ref=""` | Référence DOM | `ref="monInput"` |

**Prochaine étape :** Les composants Vue 3 — props, emits, slots →
