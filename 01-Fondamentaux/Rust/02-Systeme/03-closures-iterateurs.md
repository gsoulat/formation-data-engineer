# Rust — Closures, Fn/FnMut/FnOnce, Iterator Trait, map/filter/collect

## 1. Closures

Une **closure** est une fonction anonyme qui peut capturer des variables de son environnement.

```rust
fn main() {
    // Syntaxe : |paramètres| corps
    let ajouter_un = |x| x + 1;
    println!("{}", ajouter_un(5));  // 6

    // Type annoté explicitement
    let additionner = |x: i32, y: i32| -> i32 { x + y };
    println!("{}", additionner(3, 4));  // 7

    // Corps multi-lignes
    let description = |n: i32| {
        if n < 0      { "négatif".to_string() }
        else if n == 0 { "zéro".to_string() }
        else           { format!("positif ({})", n) }
    };
    println!("{}", description(-5));
    println!("{}", description(0));
    println!("{}", description(10));

    // --- Capture de l'environnement ---
    let base = 10;
    let ajouter_base = |x| x + base;  // capture base par référence
    println!("{}", ajouter_base(5));   // 15
    println!("{}", base);              // OK : base toujours valide

    // Capture par mouvement avec move
    let message = String::from("hello");
    let afficher = move || println!("{}", message);  // move : capture par valeur
    afficher();
    // println!("{}", message);  // ERREUR si pas move, OK sinon

    // --- Closures passées à des fonctions ---
    let nombres = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    // map, filter, etc. prennent des closures
    let pairs_doubles: Vec<i32> = nombres.iter()
        .filter(|&&x| x % 2 == 0)  // && car iter() retourne &&i32
        .map(|&x| x * 2)
        .collect();
    println!("{:?}", pairs_doubles);  // [4, 8, 12, 16, 20]

    // Stocker une closure dans une variable
    let multiplier_par = |facteur: i32| {
        move |x: i32| x * facteur  // retourne une closure
    };
    let doubler  = multiplier_par(2);
    let tripler  = multiplier_par(3);
    println!("{}", doubler(5));   // 10
    println!("{}", tripler(5));   // 15
}
```

## 2. Les traits Fn, FnMut, FnOnce

```rust
// FnOnce  : peut être appelée AU PLUS UNE FOIS (consomme ce qu'elle capture)
// FnMut   : peut être appelée PLUSIEURS FOIS, modifie l'environnement
// Fn      : peut être appelée PLUSIEURS FOIS, ne modifie pas l'environnement
// Fn ⊂ FnMut ⊂ FnOnce

// --- FnOnce : consomme une valeur capturée ---
fn appeler_une_fois<F: FnOnce() -> String>(f: F) -> String {
    f()  // f ne peut être appelée qu'une seule fois
}

fn main() {
    let s = String::from("hello");
    let closure_once = move || s;  // consomme s (FnOnce)
    println!("{}", appeler_une_fois(closure_once));
    // appeler_une_fois(closure_once);  // ERREUR : déjà consommée

    // --- FnMut : modifie l'environnement ---
    let mut compteur = 0;
    let mut incrementer = || { compteur += 1; compteur };  // FnMut
    println!("{}", incrementer());  // 1
    println!("{}", incrementer());  // 2
    println!("{}", incrementer());  // 3

    // --- Fn : lecture seule de l'environnement ---
    let base = 10;
    let ajouter_base = |x| x + base;  // Fn (base capturé par référence)
    println!("{}", ajouter_base(5));   // 15
    println!("{}", ajouter_base(7));   // 17

    // --- Fonctions d'ordre supérieur ---
    fn appliquer<F: Fn(i32) -> i32>(liste: &[i32], f: F) -> Vec<i32> {
        liste.iter().map(|&x| f(x)).collect()
    }

    let nums = vec![1, 2, 3, 4, 5];
    println!("{:?}", appliquer(&nums, |x| x * x));  // [1, 4, 9, 16, 25]
    println!("{:?}", appliquer(&nums, |x| x + 10)); // [11, 12, 13, 14, 15]

    // --- Retourner une closure ---
    fn creer_adder(n: i32) -> impl Fn(i32) -> i32 {
        move |x| x + n  // move : n est capturé dans la closure retournée
    }

    let add5 = creer_adder(5);
    let add10 = creer_adder(10);
    println!("{}", add5(3));   // 8
    println!("{}", add10(3));  // 13

    // Stocker des closures différentes : Box<dyn Fn(...)>
    let operations: Vec<Box<dyn Fn(i32) -> i32>> = vec![
        Box::new(|x| x + 1),
        Box::new(|x| x * 2),
        Box::new(|x| x * x),
    ];

    let valeur = 5;
    for (i, op) in operations.iter().enumerate() {
        println!("Op {}: {}", i, op(valeur));
    }
    // Op 0: 6
    // Op 1: 10
    // Op 2: 25
}
```

