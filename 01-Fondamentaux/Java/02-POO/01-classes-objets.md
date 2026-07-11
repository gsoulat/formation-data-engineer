# Java POO — Classes, Objets, Constructeurs, this, static, toString, equals

## 1. Paradigme orienté objet

La POO modélise le monde réel avec des **objets** qui ont :
- Des **attributs** (état, données) → ce qu'ils *sont*
- Des **méthodes** (comportements) → ce qu'ils *font*

Une **classe** est le plan de construction (le moule) ; un **objet** est une instance concrète de cette classe.

```
Classe Voiture              Objet maVoiture
───────────────             ────────────────────
+ marque : String    →      marque = "Renault"
+ modele : String    →      modele = "Clio"
+ vitesse : int      →      vitesse = 0
─────────────────           ────────────────────
+ demarrer()         →      maVoiture.demarrer()
+ accelerer(km/h)    →      maVoiture.accelerer(50)
+ freiner()          →      maVoiture.freiner()
```

## 2. Définir une classe

```java
// Fichier : Voiture.java
public class Voiture {

    // --- Attributs (champs / fields) ---
    // Convention : private pour l'encapsulation
    private String marque;
    private String modele;
    private int annee;
    private double vitesse;    // km/h courante
    private double vitesseMax; // km/h maximum

    // --- Constructeur par défaut (sans paramètre) ---
    public Voiture() {
        this.marque = "Inconnue";
        this.modele = "Inconnu";
        this.annee = 2020;
        this.vitesseMax = 150;
        this.vitesse = 0;
    }

    // --- Constructeur paramétré ---
    public Voiture(String marque, String modele, int annee, double vitesseMax) {
        this.marque = marque;       // this.marque = attribut, marque = paramètre
        this.modele = modele;
        this.annee = annee;
        this.vitesseMax = vitesseMax;
        this.vitesse = 0;           // toujours démarré à 0
    }

    // --- Constructeur de copie ---
    public Voiture(Voiture autre) {
        this(autre.marque, autre.modele, autre.annee, autre.vitesseMax);
        // this(...) appelle un autre constructeur de la même classe
    }

    // --- Getters (accesseurs) ---
    public String getMarque()     { return marque; }
    public String getModele()     { return modele; }
    public int    getAnnee()      { return annee; }
    public double getVitesse()    { return vitesse; }
    public double getVitesseMax() { return vitesseMax; }

    // --- Setters (mutateurs) ---
    public void setMarque(String marque) {
        if (marque != null && !marque.isBlank()) {
            this.marque = marque;
        }
    }

    public void setAnnee(int annee) {
        if (annee >= 1886 && annee <= 2030) {  // validation
            this.annee = annee;
        } else {
            throw new IllegalArgumentException("Année invalide : " + annee);
        }
    }

    // --- Méthodes métier ---
    public void demarrer() {
        System.out.println(marque + " " + modele + " démarre !");
    }

    public void accelerer(double kmh) {
        if (kmh <= 0) {
            System.out.println("L'accélération doit être positive");
            return;
        }
        double nouvelleVitesse = vitesse + kmh;
        if (nouvelleVitesse > vitesseMax) {
            vitesse = vitesseMax;
            System.out.println("Vitesse maximum atteinte : " + vitesseMax + " km/h");
        } else {
            vitesse = nouvelleVitesse;
            System.out.printf("Accélération à %.1f km/h%n", vitesse);
        }
    }

    public void freiner(double kmh) {
        vitesse = Math.max(0, vitesse - kmh);
        System.out.printf("Freinage à %.1f km/h%n", vitesse);
    }

    public boolean estALArret() {
        return vitesse == 0;
    }

    // --- toString() ---
    @Override
    public String toString() {
        return String.format("Voiture{%s %s (%d), %.1f/%.1f km/h}",
                marque, modele, annee, vitesse, vitesseMax);
    }

    // --- equals() ---
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;                    // même référence
        if (obj == null) return false;
        if (getClass() != obj.getClass()) return false;
        Voiture autre = (Voiture) obj;
        return annee == autre.annee
                && Double.compare(vitesseMax, autre.vitesseMax) == 0
                && java.util.Objects.equals(marque, autre.marque)
                && java.util.Objects.equals(modele, autre.modele);
    }

    // --- hashCode() : toujours redéfinir avec equals ---
    @Override
    public int hashCode() {
        return java.util.Objects.hash(marque, modele, annee, vitesseMax);
    }
}
```

