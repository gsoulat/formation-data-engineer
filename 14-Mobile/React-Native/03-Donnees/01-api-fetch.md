# 01 — Appels API : fetch, axios et gestion des états

## fetch en React Native

React Native inclut l'API `fetch` nativement (pas besoin de polyfill). Elle fonctionne exactement comme dans un navigateur web.

```typescript
// Appel GET simple
async function chargerArticles() {
  const reponse = await fetch('https://jsonplaceholder.typicode.com/posts');
  const donnees = await reponse.json();
  return donnees;
}

// Appel POST avec body JSON
async function creerArticle(article: { title: string; body: string; userId: number }) {
  const reponse = await fetch('https://jsonplaceholder.typicode.com/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${monToken}`,
    },
    body: JSON.stringify(article),
  });

  if (!reponse.ok) {
    throw new Error(`Erreur HTTP : ${reponse.status}`);
  }

  return reponse.json();
}
```

---

## Pattern de base — useEffect + useState

```tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';

interface Article {
  id: number;
  title: string;
  body: string;
  userId: number;
}

export default function ListeArticlesScreen() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const charger = async () => {
    try {
      setChargement(true);
      setErreur(null);

      const reponse = await fetch('https://jsonplaceholder.typicode.com/posts');

      if (!reponse.ok) {
        throw new Error(`Erreur serveur : ${reponse.status}`);
      }

      const donnees: Article[] = await reponse.json();
      setArticles(donnees);
    } catch (e) {
      setErreur(e instanceof Error ? e.message : 'Une erreur est survenue');
    } finally {
      setChargement(false);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  // État de chargement
  if (chargement) {
    return (
      <View style={styles.centrer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.chargementTexte}>Chargement des articles...</Text>
      </View>
    );
  }

  // État d'erreur
  if (erreur) {
    return (
      <View style={styles.centrer}>
        <Text style={styles.erreurIcone}>⚠️</Text>
        <Text style={styles.erreurTexte}>{erreur}</Text>
        <TouchableOpacity style={styles.boutonReessayer} onPress={charger}>
          <Text style={styles.boutonTexte}>Réessayer</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Données chargées
  return (
    <FlatList
      data={articles}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => (
        <View style={styles.carte}>
          <Text style={styles.carteTitre}>{item.title}</Text>
          <Text style={styles.carteCorps} numberOfLines={2}>{item.body}</Text>
        </View>
      )}
      contentContainerStyle={styles.liste}
    />
  );
}

const styles = StyleSheet.create({
  centrer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    gap: 16,
  },
  chargementTexte: {
    color: '#666',
    fontSize: 16,
    marginTop: 8,
  },
  erreurIcone: {
    fontSize: 48,
  },
  erreurTexte: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
  },
  boutonReessayer: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  boutonTexte: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  liste: {
    padding: 16,
    gap: 12,
  },
  carte: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  carteTitre: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 6,
    textTransform: 'capitalize',
  },
  carteCorps: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});
```

---

## Axios — alternative plus puissante

Axios simplifie les appels API grâce à ses intercepteurs, la gestion automatique des erreurs HTTP, et la transformation des données.

```bash
npm install axios
```

### Configuration d'une instance Axios

```typescript
// api/client.ts
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = __DEV__
  ? 'http://192.168.1.100:8000/api'  // Dev : IP locale (pas localhost !)
  : 'https://mon-api.com/api';       // Production

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10 secondes
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Intercepteur requête — ajouter le token JWT
apiClient.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur réponse — gestion centralisée des erreurs
apiClient.interceptors.response.use(
  (response) => response.data, // Retourner directement les données
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré → déconnexion
      await SecureStore.deleteItemAsync('authToken');
      // Rediriger vers login (via un événement ou store global)
    }

    const message = error.response?.data?.message
      || error.message
      || 'Une erreur est survenue';

    return Promise.reject(new Error(message));
  }
);

export default apiClient;
```

**Note importante :** Sur simulateur/device en développement, `localhost` ne pointe pas vers votre machine — il faut utiliser l'adresse IP LAN de votre ordinateur (ex: `192.168.1.100`).

```bash
# Trouver son IP LAN sur macOS
ipconfig getifaddr en0

