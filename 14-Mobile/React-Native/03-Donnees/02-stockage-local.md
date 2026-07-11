# 02 — Stockage local : AsyncStorage, MMKV, SecureStore et SQLite

## Pourquoi stocker des données localement ?

Le stockage local est indispensable pour :
- **Persister les préférences** utilisateur (thème, langue, notifications...)
- **Mettre en cache** des données pour le mode hors-ligne
- **Stocker les tokens** d'authentification de manière sécurisée
- **Sauvegarder les données** d'une session (formulaires, panier...)
- **Bases de données embarquées** pour des applications riches hors-ligne

| Solution | Usage | Chiffrement | Synchrone | Taille max |
|----------|-------|-------------|-----------|------------|
| AsyncStorage | Clé-valeur simple | Non | Non (async) | ~6 MB iOS |
| MMKV | Clé-valeur rapide | Optionnel | Oui | Large |
| SecureStore (Expo) | Tokens sensibles | Oui (Keychain/Keystore) | Non | ~2 KB/valeur |
| SQLite | Données relationnelles | Via SQLCipher | Non | Illimité |

---

## AsyncStorage

AsyncStorage est la solution la plus simple pour stocker des données clé-valeur. C'est l'équivalent de `localStorage` mais **asynchrone**.

```bash
npx expo install @react-native-async-storage/async-storage
```

### API de base

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Stocker une valeur
await AsyncStorage.setItem('cle', 'valeur');

// Lire une valeur
const valeur = await AsyncStorage.getItem('cle');
// Retourne null si la clé n'existe pas

// Supprimer une clé
await AsyncStorage.removeItem('cle');

// Supprimer plusieurs clés
await AsyncStorage.multiRemove(['cle1', 'cle2']);

// Tout supprimer (ATTENTION : dangereux)
await AsyncStorage.clear();

// Lister toutes les clés
const cles = await AsyncStorage.getAllKeys();

// Stocker plusieurs valeurs en une fois
await AsyncStorage.multiSet([
  ['cle1', 'valeur1'],
  ['cle2', 'valeur2'],
]);

// Lire plusieurs valeurs
const paires = await AsyncStorage.multiGet(['cle1', 'cle2']);
// [['cle1', 'valeur1'], ['cle2', 'valeur2']]
```

### Stocker des objets (JSON)

AsyncStorage ne stocke que des **strings**. Pour les objets, il faut sérialiser/désérialiser :

```typescript
// Utilitaires de sérialisation
export const storage = {
  async set(cle: string, valeur: unknown): Promise<void> {
    const json = JSON.stringify(valeur);
    await AsyncStorage.setItem(cle, json);
  },

  async get<T>(cle: string): Promise<T | null> {
    const json = await AsyncStorage.getItem(cle);
    if (json === null) return null;
    return JSON.parse(json) as T;
  },

  async remove(cle: string): Promise<void> {
    await AsyncStorage.removeItem(cle);
  },
};

// Utilisation
interface Preferences {
  theme: 'light' | 'dark';
  langue: string;
  notificationsActivees: boolean;
}

// Sauvegarder
await storage.set('preferences', {
  theme: 'dark',
  langue: 'fr',
  notificationsActivees: true,
});

// Lire
const prefs = await storage.get<Preferences>('preferences');
console.log(prefs?.theme); // 'dark'
```

### Hook useAsyncStorage

```typescript
// hooks/useAsyncStorage.ts
import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export function useAsyncStorage<T>(
  cle: string,
  valeurDefaut: T
): [T, (valeur: T) => Promise<void>, boolean] {
  const [valeur, setValeur] = useState<T>(valeurDefaut);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    const charger = async () => {
      try {
        const json = await AsyncStorage.getItem(cle);
        if (json !== null) {
          setValeur(JSON.parse(json));
        }
      } catch (e) {
        console.error('Erreur lecture AsyncStorage:', e);
      } finally {
        setChargement(false);
      }
    };
    charger();
  }, [cle]);

  const sauvegarder = useCallback(async (nouvelleValeur: T) => {
    try {
      setValeur(nouvelleValeur);
      await AsyncStorage.setItem(cle, JSON.stringify(nouvelleValeur));
    } catch (e) {
      console.error('Erreur écriture AsyncStorage:', e);
    }
  }, [cle]);

  return [valeur, sauvegarder, chargement];
}

