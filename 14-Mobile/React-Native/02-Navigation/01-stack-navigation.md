# 01 — React Navigation v6 — Stack Navigator

## Pourquoi React Navigation ?

React Native ne fournit pas de système de navigation intégré. React Navigation est la solution de référence de la communauté, utilisée dans la quasi-totalité des projets.

**Alternatives :**
- **Expo Router** (basé sur React Navigation) — routage basé sur le système de fichiers, similaire à Next.js
- **React Native Navigation** (Wix) — navigation 100% native, plus performante mais plus complexe

Pour cette formation, on utilise **React Navigation v6** directement, ce qui donne une compréhension solide des concepts.

---

## Installation

```bash
# Dépendances de base
npm install @react-navigation/native

# Dépendances natives requises
npx expo install react-native-screens react-native-safe-area-context

# Stack Navigator
npm install @react-navigation/native-stack
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant l'installation des packages, puis l'application avec le stack navigator opérationnel — montrer la transition entre deux écrans avec l'animation native iOS (slide depuis la droite)
> **Expliquer :** React Navigation utilise des composants natifs réels pour les transitions (via `react-native-screens`). Sur iOS, le glissement depuis le bord gauche fonctionne automatiquement (gesture de retour). Sur Android, le bouton Back physique est géré automatiquement.
---

## Configuration de base — NavigationContainer

Le `NavigationContainer` doit envelopper toute l'application. Il gère l'état de navigation global.

```jsx
// App.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { RootStackNavigator } from './navigation/RootStackNavigator';

export default function App() {
  return (
    <NavigationContainer>
      <RootStackNavigator />
    </NavigationContainer>
  );
}
```

---

## Stack Navigator — Navigation empilée

Le Stack Navigator fonctionne comme une pile de cartes. Naviguer vers un écran l'empile par-dessus. Revenir en arrière le dépile.

```
[Accueil] → [Liste] → [Détail] → [Formulaire]
                ↑                      ↑
           navigation.goBack()    navigation.popToTop()
```

### Structure de base

```tsx
// navigation/RootStackNavigator.tsx
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import AccueilScreen from '../screens/AccueilScreen';
import ListeScreen from '../screens/ListeScreen';
import DetailScreen from '../screens/DetailScreen';

// Typage des routes et paramètres — TypeScript
export type RootStackParamList = {
  Accueil: undefined;             // Pas de paramètres
  Liste: { categorie: string };   // Un paramètre requis
  Detail: { articleId: number; titre: string }; // Deux paramètres
  Profil: { userId: string } | undefined; // Paramètres optionnels
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootStackNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Accueil"
      screenOptions={{
        headerShown: true,
        headerStyle: {
          backgroundColor: '#fff',
        },
        headerTintColor: '#007AFF',
        headerTitleStyle: {
          fontWeight: 'bold',
          color: '#1a1a1a',
        },
        animation: 'slide_from_right', // iOS par défaut
      }}
    >
      <Stack.Screen
        name="Accueil"
        component={AccueilScreen}
        options={{ title: 'Mes Articles' }}
      />
      <Stack.Screen
        name="Liste"
        component={ListeScreen}
        options={({ route }) => ({ title: route.params.categorie })}
      />
      <Stack.Screen
        name="Detail"
        component={DetailScreen}
        options={({ route }) => ({ title: route.params.titre })}
      />
    </Stack.Navigator>
  );
}
```

---

## Les props navigation et route

Chaque écran dans un Stack reçoit automatiquement deux props :

### navigation

```tsx
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/RootStackNavigator';

type AccueilNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Accueil'>;

interface Props {
  navigation: AccueilNavigationProp;
}

export default function AccueilScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Écran d'accueil</Text>

      {/* navigate — aller à un écran */}
      <TouchableOpacity
        style={styles.bouton}
        onPress={() => navigation.navigate('Liste', { categorie: 'Tech' })}
      >
        <Text style={styles.boutonTexte}>Voir les articles Tech</Text>
      </TouchableOpacity>

      {/* push — empiler même si déjà dans la pile */}
      <TouchableOpacity
        onPress={() => navigation.push('Detail', { articleId: 1, titre: 'Mon article' })}
      >
        <Text>Push direct vers Détail</Text>
      </TouchableOpacity>

      {/* goBack — retour arrière */}
      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text>Retour</Text>
      </TouchableOpacity>

      {/* popToTop — retour au premier écran */}
      <TouchableOpacity onPress={() => navigation.popToTop()}>
        <Text>Retour à l'accueil</Text>
      </TouchableOpacity>

      {/* replace — remplacer l'écran courant */}
      <TouchableOpacity onPress={() => navigation.replace('Liste', { categorie: 'Sport' })}>
        <Text>Remplacer par Liste Sport</Text>
      </TouchableOpacity>
    </View>
  );
}
```

### route

```tsx
import { RouteProp } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/RootStackNavigator';

