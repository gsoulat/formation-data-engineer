# 01 — Manipulation du DOM : querySelector, Événements, addEventListener

## Introduction

Le DOM (Document Object Model) est la représentation en mémoire de votre page HTML sous forme d'arbre d'objets. JavaScript peut lire et modifier cet arbre — c'est ce qui rend les pages web interactives.

---

## 1. Sélectionner des éléments

### Les méthodes modernes (recommandées)

```javascript
// querySelector — sélectionne le PREMIER élément correspondant au sélecteur CSS
const titre = document.querySelector("h1");
const bouton = document.querySelector(".btn-primary");
const champ = document.querySelector("#email");
const premier = document.querySelector("ul li");

// querySelectorAll — sélectionne TOUS les éléments (retourne une NodeList)
const tousLesBoutons = document.querySelectorAll("button");
const liensExternes = document.querySelectorAll('a[target="_blank"]');
const actifsSelectionnes = document.querySelectorAll(".actif.selectionne");

// NodeList — similaire à un tableau mais pas identique
console.log(tousLesBoutons.length);    // Nombre de boutons
tousLesBoutons.forEach(btn => {        // forEach disponible sur NodeList
  console.log(btn.textContent);
});

// Convertir en vrai tableau pour utiliser toutes les méthodes Array
const tableau = Array.from(tousLesBoutons);
// ou
const tableau2 = [...tousLesBoutons];

// Chercher dans un sous-arbre
const nav = document.querySelector("nav");
const liensDuNav = nav.querySelectorAll("a"); // Seulement dans <nav>
```

### Méthodes legacy (toujours utilisées, mais moins flexibles)

```javascript
// getElementById — très rapide, uniquement par ID
const monElement = document.getElementById("mon-id");

// getElementsByClassName — retourne une HTMLCollection (live)
const elements = document.getElementsByClassName("ma-classe");

// getElementsByTagName
const divs = document.getElementsByTagName("div");

// Attention : HTMLCollection est "live" — se met à jour automatiquement
// NodeList (querySelectorAll) est "static" — snapshot au moment de l'appel
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console DevTools sur n'importe quel site — taper `document.querySelector("h1")`, `document.querySelectorAll("a")`, montrer comment naviguer dans l'objet retourné, et utiliser `$0` (l'élément sélectionné dans l'inspecteur)
> **Expliquer :** Le `$` de DevTools (`$`, `$$`) sont des raccourcis pour `querySelector` et `querySelectorAll`. Extrêmement utiles pour tester rapidement ses sélecteurs.

---

## 2. Lire et modifier les propriétés d'un élément

### Contenu textuel et HTML

```javascript
// HTML de la page pour les exemples :
// <div id="app">
//   <h1 class="titre">Bonjour</h1>
//   <p id="description">Un paragraphe</p>
//   <ul id="liste"><li>Item 1</li><li>Item 2</li></ul>
// </div>

const titre = document.querySelector(".titre");

// textContent — texte brut (sans HTML)
console.log(titre.textContent); // "Bonjour"
titre.textContent = "Au revoir"; // Modifie le texte (échappe les caractères HTML)
titre.textContent = "<script>alert('xss')</script>"; // Affiché comme texte, pas exécuté — SÉCURISÉ

// innerHTML — HTML interne (attention aux injections XSS !)
const liste = document.querySelector("#liste");
console.log(liste.innerHTML); // "<li>Item 1</li><li>Item 2</li>"
liste.innerHTML = "<li>Nouveau</li><li>Items</li>"; // Remplace tout le contenu

// ⚠️ NE JAMAIS injecter des données utilisateur dans innerHTML !
const saisieUtilisateur = '<img src="x" onerror="alert(\'XSS\')">';
// liste.innerHTML = saisieUtilisateur; // DANGER — XSS !
liste.textContent = saisieUtilisateur; // Sécurisé — affiché comme texte

// innerText — similaire à textContent mais respecte le CSS (display:none, etc.)
// Généralement, préférer textContent pour les modifications programmatiques
```

### Attributs HTML

```javascript
const lien = document.querySelector("a");
const image = document.querySelector("img");
const champ = document.querySelector("input");

// getAttribute / setAttribute / removeAttribute / hasAttribute
console.log(lien.getAttribute("href"));  // "https://example.com"
lien.setAttribute("href", "/nouvelle-page");
lien.setAttribute("target", "_blank");
lien.removeAttribute("title");
console.log(lien.hasAttribute("class")); // true/false

// Propriétés directes (recommandé pour les attributs standards)
console.log(image.src);    // URL absolue
console.log(image.alt);
console.log(champ.value);
console.log(champ.type);
console.log(champ.placeholder);
console.log(champ.disabled);

champ.value = "Nouvelle valeur";
champ.disabled = true;
image.src = "/nouvelle-image.jpg";

