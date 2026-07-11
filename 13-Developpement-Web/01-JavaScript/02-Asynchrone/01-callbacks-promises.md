# 01 — Callbacks et Promises

## Introduction

JavaScript est **mono-thread** : il ne peut exécuter qu'une seule opération à la fois. Mais une application web doit gérer des opérations longues (appels réseau, accès fichiers, timers) sans bloquer l'interface. C'est le problème que résout la programmation asynchrone.

Comprendre comment JavaScript gère l'asynchronicité est fondamental — c'est l'un des concepts les plus distinctifs du langage.

---

## 1. Le modèle d'exécution JavaScript

### La Call Stack, la Task Queue et l'Event Loop

```javascript
// SYNCHRONE — s'exécute immédiatement, dans l'ordre
console.log("1 - Début");
console.log("2 - Milieu");
console.log("3 - Fin");
// → 1, 2, 3

// ASYNCHRONE — le callback sera placé dans la Task Queue
console.log("1 - Avant setTimeout");

setTimeout(() => {
  console.log("3 - Dans le setTimeout (0ms)");
}, 0); // 0ms ne signifie PAS "immédiatement"

console.log("2 - Après setTimeout");
// → 1, 2, 3 (même avec 0ms !)
```

**Explication du modèle :**
1. Le code synchrone s'exécute entièrement (Call Stack)
2. Les callbacks asynchrones sont placés dans une queue
3. L'Event Loop vérifie si la Call Stack est vide, puis exécute les callbacks en attente

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir [https://latentflip.com/loupe/](https://latentflip.com/loupe/) — visualiseur de l'Event Loop — coller l'exemple setTimeout et montrer l'animation de la Call Stack, de la Callback Queue et de l'Event Loop
> **Expliquer :** Montrer en temps réel comment setTimeout(fn, 0) ne s'exécute PAS immédiatement mais attend que la call stack soit vide. C'est la clé pour comprendre tout le JS asynchrone.

---

## 2. Les Callbacks

Un callback est simplement une fonction passée en argument à une autre fonction, pour être appelée plus tard.

```javascript
// Callback synchrone (exemple simple)
function traiterTableau(tableau, callback) {
  const resultats = [];
  for (const element of tableau) {
    resultats.push(callback(element));
  }
  return resultats;
}

const nombres = [1, 2, 3, 4, 5];
const doubles = traiterTableau(nombres, n => n * 2);
console.log(doubles); // [2, 4, 6, 8, 10]

// Callback asynchrone — cas typique
function chargerDonnees(url, callback) {
  // Simulation d'un appel réseau
  setTimeout(() => {
    // Convention Node.js : (erreur, résultat)
    if (url.includes("error")) {
      callback(new Error("Ressource non trouvée"), null);
    } else {
      callback(null, { id: 1, data: "Données chargées depuis " + url });
    }
  }, 1000);
}

console.log("Début du chargement...");

chargerDonnees("/api/utilisateurs", (erreur, donnees) => {
  if (erreur) {
    console.error("Erreur:", erreur.message);
    return;
  }
  console.log("Données reçues:", donnees);
});

console.log("Code après chargerDonnees — s'exécute AVANT la réponse");
// Ordre d'affichage :
// 1. "Début du chargement..."
// 2. "Code après chargerDonnees..."
// 3. (après 1 seconde) "Données reçues: ..."
```

### Le Callback Hell — le problème

```javascript
// Quand on enchaîne des opérations asynchrones avec des callbacks...
// c'est le "Pyramid of Doom" ou "Callback Hell"

chargerDonnees("/api/utilisateurs", (err1, utilisateurs) => {
  if (err1) return console.error(err1);

  chargerDonnees(`/api/commandes/${utilisateurs[0].id}`, (err2, commandes) => {
    if (err2) return console.error(err2);

    chargerDonnees(`/api/details/${commandes[0].id}`, (err3, details) => {
      if (err3) return console.error(err3);

      chargerDonnees(`/api/produits/${details.produitId}`, (err4, produit) => {
        if (err4) return console.error(err4);

        // Enfin ! On peut utiliser les données
        console.log("Produit final:", produit);
        // ← On est maintenant 4 niveaux d'indentation plus loin
      });
    });
  });
});

// Problèmes :
// 1. Code difficile à lire (imbrication profonde)
// 2. Gestion d'erreurs répétitive et fastidieuse
// 3. Difficile à maintenir et refactoriser
// 4. Impossible de gérer les opérations en parallèle facilement
```

---

## 3. Les Promises — La solution

Une Promise est un objet représentant la **valeur éventuelle** (ou l'échec) d'une opération asynchrone. Elle a trois états :
- **pending** : en cours d'exécution
- **fulfilled** : résolue avec succès
- **rejected** : échouée avec une erreur

```javascript
// Créer une Promise
const maPromesse = new Promise((resolve, reject) => {
  // Cette fonction s'exécute immédiatement (synchrone)
  const succes = true;

  setTimeout(() => {
    if (succes) {
      resolve("Opération réussie !"); // Passe en état 'fulfilled'
    } else {
      reject(new Error("Quelque chose a mal tourné")); // Passe en état 'rejected'
    }
  }, 1000);
});

// État initial
console.log(maPromesse); // Promise { <pending> }

// Consommer la Promise
maPromesse
  .then(valeur => {
    console.log("Succès:", valeur); // "Succès: Opération réussie !"
    return valeur.toUpperCase(); // Le .then() retourne une nouvelle Promise
  })
  .then(valeurTransformee => {
    console.log("Transformée:", valeurTransformee); // "Transformée: OPÉRATION RÉUSSIE !"
  })
  .catch(erreur => {
    console.error("Erreur:", erreur.message);
  })
  .finally(() => {
    console.log("Toujours exécuté (succès ou échec)");
  });
```

### Réécrire les callbacks en Promises

```javascript
// Version callback (avant)
function chargerDonneesCallback(url, callback) {
  setTimeout(() => {
    if (url.includes("error")) {
      callback(new Error("Erreur réseau"), null);
    } else {
      callback(null, { url, data: "réponse" });
    }
  }, 500);
}

// Version Promise (après)
function chargerDonnees(url) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (url.includes("error")) {
        reject(new Error(`Erreur: ${url} non trouvé`));
      } else {
        resolve({ url, data: "réponse", timestamp: Date.now() });
      }
    }, 500);
  });
}

// Utilisation — beaucoup plus lisible !
chargerDonnees("/api/utilisateurs")
  .then(donnees => {
    console.log("Données:", donnees);
    return chargerDonnees(`/api/commandes/${donnees.url}`);
  })
  .then(commandes => {
    console.log("Commandes:", commandes);
    return chargerDonnees(`/api/details/${commandes.url}`);
  })
  .then(details => {
    console.log("Détails:", details);
  })
  .catch(erreur => {
    // UNE seule gestion d'erreur pour toute la chaîne !
    console.error("Erreur dans la chaîne:", erreur.message);
  });
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans la console DevTools, créer une Promise et l'afficher avant qu'elle soit résolue (montrer l'état `<pending>`), puis après (montrer `fulfilled`)
> **Expliquer :** Une Promise est un objet concret en mémoire. On peut l'inspecter, la stocker, la passer en argument. Contrairement aux callbacks, on peut "attacher" des handlers `.then()` à n'importe quel moment, même après la résolution.

---

## 4. Chaînage de Promises

La clé du chaînage est que chaque `.then()` **retourne une nouvelle Promise**.

```javascript
// Règles du chaînage :
// 1. Si le callback retourne une valeur → la Promise suivante est résolue avec cette valeur
// 2. Si le callback retourne une Promise → la Promise suivante attend sa résolution
// 3. Si le callback lance une exception → la Promise suivante est rejetée

function etape(n, delai = 100) {
  return new Promise(resolve => {
    setTimeout(() => resolve(n), delai);
  });
}

// Chaînage séquentiel
etape(1)
  .then(v => {
    console.log(`Étape 1: ${v}`);
    return etape(v + 1); // Retourne une Promise — attend sa résolution
  })
  .then(v => {
    console.log(`Étape 2: ${v}`);
    return v * 10; // Retourne une valeur simple
  })
  .then(v => {
    console.log(`Étape 3: ${v}`);
    if (v > 50) throw new Error("Valeur trop grande !");
    return v;
  })
  .then(v => console.log(`Final: ${v}`))
  .catch(err => console.error(`Erreur: ${err.message}`));

// Exemple concret : pipeline de traitement de données
function validerEmail(email) {
  return new Promise((resolve, reject) => {
    if (!email.includes("@")) reject(new Error("Email invalide"));
    else resolve(email.toLowerCase().trim());
  });
}

function verifierDisponibilite(email) {
  return new Promise((resolve, reject) => {
    // Simulation d'une vérification en base de données
    const emailsExistants = ["admin@example.com", "test@example.com"];
    setTimeout(() => {
      if (emailsExistants.includes(email)) {
        reject(new Error("Email déjà utilisé"));
      } else {
        resolve({ email, disponible: true });
      }
    }, 300);
  });
}

function creerCompte(emailInfo) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        id: Math.random().toString(36).slice(2, 9),
        email: emailInfo.email,
        createdAt: new Date().toISOString(),
      });
    }, 200);
  });
}

