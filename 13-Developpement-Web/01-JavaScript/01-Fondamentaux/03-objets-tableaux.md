# 03 — Objets et Tableaux : Destructuring, Spread, map/filter/reduce

## Introduction

Les objets et les tableaux sont les structures de données fondamentales de JavaScript. Maîtriser les techniques modernes de manipulation (destructuring, spread/rest, méthodes fonctionnelles) est indispensable pour écrire du code lisible et maintenable — et particulièrement pour travailler avec React.

---

## 1. Objets — Object Literals

### Création et accès

```javascript
// Création d'un objet avec la syntaxe littérale
const produit = {
  id: 1,
  nom: "Ordinateur portable",
  prix: 999.99,
  disponible: true,
  categorie: {          // Objet imbriqué
    id: 5,
    libelle: "Informatique",
  },
  tags: ["tech", "portable", "pro"],
  // Méthode dans l'objet
  description() {
    return `${this.nom} - ${this.prix}€`;
  },
};

// Accès aux propriétés
console.log(produit.nom);              // "Ordinateur portable"
console.log(produit["prix"]);          // 999.99 — notation bracket (utile si la clé est dynamique)
console.log(produit.categorie.libelle); // "Informatique"
console.log(produit.tags[0]);          // "tech"
console.log(produit.description());    // "Ordinateur portable - 999.99€"

// Propriété inexistante → undefined (pas d'erreur)
console.log(produit.stock); // undefined

// Clé dynamique
const cle = "nom";
console.log(produit[cle]); // "Ordinateur portable"
```

### Manipulation des objets

```javascript
// Ajout / modification de propriétés
const voiture = { marque: "Renault", modele: "Clio" };
voiture.annee = 2022;           // Ajout
voiture.modele = "Megane";      // Modification
console.log(voiture); // { marque: "Renault", modele: "Megane", annee: 2022 }

// Suppression d'une propriété
delete voiture.annee;
console.log(voiture.annee); // undefined

// Vérifier l'existence d'une propriété
console.log("marque" in voiture);         // true
console.log("annee" in voiture);          // false
console.log(voiture.hasOwnProperty("marque")); // true

// Object.keys() — tableau des clés
const keys = Object.keys(voiture);
console.log(keys); // ["marque", "modele"]

// Object.values() — tableau des valeurs
const values = Object.values(voiture);
console.log(values); // ["Renault", "Megane"]

// Object.entries() — tableau de paires [clé, valeur]
const entries = Object.entries(voiture);
console.log(entries); // [["marque", "Renault"], ["modele", "Megane"]]

// Itérer sur les entrées
for (const [cle, valeur] of Object.entries(voiture)) {
  console.log(`${cle}: ${valeur}`);
}
```

### Raccourcis ES6 pour les objets

```javascript
const nom = "Alice";
const age = 30;
const ville = "Paris";

// Raccourci : si la clé = le nom de la variable
const ancien = { nom: nom, age: age, ville: ville }; // Verbeux
const moderne = { nom, age, ville }; // Raccourci ES6

console.log(moderne); // { nom: "Alice", age: 30, ville: "Paris" }

// Noms de propriétés calculés (computed property names)
const prefixe = "get";
const objet = {
  [`${prefixe}Nom`]() { return "Alice"; },
  [`${prefixe}Age`]() { return 30; },
};
console.log(objet.getNom()); // "Alice"
console.log(objet.getAge()); // 30

// Méthodes raccourcies
const calculatrice = {
  valeur: 0,
  ajouter(n) { this.valeur += n; return this; }, // Chaînage
  soustraire(n) { this.valeur -= n; return this; },
  resultat() { return this.valeur; },
};

console.log(calculatrice.ajouter(10).ajouter(5).soustraire(3).resultat()); // 12
```

---

## 2. Destructuring (Déstructuration)

### Déstructuration d'objets