## 3. Le trait Iterator

```rust
fn main() {
    // Tout ce qui implémente Iterator peut utiliser map, filter, etc.

    // --- Sources d'itérateurs ---
    let v = vec![1, 2, 3, 4, 5];

    // iter() : itérateur de &T (emprunt immuable)
    for x in v.iter() {
        print!("{} ", x);   // x est &i32
    }

    // iter_mut() : itérateur de &mut T (emprunt mutable)
    let mut v2 = vec![1, 2, 3];
    for x in v2.iter_mut() {
        *x *= 2;  // modifier via déréférence
    }
    println!("{:?}", v2);  // [2, 4, 6]

    // into_iter() : itérateur de T (consomme le Vec)
    let v3 = vec![1, 2, 3];
    let doubled: Vec<i32> = v3.into_iter().map(|x| x * 2).collect();
    // v3 n'est plus accessible

    // Plages
    let _ = (0..10).collect::<Vec<i32>>();
    let _ = (0..=10).collect::<Vec<i32>>();
    let _ = ('a'..='z').collect::<Vec<char>>();

    // Chaînes
    let s = "hello world";
    let mots: Vec<&str> = s.split_whitespace().collect();
    let chars: Vec<char> = s.chars().collect();
    let bytes: Vec<u8> = s.bytes().collect();

    // --- Opérations intermédiaires (lazy) ---
    let v = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    // map : transformer
    let carres: Vec<i32> = v.iter().map(|&x| x * x).collect();
    println!("{:?}", carres);

    // filter : filtrer
    let pairs: Vec<&i32> = v.iter().filter(|&&x| x % 2 == 0).collect();
    println!("{:?}", pairs);

    // filter_map : filter + map combinés
    let valides: Vec<i32> = vec!["1", "deux", "3", "quatre", "5"]
        .iter()
        .filter_map(|s| s.parse::<i32>().ok())
        .collect();
    println!("{:?}", valides);  // [1, 3, 5]

    // flat_map : aplatir des itérables imbriqués
    let phrases = vec!["bonjour monde", "rust est cool"];
    let mots: Vec<&str> = phrases.iter()
        .flat_map(|s| s.split_whitespace())
        .collect();
    println!("{:?}", mots);  // ["bonjour", "monde", "rust", "est", "cool"]

    // flatten : aplatir un itérable d'itérables
    let nested = vec![vec![1, 2], vec![3, 4], vec![5]];
    let flat: Vec<i32> = nested.into_iter().flatten().collect();
    println!("{:?}", flat);  // [1, 2, 3, 4, 5]

    // take / skip
    let premiers_5: Vec<i32> = (1..=100).take(5).collect();
    let apres_5: Vec<i32> = (1..=10).skip(5).collect();
    println!("{:?}", premiers_5);  // [1, 2, 3, 4, 5]
    println!("{:?}", apres_5);     // [6, 7, 8, 9, 10]

    // take_while / skip_while
    let jusqua_5: Vec<i32> = (1..=10).take_while(|&x| x < 5).collect();
    let apres_5: Vec<i32>  = (1..=10).skip_while(|&x| x < 5).collect();

    // zip : combiner deux itérateurs
    let noms = vec!["Alice", "Bob", "Charlie"];
    let ages = vec![30, 25, 35];
    let couples: Vec<(&str, i32)> = noms.iter().copied().zip(ages.iter().copied()).collect();
    println!("{:?}", couples);  // [("Alice", 30), ("Bob", 25), ("Charlie", 35)]

    // enumerate : ajouter un index
    for (i, nom) in noms.iter().enumerate() {
        println!("{}: {}", i, nom);
    }

    // chain : concatener des itérateurs
    let a = vec![1, 2, 3];
    let b = vec![4, 5, 6];
    let concat: Vec<i32> = a.iter().chain(b.iter()).copied().collect();
    println!("{:?}", concat);  // [1, 2, 3, 4, 5, 6]

    // distinct (pas dans la stdlib — utiliser BTreeSet ou HashSet)
    use std::collections::HashSet;
    let avec_doublons = vec![1, 2, 2, 3, 3, 3, 4];
    let unique: HashSet<i32> = avec_doublons.into_iter().collect();

    // windows / chunks (sur slices)
    let data = vec![1, 2, 3, 4, 5];
    for window in data.windows(3) {
        print!("{:?} ", window);  // [1,2,3] [2,3,4] [3,4,5]
    }
    println!();
    for chunk in data.chunks(2) {
        print!("{:?} ", chunk);   // [1,2] [3,4] [5]
    }
    println!();
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans VS Code que les opérations intermédiaires sont **lazy** : écrire `let iter = vec![1,2,3].iter().map(|x| { println!("map!"); x * 2 });` et montrer que "map!" n'est pas affiché. Ajouter `.collect::<Vec<_>>()` et montrer que seulement alors "map!" s'affiche.
> **Expliquer :** Les itérateurs Rust sont "zero-cost abstractions" : pas d'allocation intermédiaire, les opérations sont fusionnées à la compilation. Comparer avec Java Streams (similaires) et Python generators. Montrer `cargo build --release` et que le compilateur élimine les itérateurs inutiles.
---

## 4. Opérations terminales

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    // collect : materialiser en collection
    let liste: Vec<i32>       = v.iter().copied().collect();
    let ensemble: std::collections::HashSet<i32> = v.iter().copied().collect();
    let map: std::collections::HashMap<i32, i32> = v.iter().map(|&x| (x, x*x)).collect();

    // sum / product
    let somme: i32    = v.iter().sum();         // 55
    let produit: i32  = v.iter().copied().product();  // 3628800

    // count
    let nb_pairs = v.iter().filter(|&&x| x % 2 == 0).count();
    println!("Pairs : {}", nb_pairs);  // 5

    // any / all
    println!("{}", v.iter().any(|&x| x > 9));    // true
    println!("{}", v.iter().all(|&x| x > 0));    // true
    println!("{}", v.iter().all(|&x| x > 5));    // false

    // find / position
    let premier_pair: Option<&i32> = v.iter().find(|&&x| x % 2 == 0);  // Some(&2)
    let pos: Option<usize> = v.iter().position(|&x| x == 5);            // Some(4)
    println!("{:?} {:?}", premier_pair, pos);

    // min / max
    let min: Option<&i32> = v.iter().min();  // Some(&1)
    let max: Option<&i32> = v.iter().max();  // Some(&10)

    // min_by / max_by avec critère personnalisé
    let mots = vec!["pomme", "banane", "cerise", "kiwi"];
    let plus_court = mots.iter().min_by_key(|s| s.len());  // Some(&"kiwi")
    let plus_long  = mots.iter().max_by_key(|s| s.len());  // Some(&"banane")

    // reduce : agréger
    let concat = mots.iter().copied().reduce(|a, b| {
        // ne peut pas retourner de String ici (borrow issues)
        // utiliser fold à la place pour les String
        if a.len() > b.len() { a } else { b }
    });
    println!("{:?}", concat);  // Some("banane")

    // fold : réduction avec accumulateur
    let somme_fold = v.iter().fold(0, |acc, &x| acc + x);
    println!("{}", somme_fold);  // 55

    let histogramme = vec![1, 2, 2, 3, 3, 3, 4, 4, 4, 4];
    let freq = histogramme.iter().fold(
        std::collections::HashMap::new(),
        |mut map, &x| { *map.entry(x).or_insert(0) += 1; map }
    );
    println!("{:?}", freq);  // {1: 1, 2: 2, 3: 3, 4: 4}

    // for_each (effet de bord)
    v.iter().for_each(|&x| print!("{} ", x));
    println!();

    // unzip
    let couples = vec![(1, 'a'), (2, 'b'), (3, 'c')];
    let (nombres, lettres): (Vec<i32>, Vec<char>) = couples.into_iter().unzip();
    println!("{:?} {:?}", nombres, lettres);
}
```

