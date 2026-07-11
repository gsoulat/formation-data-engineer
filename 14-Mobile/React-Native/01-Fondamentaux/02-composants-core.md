# 02 — Composants Core de React Native

React Native fournit un ensemble de composants primitifs qui correspondent à des composants UI natifs sur iOS et Android. Ce chapitre couvre les plus importants.

---

## View — Le conteneur de base

`View` est l'équivalent de `div` en HTML. C'est le bloc de construction fondamental pour créer des mises en page.

```jsx
import { View, Text, StyleSheet } from 'react-native';

// View simple
export default function ExempleView() {
  return (
    <View style={styles.container}>
      <View style={styles.boite}>
        <Text>Contenu de la boîte</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  boite: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3, // Android
  },
});
```

**Props importantes de View :**
- `style` — objet de style ou tableau de styles
- `onLayout` — callback appelé quand les dimensions changent
- `accessible` — pour l'accessibilité
- `testID` — pour les tests automatisés
- `pointerEvents` — contrôle la gestion des événements tactiles (`'none'`, `'box-none'`, `'box-only'`, `'auto'`)

---

## Text — Tout ce qui est textuel

**Règle absolue : tout texte affiché DOIT être dans un composant `<Text>`**. Mettre du texte directement dans une `View` provoque une erreur en production.

```jsx
import { Text, StyleSheet } from 'react-native';

export default function ExempleText() {
  const nom = "Alice";
  const score = 42;

  return (
    <>
      {/* Texte simple */}
      <Text>Bonjour !</Text>

      {/* Interpolation */}
      <Text>Bonjour {nom}, votre score est {score}</Text>

      {/* Styles */}
      <Text style={styles.titre}>Titre principal</Text>
      <Text style={styles.sous_titre}>Sous-titre</Text>

      {/* Texte imbriqué — pour styles inline */}
      <Text style={styles.paragraphe}>
        Ce texte est normal,{' '}
        <Text style={styles.gras}>celui-ci est en gras</Text>,{' '}
        <Text style={styles.italique}>celui-là en italique</Text>.
      </Text>

      {/* Limiter le nombre de lignes */}
      <Text numberOfLines={2} ellipsizeMode="tail">
        Ce texte très long sera tronqué après deux lignes avec des points de suspension à la fin de la deuxième ligne.
      </Text>

      {/* Texte sélectionnable */}
      <Text selectable>Ce texte peut être copié par l'utilisateur</Text>
    </>
  );
}

const styles = StyleSheet.create({
  titre: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  sous_titre: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  paragraphe: {
    fontSize: 16,
    lineHeight: 24,
    color: '#444',
  },
  gras: {
    fontWeight: 'bold',
  },
  italique: {
    fontStyle: 'italic',
  },
});
```

**Props importantes de Text :**
- `numberOfLines` — nombre max de lignes avant troncature
- `ellipsizeMode` — `'head'`, `'middle'`, `'tail'`, `'clip'`
- `selectable` — permet la sélection/copie
- `onPress` — gestionnaire de tap (transforme le texte en lien cliquable)
- `adjustsFontSizeToFit` — réduit la police pour tenir dans l'espace

---

## Image — Afficher des images

```jsx
import { Image, StyleSheet, View, Text } from 'react-native';

export default function ExempleImage() {
  return (
    <View style={styles.container}>

      {/* Image locale (depuis assets) */}
      <Image
        source={require('../assets/images/logo.png')}
        style={styles.imageLogo}
      />

      {/* Image distante (depuis URL) */}
      <Image
        source={{ uri: 'https://picsum.photos/300/200' }}
        style={styles.imageDistante}
        // Pour les images distantes, les dimensions sont OBLIGATOIRES
      />

      {/* Image avec placeholder et gestion d'erreur */}
      <Image
        source={{ uri: 'https://example.com/avatar.jpg' }}
        style={styles.avatar}
        defaultSource={require('../assets/images/avatar-placeholder.png')}
        onError={(e) => console.log('Erreur image:', e.nativeEvent.error)}
        onLoad={() => console.log('Image chargée')}
      />

      {/* resizeMode */}
      <Image
        source={{ uri: 'https://picsum.photos/600/200' }}
        style={styles.banniereContain}
        resizeMode="contain"
      />

      <Image
        source={{ uri: 'https://picsum.photos/600/200' }}
        style={styles.banniereCover}
        resizeMode="cover"
      />

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 16,
  },
  imageLogo: {
    width: 100,
    height: 100,
  },
  imageDistante: {
    width: 300,
    height: 200,
    borderRadius: 8,
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30, // Cercle parfait si width === height
  },
  banniereContain: {
    width: '100%',
    height: 100,
    backgroundColor: '#eee',
  },
  banniereCover: {
    width: '100%',
    height: 100,
  },
});
```