// dataset — attributs data-*
// <div data-user-id="42" data-role="admin">
const el = document.querySelector("[data-user-id]");
console.log(el.dataset.userId); // "42" (camelCase depuis kebab-case)
console.log(el.dataset.role);   // "admin"
el.dataset.status = "actif";    // Crée data-status="actif"
```

### Classes CSS

```javascript
const bouton = document.querySelector(".btn");

// classList — la façon moderne
bouton.classList.add("actif");
bouton.classList.remove("desactive");
bouton.classList.toggle("ouvert"); // Ajoute si absent, retire si présent
bouton.classList.toggle("visible", true);  // Force l'ajout
bouton.classList.toggle("visible", false); // Force la suppression
console.log(bouton.classList.contains("actif")); // true/false
console.log(bouton.classList.length); // Nombre de classes

// Ajouter/retirer plusieurs classes
bouton.classList.add("classe1", "classe2", "classe3");
bouton.classList.remove("classe1", "classe2");

// className — propriété string (toutes les classes)
console.log(bouton.className); // "btn actif classe3"
bouton.className = "btn autre-classe"; // Remplace TOUTES les classes
```

### Styles CSS

```javascript
const boite = document.querySelector(".boite");

// Style inline (éviter si possible — préférer les classes CSS)
boite.style.backgroundColor = "red";    // camelCase en JS, kebab-case en CSS
boite.style.fontSize = "16px";          // Inclure l'unité !
boite.style.display = "flex";
boite.style.transform = "rotate(45deg)";

// Lire un style calculé (incluant les styles des feuilles CSS)
const styleCalcule = window.getComputedStyle(boite);
console.log(styleCalcule.backgroundColor); // "rgb(255, 0, 0)"
console.log(styleCalcule.fontSize);         // "16px"
console.log(styleCalcule.display);          // "block", "flex", etc.

// Supprimer un style inline
boite.style.backgroundColor = ""; // Retirer → revient au style CSS
```

---

## 3. Créer et insérer des éléments

```javascript
// Créer un élément
const nouveauParagraphe = document.createElement("p");
nouveauParagraphe.textContent = "Je suis un nouveau paragraphe";
nouveauParagraphe.classList.add("intro");

// Créer un élément complexe
function creerCarteUtilisateur(utilisateur) {
  const carte = document.createElement("article");
  carte.classList.add("carte", "carte-utilisateur");
  carte.dataset.userId = utilisateur.id;

  const nom = document.createElement("h3");
  nom.textContent = utilisateur.nom;

  const email = document.createElement("a");
  email.href = `mailto:${utilisateur.email}`;
  email.textContent = utilisateur.email;

  const badge = document.createElement("span");
  badge.classList.add("badge", `badge-${utilisateur.role}`);
  badge.textContent = utilisateur.role;

  carte.appendChild(nom);
  carte.appendChild(email);
  carte.appendChild(badge);

  return carte;
}

const utilisateur = { id: 1, nom: "Alice", email: "alice@ex.com", role: "admin" };
const carte = creerCarteUtilisateur(utilisateur);

// Insérer dans le DOM
const conteneur = document.querySelector("#conteneur");
conteneur.appendChild(carte);                        // À la fin
conteneur.prepend(carte);                            // Au début
conteneur.insertBefore(carte, conteneur.firstChild); // Avant un élément
carte.insertAdjacentHTML("beforeend", "<button>Supprimer</button>"); // Insérer du HTML

// insertAdjacentHTML — 4 positions
// 'beforebegin' — avant l'élément lui-même
// 'afterbegin'  — dans l'élément, avant son premier enfant
// 'beforeend'   — dans l'élément, après son dernier enfant
// 'afterend'    — après l'élément lui-même

// Supprimer un élément
const aSupprimer = document.querySelector(".obsolete");
aSupprimer?.remove(); // L'opérateur ?. évite l'erreur si l'élément n'existe pas
// ou : aSupprimer.parentNode.removeChild(aSupprimer); // Ancienne façon

// Remplacer un élément
const ancien = document.querySelector(".ancien");
const nouveau = document.createElement("div");
nouveau.textContent = "Nouveau contenu";
ancien?.replaceWith(nouveau); // ou ancien.parentNode.replaceChild(nouveau, ancien)

// Cloner un élément
const original = document.querySelector(".modele");
const clone = original.cloneNode(true); // true = copie profonde (avec enfants)
clone.querySelector("h3").textContent = "Copie";
conteneur.appendChild(clone);
```

---

## 4. Navigation dans l'arbre DOM

```javascript
const element = document.querySelector("#mon-element");

