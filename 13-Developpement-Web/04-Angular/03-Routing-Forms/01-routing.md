# Routing Angular — Navigation SPA

## Configuration du Router

```typescript
// src/app/app.routes.ts
import { Routes } from '@angular/router'

export const routes: Routes = [
  // Route simple
  {
    path: '',
    title: 'Accueil',
    loadComponent: () =>
      import('./features/home/home.component').then((m) => m.HomeComponent),
  },

  // Route avec paramètre
  {
    path: 'users/:id',
    title: 'Profil utilisateur',
    loadComponent: () =>
      import('./features/users/user-detail.component').then(
        (m) => m.UserDetailComponent
      ),
  },

  // Groupe de routes avec layout partagé
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./layouts/dashboard-layout.component').then(
        (m) => m.DashboardLayoutComponent
      ),
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent
          ),
      },
      {
        path: 'profil',
        loadComponent: () =>
          import('./features/profil/profil.component').then(
            (m) => m.ProfilComponent
          ),
      },
    ],
  },

  // Routes protégées avec guard
  {
    path: 'admin',
    canActivate: [authGuard],       // Vérifie l'authentification
    canActivateChild: [roleGuard],  // Vérifie le rôle sur les enfants
    loadChildren: () =>
      import('./features/admin/admin.routes').then((m) => m.adminRoutes),
  },

  // Redirection
  { path: 'home', redirectTo: '', pathMatch: 'full' },

  // Route 404 — doit être en dernier
  {
    path: '**',
    loadComponent: () =>
      import('./pages/not-found.component').then((m) => m.NotFoundComponent),
  },
]
```

```typescript
// src/app/app.config.ts
import { provideRouter, withComponentInputBinding, withViewTransitions } from '@angular/router'

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),  // Injecter les params de route comme @Input
      withViewTransitions(),         // Transitions CSS entre les pages (Angular 17+)
    ),
  ],
}
```

## RouterLink et RouterOutlet

```typescript
// Composant de navigation
@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav>
      <!-- Navigation simple -->
      <a routerLink="/">Accueil</a>

      <!-- routerLinkActive ajoute la classe CSS quand la route est active -->
      <a routerLink="/users" routerLinkActive="active-link">Utilisateurs</a>

      <!-- exact: true → active seulement si l'URL correspond exactement -->
      <a
        routerLink="/"
        routerLinkActive="active-link"
        [routerLinkActiveOptions]="{ exact: true }"
      >
        Accueil exact
      </a>

      <!-- Navigation avec paramètres -->
      <a [routerLink]="['/users', userId]">Mon profil</a>
      <a [routerLink]="['/users', userId, 'posts']">Mes posts</a>

      <!-- Navigation avec query params -->
      <a [routerLink]="['/recherche']" [queryParams]="{ q: terme, page: 1 }">
        Rechercher
      </a>

      <!-- Préserver les query params existants -->
      <a [routerLink]="['/produits']" queryParamsHandling="merge">
        Produits
      </a>
    </nav>

    <!-- router-outlet affiche le composant actif -->
    <router-outlet />
  `,
})
export class NavbarComponent {
  userId = 42
  terme = 'angular'
}
```

## Lire les paramètres de route

### Méthode moderne — `withComponentInputBinding`

```typescript
// Si withComponentInputBinding() est activé dans provideRouter(),
// les paramètres de route sont automatiquement injectés comme @Input

@Component({
  selector: 'app-user-detail',
  standalone: true,
  template: '<p>User ID: {{ id }}</p>',
})
export class UserDetailComponent implements OnInit {
  // ✅ Injections automatiques quand withComponentInputBinding est activé
  @Input() id!: string            // params.id
  @Input() page?: string          // queryParams.page
  @Input() fragment?: string      // fragment (#section)

  ngOnInit(): void {
    this.chargerUser(Number(this.id))
  }
}
```

### Méthode classique — ActivatedRoute

```typescript
import { Component, OnInit, inject, DestroyRef } from '@angular/core'
import { ActivatedRoute, Router } from '@angular/router'
import { takeUntilDestroyed } from '@angular/core/rxjs-interop'
import { map, switchMap } from 'rxjs/operators'

@Component({
  selector: 'app-user-detail',
  standalone: true,
  template: '',
})
export class UserDetailComponent implements OnInit {
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private destroyRef = inject(DestroyRef)

