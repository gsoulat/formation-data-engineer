# Exercice Rust 1 — Ownership et Borrowing : Défis

## Objectif

Comprendre en profondeur l'ownership, le borrowing et les lifetimes à travers des problèmes progressifs. Chaque exercice commence par un code invalide que vous devez corriger.

## Durée estimée : 2 à 3 heures

---

## Partie 1 — Corriger les erreurs d'ownership (30 min)

### 1.1 Move après utilisation

Corrigez ce code pour qu'il compile et affiche les deux valeurs :

```rust
fn afficher(s: String) {
    println!("{}", s);
}

fn main() {
    let message = String::from("bonjour");
    afficher(message);
    println!("{}", message);  // ERREUR : message a été déplacé
}
```

**Indice** : Deux approches possibles — modifier le type du paramètre, ou cloner.

### 1.2 Modification à travers une référence

```rust
fn ajouter_exclamation(s: &String) {
    s.push_str("!");  // ERREUR
}

fn main() {
    let mut msg = String::from("Hello");
    ajouter_exclamation(&msg);
    println!("{}", msg);
}
```

### 1.3 Référence invalide (dangling)

```rust
fn creer_string() -> &str {  // ERREUR
    let s = String::from("hello");
    &s
}

fn main() {
    let s = creer_string();
    println!("{}", s);
}
```

### 1.4 Double mutable borrow

```rust
fn main() {
    let mut v = vec![1, 2, 3];
    let premier = &v[0];
    v.push(4);           // ERREUR
    println!("{}", premier);
}
```

---

## Partie 2 — Structures avec ownership (45 min)

### 2.1 Bibliothèque

Implémentez ces structs sans erreurs de compilation :

```rust
struct Bibliotheque {
    livres: Vec<String>,
}

impl Bibliotheque {
    fn new() -> Self { todo!() }

    // Ajouter un livre (prend possession du nom)
    fn ajouter(&mut self, titre: String) { todo!() }

    // Retourner une référence vers le premier livre
    fn premier(&self) -> Option<&String> { todo!() }

    // Retourner une LISTE de références vers tous les livres contenant un mot clé
    fn rechercher<'a>(&'a self, motcle: &str) -> Vec<&'a String> { todo!() }

    // Retirer et retourner le dernier livre (ownership transféré)
    fn retirer_dernier(&mut self) -> Option<String> { todo!() }

    // Nombre de livres
    fn nombre(&self) -> usize { todo!() }
}

fn main() {
    let mut lib = Bibliotheque::new();
    lib.ajouter("Le Seigneur des Anneaux".into());
    lib.ajouter("Harry Potter".into());
    lib.ajouter("Les Misérables".into());

    println!("Premier: {:?}", lib.premier());

    let resultats = lib.rechercher("Le");
    for r in &resultats {
        println!("Trouvé: {}", r);
    }

    let retire = lib.retirer_dernier();
    println!("Retiré: {:?}", retire);
    println!("Nombre: {}", lib.nombre());  // 2
}
```

### 2.2 Calculatrice avec historique

```rust
// Implémentez une calculatrice qui garde l'historique
struct Calculatrice {
    valeur: f64,
    historique: Vec<String>,
}

impl Calculatrice {
    fn new(valeur_initiale: f64) -> Self { todo!() }

    // Chaque opération retourne &mut Self pour permettre le chaînage
    fn ajouter(&mut self, n: f64) -> &mut Self { todo!() }
    fn soustraire(&mut self, n: f64) -> &mut Self { todo!() }
    fn multiplier(&mut self, n: f64) -> &mut Self { todo!() }
    fn diviser(&mut self, n: f64) -> &mut Self { todo!() }  // gérer la division par zéro

    fn resultat(&self) -> f64 { todo!() }
    fn afficher_historique(&self) { todo!() }
}

fn main() {
    let mut calc = Calculatrice::new(10.0);
    calc.ajouter(5.0)
        .multiplier(2.0)
        .soustraire(3.0)
        .diviser(0.0);  // division par zéro → ne doit pas changer la valeur

    calc.afficher_historique();
    println!("Résultat: {}", calc.resultat());
}
```

---

## Partie 3 — Lifetimes explicites (45 min)

### 3.1 Plus long mot

```rust
// Cette fonction ne compile pas → ajouter les lifetimes
fn plus_long_mot(phrase1: &str, phrase2: &str) -> &str {
    let mots1: Vec<&str> = phrase1.split_whitespace().collect();
    let mots2: Vec<&str> = phrase2.split_whitespace().collect();

    let max1 = mots1.iter().max_by_key(|s| s.len()).copied().unwrap_or("");
    let max2 = mots2.iter().max_by_key(|s| s.len()).copied().unwrap_or("");

    if max1.len() >= max2.len() { max1 } else { max2 }
}

fn main() {
    let phrase1 = String::from("le chat siamois dort");
    let result;
    {
        let phrase2 = String::from("un chimpanzé mange");
        result = plus_long_mot(&phrase1, &phrase2);
        println!("{}", result);
    }
}
```

