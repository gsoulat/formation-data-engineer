# 02 — Fonctions : Déclarations, Expressions, Arrow Functions, Closures, IIFE

## Introduction

Les fonctions sont au cœur de JavaScript. Elles ne sont pas de simples blocs de code réutilisables : en JavaScript, les fonctions sont des **valeurs de première classe** (*first-class citizens*). Cela signifie qu'elles peuvent être stockées dans des variables, passées en argument, retournées par d'autres fonctions — exactement comme un nombre ou une chaîne de caractères.

---

## 1. Les différentes façons de déclarer une fonction

### Déclaration de fonction (*Function Declaration*)

```javascript
// Syntaxe classique avec le mot-clé function
function additionner(a, b) {
  return a + b;
}

console.log(additionner(3, 5)); // 8

// Particularité : HOISTING
// Les function declarations sont entièrement "hissées" en haut du scope
// On peut appeler la fonction AVANT sa déclaration dans le code
const resultat = multiplier(4, 5); // Fonctionne !
console.log(resultat); // 20

function multiplier(x, y) {
  return x * y;
}
```

### Expression de fonction (*Function Expression*)

```javascript
// La fonction est assignée à une variable
const soustraire = function(a, b) {
  return a - b;
};

console.log(soustraire(10, 4)); // 6

// PAS de hoisting : impossible d'appeler avant la déclaration
// console.log(diviser(10, 2)); // ReferenceError ou TypeError

const diviser = function(a, b) {
  if (b === 0) throw new Error("Division par zéro");
  return a / b;
};

// Expression de fonction nommée — utile pour le débogage (le nom apparaît dans la stack trace)
const factorielle = function calc(n) {
  if (n <= 1) return 1;
  return n * calc(n - 1); // On peut référencer calc à l'intérieur
};

console.log(factorielle(5)); // 120
// calc(5); // ReferenceError — calc n'est pas accessible à l'extérieur
```

### Arrow Function (ES6) — La syntaxe moderne

```javascript
// Syntaxe complète
const saluer = (prenom) => {
  const message = `Bonjour, ${prenom} !`;
  return message;
};

// Avec un seul paramètre : parenthèses optionnelles
const doubler = n => {
  return n * 2;
};

// Corps à une seule expression : return implicite (sans accolades)
const tripler = n => n * 3;
const carre = n => n ** 2;

console.log(saluer("Alice")); // "Bonjour, Alice !"
console.log(doubler(5));      // 10
console.log(tripler(5));      // 15
console.log(carre(4));        // 16

// Retourner un objet littéral : entourer de parenthèses (sinon les {} sont interprétés comme un bloc)
const creerUtilisateur = (nom, age) => ({ nom, age });
// Équivalent à : const creerUtilisateur = (nom, age) => { return { nom, age }; };

console.log(creerUtilisateur("Bob", 30)); // { nom: "Bob", age: 30 }

// Sans paramètres : parenthèses obligatoires
const direBonjour = () => "Bonjour !";
console.log(direBonjour()); // "Bonjour !"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Écrire les trois syntaxes côte à côte dans VS Code, puis dans la console — montrer que le résultat est identique pour les trois formes de la même fonction
> **Expliquer :** La syntaxe arrow function est la plus utilisée dans React et le JS moderne. La différence principale n'est pas que la syntaxe — c'est le comportement de `this` (abordé en section 5).

---

### Différence cruciale : `this` dans les arrow functions

```javascript
// Avec une function classique, 'this' dépend du contexte d'appel
const minuteur1 = {
  nom: "Timer classique",
  demarrer: function() {
    console.log(`Démarrage: ${this.nom}`); // "Timer classique"

    // Dans le callback setTimeout, 'this' perd son contexte !
    setTimeout(function() {
      console.log(`Dans setTimeout: ${this.nom}`); // undefined (ou erreur en strict mode)
    }, 100);
  }
};

// Avec une arrow function, 'this' est hérité du contexte parent (lexical)
const minuteur2 = {
  nom: "Timer arrow",
  demarrer: function() {
    console.log(`Démarrage: ${this.nom}`); // "Timer arrow"

    // Arrow function hérite du 'this' de demarrer()
    setTimeout(() => {
      console.log(`Dans setTimeout: ${this.nom}`); // "Timer arrow"
    }, 100);
  }
};

