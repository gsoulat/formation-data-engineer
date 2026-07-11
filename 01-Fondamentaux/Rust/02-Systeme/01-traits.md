# Rust — Traits : Définition, impl, Génériques, Trait Bounds, Traits Communs

## 1. Qu'est-ce qu'un trait ?

Un **trait** définit une interface : un ensemble de méthodes qu'un type doit implémenter. C'est l'équivalent des interfaces Java, mais plus puissant.

```rust
// Définition d'un trait
pub trait Saluer {
    // Méthode requise (doit être implémentée)
    fn salutation(&self) -> String;

    // Méthode par défaut (peut être surchargée)
    fn saluer(&self) {
        println!("{}", self.salutation());
    }
}

// Implémenter le trait pour un type
struct Personne {
    nom: String,
    langue: String,
}

impl Saluer for Personne {
    fn salutation(&self) -> String {
        match self.langue.as_str() {
            "fr" => format!("Bonjour, {} !", self.nom),
            "en" => format!("Hello, {} !", self.nom),
            "es" => format!("¡Hola, {} !", self.nom),
            _    => format!("Hi, {} !", self.nom),
        }
    }
    // saluer() utilise l'implémentation par défaut
}

struct Robot { id: u32 }

impl Saluer for Robot {
    fn salutation(&self) -> String {
        format!("BEEP BOOP, je suis le robot {}", self.id)
    }

    // Surcharger la méthode par défaut
    fn saluer(&self) {
        println!("*sons mécaniques* {}", self.salutation());
    }
}

fn main() {
    let alice = Personne { nom: String::from("Alice"), langue: String::from("fr") };
    let r2d2 = Robot { id: 2 };

    alice.saluer();  // "Bonjour, Alice !"
    r2d2.saluer();   // "*sons mécaniques* BEEP BOOP, je suis le robot 2"
}
```

## 2. Traits comme paramètres de fonctions

```rust
// Syntaxe impl Trait (sugar syntax)
fn saluer_quelquun(entite: &impl Saluer) {
    entite.saluer();
}

// Syntaxe Trait Bound (équivalente, plus flexible)
fn saluer_quelquun_v2<T: Saluer>(entite: &T) {
    entite.saluer();
}

// Multiple trait bounds avec +
fn afficher_et_saluer<T: Saluer + std::fmt::Debug>(entite: &T) {
    println!("{:?}", entite);
    entite.saluer();
}

// Where clause pour une syntaxe plus lisible avec plusieurs bounds
fn traiter<T, U>(t: &T, u: &U) -> String
where
    T: Saluer + Clone,
    U: std::fmt::Debug + PartialEq,
{
    t.saluer();
    format!("{:?}", u)
}

// Retourner un trait (impl Trait dans la position de retour)
fn creer_salutation(langue: &str) -> impl Saluer {
    Personne {
        nom: String::from("Monde"),
        langue: String::from(langue),
    }
    // Note : toutes les branches DOIVENT retourner le même type concret
}

fn main() {
    let alice = Personne { nom: String::from("Alice"), langue: String::from("fr") };
    saluer_quelquun(&alice);

    let s = creer_salutation("en");
    s.saluer();
}
```

## 3. Traits communs de la stdlib

### Display et Debug

```rust
use std::fmt;

struct Matrice {
    valeurs: [[f64; 2]; 2],
}

// Display : pour l'affichage utilisateur
impl fmt::Display for Matrice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "| {:.2} {:.2} |\n| {:.2} {:.2} |",
            self.valeurs[0][0], self.valeurs[0][1],
            self.valeurs[1][0], self.valeurs[1][1])
    }
}

// Debug : pour le débogage (dérivable avec #[derive(Debug)])
impl fmt::Debug for Matrice {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Matrice({:?})", self.valeurs)
    }
}

fn main() {
    let m = Matrice { valeurs: [[1.0, 2.0], [3.0, 4.0]] };
    println!("{}", m);    // utilise Display
    println!("{:?}", m);  // utilise Debug
    println!("{:#?}", m); // Debug pretty-print
}
```

### PartialEq, Eq, PartialOrd, Ord

