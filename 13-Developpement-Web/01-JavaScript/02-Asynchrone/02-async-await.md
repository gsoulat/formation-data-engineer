# 02 — async/await : Syntaxe Moderne de l'Asynchrone

## Introduction

`async/await` (ES2017) est une syntaxe qui permet d'écrire du code asynchrone comme s'il était synchrone. Il ne remplace pas les Promises — il en est une surcouche syntaxique qui les rend beaucoup plus lisibles.

**Règle fondamentale :** `async/await` ne peut exister sans Promises. Comprendre les Promises est donc un prérequis indispensable.

---

## 1. Les mots-clés `async` et `await`

### `async` — Transformer une fonction en fonction asynchrone

```javascript
// Une fonction async retourne TOUJOURS une Promise,
// même si elle retourne une valeur simple

async function saluer() {
  return "Bonjour !"; // Devient automatiquement Promise.resolve("Bonjour !")
}

const resultat = saluer();
console.log(resultat);         // Promise { 'Bonjour !' }
resultat.then(v => console.log(v)); // "Bonjour !"

// Équivalent exact (sans async/await)
function saluerPromesse() {
  return Promise.resolve("Bonjour !");
}

// async fonctionne sur toutes les formes de fonctions
const fetchData = async (url) => { /* ... */ };
const obj = {
  async charger() { /* ... */ }
};
class Service {
  async getData() { /* ... */ }
}
```

### `await` — Attendre la résolution d'une Promise

```javascript
// await ne peut être utilisé QU'À L'INTÉRIEUR d'une fonction async
// (sauf au niveau module — top-level await)

function delai(ms, valeur) {
  return new Promise(resolve => setTimeout(() => resolve(valeur), ms));
}

async function exemple() {
  console.log("1 - Début");

  const valeur = await delai(1000, "Résultat après 1 seconde");
  // Le code "pause" ici jusqu'à la résolution de la Promise
  // MAIS le thread principal n'est PAS bloqué !

  console.log("2 - Reçu:", valeur);
  console.log("3 - Fin");
}

exemple();
console.log("Ce code s'exécute PENDANT que exemple() attend");

// Ordre d'affichage :
// "Ce code s'exécute PENDANT que exemple() attend"
// "1 - Début"
// (1 seconde plus tard)
// "2 - Reçu: Résultat après 1 seconde"
// "3 - Fin"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — exécuter le code ci-dessus et montrer l'ordre d'affichage, notamment que "Ce code s'exécute PENDANT..." apparaît après "1 - Début" mais AVANT "2 - Reçu"
> **Expliquer :** await ne bloque pas le thread. Il suspend l'exécution de la fonction async et rend le contrôle à l'appelant. Le thread peut continuer à exécuter d'autres choses pendant l'attente.

---

## 2. Gestion des erreurs avec try/catch

```javascript
// Avec les Promises
function charger(url) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (url.includes("erreur")) {
        reject(new Error(`404: ${url} non trouvé`));
      } else {
        resolve({ url, data: "données" });
      }
    }, 200);
  });
}

// Version Promise — gestion d'erreur avec .catch()
charger("/api/users")
  .then(data => console.log(data))
  .catch(err => console.error(err.message));

// Version async/await — gestion d'erreur avec try/catch
async function chargerAvecGestion() {
  try {
    const data = await charger("/api/users");
    console.log("Succès:", data);

    const data2 = await charger("/api/erreur"); // Va échouer
    console.log("Jamais atteint");
  } catch (erreur) {
    console.error("Erreur capturée:", erreur.message);
    // "Erreur capturée: 404: /api/erreur non trouvé"
  } finally {
    console.log("Toujours exécuté (comme Promise.finally)");
  }
}

chargerAvecGestion();
```

### Gestion fine des erreurs

```javascript
// Distinguer différents types d'erreurs
class ErreurReseau extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = "ErreurReseau";
    this.statusCode = statusCode;
  }
}

class ErreurValidation extends Error {
  constructor(message, champs) {
    super(message);
    this.name = "ErreurValidation";
    this.champs = champs;
  }
}

