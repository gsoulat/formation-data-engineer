# Rust — Borrowing : References &T, &mut T, Règles du Borrow Checker, Lifetimes

## 1. Le problème sans borrowing

Sans borrowing, utiliser une valeur dans une fonction la consomme :

```rust
fn longueur(s: String) -> usize {
    s.len()
}  // s est droppé ici

fn main() {
    let s = String::from("hello");
    let len = longueur(s);   // s est DÉPLACÉ
    // println!("{}", s);    // ERREUR ! s a été déplacé
    println!("{}", len);     // 5
}
```

Le borrowing résout ce problème : **emprunter** sans prendre la propriété.

## 2. Références immuables &T

```rust
fn longueur(s: &String) -> usize {  // s est une référence, pas le propriétaire
    s.len()
}  // s sort de portée mais ne droppe PAS la String (elle ne lui appartient pas)

fn main() {
    let s1 = String::from("hello");
    let len = longueur(&s1);  // & = passer une référence (emprunter)
    println!("'{}' a {} caractères", s1, len);  // s1 toujours valide !
}
```

```
s1 (propriétaire)    &s1 (référence/emprunt)
┌───────────────┐    ┌──────────┐
│ ptr ──────────┼────► ptr ─────┼───► "hello" sur le tas
│ len: 5        │    └──────────┘
│ cap: 5        │
└───────────────┘
```

### Plusieurs références immuables simultanées

```rust
fn main() {
    let s = String::from("hello");

    // Plusieurs références immuables : AUTORISÉ
    let r1 = &s;
    let r2 = &s;
    let r3 = &s;
    println!("{} {} {}", r1, r2, r3);  // OK !

    // Les références n'ont pas de propriété, elles ne peuvent pas modifier
    // r1.push_str(" world");  // ERREUR : &String ne permet pas la mutation
}
```

## 3. Références mutables &mut T

```rust
fn ajouter_monde(s: &mut String) {
    s.push_str(" monde");
}

fn main() {
    let mut s = String::from("bonjour");  // doit être mut
    ajouter_monde(&mut s);               // référence mutable
    println!("{}", s);  // "bonjour monde"
}
```

## 4. Les règles du Borrow Checker

```
Règle 1 : À tout moment, vous pouvez avoir SOIT :
          - N références immuables (&T)
          - OU exactement UNE référence mutable (&mut T)
          Mais PAS les deux en même temps.

Règle 2 : Les références doivent toujours être VALIDES
          (pas de référence vers une valeur qui n'existe plus)
```

Ces règles **éliminent les data races à la compilation**.

```rust
fn main() {
    let mut s = String::from("hello");

    // ERREUR : &mut + & en même temps
    let r1 = &s;
    let r2 = &s;
    let r3 = &mut s;  // ERREUR !
    // error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable
    println!("{} {} {}", r1, r2, r3);

    // ---

    // ERREUR : deux &mut en même temps
    let mut s2 = String::from("hello");
    let r4 = &mut s2;
    let r5 = &mut s2;  // ERREUR !
    // error[E0499]: cannot borrow `s2` as mutable more than once at a time
    println!("{} {}", r4, r5);
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans VS Code, créer le code avec `r3 = &mut s` en même temps que `r1 = &s`. Montrer l'erreur rouge de rust-analyzer en temps réel avec le message complet. Puis taper `cargo build` pour voir le message du compilateur avec les lignes exactes du problème.
> **Expliquer :** Insister sur le message d'erreur Rust qui est extrêmement précis et pédagogique. Comparer avec Java/C++ où ce type de bug ne provoquerait qu'un crash à l'exécution ou pire, un comportement silencieusement incorrect. En Rust, c'est IMPOSSIBLE à l'exécution car bloqué à la compilation.
---

## 5. Non-Lexical Lifetimes (NLL) — Portée des références

Depuis Rust 2018, la portée d'une référence se termine au dernier usage, pas à la fin du bloc :

```rust
fn main() {
    let mut s = String::from("hello");

    let r1 = &s;    // référence immuable
    let r2 = &s;    // deuxième référence immuable
    println!("{} {}", r1, r2);
    // r1 et r2 ne sont plus utilisées après cette ligne
    // Leur portée se termine ici (NLL)

    let r3 = &mut s;  // OK ! r1 et r2 ne sont plus actives
    r3.push_str(" world");
    println!("{}", r3);
}
```

## 6. Dangling References — L'invariant de validité

```rust
// ERREUR : référence vers une valeur qui sera détruite
fn reference_invalide() -> &String {  // Rust refusera de compiler
    let s = String::from("hello");
    &s  // ERREUR : s sera droppé à la fin de la fonction
}
// error[E0106]: missing lifetime specifier

