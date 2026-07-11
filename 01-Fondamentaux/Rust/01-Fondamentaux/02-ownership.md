# Rust — Ownership : Règles, Move Semantics, Copy Trait

## 1. Pourquoi l'Ownership existe

En C/C++, la gestion manuelle de la mémoire cause des bugs catastrophiques :

```c
// C : use-after-free (undefined behavior)
char* ptr = malloc(10);
free(ptr);
*ptr = 'x';  // DANGER : mémoire libérée mais encore utilisée

// Double free
free(ptr);
free(ptr);  // DANGER : comportement indéfini

// Memory leak
char* data = malloc(1000);
// Oubli de free(data) → fuite mémoire
```

Rust résout ces problèmes **au moment de la compilation** grâce à l'ownership.

## 2. Les trois règles de l'Ownership

```
Règle 1 : Chaque valeur a exactement UN propriétaire (owner)
Règle 2 : Il ne peut y avoir qu'un seul owner à la fois
Règle 3 : Quand l'owner sort de portée, la valeur est libérée (drop)
```

```rust
fn main() {
    // s1 est le propriétaire de la String "hello"
    let s1 = String::from("hello");

    // s1 est DÉPLACÉ (move) dans s2 — s1 n'est plus valide
    let s2 = s1;

    // println!("{}", s1);  // ERREUR de compilation !
    // error[E0382]: borrow of moved value: `s1`

    println!("{}", s2);  // OK : s2 est le propriétaire

} // s2 sort de portée → String libérée (drop)
  // La mémoire est libérée exactement une fois
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Écrire dans VS Code :
> ```rust
> let s1 = String::from("hello");
> let s2 = s1;
> println!("{}", s1); // Cette ligne doit montrer une erreur
> ```
> Montrer l'erreur rouge en temps réel de rust-analyzer AVANT même de compiler : "value borrowed here after move". Puis lancer `cargo build` pour voir le même message du compilateur.
> **Expliquer :** C'est LA particularité de Rust. Contraster avec Java où `String s2 = s1` ne fait que copier la référence (les deux pointent vers le même objet). En Rust, après le move, s1 est invalidé. Il ne peut pas y avoir de double free.
---

## 3. Stack vs Heap — Comprendre la mémoire

```rust
fn main() {
    // --- STACK (pile) : taille connue à la compilation, rapide ---
    let x = 5;      // i32 : 4 octets sur la pile
    let y = true;   // bool : 1 octet sur la pile
    let arr = [1, 2, 3];  // [i32; 3] : 12 octets sur la pile

    // --- HEAP (tas) : taille dynamique, allocation explicite ---
    // String::from alloue sur le tas
    let s = String::from("hello");
    // s contient sur la pile : { ptr: 0x..., len: 5, capacity: 5 }
    //                  sur le tas : ['h', 'e', 'l', 'l', 'o']

    // Quand s sort de portée → Rust appelle drop() → libère le tas
}
```

```
Stack                    Heap
┌───────────────┐        ┌───────────────┐
│ s:            │        │               │
│   ptr ────────┼──────► │ h e l l o     │
│   len: 5      │        │               │
│   cap: 5      │        └───────────────┘
└───────────────┘
```

## 4. Move Semantics

```rust
fn main() {
    // --- Types heap : MOVE par défaut ---
    let s1 = String::from("hello");
    let s2 = s1;  // MOVE : s1 est invalidé

    // --- Fonction avec move ---
    let s3 = String::from("world");
    prendre_propriete(s3);  // s3 est déplacé dans la fonction
    // println!("{}", s3);  // ERREUR : s3 a été déplacé

    // --- Récupérer la propriété ---
    let s4 = String::from("retour");
    let s5 = donner_et_reprendre(s4);  // s4 déplacé, s5 est le nouveau propriétaire
    println!("{}", s5);  // OK

    // C'est verbeux → c'est pourquoi le borrowing existe (chapitre suivant)
}

