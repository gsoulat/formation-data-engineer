# 02 — Bottom Tabs, Drawer et Navigateurs imbriqués

## Installation

```bash
# Bottom Tabs
npm install @react-navigation/bottom-tabs

# Drawer
npm install @react-navigation/drawer
npx expo install react-native-gesture-handler react-native-reanimated
```

**Important pour le Drawer :** Ajouter le plugin Reanimated dans `babel.config.js` :

```javascript
// babel.config.js
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-reanimated/plugin'],
  };
};
```

---

## Bottom Tab Navigator

C'est le pattern de navigation le plus courant dans les applications mobiles (Instagram, Twitter, TikTok...).

```tsx
// navigation/MainTabNavigator.tsx
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StyleSheet, Platform } from 'react-native';

// Écrans
import AccueilScreen from '../screens/AccueilScreen';
import RechercheScreen from '../screens/RechercheScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import ProfilScreen from '../screens/ProfilScreen';

export type MainTabParamList = {
  Accueil: undefined;
  Recherche: undefined;
  Notifications: { count?: number };
  Profil: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

export function MainTabNavigator() {
  return (
    <Tab.Navigator
      initialRouteName="Accueil"
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8e8e93',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopColor: '#e0e0e0',
          borderTopWidth: 1,
          height: Platform.OS === 'ios' ? 88 : 64,
          paddingBottom: Platform.OS === 'ios' ? 28 : 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        headerShown: false, // Les headers sont gérés par les stacks imbriqués
      }}
    >
      <Tab.Screen
        name="Accueil"
        component={AccueilScreen}
        options={{
          tabBarLabel: 'Accueil',
          tabBarIcon: ({ color, size, focused }) => (
            <IconMaison color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Recherche"
        component={RechercheScreen}
        options={{
          tabBarLabel: 'Recherche',
          tabBarIcon: ({ color, size }) => (
            <IconLoupe color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{
          tabBarLabel: 'Notifs',
          tabBarIcon: ({ color, size }) => (
            <IconCloche color={color} size={size} />
          ),
          tabBarBadge: 3, // Badge numérique
        }}
      />
      <Tab.Screen
        name="Profil"
        component={ProfilScreen}
        options={{
          tabBarLabel: 'Profil',
          tabBarIcon: ({ color, size }) => (
            <IconPersonne color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application avec Bottom Tab Navigator — montrer la navigation entre les onglets, le badge de notification, et la différence visuelle iOS vs Android (couleur de la barre, hauteur du padding pour le home indicator iOS)
> **Expliquer :** Sur iOS, la barre d'onglets utilise un blur natif. Sur Android, c'est une surface unie. La hauteur doit être ajustée selon la plateforme (Platform.OS) pour ne pas chevaucher le home indicator de l'iPhone X+. Montrer aussi que l'état des écrans est **préservé** quand on change d'onglet (la liste garde sa position de scroll).
---

### Icônes avec @expo/vector-icons

```bash
# Inclus dans le SDK Expo — pas besoin d'installer
# Import direct
```

```tsx
import { Ionicons, MaterialIcons, FontAwesome5 } from '@expo/vector-icons';

// Utilisation dans tabBarIcon
<Tab.Screen
  name="Accueil"
  component={AccueilScreen}
  options={{
    tabBarIcon: ({ color, size, focused }) => (
      <Ionicons
        name={focused ? 'home' : 'home-outline'}
        size={size}
        color={color}
      />
    ),
  }}
/>

// Autres exemples
// Ionicons : 'search', 'search-outline', 'notifications', 'person'
// MaterialIcons : 'home', 'search', 'notifications', 'person'
// FontAwesome5 : 'home', 'search', 'bell', 'user'
```

### Badge dynamique

```tsx
// Récupérer le nombre de notifications depuis un state global
import { useNotifications } from '../hooks/useNotifications';

