# Exercice 01 — Application Todo Mobile avec AsyncStorage

## Objectif

Créer une application de gestion de tâches complète pour mobile, incluant la persistance des données avec AsyncStorage, le filtrage, les animations et une interface soignée.

## Durée estimée

**2h30**

## Compétences travaillées

- Composants core (FlatList, TextInput, TouchableOpacity, Modal)
- StyleSheet et Flexbox
- useState, useEffect, useCallback
- AsyncStorage — lecture, écriture, suppression
- Navigation avec React Navigation (optionnel : version avancée)
- Gestion des gestes (swipe to delete optionnel)

---

## Spécifications fonctionnelles

### Fonctionnalités requises (Niveau 1)

- [ ] Ajouter une tâche via un champ de saisie
- [ ] Afficher la liste des tâches dans une FlatList
- [ ] Marquer une tâche comme terminée (tap sur la tâche)
- [ ] Supprimer une tâche (appui long → confirmation)
- [ ] Persister les tâches dans AsyncStorage (survit aux redémarrages)
- [ ] Afficher le nombre de tâches restantes

### Fonctionnalités avancées (Niveau 2)

- [ ] Filtrer par statut : Toutes / En cours / Terminées
- [ ] Modifier le texte d'une tâche existante
- [ ] Catégories de tâches (Perso, Travail, Courses...)
- [ ] Priorité (haute, normale, basse) avec indicateur visuel
- [ ] Date limite avec rappel de couleur si dépassée

### Fonctionnalités bonus (Niveau 3)

- [ ] Réorganiser les tâches (drag and drop avec `react-native-draggable-flatlist`)
- [ ] Notification locale de rappel pour une tâche avec date limite
- [ ] Statistiques : tâches créées, terminées cette semaine
- [ ] Thème sombre/clair

---

## Structure recommandée du projet

```
todo-app/
├── App.tsx
├── src/
│   ├── components/
│   │   ├── TodoItem.tsx          ← Une tâche dans la liste
│   │   ├── TodoInput.tsx         ← Champ de saisie + bouton
│   │   ├── FiltreBar.tsx         ← Boutons Toutes/En cours/Terminées
│   │   ├── CategoriesBadge.tsx   ← Badge de catégorie coloré
│   │   └── EtatVide.tsx          ← Illustration quand la liste est vide
│   ├── screens/
│   │   ├── ListeTodosScreen.tsx  ← Écran principal
│   │   └── DetailTodoScreen.tsx  ← Édition d'une tâche (niveau 2)
│   ├── hooks/
│   │   └── useTodos.ts           ← Logique métier + AsyncStorage
│   ├── types/
│   │   └── index.ts              ← Types TypeScript
│   └── constants/
│       └── categories.ts         ← Liste des catégories
```

---

## Types à définir

```typescript
// src/types/index.ts

export type Priorite = 'haute' | 'normale' | 'basse';
export type Categorie = 'perso' | 'travail' | 'courses' | 'sante' | 'autre';
export type Filtre = 'toutes' | 'en_cours' | 'terminees';

export interface Todo {
  id: string;
  texte: string;
  complete: boolean;
  categorie: Categorie;
  priorite: Priorite;
  dateLimite?: string;      // ISO string, optionnel
  creeLe: string;           // ISO string
  misAJour: string;         // ISO string
}

export interface StatsTodos {
  total: number;
  terminees: number;
  enCours: number;
  tauxCompletion: number;   // 0-100
}
```

---

## Hook useTodos — à compléter

