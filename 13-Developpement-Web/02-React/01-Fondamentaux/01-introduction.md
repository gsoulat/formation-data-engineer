# 01 — Introduction à React : JSX, Vite, Structure d'un Composant

## Qu'est-ce que React ?

React est une **bibliothèque JavaScript** (pas un framework complet) développée par Meta pour construire des interfaces utilisateur. Ses caractéristiques principales :

- **Composants** : l'UI est découpée en blocs réutilisables et composables
- **Déclaratif** : on décrit CE QUE l'UI doit afficher, pas COMMENT le DOM doit être mis à jour
- **Virtual DOM** : React maintient une représentation virtuelle du DOM en mémoire pour optimiser les mises à jour
- **Unidirectionnel** : les données circulent toujours du parent vers l'enfant

---

## 1. Créer un projet avec Vite

```bash
# Créer un nouveau projet
npm create vite@latest formation-react -- --template react
cd formation-react

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
# → http://localhost:5173
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter les commandes de création, puis montrer le navigateur s'ouvrir sur http://localhost:5173 avec la page React par défaut. Modifier un texte dans `App.jsx`, sauvegarder, et montrer la mise à jour instantanée dans le navigateur (HMR — Hot Module Replacement)
> **Expliquer :** Le HMR (Hot Module Replacement) de Vite remplace le module modifié à chaud, sans recharger toute la page. L'état des composants est préservé. C'est un gain de productivité énorme en développement.

---

### Structure initiale du projet

```
formation-react/
├── src/
│   ├── assets/
│   │   └── react.svg
│   ├── App.css        ← Styles du composant App
│   ├── App.jsx        ← Composant racine
│   ├── index.css      ← Styles globaux
│   └── main.jsx       ← Point d'entrée
├── index.html         ← Template HTML (React s'injecte dans #root)
├── package.json
└── vite.config.js
```

### Le point d'entrée (`src/main.jsx`)

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Monter React dans le div#root de index.html
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

**Note sur StrictMode :** En développement, `StrictMode` exécute certains cycles de rendu deux fois pour détecter les effets de bord. C'est intentionnel — ne pas le retirer.

---

## 2. JSX — JavaScript + XML

JSX est une extension syntaxique de JavaScript qui ressemble à du HTML. Elle est **transformée en appels JavaScript** par Babel ou esbuild.

### JSX vs HTML — les différences

```jsx
// HTML
<div class="container">
  <label for="email">Email</label>
  <input type="text" autofocus>
  <p style="color: red; font-size: 14px;">Erreur</p>
</div>

// JSX — MÊMES BALISES mais quelques différences
<div className="container">   {/* class → className */}
  <label htmlFor="email">Email</label>  {/* for → htmlFor */}
  <input type="text" autoFocus />  {/* Attributs camelCase, balises auto-fermantes */}
  <p style={{ color: "red", fontSize: "14px" }}>Erreur</p>  {/* style = objet */}
</div>
```

### Expressions JavaScript dans JSX

```jsx
function Greeting() {
  const prenom = "Alice";
  const age = 30;
  const estAdmin = true;
  const couleur = "blue";

  return (
    <div>
      {/* Commentaire JSX */}
      <h1>Bonjour, {prenom} !</h1>                    {/* Variable */}
      <p>Vous avez {age} ans</p>                        {/* Calcul */}
      <p>Votre score : {age * 2}</p>                    {/* Expression */}
      <p style={{ color: couleur }}>Texte coloré</p>   {/* Objet style */}

      {/* Ternaire pour le rendu conditionnel */}
      <span>{estAdmin ? "Administrateur" : "Utilisateur"}</span>

      {/* && pour afficher/masquer */}
      {estAdmin && <button>Panneau admin</button>}

      {/* Appels de méthode */}
      <p>{"hello world".toUpperCase()}</p>

      {/* Tableau */}
      <ul>
        {["pomme", "banane", "cerise"].map(fruit => (
          <li key={fruit}>{fruit}</li>   {/* key OBLIGATOIRE dans les listes */}
        ))}
      </ul>
    </div>
  );
}
```

### Règles JSX importantes

```jsx
// 1. Un seul élément racine — utiliser <> </> (Fragment) si besoin
function BienFormate() {
  return (
    <>
      <h1>Titre</h1>
      <p>Paragraphe</p>
    </>
  );
}

// Mauvais — deux éléments racines
// function MalFormate() {
//   return (
//     <h1>Titre</h1>
//     <p>Paragraphe</p>
//   );
// }

// 2. Toutes les balises doivent être fermées
function FormExemple() {
  return (
    <form>
      <input type="text" />     {/* Auto-fermant */}
      <img src="/img.jpg" />    {/* Auto-fermant */}
      <br />                    {/* Auto-fermant */}
    </form>
  );
}

// 3. Les expressions doivent retourner du JSX, une string, un nombre, null, ou un tableau
// On ne peut pas retourner un objet plain (provoque une erreur)

// 4. false, null, undefined ne s'affichent pas
function Affichage({ montrer }) {
  return (
    <div>
      {false}        {/* N'affiche rien */}
      {null}         {/* N'affiche rien */}
      {undefined}    {/* N'affiche rien */}
      {0}            {/* Affiche "0" — ATTENTION avec && ! */}
    </div>
  );
}

// Piège courant avec 0 et &&
function ListeProduits({ produits }) {
  return (
    <div>
      {/* ❌ Affiche "0" si produits est un tableau vide ! */}
      {produits.length && <ul>...</ul>}

      {/* ✅ Correct */}
      {produits.length > 0 && <ul>...</ul>}
      {/* OU */}
      {produits.length ? <ul>...</ul> : null}
    </div>
  );
}
```

---

## 3. Premier composant

Un composant React est simplement une **fonction JavaScript** qui retourne du JSX.

```jsx
// Composant simple — convention : nom en PascalCase
function Bonjour() {
  return <h1>Bonjour le monde !</h1>;
}

// Avec un peu de logique
function CarteProfil() {
  const utilisateur = {
    nom: "Alice Martin",
    poste: "Développeuse React",
    avatar: "https://i.pravatar.cc/100",
    nbProjets: 12,
  };

  return (
    <article style={{
      border: "1px solid #e2e8f0",
      borderRadius: "8px",
      padding: "1.5rem",
      maxWidth: "300px",
      fontFamily: "sans-serif",
    }}>
      <img
        src={utilisateur.avatar}
        alt={`Photo de ${utilisateur.nom}`}
        style={{ borderRadius: "50%", width: 80, height: 80 }}
      />
      <h2 style={{ margin: "0.5rem 0 0.25rem" }}>{utilisateur.nom}</h2>
      <p style={{ color: "#64748b", margin: 0 }}>{utilisateur.poste}</p>
      <p style={{ marginTop: "0.75rem" }}>
        <strong>{utilisateur.nbProjets}</strong> projets
      </p>
    </article>
  );
}

// Utiliser des composants comme des balises HTML
function App() {
  return (
    <div>
      <Bonjour />
      <CarteProfil />
      <CarteProfil />  {/* Réutilisable autant de fois qu'on veut */}
    </div>
  );
}

export default App;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir React Developer Tools (extension navigateur) → onglet "Components" → montrer l'arbre des composants avec App > CarteProfil > CarteProfil. Cliquer sur un composant pour voir ses props et son state.
> **Expliquer :** React DevTools est l'équivalent de l'inspecteur HTML mais pour les composants React. On peut voir la hiérarchie des composants, leurs props, leur état, et même modifier des valeurs en live pour tester.

---

## 4. Comment React transforme JSX

```jsx
// Ce que vous écrivez
const element = <h1 className="titre">Bonjour</h1>;

// Ce que Babel/esbuild produit (React 17+)
import { jsx as _jsx } from "react/jsx-runtime";
const element = _jsx("h1", { className: "titre", children: "Bonjour" });

// Avant React 17, c'était :
const element = React.createElement("h1", { className: "titre" }, "Bonjour");
// C'est pourquoi les anciens codes avaient import React from 'react' même sans utiliser React directement
```

### Rendu conditionnel — les différentes façons

```jsx
function Statut({ utilisateur }) {
  // 1. if/else hors du return
  if (!utilisateur) {
    return <p>Chargement...</p>;
  }

  // 2. Ternaire dans le JSX
  return (
    <div>
      <h2>{utilisateur.nom}</h2>

      {/* 3. Ternaire */}
      <span>{utilisateur.actif ? "✅ Actif" : "❌ Inactif"}</span>

      {/* 4. && pour affichage optionnel */}
      {utilisateur.estAdmin && <AdminBadge />}

      {/* 5. Variable intermédiaire */}
      {(() => {
        if (utilisateur.role === "admin") return <AdminPanel />;
        if (utilisateur.role === "moderateur") return <ModPanel />;
        return <UserPanel />;
      })()}
    </div>
  );
}

// Composant helper pour switch complexe
function AfficherRole({ role }) {
  const composants = {
    admin: <AdminPanel />,
    moderateur: <ModPanel />,
    utilisateur: <UserPanel />,
  };

  return composants[role] ?? <p>Rôle inconnu</p>;
}
```

---

## 5. Listes et clés

```jsx
const PRODUITS = [
  { id: 1, nom: "Laptop", prix: 999, categorie: "informatique" },
  { id: 2, nom: "Casque", prix: 149, categorie: "audio" },
  { id: 3, nom: "Souris", prix: 59, categorie: "informatique" },
  { id: 4, nom: "Clavier", prix: 89, categorie: "informatique" },
];

// Composant item
function ProduitItem({ produit }) {
  return (
    <li style={{ padding: "0.75rem", borderBottom: "1px solid #e2e8f0" }}>
      <strong>{produit.nom}</strong>
      <span style={{ float: "right" }}>{produit.prix}€</span>
    </li>
  );
}

// Liste
function ListeProduits({ produits = PRODUITS }) {
  if (produits.length === 0) {
    return <p>Aucun produit disponible</p>;
  }

  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {produits.map(produit => (
        // key DOIT être unique et stable (pas l'index si la liste peut être réordonnée)
        <ProduitItem key={produit.id} produit={produit} />
      ))}
    </ul>
  );
}

// ❌ Pourquoi ne pas utiliser l'index comme key (si la liste peut changer)
{items.map((item, index) => (
  <Item key={index} item={item} /> // Problèmes si on réordonne/supprime !
))}

// ✅ Utiliser un identifiant stable
{items.map(item => (
  <Item key={item.id} item={item} />
))}
```

---

## 6. Comprendre le Virtual DOM

```
État React change
       ↓
React re-rend le composant (crée un nouveau Virtual DOM)
       ↓
React compare le nouveau Virtual DOM avec l'ancien (diffing)
       ↓
React applique UNIQUEMENT les changements au vrai DOM (reconciliation)
```

```jsx
// React ne re-rend que ce qui a changé
// Si on a 1000 <li> et qu'un seul change, seul ce <li> est mis à jour dans le DOM

// C'est pour ça que les keys sont importantes :
// Avec une bonne key, React sait EXACTEMENT quel élément a changé
// Sans key (ou avec une mauvaise key), React peut tout re-créer inutilement
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| JSX | Syntaxe = HTML + `{}` pour les expressions JS |
| `className` | Remplace `class` en JSX |
| `htmlFor` | Remplace `for` en JSX |
| `style` | Reçoit un objet JS (`style={{ color: "red" }}`) |
| Composant | Fonction en PascalCase retournant du JSX |
| Fragment | `<>...</>` pour éviter un div wrapper inutile |
| `key` | Obligatoire dans les `.map()`, doit être unique et stable |
| Rendu conditionnel | Ternaire `?:`, logique `&&`, ou variable intermédiaire |
