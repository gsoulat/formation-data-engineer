# Migrations de base de données — Vue d'ensemble

Une migration est un script versionnée qui modifie le schéma de votre base de données de manière contrôlée et reproductible.

## Pourquoi les migrations sont essentielles

Sans migrations, votre schéma de BDD devient incontrôlable :

```
❌ Sans migrations :
   - "Ça marche chez moi mais pas en production..."
   - Modifications manuelles en prod, pas de traçabilité
   - Impossible de revenir en arrière
   - Synchronisation difficile entre dev/staging/prod
   - Nouvelles colonnes oubliées par certains développeurs

✅ Avec migrations :
   - Schéma versionné dans Git
   - Appliqué identiquement sur tous les environnements
   - Historique des changements
   - Rollback possible
   - Intégration CI/CD
```

## Concepts fondamentaux

### Migration up et down

Chaque migration a deux parties :
- **up** : applique le changement (ajouter une colonne, créer une table...)
- **down** : annule le changement (rollback)

```sql
-- up.sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- down.sql
ALTER TABLE users DROP COLUMN phone;
```

### Table de tracking

Tous les outils de migration maintiennent une table dans la BDD pour savoir quelles migrations ont été appliquées.

| Outil | Table de tracking |
|-------|------------------|
| Alembic | `alembic_version` |
| Diesel | `__diesel_schema_migrations` |
| SeaORM | `seaql_migrations` |
| Flyway (Java) | `flyway_schema_history` |
| Liquibase | `databasechangelog` |
| Django | `django_migrations` |

### Workflow typique

```bash
# 1. Modifier votre modèle (en code)
# 2. Générer la migration
alembic revision --autogenerate -m "add_phone_to_users"

# 3. Vérifier le fichier de migration généré
cat alembic/versions/xxx_add_phone_to_users.py

# 4. Appliquer en développement
alembic upgrade head

# 5. Tester
# 6. Committer dans Git
git add alembic/versions/xxx_add_phone_to_users.py
git commit -m "migration: add phone to users"

# 7. Appliquer en production (dans la CI/CD)
alembic upgrade head
```

## Types d'opérations de migration

### Opérations sûres (backward compatible)
Ces opérations ne cassent pas l'application existante et peuvent être déployées sans downtime.

```sql
-- Ajouter une colonne nullable
ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL;

-- Ajouter un index
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Ajouter une table
CREATE TABLE notifications (...);

-- Ajouter une colonne avec valeur par défaut
ALTER TABLE products ADD COLUMN archived BOOLEAN NOT NULL DEFAULT FALSE;
```

### Opérations dangereuses (breaking changes)
Ces opérations peuvent casser l'application si elles ne sont pas coordonnées avec le déploiement du code.

```sql
-- Supprimer une colonne (l'ancien code peut encore l'utiliser)
ALTER TABLE users DROP COLUMN old_field;

-- Renommer une colonne (casse les requêtes existantes)
ALTER TABLE users RENAME COLUMN phone TO phone_number;

-- Ajouter une contrainte NOT NULL sur une colonne existante
-- (échoue si des données NULL existent)
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

### Migration de données

Parfois on doit transformer les données existantes, pas seulement le schéma.

```sql
-- Exemple : déplacer les données d'une ancienne colonne vers une nouvelle
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Normalisation : créer une table de lookup depuis une colonne textuelle
INSERT INTO categories (nom)
SELECT DISTINCT categorie_texte FROM produits WHERE categorie_texte IS NOT NULL;

UPDATE produits p
SET categorie_id = c.id
FROM categories c
WHERE p.categorie_texte = c.nom;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal + DBeaver — montrer la table de tracking des migrations dans DBeaver et son contenu
> **Expliquer :** Ouvrir DBeaver, naviguer vers la table `alembic_version` (ou `__diesel_schema_migrations`). Montrer la colonne `version_num` et expliquer comment l'outil sait quelles migrations ont été appliquées. Montrer que cette table est dans la même BDD que les données applicatives.

---

## Stratégies de déploiement

### Expand-Contract (recommandé pour zéro downtime)

```
Phase 1 — EXPAND (migration + déploiement code qui supporte les deux)
  → Ajouter la nouvelle colonne (nullable)
  → Déployer le code qui écrit dans les DEUX colonnes

Phase 2 — MIGRATE (remplir les données)
  → Backfill : UPDATE new_col = transform(old_col)

Phase 3 — CONTRACT (supprimer l'ancienne version)
  → Déployer le code qui ne lit plus l'ancienne colonne
  → Supprimer l'ancienne colonne
```

### Bonnes pratiques

```
✅ Toujours versionner les migrations dans Git
✅ Ne jamais modifier une migration déjà appliquée en prod
✅ Tester le down (rollback) avant de déployer
✅ Une migration = un changement logique
✅ Utiliser des transactions dans les migrations SQL
✅ Appliquer les migrations en CI/CD, pas manuellement
✅ Conserver les migrations indéfiniment (historique)

❌ Ne jamais supprimer une migration du dépôt Git
❌ Ne jamais modifier une migration existante déjà appliquée
❌ Ne jamais lancer migrate manuellement en prod sans backup
```

## Outils couverts dans ce cours

| Section | Outil | Langage | ORM associé |
|---------|-------|---------|-------------|
| [Alembic](./Alembic/) | Alembic | Python | SQLAlchemy, SQLModel |
| [Diesel Migrations](./Diesel-Migrations/) | diesel_migrations | Rust | Diesel |