minuteur1.demarrer();
minuteur2.demarrer();
```

---

## 2. Paramètres et arguments

### Paramètres par défaut (ES6)

```javascript
function creerProfil(nom, age = 18, ville = "Paris") {
  return { nom, age, ville };
}

console.log(creerProfil("Alice"));              // { nom: "Alice", age: 18, ville: "Paris" }
console.log(creerProfil("Bob", 25));             // { nom: "Bob", age: 25, ville: "Paris" }
console.log(creerProfil("Carol", 30, "Lyon"));   // { nom: "Carol", age: 30, ville: "Lyon" }

// On peut utiliser undefined pour forcer la valeur par défaut
console.log(creerProfil("Dave", undefined, "Marseille")); // { nom: "Dave", age: 18, ville: "Marseille" }
// Note : null ne déclenche PAS la valeur par défaut
console.log(creerProfil("Eve", null, "Nice")); // { nom: "Eve", age: null, ville: "Nice" }

// La valeur par défaut peut être une expression ou appeler une autre fonction
function genererID() {
  return Math.random().toString(36).slice(2, 9);
}

function creerItem(nom, id = genererID()) {
  return { id, nom };
}

console.log(creerItem("Pomme")); // { id: "a3f2g1k", nom: "Pomme" }
console.log(creerItem("Banane")); // { id: "x9m4n2p", nom: "Banane" } — ID différent !
```

### Rest parameters (...)

```javascript
// Capture les arguments restants dans un tableau
function somme(...nombres) {
  return nombres.reduce((total, n) => total + n, 0);
}

console.log(somme(1, 2, 3));          // 6
console.log(somme(1, 2, 3, 4, 5));    // 15
console.log(somme());                  // 0

// Le paramètre rest doit être le dernier
function logAvecPrefixe(prefixe, ...messages) {
  messages.forEach(msg => console.log(`[${prefixe}] ${msg}`));
}

logAvecPrefixe("INFO", "Démarrage", "Connexion réussie", "Prêt");
// [INFO] Démarrage
// [INFO] Connexion réussie
// [INFO] Prêt
```

### L'objet `arguments` (ancienne façon)

```javascript
// Disponible dans les function classiques (pas les arrow functions)
function ancienneSomme() {
  let total = 0;
  for (let i = 0; i < arguments.length; i++) {
    total += arguments[i];
  }
  return total;
}
// À éviter : préférer les rest parameters qui sont plus explicites

// Dans une arrow function, arguments n'existe pas
const testArrow = () => {
  // console.log(arguments); // ReferenceError dans les arrow functions
};
```

---

## 3. Fonctions de première classe

```javascript
// 1. Stocker une fonction dans une variable (déjà vu)
const maFonction = () => "je suis une valeur";

// 2. Stocker des fonctions dans un tableau
const operations = [
  (a, b) => a + b,
  (a, b) => a - b,
  (a, b) => a * b,
  (a, b) => a / b,
];

console.log(operations[0](10, 5)); // 15
console.log(operations[2](10, 5)); // 50

// 3. Passer une fonction en argument (callback)
function appliquerOperation(a, b, operation) {
  const resultat = operation(a, b);
  console.log(`Résultat : ${resultat}`);
  return resultat;
}

appliquerOperation(10, 5, (a, b) => a + b);   // Résultat : 15
appliquerOperation(10, 5, (a, b) => a * b);   // Résultat : 50
appliquerOperation(10, 5, Math.max);           // Résultat : 10

// 4. Retourner une fonction depuis une autre fonction (Higher-Order Function)
function multiplierPar(facteur) {
  // Retourne une nouvelle fonction
  return (nombre) => nombre * facteur;
}

const doubler = multiplierPar(2);
const tripler = multiplierPar(3);
const decupler = multiplierPar(10);

console.log(doubler(5));   // 10
console.log(tripler(5));   // 15
console.log(decupler(5));  // 50

// 5. Stocker des fonctions dans un objet
const calculatrice = {
  addition: (a, b) => a + b,
  soustraction: (a, b) => a - b,
  multiplication: (a, b) => a * b,
  division: (a, b) => b !== 0 ? a / b : "Erreur: division par zéro",
};

console.log(calculatrice.addition(10, 3));     // 13
console.log(calculatrice.division(10, 0));     // "Erreur: division par zéro"
```

---

## 4. Closures (Fermetures)

Une closure est la combinaison d'une fonction et de son environnement lexical (les variables du scope dans lequel elle a été créée). La fonction "ferme" autour des variables de son scope parent, même après que ce scope parent ait terminé son exécution.

```javascript
// Exemple fondamental
function creerCompteur() {
  let count = 0; // Variable dans le scope de creerCompteur

  return function() { // Cette fonction "ferme" autour de count
    count++;
    console.log(`Compteur: ${count}`);
    return count;
  };
}