export function MainTabNavigator() {
  const { nonLues } = useNotifications();

  return (
    <Tab.Navigator>
      <Tab.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{
          tabBarBadge: nonLues > 0 ? nonLues : undefined,
          tabBarBadgeStyle: {
            backgroundColor: '#FF3B30',
            color: '#fff',
            fontSize: 10,
            minWidth: 18,
            height: 18,
          },
        }}
      />
    </Tab.Navigator>
  );
}
```

### Bouton central personnalisé (style Instagram)

```tsx
import { TouchableOpacity, View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

function BoutonCreer({ onPress }) {
  return (
    <TouchableOpacity style={styles.boutonCreer} onPress={onPress}>
      <Ionicons name="add" size={32} color="#fff" />
    </TouchableOpacity>
  );
}

// Dans le Tab.Navigator
<Tab.Screen
  name="Creer"
  component={CreerScreen}
  options={{
    tabBarLabel: '',
    tabBarIcon: () => null,
    tabBarButton: (props) => (
      <BoutonCreer onPress={props.onPress} />
    ),
  }}
/>

const styles = StyleSheet.create({
  boutonCreer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Platform.OS === 'ios' ? 20 : 0,
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
});
```

---

## Drawer Navigator

Le Drawer est un menu latéral qui se glisse depuis le bord de l'écran. Courant sur Android, moins sur iOS.

```tsx
// navigation/DrawerNavigator.tsx
import React from 'react';
import {
  createDrawerNavigator,
  DrawerContentScrollView,
  DrawerItemList,
  DrawerItem,
} from '@react-navigation/drawer';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const Drawer = createDrawerNavigator();

export function DrawerNavigator() {
  return (
    <Drawer.Navigator
      initialRouteName="Tableau de bord"
      drawerContent={(props) => <DrawerPersonnalise {...props} />}
      screenOptions={{
        drawerActiveTintColor: '#007AFF',
        drawerInactiveTintColor: '#666',
        drawerActiveBackgroundColor: '#EBF5FB',
        drawerStyle: {
          backgroundColor: '#fff',
          width: 280,
        },
        drawerLabelStyle: {
          fontSize: 15,
          fontWeight: '500',
        },
        headerStyle: {
          backgroundColor: '#fff',
        },
        headerTintColor: '#007AFF',
      }}
    >
      <Drawer.Screen
        name="Tableau de bord"
        component={DashboardScreen}
        options={{
          drawerIcon: ({ color, size }) => (
            <Ionicons name="grid-outline" size={size} color={color} />
          ),
        }}
      />
      <Drawer.Screen
        name="Mes Articles"
        component={ArticlesScreen}
        options={{
          drawerIcon: ({ color, size }) => (
            <Ionicons name="document-text-outline" size={size} color={color} />
          ),
        }}
      />
      <Drawer.Screen
        name="Statistiques"
        component={StatsScreen}
        options={{
          drawerIcon: ({ color, size }) => (
            <Ionicons name="bar-chart-outline" size={size} color={color} />
          ),
        }}
      />
      <Drawer.Screen
        name="Paramètres"
        component={ParametresScreen}
        options={{
          drawerIcon: ({ color, size }) => (
            <Ionicons name="settings-outline" size={size} color={color} />
          ),
        }}
      />
    </Drawer.Navigator>
  );
}

// Contenu personnalisé du drawer
function DrawerPersonnalise(props) {
  const { navigation } = props;

  return (
    <DrawerContentScrollView {...props}>
      {/* En-tête du profil */}
      <View style={styles.profil}>
        <Image
          source={{ uri: 'https://i.pravatar.cc/80' }}
          style={styles.avatar}
        />
        <Text style={styles.profilNom}>Marie Dupont</Text>
        <Text style={styles.profilEmail}>marie@example.com</Text>
      </View>

      {/* Items de navigation standard */}
      <DrawerItemList {...props} />

      {/* Séparateur */}
      <View style={styles.separateur} />

      {/* Item personnalisé */}
      <DrawerItem
        label="Aide & Support"
        icon={({ color, size }) => (
          <Ionicons name="help-circle-outline" size={size} color={color} />
        )}
        onPress={() => navigation.navigate('Support')}
      />

      {/* Déconnexion */}
      <DrawerItem
        label="Déconnexion"
        labelStyle={{ color: '#FF3B30' }}
        icon={({ size }) => (
          <Ionicons name="log-out-outline" size={size} color="#FF3B30" />
        )}
        onPress={() => {
          // Logique de déconnexion
          console.log('Déconnexion');
        }}
      />
    </DrawerContentScrollView>
  );
}

const styles = StyleSheet.create({
  profil: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    marginBottom: 8,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    marginBottom: 12,
  },
  profilNom: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  profilEmail: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  separateur: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 16,
    marginVertical: 8,
  },
});
```

### Ouvrir/fermer le drawer depuis un écran

```tsx
// Via les props navigation
export default function DashboardScreen({ navigation }) {
  return (
    <View>
      {/* Ouvrir le drawer */}
      <TouchableOpacity onPress={() => navigation.openDrawer()}>
        <Ionicons name="menu" size={24} color="#333" />
      </TouchableOpacity>

      {/* Fermer le drawer */}
      <TouchableOpacity onPress={() => navigation.closeDrawer()}>
        <Text>Fermer</Text>
      </TouchableOpacity>

      {/* Toggle */}
      <TouchableOpacity onPress={() => navigation.toggleDrawer()}>
        <Text>Toggle</Text>
      </TouchableOpacity>
    </View>
  );
}

