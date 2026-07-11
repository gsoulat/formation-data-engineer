# Rust — Introduction : Why Rust, Cargo, Variables, Types

## 1. Pourquoi Rust ?

Rust résout le problème fondamental de la programmation système : **sécurité mémoire sans garbage collector**.

```
Langages de bas niveau (C, C++) :
→ Rapides, contrôle total
→ Bugs mémoire dangereux (use-after-free, buffer overflow, data races)

Langages avec GC (Java, Python, Go) :
→ Sécurité mémoire garantie
→ Pause GC, overhead mémoire, moins de contrôle

Rust :
→ Rapide comme C
→ Sûr comme Java
→ Pas de GC — le compilateur vérifie la sécurité
```

### Cas d'usage de Rust

- **Systèmes d'exploitation** : Linux (pilotes), Windows (composants)
- **WebAssembly** : performances natives dans le navigateur
- **CLI tools** : `ripgrep`, `fd`, `bat`, `exa`
- **Web backends** : APIs haute performance (Axum, Actix-web)
- **Blockchain** : Solana, Polkadot
- **Embedded** : microcontrôleurs (ARM Cortex-M)

## 2. Cargo — Le gestionnaire de projet

Cargo fait tout : créer un projet, compiler, tester, gérer les dépendances.

```bash
# Créer un nouveau projet binaire
cargo new hello-rust
cd hello-rust

# Structure créée :
# hello-rust/
# ├── Cargo.toml    ← manifest (dépendances, metadata)
# └── src/
#     └── main.rs   ← point d'entrée

# Compiler et exécuter
cargo run

# Compiler seulement
cargo build

# Compiler en mode release (optimisé)
cargo build --release

# Lancer les tests
cargo test

# Vérifier sans compiler (plus rapide)
cargo check

# Formater le code
cargo fmt

# Linter (détecte les problèmes courants)
cargo clippy

# Générer la documentation
cargo doc --open

# Créer une bibliothèque
cargo new ma-lib --lib
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans le terminal, exécuter `cargo new hello-rust && cd hello-rust && cargo run`. Montrer la sortie du compilateur, puis la sortie du programme ("Hello, world!"). Montrer aussi `cargo check` pour la vérification rapide.
> **Expliquer :** Expliquer la différence entre `cargo build` (debug, informations de débogage incluses, moins optimisé) et `cargo build --release` (optimisé, sans symboles de débogage). Montrer la taille des binaires produits dans `target/debug/` vs `target/release/`.
---

### Cargo.toml

```toml
[package]
name = "hello-rust"
version = "0.1.0"
edition = "2021"   # Edition Rust (2015, 2018, 2021)

[dependencies]
# Ajouter des crates depuis crates.io
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
rand = "0.8"

[dev-dependencies]
# Seulement pour les tests
pretty_assertions = "1.0"

