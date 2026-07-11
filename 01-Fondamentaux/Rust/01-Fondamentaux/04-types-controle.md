# Rust — Structs, Enums, match, if let, while let

## 1. Structs

```rust
// --- Struct classique ---
#[derive(Debug, Clone)]  // dériver des traits automatiquement
struct Utilisateur {
    nom: String,
    email: String,
    age: u32,
    actif: bool,
}

// --- Struct tuple (champs positionnels) ---
#[derive(Debug, Clone, Copy)]
struct Point(f64, f64);

#[derive(Debug, Clone, Copy)]
struct Couleur(u8, u8, u8);  // RGB

// --- Unit struct (pas de données, souvent pour les traits) ---
struct Marqueur;

// --- Implémentation de méthodes ---
impl Utilisateur {

    // Méthode associée (fonction associée / static method) : pas de self
    // Souvent utilisée comme constructeur
    fn new(nom: &str, email: &str, age: u32) -> Self {
        Utilisateur {
            nom: String::from(nom),
            email: String::from(email),
            age,                      // shorthand : age = age
            actif: true,
        }
    }

    // Méthode d'instance : &self (lecture)
    fn afficher(&self) {
        println!("{} ({}) - {}", self.nom, self.age, self.email);
    }

    fn est_adulte(&self) -> bool {
        self.age >= 18
    }

    fn email_domaine(&self) -> &str {
        self.email.split('@').last().unwrap_or("")
    }

    // Méthode d'instance : &mut self (modification)
    fn desactiver(&mut self) {
        self.actif = false;
    }

    fn changer_email(&mut self, nouvel_email: String) {
        self.email = nouvel_email;
    }

    // Méthode qui consomme : self (prend la propriété)
    fn en_log(self) -> String {
        format!("[LOG] {} <{}>", self.nom, self.email)
    }
}

impl Point {
    fn new(x: f64, y: f64) -> Self { Point(x, y) }

    fn distance_origine(&self) -> f64 {
        (self.0 * self.0 + self.1 * self.1).sqrt()
    }

    fn distance(&self, autre: &Point) -> f64 {
        let dx = self.0 - autre.0;
        let dy = self.1 - autre.1;
        (dx * dx + dy * dy).sqrt()
    }
}

// Plusieurs blocs impl pour le même type : valide
impl Point {
    fn milieu(&self, autre: &Point) -> Point {
        Point((self.0 + autre.0) / 2.0, (self.1 + autre.1) / 2.0)
    }
}

fn main() {
    // Création
    let mut user = Utilisateur::new("Alice", "alice@example.com", 30);
    println!("{:?}", user);      // debug
    user.afficher();              // méthode d'instance

    // Modification
    user.changer_email(String::from("alice2@example.com"));
    user.desactiver();
    println!("{:?}", user);

    // Syntaxe de mise à jour : copier les champs non spécifiés
    let user2 = Utilisateur {
        nom: String::from("Bob"),
        email: String::from("bob@example.com"),
        ..user  // les autres champs depuis user
    };
    println!("{:?}", user2);

    // Points
    let p1 = Point::new(3.0, 4.0);
    let p2 = Point(6.0, 8.0);
    println!("Distance origine : {:.2}", p1.distance_origine());  // 5.00
    println!("Distance p1-p2 : {:.2}", p1.distance(&p2));

    // Déstructuration
    let Point(x, y) = p1;
    println!("x={}, y={}", x, y);

    let Utilisateur { nom, email, age, actif } = user2;
    println!("{} {} {} {}", nom, email, age, actif);
}
```

## 2. Enums

