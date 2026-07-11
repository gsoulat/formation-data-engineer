# Cheatsheet JavaScript — Référence Rapide

## Variables et Types

```javascript
// Déclaration
const x = 42;          // Référence constante (préféré)
let y = "hello";       // Variable réassignable
// var — à éviter

// Types
typeof 42               // "number"
typeof "str"            // "string"
typeof true             // "boolean"
typeof undefined        // "undefined"
typeof null             // "object" ← BUG HISTORIQUE
typeof {}               // "object"
typeof []               // "object"
typeof function(){}     // "function"
Array.isArray([])       // true

// Conversions
Number("42")            // 42
String(42)              // "42"
Boolean(0)              // false — valeurs falsy: 0, "", null, undefined, NaN, false
parseInt("42px")        // 42
parseFloat("3.14")      // 3.14
```

---

## Opérateurs

```javascript
// Arithmétique
5 + 3   // 8     | 5 - 3  // 2
5 * 3   // 15    | 5 / 3  // 1.666
5 % 3   // 2     | 5 ** 3 // 125 (exponentiation)

// Comparaison (TOUJOURS utiliser ===)
5 === 5     // true  | 5 === "5"  // false
5 !== "5"   // true  | 5 == "5"   // true (NE PAS utiliser)

// Logiques
&&    // ET   | ||   // OU  | !    // NON
??    // Nullish: valeur si null/undefined (pas si 0 ou "")
?.    // Optional chaining: objet?.prop?.methode?.()

// Assignation
x += 1  | x -= 1  | x *= 2  | x /= 2
x ??= "défaut"    // Assigne seulement si null/undefined
x ||= "défaut"    // Assigne si falsy
x &&= transformer() // Assigne si truthy

// Ternaire
condition ? valeurSiVrai : valeurSiFaux
```

---

## Strings

```javascript
const s = "Hello World";

s.length            // 11
s.toUpperCase()     // "HELLO WORLD"
s.toLowerCase()     // "hello world"
s.trim()            // Supprime espaces début/fin
s.includes("World") // true
s.startsWith("He")  // true
s.endsWith("ld")    // true
s.indexOf("o")      // 4
s.slice(0, 5)       // "Hello"
s.split(" ")        // ["Hello", "World"]
s.replace("l", "L") // "HeLlo World" (premier uniquement)
s.replaceAll("l","L") // "HeLLo WorLd"
s.repeat(2)         // "Hello WorldHello World"
s.padStart(15, "*") // "****Hello World"
s.padEnd(15, "*")   // "Hello World****"
s.at(-1)            // "d"

// Template literals
`Bonjour ${nom}, vous avez ${age} ans`
`Multilignes
sont supportées`
```

---

## Tableaux

```javascript
const arr = [1, 2, 3, 4, 5];

// Accès
arr[0]              // 1
arr.at(-1)          // 5
arr.length          // 5

// Modification (mutent le tableau)
arr.push(6)         // Ajoute à la fin → [1,2,3,4,5,6]
arr.pop()           // Retire la fin → retourne 6
arr.unshift(0)      // Ajoute au début → [0,1,2,3,4,5]
arr.shift()         // Retire le début → retourne 0
arr.splice(1, 2)    // Retire 2 éléments à partir de l'index 1
arr.sort((a,b)=>a-b) // Trie (mute !)
arr.reverse()       // Inverse (mute !)

// Sans mutation (retournent un nouveau tableau)
arr.map(x => x * 2)           // [2,4,6,8,10]
arr.filter(x => x > 2)        // [3,4,5]
arr.reduce((acc,x) => acc+x, 0) // 15
arr.slice(1, 3)               // [2,3] (de 1 inclus à 3 exclus)
arr.concat([6,7])             // [1,2,3,4,5,6,7]
arr.toSorted((a,b)=>b-a)      // [5,4,3,2,1] (ES2023)
arr.toReversed()              // [5,4,3,2,1] (ES2023)
arr.with(2, 99)               // [1,2,99,4,5] (ES2023)
[...arr]                      // Copie superficielle

// Recherche
arr.find(x => x > 3)         // 4
arr.findIndex(x => x > 3)    // 3
arr.findLast(x => x < 4)     // 3
arr.indexOf(3)               // 2
arr.includes(3)              // true
arr.some(x => x > 4)         // true
arr.every(x => x > 0)        // true

// Transformation
arr.flat()                    // Aplatit d'un niveau
arr.flatMap(x => [x, x*2])   // map + flat
Array.from({length:5}, (_,i) => i) // [0,1,2,3,4]
[...new Set(arr)]            // Valeurs uniques
```

---

## Objets

```javascript
const obj = { a: 1, b: 2, c: 3 };

// Accès
obj.a          // 1
obj["a"]       // 1 (clé dynamique)
obj?.a         // 1 (optional chaining)

// Manipulation
Object.keys(obj)     // ["a","b","c"]
Object.values(obj)   // [1,2,3]
Object.entries(obj)  // [["a",1],["b",2],["c",3]]
Object.assign({}, obj, { d: 4 })   // Fusion
{ ...obj, d: 4 }                    // Spread (préféré)
Object.freeze(obj)   // Immutable
Object.fromEntries([["a",1]])       // { a: 1 }
Object.hasOwn(obj, "a")            // true
"a" in obj           // true

// Destructuring
const { a, b } = obj
const { a: alpha, c: gamma = 99 } = obj  // Renommer + défaut
const { a: first, ...reste } = obj        // Rest

// Copie profonde
structuredClone(obj)               // Deep copy (moderne)
JSON.parse(JSON.stringify(obj))    // Deep copy (limité)
```

---

## Fonctions