# Sur Windows
ipconfig | findstr /i "IPv4"
```

### Services API modulaires

```typescript
// api/articlesService.ts
import apiClient from './client';

export interface Article {
  id: number;
  title: string;
  body: string;
  userId: number;
}

export interface CreateArticleDTO {
  title: string;
  body: string;
}

const articlesService = {
  // GET tous les articles
  async lister(): Promise<Article[]> {
    return apiClient.get('/articles');
  },

  // GET article par ID
  async getById(id: number): Promise<Article> {
    return apiClient.get(`/articles/${id}`);
  },

  // POST créer un article
  async creer(data: CreateArticleDTO): Promise<Article> {
    return apiClient.post('/articles', data);
  },

  // PUT modifier un article
  async modifier(id: number, data: Partial<CreateArticleDTO>): Promise<Article> {
    return apiClient.put(`/articles/${id}`, data);
  },

  // DELETE supprimer un article
  async supprimer(id: number): Promise<void> {
    return apiClient.delete(`/articles/${id}`);
  },
};

export default articlesService;
```

---

## Custom hook — useApi

Centraliser la logique de chargement/erreur dans un hook réutilisable :

```typescript
// hooks/useApi.ts
import { useState, useEffect, useCallback } from 'react';

interface UseApiOptions {
  immediate?: boolean; // Lancer automatiquement au montage (défaut: true)
}

interface UseApiResult<T> {
  data: T | null;
  chargement: boolean;
  erreur: string | null;
  executer: (...args: any[]) => Promise<void>;
  reinitialiser: () => void;
}

export function useApi<T>(
  apiFn: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
): UseApiResult<T> {
  const { immediate = true } = options;

  const [data, setData] = useState<T | null>(null);
  const [chargement, setChargement] = useState(immediate);
  const [erreur, setErreur] = useState<string | null>(null);

  const executer = useCallback(async (...args: any[]) => {
    try {
      setChargement(true);
      setErreur(null);
      const resultat = await apiFn(...args);
      setData(resultat);
    } catch (e) {
      setErreur(e instanceof Error ? e.message : 'Erreur inconnue');
    } finally {
      setChargement(false);
    }
  }, [apiFn]);

  const reinitialiser = useCallback(() => {
    setData(null);
    setErreur(null);
    setChargement(false);
  }, []);

  useEffect(() => {
    if (immediate) {
      executer();
    }
  }, []);

  return { data, chargement, erreur, executer, reinitialiser };
}

// Utilisation du hook
import articlesService from '../api/articlesService';
import { useApi } from '../hooks/useApi';

export default function ArticlesScreen() {
  const {
    data: articles,
    chargement,
    erreur,
    executer: recharger,
  } = useApi(articlesService.lister);

  if (chargement) return <Loading />;
  if (erreur) return <Erreur message={erreur} onRetry={recharger} />;

  return (
    <FlatList
      data={articles ?? []}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => <CarteArticle article={item} />}
      refreshControl={
        <RefreshControl refreshing={chargement} onRefresh={recharger} />
      }
    />
  );
}
```

---

## Chargement paginé (infinite scroll)

```tsx
import React, { useState, useCallback } from 'react';
import { FlatList, ActivityIndicator, View } from 'react-native';
import articlesService from '../api/articlesService';

const PAGE_SIZE = 20;