```typescript
// src/hooks/useTodos.ts
import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Todo, Filtre, StatsTodos } from '../types';

const CLE_STORAGE = '@todos_app_v1';

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [chargement, setChargement] = useState(true);
  const [filtre, setFiltre] = useState<Filtre>('toutes');
  const [recherche, setRecherche] = useState('');

  // TODO : Charger les todos depuis AsyncStorage au montage
  useEffect(() => {
    // À COMPLÉTER
  }, []);

  // TODO : Sauvegarder les todos dans AsyncStorage à chaque changement
  // (déclenché quand todos change, mais pas au premier rendu)
  const sauvegarder = useCallback(async (nouveauxTodos: Todo[]) => {
    // À COMPLÉTER
  }, []);

  // TODO : Ajouter une nouvelle tâche
  const ajouter = useCallback((
    texte: string,
    categorie: Todo['categorie'] = 'autre',
    priorite: Todo['priorite'] = 'normale',
    dateLimite?: string
  ) => {
    // À COMPLÉTER
    // Créer un Todo avec un id unique (Date.now().toString() ou uuid)
  }, [sauvegarder, todos]);

  // TODO : Basculer l'état complete/incomplete
  const basculer = useCallback((id: string) => {
    // À COMPLÉTER
  }, [sauvegarder, todos]);

  // TODO : Modifier le texte d'une tâche
  const modifier = useCallback((id: string, updates: Partial<Omit<Todo, 'id' | 'creeLe'>>) => {
    // À COMPLÉTER
  }, [sauvegarder, todos]);

  // TODO : Supprimer une tâche
  const supprimer = useCallback((id: string) => {
    // À COMPLÉTER
  }, [sauvegarder, todos]);

  // TODO : Supprimer toutes les tâches terminées
  const supprimerTerminees = useCallback(() => {
    // À COMPLÉTER
  }, [sauvegarder, todos]);

  // Filtrer les todos selon le filtre actif et la recherche
  const todosFiltres = todos.filter(todo => {
    const matchFiltre =
      filtre === 'toutes' ? true :
      filtre === 'en_cours' ? !todo.complete :
      todo.complete;

    const matchRecherche = recherche
      ? todo.texte.toLowerCase().includes(recherche.toLowerCase())
      : true;

    return matchFiltre && matchRecherche;
  });

  // Calculer les statistiques
  const stats: StatsTodos = {
    total: todos.length,
    terminees: todos.filter(t => t.complete).length,
    enCours: todos.filter(t => !t.complete).length,
    tauxCompletion: todos.length
      ? Math.round((todos.filter(t => t.complete).length / todos.length) * 100)
      : 0,
  };

  return {
    todos: todosFiltres,
    tousLesTodos: todos,
    stats,
    chargement,
    filtre,
    setFiltre,
    recherche,
    setRecherche,
    ajouter,
    basculer,
    modifier,
    supprimer,
    supprimerTerminees,
  };
}
```

---

## Composant TodoItem — à compléter

