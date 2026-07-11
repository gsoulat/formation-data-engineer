# Composants Vue 3

## Qu'est-ce qu'un composant ?

Un composant est un bloc de code réutilisable qui encapsule son propre template, sa logique et ses styles. L'idée est de décomposer l'interface en pièces indépendantes que l'on peut assembler comme des briques.

```
App.vue
├── NavBar.vue
│   ├── NavLink.vue
│   └── NavLink.vue
├── ProductList.vue
│   ├── ProductCard.vue
│   ├── ProductCard.vue
│   └── ProductCard.vue
└── Footer.vue
```

## Créer et utiliser un composant

### Composant enfant

```vue
<!-- src/components/BoutonPrincipal.vue -->
<template>
  <button class="btn-principal" :disabled="disabled">
    <slot>Cliquer</slot>
  </button>
</template>

<script setup>
defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.btn-principal {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-principal:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
```

### Composant parent — importer et utiliser

```vue
<!-- src/views/HomeView.vue -->
<template>
  <div>
    <!-- Le composant est utilisé comme une balise HTML -->
    <BoutonPrincipal>Valider</BoutonPrincipal>
    <BoutonPrincipal :disabled="true">Désactivé</BoutonPrincipal>
    <BoutonPrincipal /><!-- utilise le texte par défaut du slot -->
  </div>
</template>

<script setup>
// Avec <script setup>, l'import suffit — pas besoin de "components: {}"
import BoutonPrincipal from '@/components/BoutonPrincipal.vue'
</script>
```

## Props — Passer des données parent → enfant

Les props sont les paramètres que le parent transmet à l'enfant.

### Déclaration des props avec `defineProps`

```vue
<!-- src/components/CarteUtilisateur.vue -->
<template>
  <div class="carte">
    <img :src="avatar" :alt="`Avatar de ${prenom}`" class="avatar" />
    <div class="infos">
      <h3>{{ prenom }} {{ nom }}</h3>
      <p class="role" :class="`role-${role}`">{{ role }}</p>
      <p v-if="bio">{{ bio }}</p>
      <span class="badge" v-if="estActif">Actif</span>
    </div>
  </div>
</template>

<script setup>
// Définition des props avec validation
const props = defineProps({
  prenom: {
    type: String,
    required: true,
  },
  nom: {
    type: String,
    required: true,
  },
  role: {
    type: String,
    default: 'utilisateur',
    validator: (valeur) => ['admin', 'moderateur', 'utilisateur'].includes(valeur),
  },
  avatar: {
    type: String,
    default: '/images/avatar-defaut.png',
  },
  bio: {
    type: String,
    default: null, // optionnel
  },
  estActif: {
    type: Boolean,
    default: false,
  },
  score: {
    type: Number,
    default: 0,
  },
})

// On peut accéder aux props via props.prenom, props.nom, etc.
// Mais dans le template on utilise directement prenom, nom, etc.
console.log('Props reçues :', props.prenom, props.nom)
</script>

<style scoped>
.carte {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
}
.role-admin { color: red; font-weight: bold; }
.role-moderateur { color: orange; }
.role-utilisateur { color: gray; }
.badge {
  background: #42b883;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}
</style>
```

### Utilisation du composant avec props

```vue
<!-- src/views/EquipeView.vue -->
<template>
  <div>
    <h1>Notre équipe</h1>

    <!-- Props statiques (chaînes sans :) -->
    <CarteUtilisateur
      prenom="Alice"
      nom="Dubois"
      role="admin"
      :est-actif="true"
    />

    <!-- Props dynamiques (avec :) -->
    <CarteUtilisateur
      v-for="membre in equipe"
      :key="membre.id"
      :prenom="membre.prenom"
      :nom="membre.nom"
      :role="membre.role"
      :avatar="membre.avatar"
      :bio="membre.bio"
      :est-actif="membre.actif"
    />

    <!-- Passer toutes les propriétés d'un objet avec v-bind -->
    <CarteUtilisateur v-bind="membreSpecial" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CarteUtilisateur from '@/components/CarteUtilisateur.vue'

const equipe = ref([
  {
    id: 1,
    prenom: 'Bob',
    nom: 'Martin',
    role: 'moderateur',
    avatar: null,
    bio: 'Expert Vue.js',
    actif: true,
  },
  {
    id: 2,
    prenom: 'Clara',
    nom: 'Petit',
    role: 'utilisateur',
    avatar: null,
    bio: null,
    actif: false,
  },
])

// v-bind sur un objet — les clés doivent correspondre aux noms de props
const membreSpecial = ref({
  prenom: 'Diana',
  nom: 'Leroy',
  role: 'admin',
  estActif: true,
  bio: 'Fondatrice',
})
</script>
```