  user: User | null = null

  ngOnInit(): void {
    // Lire un paramètre une seule fois
    const id = this.route.snapshot.params['id']
    const page = this.route.snapshot.queryParams['page']
    const fragment = this.route.snapshot.fragment

    // Observer les changements de paramètres (quand le composant est réutilisé)
    // Ex: navigation /users/1 → /users/2 sans recréer le composant
    this.route.params
      .pipe(
        map((params) => Number(params['id'])),
        switchMap((id) => this.usersService.getById(id)),
        takeUntilDestroyed(this.destroyRef) // Unsubscribe auto à la destruction
      )
      .subscribe((user) => {
        this.user = user
      })

    // Lire les query params réactifs
    this.route.queryParams
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        console.log('Page:', params['page'])
        console.log('Recherche:', params['q'])
      })
  }
}
```

## Navigation programmatique

```typescript
import { Component, inject } from '@angular/core'
import { Router, NavigationExtras } from '@angular/router'

@Component({ selector: 'app-login', standalone: true, template: '' })
export class LoginComponent {
  private router = inject(Router)
  private route = inject(ActivatedRoute)

  apresConnexion(user: User): void {
    // Navigation simple
    this.router.navigate(['/dashboard'])

    // Navigation avec paramètres
    this.router.navigate(['/users', user.id])

    // Navigation avec query params
    this.router.navigate(['/produits'], {
      queryParams: { categorie: 'electronique', page: '1' },
    })

    // Navigation relative (par rapport à la route actuelle)
    this.router.navigate(['../autre'], { relativeTo: this.route })

    // Rediriger vers la page demandée (avant le login)
    const redirect = this.route.snapshot.queryParams['redirect'] || '/dashboard'
    this.router.navigateByUrl(redirect)

    // Replace (sans entrée dans l'historique)
    this.router.navigate(['/home'], { replaceUrl: true })

    // Préserver les query params
    this.router.navigate(['/produits'], { queryParamsHandling: 'preserve' })
  }
}
```

## Guards de navigation

### `canActivate` — Vérifier l'accès avant de naviguer

```typescript
// src/app/guards/auth.guard.ts
import { inject } from '@angular/core'
import { CanActivateFn, Router } from '@angular/router'
import { AuthService } from '@/core/services/auth.service'

// Fonction guard (syntaxe moderne Angular 14+)
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService)
  const router = inject(Router)

  if (authService.isLoggedIn()) {
    return true
  }

  // Rediriger vers le login avec l'URL demandée
  return router.createUrlTree(['/login'], {
    queryParams: { redirect: state.url },
  })
}
```

```typescript
// src/app/guards/role.guard.ts
import { inject } from '@angular/core'
import { CanActivateFn, Router } from '@angular/router'
import { AuthService } from '@/core/services/auth.service'

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService)
  const router = inject(Router)

  // Lire les métadonnées de la route
  const rolesRequis = route.data['roles'] as string[]

  if (!rolesRequis || rolesRequis.length === 0) return true

  const userRole = authService.currentUser()?.role
  if (userRole && rolesRequis.includes(userRole)) {
    return true
  }

  // Accès refusé
  return router.createUrlTree(['/forbidden'])
}
```

```typescript
// Utilisation dans les routes
export const routes: Routes = [
  {
    path: 'dashboard',
    canActivate: [authGuard],  // Vérifie isLoggedIn
    loadComponent: () => import('./dashboard.component'),
  },
  {
    path: 'admin',
    canActivate: [authGuard, roleGuard],
    data: { roles: ['admin'] },  // Meta-données lues par roleGuard
    loadComponent: () => import('./admin.component'),
  },
]
```

### `canDeactivate` — Confirmation avant de quitter

```typescript
// src/app/guards/unsaved-changes.guard.ts
import { CanDeactivateFn } from '@angular/router'

// Interface pour les composants avec modifications non sauvegardées
export interface HasUnsavedChanges {
  hasUnsavedChanges(): boolean
}

export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (
  component
) => {
  if (component.hasUnsavedChanges()) {
    return confirm(
      'Vous avez des modifications non sauvegardées. Quitter quand même ?'
    )
  }
  return true
}
```

```typescript
// Implémenter l'interface dans le composant
@Component({ selector: 'app-edit-form', standalone: true, template: '' })
export class EditFormComponent implements HasUnsavedChanges {
  formModified = false