## 5. Implémenter Iterator pour ses propres types

```rust
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Self {
        Fibonacci { a: 0, b: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let suivant = self.a + self.b;
        self.a = self.b;
        self.b = suivant;
        Some(self.a)  // infini : retourne toujours Some
    }
}

struct Compte {
    debut: i32,
    fin: i32,
    actuel: i32,
}

impl Compte {
    fn new(debut: i32, fin: i32) -> Self {
        Compte { debut, fin, actuel: debut }
    }
}

impl Iterator for Compte {
    type Item = i32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.actuel <= self.fin {
            let val = self.actuel;
            self.actuel += 1;
            Some(val)
        } else {
            None  // fin de l'itération
        }
    }
}

fn main() {
    // Fibonacci : les 10 premiers
    let fib: Vec<u64> = Fibonacci::new().take(10).collect();
    println!("{:?}", fib);  // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

    // Utiliser TOUTES les méthodes d'Iterator gratuitement !
    let fib_pairs: Vec<u64> = Fibonacci::new()
        .filter(|&x| x % 2 == 0)
        .take(5)
        .collect();
    println!("{:?}", fib_pairs);  // [2, 8, 34, 144, 610]

    // Compte
    let compte: Vec<i32> = Compte::new(1, 5).collect();
    println!("{:?}", compte);  // [1, 2, 3, 4, 5]

    // zip avec lui-même décalé
    let zip_compte: Vec<(i32, i32)> = Compte::new(1, 5)
        .zip(Compte::new(2, 6))
        .collect();
    println!("{:?}", zip_compte);  // [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]

    let somme: i32 = Compte::new(1, 100).sum();
    println!("Somme 1..100 = {}", somme);  // 5050
}
```

## Récapitulatif

| Concept | Description | Exemple |
|---------|-------------|---------|
| Closure | Fonction anonyme | `\|x\| x + 1` |
| `Fn` | Lit l'environnement | `\|x\| x + base` |
| `FnMut` | Modifie l'environnement | `\|\| compteur += 1` |
| `FnOnce` | Consomme l'environnement | `move \|\| valeur` |
| `move` | Capture par valeur | `move \|\| println!("{}", s)` |
| `iter()` | Emprunte (&T) | Lecture seule |
| `iter_mut()` | Emprunte (&mut T) | Modification en place |
| `into_iter()` | Consomme | Transféré |
| `map` | Transformer | `\|x\| x * 2` |
| `filter` | Filtrer | `\|&x\| x > 0` |
| `filter_map` | Filtrer + transformer | `\|s\| s.parse().ok()` |
| `flat_map` | Aplatir | `\|v\| v.iter()` |
| `collect` | Matérialiser | `→ Vec<T>`, `HashMap`, ... |
| `fold` | Réduire avec état | `fold(0, \|acc, x\| acc + x)` |
| `impl Iterator` | Itérateur custom | `fn next(&mut self) → Option<T>` |