**resizeMode — valeurs disponibles :**
| Valeur | Comportement |
|--------|-------------|
| `cover` | Couvre tout l'espace, peut rogner |
| `contain` | L'image entière visible, peut laisser des espaces |
| `stretch` | Étire pour remplir exactement |
| `repeat` | Répète l'image (comme background-repeat) |
| `center` | Centré, taille originale |

**Conseil :** Pour les images d'avatars circulaires, utiliser `borderRadius: width/2`.

---

## TextInput — Champ de saisie

```jsx
import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';

export default function ExempleTextInput() {
  const [nom, setNom] = useState('');
  const [email, setEmail] = useState('');
  const [motDePasse, setMotDePasse] = useState('');
  const [message, setMessage] = useState('');

  return (
    <View style={styles.container}>

      {/* Champ texte simple */}
      <TextInput
        style={styles.input}
        value={nom}
        onChangeText={setNom}
        placeholder="Votre nom"
        placeholderTextColor="#999"
      />

      {/* Email */}
      <TextInput
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        keyboardType="email-address"
        autoCapitalize="none"
        autoCorrect={false}
      />

      {/* Mot de passe */}
      <TextInput
        style={styles.input}
        value={motDePasse}
        onChangeText={setMotDePasse}
        placeholder="Mot de passe"
        secureTextEntry
        autoCapitalize="none"
      />

      {/* Multiline (textarea) */}
      <TextInput
        style={[styles.input, styles.textArea]}
        value={message}
        onChangeText={setMessage}
        placeholder="Votre message..."
        multiline
        numberOfLines={4}
        textAlignVertical="top"
      />

      <Text>Nom saisi : {nom}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  textArea: {
    height: 100,
    paddingTop: 10,
  },
});
```

**Props importantes de TextInput :**
- `keyboardType` : `'default'`, `'numeric'`, `'email-address'`, `'phone-pad'`, `'decimal-pad'`
- `autoCapitalize` : `'none'`, `'sentences'`, `'words'`, `'characters'`
- `returnKeyType` : `'done'`, `'go'`, `'next'`, `'search'`, `'send'`
- `onSubmitEditing` : appelé quand on appuie sur la touche de validation du clavier
- `blurOnSubmit` : ferme le clavier à la validation
- `maxLength` : longueur maximale
- `editable` : `false` pour désactiver

---

## ScrollView — Défilement basique

`ScrollView` rend tout son contenu d'un coup — à utiliser uniquement pour des contenus de taille connue et raisonnablement courte (moins de 50-100 éléments).

```jsx
import { ScrollView, View, Text, StyleSheet } from 'react-native';

export default function ExempleScrollView() {
  return (
    // ScrollView vertical (par défaut)
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.contenu}
      showsVerticalScrollIndicator={false}
      bounces={true} // iOS seulement
    >
      {Array.from({ length: 20 }, (_, i) => (
        <View key={i} style={styles.carte}>
          <Text style={styles.carteTexte}>Carte numéro {i + 1}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

// ScrollView horizontal
export function GalerieHorizontale() {
  const photos = [
    'https://picsum.photos/200/150?random=1',
    'https://picsum.photos/200/150?random=2',
    'https://picsum.photos/200/150?random=3',
    'https://picsum.photos/200/150?random=4',
  ];

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.galerie}
    >
      {photos.map((uri, index) => (
        <Image
          key={index}
          source={{ uri }}
          style={styles.photo}
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flex: 1,
  },
  contenu: {
    padding: 16,
    gap: 8,
  },
  carte: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#eee',
  },
  carteTexte: {
    fontSize: 16,
  },
  galerie: {
    paddingHorizontal: 16,
    gap: 12,
  },
  photo: {
    width: 200,
    height: 150,
    borderRadius: 8,
  },
});
```