  hasUnsavedChanges(): boolean {
    return this.formModified
  }
}

// Dans les routes
{
  path: 'edit',
  component: EditFormComponent,
  canDeactivate: [unsavedChangesGuard],
}
```

### `resolve` — Pré-charger des données

```typescript
// src/app/resolvers/user.resolver.ts
import { inject } from '@angular/core'
import { ResolveFn, Router } from '@angular/router'
import { catchError, EMPTY } from 'rxjs'
import { UsersService, User } from '@/features/users/users.service'

export const userResolver: ResolveFn<User> = (route) => {
  const usersService = inject(UsersService)
  const router = inject(Router)
  const id = Number(route.params['id'])

  return usersService.getById(id).pipe(
    catchError(() => {
      // Rediriger vers 404 si l'utilisateur n'existe pas
      router.navigate(['/not-found'])
      return EMPTY
    })
  )
}
```

```typescript
// Utilisation dans les routes
{
  path: 'users/:id',
  component: UserDetailComponent,
  resolve: {
    user: userResolver,  // Les données sont disponibles avant le rendu
  },
}

// Dans le composant — lire les données résolues
@Component({ ... })
export class UserDetailComponent implements OnInit {
  private route = inject(ActivatedRoute)
  user!: User

  ngOnInit(): void {
    this.user = this.route.snapshot.data['user']
    // Pas besoin d'état loading — les données sont déjà là
  }
}
```

## Lazy Loading — Chargement différé des routes

```typescript
// routes par fonctionnalité (feature modules)
// src/app/app.routes.ts
export const routes: Routes = [
  { path: '', loadComponent: () => import('./home.component').then(m => m.HomeComponent) },

  // Lazy loading d'un composant
  {
    path: 'users',
    loadComponent: () =>
      import('./features/users/user-list.component').then(
        (m) => m.UserListComponent
      ),
  },

  // Lazy loading d'un groupe de routes (sous-module)
  {
    path: 'admin',
    loadChildren: () =>
      import('./features/admin/admin.routes').then((m) => m.adminRoutes),
  },
]
```

```typescript
// src/app/features/admin/admin.routes.ts
import { Routes } from '@angular/router'

export const adminRoutes: Routes = [
  { path: '', loadComponent: () => import('./dashboard.component') },
  { path: 'users', loadComponent: () => import('./user-management.component') },
  { path: 'settings', loadComponent: () => import('./settings.component') },
]
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur — onglet Network pendant une navigation vers une route lazy-loadée
> **Expliquer :** Naviguer vers une route avec lazy loading et montrer dans l'onglet Network qu'un nouveau chunk JavaScript est téléchargé au moment de la navigation. Montrer la différence de taille du bundle initial entre "tout importé" et "lazy loading". Démontrer aussi le comportement des guards en essayant d'accéder à une route protégée sans être connecté — la redirection vers /login.
---

## Transitions de vue (Angular 17+)

```typescript
// app.config.ts
import { provideRouter, withViewTransitions } from '@angular/router'

provideRouter(routes, withViewTransitions({
  skipInitialTransition: true,
}))
```

```css
/* styles.scss — styles des transitions */
::view-transition-old(root) {
  animation: 300ms ease-out fadeOut;
}

::view-transition-new(root) {
  animation: 300ms ease-in fadeIn;
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## Résumé

| Concept | Description | API |
|---|---|---|
| `loadComponent` | Lazy load un composant | `() => import('./comp')` |
| `loadChildren` | Lazy load des routes | `() => import('./routes')` |
| `routerLink` | Lien déclaratif | `[routerLink]="['/users', id]"` |
| `RouterOutlet` | Zone d'affichage | `<router-outlet />` |
| `ActivatedRoute` | Lire les params | `inject(ActivatedRoute)` |
| `Router` | Navigation programmatique | `router.navigate(['/path'])` |
| `canActivate` | Guard d'accès | `canActivate: [authGuard]` |
| `canDeactivate` | Guard de sortie | `canDeactivate: [unsavedGuard]` |
| `resolve` | Pré-charger les données | `resolve: { data: resolver }` |

**Prochaine étape :** Formulaires réactifs (Reactive Forms) →