// Pipeline d'inscription
function inscrireUtilisateur(email) {
  return validerEmail(email)
    .then(emailValide => verifierDisponibilite(emailValide))
    .then(info => creerCompte(info))
    .then(compte => {
      console.log("Compte créé:", compte);
      return compte;
    })
    .catch(erreur => {
      console.error("Échec inscription:", erreur.message);
      throw erreur; // Re-propager pour que l'appelant puisse aussi gérer
    });
}

inscrireUtilisateur("alice@newdomain.com");
inscrireUtilisateur("admin@example.com"); // → "Échec inscription: Email déjà utilisé"
inscrireUtilisateur("pas-un-email");       // → "Échec inscription: Email invalide"
```

---

## 5. Promise.all() — Exécution parallèle

```javascript
function delai(ms, valeur) {
  return new Promise(resolve => setTimeout(() => resolve(valeur), ms));
}

// SÉQUENTIEL — lent : 300ms + 200ms + 400ms = 900ms total
async function chargerSequentiel() {
  const debut = Date.now();
  const a = await delai(300, "Utilisateur");
  const b = await delai(200, "Commandes");
  const c = await delai(400, "Produits");
  console.log(`Séquentiel: ${Date.now() - debut}ms`, [a, b, c]);
}

// PARALLÈLE — rapide : max(300, 200, 400) = 400ms total
async function chargerParallele() {
  const debut = Date.now();
  const [a, b, c] = await Promise.all([
    delai(300, "Utilisateur"),
    delai(200, "Commandes"),
    delai(400, "Produits"),
  ]);
  console.log(`Parallèle: ${Date.now() - debut}ms`, [a, b, c]);
}