async function creerUtilisateur(donnees) {
  // Validation
  if (!donnees.email) {
    throw new ErreurValidation("Données invalides", ["email"]);
  }

  // Appel API simulé
  if (donnees.email === "banned@example.com") {
    throw new ErreurReseau("Utilisateur banni", 403);
  }

  return { id: 1, ...donnees, createdAt: new Date() };
}

async function gererCreation(donnees) {
  try {
    const utilisateur = await creerUtilisateur(donnees);
    console.log("Créé:", utilisateur);
  } catch (erreur) {
    if (erreur instanceof ErreurValidation) {
      console.error(`Validation: ${erreur.message}. Champs: ${erreur.champs.join(", ")}`);
    } else if (erreur instanceof ErreurReseau) {
      console.error(`Réseau [${erreur.statusCode}]: ${erreur.message}`);
    } else {
      console.error("Erreur inattendue:", erreur);
      throw erreur; // Re-propager les erreurs inattendues
    }
  }
}

gererCreation({ nom: "Alice" });             // Validation: Données invalides. Champs: email
gererCreation({ email: "banned@example.com" }); // Réseau [403]: Utilisateur banni
gererCreation({ email: "alice@example.com", nom: "Alice" }); // Créé: {...}
```

### Pattern "safe await" — éviter les try/catch répétitifs

```javascript
// Utilitaire pour éviter les try/catch partout
async function safeAwait(promise) {
  try {
    const data = await promise;
    return [null, data];
  } catch (erreur) {
    return [erreur, null];
  }
}

// Utilisation
async function traitement() {
  const [err1, utilisateur] = await safeAwait(charger("/api/user/1"));
  if (err1) return console.error("Impossible de charger l'utilisateur:", err1.message);

  const [err2, commandes] = await safeAwait(charger(`/api/commandes/${utilisateur.url}`));
  if (err2) return console.error("Impossible de charger les commandes:", err2.message);

  console.log("Utilisateur:", utilisateur);
  console.log("Commandes:", commandes);
}
```

---

## 3. Séquentiel vs Parallèle

C'est l'une des erreurs les plus courantes avec async/await : utiliser await en série quand les opérations pourraient être parallèles.

```javascript
function simulerAPI(nom, ms) {
  return new Promise(resolve =>
    setTimeout(() => resolve(`${nom} (${ms}ms)`), ms)
  );
}

// ❌ SÉQUENTIEL — LENT : 300 + 200 + 400 = 900ms
async function chargerSequentiel() {
  const debut = Date.now();

  const utilisateur = await simulerAPI("utilisateur", 300);
  const commandes = await simulerAPI("commandes", 200);
  const produits = await simulerAPI("produits", 400);

  console.log(`Séquentiel: ${Date.now() - debut}ms`); // ~900ms
  console.log(utilisateur, commandes, produits);
}

// ✅ PARALLÈLE — RAPIDE : max(300, 200, 400) = 400ms
async function chargerParallele() {
  const debut = Date.now();

  const [utilisateur, commandes, produits] = await Promise.all([
    simulerAPI("utilisateur", 300),
    simulerAPI("commandes", 200),
    simulerAPI("produits", 400),
  ]);

  console.log(`Parallèle: ${Date.now() - debut}ms`); // ~400ms
  console.log(utilisateur, commandes, produits);
}

chargerSequentiel();
chargerParallele();
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de DevTools — ouvrir un site avec plusieurs requêtes et montrer la timeline, puis montrer la différence entre des requêtes séquentielles (en cascade) et parallèles (toutes partent en même temps)
> **Expliquer :** En production, la différence peut être dramatique. Si on charge 5 ressources de 200ms chacune, séquentiel = 1 seconde, parallèle = 200ms. Toujours penser à Promise.all() quand les opérations sont indépendantes.

---

```javascript
// Cas intermédiaire : certaines opérations dépendent d'autres
async function chargerDonneesDependantes() {
  // Étape 1 : obtenir l'utilisateur (nécessaire pour la suite)
  const utilisateur = await simulerAPI("utilisateur", 300);

  // Étapes 2a et 2b : ne dépendent QUE de l'utilisateur, pas l'une de l'autre
  const [commandes, preferences] = await Promise.all([
    simulerAPI(`commandes de ${utilisateur}`, 200),
    simulerAPI(`preferences de ${utilisateur}`, 150),
  ]);

  // Étape 3 : dépend des commandes
  const details = await simulerAPI(`details de ${commandes}`, 100);

  return { utilisateur, commandes, preferences, details };
}
// Durée totale : 300 + max(200, 150) + 100 = 600ms (vs 750ms en séquentiel pur)
```