```javascript
const utilisateur = {
  id: 42,
  prenom: "Marie",
  nom: "Dupont",
  age: 28,
  adresse: {
    rue: "12 rue de la Paix",
    ville: "Lyon",
    codePostal: "69001",
  },
};

// Déstructuration basique
const { prenom, age } = utilisateur;
console.log(prenom); // "Marie"
console.log(age);    // 28

// Renommer lors de la déstructuration
const { prenom: firstName, nom: lastName } = utilisateur;
console.log(firstName); // "Marie"
console.log(lastName);  // "Dupont"

// Valeur par défaut si la propriété n'existe pas
const { prenom: p, role = "utilisateur", score = 0 } = utilisateur;
console.log(role);  // "utilisateur" — propriété absente
console.log(score); // 0 — propriété absente

// Déstructuration imbriquée
const { adresse: { ville, codePostal } } = utilisateur;
console.log(ville);      // "Lyon"
console.log(codePostal); // "69001"

// Dans les paramètres de fonction
function afficherUtilisateur({ prenom, nom, age = "non renseigné" }) {
  console.log(`${prenom} ${nom}, ${age} ans`);
}
afficherUtilisateur(utilisateur); // "Marie Dupont, 28 ans"

// Reste des propriétés avec ...rest
const { id, ...sansId } = utilisateur;
console.log(id);      // 42
console.log(sansId);  // { prenom: "Marie", nom: "Dupont", age: 28, adresse: {...} }
```

### Déstructuration de tableaux

```javascript
const couleurs = ["rouge", "vert", "bleu", "jaune", "violet"];

// Déstructuration basique
const [premiere, deuxieme] = couleurs;
console.log(premiere); // "rouge"
console.log(deuxieme); // "vert"

// Ignorer des éléments avec des virgules
const [, , troisieme] = couleurs;
console.log(troisieme); // "bleu"

// Valeur par défaut
const [a, b, c, d, e, f = "blanc"] = couleurs;
console.log(f); // "blanc" — index 5 n'existe pas

// Reste des éléments
const [premier, ...autresCouleurs] = couleurs;
console.log(premier);         // "rouge"
console.log(autresCouleurs);  // ["vert", "bleu", "jaune", "violet"]

// Échanger deux variables (sans variable temporaire)
let x = 1;
let y = 2;
[x, y] = [y, x];
console.log(x, y); // 2, 1

// Déstructuration de tableau retourné par une fonction
function getCoordonnees() {
  return [48.8566, 2.3522];
}
const [latitude, longitude] = getCoordonnees();
console.log(`Paris: ${latitude}°N, ${longitude}°E`);
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans VS Code, montrer un exemple React où les props sont destructurées dans la signature de fonction `function Card({ titre, description, image })` — puis dans la console, déstructurer un objet en live
> **Expliquer :** La destructuration est omniprésente en React. Chaque composant fonctionnel reçoit ses props via destructuration. Maîtriser cette syntaxe est non-négociable pour travailler avec React.

---

## 3. Spread Operator et Rest Parameters

### Spread sur les objets

```javascript
const base = { a: 1, b: 2, c: 3 };

// Copier un objet (shallow copy)
const copie = { ...base };
copie.a = 99;
console.log(base.a);  // 1 — l'original n'est pas modifié
console.log(copie.a); // 99

// Attention : shallow copy seulement
const original = { x: 1, nested: { y: 2 } };
const shallowCopy = { ...original };
shallowCopy.nested.y = 99; // Modifie aussi original !
console.log(original.nested.y); // 99 — les objets imbriqués sont partagés

// Fusionner des objets
const defauts = { theme: "clair", langue: "fr", debug: false };
const preferences = { theme: "sombre", notifications: true };
const config = { ...defauts, ...preferences }; // Les propriétés de droite écrasent celles de gauche
console.log(config);
// { theme: "sombre", langue: "fr", debug: false, notifications: true }

// Cas d'usage : mise à jour partielle d'un objet (immutable update)
const utilisateur = { id: 1, nom: "Alice", age: 30, email: "alice@example.com" };
const utilisateurModifie = { ...utilisateur, age: 31, email: "alice.pro@example.com" };
console.log(utilisateur.age);         // 30 — original inchangé
console.log(utilisateurModifie.age);  // 31