```rust
// --- Enum simple ---
#[derive(Debug, PartialEq)]
enum Direction {
    Nord,
    Sud,
    Est,
    Ouest,
}

// --- Enum avec données ---
#[derive(Debug)]
enum Message {
    Quitter,                          // pas de données
    Bouger { x: i32, y: i32 },        // struct anonyme
    Ecrire(String),                    // tuple d'une valeur
    ChangerCouleur(u8, u8, u8),        // tuple de trois valeurs
}

// --- Enum générique (Option et Result sont définis ainsi) ---
enum MaOption<T> {
    Aucun,
    Valeur(T),
}

// Implémentation de méthodes sur un enum
impl Message {
    fn appeler(&self) {
        match self {
            Message::Quitter          => println!("Quitter"),
            Message::Bouger { x, y }  => println!("Bouger vers ({}, {})", x, y),
            Message::Ecrire(texte)    => println!("Écrire : {}", texte),
            Message::ChangerCouleur(r, g, b) => println!("Couleur : ({},{},{})", r, g, b),
        }
    }
}

fn main() {
    let dir = Direction::Nord;
    println!("{:?}", dir);

    let messages = vec![
        Message::Ecrire(String::from("hello")),
        Message::Bouger { x: 10, y: 20 },
        Message::ChangerCouleur(255, 0, 0),
        Message::Quitter,
    ];

    for msg in &messages {
        msg.appeler();
    }
}
```

## 3. match — Pattern Matching

```rust
fn main() {
    // --- match simple ---
    let nb = 5;
    match nb {
        1 => println!("un"),
        2 => println!("deux"),
        3 | 4 | 5 => println!("trois, quatre ou cinq"),  // | pour OR
        6..=10 => println!("six à dix"),                  // plage inclusive
        _ => println!("autre chose"),                     // wildcard (obligatoire si non exhaustif)
    }

    // --- match retourne une valeur ---
    let description = match nb {
        0 => "zéro",
        1..=9 => "un chiffre",
        10..=99 => "deux chiffres",
        _ => "beaucoup",
    };
    println!("{}", description);

    // --- match sur un enum ---
    let msg = Message::Bouger { x: 5, y: 10 };
    match msg {
        Message::Quitter => println!("Quitter"),
        Message::Bouger { x, y } => println!("Bouger ({}, {})", x, y),
        Message::Ecrire(ref texte) => println!("Écrire: {}", texte),
        Message::ChangerCouleur(r, g, b) => println!("RGB({},{},{})", r, g, b),
    }

    // --- Binding avec @ ---
    let nb = 15;
    match nb {
        n @ 1..=12 => println!("Mois : {}", n),
        n @ 13..=19 => println!("Ado : {}", n),
        n => println!("Autre : {}", n),
    }

    // --- Guards (conditions supplémentaires) ---
    let paire = (2, -3);
    match paire {
        (x, y) if x == y         => println!("Égaux : {}", x),
        (x, y) if x + y == 0     => println!("Opposés"),
        (x, _) if x % 2 == 0     => println!("x est pair : {}", x),
        (x, y)                   => println!("Autre : ({}, {})", x, y),
    }

    // --- Destructuration dans match ---
    struct Point { x: i32, y: i32 }
    let p = Point { x: 0, y: 7 };
    match p {
        Point { x: 0, y }  => println!("Sur l'axe Y à {}", y),
        Point { x, y: 0 }  => println!("Sur l'axe X à {}", x),
        Point { x, y }     => println!("({}, {})", x, y),
    }

    // --- Tuple dans match ---
    let etat = (true, false);
    match etat {
        (true, true)   => println!("Les deux vrais"),
        (true, false)  => println!("Premier seulement"),
        (false, true)  => println!("Second seulement"),
        (false, false) => println!("Aucun"),
    }

    // --- Reference dans match ---
    let v = vec![1, 2, 3];
    match v.as_slice() {
        []         => println!("Vide"),
        [x]        => println!("Un élément : {}", x),
        [x, y]     => println!("Deux : {} {}", x, y),
        [first, .., last] => println!("Premier: {}, Dernier: {}", first, last),
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Créer un `enum Forme { Cercle(f64), Rectangle(f64, f64), Triangle(f64, f64, f64) }` et un `match` dessus. Enlever un cas (`Triangle`) et montrer l'erreur de compilation "non-exhaustive patterns : `Triangle(_,_,_)` not covered". Rust force l'exhaustivité du match.
> **Expliquer :** C'est l'avantage majeur des enums + match par rapport à Java. Le compilateur garantit que tous les cas sont traités. Si on ajoute un nouveau variant à l'enum, tous les match dans le code cesseront de compiler jusqu'à ce qu'on les gère.
---

## 4. Option<T> — Absence de valeur

```rust
fn main() {
    // Option<T> : soit Some(T) soit None
    // Défini dans la stdlib : enum Option<T> { Some(T), None }

    let nombre: Option<i32> = Some(42);
    let vide: Option<i32>   = None;

    // --- match ---
    match nombre {
        Some(n) => println!("Valeur : {}", n),
        None    => println!("Pas de valeur"),
    }

    // --- Méthodes de Option ---
    println!("{}", nombre.unwrap());          // 42 (panic si None !)
    println!("{}", vide.unwrap_or(0));        // 0 (valeur par défaut)
    println!("{}", vide.unwrap_or_else(|| calculer_defaut())); // lazy

    let double = nombre.map(|n| n * 2);       // Some(84)
    let filtre = nombre.filter(|&n| n > 100); // None (42 n'est pas > 100)

    nombre.iter().for_each(|n| println!("{}", n));

    if nombre.is_some() { println!("Présent"); }
    if vide.is_none()   { println!("Absent");  }

    // --- Option dans les fonctions ---
    let vec = vec![1, 2, 3, 4, 5];
    let premier: Option<&i32> = vec.first();
    let dernier: Option<&i32> = vec.last();

    // find retourne Option
    let trouve: Option<&i32> = vec.iter().find(|&&x| x > 3);  // Some(&4)

    // --- Option comme résultat de division sûre ---
    fn diviser(a: f64, b: f64) -> Option<f64> {
        if b == 0.0 { None } else { Some(a / b) }
    }

    match diviser(10.0, 2.0) {
        Some(r) => println!("Résultat: {}", r),
        None    => println!("Division par zéro"),
    }
}