```tsx
// src/components/TodoItem.tsx
import React, { useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Animated,
  Alert,
  StyleSheet,
} from 'react-native';
import { Todo } from '../types';

interface Props {
  todo: Todo;
  onBasculer: (id: string) => void;
  onSupprimer: (id: string) => void;
  onModifier?: (todo: Todo) => void;
}

// Couleurs des priorités
const COULEURS_PRIORITE: Record<Todo['priorite'], string> = {
  haute: '#FF3B30',
  normale: '#007AFF',
  basse: '#8E8E93',
};

// Couleurs des catégories
const COULEURS_CATEGORIE: Record<Todo['categorie'], string> = {
  perso: '#FF9500',
  travail: '#007AFF',
  courses: '#34C759',
  sante: '#FF2D55',
  autre: '#8E8E93',
};

export const TodoItem: React.FC<Props> = ({ todo, onBasculer, onSupprimer, onModifier }) => {
  // TODO : Ajouter une animation d'opacité quand la tâche est complète
  const opaciteAnim = useRef(new Animated.Value(todo.complete ? 0.6 : 1)).current;

  // TODO : Animation lors du basculement
  const handleBasculer = () => {
    // À COMPLÉTER : animer puis appeler onBasculer
    onBasculer(todo.id);
  };

  const handleSupprimer = () => {
    Alert.alert(
      'Supprimer',
      `Supprimer "${todo.texte}" ?`,
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: () => onSupprimer(todo.id),
        },
      ]
    );
  };

  // Vérifier si la date limite est dépassée
  const estEnRetard = todo.dateLimite && !todo.complete
    ? new Date(todo.dateLimite) < new Date()
    : false;

  return (
    <Animated.View style={[styles.container, { opacity: opaciteAnim }]}>
      <TouchableOpacity
        style={styles.contenu}
        onPress={handleBasculer}
        onLongPress={handleSupprimer}
        delayLongPress={500}
        activeOpacity={0.7}
      >
        {/* Indicateur de priorité */}
        <View style={[styles.prioriteIndicateur, { backgroundColor: COULEURS_PRIORITE[todo.priorite] }]} />

        {/* Case à cocher */}
        <View style={[styles.coche, todo.complete && styles.cocheComplete]}>
          {todo.complete && <Text style={styles.cocheIcone}>✓</Text>}
        </View>

        {/* Contenu de la tâche */}
        <View style={styles.info}>
          <Text
            style={[styles.texte, todo.complete && styles.texteComplete]}
            numberOfLines={2}
          >
            {todo.texte}
          </Text>

          <View style={styles.meta}>
            {/* Badge de catégorie */}
            <View style={[styles.categorieBadge, { backgroundColor: COULEURS_CATEGORIE[todo.categorie] + '20' }]}>
              <Text style={[styles.categorieTexte, { color: COULEURS_CATEGORIE[todo.categorie] }]}>
                {todo.categorie}
              </Text>
            </View>

            {/* Date limite */}
            {todo.dateLimite && (
              <Text style={[styles.dateLimite, estEnRetard && styles.dateLimiteRetard]}>
                {estEnRetard ? '⚠ ' : '📅 '}
                {new Date(todo.dateLimite).toLocaleDateString('fr-FR')}
              </Text>
            )}
          </View>
        </View>

        {/* Bouton modifier (optionnel) */}
        {onModifier && !todo.complete && (
          <TouchableOpacity
            style={styles.boutonModifier}
            onPress={() => onModifier(todo)}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <Text style={styles.iconeModifier}>✏️</Text>
          </TouchableOpacity>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    overflow: 'hidden',
  },
  contenu: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
  },
  prioriteIndicateur: {
    width: 4,
    height: '100%',
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
  },
  coche: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 8,
    marginRight: 12,
  },
  cocheComplete: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  cocheIcone: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  info: {
    flex: 1,
    gap: 6,
  },
  texte: {
    fontSize: 16,
    color: '#1a1a1a',
    lineHeight: 20,
  },
  texteComplete: {
    textDecorationLine: 'line-through',
    color: '#aaa',
  },
  meta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
  },
  categorieBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  categorieTexte: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  dateLimite: {
    fontSize: 11,
    color: '#999',
  },
  dateLimiteRetard: {
    color: '#FF3B30',
    fontWeight: '600',
  },
  boutonModifier: {
    padding: 4,
  },
  iconeModifier: {
    fontSize: 16,
  },
});
```

---

## Écran principal — à compléter

```tsx
// src/screens/ListeTodosScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { useTodos } from '../hooks/useTodos';
import { TodoItem } from '../components/TodoItem';
// import { TodoInput } from '../components/TodoInput';
// import { FiltreBar } from '../components/FiltreBar';

export default function ListeTodosScreen() {
  const {
    todos,
    stats,
    chargement,
    filtre,
    setFiltre,
    ajouter,
    basculer,
    supprimer,
    supprimerTerminees,
  } = useTodos();

  // TODO : Implémenter l'écran complet avec :
  // - SafeAreaView comme conteneur racine
  // - En-tête avec titre + statistiques
  // - FiltreBar pour changer le filtre
  // - TodoInput pour ajouter une tâche
  // - FlatList avec TodoItem
  // - Bouton "Nettoyer terminées" si stats.terminees > 0
  // - Message état vide si todos.length === 0

  return (
    <SafeAreaView style={styles.container}>
      {/* TODO : Construire l'interface */}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});
```

---

## Solution complète du hook useTodos