> **Règle fondamentale :** Les props sont **read-only** dans l'enfant. Ne jamais modifier directement une prop. Si l'enfant doit modifier la valeur, il doit émettre un événement vers le parent.

## Emits — Communiquer enfant → parent

L'enfant ne peut pas modifier les props du parent directement. Il utilise `defineEmits` pour émettre des événements.

```vue
<!-- src/components/FormulaireCommentaire.vue -->
<template>
  <form @submit.prevent="soumettre" class="formulaire">
    <textarea
      v-model="texte"
      :maxlength="maxCaracteres"
      placeholder="Votre commentaire..."
      rows="4"
    ></textarea>
    <div class="footer-form">
      <span :class="{ 'presque-plein': texte.length > maxCaracteres * 0.8 }">
        {{ texte.length }} / {{ maxCaracteres }}
      </span>
      <div class="boutons">
        <button type="button" @click="annuler">Annuler</button>
        <button type="submit" :disabled="!texte.trim()">Publier</button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  maxCaracteres: {
    type: Number,
    default: 280,
  },
})

// Déclarer les événements que ce composant peut émettre
const emit = defineEmits({
  // Validation optionnelle de la payload
  soumettre: (commentaire) => {
    return typeof commentaire === 'string' && commentaire.trim().length > 0
  },
  annuler: null, // pas de payload, pas de validation
})

const texte = ref('')

function soumettre() {
  if (!texte.value.trim()) return

  // Émettre l'événement avec la payload
  emit('soumettre', texte.value.trim())
  texte.value = '' // Réinitialiser après soumission
}

function annuler() {
  texte.value = ''
  emit('annuler')
}
</script>
```

```vue
<!-- Utilisation dans le parent -->
<template>
  <div>
    <h2>Commentaires ({{ commentaires.length }})</h2>

    <!-- Écoute des événements émis par l'enfant -->
    <FormulaireCommentaire
      :max-caracteres="500"
      @soumettre="ajouterCommentaire"
      @annuler="() => console.log('Annulé')"
    />

    <div v-for="c in commentaires" :key="c.id" class="commentaire">
      <p>{{ c.texte }}</p>
      <small>{{ c.date }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FormulaireCommentaire from '@/components/FormulaireCommentaire.vue'

const commentaires = ref([])

function ajouterCommentaire(texte) {
  commentaires.value.push({
    id: Date.now(),
    texte,
    date: new Date().toLocaleDateString('fr-FR'),
  })
}
</script>
```

## Slots — Injection de contenu

Les slots permettent au parent d'injecter du contenu HTML dans l'enfant.

### Slot par défaut

```vue
<!-- src/components/Carte.vue -->
<template>
  <div class="carte">
    <div class="carte-header" v-if="titre">
      <h3>{{ titre }}</h3>
    </div>
    <div class="carte-body">
      <!-- slot par défaut — le contenu vient du parent -->
      <slot>
        <p class="placeholder">Aucun contenu fourni.</p>
      </slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  titre: String,
})
</script>
```

```vue
<!-- Utilisation -->
<Carte titre="Mes statistiques">
  <p>Ventes : <strong>1 234</strong></p>
  <p>Visites : <strong>5 678</strong></p>
</Carte>

<Carte>
  <!-- Utilise le contenu par défaut du slot -->
</Carte>
```

### Slots nommés

