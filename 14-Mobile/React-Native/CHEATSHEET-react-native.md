# Cheatsheet React Native

## Démarrage rapide

```bash
# Créer un projet Expo TypeScript
npx create-expo-app mon-app --template blank-typescript
cd mon-app && npx expo start

# Installer un module Expo (toujours avec npx expo install, pas npm)
npx expo install expo-camera expo-location expo-notifications

# Build de test Android (APK)
eas build --profile preview --platform android

# Mise à jour OTA
eas update --branch production --message "Fix bug"
```

---

## Composants essentiels

| Web (React DOM) | React Native | Notes |
|-----------------|--------------|-------|
| `<div>` | `<View>` | Conteneur de base |
| `<p>`, `<h1>`, `<span>` | `<Text>` | Tout texte dans `<Text>` |
| `<img>` | `<Image>` | URI locale ou distante |
| `<input>` | `<TextInput>` | Clavier mobile |
| `<ul>` + scroll | `<FlatList>` | Listes longues virtualisées |
| `<div>` scrollable | `<ScrollView>` | Petites listes seulement |
| `<button>` | `<TouchableOpacity>` ou `<Pressable>` | Réduction d'opacité |
| `<dialog>` | `<Modal>` | Fenêtre modale |

---

## StyleSheet

```javascript
import { StyleSheet, Platform } from 'react-native';

const styles = StyleSheet.create({
  // Flexbox (column par défaut !)
  container: {
    flex: 1,
    flexDirection: 'row',       // 'column' par défaut (≠ CSS)
    justifyContent: 'center',   // axe principal
    alignItems: 'center',       // axe croisé
    flexWrap: 'wrap',
    gap: 8,                     // RN 0.71+
  },

  // Ombres
  ombre: {
    shadowColor: '#000',        // iOS
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,               // Android
  },

  // Plateforme
  bouton: {
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    // ou
    marginTop: Platform.select({ ios: 20, android: 10, default: 15 }),
  },
});

// Combiner des styles
<View style={[styles.base, estActif && styles.actif]} />
```

---

## Hooks essentiels

```javascript
import {
  useWindowDimensions,    // Dimensions réactives (orientation)
  useColorScheme,         // 'light' | 'dark'
  Platform,
} from 'react-native';

// Dimensions réactives
const { width, height, fontScale } = useWindowDimensions();

// Thème
const colorScheme = useColorScheme(); // 'light' | 'dark'

// Navigation
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';
const navigation = useNavigation();
const route = useRoute();
useFocusEffect(useCallback(() => { /* focus */ return () => { /* blur */ }; }, []));

// Safe Area
import { useSafeAreaInsets } from 'react-native-safe-area-context';
const insets = useSafeAreaInsets();
// insets.top, insets.bottom, insets.left, insets.right
```

---

## Navigation

```javascript
// Naviguer
navigation.navigate('NomEcran', { parametre: 'valeur' });
navigation.push('NomEcran', params);
navigation.goBack();
navigation.popToTop();
navigation.replace('NomEcran', params);

// Tabs imbriqués
navigation.navigate('AccueilTab', { screen: 'Detail', params: { id: 42 } });

// Header depuis le composant
navigation.setOptions({ title: 'Nouveau titre', headerRight: () => <Btn /> });

// Modifier les params de la route courante
navigation.setParams({ key: 'newValue' });
```

---

## AsyncStorage

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Écrire (string uniquement — sérialiser les objets)
await AsyncStorage.setItem('cle', JSON.stringify({ key: 'val' }));

// Lire (null si absent)
const json = await AsyncStorage.getItem('cle');
const obj = json ? JSON.parse(json) : null;

// Supprimer
await AsyncStorage.removeItem('cle');

// Multi
await AsyncStorage.multiSet([['k1','v1'], ['k2','v2']]);
const pairs = await AsyncStorage.multiGet(['k1', 'k2']);
```

---

## SecureStore

```javascript
import * as SecureStore from 'expo-secure-store';

await SecureStore.setItemAsync('token', jwtToken);
const token = await SecureStore.getItemAsync('token');
await SecureStore.deleteItemAsync('token');
```

---

## Permissions

```javascript
// Caméra
import { useCameraPermissions } from 'expo-camera';
const [perm, requestPerm] = useCameraPermissions();
// perm.granted, perm.canAskAgain

// Localisation
import * as Location from 'expo-location';
const [perm, requestPerm] = Location.useForegroundPermissions();
const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
const [addr] = await Location.reverseGeocodeAsync({ latitude, longitude });

// Notifications
import * as Notifications from 'expo-notifications';
const { status } = await Notifications.requestPermissionsAsync();

// Ouvrir les Réglages si permission refusée définitivement
import { Linking } from 'react-native';
Linking.openSettings();
```

---

## Notifications locales

```javascript
import * as Notifications from 'expo-notifications';

// Configuration globale (dans App.tsx)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Planifier
await Notifications.scheduleNotificationAsync({
  content: { title: 'Titre', body: 'Corps', data: { id: 42 } },
  trigger: null,                    // immédiat
  // trigger: { seconds: 60 },      // dans 60s
  // trigger: { hour: 9, minute: 0, repeats: true }, // quotidien à 9h
});