// Bouton hamburger dans le header
<Drawer.Screen
  name="Dashboard"
  component={DashboardScreen}
  options={({ navigation }) => ({
    headerLeft: () => (
      <TouchableOpacity
        onPress={() => navigation.toggleDrawer()}
        style={{ marginLeft: 16 }}
      >
        <Ionicons name="menu" size={24} color="#007AFF" />
      </TouchableOpacity>
    ),
  })}
/>
```

---

## Navigateurs imbriqués — la structure complète

La majorité des applications réelles combinent plusieurs navigateurs :

```
NavigationContainer
└── RootStack (Stack)
    ├── Auth (Stack) ← si non connecté
    │   ├── Login
    │   ├── Register
    │   └── ForgotPassword
    └── App (Tabs) ← si connecté
        ├── Accueil (Stack)  ← tab 1
        │   ├── ListeArticles
        │   └── DetailArticle
        ├── Recherche (Screen) ← tab 2
        ├── Notifications (Stack) ← tab 3
        │   ├── ListeNotifications
        │   └── DetailNotification
        └── Profil (Stack) ← tab 4
            ├── MonProfil
            ├── Parametres
            └── EditProfil
```

### Implémentation

```tsx
// navigation/TabAccueilStack.tsx
import { createNativeStackNavigator } from '@react-navigation/native-stack';

export type AccueilStackParamList = {
  ListeArticles: undefined;
  DetailArticle: { id: number; titre: string };
};

const AccueilStack = createNativeStackNavigator<AccueilStackParamList>();

export function TabAccueilStack() {
  return (
    <AccueilStack.Navigator>
      <AccueilStack.Screen
        name="ListeArticles"
        component={ListeArticlesScreen}
        options={{ title: 'Articles' }}
      />
      <AccueilStack.Screen
        name="DetailArticle"
        component={DetailArticleScreen}
        options={({ route }) => ({ title: route.params.titre })}
      />
    </AccueilStack.Navigator>
  );
}

// navigation/MainTabNavigator.tsx
export function MainTabNavigator() {
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen
        name="AccueilTab"
        component={TabAccueilStack}  // ← Stack dans le Tab
        options={{ tabBarLabel: 'Accueil' }}
      />
      <Tab.Screen
        name="Recherche"
        component={RechercheScreen}
        options={{ tabBarLabel: 'Recherche' }}
      />
    </Tab.Navigator>
  );
}
```

### Naviguer entre navigateurs imbriqués

```tsx
// Naviguer vers un écran dans un autre onglet + sous-écran
navigation.navigate('AccueilTab', {
  screen: 'DetailArticle',
  params: { id: 42, titre: 'Mon Article' },
});

// Naviguer vers un écran dans un navigateur imbriqué profond
navigation.navigate('App', {
  screen: 'AccueilTab',
  params: {
    screen: 'DetailArticle',
    params: { id: 42, titre: 'Mon Article' },
  },
});
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application complète avec Tabs + Stack imbriqué — naviguer depuis la liste (tab 1) vers un détail, puis naviguer vers un autre tab, puis revenir au tab 1. Montrer que la position dans la pile (le détail) est **préservée** dans le tab 1.
> **Expliquer :** Chaque Tab maintient son propre historique de navigation indépendamment. Ce comportement est attendu et correspond à ce que l'utilisateur mobile anticipe. Montrer aussi comment Android gère le bouton Back physique dans ce contexte (il revient dans la pile du tab actif, puis change de tab au dernier recours).
---