```vue
<!-- src/components/MiseEnPage.vue -->
<template>
  <div class="layout">
    <header>
      <!-- Slot nommé "header" -->
      <slot name="header">
        <h1>Titre par défaut</h1>
      </slot>
    </header>

    <aside>
      <slot name="sidebar" />
    </aside>

    <main>
      <!-- Slot par défaut (sans nom) -->
      <slot />
    </main>

    <footer>
      <slot name="footer">
        <p>© 2024 Mon App</p>
      </slot>
    </footer>
  </div>
</template>
```

```vue
<!-- Utilisation des slots nommés -->
<MiseEnPage>
  <!-- Syntaxe v-slot:nomDuSlot ou #nomDuSlot (raccourci) -->
  <template #header>
    <h1>Tableau de bord</h1>
    <p>Bienvenue, {{ utilisateur }}</p>
  </template>

  <template #sidebar>
    <nav>
      <a href="#">Accueil</a>
      <a href="#">Profil</a>
    </nav>
  </template>

  <!-- Contenu du slot par défaut — sans template -->
  <p>Contenu principal de la page</p>
  <p>Ici va le contenu principal.</p>

  <template #footer>
    <p>Personnalisé — Dernière connexion : {{ dateDernierConnexion }}</p>
  </template>
</MiseEnPage>
```

### Scoped Slots — données de l'enfant vers le parent

```vue
<!-- src/components/ListeGenerique.vue -->
<template>
  <ul>
    <li v-for="(item, index) in items" :key="item.id">
      <!-- Le slot expose les données de l'enfant au parent -->
      <slot :item="item" :index="index" :estDernier="index === items.length - 1">
        <!-- Rendu par défaut si le parent ne fournit pas de slot -->
        {{ item }}
      </slot>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
  },
})
</script>
```

```vue
<!-- Utilisation avec scoped slot -->
<ListeGenerique :items="produits">
  <!-- v-slot="{ item, index, estDernier }" destructure les données exposées -->
  <template #default="{ item, index, estDernier }">
    <div :class="{ 'dernier': estDernier }">
      <span class="numero">{{ index + 1 }}</span>
      <strong>{{ item.nom }}</strong>
      <span class="prix">{{ item.prix }}€</span>
    </div>
  </template>
</ListeGenerique>
```

## Cycle de vie des composants

Vue appelle des hooks à chaque étape du cycle de vie d'un composant.

```vue
<template>
  <div>
    <p>Compteur : {{ compteur }}</p>
    <button @click="compteur++">Incrémenter</button>
  </div>
</template>

<script setup>
import {
  ref,
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
} from 'vue'

const compteur = ref(0)

// Avant que le composant soit monté dans le DOM
onBeforeMount(() => {
  console.log('onBeforeMount — DOM pas encore créé')
})

// Après que le composant est monté — accès au DOM disponible
onMounted(() => {
  console.log('onMounted — DOM disponible, parfait pour les appels API !')
  // C'est ici qu'on fait généralement les fetch() initiaux
  chargerDonnees()
})

// Avant chaque mise à jour du DOM
onBeforeUpdate(() => {
  console.log('onBeforeUpdate — le DOM va être mis à jour')
})

// Après chaque mise à jour du DOM
onUpdated(() => {
  console.log('onUpdated — DOM mis à jour, compteur =', compteur.value)
})

// Avant que le composant soit démonté
onBeforeUnmount(() => {
  console.log('onBeforeUnmount — nettoyage avant démontage')
  // Nettoyer les écouteurs d'événements, intervals, etc.
})

// Après le démontage — le composant n'existe plus dans le DOM
onUnmounted(() => {
  console.log('onUnmounted — composant complètement détruit')
})

async function chargerDonnees() {
  // Simulation d'un appel API
  console.log('Chargement des données...')
}
</script>
```

### Diagramme du cycle de vie

