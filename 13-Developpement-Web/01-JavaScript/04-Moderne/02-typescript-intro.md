# 02 — Introduction à TypeScript : Types, Interfaces, Generics, tsconfig

## Introduction

TypeScript est un **sur-ensemble typé de JavaScript**. Tout code JavaScript valide est du TypeScript valide. TypeScript ajoute un système de types statiques qui sont vérifiés à la compilation — les types n'existent plus à l'exécution (effacement de types).

**Pourquoi TypeScript ?**
- Détecte les bugs avant l'exécution
- Améliore l'autocomplétion et la navigation dans le code
- Documentation vivante du code (les types sont la documentation)
- Refactoring plus sûr

---

## 1. Installation et configuration

```bash
# Installation globale
npm install -g typescript

# Ou en dépendance de développement d'un projet
npm install -D typescript

# Créer un fichier tsconfig.json
npx tsc --init
```

### Configuration tsconfig.json recommandée

```json
{
  "compilerOptions": {
    // Cible d'exécution
    "target": "ES2022",            // Version JS produite
    "module": "ESNext",            // Système de modules
    "moduleResolution": "bundler", // Pour Vite/webpack
    "lib": ["ES2022", "DOM", "DOM.Iterable"],

    // Rigueur du typage
    "strict": true,              // Active toutes les vérifications strictes
    "noImplicitAny": true,       // Interdit les types 'any' implicites
    "strictNullChecks": true,    // null et undefined sont des types distincts
    "noImplicitReturns": true,   // Toutes les branches doivent retourner une valeur

    // Bonnes pratiques
    "noUnusedLocals": true,          // Avertit pour les variables non utilisées
    "noUnusedParameters": true,      // Avertit pour les paramètres non utilisés
    "exactOptionalPropertyTypes": true, // Différencie absent vs undefined
    "noFallthroughCasesInSwitch": true, // Prévient les switch sans break

    // Interopérabilité
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "isolatedModules": true,     // Requis par Vite/esbuild

    // Paths
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]  // Alias pour les imports
    },

    // Sortie
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,    // Génère les fichiers .d.ts
    "sourceMap": true       // Pour le débogage
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 2. Types de base

```typescript
// Types primitifs — identiques à JavaScript mais déclarés explicitement
const prenom: string = "Alice";
const age: number = 30;
const actif: boolean = true;
const identifiant: bigint = 9007199254740993n;
const cle: symbol = Symbol("unique");

// TypeScript infère généralement le type — annotation souvent inutile
const nom = "Bob";  // TypeScript sait que c'est une string

// Types spéciaux
let valeurQuelconque: any = 42;     // Désactive la vérification — à éviter
valeurQuelconque = "string";         // Autorisé avec any
valeurQuelconque = { objet: true };  // Autorisé avec any

let inconnue: unknown = 42;          // Plus sûr que any
// console.log(inconnue.toFixed(2)); // Erreur : on ne peut pas utiliser unknown directement
if (typeof inconnue === "number") {
  console.log(inconnue.toFixed(2)); // OK : TypeScript sait que c'est un number ici
}

// void — fonction qui ne retourne rien (ou undefined)
function logMessage(message: string): void {
  console.log(message);
  // Pas de return (ou return; sans valeur)
}

// never — code qui ne peut jamais se terminer normalement
function lancerErreur(message: string): never {
  throw new Error(message);
  // Jamais atteint
}

function boucleInfinie(): never {
  while (true) {}
}

// null et undefined — avec strictNullChecks activé
let valeurNullable: string | null = "bonjour";
valeurNullable = null; // OK

let optionnel: string | undefined = "valeur";
optionnel = undefined; // OK

// Avec strictNullChecks, on ne peut pas assigner null à une variable non-nullable
// let texte: string = null; // Erreur !
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** VS Code — dans un fichier .ts, montrer les soulignements rouges en temps réel quand on essaie d'assigner une string à un number, ou d'appeler une méthode sur null. Puis montrer l'autocomplétion avec les bonnes méthodes disponibles.
> **Expliquer :** Le compilateur TypeScript s'exécute en permanence dans VS Code (via tsserver). On voit les erreurs IMMÉDIATEMENT, avant même d'exécuter le code. C'est ce qui rend TypeScript si productif.

