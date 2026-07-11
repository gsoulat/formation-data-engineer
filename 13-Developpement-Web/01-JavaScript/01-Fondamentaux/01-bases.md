# 01 — Les bases de JavaScript : Variables, Types, Opérateurs

## Introduction

JavaScript est un langage de programmation **interprété**, **dynamiquement typé** et **orienté prototype**. Il s'exécute dans le navigateur (côté client) et aussi côté serveur grâce à Node.js.

Avant d'écrire la moindre ligne, comprenons l'environnement d'exécution.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir Chrome → F12 → onglet "Console" → taper `console.log("Bonjour JavaScript")` et appuyer sur Entrée
> **Expliquer :** La console du navigateur est l'environnement REPL de JavaScript. Tout code JS peut y être exécuté immédiatement. C'est l'outil numéro 1 pour tester et déboguer.

---

## 1. Déclarer des variables : `var`, `let`, `const`

JavaScript possède trois mots-clés pour déclarer des variables. Chacun a un comportement distinct qu'il est **crucial** de comprendre.

### `var` — L'ancienne façon (à éviter)

```javascript
var age = 25;
var age = 30; // Redéclaration autorisée — source de bugs !
console.log(age); // 30

// var est function-scoped (pas block-scoped)
function exemple() {
  if (true) {
    var x = 10; // Déclaré dans le bloc if...
  }
  console.log(x); // ...mais accessible ici ! → 10
}
exemple();

// Hoisting avec var
console.log(message); // undefined (pas d'erreur !)
var message = "bonjour";
console.log(message); // "bonjour"
```

**Pourquoi `var` est problématique :** la redéclaration silencieuse et le hoisting créent des bugs difficiles à trouver. N'utilisez plus `var` dans du code moderne.

### `let` — Variable mutable, à portée de bloc

```javascript
let compteur = 0;
compteur = 1;        // Réassignation autorisée
// let compteur = 2; // SyntaxError : déjà déclaré dans ce scope

// let est block-scoped
if (true) {
  let blockVar = "je suis dans le bloc";
  console.log(blockVar); // "je suis dans le bloc"
}
// console.log(blockVar); // ReferenceError : blockVar is not defined

// Pas de hoisting accessible
// console.log(valeur); // ReferenceError (Temporal Dead Zone)
let valeur = 42;
```

### `const` — Référence constante (recommandé par défaut)

```javascript
const PI = 3.14159;
// PI = 3; // TypeError : Assignment to constant variable

// IMPORTANT : const ne rend pas un objet immuable
const utilisateur = { nom: "Alice", age: 30 };
utilisateur.age = 31; // Autorisé ! On modifie la propriété, pas la référence
console.log(utilisateur.age); // 31

// utilisateur = {}; // TypeError : on ne peut pas rechanger la référence

const couleurs = ["rouge", "vert", "bleu"];
couleurs.push("jaune"); // Autorisé
console.log(couleurs); // ["rouge", "vert", "bleu", "jaune"]
// couleurs = []; // TypeError
```

### Règle d'utilisation recommandée

```
1. Utiliser const par défaut
2. Utiliser let si la variable doit être réassignée
3. Ne jamais utiliser var dans du code nouveau
```

---

## 2. Les types de données

JavaScript possède **8 types primitifs** et le type **Object**.

### Types primitifs

```javascript
// 1. Number — entiers ET décimaux dans le même type
const entier = 42;
const decimal = 3.14;
const negatif = -100;
const infini = Infinity;
const pasUnNombre = NaN; // résultat d'opérations invalides

console.log(typeof entier);   // "number"
console.log(typeof NaN);      // "number" (oui, NaN est de type number !)
console.log(isNaN(NaN));      // true
console.log(isNaN("abc"));    // true (coercion implicite — attention !)
console.log(Number.isNaN(NaN));   // true (plus fiable)
console.log(Number.isNaN("abc")); // false (pas de coercion)

// Limites des nombres
console.log(Number.MAX_SAFE_INTEGER); // 9007199254740991 (2^53 - 1)
console.log(Number.MIN_SAFE_INTEGER); // -9007199254740991

// 2. BigInt — pour les très grands entiers
const grandNombre = 9007199254740992n; // le 'n' indique BigInt
const autreGrand = BigInt("12345678901234567890");
console.log(typeof grandNombre); // "bigint"

// 3. String — chaînes de caractères
const simple = 'guillemets simples';
const double = "guillemets doubles";
const template = `template literal avec ${entier} interpolé`;
console.log(template); // "template literal avec 42 interpolé"

// Méthodes utiles des strings
const texte = "  Bonjour le Monde  ";
console.log(texte.trim());           // "Bonjour le Monde"
console.log(texte.toLowerCase());    // "  bonjour le monde  "
console.log(texte.toUpperCase());    // "  BONJOUR LE MONDE  "
console.log(texte.includes("le"));   // true
console.log(texte.replace("Monde", "JS")); // "  Bonjour le JS  "
console.log("abc".repeat(3));        // "abcabcabc"
console.log("hello".split(""));      // ["h", "e", "l", "l", "o"]

// Template literals multi-lignes
const html = `
  <div class="carte">
    <h2>${utilisateur.nom}</h2>
    <p>Age: ${utilisateur.age}</p>
  </div>