```typescript
// src/hooks/useTodos.ts — Solution
export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [chargement, setChargement] = useState(true);
  const [filtre, setFiltre] = useState<Filtre>('toutes');
  const [recherche, setRecherche] = useState('');

  useEffect(() => {
    const charger = async () => {
      try {
        const json = await AsyncStorage.getItem(CLE_STORAGE);
        if (json) setTodos(JSON.parse(json));
      } catch (e) {
        console.error('Erreur chargement todos:', e);
      } finally {
        setChargement(false);
      }
    };
    charger();
  }, []);

  const sauvegarder = useCallback(async (nouveauxTodos: Todo[]) => {
    try {
      await AsyncStorage.setItem(CLE_STORAGE, JSON.stringify(nouveauxTodos));
    } catch (e) {
      console.error('Erreur sauvegarde:', e);
    }
  }, []);

  const ajouter = useCallback((
    texte: string,
    categorie: Todo['categorie'] = 'autre',
    priorite: Todo['priorite'] = 'normale',
    dateLimite?: string
  ) => {
    const maintenant = new Date().toISOString();
    const nouveau: Todo = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      texte: texte.trim(),
      complete: false,
      categorie,
      priorite,
      dateLimite,
      creeLe: maintenant,
      misAJour: maintenant,
    };
    const nouveaux = [nouveau, ...todos];
    setTodos(nouveaux);
    sauvegarder(nouveaux);
  }, [sauvegarder, todos]);

  const basculer = useCallback((id: string) => {
    const mis = todos.map(t =>
      t.id === id
        ? { ...t, complete: !t.complete, misAJour: new Date().toISOString() }
        : t
    );
    setTodos(mis);
    sauvegarder(mis);
  }, [sauvegarder, todos]);

  const modifier = useCallback((id: string, updates: Partial<Omit<Todo, 'id' | 'creeLe'>>) => {
    const mis = todos.map(t =>
      t.id === id
        ? { ...t, ...updates, misAJour: new Date().toISOString() }
        : t
    );
    setTodos(mis);
    sauvegarder(mis);
  }, [sauvegarder, todos]);

  const supprimer = useCallback((id: string) => {
    const filtres = todos.filter(t => t.id !== id);
    setTodos(filtres);
    sauvegarder(filtres);
  }, [sauvegarder, todos]);

  const supprimerTerminees = useCallback(() => {
    const actives = todos.filter(t => !t.complete);
    setTodos(actives);
    sauvegarder(actives);
  }, [sauvegarder, todos]);

  const todosFiltres = todos.filter(todo => {
    const matchFiltre =
      filtre === 'toutes' ? true :
      filtre === 'en_cours' ? !todo.complete :
      todo.complete;
    const matchRecherche = recherche
      ? todo.texte.toLowerCase().includes(recherche.toLowerCase())
      : true;
    return matchFiltre && matchRecherche;
  });

  const stats: StatsTodos = {
    total: todos.length,
    terminees: todos.filter(t => t.complete).length,
    enCours: todos.filter(t => !t.complete).length,
    tauxCompletion: todos.length
      ? Math.round((todos.filter(t => t.complete).length / todos.length) * 100)
      : 0,
  };

  return {
    todos: todosFiltres,
    tousLesTodos: todos,
    stats,
    chargement,
    filtre,
    setFiltre,
    recherche,
    setRecherche,
    ajouter,
    basculer,
    modifier,
    supprimer,
    supprimerTerminees,
  };
}
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Ajout et affichage des tâches | 2 |
| Basculement terminé/en cours | 2 |
| Suppression avec confirmation | 1 |
| Persistance AsyncStorage (survit au redémarrage) | 3 |
| Filtrage par statut | 2 |
| Styles soignés (flexbox, couleurs, ombres) | 2 |
| TypeScript correct (types définis, pas de `any` injustifié) | 2 |
| Code organisé (composants séparés, hook dédié) | 2 |
| Fonctionnalités bonus (catégories, priorités...) | +2 |

**Total : 16 points (+ 2 bonus)**

---

## Commandes pour démarrer

```bash
# Créer le projet
npx create-expo-app todo-mobile --template blank-typescript
cd todo-mobile

# Installer les dépendances
npx expo install @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/native-stack
npx expo install react-native-screens react-native-safe-area-context

# Lancer
npx expo start
```