fn calculer_defaut() -> i32 { 99 }
```

## 5. if let — Match simplifié pour un seul cas

```rust
fn main() {
    let nombre: Option<i32> = Some(42);

    // Verbose avec match :
    match nombre {
        Some(n) => println!("Valeur: {}", n),
        None    => (),  // ne rien faire pour None
    }

    // Équivalent avec if let (plus concis) :
    if let Some(n) = nombre {
        println!("Valeur: {}", n);
    }

    // Avec else
    if let Some(n) = nombre {
        println!("Valeur: {}", n);
    } else {
        println!("Pas de valeur");
    }

    // if let avec enum
    let msg = Message::Ecrire(String::from("hello"));
    if let Message::Ecrire(ref texte) = msg {
        println!("Message: {}", texte);
    }

    // Chaîner avec else if let
    let coin = Some(5u8);
    if let Some(3) = coin {
        println!("three");
    } else if let Some(5) = coin {
        println!("five");   // → "five"
    } else {
        println!("autre");
    }

    // let-else (Rust 1.65+) : "unwrap ou return"
    fn traiter(val: Option<i32>) {
        let Some(n) = val else {
            println!("Valeur absente, on retourne");
            return;
        };
        println!("Valeur: {}", n);
    }

    traiter(Some(10));  // "Valeur: 10"
    traiter(None);      // "Valeur absente, on retourne"
}
```

## 6. while let — Boucle sur un pattern

```rust
fn main() {
    // Dépiler jusqu'à None
    let mut pile = vec![1, 2, 3, 4, 5];
    while let Some(sommet) = pile.pop() {
        println!("{}", sommet);  // 5, 4, 3, 2, 1
    }

    // Lire depuis un canal jusqu'à fermeture
    use std::sync::mpsc;
    let (tx, rx) = mpsc::channel();

    // Dans un autre thread : tx.send(valeur) puis drop(tx)
    // Dans le thread actuel :
    // while let Ok(msg) = rx.recv() {
    //     println!("Reçu: {}", msg);
    // }

    // Itérateur manuel
    let mut iter = vec![1, 2, 3].into_iter();
    while let Some(val) = iter.next() {
        println!("{}", val);
    }
}
```

## 7. Exemple complet : système de commandes

```rust
#[derive(Debug)]
enum EtatCommande {
    EnAttente,
    EnCours { employe: String },
    Livree { date: String },
    Annulee { raison: String },
}

#[derive(Debug)]
struct Commande {
    id: u32,
    produit: String,
    quantite: u32,
    etat: EtatCommande,
}