// Promise.all : si UNE promesse échoue → toutes échouent
const promessesAvecEchec = [
  delai(100, "OK 1"),
  Promise.reject(new Error("Promesse 2 échoue")),
  delai(300, "OK 3"),
];

Promise.all(promessesAvecEchec)
  .then(resultats => console.log(resultats))
  .catch(err => console.error("Promise.all échoue:", err.message));
// → Promise.all échoue: Promesse 2 échoue

// Promise.allSettled — attend TOUTES les promesses, succès ou échec
Promise.allSettled(promessesAvecEchec)
  .then(resultats => {
    resultats.forEach((r, i) => {
      if (r.status === "fulfilled") {
        console.log(`Promesse ${i + 1}: ✓ ${r.value}`);
      } else {
        console.log(`Promesse ${i + 1}: ✗ ${r.reason.message}`);
      }
    });
  });
// Promesse 1: ✓ OK 1
// Promesse 2: ✗ Promesse 2 échoue
// Promesse 3: ✓ OK 3
```

### Promise.race() et Promise.any()

```javascript
// Promise.race — la première qui se résout OU qui échoue "gagne"
const course = Promise.race([
  delai(500, "lente"),
  delai(100, "rapide"),
  delai(300, "moyenne"),
]);
course.then(v => console.log("Winner:", v)); // "Winner: rapide"

