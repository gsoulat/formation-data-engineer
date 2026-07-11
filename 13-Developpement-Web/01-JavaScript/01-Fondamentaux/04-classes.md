# 04 — Classes : Constructor, Héritage, Private Fields, Static

## Introduction

Les classes en JavaScript (introduites avec ES6) offrent une syntaxe claire pour la programmation orientée objet. Il est important de comprendre qu'elles ne changent pas le système de prototypes sous-jacent — elles en sont une **surcouche syntaxique** (*syntactic sugar*). Néanmoins, les classes modernes (ES2022) apportent de véritables nouvelles fonctionnalités comme les champs privés.

---

## 1. La syntaxe de base

### Avant les classes : les fonctions constructeurs

```javascript
// Ancienne syntaxe — encore valide mais peu lisible
function Animal(nom, espece) {
  this.nom = nom;
  this.espece = espece;
}

Animal.prototype.parler = function() {
  return `${this.nom} fait du bruit`;
};

const chien = new Animal("Rex", "chien");
console.log(chien.parler()); // "Rex fait du bruit"
```

### Avec la syntaxe class (ES6)

```javascript
class Animal {
  // Le constructeur est appelé lors de l'instanciation avec 'new'
  constructor(nom, espece) {
    this.nom = nom;
    this.espece = espece;
  }

  // Méthode d'instance (définie sur le prototype)
  parler() {
    return `${this.nom} fait du bruit`;
  }

  // Getter — accès comme une propriété
  get description() {
    return `${this.nom} est un ${this.espece}`;
  }

  // Setter
  set nomAnimal(nouveauNom) {
    if (typeof nouveauNom !== "string" || nouveauNom.length < 2) {
      throw new Error("Nom invalide");
    }
    this.nom = nouveauNom;
  }

  toString() {
    return `Animal(${this.nom}, ${this.espece})`;
  }
}

const chien = new Animal("Rex", "chien");
console.log(chien.nom);          // "Rex"
console.log(chien.parler());     // "Rex fait du bruit"
console.log(chien.description);  // "Rex est un chien" (sans parenthèses, c'est un getter)
chien.nomAnimal = "Max";         // Utilise le setter
console.log(chien.nom);          // "Max"
console.log(String(chien));      // "Animal(Max, chien)"

// Vérifications
console.log(chien instanceof Animal); // true
console.log(typeof Animal);           // "function" — les classes sont des fonctions !
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools — créer une instance de classe, puis inspecter l'objet dans la console (cliquer sur le triangle pour développer) pour voir les propriétés d'instance vs les méthodes sur le prototype
> **Expliquer :** Les méthodes définies dans la classe ne sont PAS copiées sur chaque instance — elles sont sur le prototype. C'est ce qui rend les classes mémoire-efficaces : 1000 instances partagent les mêmes méthodes en mémoire.

---

## 2. Champs de classe (Class Fields — ES2022)

Les champs de classe permettent de déclarer des propriétés directement dans le corps de la classe, sans passer par le constructeur.

```javascript
class Compteur {
  // Champ public — déclaration et initialisation
  valeur = 0;
  pas = 1;

  constructor(valeurInitiale = 0, pas = 1) {
    this.valeur = valeurInitiale;
    this.pas = pas;
  }

  incrementer() {
    this.valeur += this.pas;
    return this;
  }

  decrementer() {
    this.valeur -= this.pas;
    return this;
  }

  afficher() {
    console.log(`Valeur: ${this.valeur}`);
    return this;
  }
}

const c = new Compteur(10, 2);
c.incrementer().incrementer().afficher(); // Valeur: 14
c.decrementer().afficher();               // Valeur: 12
```

### Champs privés (Private Fields — #)

Les champs privés sont une vraie nouveauté ES2022 — pas juste une convention. Le symbole `#` rend le champ réellement inaccessible depuis l'extérieur.