// Ajouter des propriétés lors du spread
const produitBase = { nom: "T-shirt", prix: 29.99 };
const produitEnPromo = { ...produitBase, prix: 19.99, enPromo: true, reduction: "33%" };
console.log(produitEnPromo);
// { nom: "T-shirt", prix: 19.99, enPromo: true, reduction: "33%" }
```

### Spread sur les tableaux

```javascript
const premiers = [1, 2, 3];
const suivants = [4, 5, 6];

// Copier un tableau
const copiePremiers = [...premiers];

// Concaténer des tableaux
const tous = [...premiers, ...suivants];
console.log(tous); // [1, 2, 3, 4, 5, 6]

// Insérer des éléments
const avecMilieu = [...premiers, 3.5, ...suivants];
console.log(avecMilieu); // [1, 2, 3, 3.5, 4, 5, 6]

// Convertir un Set en tableau
const valeurs = new Set([1, 2, 2, 3, 3, 3]);
const sansDoublons = [...valeurs];
console.log(sansDoublons); // [1, 2, 3]

// Convertir une NodeList (DOM) en tableau
// const divs = [...document.querySelectorAll("div")];

// Passer un tableau comme arguments d'une fonction
const nombres = [5, 1, 8, 3, 9, 2];
console.log(Math.max(...nombres)); // 9
console.log(Math.min(...nombres)); // 1

// Équivalent ancien : apply
console.log(Math.max.apply(null, nombres)); // 9
```

---

## 4. Méthodes fonctionnelles des tableaux

Ces méthodes ne modifient pas le tableau original — elles retournent de nouveaux tableaux ou des valeurs.

### `map()` — Transformer chaque élément

```javascript
const nombres = [1, 2, 3, 4, 5];

// Doubler chaque valeur
const doubles = nombres.map(n => n * 2);
console.log(doubles);  // [2, 4, 6, 8, 10]
console.log(nombres);  // [1, 2, 3, 4, 5] — original inchangé

// Transformer des objets
const produits = [
  { id: 1, nom: "Pomme", prixHT: 1.00 },
  { id: 2, nom: "Banane", prixHT: 0.50 },
  { id: 3, nom: "Cerise", prixHT: 3.00 },
];

const produitsAvecTVA = produits.map(p => ({
  ...p,
  prixTTC: +(p.prixHT * 1.2).toFixed(2),
  label: `${p.nom} - ${(p.prixHT * 1.2).toFixed(2)}€`,
}));

console.log(produitsAvecTVA);
// [
//   { id: 1, nom: "Pomme", prixHT: 1, prixTTC: 1.2, label: "Pomme - 1.20€" },
//   ...
// ]

// map avec index
const items = ["a", "b", "c"];
const avecIndex = items.map((item, index) => `${index}: ${item}`);
console.log(avecIndex); // ["0: a", "1: b", "2: c"]
```

### `filter()` — Sélectionner des éléments

```javascript
const utilisateurs = [
  { nom: "Alice", age: 30, actif: true, score: 85 },
  { nom: "Bob", age: 17, actif: true, score: 72 },
  { nom: "Carol", age: 25, actif: false, score: 90 },
  { nom: "Dave", age: 22, actif: true, score: 45 },
  { nom: "Eve", age: 35, actif: true, score: 88 },
];

// Filtrer les utilisateurs actifs ET majeurs
const actifsMajeurs = utilisateurs.filter(u => u.actif && u.age >= 18);
console.log(actifsMajeurs.map(u => u.nom)); // ["Alice", "Dave", "Eve"]

// Filtrer avec score supérieur à 70
const bonScore = utilisateurs.filter(u => u.score > 70);
console.log(bonScore.map(u => u.nom)); // ["Alice", "Bob", "Carol", "Eve"]

// Supprimer un élément par ID (pattern immutable)
const elements = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];
const sansId2 = elements.filter(el => el.id !== 2);
console.log(sansId2); // [{ id: 1 }, { id: 3 }, { id: 4 }]
```

### `reduce()` — Réduire à une valeur

```javascript
const nombres = [1, 2, 3, 4, 5];

// Somme
const somme = nombres.reduce((accumulateur, valeurCourante) => {
  return accumulateur + valeurCourante;
}, 0); // 0 est la valeur initiale
console.log(somme); // 15