```rust
#[derive(Debug, Clone, PartialEq)]  // PartialEq généré par derive
struct Point {
    x: f64,
    y: f64,
}

// Implémentation manuelle pour un comportement personnalisé
#[derive(Debug)]
struct Etudiant {
    nom: String,
    note: f64,
}

impl PartialEq for Etudiant {
    fn eq(&self, autre: &Self) -> bool {
        self.nom == autre.nom  // égalité basée sur le nom seulement
    }
}

impl PartialOrd for Etudiant {
    fn partial_cmp(&self, autre: &Self) -> Option<std::cmp::Ordering> {
        self.note.partial_cmp(&autre.note)  // comparaison par note
    }
}

fn main() {
    let p1 = Point { x: 1.0, y: 2.0 };
    let p2 = Point { x: 1.0, y: 2.0 };
    let p3 = Point { x: 3.0, y: 4.0 };

    println!("{}", p1 == p2);  // true
    println!("{}", p1 == p3);  // false
    println!("{}", p1 != p3);  // true

    // Tri avec Ord (dérivable si tous les champs sont Ord)
    #[derive(Debug, PartialEq, Eq, PartialOrd, Ord)]
    struct Version(u32, u32, u32);

    let mut versions = vec![
        Version(1, 2, 0),
        Version(2, 0, 0),
        Version(1, 0, 5),
        Version(1, 2, 3),
    ];
    versions.sort();
    println!("{:?}", versions);
    // [Version(1, 0, 5), Version(1, 2, 0), Version(1, 2, 3), Version(2, 0, 0)]
}
```

### Clone et Copy (revu)

```rust
#[derive(Debug, Clone)]
struct Config {
    host: String,
    port: u16,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            host: String::from("localhost"),
            port: 8080,
        }
    }
}

fn main() {
    let config = Config::default();
    let config2 = config.clone();  // clone explicite
    println!("{:?}", config);
    println!("{:?}", config2);

    // Default permet de créer avec des valeurs par défaut
    let config3 = Config {
        port: 9000,
        ..Default::default()  // les autres champs = valeurs par défaut
    };
    println!("{:?}", config3);
}
```

## 4. Génériques avec trait bounds

```rust
use std::fmt::Display;

// Générique avec bounds : T doit implémenter Display et PartialOrd
fn afficher_max<T: Display + PartialOrd>(liste: &[T]) {
    if liste.is_empty() {
        println!("Liste vide");
        return;
    }
    let mut max = &liste[0];
    for item in &liste[1..] {
        if item > max {
            max = item;
        }
    }
    println!("Maximum : {}", max);
}

// Struct générique avec bounds
#[derive(Debug)]
struct MaxTracker<T: PartialOrd + Clone + Display> {
    valeurs: Vec<T>,
}

impl<T: PartialOrd + Clone + Display> MaxTracker<T> {
    fn new() -> Self {
        MaxTracker { valeurs: Vec::new() }
    }

    fn ajouter(&mut self, val: T) {
        self.valeurs.push(val);
    }

    fn maximum(&self) -> Option<&T> {
        self.valeurs.iter().max_by(|a, b| a.partial_cmp(b).unwrap())
    }

    fn afficher_tout(&self) {
        for v in &self.valeurs {
            print!("{} ", v);
        }
        println!();
    }
}

fn main() {
    let nombres = vec![34, 50, 25, 100, 65];
    afficher_max(&nombres);  // 100

    let flottants = vec![1.5, 3.2, 0.8, 4.1];
    afficher_max(&flottants);  // 4.1

    let chaines = vec!["orange", "pomme", "cerise"];
    afficher_max(&chaines);   // "pomme" (alphabétique)

    let mut tracker: MaxTracker<f64> = MaxTracker::new();
    tracker.ajouter(3.14);
    tracker.ajouter(2.71);
    tracker.ajouter(1.41);
    tracker.afficher_tout();
    if let Some(max) = tracker.maximum() {
        println!("Max: {}", max);
    }
}
```

## 5. Trait Objects — Polymorphisme dynamique