impl Commande {
    fn new(id: u32, produit: &str, quantite: u32) -> Self {
        Commande {
            id,
            produit: String::from(produit),
            quantite,
            etat: EtatCommande::EnAttente,
        }
    }

    fn traiter(&mut self, employe: &str) {
        match self.etat {
            EtatCommande::EnAttente => {
                self.etat = EtatCommande::EnCours {
                    employe: String::from(employe),
                };
                println!("Commande {} prise en charge par {}", self.id, employe);
            }
            _ => println!("Commande {} ne peut pas être traitée (état: {:?})", self.id, self.etat),
        }
    }

    fn livrer(&mut self, date: &str) {
        if let EtatCommande::EnCours { .. } = self.etat {
            self.etat = EtatCommande::Livree { date: String::from(date) };
            println!("Commande {} livrée le {}", self.id, date);
        } else {
            println!("Commande {} ne peut pas être livrée", self.id);
        }
    }

    fn annuler(&mut self, raison: &str) {
        match &self.etat {
            EtatCommande::Livree { .. } => {
                println!("Impossible d'annuler une commande livrée");
            }
            _ => {
                self.etat = EtatCommande::Annulee { raison: String::from(raison) };
                println!("Commande {} annulée : {}", self.id, raison);
            }
        }
    }

    fn resume(&self) -> String {
        let etat_str = match &self.etat {
            EtatCommande::EnAttente             => "En attente".to_string(),
            EtatCommande::EnCours { employe }   => format!("En cours ({})", employe),
            EtatCommande::Livree { date }        => format!("Livrée le {}", date),
            EtatCommande::Annulee { raison }     => format!("Annulée : {}", raison),
        };
        format!("#{} {} x{} — {}", self.id, self.produit, self.quantite, etat_str)
    }
}

fn main() {
    let mut commande = Commande::new(1, "Clavier", 2);
    println!("{}", commande.resume());

    commande.traiter("Alice");
    println!("{}", commande.resume());

    commande.livrer("2024-01-15");
    println!("{}", commande.resume());

    commande.annuler("Client demande");  // impossible après livraison
    println!("{}", commande.resume());

    // Vec de commandes avec différents états
    let commandes: Vec<Commande> = vec![
        { let mut c = Commande::new(2, "Souris", 1); c.traiter("Bob"); c },
        Commande::new(3, "Écran", 1),
        { let mut c = Commande::new(4, "Clavier", 3); c.traiter("Carol"); c.livrer("2024-01-10"); c },
    ];

    // Compter par état
    let en_cours = commandes.iter()
        .filter(|c| matches!(c.etat, EtatCommande::EnCours { .. }))
        .count();
    println!("Commandes en cours : {}", en_cours);

    for c in &commandes {
        println!("{}", c.resume());
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Compiler et exécuter le programme `Commande`. Montrer dans VS Code comment rust-analyzer propose l'autocomplétion des variants de l'enum dans un `match`. Montrer aussi que si on ajoute un nouveau variant à `EtatCommande`, tous les `match` cessent de compiler jusqu'à ce qu'on l'ajoute.
> **Expliquer :** Comparer avec Java où on utiliserait des classes et une hiérarchie d'héritage pour faire la même chose. Les enums Rust avec données associées sont beaucoup plus expressifs et sûrs que les classes Java ou les constantes C/Java.
---

## Récapitulatif

| Concept | Syntaxe | Cas d'usage |
|---------|---------|-------------|
| Struct | `struct Nom { champ: Type }` | Grouper des données nommées |
| Struct tuple | `struct Point(f64, f64)` | Grouper par position |
| Impl | `impl Struct { fn methode(&self) }` | Méthodes |
| Enum | `enum Forme { Cercle(f64), Rect(f64,f64) }` | Type somme avec données |
| match | `match val { pat => expr, _ => ... }` | Pattern matching exhaustif |
| if let | `if let Some(x) = opt { ... }` | Match pour un seul cas |
| while let | `while let Some(x) = iter.next() { }` | Boucle sur un pattern |
| Option | `Some(T)` / `None` | Valeur absente sans null |
| Déstructuration | `let (x, y) = tuple;` | Extraire des valeurs |
