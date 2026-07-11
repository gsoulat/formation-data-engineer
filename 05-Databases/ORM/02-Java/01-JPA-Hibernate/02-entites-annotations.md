# JPA / Hibernate — Entités et annotations

## Annotations fondamentales

```java
package com.formation.models;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity                          // Obligatoire : déclare une entité JPA
@Table(
    name = "produits",           // Nom de la table (défaut : nom de la classe)
    schema = "public",           // Schéma PostgreSQL
    uniqueConstraints = {
        @UniqueConstraint(name = "uq_produit_sku", columnNames = {"sku"}),
        @UniqueConstraint(name = "uq_produit_nom_cat", columnNames = {"nom", "categorie_id"})
    },
    indexes = {
        @Index(name = "idx_produit_actif", columnList = "actif"),
        @Index(name = "idx_produit_prix", columnList = "prix")
    }
)
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // SERIAL PostgreSQL
    private Long id;

    // Colonne avec contraintes
    @Column(name = "sku", unique = true, length = 50)
    @NotBlank
    private String sku;

    @Column(name = "nom", nullable = false, length = 200)
    @NotBlank
    @Size(max = 200)
    private String nom;

    // Texte long
    @Column(columnDefinition = "TEXT")
    private String description;

    // Décimal précis
    @Column(name = "prix", precision = 10, scale = 2, nullable = false)
    @DecimalMin("0.01")
    private BigDecimal prix;

    // Entier avec valeur par défaut
    @Column(name = "stock")
    @Min(0)
    private int stock = 0;

    // Booléen
    @Column(name = "actif")
    private boolean actif = true;

    // Enum stocké comme String
    @Enumerated(EnumType.STRING)
    @Column(name = "statut", length = 20)
    private StatutProduit statut = StatutProduit.DISPONIBLE;

    // Timestamps automatiques
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // Version pour l'optimistic locking (prévient les conflits concurrents)
    @Version
    private Long version;

    // Enum
    public enum StatutProduit {
        DISPONIBLE, RUPTURE_STOCK, DISCONTINUE
    }

    // Lifecycle callbacks
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    // Constructeurs, getters, setters...
    public Produit() {}

    public Produit(String sku, String nom, BigDecimal prix) {
        this.sku = sku;
        this.nom = nom;
        this.prix = prix;
    }

    // Getters/Setters
    public Long getId() { return id; }
    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public BigDecimal getPrix() { return prix; }
    public void setPrix(BigDecimal prix) { this.prix = prix; }
    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }
    public boolean isActif() { return actif; }
    public void setActif(boolean actif) { this.actif = actif; }
    public StatutProduit getStatut() { return statut; }
    public void setStatut(StatutProduit statut) { this.statut = statut; }

    @Override
    public String toString() {
        return String.format("Produit{id=%d, sku='%s', nom='%s', prix=%s}",
            id, sku, nom, prix);
    }
}
```

## Héritage avec JPA

JPA supporte plusieurs stratégies d'héritage. La plus courante est `SINGLE_TABLE`.

### Stratégie SINGLE_TABLE

Une seule table pour toute la hiérarchie. Colonne discriminante pour différencier les types.

```java
@Entity
@Table(name = "vehicules")
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "type_vehicule", discriminatorType = DiscriminatorType.STRING)
public abstract class Vehicule {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String marque;

    @Column(nullable = false)
    private String modele;

    // Getters/Setters...
}

@Entity
@DiscriminatorValue("VOITURE")
public class Voiture extends Vehicule {
    private int nbPortes;
    // Getters/Setters...
}

@Entity
@DiscriminatorValue("CAMION")
public class Camion extends Vehicule {
    private double chargeMaxTonnes;
    // Getters/Setters...
}
```

```sql
-- Table générée :
-- CREATE TABLE vehicules (
--   id BIGSERIAL PRIMARY KEY,
--   type_vehicule VARCHAR(31),  -- "VOITURE" ou "CAMION"
--   marque VARCHAR(255),
--   modele VARCHAR(255),
--   nb_portes INTEGER,          -- NULL pour les camions
--   charge_max_tonnes DOUBLE,   -- NULL pour les voitures
-- );
```

### Stratégie JOINED

