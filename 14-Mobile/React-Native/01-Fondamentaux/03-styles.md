# 03 — Styles, Flexbox et Responsive en React Native

## StyleSheet — le système de styles

React Native n'utilise pas CSS mais un sous-ensemble des propriétés CSS, exprimé en objets JavaScript. `StyleSheet.create()` est le moyen recommandé pour définir ses styles.

```jsx
import { StyleSheet, View, Text } from 'react-native';

// Définir les styles en dehors du composant (bonne pratique)
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  titre: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
  },
});

// Utilisation
export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.titre}>Mon titre</Text>
    </View>
  );
}
```

**Pourquoi StyleSheet.create() ?**
- Valide les propriétés (erreur en dev si nom de propriété invalide)
- Optimisation : les objets de style sont envoyés au thread natif une seule fois et référencés par ID ensuite
- Meilleure lisibilité

### Styles inline (à utiliser avec parcimonie)

```jsx
<View style={{ backgroundColor: 'red', padding: 10 }}>
  <Text style={{ color: '#fff', fontSize: 16 }}>Inline style</Text>
</View>
```

### Combinaison de styles (tableau)

```jsx
const styles = StyleSheet.create({
  base: {
    padding: 16,
    borderRadius: 8,
  },
  primaire: {
    backgroundColor: '#007AFF',
  },
  danger: {
    backgroundColor: '#FF3B30',
  },
  desactive: {
    opacity: 0.5,
  },
});

// Combiner : le dernier style gagne en cas de conflit
<View style={[styles.base, styles.primaire]} />
<View style={[styles.base, styles.danger, estDesactive && styles.desactive]} />
```

---

## Propriétés de style disponibles

### Typographie

```javascript
const typographie = StyleSheet.create({
  exemple: {
    fontSize: 16,           // taille (en dp, pas en px)
    fontWeight: 'bold',     // '100' à '900', 'normal', 'bold'
    fontStyle: 'italic',    // 'normal', 'italic'
    color: '#333',          // hex, rgb, rgba, named
    textAlign: 'center',    // 'left', 'right', 'center', 'justify'
    textDecorationLine: 'underline', // 'none', 'underline', 'line-through'
    letterSpacing: 1,       // espacement entre lettres
    lineHeight: 24,         // hauteur de ligne (en dp)
    textTransform: 'uppercase', // 'none', 'uppercase', 'lowercase', 'capitalize'
    fontFamily: 'Roboto',   // si la police est chargée
  },
});
```

### Dimensions et espacements

```javascript
const espacements = StyleSheet.create({
  exemple: {
    // Marges externes
    margin: 16,
    marginTop: 8,
    marginBottom: 8,
    marginLeft: 16,
    marginRight: 16,
    marginHorizontal: 16, // marginLeft + marginRight
    marginVertical: 8,    // marginTop + marginBottom

    // Padding interne
    padding: 16,
    paddingTop: 8,
    paddingBottom: 8,
    paddingLeft: 16,
    paddingRight: 16,
    paddingHorizontal: 16,
    paddingVertical: 8,

    // Dimensions
    width: 200,
    height: 100,
    minWidth: 50,
    maxWidth: 400,
    minHeight: 50,
    maxHeight: 300,

    // Pourcentages (string)
    width: '100%',
    width: '50%',
  },
});
```

### Couleurs et arrière-plan

```javascript
const couleurs = StyleSheet.create({
  exemple: {
    // Fond
    backgroundColor: '#fff',
    backgroundColor: 'transparent',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',

    // Opacité de tout le composant
    opacity: 0.8,

    // Bordures
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderLeftWidth: 0,
    borderRightWidth: 0,
    borderTopLeftRadius: 8,
    borderTopRightRadius: 8,
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,

    // Ombre iOS
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,

    // Ombre Android
    elevation: 4,
  },
});
```

---

## Flexbox dans React Native

React Native utilise Flexbox pour tout le layout — **et c'est le seul système de mise en page** (pas de float, pas de position relative avec left/top seuls, pas de grid natif). La bonne nouvelle : si vous connaissez flexbox CSS, c'est presque identique, avec quelques différences.