// Utilisation
export default function PreferencesScreen() {
  const [theme, setTheme, chargement] = useAsyncStorage<'light' | 'dark'>(
    'theme',
    'light'
  );

  if (chargement) return <ActivityIndicator />;

  return (
    <View>
      <Switch
        value={theme === 'dark'}
        onValueChange={(dark) => setTheme(dark ? 'dark' : 'light')}
      />
    </View>
  );
}
```

### Exemple complet — Todo list persistante

```tsx
// screens/TodoScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  FlatList, StyleSheet, Alert
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const CLE_TODOS = '@todos_v1';

interface Todo {
  id: string;
  texte: string;
  complete: boolean;
  creeLe: string;
}

export default function TodoScreen() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [nouveau, setNouveau] = useState('');
  const [chargement, setChargement] = useState(true);

  // Charger les todos au démarrage
  useEffect(() => {
    const charger = async () => {
      try {
        const json = await AsyncStorage.getItem(CLE_TODOS);
        if (json) {
          setTodos(JSON.parse(json));
        }
      } catch (e) {
        console.error('Erreur chargement:', e);
      } finally {
        setChargement(false);
      }
    };
    charger();
  }, []);

  // Sauvegarder à chaque modification
  const sauvegarder = async (nouveauxTodos: Todo[]) => {
    try {
      await AsyncStorage.setItem(CLE_TODOS, JSON.stringify(nouveauxTodos));
    } catch (e) {
      console.error('Erreur sauvegarde:', e);
    }
  };

  const ajouter = () => {
    if (!nouveau.trim()) return;

    const todo: Todo = {
      id: Date.now().toString(),
      texte: nouveau.trim(),
      complete: false,
      creeLe: new Date().toISOString(),
    };

    const nouvelleListе = [todo, ...todos];
    setTodos(nouvelleListе);
    sauvegarder(nouvelleListе);
    setNouveau('');
  };

  const basculer = (id: string) => {
    const mis = todos.map(t =>
      t.id === id ? { ...t, complete: !t.complete } : t
    );
    setTodos(mis);
    sauvegarder(mis);
  };

  const supprimer = (id: string) => {
    Alert.alert('Supprimer', 'Supprimer cette tâche ?', [
      { text: 'Annuler' },
      {
        text: 'Supprimer',
        style: 'destructive',
        onPress: () => {
          const filtres = todos.filter(t => t.id !== id);
          setTodos(filtres);
          sauvegarder(filtres);
        },
      },
    ]);
  };

  const restants = todos.filter(t => !t.complete).length;

  return (
    <View style={styles.container}>
      <View style={styles.entete}>
        <Text style={styles.titre}>Mes Tâches</Text>
        <Text style={styles.compteur}>{restants} restante(s)</Text>
      </View>

      <View style={styles.saisie}>
        <TextInput
          style={styles.input}
          value={nouveau}
          onChangeText={setNouveau}
          placeholder="Nouvelle tâche..."
          returnKeyType="done"
          onSubmitEditing={ajouter}
        />
        <TouchableOpacity style={styles.boutonAjouter} onPress={ajouter}>
          <Text style={styles.boutonTexte}>+</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={todos}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.todo, item.complete && styles.todoComplete]}
            onPress={() => basculer(item.id)}
            onLongPress={() => supprimer(item.id)}
          >
            <View style={[styles.coche, item.complete && styles.cocheComplete]}>
              {item.complete && <Text style={styles.cocheTexte}>✓</Text>}
            </View>
            <Text style={[styles.todoTexte, item.complete && styles.todoTexteComplete]}>
              {item.texte}
            </Text>
          </TouchableOpacity>
        )}
        contentContainerStyle={styles.liste}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  entete: {
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  titre: { fontSize: 24, fontWeight: 'bold' },
  compteur: { fontSize: 14, color: '#666' },
  saisie: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  boutonAjouter: {
    backgroundColor: '#007AFF',
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  boutonTexte: { color: '#fff', fontSize: 28, lineHeight: 32 },
  liste: { paddingHorizontal: 16, gap: 8 },
  todo: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  todoComplete: { opacity: 0.6 },
  coche: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cocheComplete: { backgroundColor: '#34C759', borderColor: '#34C759' },
  cocheTexte: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  todoTexte: { flex: 1, fontSize: 16, color: '#1a1a1a' },
  todoTexteComplete: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
});
```

---

## Expo SecureStore — Stockage sécurisé

SecureStore utilise le **Keychain iOS** et le **Keystore Android** pour stocker des valeurs de manière chiffrée. À utiliser impérativement pour les tokens d'authentification.

```bash
npx expo install expo-secure-store
```

```typescript
import * as SecureStore from 'expo-secure-store';

