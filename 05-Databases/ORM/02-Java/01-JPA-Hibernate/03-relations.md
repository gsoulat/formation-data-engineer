# JPA / Hibernate — Relations entre entités

## @ManyToOne et @OneToMany

La relation la plus courante : une commande appartient à un client, un client a plusieurs commandes.

```java
// Client.java — le côté "un"
@Entity
@Table(name = "clients")
public class Client {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String nom;

    @Column(unique = true, nullable = false)
    private String email;

    // mappedBy indique que Commande.client est le "propriétaire" de la relation
    // cascade : les opérations sur Client se propagent aux Commandes
    @OneToMany(
        mappedBy = "client",
        cascade = CascadeType.ALL,    // persist, merge, remove, refresh, detach
        orphanRemoval = true,         // Supprimer les commandes orphelines
        fetch = FetchType.LAZY        // Chargement lazy (par défaut pour collections)
    )
    private List<Commande> commandes = new ArrayList<>();

    // Méthodes utilitaires pour maintenir les deux côtés de la relation
    public void addCommande(Commande commande) {
        commandes.add(commande);
        commande.setClient(this);  // Maintenir la cohérence bidirectionnelle
    }

    public void removeCommande(Commande commande) {
        commandes.remove(commande);
        commande.setClient(null);
    }

    // Constructeurs, getters, setters
    public Client() {}
    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public List<Commande> getCommandes() { return commandes; }
}
```

```java
// Commande.java — le côté "N" (propriétaire de la relation)
@Entity
@Table(name = "commandes")
public class Commande {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(precision = 10, scale = 2)
    private BigDecimal total;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private StatutCommande statut = StatutCommande.EN_ATTENTE;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    // La FK est ici — Commande est le propriétaire de la relation
    @ManyToOne(
        fetch = FetchType.LAZY,       // Lazy par défaut recommandé
        optional = false              // La commande DOIT avoir un client
    )
    @JoinColumn(name = "client_id", nullable = false)  // Nom de la FK
    private Client client;

    public enum StatutCommande { EN_ATTENTE, CONFIRMEE, EXPEDIEE, LIVREE, ANNULEE }

    @PrePersist
    protected void onCreate() { createdAt = LocalDateTime.now(); }

    public Commande() {}
    public Long getId() { return id; }
    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal total) { this.total = total; }
    public StatutCommande getStatut() { return statut; }
    public void setStatut(StatutCommande statut) { this.statut = statut; }
    public Client getClient() { return client; }
    public void setClient(Client client) { this.client = client; }
}
```

### Utilisation

```java
EntityManager em = emf.createEntityManager();
EntityTransaction tx = em.getTransaction();

try {
    tx.begin();

    Client client = new Client();
    client.setNom("Alice Dupont");
    client.setEmail("alice@example.com");

    Commande cmd1 = new Commande();
    cmd1.setTotal(new BigDecimal("89.99"));
    client.addCommande(cmd1);  // Utiliser la méthode utilitaire

    Commande cmd2 = new Commande();
    cmd2.setTotal(new BigDecimal("149.00"));
    client.addCommande(cmd2);

    em.persist(client);  // Cascade → persiste aussi les commandes
    tx.commit();

    // Charger les commandes d'un client
    Client alice = em.find(Client.class, client.getId());
    // Déclenche un SELECT lazily quand on accède à la collection
    System.out.println("Nombre de commandes: " + alice.getCommandes().size());

} finally {
    em.close();
}
```

## @ManyToMany

Un produit peut avoir plusieurs tags, un tag peut s'appliquer à plusieurs produits.