### Différences clés vs CSS Flexbox

| Propriété | CSS | React Native |
|-----------|-----|--------------|
| `flexDirection` | `'row'` par défaut | `'column'` par défaut |
| `alignContent` | `'stretch'` | `'flex-start'` |
| `flexShrink` | `1` par défaut | `0` par défaut |

**Le plus important : `flexDirection` est `'column'` par défaut en RN** (les enfants s'empilent verticalement).

### Propriétés du parent (container)

```jsx
import { View, Text, StyleSheet } from 'react-native';

// flex: 1 — prendre tout l'espace disponible
export function LayoutBase() {
  return (
    <View style={{ flex: 1, backgroundColor: '#f0f0f0' }}>
      <View style={{ flex: 1, backgroundColor: '#ff9500' }}>
        <Text>Prend 1/3 de l'espace</Text>
      </View>
      <View style={{ flex: 2, backgroundColor: '#007aff' }}>
        <Text>Prend 2/3 de l'espace</Text>
      </View>
    </View>
  );
}

// flexDirection — sens des enfants
export function DirectionExemple() {
  return (
    <View>
      {/* Colonne (défaut) */}
      <View style={styles.containerColonne}>
        <View style={styles.boite} />
        <View style={styles.boite} />
        <View style={styles.boite} />
      </View>

      {/* Ligne */}
      <View style={styles.containerLigne}>
        <View style={styles.boite} />
        <View style={styles.boite} />
        <View style={styles.boite} />
      </View>
    </View>
  );
}

// justifyContent — alignement sur l'axe principal
// (vertical si column, horizontal si row)
export function JustifyExemple() {
  return (
    <View style={{ flex: 1, flexDirection: 'row', justifyContent: 'space-between' }}>
      <View style={styles.boite} />
      <View style={styles.boite} />
      <View style={styles.boite} />
    </View>
  );
  // Autres valeurs : 'flex-start', 'flex-end', 'center',
  // 'space-around', 'space-evenly'
}

// alignItems — alignement sur l'axe croisé
export function AlignExemple() {
  return (
    <View style={{ flex: 1, flexDirection: 'row', alignItems: 'center' }}>
      <View style={{ ...styles.boite, height: 40 }} />
      <View style={{ ...styles.boite, height: 80 }} />
      <View style={{ ...styles.boite, height: 60 }} />
    </View>
  );
  // Autres valeurs : 'flex-start', 'flex-end', 'stretch', 'baseline'
}

// flexWrap — retour à la ligne
export function WrapExemple() {
  return (
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, padding: 8 }}>
      {['React', 'Native', 'Expo', 'TypeScript', 'JavaScript', 'Mobile', 'iOS', 'Android'].map(tag => (
        <View key={tag} style={styles.tag}>
          <Text style={styles.tagTexte}>{tag}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  containerColonne: {
    height: 200,
    backgroundColor: '#e0e0e0',
    padding: 8,
    gap: 8,
  },
  containerLigne: {
    backgroundColor: '#c8e6c9',
    padding: 8,
    flexDirection: 'row',
    gap: 8,
  },
  boite: {
    width: 60,
    height: 60,
    backgroundColor: '#007AFF',
    borderRadius: 4,
  },
  tag: {
    backgroundColor: '#E1F5FE',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#B3E5FC',
  },
  tagTexte: {
    color: '#0277BD',
    fontSize: 13,
    fontWeight: '600',
  },
});
```

### Propriétés de l'enfant

```jsx
// alignSelf — override alignItems du parent pour cet enfant
<View style={{ flexDirection: 'row', alignItems: 'flex-start', height: 100 }}>
  <View style={{ width: 50, height: 50, alignSelf: 'flex-end', backgroundColor: 'red' }} />
  <View style={{ width: 50, height: 50, alignSelf: 'center', backgroundColor: 'green' }} />
  <View style={{ width: 50, height: 50, backgroundColor: 'blue' }} />
</View>

// flexGrow, flexShrink, flexBasis
<View style={{ flexDirection: 'row' }}>
  <View style={{ flexGrow: 1, height: 50, backgroundColor: 'red' }} />   {/* Prend tout l'espace restant */}
  <View style={{ flexBasis: 100, height: 50, backgroundColor: 'blue' }} /> {/* 100dp de base */}
</View>

// position absolute — superposition
<View style={{ position: 'relative', height: 200 }}>
  <View style={{ backgroundColor: '#ddd', flex: 1 }} />
  <View style={{
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: 'red',
    padding: 8,
    borderRadius: 12,
  }}>
    <Text style={{ color: '#fff', fontSize: 12 }}>Badge</Text>
  </View>
</View>
```

---

## Mise en page complète — exemples pratiques

### Layout d'écran standard

```jsx
import { SafeAreaView, View, Text, StyleSheet, StatusBar } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// Pattern avec SafeAreaView — gérer le notch iOS et la barre d'état Android
export default function EcranStandard() {
  return (
    <SafeAreaView style={styles.safeArea}>
      {/* En-tête */}
      <View style={styles.entete}>
        <Text style={styles.titrePage}>Mes articles</Text>
        <TouchableOpacity style={styles.boutonAction}>
          <Text style={styles.boutonTexte}>+ Nouveau</Text>
        </TouchableOpacity>
      </View>

      {/* Contenu scrollable */}
      <FlatList
        data={articles}
        renderItem={renderArticle}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.liste}
      />

      {/* Barre du bas fixe */}
      <View style={styles.barreBasFixe}>
        <Text style={styles.barreTexte}>3 articles en attente</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  entete: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  titrePage: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  boutonAction: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  boutonTexte: {
    color: '#fff',
    fontWeight: '600',
  },
  liste: {
    padding: 16,
    gap: 12,
  },
  barreBasFixe: {
    padding: 16,
    backgroundColor: '#f8f8f8',
    borderTopWidth: 1,
    borderTopColor: '#eee',
    alignItems: 'center',
  },
  barreTexte: {
    color: '#666',
    fontSize: 14,
  },
});
```

### Carte avec image et contenu

```jsx
const CarteArticle = ({ article }) => (
  <TouchableOpacity style={styles.carte}>
    <Image
      source={{ uri: article.image }}
      style={styles.carteImage}
      resizeMode="cover"
    />
    <View style={styles.carteContenu}>
      <View style={styles.carteCategorie}>
        <Text style={styles.carteCategorieTexte}>{article.categorie}</Text>
      </View>
      <Text style={styles.carteTitre} numberOfLines={2}>{article.titre}</Text>
      <Text style={styles.carteExtrait} numberOfLines={3}>{article.extrait}</Text>
      <View style={styles.carteMeta}>
        <Image source={{ uri: article.auteur.avatar }} style={styles.auteurAvatar} />
        <View>
          <Text style={styles.auteurNom}>{article.auteur.nom}</Text>
          <Text style={styles.carteDate}>{article.date}</Text>
        </View>
        <View style={styles.carteDuree}>
          <Text style={styles.carteDureeTexte}>{article.duree} min</Text>
        </View>
      </View>
    </View>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  carte: {
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  carteImage: {
    width: '100%',
    height: 180,
  },
  carteContenu: {
    padding: 16,
  },
  carteCategorie: {
    backgroundColor: '#EBF5FB',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 8,
  },
  carteCategorieTexte: {
    color: '#007AFF',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  carteTitre: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    lineHeight: 24,
    marginBottom: 8,
  },
  carteExtrait: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  carteMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  auteurAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
  },
  auteurNom: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
  },
  carteDate: {
    fontSize: 12,
    color: '#999',
  },
  carteDuree: {
    marginLeft: 'auto',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  carteDureeTexte: {
    fontSize: 12,
    color: '#666',
  },
});
```

---

## Dimensions et unités

React Native utilise des **density-independent pixels (dp)** — pas des pixels physiques. Cela garantit une taille visuelle cohérente sur tous les écrans.

```javascript
// Sur un iPhone 12 (scale 3x) : 1dp = 3px physiques
// Sur un iPhone 8 (scale 2x) : 1dp = 2px physiques

// Obtenir les dimensions de l'écran
import { Dimensions, useWindowDimensions } from 'react-native';

// Version statique (ne se met pas à jour si l'orientation change)
const { width, height } = Dimensions.get('window');

// Version dynamique (hook) — préférer celle-ci
export function MonComposant() {
  const { width, height, fontScale } = useWindowDimensions();

  return (
    <View style={{ width: width * 0.8 }}> {/* 80% de la largeur */}
      <Text style={{ fontSize: 16 * fontScale }}> {/* Respect accessibilité */}
        Texte adaptatif
      </Text>
    </View>
  );
}
```

**Pourcentages dans les styles :**
```javascript
// Les % fonctionnent pour width et height
style={{ width: '100%', height: '50%' }}

// Mais pas pour padding/margin → utiliser Dimensions ou useSafeAreaInsets
```

---

## Platform.OS — Styles spécifiques par plateforme

```javascript
import { Platform, StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    // ou
    paddingTop: Platform.select({
      ios: 50,
      android: 30,
      default: 20, // web, etc.
    }),
  },

  ombre: {
    // Ombre iOS
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    // Ombre Android
    elevation: 4,
  },
});

// Dans le JSX
export function ExemplePlatform() {
  return (
    <View style={styles.container}>
      {Platform.OS === 'ios' && (
        <Text>Ceci ne s'affiche que sur iOS</Text>
      )}
      {Platform.OS === 'android' && (
        <Text>Ceci ne s'affiche que sur Android</Text>
      )}
      <Text>
        Version : {Platform.Version}
      </Text>
      <Text>
        {Platform.select({
          ios: 'iPhone/iPad',
          android: 'Appareil Android',
          default: 'Autre plateforme',
        })}
      </Text>
    </View>
  );
}
```

**Fichiers spécifiques par plateforme :**

React Native résout automatiquement les fichiers avec suffixe de plateforme :
```
MonComposant.ios.tsx    → utilisé sur iOS
MonComposant.android.tsx → utilisé sur Android
MonComposant.tsx        → fallback
```

---

## Responsive Design — s'adapter aux tailles d'écran

```javascript
import { useWindowDimensions, StyleSheet, View, Text } from 'react-native';

// Hook utilitaire pour le responsive
function useResponsive() {
  const { width } = useWindowDimensions();
  return {
    isSmall: width < 380,
    isMedium: width >= 380 && width < 768,
    isLarge: width >= 768,      // tablettes
    isTablet: width >= 768,
    colonnes: width < 600 ? 1 : width < 900 ? 2 : 3,
  };
}

// Grille responsive
export function GrilleResponsive({ items }) {
  const { colonnes, isTablet } = useResponsive();
  const { width } = useWindowDimensions();

  const PADDING = 16;
  const GAP = 12;
  const largeurItem = (width - PADDING * 2 - GAP * (colonnes - 1)) / colonnes;

  return (
    <View style={styles.grille}>
      {items.map(item => (
        <View
          key={item.id}
          style={[styles.grilleItem, { width: largeurItem }]}
        >
          <Text>{item.nom}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  grille: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  grilleItem: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    aspectRatio: 1, // Carré
  },
});
```

---

## SafeAreaView et gestion du notch

```jsx
import { SafeAreaView, SafeAreaProvider } from 'react-native-safe-area-context';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// Dans app.json, s'assurer que expo-status-bar est configuré

// Option 1 : SafeAreaView (simple)
export function EcranSimple() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }}>
      <Text>Contenu sans chevauchement avec le notch</Text>
    </SafeAreaView>
  );
}

// Option 2 : useSafeAreaInsets (plus de contrôle)
export function EcranAvecInsets() {
  const insets = useSafeAreaInsets();

  return (
    <View
      style={{
        flex: 1,
        paddingTop: insets.top,
        paddingBottom: insets.bottom,
        paddingLeft: insets.left,
        paddingRight: insets.right,
      }}
    >
      <Text>Contenu avec insets manuels</Text>
    </View>
  );
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Côte à côte simulateur iPhone (avec notch) et simulateur Android — montrer la même application avec et sans SafeAreaView. Montrer le texte qui se cache derrière le notch sans SafeAreaView.
> **Expliquer :** Le notch (encoche) de l'iPhone et la barre de statut Android occupent un espace physique. SafeAreaView décale automatiquement le contenu pour éviter ces zones. Montrer aussi le comportement en paysage (landscape) où les insets changent.
---

## Thèmes — Dark Mode

```javascript
import { useColorScheme, StyleSheet } from 'react-native';

// Palette de thèmes
const Themes = {
  light: {
    fond: '#ffffff',
    surface: '#f5f5f5',
    texte: '#1a1a1a',
    texteMuted: '#666666',
    primaire: '#007AFF',
    bordure: '#e0e0e0',
  },
  dark: {
    fond: '#000000',
    surface: '#1c1c1e',
    texte: '#ffffff',
    texteMuted: '#aeaeb2',
    primaire: '#0A84FF',
    bordure: '#38383A',
  },
};

// Hook personnalisé
export function useTheme() {
  const colorScheme = useColorScheme(); // 'light' | 'dark' | null
  return Themes[colorScheme ?? 'light'];
}

// Utilisation dans un composant
export function MonComposantTheme() {
  const theme = useTheme();

  return (
    <View style={{ flex: 1, backgroundColor: theme.fond }}>
      <Text style={{ color: theme.texte, fontSize: 18 }}>
        Titre
      </Text>
      <Text style={{ color: theme.texteMuted }}>
        Sous-titre
      </Text>
    </View>
  );
}
```

---

## Fonts personnalisées avec Expo

```bash
npx expo install expo-font @expo-google-fonts/inter
```

```jsx
import { useFonts, Inter_400Regular, Inter_700Bold } from '@expo-google-fonts/inter';
import { Text, View } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect, useCallback } from 'react';