### Boucles asynchrones

```javascript
const ids = [1, 2, 3, 4, 5];

// ❌ forEach NE FONCTIONNE PAS avec async/await
// forEach n'attend pas les callbacks async !
async function incorrectAvecForEach() {
  console.log("Début forEach");
  ids.forEach(async (id) => {
    const data = await simulerAPI(`item-${id}`, 100);
    console.log(data); // S'exécute de façon désordonnée
  });
  console.log("Fin forEach — mais les await ne sont pas terminés !");
}

// ✅ for...of avec await — séquentiel
async function sequentielAvecFor() {
  console.log("Début séquentiel");
  for (const id of ids) {
    const data = await simulerAPI(`item-${id}`, 100);
    console.log(data); // Dans l'ordre, l'un après l'autre
  }
  console.log("Fin séquentiel — ~500ms total");
}

// ✅ Promise.all avec map — parallèle
async function parallelAvecMap() {
  console.log("Début parallèle");
  const resultats = await Promise.all(
    ids.map(id => simulerAPI(`item-${id}`, 100))
  );
  console.log(resultats); // Tous les résultats en même temps, ~100ms
  console.log("Fin parallèle");
}

// ✅ Parallèle avec limite de concurrence
async function paralleleLimite(ids, limite = 2) {
  const resultats = [];

  for (let i = 0; i < ids.length; i += limite) {
    const lot = ids.slice(i, i + limite);
    const lotResultats = await Promise.all(
      lot.map(id => simulerAPI(`item-${id}`, 100))
    );
    resultats.push(...lotResultats);
    console.log(`Lot ${Math.floor(i / limite) + 1} terminé`);
  }

  return resultats;
}

paralleleLimite([1, 2, 3, 4, 5], 2);
// Lot 1 terminé (ids 1, 2)
// Lot 2 terminé (ids 3, 4)
// Lot 3 terminé (id 5)
```

---

## 4. Top-level await (ES2022)

Dans les modules ES6, on peut utiliser `await` directement au niveau du module, sans envelopper dans une fonction async.

```javascript
// fichier: config.js (module ES6)
// Top-level await — ne fonctionne que dans les modules (type="module" ou .mjs)

const config = await fetch("/api/config").then(r => r.json());
export const API_URL = config.apiUrl;
export const VERSION = config.version;

// D'autres modules qui importent config.js attendent automatiquement
// que ces awaits se résolvent avant d'utiliser les exports
```

---

## 5. Patterns avancés

### Async Generator — traiter des données en streaming

```javascript
// Un générateur async peut yield des valeurs asynchrones
async function* paginerAPI(baseUrl, taillePage = 10) {
  let page = 1;
  let continuer = true;

  while (continuer) {
    // Simule une API paginée
    const donnees = await new Promise(resolve =>
      setTimeout(() => resolve({
        items: Array.from({ length: taillePage }, (_, i) => ({
          id: (page - 1) * taillePage + i + 1,
          nom: `Item ${(page - 1) * taillePage + i + 1}`
        })),
        hasMore: page < 3,
      }), 200)
    );

    yield donnees.items;

    if (!donnees.hasMore) continuer = false;
    page++;
  }
}

async function traiterToutesLesDonnees() {
  for await (const page of paginerAPI("/api/items")) {
    console.log(`Page reçue: ${page.length} items, premier ID: ${page[0].id}`);
    // Traiter la page...
  }
  console.log("Toutes les pages traitées");
}

traiterToutesLesDonnees();
// Page reçue: 10 items, premier ID: 1
// Page reçue: 10 items, premier ID: 11
// Page reçue: 10 items, premier ID: 21
// Toutes les pages traitées
```

### Mémoïsation async