const compteur1 = creerCompteur();
const compteur2 = creerCompteur(); // Instance indépendante

compteur1(); // Compteur: 1
compteur1(); // Compteur: 2
compteur1(); // Compteur: 3
compteur2(); // Compteur: 1 — indépendant de compteur1 !
compteur1(); // Compteur: 4
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — créer compteur1 et compteur2, les appeler plusieurs fois, montrer que les deux compteurs sont indépendants
> **Expliquer :** Chaque appel à `creerCompteur()` crée un nouveau scope avec sa propre variable `count`. La fonction retournée "capture" ce scope. C'est le mécanisme qui permet d'encapsuler des données en JavaScript.

---

```javascript
// Closure pour créer des fonctions configurables
function creerValidateur(min, max) {
  return (valeur) => {
    if (valeur < min) return `Trop petit (min: ${min})`;
    if (valeur > max) return `Trop grand (max: ${max})`;
    return `Valeur ${valeur} valide`;
  };
}

const validerAge = creerValidateur(0, 150);
const validerNote = creerValidateur(0, 20);
const validerPort = creerValidateur(1, 65535);

console.log(validerAge(25));     // "Valeur 25 valide"
console.log(validerAge(-5));     // "Trop petit (min: 0)"
console.log(validerNote(25));    // "Trop grand (max: 20)"
console.log(validerPort(8080));  // "Valeur 8080 valide"

// Pattern "module" grâce aux closures — encapsulation
function creerBanqueCompte(soldeInitial) {
  let solde = soldeInitial; // Privé — inaccessible de l'extérieur
  const historique = [];

  return {
    deposer(montant) {
      if (montant <= 0) throw new Error("Montant invalide");
      solde += montant;
      historique.push({ type: "dépôt", montant, solde });
      console.log(`Dépôt de ${montant}€. Nouveau solde: ${solde}€`);
    },
    retirer(montant) {
      if (montant > solde) throw new Error("Solde insuffisant");
      solde -= montant;
      historique.push({ type: "retrait", montant, solde });
      console.log(`Retrait de ${montant}€. Nouveau solde: ${solde}€`);
    },
    consulterSolde() {
      return solde;
    },
    consulterHistorique() {
      return [...historique]; // Copie pour protéger le tableau original
    },
  };
}

const monCompte = creerBanqueCompte(1000);
monCompte.deposer(500);    // Dépôt de 500€. Nouveau solde: 1500€
monCompte.retirer(200);    // Retrait de 200€. Nouveau solde: 1300€
console.log(monCompte.consulterSolde()); // 1300
// console.log(monCompte.solde); // undefined — 'solde' n'est pas accessible directement
```

### Le piège classique des closures dans les boucles

```javascript
// Piège avec var (comportement contre-intuitif)
for (var i = 0; i < 3; i++) {
  setTimeout(function() {
    console.log(i); // 3, 3, 3 — pas 0, 1, 2 !
  }, 100);
}
// Explication : var est function-scoped, donc une seule variable 'i'
// Quand les setTimeout s'exécutent, la boucle est terminée et i vaut 3

// Solution 1 : utiliser let (block-scoped — crée une variable par itération)
for (let j = 0; j < 3; j++) {
  setTimeout(() => {
    console.log(j); // 0, 1, 2 — correct !
  }, 100);
}

// Solution 2 : IIFE (ancienne façon)
for (var k = 0; k < 3; k++) {
  ((valeur) => {
    setTimeout(() => {
      console.log(valeur); // 0, 1, 2
    }, 100);
  })(k);
}
```

---

## 5. IIFE — Immediately Invoked Function Expression

Une IIFE est une fonction qui est déclarée et immédiatement exécutée. Elle crée un scope isolé.