---

## 3. Types composés

### Union Types

```typescript
// Une valeur peut être de plusieurs types
type ID = string | number;
type Reponse = "oui" | "non" | "peut-être"; // Union de literals
type StatutCommande = "en_attente" | "confirmée" | "expédiée" | "livrée" | "annulée";

function traiterID(id: ID): string {
  if (typeof id === "string") {
    return id.toUpperCase(); // TypeScript sait que c'est une string ici
  }
  return id.toString(); // Ici, TypeScript sait que c'est un number
}

// Narrowing — rétrécissement du type
function afficherValeur(valeur: string | number | boolean) {
  if (typeof valeur === "string") {
    console.log(`String: ${valeur.toUpperCase()}`);
  } else if (typeof valeur === "number") {
    console.log(`Number: ${valeur.toFixed(2)}`);
  } else {
    console.log(`Boolean: ${valeur}`);
  }
}

// Discriminated unions — très puissant
type Forme =
  | { type: "cercle"; rayon: number }
  | { type: "rectangle"; largeur: number; hauteur: number }
  | { type: "triangle"; base: number; hauteur: number };

function calculerAire(forme: Forme): number {
  switch (forme.type) {
    case "cercle":
      return Math.PI * forme.rayon ** 2; // TypeScript sait que forme.rayon existe
    case "rectangle":
      return forme.largeur * forme.hauteur;
    case "triangle":
      return (forme.base * forme.hauteur) / 2;
    // Pas de default nécessaire — TypeScript vérifie l'exhaustivité
  }
}
```

### Intersection Types

```typescript
type Personne = { nom: string; age: number };
type Employe = { entreprise: string; poste: string };
type EmployePersonne = Personne & Employe; // Doit avoir toutes les propriétés des deux

const employe: EmployePersonne = {
  nom: "Alice",
  age: 30,
  entreprise: "TechCorp",
  poste: "Développeuse",
};
```

---

## 4. Interfaces

```typescript
// Interface — décrit la forme d'un objet
interface Utilisateur {
  readonly id: number;     // readonly — ne peut pas être modifié après création
  nom: string;
  email: string;
  age?: number;            // ? — propriété optionnelle
  adresse?: {
    rue: string;
    ville: string;
  };
}

// Utilisation
const user: Utilisateur = {
  id: 1,
  nom: "Alice",
  email: "alice@example.com",
};

// user.id = 2; // Erreur : propriété readonly

// Interfaces de fonctions
interface ComparaisonFn {
  (a: number, b: number): number;
}

const comparerCroissant: ComparaisonFn = (a, b) => a - b;
const comparerDecroissant: ComparaisonFn = (a, b) => b - a;

// Extension d'interfaces
interface Animal {
  nom: string;
  age: number;
}

interface AnimalDomestique extends Animal {
  proprietaire: string;
  vaccins: string[];
}

interface ChienDomestique extends AnimalDomestique {
  race: string;
  dresserCommandement(commande: string): boolean;
}

// Implémentation dans une classe
class Chien implements ChienDomestique {
  nom: string;
  age: number;
  proprietaire: string;
  vaccins: string[];
  race: string;

  constructor(nom: string, race: string, proprietaire: string) {
    this.nom = nom;
    this.race = race;
    this.proprietaire = proprietaire;
    this.age = 0;
    this.vaccins = [];
  }

  dresserCommandement(commande: string): boolean {
    console.log(`${this.nom} essaie "${commande}"`);
    return Math.random() > 0.3; // 70% de chances de succès
  }
}

// Fusion de déclarations (Declaration Merging) — unique aux interfaces
interface Config {
  debug: boolean;
}
interface Config {  // Pas d'erreur — les deux définitions sont fusionnées
  version: string;
}
const config: Config = { debug: true, version: "1.0" };
```

---

## 5. Types Alias vs Interfaces