// Produit
const produit = nombres.reduce((acc, val) => acc * val, 1);
console.log(produit); // 120

// Maximum (sans Math.max)
const max = nombres.reduce((acc, val) => val > acc ? val : acc, -Infinity);
console.log(max); // 5

// Compter les occurrences
const fruits = ["pomme", "banane", "pomme", "cerise", "banane", "pomme"];
const comptage = fruits.reduce((acc, fruit) => {
  acc[fruit] = (acc[fruit] || 0) + 1;
  return acc;
}, {});
console.log(comptage); // { pomme: 3, banane: 2, cerise: 1 }

// Grouper des objets
const commandes = [
  { id: 1, statut: "livré", montant: 50 },
  { id: 2, statut: "en cours", montant: 30 },
  { id: 3, statut: "livré", montant: 80 },
  { id: 4, statut: "annulé", montant: 20 },
  { id: 5, statut: "en cours", montant: 45 },
];

const parStatut = commandes.reduce((acc, commande) => {
  if (!acc[commande.statut]) {
    acc[commande.statut] = [];
  }
  acc[commande.statut].push(commande);
  return acc;
}, {});

console.log(Object.keys(parStatut)); // ["livré", "en cours", "annulé"]
console.log(parStatut["livré"].length); // 2
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Écrire en live un pipeline map → filter → reduce sur un tableau de commandes : filtrer les commandes livrées, extraire les montants, calculer le total
> **Expliquer :** Montrer que ces méthodes sont chaînables et constituent un style de programmation "déclaratif" — on décrit QUOI on veut, pas COMMENT le calculer boucle par boucle.

---

### Chaînage des méthodes

```javascript
const ventes = [
  { vendeur: "Alice", produit: "Laptop", montant: 1200, mois: "janvier" },
  { vendeur: "Bob", produit: "Souris", montant: 35, mois: "janvier" },
  { vendeur: "Alice", produit: "Clavier", montant: 85, mois: "février" },
  { vendeur: "Carol", produit: "Laptop", montant: 1200, mois: "février" },
  { vendeur: "Bob", produit: "Laptop", montant: 1200, mois: "mars" },
  { vendeur: "Alice", produit: "Écran", montant: 450, mois: "mars" },
];

// Calculer le total des ventes d'Alice
const totalAlice = ventes
  .filter(v => v.vendeur === "Alice")    // Garder les ventes d'Alice
  .map(v => v.montant)                   // Extraire les montants
  .reduce((sum, montant) => sum + montant, 0); // Sommer

console.log(`Total Alice: ${totalAlice}€`); // Total Alice: 1735€

// Top vendeur
const totalParVendeur = ventes.reduce((acc, v) => {
  acc[v.vendeur] = (acc[v.vendeur] || 0) + v.montant;
  return acc;
}, {});

const topVendeur = Object.entries(totalParVendeur)
  .sort(([, a], [, b]) => b - a)
  .map(([nom, total]) => `${nom}: ${total}€`);

console.log(topVendeur); // ["Alice: 1735€", "Carol: 1200€", "Bob: 1235€"]
```

### Autres méthodes importantes