[profile.release]
opt-level = 3     # Niveau d'optimisation (0-3)
lto = true        # Link-Time Optimization
```

```bash
# Ajouter une dépendance automatiquement
cargo add serde --features derive
cargo add tokio --features full
```

## 3. Premier programme Rust

```rust
// src/main.rs
fn main() {
    // println! est une macro (le ! indique que c'est une macro, pas une fonction)
    println!("Hello, world!");

    // Formatage similaire à Python's f-strings mais avec {}
    let nom = "Alice";
    let age = 30;
    println!("Je m'appelle {} et j'ai {} ans.", nom, age);

    // Debug avec {:?} ou pretty-print avec {:#?}
    let tableau = [1, 2, 3, 4, 5];
    println!("{:?}", tableau);    // [1, 2, 3, 4, 5]
    println!("{:#?}", tableau);   // formatage multi-lignes

    // eprintln! pour stderr
    eprintln!("Ceci va sur stderr");

    // Expressions (tout retourne une valeur en Rust)
    let x = {
        let a = 3;
        let b = 4;
        a + b   // pas de point-virgule = valeur retournée du bloc
    };
    println!("x = {}", x);  // 7
}
```

## 4. Variables et mutabilité

```rust
fn main() {
    // --- Variables immuables par défaut ---
    let x = 5;
    // x = 6;  // ERREUR : "cannot assign twice to immutable variable"

    // --- Variables mutables : mut ---
    let mut y = 5;
    println!("y = {}", y);
    y = 6;
    println!("y = {}", y);

    // --- Shadowing : redéclarer avec let ---
    let z = 5;
    let z = z + 1;       // nouveau z shadowing l'ancien
    let z = z * 2;       // encore un nouveau z
    println!("z = {}", z);  // 12

    // Shadowing permet de changer le type
    let espaces = "   ";      // &str
    let espaces = espaces.len();  // usize (shadowing avec type différent)
    println!("espaces = {}", espaces);  // 3

    // --- Constantes ---
    // Toujours immuables, type obligatoire, calculées à la compilation
    const MAX_POINTS: u32 = 100_000;
    const PI: f64 = 3.14159265358979;
    println!("Max: {}, Pi: {}", MAX_POINTS, PI);

    // --- Types inférés ---
    let entier = 42;        // i32 (défaut pour les entiers)
    let flottant = 3.14;    // f64 (défaut pour les flottants)
    let booleen = true;     // bool
    let caractere = 'A';    // char (Unicode scalaire, 4 octets)

    // Types explicites
    let x: i32 = 42;
    let y: f64 = 3.14;
    let b: bool = false;
}
```

## 5. Types de données

### Types scalaires

```rust
fn main() {
    // --- Entiers ---
    // Signés : i8, i16, i32, i64, i128, isize
    // Non-signés : u8, u16, u32, u64, u128, usize
    let a: i8   = -128;          // -128 à 127
    let b: u8   = 255;           // 0 à 255
    let c: i32  = 2_147_483_647; // underscore pour la lisibilité
    let d: u64  = 18_446_744_073_709_551_615;
    let e: i64  = -9_223_372_036_854_775_808;
    let idx: usize = 42;  // taille d'un pointeur (32 ou 64 bits selon la plateforme)

    // Littéraux entiers
    let decimal     = 98_222;
    let hexa        = 0xff;       // 255
    let octal       = 0o77;       // 63
    let binaire     = 0b1111_0000;  // 240
    let octet: u8   = b'A';       // 65 (valeur ASCII)

    // --- Flottants ---
    let x: f32 = 3.14;    // 32 bits, moins précis
    let y: f64 = 3.141592653589793;  // 64 bits, défaut

    // Opérations
    println!("{}", 5 / 2);    // 2   (division entière !)
    println!("{}", 5 % 2);    // 1   (modulo)
    println!("{:.2}", 5.0_f64 / 2.0);  // 2.50 (division flottante)

    // Overflow en mode debug → panic
    // En mode release → comportement wrapping
    // Utiliser : wrapping_add, saturating_add, checked_add, overflowing_add

    // --- Booléens ---
    let t: bool = true;
    let f: bool = false;
    println!("{}", t && f);  // false
    println!("{}", t || f);  // true
    println!("{}", !t);      // false

    // --- Caractères ---
    let c1: char = 'A';
    let c2: char = '€';    // Unicode
    let c3: char = '🦀';   // Emoji (crabe Rust)
    println!("{} {} {}", c1, c2, c3);
    println!("char taille: {} octets", std::mem::size_of::<char>());  // 4
}
```

### Types composés

```rust
fn main() {
    // --- Tuple : types hétérogènes, taille fixe ---
    let tup: (i32, f64, bool) = (500, 6.4, true);

    // Déstructuration
    let (x, y, z) = tup;
    println!("{} {} {}", x, y, z);

    // Accès par index
    println!("{}", tup.0);  // 500
    println!("{}", tup.1);  // 6.4

    // Tuple unitaire : "()" = le type "unit" (équivalent de void)
    let _unit: () = ();

    // Tuple nommé (via struct)
    struct Point(f64, f64);
    let p = Point(1.0, 2.0);
    println!("{} {}", p.0, p.1);

    // --- Array : même type, taille fixe connue à la compilation ---
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    let arr2 = [3; 5];  // [3, 3, 3, 3, 3]

    println!("{}", arr[0]);      // 1
    println!("{}", arr.len());   // 5

    // Array est sur la pile (stack), contrairement à Vec sur le tas (heap)
    let matrice: [[i32; 3]; 3] = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ];

    // Slice : référence à une partie d'un array
    let slice: &[i32] = &arr[1..4];  // [2, 3, 4]
    println!("{:?}", slice);
}
```

## 6. Fonctions

```rust
// Fonctions définies avec fn
// Type de retour avec ->
// La dernière expression sans ; est la valeur retournée

fn addition(a: i32, b: i32) -> i32 {
    a + b  // pas de point-virgule = retour implicite
}

// Équivalent (return explicite)
fn addition_v2(a: i32, b: i32) -> i32 {
    return a + b;  // return explicite
}

// Void : ne pas spécifier -> ou utiliser -> ()
fn afficher(message: &str) {
    println!("{}", message);
}