// SOLUTION : retourner la valeur (transférer la propriété)
fn valeur_valide() -> String {
    let s = String::from("hello");
    s   // OK : ownership transféré à l'appelant
}

fn main() {
    let s = valeur_valide();
    println!("{}", s);  // OK
}
```

## 7. Slices — Références vers une partie d'une collection

```rust
fn premier_mot(s: &str) -> &str {
    let octets = s.as_bytes();

    for (i, &octet) in octets.iter().enumerate() {
        if octet == b' ' {
            return &s[0..i];  // slice jusqu'à l'espace
        }
    }

    &s[..]  // toute la chaîne si pas d'espace
}

fn main() {
    let s = String::from("bonjour monde");

    let mot = premier_mot(&s);
    println!("Premier mot: {}", mot);  // "bonjour"

    // String slices
    let s = String::from("hello world");
    let hello = &s[0..5];  // &str : référence vers une partie
    let world = &s[6..11];
    println!("{} {}", hello, world);

    // Raccourcis
    let debut = &s[..5];    // 0..5
    let fin   = &s[6..];    // 6..fin
    let tout  = &s[..];     // toute la chaîne

    // &String et &str
    // &str est plus flexible : accepte &String et les littéraux
    let litterale: &str = "hello";         // stockée dans le binaire
    let string = String::from("hello");
    let ref_string: &str = &string;        // &String → &str automatique

    // Array slices
    let arr = [1, 2, 3, 4, 5];
    let slice: &[i32] = &arr[1..3];  // [2, 3]
    println!("{:?}", slice);

    // Vec slices
    let v = vec![10, 20, 30, 40, 50];
    let milieu: &[i32] = &v[1..4];  // [20, 30, 40]
    println!("{:?}", milieu);
}
```

## 8. Lifetimes — Introduction

Les lifetimes sont des annotations qui indiquent au compilateur comment les durées de vie des références sont liées entre elles.

```rust
// ERREUR : le compilateur ne sait pas quelle référence est retournée
fn plus_longue(x: &str, y: &str) -> &str {  // ERREUR !
    if x.len() > y.len() { x } else { y }
}
// error[E0106]: missing lifetime specifier

// SOLUTION : annoter les lifetimes avec 'a
fn plus_longue_annotee<'a>(x: &'a str, y: &'a str) -> &'a str {
    // 'a signifie : la référence retournée vit au moins aussi longtemps que x ET y
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let s1 = String::from("longue chaîne");
    let resultat;
    {
        let s2 = String::from("xyz");
        resultat = plus_longue_annotee(s1.as_str(), s2.as_str());
        println!("Plus longue : {}", resultat);
    }
    // println!("{}", resultat);  // ERREUR : s2 est sorti de portée
}
```

### Lifetimes dans les structs

```rust
// Un struct qui contient une référence DOIT avoir un lifetime
struct Extrait<'a> {
    partie: &'a str,  // référence vers quelque chose qui vit au moins aussi longtemps que Extrait
}

impl<'a> Extrait<'a> {
    fn afficher(&self) -> &str {
        self.partie
    }
}

fn main() {
    let roman = String::from("Appeler moi Ismaël. Il y a quelques années...");

    let premier_phrase;
    {
        let i = roman.find('.').unwrap_or(roman.len());
        premier_phrase = Extrait {
            partie: &roman[..i],
        };
        println!("{}", premier_phrase.afficher());  // OK
    }
    // premier_phrase ne peut pas être utilisé après la fin de roman
}
```

### Règles d'élision des lifetimes

Le compilateur infère les lifetimes dans les cas courants :

```rust
// Règle 1 : chaque paramètre référence a son propre lifetime
fn premierligne(s: &str) -> &str {
    // Équivalent à : fn premierligne<'a>(s: &'a str) -> &'a str
    s.lines().next().unwrap_or("")
}

