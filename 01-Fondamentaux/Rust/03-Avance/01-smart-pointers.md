# Rust — Smart Pointers : Box<T>, Rc<T>, RefCell<T>, Arc<T>, Mutex<T>

## 1. Pourquoi les smart pointers ?

Les smart pointers étendent les capacités du système d'ownership en fournissant des sémantiques spéciales :

| Type | Ownership | Thread-safe | Mutabilité | Cas d'usage |
|------|-----------|-------------|------------|-------------|
| `Box<T>` | Un propriétaire | ✓ (si T: Send) | Oui | Allocation heap, taille inconnue |
| `Rc<T>` | Multiple | ✗ | Non | Graphes, partage dans un thread |
| `RefCell<T>` | Un propriétaire | ✗ | Dynamique | Interior mutability |
| `Arc<T>` | Multiple | ✓ | Non | Partage entre threads |
| `Mutex<T>` | Un propriétaire | ✓ | Exclusif | Accès concurrent |

## 2. Box<T> — Allocation sur le tas

```rust
fn main() {
    // Box : alloue T sur le tas, pointeur sur la pile
    let b = Box::new(5);   // i32 sur le tas
    println!("{}", b);     // 5 (déréférencement automatique)
    println!("{}", *b);    // 5 (déréférencement explicite)

    // Utile pour les types de taille inconnue à la compilation
    // (ex : types récursifs)

    // Arbre binaire récursif (impossible sans Box)
    #[derive(Debug)]
    enum Arbre {
        Feuille(i32),
        Noeud(Box<Arbre>, i32, Box<Arbre>),
    }

    let arbre = Arbre::Noeud(
        Box::new(Arbre::Feuille(1)),
        2,
        Box::new(Arbre::Noeud(
            Box::new(Arbre::Feuille(3)),
            4,
            Box::new(Arbre::Feuille(5)),
        )),
    );
    println!("{:#?}", arbre);

    // Liste chaînée récursive
    #[derive(Debug)]
    enum Liste {
        Cons(i32, Box<Liste>),
        Nil,
    }

    let l = Liste::Cons(1,
        Box::new(Liste::Cons(2,
            Box::new(Liste::Cons(3,
                Box::new(Liste::Nil))))));
    println!("{:?}", l);

    // Box<dyn Trait> : trait object
    trait Animal { fn cri(&self) -> &str; }
    struct Chien;
    struct Chat;
    impl Animal for Chien { fn cri(&self) -> &str { "Woof" } }
    impl Animal for Chat  { fn cri(&self) -> &str { "Meow" } }

    let animaux: Vec<Box<dyn Animal>> = vec![
        Box::new(Chien),
        Box::new(Chat),
        Box::new(Chien),
    ];
    for a in &animaux {
        println!("{}", a.cri());
    }
}
```

## 3. Rc<T> — Reference Counting (thread unique)

```rust
use std::rc::Rc;

fn main() {
    // Rc : plusieurs propriétaires via comptage de références
    let a = Rc::new(String::from("hello"));
    println!("Count après création de a : {}", Rc::strong_count(&a));  // 1

    let b = Rc::clone(&a);  // clone léger : incrémente le compteur, NE copie PAS la String
    println!("Count après clone b : {}", Rc::strong_count(&a));  // 2

    {
        let c = Rc::clone(&a);
        println!("Count dans le bloc : {}", Rc::strong_count(&a));  // 3
    }  // c droppé → décrémente
    println!("Count après bloc : {}", Rc::strong_count(&a));  // 2

    // a et b pointent vers la même String
    println!("{} {}", a, b);  // hello hello

    // Rc est immuable : pas de &mut à travers Rc
    // a.push_str(" world");  // ERREUR : ne peut pas muter à travers Rc

    // --- Exemple : graphe partagé ---
    #[derive(Debug)]
    struct Noeud {
        valeur: i32,
        enfants: Vec<Rc<Noeud>>,
    }

    let feuille1 = Rc::new(Noeud { valeur: 1, enfants: vec![] });
    let feuille2 = Rc::new(Noeud { valeur: 2, enfants: vec![] });

    let parent = Rc::new(Noeud {
        valeur: 10,
        enfants: vec![Rc::clone(&feuille1), Rc::clone(&feuille2)],
    });

    let parent2 = Rc::new(Noeud {
        valeur: 20,
        enfants: vec![Rc::clone(&feuille1)],  // feuille1 est partagée !
    });

    println!("feuille1 count: {}", Rc::strong_count(&feuille1));  // 3
}
```

## 4. RefCell<T> — Interior Mutability