// Retourner plusieurs valeurs via un tuple
fn min_max(valeurs: &[i32]) -> (i32, i32) {
    let mut min = valeurs[0];
    let mut max = valeurs[0];
    for &v in valeurs {
        if v < min { min = v; }
        if v > max { max = v; }
    }
    (min, max)
}

// Fonctions imbriquées (inner functions)
fn externe() -> i32 {
    fn interne(x: i32) -> i32 {
        x * 2
    }
    interne(5)
}

fn main() {
    println!("{}", addition(3, 4));    // 7
    afficher("Bonjour Rust");

    let tab = [5, 2, 8, 1, 9, 3];
    let (min, max) = min_max(&tab);
    println!("Min: {}, Max: {}", min, max);

    println!("{}", externe());  // 10
}
```

## 7. Contrôle de flux

```rust
fn main() {
    // --- if / else if / else ---
    let nombre = 7;

    if nombre < 0 {
        println!("Négatif");
    } else if nombre == 0 {
        println!("Zéro");
    } else {
        println!("Positif");
    }

    // if est une expression (retourne une valeur)
    let description = if nombre > 0 { "positif" } else { "non positif" };
    println!("{}", description);

    // --- loop : boucle infinie ---
    let mut compteur = 0;
    let resultat = loop {
        compteur += 1;
        if compteur == 10 {
            break compteur * 2;  // loop peut retourner une valeur
        }
    };
    println!("Résultat: {}", resultat);  // 20

    // --- while ---
    let mut n = 3;
    while n != 0 {
        println!("{}!", n);
        n -= 1;
    }

    // --- for : le plus idiomatique ---
    // Itérer sur une plage
    for i in 0..5 {   // 0, 1, 2, 3, 4 (5 exclu)
        print!("{} ", i);
    }
    println!();

    for i in 0..=5 {  // 0, 1, 2, 3, 4, 5 (5 inclus)
        print!("{} ", i);
    }
    println!();

    // Itérer sur une collection
    let animaux = ["chat", "chien", "lapin"];
    for animal in &animaux {  // & pour ne pas déplacer
        println!("{}", animal);
    }

    // Avec index : enumerate()
    for (i, animal) in animaux.iter().enumerate() {
        println!("{}: {}", i, animal);
    }

    // Itération en sens inverse
    for i in (0..5).rev() {
        print!("{} ", i);  // 4 3 2 1 0
    }

    // --- Labels pour break/continue imbriqués ---
    'externe: for i in 0..5 {
        for j in 0..5 {
            if i == 2 && j == 2 {
                break 'externe;  // sort de la boucle externe
            }
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans VS Code avec rust-analyzer l'inférence de types : survoler une variable `let x = 42` pour voir le type inféré `i32` dans le tooltip. Montrer aussi les erreurs de type affichées en temps réel par rust-analyzer avant même de compiler.
> **Expliquer :** Expliquer le système de types stricts de Rust et l'inférence de types. Contraster avec la déclaration implicite de variables en Python. Insister sur le fait que l'immuabilité par défaut est une protection contre les bugs (variable modifiée par accident).
---

## 8. Commentaires et documentation

```rust
/// Documentation externe (apparaît dans `cargo doc`)
/// Supporte le Markdown.
///
/// # Arguments
///
/// * `nom` - Le nom à saluer
///
/// # Exemples
///
/// ```
/// let message = saluer("Alice");
/// assert_eq!(message, "Bonjour, Alice !");
/// ```
pub fn saluer(nom: &str) -> String {
    format!("Bonjour, {} !", nom)
}

//! Documentation de module (en tête du fichier ou du module)
//! Ce module contient les fonctions utilitaires.

fn main() {
    // Commentaire inline (une ligne)

    /* Commentaire
       multi-lignes */

    // Les doctests dans /// sont exécutés avec `cargo test` !
    println!("{}", saluer("Bob"));  // "Bonjour, Bob !"
}
```

## Récapitulatif

| Concept | Rust | Java/Python |
|---------|------|-------------|
| Variables | `let x = 5` | Immuable par défaut |
| Mutabilité | `let mut x = 5` | Explicite avec `mut` |
| Constante | `const MAX: u32 = 100` | Type obligatoire |
| Shadowing | `let x = x + 1` | Redéclare, change le type possible |
| Entier défaut | `i32` | 32 bits signé |
| Flottant défaut | `f64` | 64 bits |
| Division entière | `5 / 2 = 2` | Comme Java |
| Retour de fonction | Dernière expr sans `;` | Implicite |
| Build | `cargo build` | `javac` |
| Run | `cargo run` | `java` |