```javascript
class CompteBancaire {
  // Champs privés — accessibles UNIQUEMENT depuis la classe
  #solde;
  #titulaire;
  #historique = [];
  #nombreOperations = 0;

  constructor(titulaire, soldeInitial = 0) {
    this.#titulaire = titulaire;
    this.#solde = soldeInitial;
    this.#enregistrer("création", soldeInitial);
  }

  // Méthode privée
  #enregistrer(type, montant) {
    this.#historique.push({
      type,
      montant,
      soldeApres: this.#solde,
      date: new Date().toISOString(),
    });
    this.#nombreOperations++;
  }

  #validerMontant(montant) {
    if (typeof montant !== "number" || montant <= 0) {
      throw new TypeError("Le montant doit être un nombre positif");
    }
  }

  // Interface publique
  deposer(montant) {
    this.#validerMontant(montant);
    this.#solde += montant;
    this.#enregistrer("dépôt", montant);
    console.log(`Dépôt de ${montant}€ effectué. Solde: ${this.#solde}€`);
    return this;
  }

  retirer(montant) {
    this.#validerMontant(montant);
    if (montant > this.#solde) {
      throw new Error(`Solde insuffisant (disponible: ${this.#solde}€)`);
    }
    this.#solde -= montant;
    this.#enregistrer("retrait", montant);
    console.log(`Retrait de ${montant}€ effectué. Solde: ${this.#solde}€`);
    return this;
  }

  get solde() {
    return this.#solde;
  }

  get titulaire() {
    return this.#titulaire;
  }

  get historique() {
    return [...this.#historique]; // Copie pour protéger
  }

  get nombreOperations() {
    return this.#nombreOperations;
  }

  toString() {
    return `Compte de ${this.#titulaire} — Solde: ${this.#solde}€`;
  }
}

const compte = new CompteBancaire("Alice", 1000);
compte.deposer(500).retirer(200);

console.log(compte.solde);           // 1300
console.log(compte.titulaire);       // "Alice"
console.log(compte.nombreOperations); // 3
console.log(String(compte));          // "Compte de Alice — Solde: 1300€"

// Les champs privés sont VRAIMENT privés
// console.log(compte.#solde);   // SyntaxError
// console.log(compte["#solde"]); // undefined (pas d'erreur, mais rien)

// Vérifier si un objet a un champ privé
class Test {
  #valeur = 42;
  static aValeur(obj) {
    return #valeur in obj; // Syntaxe 'in' pour les champs privés
  }
}
const t = new Test();
console.log(Test.aValeur(t));         // true
console.log(Test.aValeur({}));        // false
```

---

## 3. Membres statiques

Les membres statiques appartiennent à la **classe** elle-même, pas aux instances.

```javascript
class Utilisateur {
  // Champ statique
  static nombreInstances = 0;
  static readonly VERSION = "2.0";

  // Champ d'instance
  id;
  nom;
  email;

  constructor(nom, email) {
    Utilisateur.nombreInstances++;
    this.id = Utilisateur.nombreInstances;
    this.nom = nom;
    this.email = email;
  }

  // Méthode statique — ne peut pas utiliser 'this' pour accéder aux propriétés d'instance
  static creer(nom, email) {
    // Validation
    if (!email.includes("@")) throw new Error("Email invalide");
    return new Utilisateur(nom, email);
  }

  static reinitialiserCompteur() {
    Utilisateur.nombreInstances = 0;
  }

  // Méthode statique utilitaire
  static comparer(u1, u2) {
    return u1.nom.localeCompare(u2.nom);
  }

  afficher() {
    console.log(`[${this.id}] ${this.nom} <${this.email}>`);
  }
}

const alice = Utilisateur.creer("Alice", "alice@example.com");
const bob = Utilisateur.creer("Bob", "bob@example.com");
const carol = new Utilisateur("Carol", "carol@example.com");

alice.afficher(); // [1] Alice <alice@example.com>
bob.afficher();   // [2] Bob <bob@example.com>
carol.afficher(); // [3] Carol <carol@example.com>

console.log(Utilisateur.nombreInstances); // 3
console.log(Utilisateur.VERSION);          // "2.0"

// Les méthodes statiques ne sont pas accessibles sur les instances
// alice.creer(); // TypeError : alice.creer is not a function

const utilisateurs = [bob, carol, alice];
utilisateurs.sort(Utilisateur.comparer);
utilisateurs.forEach(u => u.afficher());
// [1] Alice ...
// [2] Bob ...
// [3] Carol ...
```

---

## 4. Héritage avec `extends` et `super`

```javascript
class Forme {
  constructor(couleur = "noir") {
    this.couleur = couleur;
  }

  aire() {
    throw new Error(`La méthode aire() doit être implémentée par ${this.constructor.name}`);
  }