## Material Top Tabs (onglets en haut, style Android)

```bash
npm install @react-navigation/material-top-tabs react-native-tab-view react-native-pager-view
```

```tsx
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';

const TopTab = createMaterialTopTabNavigator();

export function ArticlesTopTabs() {
  return (
    <TopTab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#666',
        tabBarIndicatorStyle: {
          backgroundColor: '#007AFF',
          height: 2,
        },
        tabBarStyle: {
          backgroundColor: '#fff',
          elevation: 0,
          shadowOpacity: 0,
        },
        tabBarLabelStyle: {
          fontSize: 14,
          fontWeight: '600',
          textTransform: 'none', // Éviter le CAPS forcé Android
        },
        swipeEnabled: true, // Swipe entre onglets
      }}
    >
      <TopTab.Screen name="Tous" component={TousArticlesScreen} />
      <TopTab.Screen name="Tech" component={TechArticlesScreen} />
      <TopTab.Screen name="Design" component={DesignArticlesScreen} />
      <TopTab.Screen name="Business" component={BusinessArticlesScreen} />
    </TopTab.Navigator>
  );
}
```

---

## Modals et overlays

```tsx
// Présentation modale d'un écran
<Stack.Screen
  name="NouvelArticle"
  component={NouvelArticleScreen}
  options={{
    presentation: 'modal',
    animation: 'slide_from_bottom',
    headerStyle: { backgroundColor: '#f8f8f8' },
    headerTitle: 'Nouvel article',
    headerLeft: () => (
      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text style={{ color: '#007AFF' }}>Annuler</Text>
      </TouchableOpacity>
    ),
    headerRight: () => (
      <TouchableOpacity onPress={sauvegarder}>
        <Text style={{ color: '#007AFF', fontWeight: '700' }}>Publier</Text>
      </TouchableOpacity>
    ),
  }}
/>

// Naviguer vers la modal depuis n'importe où
navigation.navigate('NouvelArticle');
```

---

## Deep Links

Les deep links permettent d'ouvrir un écran spécifique depuis une URL externe (`monapp://articles/42`).

```tsx
// App.tsx — configuration du linking
import { LinkingOptions } from '@react-navigation/native';

const linking: LinkingOptions<RootStackParamList> = {
  prefixes: [
    'monapp://',
    'https://monapp.com',
  ],
  config: {
    screens: {
      Auth: {
        screens: {
          Login: 'login',
          Register: 'register',
        },
      },
      App: {
        screens: {
          AccueilTab: {
            screens: {
              ListeArticles: 'articles',
              DetailArticle: 'articles/:id',
            },
          },
          Profil: {
            screens: {
              MonProfil: 'profil',
              Parametres: 'parametres',
            },
          },
        },
      },
    },
  },
};

export default function App() {
  return (
    <NavigationContainer linking={linking}>
      <RootStackNavigator />
    </NavigationContainer>
  );
}

// URLs correspondantes :
// monapp://login → écran Login
// monapp://articles → ListeArticles
// monapp://articles/42 → DetailArticle avec id: "42"
// https://monapp.com/profil → MonProfil
```

---

## Récapitulatif — Choisir son navigateur

| Besoin | Navigateur |
|--------|------------|
| Navigation linéaire (A → B → C) | Stack Navigator |
| Onglets en bas | Bottom Tab Navigator |
| Menu latéral | Drawer Navigator |
| Onglets en haut avec swipe | Material Top Tab Navigator |
| Structure app complète | Stack + Tabs imbriqués |

### Règles d'or

1. Le `NavigationContainer` n'apparaît **qu'une seule fois** à la racine
2. Chaque navigateur peut **contenir des navigateurs** (imbrication)
3. `headerShown: false` dans le Tab/Drawer parent pour éviter les doubles headers
4. Pour naviguer vers un écran dans un tab différent : `navigation.navigate('NomDuTab', { screen: 'NomEcran' })`
5. `useFocusEffect` pour exécuter du code quand l'écran devient visible (retour de navigation)