## 3. Utiliser une classe (créer des objets)

```java
public class MainVoiture {
    public static void main(String[] args) {

        // --- Instanciation avec new ---
        Voiture v1 = new Voiture("Renault", "Clio", 2022, 180);
        Voiture v2 = new Voiture("Peugeot", "308", 2021, 200);
        Voiture v3 = new Voiture();          // constructeur par défaut
        Voiture v4 = new Voiture(v1);        // constructeur de copie

        // --- Appel de méthodes ---
        v1.demarrer();
        v1.accelerer(60);
        v1.accelerer(80);
        v1.accelerer(50);  // atteint la limite de 180
        v1.freiner(30);
        System.out.println(v1.estALArret());  // false

        // --- Getters ---
        System.out.println(v1.getMarque());   // "Renault"
        System.out.println(v1.getVitesse());  // 150.0

        // --- Setters avec validation ---
        v1.setMarque("Renault-Nissan");
        try {
            v1.setAnnee(1800);  // lève une exception
        } catch (IllegalArgumentException e) {
            System.out.println("Erreur : " + e.getMessage());
        }

        // --- toString() implicite ---
        System.out.println(v1);  // appelle automatiquement toString()

        // --- equals() ---
        System.out.println(v1.equals(v4));  // true (même données à la création)
        System.out.println(v1 == v4);       // false (objets différents en mémoire)
        System.out.println(v1.equals(v2));  // false

        // --- Référence null ---
        Voiture nulle = null;
        // nulle.demarrer();  // NullPointerException !
        if (nulle != null) {
            nulle.demarrer();
        }

        // --- Tableau d'objets ---
        Voiture[] parc = new Voiture[3];
        parc[0] = v1;
        parc[1] = v2;
        parc[2] = new Voiture("Toyota", "Yaris", 2023, 170);

        for (Voiture v : parc) {
            System.out.println(v);
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans IntelliJ, montrer la génération automatique de `toString()`, `equals()`, `hashCode()`, getters et setters via le menu **Code → Generate** (ou Alt+Inser / Cmd+N). Montrer comment IntelliJ génère du code boilerplate proprement.
> **Expliquer :** Expliquer pourquoi on génère ces méthodes au lieu de les écrire à la main (moins d'erreurs, plus rapide), et ce que fait chacune. Insister sur le fait qu'`equals()` et `hashCode()` doivent toujours être redéfinies ensemble.
---

## 4. this — La référence à l'objet courant

```java
public class Compteur {

    private int valeur;
    private String nom;

    public Compteur(String nom) {
        this.nom = nom;    // this.nom = attribut ; nom = paramètre (ambiguïté résolue)
        this.valeur = 0;
    }

    public Compteur(String nom, int valeurInitiale) {
        this(nom);                    // appelle Compteur(String nom)
        this.valeur = valeurInitiale; // initialisation supplémentaire
    }

    // Retourner this permet le chaînage de méthodes (fluent API)
    public Compteur incrementer() {
        this.valeur++;
        return this;  // retourne l'objet courant
    }

    public Compteur decrementer() {
        this.valeur--;
        return this;
    }

    public Compteur reinitialiser() {
        this.valeur = 0;
        return this;
    }

    public int getValeur() { return valeur; }

    @Override
    public String toString() {
        return nom + " = " + valeur;
    }