```
Création de l'instance
       │
onBeforeMount()        ← DOM pas encore créé
       │
   Rendu initial du DOM
       │
onMounted()            ← DOM disponible ✓ → IDEAL pour les appels API
       │
   (données changent)
       │
onBeforeUpdate()       ← avant chaque re-render
       │
   Re-rendu du DOM
       │
onUpdated()            ← après chaque re-render
       │
   (composant retiré)
       │
onBeforeUnmount()      ← avant destruction
       │
   Démontage
       │
onUnmounted()          ← après destruction → nettoyer ici
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console du navigateur (F12) pendant le montage/démontage d'un composant conditionnel
> **Expliquer :** Créer un composant avec tous les hooks de cycle de vie qui loggent dans la console. Utiliser un `v-if` pour monter et démonter le composant. Observer l'ordre des logs dans la console pour bien comprendre le cycle. Insister sur `onMounted` comme le bon endroit pour les appels API.
---

## `defineExpose` — Exposer des méthodes vers le parent

Par défaut, `<script setup>` est complètement encapsulé. Si le parent a besoin d'appeler une méthode de l'enfant via une template ref, l'enfant doit l'exposer explicitement.

```vue
<!-- src/components/ModalDialog.vue -->
<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="fermer">
      <div class="modal-content">
        <button class="btn-fermer" @click="fermer">×</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)

function ouvrir() {
  visible.value = true
}

function fermer() {
  visible.value = false
}

// Exposer les méthodes pour que le parent puisse les appeler
defineExpose({ ouvrir, fermer })
</script>
```

```vue
<!-- Utilisation dans le parent -->
<template>
  <div>
    <button @click="maModal.ouvrir()">Ouvrir la modal</button>

    <ModalDialog ref="maModal">
      <h2>Contenu de la modal</h2>
      <p>Ce contenu est injecté via le slot.</p>
      <button @click="maModal.fermer()">Fermer</button>
    </ModalDialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ModalDialog from '@/components/ModalDialog.vue'

const maModal = ref(null) // sera l'instance exposée du composant
</script>
```

## Composants asynchrones avec `defineAsyncComponent`

Pour le chargement différé (lazy loading) de composants lourds :

```typescript
// src/views/DashboardView.vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Le composant n'est chargé que quand il est rendu pour la première fois
const GraphiqueVentes = defineAsyncComponent(() =>
  import('@/components/GraphiqueVentes.vue')
)

// Avec options avancées
const EditeurTexte = defineAsyncComponent({
  loader: () => import('@/components/EditeurTexte.vue'),
  loadingComponent: () => import('@/components/Chargement.vue'),
  errorComponent: () => import('@/components/Erreur.vue'),
  delay: 200,    // ms avant d'afficher le loading
  timeout: 5000, // ms avant d'afficher l'erreur
})
</script>
```

## Composants built-in de Vue 3

### `<Transition>` — animations CSS

```vue
<template>
  <button @click="visible = !visible">Toggle</button>

  <!-- Vue ajoute des classes CSS pendant les transitions -->
  <Transition name="fondu">
    <p v-if="visible">Ce texte apparaît avec une animation !</p>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'
const visible = ref(true)
</script>

<style>
/* Classes générées par Vue: .fondu-enter-active, .fondu-leave-active, etc. */
.fondu-enter-active,
.fondu-leave-active {
  transition: opacity 0.4s ease;
}
.fondu-enter-from,
.fondu-leave-to {
  opacity: 0;
}
</style>
```

### `<KeepAlive>` — préserver l'état

```vue
<template>
  <!-- KeepAlive garde le composant en mémoire quand il est masqué -->
  <KeepAlive>
    <MonFormulaireComplexe v-if="afficherFormulaire" />
  </KeepAlive>
  <!-- Sans KeepAlive, l'état du formulaire serait perdu à chaque toggle -->
</template>
```

## Résumé

| Concept | Description | Syntaxe |
|---|---|---|
| Composant | Bloc de code réutilisable | Fichier `.vue` |
| Props | Données parent → enfant | `defineProps({ ... })` |
| Emits | Événements enfant → parent | `defineEmits([...])` |
| Slot par défaut | Injection de contenu | `<slot />` |
| Slots nommés | Plusieurs zones de contenu | `<slot name="header" />` |
| Scoped slots | Données enfant → slot | `<slot :item="item" />` |
| Cycle de vie | Hooks d'exécution | `onMounted`, `onUnmounted`... |
| defineExpose | Exposer des méthodes | `defineExpose({ methode })` |

**Prochaine étape :** La Composition API — ref, reactive, computed, watch →