// Stocker un token
await SecureStore.setItemAsync('authToken', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

// Lire le token
const token = await SecureStore.getItemAsync('authToken');

// Supprimer
await SecureStore.deleteItemAsync('authToken');

// Options avancées
await SecureStore.setItemAsync('cle', 'valeur', {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  // Valeurs disponibles :
  // WHEN_UNLOCKED — accessible quand le device est déverrouillé
  // AFTER_FIRST_UNLOCK — accessible après le premier déverrouillage (pour les background tasks)
  // WHEN_UNLOCKED_THIS_DEVICE_ONLY — ne migre pas si l'utilisateur change de device
  // AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY
});
```

### Gestionnaire d'authentification

```typescript
// services/authStorage.ts
import * as SecureStore from 'expo-secure-store';

const CLES = {
  TOKEN: 'auth_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  USER_ID: 'user_id',
} as const;

export const authStorage = {
  async sauvegarderTokens(token: string, refreshToken: string, userId: string): Promise<void> {
    await Promise.all([
      SecureStore.setItemAsync(CLES.TOKEN, token),
      SecureStore.setItemAsync(CLES.REFRESH_TOKEN, refreshToken),
      SecureStore.setItemAsync(CLES.USER_ID, userId),
    ]);
  },

  async getToken(): Promise<string | null> {
    return SecureStore.getItemAsync(CLES.TOKEN);
  },

  async getRefreshToken(): Promise<string | null> {
    return SecureStore.getItemAsync(CLES.REFRESH_TOKEN);
  },

  async getUserId(): Promise<string | null> {
    return SecureStore.getItemAsync(CLES.USER_ID);
  },

  async supprimer(): Promise<void> {
    await Promise.all([
      SecureStore.deleteItemAsync(CLES.TOKEN),
      SecureStore.deleteItemAsync(CLES.REFRESH_TOKEN),
      SecureStore.deleteItemAsync(CLES.USER_ID),
    ]);
  },

  async estAuthentifie(): Promise<boolean> {
    const token = await SecureStore.getItemAsync(CLES.TOKEN);
    return token !== null;
  },
};
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Expo Go sur device, montrer une application qui stocke un token — quitter l'app complètement, relancer, montrer que le token est toujours présent (l'utilisateur reste connecté). Montrer ensuite la différence avec AsyncStorage pour une donnée non sensible.
> **Expliquer :** La différence entre AsyncStorage (fichier non chiffré, visible sur device rooté) et SecureStore (Keychain iOS / Keystore Android, chiffré par le OS). Pour les tokens d'authentification, SecureStore est obligatoire pour une app en production. AsyncStorage est suffisant pour les préférences UI (thème, langue...).
---

## MMKV — Storage ultra-rapide

MMKV est une solution de stockage clé-valeur 10x plus rapide qu'AsyncStorage, développée par WeChat. Elle supporte le stockage synchrone.

```bash
npx expo install react-native-mmkv
```

**Note :** MMKV nécessite un **Development Build** Expo (pas compatible avec Expo Go).