`;

// 4. Boolean
const vrai = true;
const faux = false;
console.log(typeof vrai); // "boolean"

// 5. undefined — variable déclarée mais non initialisée
let nonInitialisee;
console.log(nonInitialisee); // undefined
console.log(typeof nonInitialisee); // "undefined"

// 6. null — absence intentionnelle de valeur
const videIntentionnel = null;
console.log(typeof null); // "object" — BUG HISTORIQUE de JS, ne pas se fier à typeof null

// Distinguer null de undefined
console.log(null == undefined);  // true (égalité lâche)
console.log(null === undefined); // false (égalité stricte)

// 7. Symbol — identifiant unique
const sym1 = Symbol("description");
const sym2 = Symbol("description");
console.log(sym1 === sym2); // false — chaque Symbol est unique

// Usage typique : clés d'objet non conflictuelles
const ID = Symbol("id");
const objet = { [ID]: 123, nom: "test" };
console.log(objet[ID]); // 123
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — taper `typeof null` et montrer que le résultat est `"object"`, puis expliquer pourquoi c'est un bug historique qui ne peut pas être corrigé (compatibilité)
> **Expliquer :** Ce bug date de 1995. Corriger `typeof null` casserait des millions de sites web. C'est pourquoi on utilise `=== null` pour tester la nullité, jamais `typeof`.

---

### Le type Object

```javascript
// Object — tous les types non-primitifs
const obj = { a: 1, b: 2 };
const arr = [1, 2, 3];
const fn = function() {};
const date = new Date();

console.log(typeof obj);  // "object"
console.log(typeof arr);  // "object" (les tableaux SONT des objets)
console.log(typeof fn);   // "function" (exception : function a son propre typeof)
console.log(typeof date); // "object"

// Pour distinguer un tableau d'un objet ordinaire
console.log(Array.isArray(arr)); // true
console.log(Array.isArray(obj)); // false
```

---

## 3. Opérateurs

### Opérateurs arithmétiques

```javascript
const a = 10;
const b = 3;

console.log(a + b);  // 13 — addition
console.log(a - b);  // 7  — soustraction
console.log(a * b);  // 30 — multiplication
console.log(a / b);  // 3.3333... — division (toujours en virgule flottante)
console.log(a % b);  // 1  — modulo (reste de la division euclidienne)
console.log(a ** b); // 1000 — exponentiation (ES2016)

// Raccourcis d'assignation
let x = 10;
x += 5;  // x = x + 5 → 15
x -= 3;  // x = x - 3 → 12
x *= 2;  // x = x * 2 → 24
x /= 4;  // x = x / 4 → 6
x %= 4;  // x = x % 4 → 2
x **= 3; // x = x ** 3 → 8

// Incrémentation / Décrémentation
let n = 5;
console.log(n++); // 5 — retourne PUIS incrémente
console.log(n);   // 6
console.log(++n); // 7 — incrémente PUIS retourne
console.log(n--); // 7 — retourne PUIS décrémente
console.log(n);   // 6
```

### Opérateurs de comparaison

```javascript
// Égalité STRICTE (recommandée) — compare valeur ET type
console.log(5 === 5);     // true
console.log(5 === "5");   // false — types différents
console.log(null === undefined); // false

// Inégalité stricte
console.log(5 !== "5");   // true

// Égalité LÂCHE (à éviter) — effectue des coercions de type
console.log(5 == "5");    // true  — "5" est converti en nombre
console.log(0 == false);  // true  — false est converti en 0
console.log("" == false); // true  — les deux deviennent 0
console.log(null == undefined); // true
console.log(null == 0);  // false  — cas spécial