**Différence style vs contentContainerStyle :**
- `style` : style de la ScrollView elle-même (le conteneur externe)
- `contentContainerStyle` : style du conteneur interne qui se scroll

---

## FlatList — La liste performante

`FlatList` est conçue pour les listes longues : elle ne rend que les éléments visibles à l'écran (virtualisation). C'est le composant à utiliser pour toute liste dynamique.

```jsx
import React, { useState } from 'react';
import {
  FlatList,
  View,
  Text,
  Image,
  TouchableOpacity,
  RefreshControl,
  StyleSheet,
} from 'react-native';

// Données de démonstration
const UTILISATEURS = Array.from({ length: 50 }, (_, i) => ({
  id: String(i + 1),
  nom: `Utilisateur ${i + 1}`,
  email: `user${i + 1}@example.com`,
  avatar: `https://i.pravatar.cc/60?img=${(i % 70) + 1}`,
}));

interface Utilisateur {
  id: string;
  nom: string;
  email: string;
  avatar: string;
}

// Composant carte — extrait pour éviter les re-renders
const CarteUtilisateur = ({ item, onPress }: { item: Utilisateur; onPress: (u: Utilisateur) => void }) => (
  <TouchableOpacity style={styles.carte} onPress={() => onPress(item)}>
    <Image source={{ uri: item.avatar }} style={styles.avatar} />
    <View style={styles.info}>
      <Text style={styles.nom}>{item.nom}</Text>
      <Text style={styles.email}>{item.email}</Text>
    </View>
  </TouchableOpacity>
);

export default function ListeUtilisateurs() {
  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    // Simuler un rechargement API
    await new Promise(resolve => setTimeout(resolve, 1500));
    setRefreshing(false);
  };

  const renderItem = ({ item }: { item: Utilisateur }) => (
    <CarteUtilisateur
      item={item}
      onPress={(u) => console.log('Sélectionné:', u.nom)}
    />
  );

  const renderSeparateur = () => <View style={styles.separateur} />;

  const renderVide = () => (
    <View style={styles.vide}>
      <Text style={styles.videTexte}>Aucun utilisateur trouvé</Text>
    </View>
  );

  const renderEntete = () => (
    <Text style={styles.entete}>{UTILISATEURS.length} utilisateurs</Text>
  );

  return (
    <FlatList
      data={UTILISATEURS}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      ItemSeparatorComponent={renderSeparateur}
      ListEmptyComponent={renderVide}
      ListHeaderComponent={renderEntete}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      // Optimisations
      initialNumToRender={10}
      maxToRenderPerBatch={10}
      windowSize={5}
      removeClippedSubviews={true}
      // Style
      contentContainerStyle={styles.liste}
    />
  );
}

const styles = StyleSheet.create({
  liste: {
    padding: 16,
  },
  entete: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  carte: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },
  info: {
    flex: 1,
  },
  nom: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  email: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  separateur: {
    height: 8,
  },
  vide: {
    flex: 1,
    alignItems: 'center',
    paddingTop: 64,
  },
  videTexte: {
    fontSize: 16,
    color: '#999',
  },
});
```

**FlatList avec SectionList (groupes) :**

```jsx
import { SectionList, Text, View, StyleSheet } from 'react-native';

const SECTIONS = [
  {
    title: 'Fruits',
    data: ['Pomme', 'Banane', 'Orange', 'Fraise'],
  },
  {
    title: 'Légumes',
    data: ['Carotte', 'Brocoli', 'Épinards', 'Tomate'],
  },
  {
    title: 'Céréales',
    data: ['Riz', 'Blé', 'Avoine', 'Quinoa'],
  },
];

