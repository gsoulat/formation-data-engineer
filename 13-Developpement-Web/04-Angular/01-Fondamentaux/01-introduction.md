# Angular — Introduction et mise en place

## Qu'est-ce qu'Angular ?

Angular est un framework front-end complet développé et maintenu par Google. Contrairement à Vue ou React qui sont des bibliothèques, Angular est un **framework opinionated** qui impose une architecture, des conventions et fournit tous les outils nécessaires :

- **Composants** — les briques de l'interface
- **Services** — la logique métier injectable
- **Routing** — la navigation SPA
- **Formulaires** — Template-driven et Reactive Forms
- **HTTP Client** — les appels API
- **DI (Dependency Injection)** — gestion des dépendances
- **RxJS** — programmation réactive
- **CLI** — génération de code et build

### Versions et évolution

- Angular 1 (AngularJS) — 2010, JavaScript pur, **complètement différent**
- Angular 2+ — 2016, réécriture totale en TypeScript
- Angular 17+ (2023) — Standalone Components, Signals, nouvelle syntaxe `@if`/`@for`
- Angular 19+ (2024) — Signals stables, améliorations performances

> **Dans ce cours**, nous utilisons Angular 17+ avec les Standalone Components (pas de NgModules), la nouvelle syntaxe de template, et TypeScript strict.

## Pourquoi Angular dans une entreprise ?

- **Uniformité** — tout le monde code de la même façon (moins de débat architectural)
- **TypeScript natif** — impossible de contourner le typage fort
- **CLI puissante** — génération de composants, services, guards en une commande
- **Tests intégrés** — Jasmine + Karma (unitaires) / Cypress (e2e) out-of-the-box
- **Idéal pour les grandes équipes** — conventions strictes réduisent les frictions

## Installation de l'Angular CLI

```bash
# Installer Angular CLI globalement
npm install -g @angular/cli

# Vérifier l'installation
ng version

# Résultat attendu :
#     _                      _                 ____ _     ___
#    / \   _ __   __ _ _   _| | __ _ _ __     / ___| |   |_ _|
#   / △ \ | '_ \ / _` | | | | |/ _` | '__|   | |   | |    | |
#  / ___ \| | | | (_| | |_| | | (_| | |      | |___| |___ | |
# /_/   \_\_| |_|\__, |\__,_|_|\__,_|_|       \____|_____|___|
#
# Angular CLI: 17.x.x
# Node: 20.x.x
# Package Manager: npm
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec l'exécution de `ng version` montrant la version installée
> **Expliquer :** Montrer le résultat de ng version, insister sur la version Angular CLI. Expliquer que l'Angular CLI est beaucoup plus puissante que les CLIs des autres frameworks — elle permet de générer du code, lancer les tests, builder, déployer, tout en ligne de commande.
---

## Créer un projet Angular

```bash
# Création interactive — ng new pose des questions
ng new mon-app-angular

# Résultat des questions :
# ? Which stylesheet format would you like to use? SCSS
# ? Do you want to enable Server-Side Rendering (SSR)? No

# Ou avec les options passées directement
ng new mon-app-angular --style=scss --ssr=false --standalone
```

### Lancer le serveur de développement

```bash
cd mon-app-angular
ng serve
# ou ng serve --open  (ouvre automatiquement le navigateur)

# Port personnalisé
ng serve --port 4201
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `ng new` en action avec les questions interactives, puis `ng serve` et le résultat dans le navigateur
> **Expliquer :** Montrer toutes les étapes de création du projet. Insister sur le temps de compilation initial (plus long que Vue/Vite). Montrer l'application par défaut sur http://localhost:4200. Expliquer que Angular compile TypeScript + templates à chaque sauvegarde (hot reload).
---

## Structure d'un projet Angular