    public static void main(String[] args) {
        Compteur c = new Compteur("Score", 0);

        // Chaînage de méthodes grâce à return this
        c.incrementer()
         .incrementer()
         .incrementer()
         .decrementer();

        System.out.println(c);  // "Score = 2"

        // Pattern Builder (vu plus tard) utilise intensivement ce principe
    }
}
```

## 5. static — Membres de classe

```java
public class Banque {

    // --- Attributs statiques (partagés par tous les objets) ---
    private static int nombreClients = 0;         // compteur commun
    private static final double TAUX_INTERET = 0.03;  // constante de classe
    private static String nomBanque = "MaBank";

    // --- Attributs d'instance (propres à chaque objet) ---
    private int id;
    private String titulaire;
    private double solde;

    // --- Constructeur ---
    public Banque(String titulaire, double soldeInitial) {
        nombreClients++;              // incrémente le compteur partagé
        this.id = nombreClients;      // ID unique basé sur le compteur
        this.titulaire = titulaire;
        this.solde = soldeInitial;
    }

    // --- Méthode statique : ne dépend pas d'une instance ---
    public static int getNombreClients() {
        return nombreClients;
    }

    public static String getNomBanque() {
        return nomBanque;
    }

    public static double calculerInterets(double capital, int annees) {
        // Pas de this ici : méthode statique n'a pas accès aux attributs d'instance
        return capital * Math.pow(1 + TAUX_INTERET, annees) - capital;
    }

    // --- Méthode d'instance ---
    public void deposer(double montant) {
        if (montant > 0) {
            solde += montant;
            System.out.printf("Dépôt de %.2f€ — Nouveau solde : %.2f€%n", montant, solde);
        }
    }

    public void retirer(double montant) {
        if (montant > 0 && montant <= solde) {
            solde -= montant;
            System.out.printf("Retrait de %.2f€ — Nouveau solde : %.2f€%n", montant, solde);
        } else {
            System.out.println("Solde insuffisant");
        }
    }

    @Override
    public String toString() {
        return String.format("Compte[%d] %s : %.2f€", id, titulaire, solde);
    }

    public static void main(String[] args) {

        // Méthodes statiques : appelées sur la CLASSE, pas sur un objet
        System.out.println(Banque.getNomBanque());       // "MaBank"
        System.out.println(Banque.getNombreClients());   // 0
        System.out.println(Banque.calculerInterets(1000, 5));  // ~159.27

        // Créer des objets
        Banque c1 = new Banque("Alice", 1000);
        Banque c2 = new Banque("Bob", 500);

        System.out.println(Banque.getNombreClients());  // 2 (compteur mis à jour)

        c1.deposer(200);
        c1.retirer(50);
        c2.retirer(600);  // "Solde insuffisant"

        System.out.println(c1);
        System.out.println(c2);
    }
}
```

## 6. Blocs d'initialisation

```java
public class Initialisation {

    private int x;
    private static int compteur;

    // Bloc d'initialisation statique : exécuté une seule fois au chargement de la classe
    static {
        compteur = 0;
        System.out.println("Classe Initialisation chargée");
    }

    // Bloc d'initialisation d'instance : exécuté avant chaque constructeur
    {
        x = 10;
        System.out.println("Bloc d'instance exécuté");
    }

    public Initialisation() {
        System.out.println("Constructeur sans paramètre, x = " + x);
    }

    public Initialisation(int x) {
        this.x = x;
        System.out.println("Constructeur avec paramètre, x = " + x);
    }

    public static void main(String[] args) {
        System.out.println("Début main");
        Initialisation i1 = new Initialisation();
        // → "Bloc d'instance exécuté"
        // → "Constructeur sans paramètre, x = 10"

        Initialisation i2 = new Initialisation(42);
        // → "Bloc d'instance exécuté"
        // → "Constructeur avec paramètre, x = 42"
    }
}
```

## 7. Encapsulation — Principe fondamental

```java
// Mauvaise conception : tout public
public class MauvaisCompteBancaire {
    public double solde;   // ✗ Accessible et modifiable directement de partout !
}