Une table par classe, avec JOIN pour récupérer les données.

```java
@Entity
@Table(name = "animaux")
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Animal {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nom;
}

@Entity
@Table(name = "chiens")
public class Chien extends Animal {
    private String race;
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** DBeaver — montrer la structure des tables générées par SINGLE_TABLE vs JOINED
> **Expliquer :** Ouvrir DBeaver, montrer la table `vehicules` avec toutes les colonnes (y compris celles NULL selon le type), puis la structure JOINED avec deux tables et une FK. Discuter les trade-offs : SINGLE_TABLE = simple mais colonnes nullables ; JOINED = propre mais JOIN à chaque requête.

---

## Attributs transients et formules

```java
@Entity
@Table(name = "commandes")
public class Commande {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "montant_ht", precision = 10, scale = 2)
    private BigDecimal montantHt;

    @Column(name = "taux_tva", precision = 5, scale = 2)
    private BigDecimal tauxTva = new BigDecimal("0.20");

    // Champ calculé côté Java — pas stocké en BDD
    @Transient
    public BigDecimal getMontantTtc() {
        return montantHt.multiply(BigDecimal.ONE.add(tauxTva));
    }

    // Formule calculée côté SQL (Hibernate spécifique)
    @Formula("montant_ht * (1 + taux_tva)")
    private BigDecimal montantTtcCalcule;

    // Getter public
    public Long getId() { return id; }
    public BigDecimal getMontantHt() { return montantHt; }
    public void setMontantHt(BigDecimal montantHt) { this.montantHt = montantHt; }
}
```

## Embedded Objects (valeur composite)

Grouper plusieurs colonnes en un objet Java sans table séparée.

```java
@Embeddable
public class Adresse {
    @Column(name = "rue")
    private String rue;

    @Column(name = "ville", length = 100)
    private String ville;

    @Column(name = "code_postal", length = 10)
    private String codePostal;

    @Column(name = "pays", length = 50)
    private String pays;

    public Adresse() {}
    public Adresse(String rue, String ville, String codePostal, String pays) {
        this.rue = rue;
        this.ville = ville;
        this.codePostal = codePostal;
        this.pays = pays;
    }

    // Getters/Setters
    public String getRue() { return rue; }
    public String getVille() { return ville; }
    public String getCodePostal() { return codePostal; }
    public String getPays() { return pays; }
}

@Entity
@Table(name = "clients")
public class Client {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "nom", nullable = false)
    private String nom;

    // L'adresse est stockée dans la même table (colonnes rue, ville, code_postal, pays)
    @Embedded
    private Adresse adresse;

    // Si deux adresses dans la même entité, utiliser @AttributeOverrides
    @Embedded
    @AttributeOverrides({
        @AttributeOverride(name = "rue", column = @Column(name = "livraison_rue")),
        @AttributeOverride(name = "ville", column = @Column(name = "livraison_ville")),
        @AttributeOverride(name = "codePostal", column = @Column(name = "livraison_cp")),
        @AttributeOverride(name = "pays", column = @Column(name = "livraison_pays")),
    })
    private Adresse adresseLivraison;

    public Client() {}

    public Long getId() { return id; }
    public String getNom() { return nom; }
    public void setNom(String nom) { this.nom = nom; }
    public Adresse getAdresse() { return adresse; }
    public void setAdresse(Adresse adresse) { this.adresse = adresse; }
}
```

## equals() et hashCode() — critique en JPA

Les entités JPA **doivent** implémenter correctement `equals()` et `hashCode()` pour que l'identity map fonctionne correctement.

```java
@Entity
@Table(name = "produits")
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String sku;  // Identifiant métier naturel

    // ... autres champs ...

    // Option 1 : basé sur la clé naturelle (recommandé)
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Produit)) return false;
        Produit produit = (Produit) o;
        return sku != null && sku.equals(produit.sku);
    }

    @Override
    public int hashCode() {
        // Constant hashCode pour les entités avec ID null (nouvelles)
        return getClass().hashCode();
    }

    // Option 2 : basé sur l'ID (simple mais problèmes avec entities new)
    // NE PAS faire : return Objects.hash(id);
    // Car id est null avant persist(), ce qui casse les HashSets/HashMaps
}
```