```rust
// dyn Trait : dispatch dynamique (vtable)
// Nécessaire quand le type concret n'est pas connu à la compilation

trait Animal {
    fn nom(&self) -> &str;
    fn cri(&self) -> String;
    fn afficher(&self) {
        println!("{} dit : {}", self.nom(), self.cri());
    }
}

struct Chien { nom: String }
struct Chat { nom: String }
struct Vache { nom: String }

impl Animal for Chien {
    fn nom(&self) -> &str  { &self.nom }
    fn cri(&self) -> String { String::from("Woof!") }
}

impl Animal for Chat {
    fn nom(&self) -> &str  { &self.nom }
    fn cri(&self) -> String { String::from("Meow!") }
}

impl Animal for Vache {
    fn nom(&self) -> &str  { &self.nom }
    fn cri(&self) -> String { String::from("Meuh!") }
}

fn main() {
    // Vec de trait objects : hétérogène
    let animaux: Vec<Box<dyn Animal>> = vec![
        Box::new(Chien { nom: String::from("Rex") }),
        Box::new(Chat  { nom: String::from("Mimi") }),
        Box::new(Vache { nom: String::from("Marguerite") }),
    ];

    for animal in &animaux {
        animal.afficher();
    }

    // Fonction prenant un trait object
    fn faire_crier(animal: &dyn Animal) {
        println!("{}", animal.cri());
    }

    faire_crier(&Chien { nom: String::from("Buddy") });

    // impl Trait (statique) vs dyn Trait (dynamique)
    // impl Trait : monomorphisation, code dupliqué, PLUS RAPIDE
    // dyn Trait  : vtable, code unique, PLUS FLEXIBLE
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Créer un `Vec<Box<dyn Animal>>` et itérer dessus. Montrer que `cargo build` génère un seul binaire qui dispatch vers les bonnes méthodes. Comparer avec la version générique `Vec<T: Animal>` qui ne compile pas (taille inconnue). Expliquer avec `cargo build --release` la différence de taille de binaire entre les deux approches.
> **Expliquer :** Expliquer la monomorphisation (impl Trait → code dupliqué mais optimisé) versus le dispatch dynamique (dyn Trait → vtable, un seul code mais indirection). En Rust, on choisit explicitement. Contraster avec Java où le polymorphisme est TOUJOURS dynamique (vtable implicite).
---

## 6. Traits importants à connaître

```rust
// Iterator : fondamental pour les boucles et les streams
// Into / From : conversions
// AsRef / AsMut : références génériques
// Deref / DerefMut : déréférencement
// Add, Sub, Mul... : opérateurs arithmétiques

// --- From / Into ---
#[derive(Debug)]
struct Celsius(f64);
#[derive(Debug)]
struct Fahrenheit(f64);

impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Self {
        Fahrenheit(c.0 * 9.0 / 5.0 + 32.0)
    }
}

// Into est automatiquement dérivé de From
fn main() {
    let c = Celsius(100.0);
    let f: Fahrenheit = c.into();  // utilise From<Celsius> for Fahrenheit
    println!("{:?}", f);  // Fahrenheit(212.0)

    let f2 = Fahrenheit::from(Celsius(0.0));
    println!("{:?}", f2);  // Fahrenheit(32.0)

    // --- Opérateurs avec std::ops ---
    use std::ops::Add;

    #[derive(Debug, Clone, Copy, PartialEq)]
    struct Vecteur2D { x: f64, y: f64 }

    impl Add for Vecteur2D {
        type Output = Vecteur2D;
        fn add(self, autre: Vecteur2D) -> Vecteur2D {
            Vecteur2D { x: self.x + autre.x, y: self.y + autre.y }
        }
    }

    let v1 = Vecteur2D { x: 1.0, y: 2.0 };
    let v2 = Vecteur2D { x: 3.0, y: 4.0 };
    let v3 = v1 + v2;  // utilise impl Add
    println!("{:?}", v3);  // Vecteur2D { x: 4.0, y: 6.0 }
}
```

## Récapitulatif

| Concept | Syntaxe | Équivalent Java |
|---------|---------|-----------------|
| Trait | `trait T { fn f(&self); }` | Interface |
| Implémentation | `impl T for Struct { ... }` | `class C implements T` |
| Trait bound | `<T: Trait>` | `<T extends Interface>` |
| Where clause | `where T: A + B` | Plus lisible que `<T extends A & B>` |
| Trait object | `Box<dyn Trait>`, `&dyn Trait` | Référence vers interface |
| impl Trait | `fn f(x: impl Trait)` | Monomorphisation statique |
| dyn Trait | `fn f(x: &dyn Trait)` | Dispatch dynamique |
| Default | `#[derive(Default)]` | Constructeur sans argument |
| Display | `impl fmt::Display` | `toString()` |
| Debug | `#[derive(Debug)]` | Auto-debug |