```typescript
// Type alias — plus flexible
type Point = { x: number; y: number };
type Callback<T> = (valeur: T) => void;
type StringOrNumber = string | number;
type Tuple = [string, number, boolean]; // Tuple

// Interface — uniquement pour les objets/classes, extensible
interface IPoint { x: number; y: number }

// Différences :
// 1. Types peuvent représenter tout type (primitifs, unions, tuples)
// 2. Interfaces supportent la fusion de déclarations
// 3. Les deux peuvent être étendus, mais syntaxe différente

// Extension d'un type
type Point3D = Point & { z: number };

// Extension d'une interface
interface IPoint3D extends IPoint { z: number }

// Règle générale : préférer les interfaces pour les objets publics d'une API
// Utiliser les types alias pour tout le reste
```

---

## 6. Generics (Types génériques)

Les génériques permettent d'écrire du code qui fonctionne avec plusieurs types tout en restant type-safe.

```typescript
// Sans générics — répétitif et peu sûr
function premierElementString(arr: string[]): string | undefined {
  return arr[0];
}
function premierElementNumber(arr: number[]): number | undefined {
  return arr[0];
}

// Avec générics — réutilisable et type-safe
function premierElement<T>(arr: T[]): T | undefined {
  return arr[0];
}

const prenom = premierElement(["Alice", "Bob", "Carol"]); // Type inféré : string
const nombre = premierElement([1, 2, 3]);                  // Type inféré : number
const explicite = premierElement<boolean>([true, false]);  // Type explicite

// Plusieurs paramètres de type
function paire<K, V>(cle: K, valeur: V): [K, V] {
  return [cle, valeur];
}

const p1 = paire("nom", "Alice");       // [string, string]
const p2 = paire(1, { actif: true });   // [number, { actif: boolean }]

// Contraintes sur les génériques (extends)
interface AvecId {
  id: number;
}

function trouverParId<T extends AvecId>(elements: T[], id: number): T | undefined {
  return elements.find(el => el.id === id);
}

const users = [
  { id: 1, nom: "Alice", email: "alice@ex.com" },
  { id: 2, nom: "Bob", email: "bob@ex.com" },
];

const user = trouverParId(users, 1);
// TypeScript sait que user est { id: number, nom: string, email: string } | undefined
console.log(user?.nom); // "Alice"

// trouverParId([{ nom: "Alice" }], 1); // Erreur : pas de propriété 'id'
```

### Classes génériques

```typescript
class Stack<T> {
  #elements: T[] = [];

  push(element: T): void {
    this.#elements.push(element);
  }

  pop(): T | undefined {
    return this.#elements.pop();
  }

  peek(): T | undefined {
    return this.#elements.at(-1);
  }

  get size(): number {
    return this.#elements.length;
  }

  isEmpty(): boolean {
    return this.#elements.length === 0;
  }

  toArray(): T[] {
    return [...this.#elements];
  }
}

const pileNombres = new Stack<number>();
pileNombres.push(1);
pileNombres.push(2);
pileNombres.push(3);
console.log(pileNombres.pop());  // 3
console.log(pileNombres.size);   // 2

// pileNombres.push("string"); // Erreur de type !

// Repository générique
class Repository<T extends { id: number }> {
  #items: Map<number, T> = new Map();

  add(item: T): T {
    this.#items.set(item.id, item);
    return item;
  }

  findById(id: number): T | undefined {
    return this.#items.get(id);
  }

  findAll(): T[] {
    return [...this.#items.values()];
  }

  update(id: number, partiel: Partial<Omit<T, "id">>): T | undefined {
    const existant = this.#items.get(id);
    if (!existant) return undefined;

    const modifie = { ...existant, ...partiel } as T;
    this.#items.set(id, modifie);
    return modifie;
  }

  delete(id: number): boolean {
    return this.#items.delete(id);
  }

  get count(): number {
    return this.#items.size;
  }
}

interface Produit {
  id: number;
  nom: string;
  prix: number;
  stock: number;
}

const reposProduits = new Repository<Produit>();
reposProduits.add({ id: 1, nom: "Laptop", prix: 999, stock: 10 });
reposProduits.add({ id: 2, nom: "Souris", prix: 29, stock: 50 });

const laptop = reposProduits.findById(1);
console.log(laptop?.nom); // "Laptop"

reposProduits.update(1, { stock: 9 });
```

