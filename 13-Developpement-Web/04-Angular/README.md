# Formation Angular — Guide Complet

## Objectifs pédagogiques

À l'issue de cette formation, les apprenants seront capables de :

- Comprendre l'architecture Angular (modules, composants, services, injection de dépendances)
- Créer des composants avec `@Component`, `@Input`/`@Output`
- Gérer la communication avec des APIs REST via `HttpClient`
- Naviguer entre les vues avec le Router Angular
- Créer des formulaires réactifs avec validation
- Maîtriser les bases de RxJS (Observable, opérateurs)

## Prérequis

- TypeScript solide (classes, interfaces, décorateurs, génériques)
- HTML / CSS
- Notions de programmation orientée objet
- Node.js 18+ installé

## Plan de la formation

### Module 1 — Fondamentaux (3h)

| Fichier | Contenu |
|---|---|
| `Fondamentaux/01-introduction.md` | Angular CLI, structure, TypeScript first |
| `Fondamentaux/02-composants.md` | @Component, @Input/@Output, lifecycle hooks |
| `Fondamentaux/03-templates.md` | Interpolation, ngIf, ngFor, pipes |

### Module 2 — Services & DI (2h)

| Fichier | Contenu |
|---|---|
| `Services-DI/01-services.md` | @Injectable, injection de dépendances |
| `Services-DI/02-http-client.md` | HttpClient, GET/POST, intercepteurs |

### Module 3 — Routing & Formulaires (2h)

| Fichier | Contenu |
|---|---|
| `Routing-Forms/01-routing.md` | RouterModule, routerLink, guards, lazy loading |
| `Routing-Forms/02-formulaires.md` | Reactive Forms, FormBuilder, Validators |

### Module 4 — RxJS Avancé (1h)

| Fichier | Contenu |
|---|---|
| `Avance/01-rxjs.md` | Observable, Subject, map/filter/switchMap/combineLatest |

### Exercices pratiques

| Fichier | Contenu |
|---|---|
| `exercices/exercice-01-todo-angular.md` | Application Todo complète |
| `exercices/exercice-02-crud-api.md` | CRUD complet avec API REST |

## Installation rapide

```bash
# Installer Angular CLI globalement
npm install -g @angular/cli

# Vérifier l'installation
ng version

# Créer un nouveau projet
ng new mon-app-angular
# TypeScript: oui (par défaut)
# Routing: Yes
# Style: SCSS (recommandé)

cd mon-app-angular
ng serve
# Ouvrir http://localhost:4200
```

## Ressources officielles

- Documentation Angular : https://angular.dev
- Angular CLI : https://cli.angular.io
- Angular Material : https://material.angular.io
- RxJS : https://rxjs.dev

## Angular vs Vue vs React

| Critère | Angular | Vue 3 | React |
|---|---|---|---|
| Langue | TypeScript (obligatoire) | JS/TS (optionnel) | JS/TS (optionnel) |
| Architecture | MVC + DI (opinionated) | Flexible | Flexible |
| Courbe d'apprentissage | Raide | Douce | Moyenne |
| Taille bundle | Plus grand | Petit | Petit |
| Idéal pour | Grandes applications d'entreprise | Tout | Tout |
| État | NgRx / Services | Pinia | Redux / Zustand |
| CLI | Très puissante (génération de code) | Vite | CRA / Vite |

## Convention de nommage Angular

```
user.component.ts        // Composant
user.service.ts          // Service
user.model.ts            // Interface/classe modèle
user.guard.ts            // Guard de route
user.interceptor.ts      // Intercepteur HTTP
user.pipe.ts             // Pipe
user.module.ts           // Module (Angular < 17)
user.component.spec.ts   // Tests unitaires
```