// Utilisation problématique :
// MauvaisCompteBancaire c = new MauvaisCompteBancaire();
// c.solde = -99999;  // Aucune validation !

// Bonne conception : encapsulation
public class BonCompteBancaire {

    private double solde;       // ✓ Protégé
    private String titulaire;

    public BonCompteBancaire(String titulaire) {
        if (titulaire == null || titulaire.isBlank()) {
            throw new IllegalArgumentException("Le titulaire ne peut pas être vide");
        }
        this.titulaire = titulaire;
        this.solde = 0;
    }

    // Lecture uniquement (pas de setter)
    public double getSolde() {
        return solde;
    }

    public String getTitulaire() {
        return titulaire;
    }

    // Modification uniquement via méthodes qui valident
    public void crediter(double montant) {
        if (montant <= 0) throw new IllegalArgumentException("Montant invalide");
        solde += montant;
    }

    public void debiter(double montant) {
        if (montant <= 0) throw new IllegalArgumentException("Montant invalide");
        if (montant > solde) throw new IllegalStateException("Solde insuffisant");
        solde -= montant;
    }

    @Override
    public String toString() {
        return titulaire + " : " + solde + "€";
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Créer la classe `MauvaisCompteBancaire` avec `public double solde`, puis depuis `main` faire `c.solde = -99999`. Montrer que ça compile. Ensuite créer `BonCompteBancaire` avec encapsulation et essayer de faire la même chose → erreur de compilation.
> **Expliquer :** Insister sur le fait que l'encapsulation protège l'intégrité des données. C'est la base de la conception orientée objet robuste. Montrer le message d'erreur de compilation d'IntelliJ qui dit "solde has private access".
---

## 8. Pattern Builder (bonus)

```java
public class Personne {

    private final String nom;
    private final String prenom;
    private final int age;
    private final String email;
    private final String telephone;

    // Constructeur privé : accessible uniquement via le Builder
    private Personne(Builder builder) {
        this.nom = builder.nom;
        this.prenom = builder.prenom;
        this.age = builder.age;
        this.email = builder.email;
        this.telephone = builder.telephone;
    }

    // Classe Builder imbriquée
    public static class Builder {
        // Champs obligatoires
        private final String nom;
        private final String prenom;

        // Champs optionnels
        private int age = 0;
        private String email = "";
        private String telephone = "";

        public Builder(String nom, String prenom) {
            this.nom = nom;
            this.prenom = prenom;
        }

        public Builder age(int age) {
            this.age = age;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder telephone(String telephone) {
            this.telephone = telephone;
            return this;
        }

        public Personne build() {
            return new Personne(this);
        }
    }

    @Override
    public String toString() {
        return String.format("Personne{nom='%s', prenom='%s', age=%d, email='%s'}",
                nom, prenom, age, email);
    }

    public static void main(String[] args) {

        // Utilisation du builder : lisible, flexible
        Personne alice = new Personne.Builder("Dupont", "Alice")
                .age(30)
                .email("alice@example.com")
                .telephone("0601020304")
                .build();

        Personne bob = new Personne.Builder("Martin", "Bob")
                .age(25)
                .build();  // email et telephone non renseignés

        System.out.println(alice);
        System.out.println(bob);
    }
}
```

## Récapitulatif

| Concept | À retenir |
|---------|-----------|
| Classe | Plan de construction d'objets |
| Objet | Instance d'une classe, créé avec `new` |
| Attribut | Donnée d'un objet (préférer `private`) |
| Constructeur | Méthode spéciale appelée à la création |
| `this` | Référence à l'objet courant |
| `static` | Appartient à la classe, pas aux instances |
| Getter/Setter | Accès contrôlé aux attributs privés |
| `toString()` | Représentation textuelle de l'objet |
| `equals()` | Comparaison par contenu (pas `==`) |
| Encapsulation | `private` + getters/setters avec validation |