```
mon-app-angular/
├── src/
│   ├── app/
│   │   ├── app.component.ts          # Composant racine
│   │   ├── app.component.html        # Template du composant racine
│   │   ├── app.component.scss        # Styles du composant racine
│   │   ├── app.component.spec.ts     # Tests unitaires
│   │   └── app.config.ts             # Configuration de l'application
│   ├── assets/                       # Fichiers statiques (images, fonts)
│   ├── index.html                    # HTML principal
│   ├── main.ts                       # Point d'entrée
│   └── styles.scss                   # Styles globaux
├── angular.json                      # Configuration Angular CLI
├── tsconfig.json                     # Configuration TypeScript
├── tsconfig.app.json                 # TS config pour l'app
├── package.json
└── .editorconfig
```

### `main.ts` — Point d'entrée

```typescript
// src/main.ts
import { bootstrapApplication } from '@angular/platform-browser'
import { appConfig } from './app/app.config'
import { AppComponent } from './app/app.component'

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err))
```

### `app.config.ts` — Configuration

```typescript
// src/app/app.config.ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core'
import { provideRouter } from '@angular/router'
import { provideHttpClient, withFetch } from '@angular/common/http'
import { routes } from './app.routes'

export const appConfig: ApplicationConfig = {
  providers: [
    // Optimisation de la détection de changements
    provideZoneChangeDetection({ eventCoalescing: true }),
    // Routing
    provideRouter(routes),
    // HTTP Client (avec l'API Fetch moderne)
    provideHttpClient(withFetch()),
  ],
}
```

### Composant racine `app.component.ts`

```typescript
// src/app/app.component.ts
import { Component } from '@angular/core'
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router'

@Component({
  selector: 'app-root',         // La balise HTML qui représente ce composant
  standalone: true,              // Composant autonome (pas besoin de NgModule)
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'mon-app-angular'
}
```

```html
<!-- src/app/app.component.html -->
<nav>
  <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
    Accueil
  </a>
  <a routerLink="/about" routerLinkActive="active">À propos</a>
</nav>

<!-- router-outlet affiche le composant de la route active -->
<router-outlet />
```

## La CLI Angular — commandes essentielles

### Générer des fichiers

```bash
# Générer un composant
ng generate component components/user-card
# Raccourci
ng g c components/user-card

# Résultat :
# CREATE src/app/components/user-card/user-card.component.ts
# CREATE src/app/components/user-card/user-card.component.html
# CREATE src/app/components/user-card/user-card.component.scss
# CREATE src/app/components/user-card/user-card.component.spec.ts

# Générer un service
ng g s services/user
# CREATE src/app/services/user.service.ts
# CREATE src/app/services/user.service.spec.ts

# Générer une interface
ng g interface models/user
# CREATE src/app/models/user.ts

# Générer un guard de route
ng g guard guards/auth
# CREATE src/app/guards/auth.guard.ts

# Générer un intercepteur HTTP
ng g interceptor interceptors/auth
# CREATE src/app/interceptors/auth.interceptor.ts

# Générer un pipe
ng g pipe pipes/truncate
# CREATE src/app/pipes/truncate.pipe.ts

# Options utiles
ng g c mon-composant --inline-template    # template dans le .ts
ng g c mon-composant --inline-style       # style dans le .ts
ng g c mon-composant --skip-tests         # sans le .spec.ts
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec l'exécution de `ng g c components/user-card` et les 4 fichiers créés automatiquement
> **Expliquer :** Montrer en détail ce que la CLI génère. Expliquer que cette génération automatique est un des grands atouts d'Angular — on n'a pas à créer les fichiers manuellement. Montrer les 4 fichiers créés dans VSCode. Comparer avec la création manuelle en Vue (un seul fichier .vue). Angular est plus verbeux mais plus structuré.
---

### Autres commandes CLI utiles

```bash
# Build pour la production
ng build
# Résultat dans dist/mon-app-angular/

# Build en mode watch (rebuild à chaque changement)
ng build --watch

# Lancer les tests unitaires
ng test

# Lancer les tests e2e
ng e2e

# Analyser la taille du bundle
ng build --stats-json
npx webpack-bundle-analyzer dist/mon-app-angular/stats.json

# Mettre à jour Angular
ng update @angular/core @angular/cli