type DetailRouteProp = RouteProp<RootStackParamList, 'Detail'>;

interface Props {
  route: DetailRouteProp;
  navigation: any; // Simplification
}

export default function DetailScreen({ route, navigation }: Props) {
  // Récupérer les paramètres
  const { articleId, titre } = route.params;

  return (
    <View style={styles.container}>
      <Text>Article ID : {articleId}</Text>
      <Text>Titre : {titre}</Text>
    </View>
  );
}
```

### Hook useNavigation et useRoute (sans props)

```tsx
// Pour les composants enfants qui ne sont pas directement des écrans
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/RootStackNavigator';

export function BoutonRetour() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  return (
    <TouchableOpacity onPress={() => navigation.goBack()}>
      <Text>← Retour</Text>
    </TouchableOpacity>
  );
}

export function InfosRoute() {
  const route = useRoute<RouteProp<RootStackParamList, 'Detail'>>();
  return <Text>Article : {route.params.titre}</Text>;
}
```

---

## Passer des données entre écrans

### Passage simple (paramètres de route)

```tsx
// Écran A → navigue vers B avec des données
navigation.navigate('Detail', {
  articleId: 42,
  titre: 'Introduction à React Native',
  // ATTENTION : les params doivent être sérialisables (pas de fonctions, pas de classes)
});

// Écran B → lit les données
const { articleId, titre } = route.params;
```

### Retour avec données (callback)

```tsx
// Écran A — passe un callback (non recommandé par la doc officielle)
// Méthode recommandée : passer par un state global ou navigation.setParams

// Pattern recommandé par React Navigation : setParams
// Écran A
navigation.navigate('Formulaire', { userId: '123' });
// Écouter les retours via focus event
useEffect(() => {
  const unsubscribe = navigation.addListener('focus', () => {
    // L'écran A reprend le focus — recharger les données
    chargerDonnees();
  });
  return unsubscribe;
}, [navigation]);
```

### Partage d'état via Context

```tsx
// contexts/ArticlesContext.tsx
import React, { createContext, useContext, useState } from 'react';

interface ArticlesContextType {
  articleSelectionne: Article | null;
  setArticleSelectionne: (article: Article | null) => void;
}

const ArticlesContext = createContext<ArticlesContextType>({} as ArticlesContextType);

export function ArticlesProvider({ children }: { children: React.ReactNode }) {
  const [articleSelectionne, setArticleSelectionne] = useState<Article | null>(null);

  return (
    <ArticlesContext.Provider value={{ articleSelectionne, setArticleSelectionne }}>
      {children}
    </ArticlesContext.Provider>
  );
}

export const useArticles = () => useContext(ArticlesContext);

// App.tsx
export default function App() {
  return (
    <NavigationContainer>
      <ArticlesProvider>
        <RootStackNavigator />
      </ArticlesProvider>
    </NavigationContainer>
  );
}
```

---

## Configuration des headers

### Header statique

```tsx
<Stack.Screen
  name="Detail"
  component={DetailScreen}
  options={{
    title: 'Détail de l\'article',
    headerStyle: { backgroundColor: '#1a1a2e' },
    headerTintColor: '#fff',
    headerTitleStyle: { fontWeight: 'bold', fontSize: 18 },
    headerBackTitle: 'Retour',  // iOS seulement
    headerBackVisible: true,
    headerShadowVisible: false, // Supprimer la ligne sous le header
  }}
/>
```

### Header dynamique (en fonction de la route)

```tsx
<Stack.Screen
  name="Detail"
  component={DetailScreen}
  options={({ route }) => ({
    title: route.params.titre,
    headerRight: () => (
      <TouchableOpacity onPress={() => Alert.alert('Partagé !')}>
        <Text style={{ color: '#007AFF' }}>Partager</Text>
      </TouchableOpacity>
    ),
  })}
/>
```

### Modifier le header depuis le composant

```tsx
// Dans le composant, modifier les options du header
export default function DetailScreen({ navigation, route }) {
  const [aime, setAime] = useState(false);

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity onPress={() => setAime(v => !v)}>
          <Text style={{ fontSize: 20 }}>{aime ? '❤️' : '🤍'}</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation, aime]); // Recréer quand aime change

  return (
    <View>
      <Text>{route.params.titre}</Text>
    </View>
  );
}
```

### Header personnalisé complet

```tsx
import { getHeaderTitle } from '@react-navigation/elements';