export default function ListeGroups() {
  return (
    <SectionList
      sections={SECTIONS}
      keyExtractor={(item, index) => item + index}
      renderItem={({ item }) => (
        <View style={styles.item}>
          <Text style={styles.itemTexte}>{item}</Text>
        </View>
      )}
      renderSectionHeader={({ section: { title } }) => (
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitre}>{title}</Text>
        </View>
      )}
      stickySectionHeadersEnabled
    />
  );
}

const styles = StyleSheet.create({
  sectionHeader: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  sectionTitre: {
    fontSize: 14,
    fontWeight: '700',
    textTransform: 'uppercase',
    color: '#666',
    letterSpacing: 0.5,
  },
  item: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  itemTexte: {
    fontSize: 16,
  },
});
```

---

## TouchableOpacity — Bouton standard

`TouchableOpacity` est le composant cliquable le plus courant. Il réduit l'opacité au toucher pour donner un retour visuel.

```jsx
import { TouchableOpacity, Text, View, StyleSheet } from 'react-native';

export default function ExempleBoutons() {
  return (
    <View style={styles.container}>

      {/* Bouton principal */}
      <TouchableOpacity
        style={styles.boutonPrimaire}
        onPress={() => console.log('Appuyé !')}
        activeOpacity={0.7}
      >
        <Text style={styles.boutonTexte}>Bouton principal</Text>
      </TouchableOpacity>

      {/* Bouton secondaire */}
      <TouchableOpacity
        style={styles.boutonSecondaire}
        onPress={() => console.log('Secondaire')}
      >
        <Text style={styles.boutonTexteSecondaire}>Bouton secondaire</Text>
      </TouchableOpacity>

      {/* Bouton désactivé */}
      <TouchableOpacity
        style={[styles.boutonPrimaire, styles.boutonDesactive]}
        onPress={() => {}}
        disabled
      >
        <Text style={styles.boutonTexte}>Désactivé</Text>
      </TouchableOpacity>

      {/* Carte cliquable */}
      <TouchableOpacity
        style={styles.carte}
        onPress={() => console.log('Carte')}
        onLongPress={() => console.log('Appui long !')}
        delayLongPress={500}
      >
        <Text style={styles.carteTitre}>Carte cliquable</Text>
        <Text style={styles.carteDesc}>Appui normal ou appui long</Text>
      </TouchableOpacity>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 12,
  },
  boutonPrimaire: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 10,
    alignItems: 'center',
  },
  boutonSecondaire: {
    borderWidth: 1.5,
    borderColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 10,
    alignItems: 'center',
  },
  boutonDesactive: {
    backgroundColor: '#ccc',
  },
  boutonTexte: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  boutonTexteSecondaire: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  carte: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  carteTitre: {
    fontSize: 16,
    fontWeight: '600',
  },
  carteDesc: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
});
```

---

## Pressable — Le remplaçant moderne

`Pressable` (React Native 0.63+) est plus flexible que `TouchableOpacity` : il permet de modifier le style selon l'état (pressed, hovered, focused).

```jsx
import { Pressable, Text, StyleSheet } from 'react-native';

export default function ExemplePressable() {
  return (
    <>
      {/* Style dynamique selon l'état pressed */}
      <Pressable
        style={({ pressed }) => [
          styles.bouton,
          pressed && styles.boutonAppuye,
        ]}
        onPress={() => console.log('Pressable appuyé')}
      >
        {({ pressed }) => (
          <Text style={[styles.texte, pressed && styles.texteAppuye]}>
            {pressed ? 'Appuyé !' : 'Appuyez ici'}
          </Text>
        )}
      </Pressable>

      {/* Avec hitSlop — zone de tap plus grande que le visuel */}
      <Pressable
        style={styles.petitBouton}
        onPress={() => console.log('Zone élargie')}
        hitSlop={{ top: 10, bottom: 10, left: 20, right: 20 }}
      >
        <Text style={styles.petitTexte}>Zone tap élargie</Text>
      </Pressable>
    </>
  );
}

const styles = StyleSheet.create({
  bouton: {
    backgroundColor: '#34C759',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
  },
  boutonAppuye: {
    backgroundColor: '#248A3D',
    transform: [{ scale: 0.97 }],
  },
  texte: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  texteAppuye: {
    opacity: 0.8,
  },
  petitBouton: {
    backgroundColor: '#FF9500',
    padding: 8,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  petitTexte: {
    color: '#fff',
    fontSize: 12,
  },
});
```

---

## Modal — Fenêtre modale

```jsx
import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Pressable,
} from 'react-native';