---

## 7. Utility Types — Types utilitaires intégrés

```typescript
interface Utilisateur {
  id: number;
  nom: string;
  email: string;
  age: number;
  actif: boolean;
}

// Partial<T> — toutes les propriétés deviennent optionnelles
type MiseAJourUtilisateur = Partial<Utilisateur>;
const mise: MiseAJourUtilisateur = { nom: "Alice" }; // OK — seule la propriété nom

// Required<T> — toutes les propriétés deviennent obligatoires
interface Config { debug?: boolean; version?: string }
type ConfigComplete = Required<Config>;
// { debug: boolean; version: string } — plus d'optionnels

// Readonly<T> — toutes les propriétés deviennent readonly
type UtilisateurImmuable = Readonly<Utilisateur>;
const u: UtilisateurImmuable = { id: 1, nom: "Bob", email: "b@b.fr", age: 25, actif: true };
// u.nom = "Alice"; // Erreur : propriété readonly

// Pick<T, K> — sélectionner certaines propriétés
type UtilisateurPublic = Pick<Utilisateur, "id" | "nom">;
// { id: number; nom: string }

// Omit<T, K> — exclure certaines propriétés
type UtilisateurSansId = Omit<Utilisateur, "id">;
// { nom: string; email: string; age: number; actif: boolean }

// Record<K, V> — objet avec clés de type K et valeurs de type V
type ScoresParJoueur = Record<string, number>;
const scores: ScoresParJoueur = { alice: 100, bob: 85, carol: 92 };

type CacheParStatut = Record<StatutCommande, Utilisateur[]>;

// Exclude<T, U> — exclure des types d'une union
type SansNull = Exclude<string | number | null | undefined, null | undefined>;
// string | number

// Extract<T, U> — extraire des types d'une union
type StringsEtNumbers = Extract<string | number | boolean, string | number>;
// string | number

// NonNullable<T> — supprimer null et undefined
type Definit = NonNullable<string | null | undefined>;
// string

// ReturnType<T> — type de retour d'une fonction
function creerUtilisateur() {
  return { id: 1, nom: "Alice", createdAt: new Date() };
}
type TypeUtilisateur = ReturnType<typeof creerUtilisateur>;
// { id: number; nom: string; createdAt: Date }

// Parameters<T> — types des paramètres d'une fonction
function creerCommande(userId: number, produits: string[], total: number) {}
type ParamsCommande = Parameters<typeof creerCommande>;
// [userId: number, produits: string[], total: number]
```

---

## 8. Type Guards

```typescript
// Fonctions qui retournent un type prédicat
function estString(valeur: unknown): valeur is string {
  return typeof valeur === "string";
}

function estUtilisateur(obj: unknown): obj is Utilisateur {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "nom" in obj &&
    "email" in obj
  );
}

function traiter(donnees: unknown) {
  if (estString(donnees)) {
    console.log(donnees.toUpperCase()); // TypeScript sait que c'est une string
  } else if (estUtilisateur(donnees)) {
    console.log(donnees.nom);           // TypeScript sait que c'est un Utilisateur
  }
}

// Assertion de type (à utiliser avec prudence)
const canvas = document.querySelector("canvas") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!; // ! = non-null assertion
```

---

## Récapitulatif

| Concept | Exemple | Utilité |
|---|---|---|
| Types de base | `string`, `number`, `boolean` | Typage des variables |
| Union | `string \| number` | Valeur de plusieurs types possibles |
| Interface | `interface User { id: number }` | Forme des objets |
| Type alias | `type ID = string \| number` | Réutilisabilité des types |
| Generics | `function fn<T>(x: T): T` | Code réutilisable type-safe |
| Partial<T> | `Partial<User>` | Toutes les props optionnelles |
| Omit<T,K> | `Omit<User, "password">` | Exclure des propriétés |
| Type Guard | `x is string` | Narrowing de type personnalisé |