# Ajouter une bibliothèque
ng add @angular/material   # Angular Material
ng add @ngrx/store         # NgRx (state management)
```

## TypeScript First — la philosophie Angular

Angular impose TypeScript strict. Voici les patterns TypeScript indispensables :

### Classes et décorateurs

```typescript
// Angular utilise massivement les décorateurs TypeScript
// Décorateur = annotation qui ajoute des métadonnées à une classe

@Component({ ... })          // Un composant Angular
export class UserComponent { }

@Injectable({ providedIn: 'root' })  // Un service injectable
export class UserService { }

@Pipe({ name: 'truncate' })         // Un pipe
export class TruncatePipe { }

// Les décorateurs sont une fonctionnalité TypeScript/ES
// (équivalent aux annotations Java, attributs C#)
```

### Interfaces et modèles

```typescript
// src/app/models/user.model.ts
export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  createdAt: string
}

export type UserRole = 'admin' | 'user' | 'guest'

export interface ApiResponse<T> {
  data: T
  message: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// DTO (Data Transfer Object) — payload pour les requêtes
export interface CreateUserDto {
  name: string
  email: string
  password: string
  role?: UserRole
}

export interface UpdateUserDto extends Partial<Omit<CreateUserDto, 'password'>> {
  id: number
}
```

## `tsconfig.json` — Configuration TypeScript recommandée

```json
{
  "compilerOptions": {
    "strict": true,                // Active tous les checks stricts
    "strictNullChecks": true,      // null et undefined doivent être gérés explicitement
    "noImplicitAny": true,         // Pas de 'any' implicite
    "strictPropertyInitialization": true,  // Toutes les propriétés doivent être initialisées
    "forceConsistentCasingInFileNames": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## Structure recommandée d'un projet Angular

```
src/app/
├── core/                    # Services singleton, guards, intercepteurs
│   ├── guards/
│   │   └── auth.guard.ts
│   ├── interceptors/
│   │   └── auth.interceptor.ts
│   └── services/
│       └── auth.service.ts
├── shared/                  # Composants/pipes/directives partagés
│   ├── components/
│   │   ├── button/
│   │   └── spinner/
│   └── pipes/
│       └── truncate.pipe.ts
├── features/                # Fonctionnalités par domaine métier
│   ├── users/
│   │   ├── user-list/
│   │   ├── user-detail/
│   │   ├── user-form/
│   │   └── users.service.ts
│   └── products/
│       ├── product-list/
│       └── products.service.ts
├── models/                  # Interfaces et types
│   ├── user.model.ts
│   └── product.model.ts
├── app.component.ts
├── app.config.ts
└── app.routes.ts
```

## Angular Signals — la modernité (Angular 16+)

Angular 17+ introduit les **Signals**, une nouvelle façon de gérer la réactivité (similaire aux refs Vue) :

```typescript
import { signal, computed, effect } from '@angular/core'

// signal() — valeur réactive (similaire à ref() en Vue)
const count = signal(0)
const name = signal('Alice')

// computed() — valeur dérivée (similaire à computed() Vue)
const doubled = computed(() => count() * 2)

// Lire un signal → appel de fonction
console.log(count())        // 0
console.log(doubled())      // 0

// Modifier un signal
count.set(5)                // définir
count.update(n => n + 1)    // modifier avec une fonction
count.mutate(n => n++)      // pour les objets/tableaux

// effect() — effet de bord automatique (similaire à watchEffect Vue)
effect(() => {
  console.log(`Count est maintenant: ${count()}`)
  // Angular détecte automatiquement les dépendances
})
```

## Résumé

- Angular est un framework **complet** et **opinionated** — idéal pour les grandes applications d'entreprise
- **TypeScript est obligatoire** — pas d'option JavaScript
- La **CLI** est très puissante — elle génère, build, teste tout
- Structure en **composants**, **services**, **modules** (ou standalone)
- Deux systèmes de réactivité : **Zone.js** (classique) et **Signals** (moderne, Angular 16+)

**Prochaine étape :** Les composants Angular — @Component, @Input/@Output, lifecycle hooks →