// Relations familiales
console.log(element.parentElement);         // Parent direct
console.log(element.children);              // Enfants (HTMLCollection, éléments seulement)
console.log(element.childNodes);            // Enfants (NodeList, incluant texte et commentaires)
console.log(element.firstElementChild);     // Premier enfant élément
console.log(element.lastElementChild);      // Dernier enfant élément
console.log(element.nextElementSibling);    // Élément suivant
console.log(element.previousElementSibling); // Élément précédent

// Traverser l'arbre
function trouverAncetre(element, selecteur) {
  let courant = element.parentElement;
  while (courant) {
    if (courant.matches(selecteur)) return courant;
    courant = courant.parentElement;
  }
  return null;
}

// closest() — méthode native pour trouver l'ancêtre le plus proche
const lien = document.querySelector("a.btn");
const formulaire = lien.closest("form");
const section = lien.closest("section, article");

// matches() — tester si un élément correspond à un sélecteur
const elements = document.querySelectorAll("div");
elements.forEach(el => {
  if (el.matches(".actif:not(.desactive)")) {
    console.log("Actif et non désactivé:", el);
  }
});
```

---

## 5. Les événements

### Ajouter des écouteurs d'événements

```javascript
const bouton = document.querySelector("#mon-bouton");

// addEventListener — méthode recommandée
bouton.addEventListener("click", function(event) {
  console.log("Cliqué !", event);
});

// Avec une arrow function
bouton.addEventListener("click", (event) => {
  console.log("Cliqué avec arrow function");
});

// Stocker la référence pour pouvoir supprimer l'écouteur
function gererClic(event) {
  console.log("Clic géré");
}
bouton.addEventListener("click", gererClic);
bouton.removeEventListener("click", gererClic); // Supprime l'écouteur

// Options
bouton.addEventListener("click", gererClic, {
  once: true,      // S'exécute une seule fois puis se supprime automatiquement
  passive: true,   // Améliore les performances (scroll sans preventDefault)
  capture: true,   // Écoute pendant la phase de capture (vs bubbling)
});
```

### L'objet Event

```javascript
document.querySelector("form").addEventListener("submit", (event) => {
  event.preventDefault(); // Empêche le comportement par défaut (envoi du formulaire)

  console.log(event.type);    // "submit"
  console.log(event.target);  // L'élément qui a déclenché l'événement (le form)
  console.log(event.currentTarget); // L'élément sur lequel l'écouteur est attaché

  // Pour les événements de clic
  console.log(event.clientX, event.clientY);   // Position relative à la fenêtre
  console.log(event.pageX, event.pageY);        // Position relative à la page
  console.log(event.ctrlKey, event.shiftKey);   // Touches modificatrices
});

// Événements de clavier
document.querySelector("input").addEventListener("keydown", (event) => {
  console.log(event.key);     // "Enter", "Backspace", "a", "A", etc.
  console.log(event.code);    // "KeyA", "Enter", "Space" — indépendant du layout
  console.log(event.altKey);  // true si Alt enfoncé

  if (event.key === "Enter") {
    event.preventDefault();
    console.log("Entrée pressée !");
  }
});

// Événements de souris
document.querySelector(".zone").addEventListener("mousemove", (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  console.log(`Position dans la zone: ${x}, ${y}`);
});
```

---

## 6. La délégation d'événements

Plutôt que d'attacher un écouteur à chaque élément d'une liste, on attache UN SEUL écouteur au parent. C'est plus efficace et fonctionne avec les éléments ajoutés dynamiquement.

```javascript
// ❌ Un écouteur par élément — inefficace
document.querySelectorAll(".btn-supprimer").forEach(btn => {
  btn.addEventListener("click", (e) => {
    e.target.closest("li").remove();
  });
});

// ✅ Délégation — UN seul écouteur sur le parent
const liste = document.querySelector("#liste");

liste.addEventListener("click", (event) => {
  // event.target est l'élément RÉELLEMENT cliqué
  // event.currentTarget est l'élément qui a l'écouteur (la liste)

  // Vérifier si le clic était sur un bouton de suppression
  const btnSupprimer = event.target.closest(".btn-supprimer");
  if (btnSupprimer) {
    btnSupprimer.closest("li").remove();
    return;
  }

  // Vérifier si le clic était sur un bouton d'édition
  const btnEditer = event.target.closest(".btn-editer");
  if (btnEditer) {
    const item = btnEditer.closest("li");
    const texte = item.querySelector("span");
    texte.contentEditable = "true";
    texte.focus();
    return;
  }
});
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Events de DevTools (ou onglet Elements → Event Listeners) — inspecter un bouton et montrer les écouteurs attachés, puis montrer dans la console comment déclencher un événement manuellement avec `element.click()` ou `element.dispatchEvent(new Event("click"))`
> **Expliquer :** La délégation d'événements est un pattern clé en performance. Ajouter 1000 écouteurs individuels vs 1 écouteur sur le parent — la différence de mémoire est significative. React utilise ce même principe en interne.