  perimetre() {
    throw new Error(`La méthode perimetre() doit être implémentée par ${this.constructor.name}`);
  }

  toString() {
    return `${this.constructor.name}(couleur: ${this.couleur}, aire: ${this.aire().toFixed(2)})`;
  }
}

class Rectangle extends Forme {
  constructor(largeur, hauteur, couleur) {
    super(couleur); // OBLIGATOIRE avant d'utiliser 'this' dans la sous-classe
    this.largeur = largeur;
    this.hauteur = hauteur;
  }

  aire() {
    return this.largeur * this.hauteur;
  }

  perimetre() {
    return 2 * (this.largeur + this.hauteur);
  }
}

class Carre extends Rectangle {
  constructor(cote, couleur) {
    super(cote, cote, couleur); // Réutilise Rectangle avec largeur = hauteur
  }

  // Override de toString
  toString() {
    return `Carré(côté: ${this.largeur}, ${super.toString()})`;
    //                                          ↑ super.toString() appelle la méthode de la classe parente
  }
}

class Cercle extends Forme {
  #rayon;

  constructor(rayon, couleur) {
    super(couleur);
    this.#rayon = rayon;
  }

  get rayon() { return this.#rayon; }

  aire() {
    return Math.PI * this.#rayon ** 2;
  }

  perimetre() {
    return 2 * Math.PI * this.#rayon;
  }
}

const rect = new Rectangle(10, 5, "rouge");
const carre = new Carre(7, "bleu");
const cercle = new Cercle(4, "vert");

console.log(rect.aire());        // 50
console.log(carre.aire());       // 49
console.log(cercle.aire());      // 50.26...
console.log(String(rect));       // "Rectangle(couleur: rouge, aire: 50.00)"
console.log(String(carre));      // "Carré(côté: 7, Rectangle(couleur: bleu, aire: 49.00))"

// instanceof avec héritage
console.log(carre instanceof Carre);     // true
console.log(carre instanceof Rectangle); // true
console.log(carre instanceof Forme);     // true
console.log(carre instanceof Cercle);    // false

// Polymorphisme
const formes = [rect, carre, cercle, new Rectangle(3, 8, "jaune")];
const aireTotal = formes.reduce((sum, forme) => sum + forme.aire(), 0);
console.log(`Aire totale: ${aireTotal.toFixed(2)}`);
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans la console, créer les formes ci-dessus et vérifier les instanceof en cascade — montrer la chaîne de prototypes avec `Object.getPrototypeOf()`
> **Expliquer :** L'héritage en JS fonctionne via la chaîne de prototypes. `extends` configure automatiquement cette chaîne. `instanceof` parcourt la chaîne pour vérifier l'appartenance.

---

## 5. Mixins — Composition vs Héritage

JavaScript ne supporte qu'un héritage simple (une seule classe parente). Les mixins permettent de combiner des comportements de plusieurs sources.

```javascript
// Un mixin est une fonction qui retourne une classe enrichie
const Serializable = (Base) => class extends Base {
  toJSON() {
    return JSON.stringify(this);
  }

  static fromJSON(json) {
    return Object.assign(new this(), JSON.parse(json));
  }
};

const Timestamped = (Base) => class extends Base {
  constructor(...args) {
    super(...args);
    this.createdAt = new Date().toISOString();
    this.updatedAt = new Date().toISOString();
  }

  touch() {
    this.updatedAt = new Date().toISOString();
    return this;
  }
};

const Validatable = (Base) => class extends Base {
  validate() {
    const errors = [];
    // Logique de validation générique
    for (const [key, value] of Object.entries(this)) {
      if (value === null || value === undefined) {
        errors.push(`${key} ne peut pas être null/undefined`);
      }
    }
    return { valide: errors.length === 0, erreurs: errors };
  }
};

// Composition des mixins
class Produit extends Serializable(Timestamped(Validatable(Object))) {
  constructor(nom, prix) {
    super();
    this.nom = nom;
    this.prix = prix;
  }
}

const p = new Produit("Ordinateur", 999);
console.log(p.createdAt);           // ISO date string
console.log(p.toJSON());             // JSON de l'objet
console.log(p.validate());           // { valide: true, erreurs: [] }
```

---

## 6. Classes abstraites (pattern)

JavaScript n'a pas de vraies classes abstraites, mais on peut les simuler :

```javascript
class ClasseAbstraite {
  constructor() {
    if (new.target === ClasseAbstraite) {
      throw new Error("ClasseAbstraite ne peut pas être instanciée directement");
    }
  }

  // Méthode abstraite — doit être implémentée par les sous-classes
  methodeAbstraite() {
    throw new Error(`${this.constructor.name} doit implémenter methodeAbstraite()`);
  }
}

class ClasseConcrete extends ClasseAbstraite {
  methodeAbstraite() {
    return "Implémentation concrète";
  }
}

// new ClasseAbstraite();  // Error: ClasseAbstraite ne peut pas être instanciée
const obj = new ClasseConcrete(); // OK
console.log(obj.methodeAbstraite()); // "Implémentation concrète"
```

---

## 7. Exemple complet — Système de gestion

```javascript
class Entite {
  static #compteur = 0;
  #id;
  #createdAt;

  constructor() {
    Entite.#compteur++;
    this.#id = Entite.#compteur;
    this.#createdAt = new Date();
  }

  get id() { return this.#id; }
  get createdAt() { return this.#createdAt; }
}

class Personne extends Entite {
  #prenom;
  #nom;
  #email;

  constructor(prenom, nom, email) {
    super();
    this.#prenom = prenom;
    this.#nom = nom;
    this.#email = email;
  }

  get nomComplet() { return `${this.#prenom} ${this.#nom}`; }
  get email() { return this.#email; }

  set email(nouvelEmail) {
    if (!nouvelEmail.includes("@")) throw new Error("Email invalide");
    this.#email = nouvelEmail;
  }

  toString() {
    return `[${this.id}] ${this.nomComplet} <${this.#email}>`;
  }
}

class Employe extends Personne {
  #poste;
  #salaire;
  static #grilleSalaires = {
    junior: { min: 30000, max: 45000 },
    senior: { min: 45000, max: 70000 },
    lead: { min: 70000, max: 100000 },
  };

  constructor(prenom, nom, email, poste, salaire) {
    super(prenom, nom, email);
    this.#poste = poste;
    this.#validerSalaire(salaire, poste);
    this.#salaire = salaire;
  }

  #validerSalaire(salaire, poste) {
    const grille = Employe.#grilleSalaires[poste];
    if (!grille) throw new Error(`Poste inconnu: ${poste}`);
    if (salaire < grille.min || salaire > grille.max) {
      throw new Error(`Salaire hors grille pour ${poste}: [${grille.min}, ${grille.max}]`);
    }
  }