export default function ExempleModal() {
  const [visible, setVisible] = useState(false);

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.bouton}
        onPress={() => setVisible(true)}
      >
        <Text style={styles.boutonTexte}>Ouvrir la modal</Text>
      </TouchableOpacity>

      <Modal
        visible={visible}
        animationType="slide"    // "none", "slide", "fade"
        transparent
        onRequestClose={() => setVisible(false)} // Bouton retour Android
      >
        {/* Fond semi-transparent */}
        <Pressable
          style={styles.fond}
          onPress={() => setVisible(false)}
        >
          {/* Contenu de la modal — stopper la propagation du press */}
          <Pressable style={styles.contenu} onPress={(e) => e.stopPropagation()}>
            <Text style={styles.titre}>Confirmation</Text>
            <Text style={styles.message}>
              Voulez-vous vraiment effectuer cette action ?
            </Text>
            <View style={styles.actions}>
              <TouchableOpacity
                style={[styles.boutonAction, styles.boutonAnnuler]}
                onPress={() => setVisible(false)}
              >
                <Text style={styles.texteAnnuler}>Annuler</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.boutonAction, styles.boutonConfirmer]}
                onPress={() => {
                  console.log('Confirmé !');
                  setVisible(false);
                }}
              >
                <Text style={styles.texteConfirmer}>Confirmer</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bouton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 10,
  },
  boutonTexte: {
    color: '#fff',
    fontWeight: '600',
  },
  fond: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  contenu: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 24,
    paddingBottom: 40,
  },
  titre: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  message: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
    marginBottom: 24,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  boutonAction: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  boutonAnnuler: {
    backgroundColor: '#f0f0f0',
  },
  boutonConfirmer: {
    backgroundColor: '#007AFF',
  },
  texteAnnuler: {
    color: '#333',
    fontWeight: '600',
  },
  texteConfirmer: {
    color: '#fff',
    fontWeight: '600',
  },
});
```

---

## ActivityIndicator et Switch

```jsx
import { ActivityIndicator, Switch, View, Text, useState } from 'react-native';
import React, { useState } from 'react';

export default function AutresComposants() {
  const [charge, setCharge] = useState(true);
  const [actif, setActif] = useState(false);

  return (
    <View style={{ padding: 16, gap: 16 }}>
      {/* Spinner de chargement */}
      <ActivityIndicator size="large" color="#007AFF" />
      <ActivityIndicator size="small" color="#FF9500" />

      {/* Toggle switch */}
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
        <Text>Notifications</Text>
        <Switch
          value={actif}
          onValueChange={setActif}
          trackColor={{ false: '#ddd', true: '#34C759' }}
          thumbColor={actif ? '#fff' : '#fff'}
        />
      </View>
    </View>
  );
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application avec FlatList longue affichant 50 éléments — faire défiler rapidement pour montrer que les éléments hors écran sont dé-rendus et ré-rendus à la volée
> **Expliquer :** Comparer FlatList vs ScrollView. Avec ScrollView, tous les éléments sont rendus d'un coup (lourd en mémoire). Avec FlatList, seuls ~10-15 éléments sont dans le DOM natif à un instant T. Ouvrir le Performance Monitor (menu dev) pour montrer la différence de FPS et de mémoire.
---

## Recap — Quand utiliser quel composant

| Besoin | Composant |
|--------|-----------|
| Conteneur / mise en page | `View` |
| Texte | `Text` |
| Image | `Image` |
| Saisie utilisateur | `TextInput` |
| Liste courte (contenu statique) | `ScrollView` |
| Liste longue (données dynamiques) | `FlatList` |
| Liste avec groupes | `SectionList` |
| Bouton simple | `TouchableOpacity` |
| Bouton avec états visuels fins | `Pressable` |
| Fenêtre superposée | `Modal` |
| Chargement | `ActivityIndicator` |
| Interrupteur on/off | `Switch` |