```java
@Entity
@Table(name = "produits")
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String nom;

    @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinTable(
        name = "produit_tag",          // Table pivot
        joinColumns = @JoinColumn(name = "produit_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id")
    )
    private Set<Tag> tags = new HashSet<>();

    // Méthode utilitaire
    public void addTag(Tag tag) {
        tags.add(tag);
        tag.getProduits().add(this);
    }

    public void removeTag(Tag tag) {
        tags.remove(tag);
        tag.getProduits().remove(this);
    }

    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public Set<Tag> getTags() { return tags; }
}

@Entity
@Table(name = "tags")
public class Tag {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, length = 50)
    private String nom;

    @ManyToMany(mappedBy = "tags")  // Côté inverse
    private Set<Produit> produits = new HashSet<>();

    public Tag() {}
    public Tag(String nom) { this.nom = nom; }

    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public Set<Produit> getProduits() { return produits; }
}
```

## @OneToOne

Un utilisateur a exactement un profil.

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @OneToOne(
        mappedBy = "user",
        cascade = CascadeType.ALL,
        fetch = FetchType.LAZY,
        optional = true  // L'utilisateur peut ne pas avoir de profil
    )
    private UserProfile profile;

    public Long getId() { return id; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public UserProfile getProfile() { return profile; }
    public void setProfile(UserProfile profile) { this.profile = profile; }
}

@Entity
@Table(name = "user_profiles")
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 500)
    private String bio;

    @Column(name = "avatar_url")
    private String avatarUrl;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", unique = true)  // FK unique = OneToOne
    private User user;

    public Long getId() { return id; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
}
```

## FetchType — LAZY vs EAGER

```java
// LAZY (recommandé) — chargé uniquement quand on y accède
@OneToMany(fetch = FetchType.LAZY)   // Défaut pour collections
@ManyToOne(fetch = FetchType.LAZY)   // Recommandé (défaut = EAGER !)

// EAGER — chargé automatiquement avec l'entité parente
@ManyToOne(fetch = FetchType.EAGER)  // DÉFAUT pour @ManyToOne et @OneToOne !
@OneToOne(fetch = FetchType.EAGER)
```

> **Attention** : `@ManyToOne` et `@OneToOne` sont EAGER par défaut. Toujours spécifier `FetchType.LAZY` pour éviter des JOIN non désirés.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** IntelliJ IDEA — activer les logs SQL Hibernate, montrer le N+1 avec EAGER puis la solution avec JOIN FETCH dans JPQL
> **Expliquer :** Charger 10 commandes avec `fetch = FetchType.EAGER` sur `client` → montrer 11 requêtes dans les logs. Puis modifier la requête JPQL avec `JOIN FETCH` → montrer 1 seule requête. Répéter le même exercice que pour SQLAlchemy mais en Java. Le problème N+1 est universel, la solution aussi.

---

## Fetch Join en JPQL

```java
EntityManager em = emf.createEntityManager();

// MAUVAIS : Génère N+1 requêtes si client est LAZY
List<Commande> commandes = em
    .createQuery("SELECT c FROM Commande c", Commande.class)
    .getResultList();
// Pour chaque commande, Hibernate fait: SELECT * FROM clients WHERE id = ?

// BON : JOIN FETCH — une seule requête
List<Commande> commandes = em
    .createQuery(
        "SELECT c FROM Commande c JOIN FETCH c.client",
        Commande.class
    )
    .getResultList();
// → SELECT c.*, cl.* FROM commandes c JOIN clients cl ON c.client_id = cl.id

// Charger aussi les commandes d'un client avec ses lignes
List<Client> clients = em
    .createQuery(
        "SELECT DISTINCT cl FROM Client cl " +
        "JOIN FETCH cl.commandes c " +
        "JOIN FETCH c.lignes",
        Client.class
    )
    .getResultList();
```

## @EntityGraph — alternative aux JOIN FETCH

```java
@Entity
@Table(name = "commandes")
@NamedEntityGraph(
    name = "Commande.avecClient",
    attributeNodes = @NamedAttributeNode("client")
)
public class Commande { /* ... */ }

// Utilisation
EntityGraph<?> graph = em.getEntityGraph("Commande.avecClient");
List<Commande> commandes = em
    .createQuery("SELECT c FROM Commande c", Commande.class)
    .setHint("jakarta.persistence.fetchgraph", graph)
    .getResultList();
```