// Comparaisons d'ordre
console.log(5 > 3);   // true
console.log(5 >= 5);  // true
console.log(3 < 5);   // true
console.log(3 <= 2);  // false

// Comparaison de strings (ordre lexicographique Unicode)
console.log("abc" < "abd"); // true
console.log("Z" < "a");     // true (majuscules avant minuscules en ASCII)
```

### Les coercions de type — le piège majeur de JavaScript

```javascript
// Addition vs concaténation
console.log(1 + 2);       // 3 — addition numérique
console.log("1" + 2);     // "12" — concaténation (string prioritaire avec +)
console.log(1 + "2");     // "12"
console.log(1 + 2 + "3"); // "33" — évalué de gauche à droite : 3 + "3" = "33"
console.log("3" + 1 + 2); // "312"

// Les autres opérateurs convertissent vers number
console.log("6" - 2);  // 4
console.log("6" * 2);  // 12
console.log("6" / 2);  // 3
console.log("abc" - 1); // NaN

// Valeurs "falsy" (évaluées à false dans un contexte booléen)
const falsyValues = [false, 0, -0, 0n, "", '', ``, null, undefined, NaN];
falsyValues.forEach(v => console.log(`${String(v)} est falsy: ${!v}`));

// Toutes les autres valeurs sont "truthy"
console.log(Boolean({}));    // true — objet vide est truthy
console.log(Boolean([]));    // true — tableau vide est truthy !
console.log(Boolean("0"));   // true — string non-vide est truthy
console.log(Boolean(-1));    // true — tout nombre non-zéro est truthy
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — taper `[] == false` (true), `[] == ![]` (true), `{} + []` (0 ou "[object Object]" selon le contexte)
> **Expliquer :** Ces comportements surprenants viennent des règles de coercions. C'est PRÉCISÉMENT pour éviter ce genre de piège que l'on utilise TOUJOURS `===` (égalité stricte) en JavaScript moderne.

---

### Opérateurs logiques

```javascript
// ET logique (&&) — retourne le premier falsy OU le dernier opérande
console.log(true && true);   // true
console.log(true && false);  // false
console.log(1 && 2);         // 2 — 1 est truthy, retourne le second
console.log(0 && "test");    // 0 — 0 est falsy, retourne le premier (court-circuit)
console.log(null && "test"); // null

// OU logique (||) — retourne le premier truthy OU le dernier opérande
console.log(false || true);  // true
console.log(0 || "défaut");  // "défaut" — 0 est falsy
console.log("" || "backup"); // "backup"
console.log("valeur" || "backup"); // "valeur"
console.log(false || null);  // null — les deux sont falsy, retourne le dernier

// Usage classique : valeur par défaut
function saluer(nom) {
  const prenom = nom || "Anonyme"; // Si nom est falsy, utiliser "Anonyme"
  return `Bonjour, ${prenom}`;
}
console.log(saluer("Alice")); // "Bonjour, Alice"
console.log(saluer(""));      // "Bonjour, Anonyme" (string vide = falsy)
console.log(saluer(0));       // "Bonjour, Anonyme" (0 = falsy — piège !)

// NON logique (!)
console.log(!true);    // false
console.log(!false);   // true
console.log(!0);       // true
console.log(!"");      // true
console.log(!!"hello"); // true — double négation pour convertir en boolean
console.log(!!0);       // false

// Nullish Coalescing (??) — ES2020 : retourne le second opérande SEULEMENT si le premier est null ou undefined
console.log(null ?? "défaut");      // "défaut"
console.log(undefined ?? "défaut"); // "défaut"
console.log(0 ?? "défaut");         // 0 — 0 n'est PAS null/undefined
console.log("" ?? "défaut");        // "" — string vide n'est PAS null/undefined
console.log(false ?? "défaut");     // false

// Comparaison || vs ??
const port1 = 0 || 3000;  // 3000 — problème : 0 (port valide) est falsy
const port2 = 0 ?? 3000;  // 0    — correct : 0 n'est pas null/undefined
```

### Opérateur ternaire

```javascript
// condition ? valeurSiVrai : valeurSiFaux
const age = 20;
const statut = age >= 18 ? "majeur" : "mineur";
console.log(statut); // "majeur"

// Équivalent à :
let statut2;
if (age >= 18) {
  statut2 = "majeur";
} else {
  statut2 = "mineur";
}

// Ternaires imbriqués (à utiliser avec parcimonie)
const note = 75;
const mention = note >= 90 ? "Très bien"
             : note >= 70 ? "Bien"
             : note >= 50 ? "Passable"
             : "Insuffisant";
console.log(mention); // "Bien"
```

