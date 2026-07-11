# 01 — JavaScript Moderne : Modules ES6, Optional Chaining, Nullish, Generators

## Introduction

ES6 (2015) a été une révolution pour JavaScript. Depuis, une nouvelle version de la spécification est publiée chaque année. Ce chapitre couvre les fonctionnalités modernes les plus importantes pour le développement quotidien.

---

## 1. Modules ES6 — import / export

Les modules permettent d'organiser le code en fichiers séparés avec des dépendances explicites.

### Exports

```javascript
// fichier: utils/math.js

// Export nommé — on peut en avoir plusieurs par fichier
export const PI = 3.14159265358979;

export function additionner(a, b) {
  return a + b;
}

export function multiplier(a, b) {
  return a * b;
}

export class Vecteur2D {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }

  additionner(autre) {
    return new Vecteur2D(this.x + autre.x, this.y + autre.y);
  }

  magnitude() {
    return Math.sqrt(this.x ** 2 + this.y ** 2);
  }

  toString() {
    return `Vecteur2D(${this.x}, ${this.y})`;
  }
}

// Export par défaut — UN SEUL par fichier
export default function calculerAire(largeur, hauteur) {
  return largeur * hauteur;
}

// Renommer lors de l'export
const interne = (a, b) => a - b;
export { interne as soustraire };
```

### Imports

```javascript
// fichier: main.js

// Import d'un export par défaut — le nom est libre
import calculerAire from "./utils/math.js";

// Import d'exports nommés — le nom DOIT correspondre
import { PI, additionner, Vecteur2D } from "./utils/math.js";

// Renommer lors de l'import
import { additionner as add, multiplier as mul } from "./utils/math.js";

// Importer tout dans un namespace
import * as Math2D from "./utils/math.js";
console.log(Math2D.PI);           // 3.14159...
console.log(Math2D.additionner(2, 3)); // 5
console.log(Math2D.default(10, 5));    // 50 (export default)

// Import par défaut ET nommés en même temps
import calculerAire2, { PI as PI2, Vecteur2D as Vec } from "./utils/math.js";

// Utilisation
console.log(PI);                // 3.14159...
console.log(additionner(2, 3)); // 5
console.log(calculerAire(10, 5)); // 50

const v1 = new Vecteur2D(3, 4);
console.log(v1.magnitude()); // 5
```

### Import dynamique — lazy loading

```javascript
// Import statique : chargé au démarrage
// Import dynamique : chargé à la demande

// Charger un module seulement quand nécessaire
async function chargerEditeur() {
  // Afficher un indicateur de chargement
  const indicateur = document.querySelector("#loading");
  indicateur.style.display = "block";

  try {
    // L'import() retourne une Promise
    const { default: Editeur, options } = await import("./editeur-riche.js");

    const editeur = new Editeur({
      conteneur: document.querySelector("#zone-edition"),
      ...options,
    });

    return editeur;
  } finally {
    indicateur.style.display = "none";
  }
}

// Charger un module selon une condition
async function chargerTheme(nomTheme) {
  const module = await import(`./themes/${nomTheme}.js`);
  module.appliquer();
}

document.querySelector("#btn-editeur").addEventListener("click", async () => {
  const editeur = await chargerEditeur();
  editeur.focus();
});
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** VS Code — ouvrir un projet avec plusieurs fichiers .js, montrer comment l'auto-complétion suggère les imports, puis dans l'onglet Network de DevTools montrer les fichiers .js chargés séparément (ou bundlés avec Vite/Webpack)
> **Expliquer :** En développement avec Vite, les modules ES6 natifs sont utilisés directement (HMR instantané). En production, Vite les bundle en quelques fichiers optimisés. C'est transparent mais important à comprendre.

---

## 2. Optional Chaining (?.)

L'opérateur `?.` permet d'accéder à des propriétés imbriquées sans risquer une erreur si l'un des intermédiaires est `null` ou `undefined`.

```javascript
const utilisateur = {
  nom: "Alice",
  adresse: {
    rue: "12 Rue de la Paix",
    ville: {
      nom: "Paris",
      codePostal: "75001",
    },
  },
  getProfil: () => ({ avatar: "/images/alice.jpg" }),
};

