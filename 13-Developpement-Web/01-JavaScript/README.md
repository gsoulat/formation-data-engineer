# Formation JavaScript — De Zéro à Productif

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Écrire du JavaScript moderne (ES6+) en maîtrisant les fondamentaux du langage
- Comprendre et utiliser la programmation asynchrone (Promises, async/await)
- Manipuler le DOM et interagir avec des APIs REST via `fetch()`
- Organiser votre code avec les modules ES6
- Lire et écrire du TypeScript de base

---

## Prérequis

- Notions de base en HTML et CSS
- Un éditeur de code installé (VS Code recommandé)
- Node.js 18+ installé ([https://nodejs.org](https://nodejs.org))
- Un navigateur moderne (Chrome ou Firefox)

---

## Structure du cours

```
JavaScript/
├── Fondamentaux/
│   ├── 01-bases.md              ← Variables, types, opérateurs, coercions
│   ├── 02-fonctions.md          ← Déclarations, arrow functions, closures, IIFE
│   ├── 03-objets-tableaux.md    ← Destructuring, spread, map/filter/reduce
│   └── 04-classes.md            ← class, héritage, private fields, static
├── Asynchrone/
│   ├── 01-callbacks-promises.md ← Callbacks, Promise, .then/.catch/.finally
│   └── 02-async-await.md        ← async/await, gestion d'erreurs, parallélisme
├── DOM-Browser/
│   ├── 01-dom.md                ← querySelector, événements, manipulation DOM
│   └── 02-fetch-api.md          ← fetch(), JSON, headers, gestion d'erreurs
├── Moderne/
│   ├── 01-es6-plus.md           ← Modules, optional chaining, generators
│   └── 02-typescript-intro.md   ← Types, interfaces, generics, tsconfig
├── exercices/
│   ├── exercice-01-todo-vanilla.md
│   └── exercice-02-fetch-api.md
└── CHEATSHEET-javascript.md
```

---

## Environnement de travail recommandé

### VS Code — Extensions utiles

| Extension | Utilité |
|---|---|
| ESLint | Détection des erreurs en temps réel |
| Prettier | Formatage automatique du code |
| JavaScript (ES6) code snippets | Raccourcis de code |
| Live Server | Serveur local avec rechargement automatique |
| Thunder Client | Tester les APIs REST sans quitter VS Code |

### Configuration minimale VS Code

Créez un fichier `.vscode/settings.json` à la racine de votre projet :

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "javascript.updateImportsOnFileMove.enabled": "always"
}
```

---

## Parcours recommandé

### Débutant (0 expérience JS)
1. Fondamentaux 01 → 02 → 03 → 04
2. Asynchrone 01 → 02
3. DOM-Browser 01 → 02
4. Exercice 01 (Todo vanilla)

### Intermédiaire (connait les bases)
1. Fondamentaux 03 → 04 (révision rapide)
2. Asynchrone 01 → 02
3. DOM-Browser 02
4. Moderne 01 → 02
5. Exercice 02 (Fetch API)

### Vers React (objectif framework)
1. Tous les Fondamentaux
2. Asynchrone complet
3. Moderne complet (surtout modules ES6)
4. TypeScript intro
5. Les deux exercices

---

## Ressources complémentaires

- **MDN Web Docs** : [https://developer.mozilla.org/fr/docs/Web/JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript) — LA référence
- **javascript.info** : [https://fr.javascript.info/](https://fr.javascript.info/) — Cours complet en français
- **Node.js docs** : [https://nodejs.org/fr/docs/](https://nodejs.org/fr/docs/)
- **Can I Use** : [https://caniuse.com/](https://caniuse.com/) — Compatibilité navigateurs

---

## Convention utilisée dans ce cours

```
---
> 🔴 ACTION FORMATEUR — CAPTURE REQUISE
> Capturer : [description de ce qu'il faut filmer/capturer]
> Expliquer : [ce que le formateur doit montrer à voix haute]
---
```

Ces blocs indiquent les moments où le formateur doit montrer quelque chose à l'écran, dans le navigateur ou dans le terminal.

---

## Durée estimée

| Module | Durée estimée |
|---|---|
| Fondamentaux | 6–8 heures |
| Asynchrone | 3–4 heures |
| DOM & Browser | 3–4 heures |
| JavaScript Moderne | 3–4 heures |
| Exercices pratiques | 4–6 heures |
| **Total** | **~20–26 heures** |