fn prendre_propriete(texte: String) {
    println!("{}", texte);
}  // texte sort de portée → String libérée

fn donner_et_reprendre(texte: String) -> String {
    texte  // retourner = transférer la propriété à l'appelant
}
```

## 5. Le trait Copy

Les types **Copy** sont copiés sur la pile au lieu d'être déplacés. Après un Copy, les deux variables sont valides.

```rust
fn main() {
    // --- Types Copy : petits, sur la pile ---
    let x = 5;
    let y = x;  // COPIE (pas move) car i32 implémente Copy
    println!("{} {}", x, y);  // Les deux valides !

    let b = true;
    let c = b;  // Copie
    println!("{} {}", b, c);  // Les deux valides

    let t = (1, 2.0);  // Tuple de types Copy
    let u = t;         // Copie car tous les éléments sont Copy
    println!("{:?} {:?}", t, u);

    // --- Types NON-Copy : alloqués sur le tas ---
    let s = String::from("hello");
    let t = s;  // MOVE (pas copie)
    // println!("{}", s);  // ERREUR !

    let v: Vec<i32> = vec![1, 2, 3];
    let w = v;  // MOVE
    // println!("{:?}", v);  // ERREUR !

    // Pour copier un type non-Copy : utiliser .clone()
    let s1 = String::from("hello");
    let s2 = s1.clone();  // Copie PROFONDE (coûteuse)
    println!("{} {}", s1, s2);  // Les deux valides !

    let v1 = vec![1, 2, 3];
    let v2 = v1.clone();  // Copie profonde du Vec et son contenu
    println!("{:?} {:?}", v1, v2);
}

// Types qui implémentent Copy (par défaut) :
// i8, i16, i32, i64, i128, isize
// u8, u16, u32, u64, u128, usize
// f32, f64
// bool
// char
// Tuples uniquement si tous les éléments sont Copy : (i32, bool) ✓

// Types qui n'implémentent PAS Copy :
// String, Vec<T>, HashMap, Box<T>...
// (tout ce qui alloque sur le tas)
```

## 6. Implémenter Copy pour ses propres types

```rust
// Un struct peut dériver Copy si TOUS ses champs sont Copy
#[derive(Debug, Clone, Copy)]  // Copy implique Clone
struct Point {
    x: f64,
    y: f64,
}

#[derive(Debug, Clone, Copy)]
struct Couleur(u8, u8, u8);

// Un struct avec une String ne peut PAS être Copy
#[derive(Debug, Clone)]  // Clone seulement, pas Copy
struct Personne {
    nom: String,
    age: u32,
}

fn main() {
    let p1 = Point { x: 1.0, y: 2.0 };
    let p2 = p1;  // COPIE car Point implémente Copy
    println!("{:?} {:?}", p1, p2);  // Les deux valides !

    let alice = Personne { nom: String::from("Alice"), age: 30 };
    let bob = alice;  // MOVE
    // println!("{:?}", alice);  // ERREUR : alice déplacé

    let alice2 = Personne { nom: String::from("Alice"), age: 30 };
    let alice3 = alice2.clone();  // Clone : copie profonde
    println!("{:?} {:?}", alice2, alice3);  // Les deux valides
}
```

## 7. Ownership et fonctions

```rust
fn main() {
    // --- Passer par valeur : move ---
    let v = vec![1, 2, 3, 4, 5];
    let somme = calculer_somme(v);  // v est déplacé
    // println!("{:?}", v);  // ERREUR : v a été déplacé
    println!("Somme: {}", somme);

    // --- Retourner la propriété (verbeux) ---
    let v2 = vec![1, 2, 3, 4, 5];
    let (v3, somme2) = calculer_somme_et_retourner(v2);
    println!("{:?} {}", v3, somme2);

    // La vraie solution : borrowing avec & (chapitre suivant)
}

fn calculer_somme(nombres: Vec<i32>) -> i32 {
    nombres.iter().sum()
}  // nombres est droppé ici (libéré)