export default function ListePagineeScreen() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [page, setPage] = useState(1);
  const [chargement, setChargement] = useState(false);
  const [chargementPlus, setChargementPlus] = useState(false);
  const [finAtteinte, setFinAtteinte] = useState(false);

  const chargerInitial = useCallback(async () => {
    setChargement(true);
    try {
      const donnees = await articlesService.lister({ page: 1, limit: PAGE_SIZE });
      setArticles(donnees);
      setPage(2);
      setFinAtteinte(donnees.length < PAGE_SIZE);
    } finally {
      setChargement(false);
    }
  }, []);

  const chargerPlus = useCallback(async () => {
    if (chargementPlus || finAtteinte) return;

    setChargementPlus(true);
    try {
      const donnees = await articlesService.lister({ page, limit: PAGE_SIZE });
      setArticles(prev => [...prev, ...donnees]);
      setPage(prev => prev + 1);
      setFinAtteinte(donnees.length < PAGE_SIZE);
    } finally {
      setChargementPlus(false);
    }
  }, [page, chargementPlus, finAtteinte]);

  const renderPiedDeListe = () => {
    if (!chargementPlus) return null;
    return (
      <View style={{ padding: 20, alignItems: 'center' }}>
        <ActivityIndicator size="small" color="#007AFF" />
      </View>
    );
  };

  return (
    <FlatList
      data={articles}
      keyExtractor={(item) => String(item.id)}
      renderItem={({ item }) => <CarteArticle article={item} />}
      onEndReached={chargerPlus}
      onEndReachedThreshold={0.5} // Déclenche à 50% avant la fin
      ListFooterComponent={renderPiedDeListe}
      refreshControl={
        <RefreshControl
          refreshing={chargement}
          onRefresh={chargerInitial}
        />
      }
    />
  );
}
```

---

## Mutations — POST/PUT/DELETE avec état de soumission

```tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import articlesService from '../api/articlesService';