```rust
use std::cell::RefCell;

// RefCell déplace les vérifications d'emprunt à l'exécution
// Permet la mutation même à travers une référence immuable

fn main() {
    let val = RefCell::new(5);

    // borrow() : référence immuable (vérifiée à l'exécution)
    let r1 = val.borrow();
    let r2 = val.borrow();
    println!("{} {}", r1, r2);  // Plusieurs borrow() simultanés OK
    drop(r1);
    drop(r2);

    // borrow_mut() : référence mutable (exclusive)
    *val.borrow_mut() += 1;
    println!("{}", val.borrow());  // 6

    // PANIC à l'exécution si les règles sont violées :
    let r3 = val.borrow();
    // let r4 = val.borrow_mut();  // PANIC : déjà emprunté immuablement

    // --- Pattern classique : Rc<RefCell<T>> ---
    // Plusieurs propriétaires + mutation

    use std::rc::Rc;

    #[derive(Debug)]
    struct Compte {
        solde: RefCell<f64>,
        proprietaires: Vec<String>,
    }

    impl Compte {
        fn new(solde_initial: f64) -> Rc<Self> {
            Rc::new(Compte {
                solde: RefCell::new(solde_initial),
                proprietaires: Vec::new(),
            })
        }

        fn deposer(&self, montant: f64) {
            *self.solde.borrow_mut() += montant;
        }

        fn retirer(&self, montant: f64) -> Result<(), String> {
            let mut solde = self.solde.borrow_mut();
            if *solde < montant {
                return Err("Solde insuffisant".into());
            }
            *solde -= montant;
            Ok(())
        }

        fn solde(&self) -> f64 {
            *self.solde.borrow()
        }
    }

    let compte = Compte::new(1000.0);
    let compte2 = Rc::clone(&compte);  // deuxième accès au même compte

    compte.deposer(200.0);
    println!("Solde: {}", compte2.solde());  // 1200.0

    match compte2.retirer(500.0) {
        Ok(()) => println!("Retrait OK. Solde: {}", compte.solde()),
        Err(e) => println!("Erreur: {}", e),
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Provoquer intentionnellement un `panic` avec `RefCell` : appeler `borrow_mut()` quand un `borrow()` est déjà actif. Montrer le panic message dans le terminal avec `thread 'main' panicked at 'already borrowed'`. Expliquer que c'est un panic à l'EXÉCUTION (pas compilation).
> **Expliquer :** Contraster avec les règles du borrow checker normales (erreur de COMPILATION). `RefCell` est un dernier recours quand on ne peut pas satisfaire le borrow checker à la compilation. C'est l'outil pour les patterns de "interior mutability" comme les caches.
---

## 5. Arc<T> — Atomic Reference Counting (multi-threads)

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    // Arc = Rc mais thread-safe (atomic operations)

    let donnees = Arc::new(vec![1, 2, 3, 4, 5]);

    let mut handles = vec![];

    for i in 0..3 {
        let donnees_clone = Arc::clone(&donnees);  // clone du Arc (pas des données)
        let handle = thread::spawn(move || {
            println!("Thread {}: {:?}", i, donnees_clone);
            // donnees_clone est déplacé dans le thread
            let somme: i32 = donnees_clone.iter().sum();
            println!("Thread {}: somme = {}", i, somme);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    // Les données originales sont toujours accessibles
    println!("Données originales: {:?}", donnees);
}
```

## 6. Mutex<T> — Exclusion mutuelle

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Mutex : protège des données avec un verrou
    // Lock → accès → déverrouillage automatique (quand le MutexGuard est droppé)

    let compteur = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let compteur = Arc::clone(&compteur);
        let h = thread::spawn(move || {
            let mut num = compteur.lock().unwrap();  // acquiert le verrou
            *num += 1;
            // verrou libéré automatiquement quand `num` sort de portée
        });
        handles.push(h);
    }

    for h in handles { h.join().unwrap(); }
    println!("Compteur final: {}", *compteur.lock().unwrap());  // 10

    // --- RwLock : plusieurs lecteurs OU un seul écrivain ---
    use std::sync::RwLock;
    let cache = Arc::new(RwLock::new(std::collections::HashMap::<String, i32>::new()));

    // Écriture
    {
        let mut map = cache.write().unwrap();
        map.insert("clé".into(), 42);
    }

    // Lectures simultanées
    let cache2 = Arc::clone(&cache);
    let h1 = thread::spawn(move || {
        let map = cache2.read().unwrap();
        println!("Thread 1: {:?}", map.get("clé"));
    });

    let map = cache.read().unwrap();
    println!("Main: {:?}", map.get("clé"));

    h1.join().unwrap();
}
```

## 7. Choisir le bon smart pointer

```rust
// Arbre de décision :
//
// Besoin d'allocation heap ? → Box<T>
//
// Besoin de plusieurs propriétaires ?
//   OUI + Thread unique ?            → Rc<T>
//   OUI + Multi-threads ?            → Arc<T>
//   NON                              → Ownership normal
//
// Besoin de mutation partagée ?
//   Thread unique ?                  → RefCell<T> ou Rc<RefCell<T>>
//   Multi-threads ?                  → Mutex<T> ou Arc<Mutex<T>>
//   Nombreux lecteurs, rare écriture → RwLock<T> ou Arc<RwLock<T>>

// --- Récapitulatif avec exemples ---

// Box : taille inconnue à la compilation
fn exemple_box() -> Box<dyn std::fmt::Debug> {
    Box::new(vec![1, 2, 3])
}

// Rc + RefCell : cache partagé modifiable (thread unique)
fn exemple_cache() -> std::rc::Rc<std::cell::RefCell<std::collections::HashMap<String, i32>>> {
    use std::rc::Rc;
    use std::cell::RefCell;
    Rc::new(RefCell::new(std::collections::HashMap::new()))
}

// Arc + Mutex : état partagé entre threads
fn exemple_etat_partage() -> Arc<Mutex<Vec<String>>> {
    Arc::new(Mutex::new(Vec::new()))
}
```

## Récapitulatif

| Smart Pointer | Propriétaires | Thread-safe | Mutation | Pattern typique |
|--------------|---------------|-------------|----------|-----------------|
| `Box<T>` | 1 | ✓ (si T: Send) | Via `&mut T` | Types récursifs, trait objects |
| `Rc<T>` | Multiple | ✗ | Non | Graphes, DAGs (thread unique) |
| `Arc<T>` | Multiple | ✓ | Non | Partage entre threads (lecture) |
| `RefCell<T>` | 1 | ✗ | Dynamique | Interior mutability |
| `Rc<RefCell<T>>` | Multiple | ✗ | Partagée | Cache, état partagé (1 thread) |
| `Arc<Mutex<T>>` | Multiple | ✓ | Exclusive | État partagé (multi-threads) |
| `Arc<RwLock<T>>` | Multiple | ✓ | R/W | Cache concurrent (multi-threads) |