```javascript
const nombres = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// find() — premier élément qui correspond
const premierPair = nombres.find(n => n % 2 === 0);
console.log(premierPair); // 2

// findIndex() — index du premier élément qui correspond
const indexPremierPair = nombres.findIndex(n => n % 2 === 0);
console.log(indexPremierPair); // 1

// some() — au moins un élément correspond ?
console.log(nombres.some(n => n > 9));   // true
console.log(nombres.some(n => n > 100)); // false

// every() — tous les éléments correspondent ?
console.log(nombres.every(n => n > 0));  // true
console.log(nombres.every(n => n > 5));  // false

// flat() et flatMap()
const tableau2D = [[1, 2], [3, 4], [5, 6]];
console.log(tableau2D.flat()); // [1, 2, 3, 4, 5, 6]

const phrases = ["Bonjour le monde", "Hello world"];
const mots = phrases.flatMap(phrase => phrase.split(" "));
console.log(mots); // ["Bonjour", "le", "monde", "Hello", "world"]

// sort() — MUTE le tableau, attention !
const fruits = ["banane", "pomme", "cerise", "abricot"];
const fruitsTriés = [...fruits].sort(); // Copier avant de trier
console.log(fruitsTriés); // ["abricot", "banane", "cerise", "pomme"]

// sort() avec comparateur pour les nombres
const valeurs = [10, 1, 25, 3, 100, 8];
const trieCroissant = [...valeurs].sort((a, b) => a - b);
const trieDecroissant = [...valeurs].sort((a, b) => b - a);
console.log(trieCroissant);  // [1, 3, 8, 10, 25, 100]
console.log(trieDecroissant); // [100, 25, 10, 8, 3, 1]

// Trier des objets
const etudiants = [
  { nom: "Charlie", note: 15 },
  { nom: "Alice", note: 18 },
  { nom: "Bob", note: 12 },
];
const parNote = [...etudiants].sort((a, b) => b.note - a.note);
console.log(parNote.map(e => `${e.nom}: ${e.note}`));
// ["Alice: 18", "Charlie: 15", "Bob: 12"]
```

---

## 5. Object.assign() et copies profondes

```javascript
// Object.assign — fusion d'objets (comme spread)
const cible = { a: 1, b: 2 };
const source = { b: 3, c: 4 };
const resultat = Object.assign({}, cible, source);
console.log(resultat); // { a: 1, b: 3, c: 4 }

// Copie profonde (deep copy) — méthodes disponibles
const objet = { a: 1, b: { c: 2, d: [3, 4] } };

// Méthode 1 : JSON (simple mais limité — perd les fonctions, Date, undefined, Symbol)
const copieJSON = JSON.parse(JSON.stringify(objet));
copieJSON.b.c = 99;
console.log(objet.b.c);     // 2 — original intact
console.log(copieJSON.b.c); // 99

// Méthode 2 : structuredClone (moderne, recommandé)
const copieClone = structuredClone(objet);
copieClone.b.d.push(5);
console.log(objet.b.d);      // [3, 4] — intact
console.log(copieClone.b.d); // [3, 4, 5]
```

---

## 6. Set et Map

```javascript
// Set — collection de valeurs UNIQUES
const ensemble = new Set([1, 2, 3, 2, 1, 4]);
console.log(ensemble);      // Set { 1, 2, 3, 4 }
console.log(ensemble.size); // 4

ensemble.add(5);
ensemble.delete(2);
console.log(ensemble.has(3)); // true
console.log(ensemble.has(2)); // false

// Dédupliquer un tableau avec Set
const tableau = [1, 2, 2, 3, 3, 3, 4];
const unique = [...new Set(tableau)];
console.log(unique); // [1, 2, 3, 4]

// Map — collection de paires clé/valeur (les clés peuvent être de n'importe quel type)
const carte = new Map();
carte.set("nom", "Alice");
carte.set(42, "la réponse");
carte.set(true, "valide");

const objetCle = { id: 1 };
carte.set(objetCle, "référence à un objet");

console.log(carte.get("nom"));     // "Alice"
console.log(carte.get(42));        // "la réponse"
console.log(carte.get(objetCle));  // "référence à un objet"
console.log(carte.size);           // 4
console.log(carte.has("nom"));     // true

// Itérer sur une Map
for (const [cle, valeur] of carte) {
  console.log(`${String(cle)} → ${valeur}`);
}

// Convertir en tableau
const tableau2 = [...carte.entries()];
```

---

## Récapitulatif — Quand utiliser quoi ?

| Besoin | Solution |
|---|---|
| Extraire des propriétés d'un objet | Destructuring `const { a, b } = obj` |
| Copier/fusionner des objets | Spread `{ ...obj1, ...obj2 }` |
| Transformer chaque élément d'un tableau | `map()` |
| Sélectionner des éléments | `filter()` |
| Calculer une valeur agrégée | `reduce()` |
| Trouver un élément | `find()` / `findIndex()` |
| Tester une condition | `some()` / `every()` |
| Valeurs uniques | `Set` |
| Dictionnaire avec clés non-string | `Map` |
| Copie profonde simple | `structuredClone()` |