---

## 7. Propagation des événements

```javascript
// Les événements "remontent" dans l'arbre DOM (bubbling)
// <div id="parent"> <button id="enfant"> Cliquer </button> </div>

document.querySelector("#parent").addEventListener("click", () => {
  console.log("Parent reçoit le clic"); // 2. S'exécute en second
});

document.querySelector("#enfant").addEventListener("click", (event) => {
  console.log("Enfant reçoit le clic"); // 1. S'exécute en premier
  // event.stopPropagation(); // Arrêterait la propagation vers le parent
});

// stopPropagation() vs stopImmediatePropagation()
const btn = document.querySelector("#btn");
btn.addEventListener("click", (e) => {
  console.log("Handler 1");
  e.stopImmediatePropagation(); // Arrête les autres handlers SUR CET ÉLÉMENT
});
btn.addEventListener("click", () => {
  console.log("Handler 2"); // Ne s'exécute jamais avec stopImmediatePropagation
});

// Phase de capture — écouter AVANT que l'événement atteigne la cible
document.addEventListener("click", (e) => {
  console.log("Document - phase capture:", e.target.tagName);
}, true); // true = capture
```

---

## 8. Exemple pratique — Todo List interactive

```javascript
// HTML :
// <div id="todo-app">
//   <input type="text" id="nouveau-todo" placeholder="Nouvelle tâche...">
//   <button id="ajouter">Ajouter</button>
//   <ul id="liste-todos"></ul>
// </div>

class TodoApp {
  #todos = [];
  #liste;
  #input;

  constructor(conteneurId) {
    const app = document.querySelector(conteneurId);
    this.#liste = app.querySelector("#liste-todos");
    this.#input = app.querySelector("#nouveau-todo");

    this.#attacherEvenements(app);
  }

  #attacherEvenements(app) {
    // Ajouter via bouton
    app.querySelector("#ajouter").addEventListener("click", () => this.#ajouter());

    // Ajouter via Enter
    this.#input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.#ajouter();
    });

    // Délégation pour les actions sur les todos
    this.#liste.addEventListener("click", (e) => {
      const li = e.target.closest("li");
      if (!li) return;

      const id = Number(li.dataset.id);

      if (e.target.matches(".btn-terminer")) {
        this.#toggleTerminer(id);
      } else if (e.target.matches(".btn-supprimer")) {
        this.#supprimer(id);
      }
    });
  }

  #ajouter() {
    const texte = this.#input.value.trim();
    if (!texte) return;

    const todo = {
      id: Date.now(),
      texte,
      termine: false,
      createdAt: new Date(),
    };

    this.#todos.push(todo);
    this.#input.value = "";
    this.#afficherTodo(todo);
  }

  #afficherTodo(todo) {
    const li = document.createElement("li");
    li.dataset.id = todo.id;
    li.classList.toggle("termine", todo.termine);

    li.innerHTML = `
      <span class="texte">${todo.texte}</span>
      <div class="actions">
        <button class="btn-terminer">${todo.termine ? "Rouvrir" : "Terminer"}</button>
        <button class="btn-supprimer">Supprimer</button>
      </div>
    `;

    this.#liste.appendChild(li);
  }

  #toggleTerminer(id) {
    const todo = this.#todos.find(t => t.id === id);
    if (!todo) return;

    todo.termine = !todo.termine;

    const li = this.#liste.querySelector(`[data-id="${id}"]`);
    li.classList.toggle("termine", todo.termine);
    li.querySelector(".btn-terminer").textContent = todo.termine ? "Rouvrir" : "Terminer";
  }

  #supprimer(id) {
    this.#todos = this.#todos.filter(t => t.id !== id);
    this.#liste.querySelector(`[data-id="${id}"]`)?.remove();
  }
}

const app = new TodoApp("#todo-app");
```

---

## Récapitulatif

| Besoin | Méthode |
|---|---|
| Sélectionner un élément | `querySelector(css)` |
| Sélectionner plusieurs | `querySelectorAll(css)` |
| Modifier le texte | `element.textContent = "..."` |
| Modifier le HTML | `element.innerHTML = "..."` (attention XSS) |
| Ajouter une classe | `element.classList.add("classe")` |
| Écouter un événement | `element.addEventListener("click", fn)` |
| Empêcher comportement défaut | `event.preventDefault()` |
| Arrêter la propagation | `event.stopPropagation()` |
| Trouver l'ancêtre | `element.closest(".sélecteur")` |
| Créer un élément | `document.createElement("div")` |
| Insérer un élément | `parent.appendChild(el)` / `parent.prepend(el)` |
| Supprimer un élément | `element.remove()` |