```javascript
function memoiserAsync(fn) {
  const cache = new Map();

  return async (...args) => {
    const cle = JSON.stringify(args);

    if (cache.has(cle)) {
      console.log(`Cache HIT pour: ${cle}`);
      return cache.get(cle);
    }

    console.log(`Cache MISS pour: ${cle}`);
    const resultat = await fn(...args);
    cache.set(cle, resultat);
    return resultat;
  };
}

const chargerUtilisateur = memoiserAsync(async (id) => {
  await new Promise(r => setTimeout(r, 300)); // Simule appel API
  return { id, nom: `Utilisateur ${id}`, email: `user${id}@example.com` };
});

async function test() {
  const u1 = await chargerUtilisateur(1); // Cache MISS (~300ms)
  const u2 = await chargerUtilisateur(1); // Cache HIT (instantané)
  const u3 = await chargerUtilisateur(2); // Cache MISS (~300ms)
  console.log(u1, u2, u3);
}

test();
```

### AbortController — annuler des opérations asynchrones

```javascript
// AbortController permet d'annuler des fetch() en cours
async function chargerAvecAnnulation(url, signal) {
  try {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (erreur) {
    if (erreur.name === "AbortError") {
      console.log("Requête annulée");
      return null;
    }
    throw erreur;
  }
}

// Utilisation
const controller = new AbortController();

// Lancer la requête
chargerAvecAnnulation("https://api.example.com/data", controller.signal)
  .then(data => console.log("Données:", data))
  .catch(err => console.error(err));

// Annuler après 2 secondes
setTimeout(() => controller.abort(), 2000);

// Pattern avec timeout automatique
function avecTimeout(promesse, ms) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ms);

  return promesse
    .finally(() => clearTimeout(timeout));
}
```

---

## 6. Erreurs courantes à éviter

```javascript
// ❌ Erreur 1 : oublier async sur la fonction
function mauvaise() {
  // await n'est pas valide ici — SyntaxError
  // const data = await fetch("/api");
}

// ❌ Erreur 2 : await dans un callback non-async
async function mauvaise2() {
  const ids = [1, 2, 3];
  ids.forEach(id => {
    // await ici ne fonctionne pas comme attendu
    // const data = await simulerAPI(id, 100);
  });
}

// ✅ Correct : utiliser for...of ou Promise.all
async function correcte() {
  const ids = [1, 2, 3];
  for (const id of ids) {
    const data = await simulerAPI(id, 100);
    console.log(data);
  }
}

// ❌ Erreur 3 : ne pas gérer les erreurs
async function sanGestion() {
  const data = await fetch("/api/peut-echouer"); // Unhandled rejection si ça échoue
  return data.json();
}

// ✅ Correct
async function avecGestion() {
  try {
    const response = await fetch("/api/peut-echouer");
    if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error("Erreur:", err.message);
    return null;
  }
}

// ❌ Erreur 4 : await inutile sur une valeur non-Promise
async function inutile() {
  const x = await 42; // Fonctionne mais inutile — await 42 = 42
  return x;
}

// ❌ Erreur 5 : ne pas paralléliser des opérations indépendantes
async function lente() {
  const a = await simulerAPI("a", 500);
  const b = await simulerAPI("b", 500); // Attend inutilement que a soit fini
  return [a, b]; // Durée: 1000ms
}

// ✅ Correct : 500ms au lieu de 1000ms
async function rapide() {
  const [a, b] = await Promise.all([
    simulerAPI("a", 500),
    simulerAPI("b", 500),
  ]);
  return [a, b]; // Durée: 500ms
}
```

---

## Récapitulatif

| Concept | Rappel |
|---|---|
| `async function` | Retourne toujours une Promise |
| `await expression` | Pause la fonction async, retourne la valeur résolue |
| `try/catch` avec await | Équivalent au `.catch()` des Promises |
| `finally` | S'exécute toujours, succès ou échec |
| `Promise.all` + `await` | Exécuter plusieurs opérations en parallèle |
| `for await...of` | Itérer sur un itérable asynchrone |
| `for...of` avec `await` | Boucle asynchrone séquentielle |

**Mnémotechnique :**
- `async` = "cette fonction travaille de façon asynchrone"
- `await` = "attends que cette Promise soit résolue avant de continuer"
- Sans `async`, pas d'`await`
- Sans Promises en dessous, pas d'`async/await` utile