export default function FormulaireArticleScreen({ navigation }) {
  const [titre, setTitre] = useState('');
  const [contenu, setContenu] = useState('');
  const [soumission, setSoumission] = useState(false);
  const [erreurs, setErreurs] = useState<Record<string, string>>({});

  const valider = (): boolean => {
    const nouvErreurs: Record<string, string> = {};

    if (!titre.trim()) {
      nouvErreurs.titre = 'Le titre est obligatoire';
    } else if (titre.length < 5) {
      nouvErreurs.titre = 'Le titre doit faire au moins 5 caractères';
    }

    if (!contenu.trim()) {
      nouvErreurs.contenu = 'Le contenu est obligatoire';
    } else if (contenu.length < 20) {
      nouvErreurs.contenu = 'Le contenu doit faire au moins 20 caractères';
    }

    setErreurs(nouvErreurs);
    return Object.keys(nouvErreurs).length === 0;
  };

  const soumettre = async () => {
    if (!valider()) return;

    setSoumission(true);
    try {
      await articlesService.creer({ title: titre, body: contenu });
      Alert.alert('Succès', 'Article créé avec succès !', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (e) {
      Alert.alert(
        'Erreur',
        e instanceof Error ? e.message : 'Impossible de créer l\'article'
      );
    } finally {
      setSoumission(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.contenu}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.label}>Titre *</Text>
        <TextInput
          style={[styles.input, erreurs.titre && styles.inputErreur]}
          value={titre}
          onChangeText={(t) => {
            setTitre(t);
            if (erreurs.titre) setErreurs(prev => ({ ...prev, titre: '' }));
          }}
          placeholder="Titre de l'article"
          returnKeyType="next"
        />
        {erreurs.titre && <Text style={styles.erreur}>{erreurs.titre}</Text>}

        <Text style={styles.label}>Contenu *</Text>
        <TextInput
          style={[styles.input, styles.textArea, erreurs.contenu && styles.inputErreur]}
          value={contenu}
          onChangeText={(c) => {
            setContenu(c);
            if (erreurs.contenu) setErreurs(prev => ({ ...prev, contenu: '' }));
          }}
          placeholder="Contenu de l'article..."
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />
        {erreurs.contenu && <Text style={styles.erreur}>{erreurs.contenu}</Text>}

        <TouchableOpacity
          style={[styles.bouton, soumission && styles.boutonDesactive]}
          onPress={soumettre}
          disabled={soumission}
        >
          {soumission ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.boutonTexte}>Publier l'article</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  contenu: {
    padding: 16,
    gap: 6,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 12,
    marginBottom: 4,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
  },
  inputErreur: {
    borderColor: '#FF3B30',
  },
  textArea: {
    height: 140,
    paddingTop: 10,
  },
  erreur: {
    color: '#FF3B30',
    fontSize: 12,
    marginTop: 4,
  },
  bouton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 24,
  },
  boutonDesactive: {
    backgroundColor: '#ccc',
  },
  boutonTexte: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Outil de réseau (Flipper ou Chrome DevTools) montrant les requêtes HTTP sortantes depuis l'application — montrer une requête GET avec ses headers (dont le token JWT), la réponse JSON, et le timing
> **Expliquer :** Sur simulateur Android, on peut utiliser Flipper (outil de débogage officiel React Native) pour inspecter les requêtes réseau exactement comme dans les DevTools navigateur. Sur vrai device, on peut utiliser "React Native Debugger" ou simplement des console.log stratégiques. Montrer aussi comment tester avec Postman/Insomnia en parallèle pour valider que l'API fonctionne avant de déboguer le code React Native.
---

## Annuler une requête (AbortController)

```tsx
import React, { useState, useEffect, useRef } from 'react';

export default function EcranAbortable() {
  const [data, setData] = useState(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Créer un controller pour pouvoir annuler
    abortControllerRef.current = new AbortController();

    const charger = async () => {
      try {
        const reponse = await fetch('https://api.example.com/lent', {
          signal: abortControllerRef.current?.signal,
        });
        const data = await reponse.json();
        setData(data);
      } catch (e) {
        if (e.name === 'AbortError') {
          console.log('Requête annulée (navigation)');
          return; // Ne pas mettre à jour le state après unmount
        }
        console.error('Erreur réseau:', e);
      }
    };

    charger();

    // Cleanup : annuler la requête si le composant est démonté
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  return <View><Text>{JSON.stringify(data)}</Text></View>;
}
```

---

## React Query (TanStack Query) — gestion avancée du cache

Pour les applications complexes, `@tanstack/react-query` simplifie considérablement la gestion des données serveur.

```bash
npm install @tanstack/react-query
```

```tsx
// App.tsx — configuration
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Données fraîches pendant 5 min
      retry: 2,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer>
        <RootNavigator />
      </NavigationContainer>
    </QueryClientProvider>
  );
}

// Dans un composant — useQuery (GET)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export default function ArticlesScreen() {
  const {
    data: articles,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['articles'],
    queryFn: articlesService.lister,
  });

  if (isLoading) return <Loading />;
  if (isError) return <Error message={error.message} onRetry={refetch} />;

  return <FlatList data={articles} ... />;
}

// useMutation (POST/PUT/DELETE)
export default function FormulaireScreen() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: articlesService.creer,
    onSuccess: () => {
      // Invalider le cache pour forcer un rechargement
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      navigation.goBack();
    },
    onError: (error) => {
      Alert.alert('Erreur', error.message);
    },
  });

  const soumettre = () => {
    mutate({ title: titre, body: contenu });
  };

  return (
    <TouchableOpacity onPress={soumettre} disabled={isPending}>
      <Text>{isPending ? 'Envoi...' : 'Publier'}</Text>
    </TouchableOpacity>
  );
}
```

---

## Gestion du mode hors ligne

```typescript
// hooks/useConnectivity.ts
import { useState, useEffect } from 'react';
import NetInfo from '@react-native-community/netinfo';

export function useConnectivity() {
  const [estConnecte, setEstConnecte] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setEstConnecte(state.isConnected ?? false);
    });
    return unsubscribe;
  }, []);

  return estConnecte;
}

// Installation :
// npx expo install @react-native-community/netinfo

// Utilisation dans un composant
export default function AppAvecConnectivite() {
  const estConnecte = useConnectivity();

  if (!estConnecte) {
    return (
      <View style={styles.horsLigne}>
        <Text style={styles.horsLigneTexte}>
          Pas de connexion Internet
        </Text>
        <Text style={styles.horsLigneSousTitre}>
          Vérifiez votre connexion et réessayez
        </Text>
      </View>
    );
  }

  return <ContenuPrincipal />;
}
```

---

## Récapitulatif — Bonnes pratiques

1. Toujours gérer **3 états** : chargement, erreur, données
2. `localhost` ne fonctionne pas sur device/simulateur → utiliser l'**IP LAN**
3. Utiliser `KeyboardAvoidingView` + `behavior="padding"` (iOS) pour les formulaires
4. Annuler les requêtes dans le cleanup de `useEffect` (AbortController)
5. Utiliser des **services séparés** (pas d'appels fetch dans les composants directement)
6. Centraliser la gestion des tokens dans un intercepteur Axios
7. Pour les apps complexes : **React Query** pour le cache et la synchronisation
8. `RefreshControl` dans `FlatList` pour le pull-to-refresh