// Sans optional chaining — verbeux et fragile
function getVilleAncien(user) {
  if (user && user.adresse && user.adresse.ville) {
    return user.adresse.ville.nom;
  }
  return undefined;
}

// Avec optional chaining — concis et sûr
const ville = utilisateur?.adresse?.ville?.nom;
console.log(ville); // "Paris"

// Si l'utilisateur est null
const utilisateurNull = null;
const villeNull = utilisateurNull?.adresse?.ville?.nom;
console.log(villeNull); // undefined — pas d'erreur !

// Avec des tableaux
const premierTag = utilisateur?.tags?.[0];
const premierTagSecurise = utilisateur?.profil?.tags?.[0]?.label;

// Avec des appels de méthodes
const avatar = utilisateur?.getProfil?.()?.avatar;
console.log(avatar); // "/images/alice.jpg"

const methodeInexistante = utilisateur?.methodeQuiNExistePas?.();
console.log(methodeInexistante); // undefined

// Cas réels avec des données d'API
function afficherNomUtilisateur(reponseAPI) {
  // La réponse peut avoir différentes structures selon les erreurs
  const nom = reponseAPI?.data?.utilisateur?.profil?.nomComplet
            ?? reponseAPI?.data?.utilisateur?.email
            ?? "Utilisateur inconnu";

  return nom;
}

// Combinaison avec ?. dans les événements
document.querySelector("#bouton")?.addEventListener("click", handler);
// Ne lance pas d'erreur si #bouton n'existe pas dans la page
```

---

## 3. Nullish Coalescing Operator (??)

Voir section bases pour l'introduction — voici des cas d'usage avancés.

```javascript
// Différence cruciale avec ||
function configurerServeur(options = {}) {
  const port = options.port ?? 3000;     // 0 est un port valide
  const host = options.host ?? "localhost";
  const debug = options.debug ?? false;  // false est une valeur valide
  const timeout = options.timeout ?? 5000;
  const maxConns = options.maxConns ?? 100;

  console.log({ port, host, debug, timeout, maxConns });
}

configurerServeur({ port: 0, debug: false });
// { port: 0, host: "localhost", debug: false, timeout: 5000, maxConns: 100 }
// ✅ Correct : port=0 et debug=false sont préservés

// Avec || (problématique)
function configurerServeurAncien(options = {}) {
  const port = options.port || 3000; // BUG : port=0 devient 3000 !
  const debug = options.debug || false; // Pas de bug ici (false || false = false)
}

// Nullish Assignment (??=) — ES2021
let config = { titre: null, delai: undefined };
config.titre ??= "Titre par défaut";  // Assigne SEULEMENT si null ou undefined
config.delai ??= 1000;
config.autreChose ??= "valeur";  // Ajoute la propriété

console.log(config); // { titre: "Titre par défaut", delai: 1000, autreChose: "valeur" }

// Logical Assignment (||=, &&=) — ES2021
let a = null;
a ||= "défaut";    // a = a || "défaut" → "défaut"

let b = "existant";
b ||= "défaut";    // b = b || "défaut" → "existant" (inchangé)

let obj = { actif: true };
obj.actif &&= verifierAutorisation(); // Seulement si actif est truthy
```

---

## 4. Generators

Les generators sont des fonctions qui peuvent être mises en pause et reprises. Elles retournent un itérateur.

```javascript
// Syntaxe : function* (astérisque)
function* compterJusqua(max) {
  for (let i = 1; i <= max; i++) {
    yield i; // Pause et retourne la valeur
    // Reprend ici à l'appel suivant de next()
  }
}

const compteur = compterJusqua(5);
console.log(compteur.next()); // { value: 1, done: false }
console.log(compteur.next()); // { value: 2, done: false }
console.log(compteur.next()); // { value: 3, done: false }
console.log(compteur.next()); // { value: 4, done: false }
console.log(compteur.next()); // { value: 5, done: false }
console.log(compteur.next()); // { value: undefined, done: true }

// Les generators sont itérables — utilisables avec for...of
for (const n of compterJusqua(3)) {
  console.log(n); // 1, 2, 3
}