// Écouter les taps
Notifications.addNotificationResponseReceivedListener(response => {
  const data = response.notification.request.content.data;
  // Naviguer vers data.screenName...
});
```

---

## fetch / axios patterns

```javascript
// Pattern useEffect standard
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(e => { if (e.name !== 'AbortError') setError(e.message); })
    .finally(() => setLoading(false));
  return () => controller.abort();
}, []);

// IMPORTANT : sur device, pas localhost → IP LAN
const API_URL = __DEV__
  ? 'http://192.168.1.100:8000'
  : 'https://api.monapp.com';
```

---

## FlatList — Props importantes

```jsx
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={({ item, index }) => <ItemComponent item={item} />}
  // Séparateurs et états
  ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
  ListEmptyComponent={() => <Text>Aucun élément</Text>}
  ListHeaderComponent={() => <Text>En-tête</Text>}
  ListFooterComponent={() => <ActivityIndicator />}
  // Pull to refresh
  refreshControl={<RefreshControl refreshing={loading} onRefresh={reload} />}
  // Infinite scroll
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
  // Horizontal
  horizontal
  showsHorizontalScrollIndicator={false}
  // Performance
  initialNumToRender={10}
  removeClippedSubviews
  // Style
  contentContainerStyle={{ padding: 16, gap: 8 }}
/>
```

---

## Keyboard & Formulaires

```jsx
import { KeyboardAvoidingView, Platform, ScrollView } from 'react-native';

<KeyboardAvoidingView
  style={{ flex: 1 }}
  behavior={Platform.OS === 'ios' ? 'padding' : undefined}
>
  <ScrollView keyboardShouldPersistTaps="handled">
    <TextInput
      keyboardType="email-address"
      autoCapitalize="none"
      returnKeyType="next"
      onSubmitEditing={() => passwordRef.current?.focus()}
    />
    <TextInput
      ref={passwordRef}
      secureTextEntry
      returnKeyType="done"
      onSubmitEditing={submitForm}
    />
  </ScrollView>
</KeyboardAvoidingView>
```

---

## Animations rapides

```javascript
import { Animated, useRef, useEffect } from 'react';

// Apparition au montage
const opacity = useRef(new Animated.Value(0)).current;
useEffect(() => {
  Animated.timing(opacity, {
    toValue: 1, duration: 300, useNativeDriver: true,
  }).start();
}, []);

// Animation de rebond
const scale = useRef(new Animated.Value(1)).current;
const onPress = () => {
  Animated.sequence([
    Animated.timing(scale, { toValue: 0.95, duration: 100, useNativeDriver: true }),
    Animated.spring(scale, { toValue: 1, friction: 3, useNativeDriver: true }),
  ]).start();
};

// Toujours useNativeDriver: true pour transform et opacity
<Animated.View style={{ opacity, transform: [{ scale }] }}>
```

---

## EAS Build — Commandes clés

```bash
eas init                                    # Initialiser le projet
eas build --profile preview --platform android  # APK de test
eas build --profile production --platform all   # Build de production
eas submit --platform ios                   # Soumettre à l'App Store
eas submit --platform android              # Soumettre au Play Store
eas update --branch production             # Mise à jour OTA
eas secret:create --name CLE --value val   # Variable secrète
eas build:list                              # Historique des builds
eas credentials                            # Gérer certificats/keystores
```

---

## Checklist Debug

```
Problème commun → Solution
─────────────────────────────────────────────────────────────────
Texte hors de <Text>       → Erreur "Text strings must be rendered within a <Text>"
localhost API ne répond pas → Utiliser l'IP LAN (192.168.x.x)
Image distante vide         → Vérifier que width et height sont définis
FlatList saccadée           → Utiliser keyExtractor, séparer renderItem dans un composant
Shadow invisible Android    → Utiliser elevation (pas shadow*)
Notch qui cache le contenu  → Envelopper dans <SafeAreaView>
Clavier couvre le formulaire → Utiliser KeyboardAvoidingView
Animation saccadée          → Ajouter useNativeDriver: true
Permission refusée iOS      → Rediriger vers Linking.openSettings()
Fast Refresh ne marche pas  → Sauvegarder le fichier, vérifier les erreurs de syntaxe
```

---

## Ressources

| Ressource | URL |
|-----------|-----|
| Docs React Native | https://reactnative.dev |
| Docs Expo | https://docs.expo.dev |
| React Navigation | https://reactnavigation.org |
| Expo SDK API | https://docs.expo.dev/versions/latest/ |
| EAS Build | https://docs.expo.dev/build/introduction/ |
| Open-Meteo (API météo gratuite) | https://open-meteo.com |
| Pravatar (avatars tests) | https://i.pravatar.cc |
| Picsum (images tests) | https://picsum.photos |
| Expo Icons | https://icons.expo.fyi |
| Snack (playground en ligne) | https://snack.expo.dev |