function HeaderPersonnalise({ navigation, route, options, back }) {
  const titre = getHeaderTitle(options, route.name);

  return (
    <SafeAreaView style={styles.header}>
      <View style={styles.headerInterne}>
        {back ? (
          <TouchableOpacity onPress={navigation.goBack} style={styles.boutonRetour}>
            <Text style={styles.retourTexte}>← {back.title || 'Retour'}</Text>
          </TouchableOpacity>
        ) : (
          <View style={{ width: 80 }} />
        )}
        <Text style={styles.headerTitre} numberOfLines={1}>{titre}</Text>
        <View style={{ width: 80 }} />
      </View>
    </SafeAreaView>
  );
}

// Utilisation
<Stack.Navigator
  screenOptions={{
    header: (props) => <HeaderPersonnalise {...props} />,
  }}
>
```

---

## Animations de transition

```tsx
import { TransitionPresets } from '@react-navigation/stack';
// Note : TransitionPresets est dans @react-navigation/stack (non-native)
// Pour @react-navigation/native-stack, utiliser animation

// native-stack — animations disponibles
<Stack.Screen
  name="Modal"
  component={ModalScreen}
  options={{
    animation: 'slide_from_bottom', // Modal style
    presentation: 'modal',           // Présentation modale
  }}
/>

<Stack.Screen
  name="Detail"
  component={DetailScreen}
  options={{
    animation: 'fade',
  }}
/>

// Animations disponibles pour native-stack :
// 'default', 'fade', 'flip', 'simple_push',
// 'slide_from_bottom', 'slide_from_right', 'slide_from_left',
// 'none'
```

---

## Exemple complet — Application avec authentification

```tsx
// navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../hooks/useAuth';

// Navigateurs
import { AuthStackNavigator } from './AuthStackNavigator';
import { MainTabNavigator } from './MainTabNavigator';
import SplashScreen from '../screens/SplashScreen';

const RootStack = createNativeStackNavigator();

export function AppNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          // Utilisateur connecté → Application principale
          <RootStack.Screen name="Main" component={MainTabNavigator} />
        ) : (
          // Non connecté → Authentification
          <RootStack.Screen
            name="Auth"
            component={AuthStackNavigator}
            options={{ animation: 'fade' }}
          />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
}

// navigation/AuthStackNavigator.tsx
export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: { email?: string };
};

const AuthStack = createNativeStackNavigator<AuthStackParamList>();

export function AuthStackNavigator() {
  return (
    <AuthStack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="Register" component={RegisterScreen} />
      <AuthStack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
    </AuthStack.Navigator>
  );
}
```

---

## Écouter les événements de navigation

```tsx
import { useFocusEffect, useIsFocused } from '@react-navigation/native';
import { useCallback } from 'react';

export default function ListeScreen({ navigation }) {
  // Exécuter du code quand l'écran prend le focus (après un goBack)
  useFocusEffect(
    useCallback(() => {
      console.log('L\'écran Liste a le focus');
      chargerDonnees();

      return () => {
        console.log('L\'écran Liste perd le focus');
        // Nettoyage si nécessaire
      };
    }, [])
  );

  // Savoir si l'écran est actif (pour les timers, animations...)
  const isFocused = useIsFocused();

  // Écouter les événements de navigation
  useEffect(() => {
    const unsubscribeBlur = navigation.addListener('blur', () => {
      console.log('Écran caché');
    });

    const unsubscribeFocus = navigation.addListener('focus', () => {
      console.log('Écran visible');
    });

    const unsubscribeBeforeRemove = navigation.addListener('beforeRemove', (e) => {
      // Empêcher la navigation (ex : formulaire non sauvegardé)
      e.preventDefault();
      Alert.alert(
        'Quitter ?',
        'Vos modifications non sauvegardées seront perdues.',
        [
          { text: 'Rester', onPress: () => {} },
          { text: 'Quitter', onPress: () => navigation.dispatch(e.data.action) },
        ]
      );
    });

    return () => {
      unsubscribeBlur();
      unsubscribeFocus();
      unsubscribeBeforeRemove();
    };
  }, [navigation]);

  return <View><Text>Liste</Text></View>;
}
```

---

## Résumé des méthodes de navigation

| Méthode | Description |
|---------|-------------|
| `navigation.navigate('Nom', params)` | Aller à un écran (ne duplique pas) |
| `navigation.push('Nom', params)` | Empiler un écran (duplique) |
| `navigation.goBack()` | Retour arrière |
| `navigation.popToTop()` | Retour au premier écran de la pile |
| `navigation.replace('Nom', params)` | Remplacer l'écran courant |
| `navigation.reset({ routes })` | Réinitialiser la pile |
| `navigation.setOptions({})` | Modifier les options du header |
| `navigation.setParams({})` | Modifier les paramètres de la route |
| `navigation.canGoBack()` | Vérifier si on peut revenir en arrière |