### 3.2 Struct avec référence

```rust
// Ajouter les lifetimes nécessaires
struct ExtracteurMot {
    texte: &str,  // référence vers un texte externe
}

impl ExtracteurMot {
    fn new(texte: &str) -> Self {
        ExtracteurMot { texte }
    }

    fn premier_mot(&self) -> &str {
        self.texte.split_whitespace().next().unwrap_or("")
    }

    fn mots(&self) -> Vec<&str> {
        self.texte.split_whitespace().collect()
    }
}

fn main() {
    let texte = String::from("Bonjour le monde de Rust");
    let extracteur = ExtracteurMot::new(&texte);
    println!("Premier: {}", extracteur.premier_mot());
    println!("Tous: {:?}", extracteur.mots());
}
```

---

## Partie 4 — Problèmes avancés (30 min)

### 4.1 Gestionnaire de cache

Implémentez un cache simple thread-safe :

```rust
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

// CONTRAINTE : Cache doit être clonable (Arc<Mutex<...>>)
// et le type T doit être Clone + std::fmt::Debug

struct Cache<V: Clone + std::fmt::Debug> {
    donnees: Arc<Mutex<HashMap<String, V>>>,
}

impl<V: Clone + std::fmt::Debug> Cache<V> {
    fn new() -> Self { todo!() }

    fn mettre(&self, cle: String, valeur: V) { todo!() }

    fn obtenir(&self, cle: &str) -> Option<V> { todo!() }  // retourne une copie

    fn supprimer(&self, cle: &str) -> Option<V> { todo!() }

    fn taille(&self) -> usize { todo!() }
}

// Cache doit être clonable pour partage entre threads
impl<V: Clone + std::fmt::Debug> Clone for Cache<V> {
    fn clone(&self) -> Self { todo!() }
}

fn main() {
    let cache: Cache<String> = Cache::new();

    cache.mettre("user:1".into(), "Alice".into());
    cache.mettre("user:2".into(), "Bob".into());

    println!("{:?}", cache.obtenir("user:1"));  // Some("Alice")
    println!("{:?}", cache.obtenir("user:99")); // None
    println!("Taille: {}", cache.taille());

    // Partage entre threads
    let cache2 = cache.clone();
    std::thread::spawn(move || {
        cache2.mettre("user:3".into(), "Charlie".into());
    }).join().unwrap();

    println!("Après thread: {:?}", cache.obtenir("user:3"));
}
```

---

## Solutions commentées

### 1.1 — Move après utilisation

```rust
// Solution 1 : passer une référence
fn afficher(s: &str) {
    println!("{}", s);
}

fn main() {
    let message = String::from("bonjour");
    afficher(&message);    // emprunt
    println!("{}", message);  // toujours valide !
}

// Solution 2 : cloner (coûteux si grande chaîne)
fn afficher_v2(s: String) {
    println!("{}", s);
}

fn main() {
    let message = String::from("bonjour");
    afficher_v2(message.clone());  // clone explicite
    println!("{}", message);
}
```

### 1.4 — Double mutable borrow (le plus subtil)

```rust
fn main() {
    let mut v = vec![1, 2, 3];
    // Solution : ne pas garder la référence pendant le push
    let valeur = v[0];        // copie la valeur (i32 est Copy)
    v.push(4);                // maintenant OK : pas de borrow actif
    println!("{}", valeur);

    // Ou : push avant de prendre la référence
    let mut v = vec![1, 2, 3];
    v.push(4);
    let premier = &v[0];      // borrow après modification
    println!("{}", premier);
}
```

### Cache — Solution complète

```rust
impl<V: Clone + std::fmt::Debug> Cache<V> {
    fn new() -> Self {
        Cache { donnees: Arc::new(Mutex::new(HashMap::new())) }
    }

    fn mettre(&self, cle: String, valeur: V) {
        self.donnees.lock().unwrap().insert(cle, valeur);
    }

    fn obtenir(&self, cle: &str) -> Option<V> {
        self.donnees.lock().unwrap().get(cle).cloned()
    }

    fn supprimer(&self, cle: &str) -> Option<V> {
        self.donnees.lock().unwrap().remove(cle)
    }

    fn taille(&self) -> usize {
        self.donnees.lock().unwrap().len()
    }
}

impl<V: Clone + std::fmt::Debug> Clone for Cache<V> {
    fn clone(&self) -> Self {
        Cache { donnees: Arc::clone(&self.donnees) }
    }
}
```