```javascript
// Syntaxe classique
(function() {
  const x = 10; // x est isolé dans ce scope
  console.log("IIFE exécutée !");
  console.log(x);
})();
// console.log(x); // ReferenceError : x n'est pas défini

// Avec paramètre
(function(message) {
  console.log(message);
})("Bonjour depuis l'IIFE !");

// Version arrow function
(() => {
  console.log("IIFE en arrow function");
})();

// IIFE qui retourne une valeur
const resultat = (() => {
  const a = 5;
  const b = 10;
  return a + b;
})();
console.log(resultat); // 15

// Usage réel : initialisation d'application sans polluer le scope global
const app = (() => {
  // Variables privées
  const config = {
    version: "1.0.0",
    debug: false,
  };

  function initialiser() {
    console.log(`App v${config.version} démarrée`);
  }

  function getVersion() {
    return config.version;
  }

  // Interface publique
  return {
    initialiser,
    getVersion,
  };
})();

app.initialiser();          // "App v1.0.0 démarrée"
console.log(app.getVersion()); // "1.0.0"
// app.config — undefined (privé)
```

---

## 6. Récursivité

```javascript
// Fonction qui s'appelle elle-même
function factorielle(n) {
  if (n <= 1) return 1; // Cas de base (condition d'arrêt)
  return n * factorielle(n - 1); // Appel récursif
}

console.log(factorielle(5)); // 120 (5 * 4 * 3 * 2 * 1)
console.log(factorielle(0)); // 1

// Suite de Fibonacci
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// ATTENTION : cette implémentation est très lente pour les grands n
// fibonacci(50) peut prendre plusieurs secondes !

// Version optimisée avec mémoïsation
function fibonacciMemo(n, memo = {}) {
  if (n in memo) return memo[n];
  if (n <= 1) return n;
  memo[n] = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
  return memo[n];
}

console.log(fibonacciMemo(50)); // 12586269025 — instantané

// Traverser une structure arborescente (usage réel de la récursivité)
function calculerTaille(noeud) {
  if (!noeud.enfants || noeud.enfants.length === 0) {
    return 1; // Feuille
  }
  return 1 + noeud.enfants.reduce((sum, enfant) => sum + calculerTaille(enfant), 0);
}

const arbre = {
  nom: "racine",
  enfants: [
    { nom: "A", enfants: [{ nom: "A1", enfants: [] }, { nom: "A2", enfants: [] }] },
    { nom: "B", enfants: [{ nom: "B1", enfants: [] }] },
    { nom: "C", enfants: [] },
  ],
};

console.log(calculerTaille(arbre)); // 7
```

---

## 7. Fonctions pures vs impures

Un concept fondamental de la programmation fonctionnelle :

```javascript
// Fonction PURE : même entrée → toujours même sortie, pas d'effets de bord
function additionnerPure(a, b) {
  return a + b; // Aucun effet externe, résultat prévisible
}

// Fonction IMPURE : résultat dépend d'un état externe ou crée des effets de bord
let compteur = 0;
function incrementerImpure() {
  compteur++; // Modifie une variable externe
  return compteur;
}

// Autre exemple de fonction impure
function sauvegarderUtilisateur(user) {
  // Appel API, lecture/écriture fichier, modification du DOM — effets de bord
  console.log("Sauvegarde...");
  localStorage.setItem("user", JSON.stringify(user));
}

// Pourquoi les fonctions pures sont-elles préférables ?
// 1. Testables facilement (pas de setup/teardown)
// 2. Prévisibles
// 3. Mémoïsables
// 4. Parallélisables

// Exemple : transformer des données de façon pure
const utilisateurs = [
  { nom: "Alice", age: 30, actif: true },
  { nom: "Bob", age: 25, actif: false },
  { nom: "Carol", age: 35, actif: true },
];

// Pure — crée un nouveau tableau sans modifier l'original
const utilisateursActifs = utilisateurs
  .filter(u => u.actif)
  .map(u => ({ ...u, affichage: `${u.nom} (${u.age} ans)` }));

console.log(utilisateursActifs);
// [ { nom: "Alice", age: 30, actif: true, affichage: "Alice (30 ans)" },
//   { nom: "Carol", age: 35, actif: true, affichage: "Carol (35 ans)" } ]

console.log(utilisateurs.length); // 3 — l'original n'a pas changé
```

---

## Récapitulatif

| Type | Hoisting | `this` | Usage recommandé |
|---|---|---|---|
| Function Declaration | Oui (complet) | Dynamique | Fonctions nommées et réutilisables |
| Function Expression | Non | Dynamique | Callbacks, fonctions conditionnelles |
| Arrow Function | Non | Lexical (hérité) | Callbacks, méthodes courtes, React |
| IIFE | — | Dynamique | Initialisation, scope isolé |