---

## 4. Structures de contrôle

### Conditions

```javascript
// if / else if / else
const temperature = 22;

if (temperature > 30) {
  console.log("Il fait chaud !");
} else if (temperature > 20) {
  console.log("Température agréable");
} else if (temperature > 10) {
  console.log("Un peu frais");
} else {
  console.log("Il fait froid !");
}

// switch — pour comparer une valeur à plusieurs cas
const jour = "lundi";
switch (jour) {
  case "lundi":
  case "mardi":
  case "mercredi":
  case "jeudi":
  case "vendredi":
    console.log("Jour de semaine");
    break;
  case "samedi":
  case "dimanche":
    console.log("Week-end !");
    break;
  default:
    console.log("Jour inconnu");
}
```

### Boucles

```javascript
// for classique
for (let i = 0; i < 5; i++) {
  console.log(`Itération ${i}`);
}

// while
let compteur = 0;
while (compteur < 3) {
  console.log(`Compteur : ${compteur}`);
  compteur++;
}

// do...while — s'exécute au moins une fois
let tentatives = 0;
do {
  console.log(`Tentative ${tentatives + 1}`);
  tentatives++;
} while (tentatives < 3);

// for...of — itérer sur les valeurs d'un itérable (tableau, string, Map, Set...)
const fruits = ["pomme", "banane", "cerise"];
for (const fruit of fruits) {
  console.log(fruit);
}

// for...in — itérer sur les CLÉS d'un objet
const personne = { nom: "Bob", age: 25, ville: "Paris" };
for (const cle in personne) {
  console.log(`${cle}: ${personne[cle]}`);
}
// Attention : for...in parcourt aussi les propriétés héritées via le prototype

// break et continue
for (let i = 0; i < 10; i++) {
  if (i === 3) continue; // Saute l'itération 3
  if (i === 7) break;    // Arrête la boucle à 7
  console.log(i);        // 0, 1, 2, 4, 5, 6
}
```

---

## 5. Conversion de types explicite

```javascript
// Vers Number
console.log(Number("42"));      // 42
console.log(Number("3.14"));    // 3.14
console.log(Number(""));        // 0
console.log(Number("abc"));     // NaN
console.log(Number(true));      // 1
console.log(Number(false));     // 0
console.log(Number(null));      // 0
console.log(Number(undefined)); // NaN

console.log(parseInt("42px"));    // 42 — s'arrête au premier caractère non-numérique
console.log(parseInt("0xFF", 16)); // 255 — base 16
console.log(parseFloat("3.14em")); // 3.14

// Vers String
console.log(String(42));        // "42"
console.log(String(true));      // "true"
console.log(String(null));      // "null"
console.log(String(undefined)); // "undefined"
console.log((42).toString());   // "42"
console.log((255).toString(16)); // "ff" — en hexadécimal

// Vers Boolean
console.log(Boolean(0));         // false
console.log(Boolean(""));        // false
console.log(Boolean(null));      // false
console.log(Boolean(undefined)); // false
console.log(Boolean(NaN));       // false
console.log(Boolean(1));         // true
console.log(Boolean("hello"));   // true
console.log(Boolean({}));        // true
```

---

## Récapitulatif

| Concept | Recommandation |
|---|---|
| Déclaration de variable | `const` par défaut, `let` si réassignation nécessaire, jamais `var` |
| Comparaison | Toujours `===` et `!==`, jamais `==` et `!=` |
| Valeur par défaut | `??` si la valeur peut légitimement être `0` ou `""`, sinon `||` |
| Vérification de tableau | `Array.isArray()`, jamais `typeof` |
| Vérification de null | `valeur === null`, jamais `typeof valeur === "object"` |
| Conversion en nombre | `Number()` pour valeurs entières et décimales, `parseInt()` pour les strings avec suffixe |

---

## Exercice rapide

```javascript
// Que va afficher ce code ? Répondez avant d'exécuter.

console.log(typeof null);          // ?
console.log(1 + "2" + 3);         // ?
console.log(true + true + "1");    // ?
console.log([] + []);              // ?
console.log([] + {});              // ?
console.log({} + []);              // ?  (attention au contexte !)
console.log(0 == "0");            // ?
console.log(0 === "0");           // ?
console.log(null == undefined);    // ?
console.log(null === undefined);   // ?

// Réponses :
// "object", "123", "21", "", "[object Object]", 0 ou "[object Object]" selon le contexte, true, false, true, false
```