SplashScreen.preventAutoHideAsync();

export default function App() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_700Bold,
  });

  const onLayoutRootView = useCallback(async () => {
    if (fontsLoaded) {
      await SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) {
    return null;
  }

  return (
    <View onLayout={onLayoutRootView}>
      <Text style={{ fontFamily: 'Inter_400Regular', fontSize: 16 }}>
        Texte en Inter Regular
      </Text>
      <Text style={{ fontFamily: 'Inter_700Bold', fontSize: 20 }}>
        Texte en Inter Bold
      </Text>
    </View>
  );
}
```

---

## Animations de base avec Animated

```jsx
import React, { useRef, useEffect } from 'react';
import { Animated, TouchableOpacity, Text, StyleSheet } from 'react-native';

export function BoutonAnime() {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;

  // Animation d'apparition au montage
  useEffect(() => {
    Animated.timing(opacityAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true, // TOUJOURS mettre true si possible
    }).start();
  }, []);

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.95,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      friction: 3,
      useNativeDriver: true,
    }).start();
  };

  return (
    <Animated.View
      style={[
        styles.bouton,
        {
          opacity: opacityAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        style={styles.boutonInterne}
      >
        <Text style={styles.texte}>Bouton animé</Text>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  bouton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  boutonInterne: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 32,
    alignItems: 'center',
  },
  texte: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
});
```

**Règle d'or des animations : toujours utiliser `useNativeDriver: true`** pour les animations de `transform` et `opacity`. Cela fait tourner l'animation sur le thread natif et évite les saccades.

---

## Points clés à retenir

1. `StyleSheet.create()` pour définir les styles — jamais de CSS texte
2. Flexbox est le **seul** système de layout — `flexDirection: 'column'` par défaut
3. Unités en **dp** (density-independent pixels), pas en px
4. `Platform.OS` et `Platform.select()` pour les différences iOS/Android
5. `useWindowDimensions()` pour le responsive (se met à jour à l'orientation)
6. `SafeAreaView` ou `useSafeAreaInsets` pour gérer le notch
7. `shadowColor/shadowOffset/shadowOpacity/shadowRadius` pour iOS, `elevation` pour Android
8. Animations : toujours `useNativeDriver: true` pour les performances