```typescript
import { MMKV } from 'react-native-mmkv';

// Instance par défaut
export const storage = new MMKV();

// Instance avec chiffrement
export const storageChiffre = new MMKV({
  id: 'user-storage',
  encryptionKey: 'ma-cle-chiffrement',
});

// API synchrone !
storage.set('utilisateur.id', 42);
storage.set('utilisateur.nom', 'Alice');
storage.set('settings.darkMode', true);
storage.set('cache.donnees', JSON.stringify({ key: 'value' }));

const id = storage.getNumber('utilisateur.id');   // 42
const nom = storage.getString('utilisateur.nom');  // 'Alice'
const dark = storage.getBoolean('settings.darkMode'); // true

storage.delete('utilisateur.id');

// Vérifier l'existence
const existe = storage.contains('utilisateur.nom'); // true

// Lister les clés
const cles = storage.getAllKeys();

// Avec Zustand (store persistant ultra-simple)
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const zustandStorage = {
  setItem: (name: string, value: string) => storage.set(name, value),
  getItem: (name: string) => storage.getString(name) ?? null,
  removeItem: (name: string) => storage.delete(name),
};

interface SettingsStore {
  theme: 'light' | 'dark';
  langue: string;
  setTheme: (t: 'light' | 'dark') => void;
  setLangue: (l: string) => void;
}

export const useSettings = create<SettingsStore>()(
  persist(
    (set) => ({
      theme: 'light',
      langue: 'fr',
      setTheme: (theme) => set({ theme }),
      setLangue: (langue) => set({ langue }),
    }),
    {
      name: 'settings',
      storage: createJSONStorage(() => zustandStorage),
    }
  )
);
```

---

## SQLite — Base de données relationnelle embarquée

Pour les données structurées et les requêtes complexes.

```bash
npx expo install expo-sqlite
```

### Configuration et migrations

```typescript
// database/db.ts
import * as SQLite from 'expo-sqlite';

// Ouvrir (ou créer) la base de données
const db = SQLite.openDatabaseSync('myapp.db');

// Initialiser le schéma
export async function initialiserDB(): Promise<void> {
  await db.execAsync(`
    PRAGMA journal_mode = WAL;
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS articles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      titre TEXT NOT NULL,
      contenu TEXT NOT NULL,
      categorie TEXT DEFAULT 'general',
      favori INTEGER DEFAULT 0,
      cree_le TEXT NOT NULL,
      mis_a_jour TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_articles_categorie
    ON articles(categorie);

    CREATE TABLE IF NOT EXISTS tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nom TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS articles_tags (
      article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
      tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
      PRIMARY KEY (article_id, tag_id)
    );
  `);
}

export default db;
```

### Repository pattern

```typescript
// repositories/articlesRepository.ts
import db from '../database/db';

export interface Article {
  id: number;
  titre: string;
  contenu: string;
  categorie: string;
  favori: boolean;
  creeLe: string;
  misAJour: string;
}

export interface CreateArticleDTO {
  titre: string;
  contenu: string;
  categorie?: string;
}

export const articlesRepo = {
  // Lister tous les articles
  async lister(categorie?: string): Promise<Article[]> {
    if (categorie) {
      const rows = await db.getAllAsync<any>(
        'SELECT * FROM articles WHERE categorie = ? ORDER BY cree_le DESC',
        [categorie]
      );
      return rows.map(rowToArticle);
    }

    const rows = await db.getAllAsync<any>(
      'SELECT * FROM articles ORDER BY cree_le DESC'
    );
    return rows.map(rowToArticle);
  },

  // Obtenir un article par ID
  async getById(id: number): Promise<Article | null> {
    const row = await db.getFirstAsync<any>(
      'SELECT * FROM articles WHERE id = ?',
      [id]
    );
    return row ? rowToArticle(row) : null;
  },

  // Rechercher
  async rechercher(terme: string): Promise<Article[]> {
    const rows = await db.getAllAsync<any>(
      `SELECT * FROM articles
       WHERE titre LIKE ? OR contenu LIKE ?
       ORDER BY cree_le DESC`,
      [`%${terme}%`, `%${terme}%`]
    );
    return rows.map(rowToArticle);
  },

  // Créer
  async creer(data: CreateArticleDTO): Promise<Article> {
    const maintenant = new Date().toISOString();
    const result = await db.runAsync(
      `INSERT INTO articles (titre, contenu, categorie, cree_le, mis_a_jour)
       VALUES (?, ?, ?, ?, ?)`,
      [data.titre, data.contenu, data.categorie ?? 'general', maintenant, maintenant]
    );

    const article = await articlesRepo.getById(result.lastInsertRowId);
    if (!article) throw new Error('Erreur lors de la création');
    return article;
  },

  // Modifier
  async modifier(id: number, data: Partial<CreateArticleDTO>): Promise<void> {
    const champs = Object.keys(data).map(k => `${k} = ?`).join(', ');
    const valeurs = [...Object.values(data), new Date().toISOString(), id];
    await db.runAsync(
      `UPDATE articles SET ${champs}, mis_a_jour = ? WHERE id = ?`,
      valeurs
    );
  },

  // Basculer favori
  async toggleFavori(id: number): Promise<void> {
    await db.runAsync(
      'UPDATE articles SET favori = NOT favori, mis_a_jour = ? WHERE id = ?',
      [new Date().toISOString(), id]
    );
  },

  // Supprimer
  async supprimer(id: number): Promise<void> {
    await db.runAsync('DELETE FROM articles WHERE id = ?', [id]);
  },

  // Compter
  async compter(): Promise<number> {
    const result = await db.getFirstAsync<{ count: number }>(
      'SELECT COUNT(*) as count FROM articles'
    );
    return result?.count ?? 0;
  },
};

// Convertir une ligne SQLite en objet Article
function rowToArticle(row: any): Article {
  return {
    id: row.id,
    titre: row.titre,
    contenu: row.contenu,
    categorie: row.categorie,
    favori: Boolean(row.favori),
    creeLe: row.cree_le,
    misAJour: row.mis_a_jour,
  };
}
```