// Timeout pattern avec Promise.race
function avecTimeout(promesse, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout après ${ms}ms`)), ms)
  );
  return Promise.race([promesse, timeout]);
}

avecTimeout(delai(2000, "réponse serveur"), 1000)
  .then(v => console.log("Réponse:", v))
  .catch(err => console.error(err.message)); // "Timeout après 1000ms"

// Promise.any — la première qui RÉUSSIT (ignore les échecs)
const tentatives = Promise.any([
  Promise.reject(new Error("Serveur 1 down")),
  delai(200, "Serveur 2 OK"),
  delai(100, "Serveur 3 OK"), // Celui-ci est plus rapide
]);
tentatives
  .then(v => console.log("Premier succès:", v)) // "Premier succès: Serveur 3 OK"
  .catch(() => console.log("Tous les serveurs ont échoué"));
```

---

## 6. Création de Promises utilitaires

```javascript
// Promisifier une fonction callback (Node.js style)
function promisifier(fn) {
  return (...args) => new Promise((resolve, reject) => {
    fn(...args, (erreur, resultat) => {
      if (erreur) reject(erreur);
      else resolve(resultat);
    });
  });
}

// Note : Node.js fournit util.promisify() pour cela

// Promises déjà résolues/rejetées — utile pour les tests et les valeurs par défaut
const deja_resolue = Promise.resolve("valeur immédiate");
const deja_rejetee = Promise.reject(new Error("erreur immédiate"));

deja_resolue.then(v => console.log(v)); // "valeur immédiate"
deja_rejetee.catch(e => console.log(e.message)); // "erreur immédiate"

// Délai simple (utility)
const attendre = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function exempleAttente() {
  console.log("Départ");
  await attendre(1000);
  console.log("Après 1 seconde");
  await attendre(500);
  console.log("Après 0.5 seconde de plus");
}

// Retry pattern
function avecRetry(fn, maxTentatives = 3, delaiMs = 1000) {
  return new Promise(async (resolve, reject) => {
    for (let tentative = 1; tentative <= maxTentatives; tentative++) {
      try {
        const resultat = await fn();
        resolve(resultat);
        return;
      } catch (erreur) {
        console.log(`Tentative ${tentative}/${maxTentatives} échouée: ${erreur.message}`);
        if (tentative === maxTentatives) {
          reject(new Error(`Échec après ${maxTentatives} tentatives: ${erreur.message}`));
        } else {
          await attendre(delaiMs * tentative); // Délai exponentiel
        }
      }
    }
  });
}

let appels = 0;
function apiInstable() {
  return new Promise((resolve, reject) => {
    appels++;
    setTimeout(() => {
      if (appels < 3) reject(new Error("Serveur indisponible"));
      else resolve("Succès à la tentative " + appels);
    }, 100);
  });
}

avecRetry(apiInstable, 3, 100)
  .then(v => console.log(v))   // "Succès à la tentative 3"
  .catch(e => console.error(e.message));
```

---

## Récapitulatif

| Méthode | Comportement |
|---|---|
| `Promise.resolve(v)` | Promise déjà résolue avec la valeur `v` |
| `Promise.reject(e)` | Promise déjà rejetée avec l'erreur `e` |
| `Promise.all([...])` | Attend toutes, échoue si une échoue |
| `Promise.allSettled([...])` | Attend toutes, retourne les statuts |
| `Promise.race([...])` | Première résolue OU rejetée |
| `Promise.any([...])` | Première résolue (ignore les rejets) |

**Règle d'or :** Toujours attacher un `.catch()` à vos chaînes de Promises pour éviter les *unhandled rejection* silencieux.