  get poste() { return this.#poste; }
  get salaire() { return this.#salaire; }

  augmenter(pourcentage) {
    const nouveauSalaire = this.#salaire * (1 + pourcentage / 100);
    this.#validerSalaire(nouveauSalaire, this.#poste);
    this.#salaire = nouveauSalaire;
    console.log(`${this.nomComplet}: nouveau salaire ${this.#salaire.toFixed(0)}€`);
    return this;
  }

  toString() {
    return `${super.toString()} — ${this.#poste} (${this.#salaire.toLocaleString()}€)`;
  }
}

const alice = new Employe("Alice", "Martin", "alice@co.fr", "senior", 55000);
const bob = new Employe("Bob", "Durand", "bob@co.fr", "junior", 35000);

console.log(String(alice)); // [1] Alice Martin <alice@co.fr> — senior (55 000€)
alice.augmenter(10);         // Alice Martin: nouveau salaire 60500€
console.log(alice instanceof Employe); // true
console.log(alice instanceof Personne); // true
console.log(alice instanceof Entite);   // true
```

---

## Récapitulatif

| Fonctionnalité | Syntaxe | Disponibilité |
|---|---|---|
| Classe de base | `class Foo { constructor() {} }` | ES6 |
| Héritage | `class Bar extends Foo { constructor() { super() } }` | ES6 |
| Getter/Setter | `get prop() {}` / `set prop(v) {}` | ES6 |
| Méthode statique | `static maMethode() {}` | ES6 |
| Champ public | `maVariable = valeur;` (sans `this`) | ES2022 |
| Champ privé | `#maVariable = valeur;` | ES2022 |
| Méthode privée | `#maMethode() {}` | ES2022 |
| Champ statique privé | `static #compteur = 0;` | ES2022 |