### Utilisation dans un composant avec useSQLiteContext

```tsx
// App.tsx — envelopper avec SQLiteProvider
import { SQLiteProvider } from 'expo-sqlite';
import { initialiserDB } from './database/db';

export default function App() {
  return (
    <SQLiteProvider databaseName="myapp.db" onInit={initialiserDB}>
      <NavigationContainer>
        <RootNavigator />
      </NavigationContainer>
    </SQLiteProvider>
  );
}

// Dans un composant
import { useSQLiteContext } from 'expo-sqlite';

export default function ArticlesList() {
  const db = useSQLiteContext();
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    const charger = async () => {
      const rows = await db.getAllAsync<Article>(
        'SELECT * FROM articles ORDER BY cree_le DESC'
      );
      setArticles(rows);
    };
    charger();
  }, []);

  return <FlatList data={articles} ... />;
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Utiliser un outil comme DB Browser for SQLite pour ouvrir le fichier `.db` exporté depuis le simulateur iOS (accessible via Finder → ~/Library/Developer/CoreSimulator/...) — montrer les tables, les données insertées par l'app
> **Expliquer :** Le fichier SQLite est un fichier standard que vous pouvez inspecter avec n'importe quel outil SQLite. Montrer où il se trouve sur iOS (sandbox de l'app) et Android (via adb shell). Expliquer l'importance des migrations de schéma quand on publie une mise à jour (pragma user_version, création conditionnelle des tables).
---

## Résumé — Choisir son stockage

```
Besoin de stocker :
├── Token JWT / Mot de passe → SecureStore (Expo)
├── Préférences simples (thème, langue) → AsyncStorage ou MMKV
├── Cache de données API → MMKV (synchrone, rapide)
├── Données structurées complexes → SQLite (expo-sqlite)
└── State global persistant → Zustand + MMKV ou AsyncStorage
```

**Règles à retenir :**
1. **SecureStore** pour tout ce qui est sensible (tokens, identifiants)
2. **AsyncStorage** : simple mais lent (asynchrone) — éviter pour des lectures fréquentes
3. **MMKV** : le meilleur rapport simplicité/performance pour les préférences et le cache
4. **SQLite** : pour les relations, les requêtes complexes, les grands volumes de données
5. Ne jamais stocker de données sensibles dans AsyncStorage (non chiffré)
6. Préfixer les clés AsyncStorage/MMKV avec le nom de l'app : `@monapp/preference_theme`