// Déstructuration avec un generator
const [a, b, c] = compterJusqua(10); // Prend seulement les 3 premiers
console.log(a, b, c); // 1, 2, 3

// Spread
const nombres = [...compterJusqua(5)]; // [1, 2, 3, 4, 5]
```

### Generators infinis

```javascript
// Un generator peut générer une séquence infinie
function* fibonacci() {
  let [a, b] = [0, 1];
  while (true) { // Boucle infinie — mais c'est OK avec yield
    yield a;
    [a, b] = [b, a + b];
  }
}

// Prendre les N premiers éléments d'un generator infini
function prendre(generateur, n) {
  const resultats = [];
  for (const valeur of generateur) {
    resultats.push(valeur);
    if (resultats.length >= n) break; // Sortir de la boucle arrête le generator
  }
  return resultats;
}

console.log(prendre(fibonacci(), 10));
// [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

// IDs uniques
function* generateurID(prefixe = "id") {
  let n = 1;
  while (true) {
    yield `${prefixe}-${String(n++).padStart(6, "0")}`;
  }
}

const genID = generateurID("USER");
console.log(genID.next().value); // "USER-000001"
console.log(genID.next().value); // "USER-000002"
console.log(genID.next().value); // "USER-000003"
```

### Generators comme itérateurs personnalisés

```javascript
// Rendre un objet itérable avec un generator
class Plage {
  constructor(debut, fin, pas = 1) {
    this.debut = debut;
    this.fin = fin;
    this.pas = pas;
  }

  // La méthode [Symbol.iterator] rend l'objet itérable
  *[Symbol.iterator]() {
    for (let i = this.debut; i <= this.fin; i += this.pas) {
      yield i;
    }
  }
}

const plage = new Plage(1, 10, 2);
console.log([...plage]); // [1, 3, 5, 7, 9]

for (const n of new Plage(0, 100, 10)) {
  process.stdout.write(n + " ");
}
// 0 10 20 30 40 50 60 70 80 90 100

// Generator avec délégation (yield*)
function* concat(...iterables) {
  for (const iter of iterables) {
    yield* iter; // Délègue à un autre itérable
  }
}

const resultat = [...concat([1, 2, 3], [4, 5], "abc")];
console.log(resultat); // [1, 2, 3, 4, 5, "a", "b", "c"]
```

---

## 5. Proxy et Reflect

```javascript
// Proxy intercepte les opérations sur un objet
const cible = { nom: "Alice", age: 30 };

const proxy = new Proxy(cible, {
  // Intercepter la lecture de propriétés
  get(objet, propriete, recepteur) {
    console.log(`Lecture de: ${propriete}`);
    return Reflect.get(objet, propriete, recepteur);
  },

  // Intercepter l'écriture
  set(objet, propriete, valeur, recepteur) {
    if (propriete === "age" && (typeof valeur !== "number" || valeur < 0)) {
      throw new TypeError("L'age doit être un nombre positif");
    }
    console.log(`Écriture de ${propriete} = ${valeur}`);
    return Reflect.set(objet, propriete, valeur, recepteur);
  },

  // Intercepter la suppression
  deleteProperty(objet, propriete) {
    if (propriete === "nom") throw new Error("Impossible de supprimer 'nom'");
    return Reflect.deleteProperty(objet, propriete);
  },
});

console.log(proxy.nom);    // "Lecture de: nom" + "Alice"
proxy.age = 31;            // "Écriture de age = 31"
// proxy.age = -5;         // TypeError: L'age doit être un nombre positif
// delete proxy.nom;       // Error: Impossible de supprimer 'nom'

// Cas d'usage réel : objet de configuration réactif (comme Vue.js 3)
function reactive(data, onChangement) {
  return new Proxy(data, {
    set(target, key, value) {
      const ancienneValeur = target[key];
      target[key] = value;
      if (ancienneValeur !== value) {
        onChangement(key, ancienneValeur, value);
      }
      return true;
    },
  });
}

const etat = reactive(
  { compteur: 0, message: "Bonjour" },
  (cle, ancien, nouveau) => {
    console.log(`${cle}: ${ancien} → ${nouveau}`);
    // Ici on pourrait re-rendre le composant
  }
);