```javascript
// Déclaration (hoistée)
function add(a, b) { return a + b; }

// Expression
const add = function(a, b) { return a + b; };

// Arrow function
const add = (a, b) => a + b;
const double = n => n * 2;
const getObj = () => ({ key: "value" }); // Retourner un objet

// Paramètres
function fn(a, b = 10, ...reste) {}      // Défaut + rest
fn(1, undefined, 3, 4)                   // b=10, reste=[3,4]

// Destructuring dans les paramètres
function fn({ nom, age = 18 }) {}
function fn([premier, ...autres]) {}
```

---

## Asynchrone

```javascript
// Promise
const p = new Promise((resolve, reject) => {
  setTimeout(() => resolve("OK"), 1000);
});

p.then(v => console.log(v))
 .catch(e => console.error(e))
 .finally(() => console.log("Terminé"));

Promise.all([p1, p2, p3])       // Attend toutes (échoue si une échoue)
Promise.allSettled([p1, p2])    // Attend toutes (retourne statuts)
Promise.race([p1, p2])          // Première résolue OU rejetée
Promise.any([p1, p2])           // Première résolue (ignore les rejets)

// async/await
async function charger(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error(err);
    throw err;
  }
}

// Parallèle (rapide)
const [a, b] = await Promise.all([fetch("/a"), fetch("/b")]);

// Séquentiel (lent, seulement si b dépend de a)
const a = await fetch("/a");
const b = await fetch(`/${a.id}`);
```

---

## Fetch API

```javascript
// GET
const data = await fetch("/api/users").then(r => r.json());

// POST
const res = await fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ nom: "Alice" }),
});

// Vérification — fetch ne rejette PAS sur 404/500 !
if (!res.ok) throw new Error(`HTTP ${res.status}`);

// Headers Auth
headers: { "Authorization": `Bearer ${token}` }

// Query params
`/api?${new URLSearchParams({ page: 1, limit: 10 })}`

// Annulation
const ctrl = new AbortController();
fetch(url, { signal: ctrl.signal });
ctrl.abort();
```

---

## DOM

```javascript
// Sélection
document.querySelector(".classe")        // Premier
document.querySelectorAll("div.item")    // Tous (NodeList)
document.getElementById("id")           // Par ID

// Modification
el.textContent = "texte"    // Texte sécurisé
el.innerHTML = "<b>html</b>" // HTML (risque XSS !)
el.setAttribute("src", url)
el.removeAttribute("href")
el.dataset.userId           // Lire data-user-id
el.classList.add("actif")
el.classList.remove("actif")
el.classList.toggle("actif")
el.classList.contains("actif") // true/false
el.style.color = "red"

// Création / Insertion
const el = document.createElement("div");
parent.appendChild(el)
parent.prepend(el)
el.remove()
el.replaceWith(newEl)

// Navigation
el.parentElement
el.children          // Enfants éléments
el.nextElementSibling
el.closest(".selecteur")

// Événements
el.addEventListener("click", handler)
el.removeEventListener("click", handler)
event.preventDefault()    // Empêche défaut (ex: submit)
event.stopPropagation()   // Arrête le bubbling
event.target              // Élément cliqué
event.currentTarget       // Élément avec l'écouteur
```

---

## Modules ES6

```javascript
// Export
export const PI = 3.14;
export function add(a, b) { return a + b; }
export default class Main {}

// Import
import Main from "./main.js";
import { PI, add } from "./utils.js";
import { PI as pi } from "./utils.js";   // Renommer
import * as utils from "./utils.js";      // Namespace
const module = await import("./lazy.js"); // Dynamique
```

---

## Classes

```javascript
class Animal {
  #nom;                              // Champ privé
  static nombreInstances = 0;        // Statique

  constructor(nom) {
    Animal.nombreInstances++;
    this.#nom = nom;
  }

  get nom() { return this.#nom; }    // Getter

  parler() {
    return `${this.#nom} fait du bruit`;
  }

  static creer(nom) {                // Méthode statique
    return new Animal(nom);
  }
}

class Chien extends Animal {
  constructor(nom, race) {
    super(nom);                      // Appel constructeur parent
    this.race = race;
  }

  parler() {
    return `${super.parler()} (aboie)`;
  }
}
```

---

## Destructuring & Spread

```javascript
// Objet
const { a, b, c = 0 } = obj;           // Avec défaut
const { a: alpha } = obj;               // Renommer
const { a, ...reste } = obj;            // Rest

// Tableau
const [x, y, z] = arr;
const [, second] = arr;                 // Ignorer
const [first, ...others] = arr;         // Rest
[a, b] = [b, a];                        // Swap

// Spread
const merged = { ...obj1, ...obj2 };
const combined = [...arr1, ...arr2];
const copy = { ...obj };               // Shallow copy
```

---

## Patterns utiles

```javascript
// Valeur par défaut (préférer ?? à ||)
const port = options.port ?? 3000;

// Accès sécurisé imbriqué
const city = user?.address?.city?.name ?? "Inconnue";

// Dédupliquer un tableau
const unique = [...new Set(arr)];

// Grouper par propriété
const groupes = items.reduce((acc, item) => {
  (acc[item.type] ??= []).push(item);
  return acc;
}, {});

// Debounce
function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

// Throttle
function throttle(fn, ms) {
  let dernier = 0;
  return (...args) => {
    const maintenant = Date.now();
    if (maintenant - dernier >= ms) {
      dernier = maintenant;
      fn(...args);
    }
  };
}

// Copie profonde
const deepCopy = structuredClone(obj);

// Vérification de type sécurisée
Object.prototype.toString.call([]) // "[object Array]"
Object.prototype.toString.call({}) // "[object Object]"
```