fn calculer_somme_et_retourner(nombres: Vec<i32>) -> (Vec<i32>, i32) {
    let somme: i32 = nombres.iter().sum();
    (nombres, somme)  // retourner la propriété au lieu de la libérer
}
```

## 8. Drop et la libération de ressources

```rust
// Le trait Drop est appelé automatiquement quand une valeur sort de portée
// C'est l'équivalent du destructeur en C++

struct MaRessource {
    nom: String,
}

impl Drop for MaRessource {
    fn drop(&mut self) {
        println!("Libération de : {}", self.nom);
    }
}

fn main() {
    let r1 = MaRessource { nom: String::from("Connexion DB") };
    let r2 = MaRessource { nom: String::from("Fichier") };

    {
        let r3 = MaRessource { nom: String::from("Temporaire") };
        println!("Dans le bloc interne");
    }
    // → "Libération de : Temporaire" (r3 sort de portée)

    println!("Fin de main");
    // → "Libération de : Fichier"    (r2, ordre inversé)
    // → "Libération de : Connexion DB"  (r1)

    // drop() manuel (force la libération avant la fin de portée)
    let r4 = MaRessource { nom: String::from("Manuelle") };
    drop(r4);  // Libéré ici
    // println!("{}", r4.nom);  // ERREUR : r4 a été droppé
    println!("r4 a déjà été libéré");
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le programme avec `MaRessource` et `impl Drop`. Montrer dans la console l'ordre des messages de libération (inversé par rapport à la création). Insister sur le fait que c'est DÉTERMINISTE en Rust (contrairement à Java où le GC peut appeler finalize() n'importe quand ou jamais).
> **Expliquer :** Expliquer le concept RAII (Resource Acquisition Is Initialization) : la ressource est libérée automatiquement et déterministiquement à la fin de la portée. C'est ce qui permet à Rust de gérer les connexions DB, les fichiers, les mutex, etc. sans fuite mémoire.
---

## 9. Exemple pratique : pourquoi l'ownership prévient les bugs

```rust
// Démonstration : l'ownership rend certains bugs impossibles

fn main() {
    // --- Impossible : double free ---
    let s = String::from("hello");
    let t = s;  // s est déplacé
    // drop(s);  // ERREUR de compilation → impossible de drop deux fois

    // --- Impossible : use after free ---
    let s2 = String::from("monde");
    drop(s2);
    // println!("{}", s2);  // ERREUR de compilation → impossible d'utiliser après drop

    // --- Impossible : data race ---
    // (avec les règles de borrowing, voir chapitre suivant)

    // --- Impossible : null pointer dereference ---
    // Il n'y a PAS de null en Rust !
    // Utiliser Option<T> à la place (voir chapitre Gestion d'erreurs)
    let x: Option<i32> = None;    // absence de valeur
    let y: Option<i32> = Some(42); // valeur présente

    if let Some(valeur) = y {
        println!("Valeur: {}", valeur);
    }

    // match pour forcer la gestion de None
    match x {
        Some(v) => println!("{}", v),
        None    => println!("Pas de valeur"),
    }
}
```

## Récapitulatif

| Concept | Règle | Résultat |
|---------|-------|----------|
| Ownership | 1 propriétaire par valeur | Libération déterministe (pas de GC) |
| Move | Affecter déplace la propriété | L'original n'est plus utilisable |
| Copy | Types simples sur la pile | Les deux copies sont valides |
| Clone | `.clone()` sur types heap | Copie profonde explicite |
| Drop | Fin de portée = libération | Pas de fuite mémoire possible |

### Types Copy vs Move

| Type | Comportement | Exemple |
|------|-------------|---------|
| `i32`, `f64`, `bool`, `char` | Copy | `let y = x;` → deux valides |
| `String` | Move | `let t = s;` → s invalide |
| `Vec<T>` | Move | `let w = v;` → v invalide |
| `Box<T>` | Move | Pointeur intelligent (heap) |
| `&T` (référence) | Copy | Voir chapitre Borrowing |