etat.compteur++;          // "compteur: 0 → 1"
etat.message = "Salut";  // "message: Bonjour → Salut"
```

---

## 6. WeakRef et FinalizationRegistry

```javascript
// WeakRef — référence faible qui n'empêche pas le garbage collector
let objet = { nom: "Temporaire", taille: 1000000 };
const refFaible = new WeakRef(objet);

// On peut toujours accéder à l'objet via deref()
console.log(refFaible.deref()?.nom); // "Temporaire"

// Si 'objet' est mis à null, il peut être garbage collecté
// objet = null;
// Après GC : refFaible.deref() retourne undefined

// Cache avec cleanup automatique
const cache = new Map();

function cacher(cle, valeur) {
  cache.set(cle, new WeakRef(valeur));
}

function recuperer(cle) {
  return cache.get(cle)?.deref(); // undefined si GC a nettoyé
}
```

---

## 7. Fonctionnalités ES2023+ à connaître

```javascript
// Array.at() — accès depuis la fin avec index négatif
const fruits = ["pomme", "banane", "cerise", "datte"];
console.log(fruits.at(-1));  // "datte"
console.log(fruits.at(-2));  // "cerise"
console.log(fruits.at(0));   // "pomme"

// Object.hasOwn() — remplace hasOwnProperty
const obj = { a: 1 };
console.log(Object.hasOwn(obj, "a")); // true
console.log(Object.hasOwn(obj, "b")); // false

// Array.findLast() et findLastIndex()
const nombres = [1, 2, 3, 4, 5, 4, 3];
console.log(nombres.findLast(n => n < 4));      // 3 (le dernier < 4)
console.log(nombres.findLastIndex(n => n < 4)); // 6 (index du dernier < 4)

// toSorted(), toReversed(), toSpliced() — versions immutables
const original = [3, 1, 4, 1, 5];
const trie = original.toSorted((a, b) => a - b);
const inverse = original.toReversed();
const modifie = original.toSpliced(2, 1, 99); // Remplace index 2 par 99

console.log(original); // [3, 1, 4, 1, 5] — inchangé !
console.log(trie);     // [1, 1, 3, 4, 5]
console.log(inverse);  // [5, 1, 4, 1, 3]
console.log(modifie);  // [3, 1, 99, 1, 5]

// with() — remplacer un élément à un index (immutable)
const newArr = original.with(2, 99); // Remplace index 2 par 99
console.log(newArr);   // [3, 1, 99, 1, 5]
console.log(original); // [3, 1, 4, 1, 5] — inchangé

// Object.groupBy() — ES2024
const items = [
  { nom: "pomme", categorie: "fruit" },
  { nom: "carotte", categorie: "legume" },
  { nom: "banane", categorie: "fruit" },
  { nom: "brocoli", categorie: "legume" },
];

const parCategorie = Object.groupBy(items, item => item.categorie);
console.log(parCategorie);
// {
//   fruit: [{ nom: "pomme", ... }, { nom: "banane", ... }],
//   legume: [{ nom: "carotte", ... }, { nom: "brocoli", ... }]
// }
```

---

## Récapitulatif

| Feature | Depuis | Usage principal |
|---|---|---|
| `import/export` | ES6 | Organisation du code en modules |
| Import dynamique `import()` | ES2020 | Lazy loading |
| `?.` optional chaining | ES2020 | Accès sécurisé aux propriétés imbriquées |
| `??` nullish coalescing | ES2020 | Valeur par défaut pour null/undefined |
| `??=` `||=` `&&=` | ES2021 | Assignment conditionnel |
| `function*` generators | ES6 | Séquences lazy, itérateurs personnalisés |
| `Symbol.iterator` | ES6 | Rendre un objet itérable |
| `Proxy` | ES6 | Intercepter les opérations sur les objets |
| `Array.at(-1)` | ES2022 | Accès depuis la fin |
| `toSorted/toReversed` | ES2023 | Méthodes array immutables |
| `Object.groupBy` | ES2024 | Grouper des objets par propriété |