// Règle 2 : si 1 seul paramètre &, la sortie hérite de son lifetime
// Règle 3 : si &self, la sortie hérite du lifetime de self

struct Texte {
    contenu: String,
}

impl Texte {
    fn premiere_ligne(&self) -> &str {
        // Équivalent : fn premiere_ligne<'a>(&'a self) -> &'a str
        self.contenu.lines().next().unwrap_or("")
    }
}

// Lifetime statique : vit toute la durée du programme
let s: &'static str = "J'ai une vie statique.";
// Les littéraux &str sont toujours 'static
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer l'erreur de compilation de `plus_longue` sans annotation de lifetime. Le message d'erreur Rust explique exactement ce qu'il faut faire et pourquoi. Montrer aussi que `cargo check` détecte ces erreurs en quelques millisecondes.
> **Expliquer :** Expliquer que les lifetimes ne sont PAS des runtime features — elles n'existent qu'à la compilation. Elles permettent au compilateur de vérifier que les références ne "survivent" pas aux données qu'elles référencent. 90% du temps, l'élision automatique fonctionne et on n'a pas besoin de les écrire.
---

## 9. Pattern courant : emprunter puis utiliser

```rust
fn main() {
    // Pattern fréquent : itérer sans consommer
    let v = vec![1, 2, 3, 4, 5];

    // .iter() = itérateur de références &i32 (emprunte v)
    let somme: i32 = v.iter().sum();
    println!("Vec: {:?}, Somme: {}", v, somme);  // v toujours valide

    // .iter_mut() = itérateur de références mutables
    let mut v2 = vec![1, 2, 3, 4, 5];
    for n in v2.iter_mut() {
        *n *= 2;  // déréférence pour modifier
    }
    println!("{:?}", v2);  // [2, 4, 6, 8, 10]

    // .into_iter() = consomme le Vec
    let v3 = vec![1, 2, 3];
    for n in v3.into_iter() {  // v3 est consommé
        println!("{}", n);
    }
    // println!("{:?}", v3);  // ERREUR : v3 consommé

    // String : emprunter avec &str
    let mut s = String::from("hello");
    afficher_longueur(&s);  // emprunt immuable
    s.push_str(" world");   // après que l'emprunt soit terminé
    println!("{}", s);

    // Déréférencement
    let x = 5;
    let y = &x;
    println!("{} {}", x, *y);   // *y déréférence
    println!("{}", x == *y);    // true

    let s = String::from("hello");
    let r = &s;
    println!("{}", r.len());    // auto-déréférence : pas besoin de (*r).len()
}

fn afficher_longueur(s: &str) {
    println!("Longueur: {}", s.len());
}
```

## Récapitulatif

| Concept | Syntaxe | Règle |
|---------|---------|-------|
| Référence immuable | `&T` | N simultanées autorisées |
| Référence mutable | `&mut T` | UNE seule, exclusive |
| Mélange | `&T` + `&mut T` | INTERDIT simultanément |
| Dangling reference | `&valeur_détruite` | IMPOSSIBLE (erreur compilation) |
| Slice string | `&str`, `&s[0..5]` | Vue sur une partie |
| Slice tableau | `&[T]`, `&arr[1..3]` | Vue sur une partie |
| Lifetime | `<'a>` | Lien entre durées de vie |
| Élision | — | 90% des cas, inféré automatiquement |

### Analogie pour mémoriser les règles

```
&T (immuable) = Prêt d'un livre à lire
  → Plusieurs personnes peuvent lire le même livre
  → Tant que quelqu'un lit, personne ne peut l'écrire

&mut T (mutable) = Prêt d'un livre pour l'annoter
  → Une seule personne peut annoter
  → Personne d'autre ne peut lire pendant l'annotation
```
