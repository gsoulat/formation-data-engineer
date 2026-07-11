# Services et Injection de Dépendances

## Qu'est-ce qu'un service Angular ?

Un service est une classe TypeScript qui encapsule de la logique réutilisable : appels API, gestion d'état, utilitaires, etc. Les services sont partagés entre les composants grâce à l'**injection de dépendances (DI)**.

**Règle de base :** Les composants gèrent l'affichage. Les services gèrent la logique métier.

```
Component (template + interactions UI)
    ↓ injecte
Service (logique métier, appels API, état)
    ↓ appelle
API REST / Base de données / LocalStorage
```

## Créer un service

```bash
ng generate service services/user
# ou
ng g s services/user

# Génère :
# src/app/services/user.service.ts
# src/app/services/user.service.spec.ts
```

```typescript
// src/app/services/user.service.ts
import { Injectable } from '@angular/core'

// providedIn: 'root' → service singleton disponible dans toute l'application
// C'est la configuration la plus courante
@Injectable({
  providedIn: 'root',
})
export class UserService {
  // Pas de constructeur requis si pas de dépendances
  private users: User[] = []

  getAll(): User[] {
    return this.users
  }

  getById(id: number): User | undefined {
    return this.users.find((u) => u.id === id)
  }

  add(user: User): void {
    this.users.push(user)
  }
}
```

## Injection de dépendances — comment ça fonctionne

Angular maintient un **conteneur d'injection** qui instancie les services et les fournit aux composants qui en ont besoin.

```typescript
// Méthode 1 : inject() — syntaxe moderne (Angular 14+, recommandée)
import { Component, inject, OnInit } from '@angular/core'
import { UserService } from '@/services/user.service'

@Component({ selector: 'app-users', standalone: true, template: '' })
export class UsersComponent implements OnInit {
  // inject() peut être appelé n'importe où dans le contexte d'injection
  private userService = inject(UserService)

  users: User[] = []

  ngOnInit(): void {
    this.users = this.userService.getAll()
  }
}

// Méthode 2 : Constructeur (ancienne méthode, toujours valide)
@Component({ selector: 'app-users', standalone: true, template: '' })
export class UsersComponent implements OnInit {
  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.users = this.userService.getAll()
  }
}
```

## Service avec état — Pattern StateService

```typescript
// src/app/services/cart.service.ts
import { Injectable, signal, computed } from '@angular/core'

export interface CartItem {
  id: number
  nom: string
  prix: number
  quantite: number
  image: string
}

@Injectable({ providedIn: 'root' })
export class CartService {
  // État interne avec Signals
  private _items = signal<CartItem[]>([])

  // Exposer en lecture seule (les composants ne peuvent pas modifier directement)
  readonly items = this._items.asReadonly()

  // Computed signals
  readonly totalItems = computed(() =>
    this._items().reduce((sum, item) => sum + item.quantite, 0)
  )

  readonly totalPrix = computed(() =>
    this._items().reduce((sum, item) => sum + item.prix * item.quantite, 0)
  )

  readonly isEmpty = computed(() => this._items().length === 0)

  // Méthodes qui modifient l'état
  ajouterArticle(produit: Omit<CartItem, 'quantite'>, quantite = 1): void {
    this._items.update((items) => {
      const existant = items.find((i) => i.id === produit.id)
      if (existant) {
        return items.map((i) =>
          i.id === produit.id ? { ...i, quantite: i.quantite + quantite } : i
        )
      }
      return [...items, { ...produit, quantite }]
    })
  }

  retirerArticle(id: number): void {
    this._items.update((items) => items.filter((i) => i.id !== id))
  }

  modifierQuantite(id: number, quantite: number): void {
    if (quantite <= 0) {
      this.retirerArticle(id)
      return
    }
    this._items.update((items) =>
      items.map((i) => (i.id === id ? { ...i, quantite } : i))
    )
  }

  vider(): void {
    this._items.set([])
  }
}
```

```typescript
// Utilisation dans plusieurs composants — l'état est partagé
@Component({
  selector: 'app-header',
  standalone: true,
  template: `
    <nav>
      <button class="panier-btn">
        🛒 {{ cart.totalItems() }} article(s) — {{ cart.totalPrix() | currency:'EUR' }}
      </button>
    </nav>
  `,
})
export class HeaderComponent {
  cart = inject(CartService)
}
```

## Service d'authentification — exemple complet

```typescript
// src/app/core/services/auth.service.ts
import { Injectable, signal, computed, inject } from '@angular/core'
import { HttpClient } from '@angular/common/http'
import { Router } from '@angular/router'
import { Observable, tap, catchError, throwError } from 'rxjs'
import { environment } from '@env/environment'

export interface User {
  id: number
  email: string
  prenom: string
  nom: string
  role: 'admin' | 'user'
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  user: User
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient)
  private router = inject(Router)

  private readonly TOKEN_KEY = 'auth_token'

  // État interne avec Signals
  private _currentUser = signal<User | null>(null)
  private _token = signal<string | null>(
    localStorage.getItem(this.TOKEN_KEY)
  )
  private _loading = signal(false)
  private _error = signal<string | null>(null)

  // API publique (lecture seule)
  readonly currentUser = this._currentUser.asReadonly()
  readonly isLoggedIn = computed(() => !!this._token() && !!this._currentUser())
  readonly isAdmin = computed(() => this._currentUser()?.role === 'admin')
  readonly fullName = computed(() => {
    const user = this._currentUser()
    return user ? `${user.prenom} ${user.nom}` : 'Invité'
  })
  readonly loading = this._loading.asReadonly()
  readonly error = this._error.asReadonly()

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    this._loading.set(true)
    this._error.set(null)

    return this.http
      .post<AuthResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          // Sauvegarder le token
          this._token.set(response.token)
          this._currentUser.set(response.user)
          localStorage.setItem(this.TOKEN_KEY, response.token)
          this._loading.set(false)
        }),
        catchError((err) => {
          this._error.set(err.error?.message || 'Identifiants incorrects')
          this._loading.set(false)
          return throwError(() => err)
        })
      )
  }

  loadCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me`).pipe(
      tap((user) => this._currentUser.set(user)),
      catchError((err) => {
        // Token invalide ou expiré
        this.logout()
        return throwError(() => err)
      })
    )
  }

  logout(): void {
    this._token.set(null)
    this._currentUser.set(null)
    localStorage.removeItem(this.TOKEN_KEY)
    this.router.navigate(['/login'])
  }

  getToken(): string | null {
    return this._token()
  }
}
```

## Service de notifications (Toasts)

```typescript
// src/app/core/services/notification.service.ts
import { Injectable, signal } from '@angular/core'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  message: string
  type: NotificationType
  titre?: string
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private _notifications = signal<Notification[]>([])
  readonly notifications = this._notifications.asReadonly()

  private nextId = 1

  private ajouter(
    message: string,
    type: NotificationType,
    titre?: string,
    duree = 4000
  ): void {
    const id = this.nextId++
    this._notifications.update((notifs) => [
      ...notifs,
      { id, message, type, titre },
    ])

    if (duree > 0) {
      setTimeout(() => this.supprimer(id), duree)
    }
  }

  succes(message: string, titre = 'Succès'): void {
    this.ajouter(message, 'success', titre)
  }

  erreur(message: string, titre = 'Erreur'): void {
    this.ajouter(message, 'error', titre, 6000)
  }

  avertissement(message: string, titre = 'Attention'): void {
    this.ajouter(message, 'warning', titre)
  }

  info(message: string, titre?: string): void {
    this.ajouter(message, 'info', titre)
  }

  supprimer(id: number): void {
    this._notifications.update((notifs) => notifs.filter((n) => n.id !== id))
  }

  tout_supprimer(): void {
    this._notifications.set([])
  }
}
```

```typescript
// Composant Toast — affiche les notifications
@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container">
      @for (notif of notifService.notifications(); track notif.id) {
        <div class="toast" [class]="'toast-' + notif.type">
          <strong *ngIf="notif.titre">{{ notif.titre }}</strong>
          <p>{{ notif.message }}</p>
          <button (click)="notifService.supprimer(notif.id)">×</button>
        </div>
      }
    </div>
  `,
})
export class ToastContainerComponent {
  notifService = inject(NotificationService)
}

// Dans app.component.html — ajouter une seule fois
// <app-toast-container />
```

## Scopes d'injection — où le service est instancié

```typescript
// 1. providedIn: 'root' — Singleton global (le plus courant)
@Injectable({ providedIn: 'root' })
export class GlobalService { }
// → Une seule instance pour toute l'application

// 2. Fournir dans un composant → instance unique pour ce composant et ses enfants
@Component({
  selector: 'app-feature',
  standalone: true,
  providers: [FeatureService], // Nouvelle instance ici
  template: '',
})
export class FeatureComponent {
  featureService = inject(FeatureService)
  // Ses composants enfants injectent la MÊME instance
}
// → Utile pour isoler l'état d'une fonctionnalité

// 3. Fournir dans la route (lazy feature)
// Dans app.routes.ts :
{
  path: 'admin',
  loadComponent: () => import('./admin/admin.component'),
  providers: [AdminService] // Scope de la route admin
}
```

## Injection conditionnelle et optionnelle

```typescript
import { inject, Optional, InjectionToken } from '@angular/core'

// Créer un token d'injection pour des valeurs de configuration
const API_URL = new InjectionToken<string>('API_URL', {
  providedIn: 'root',
  factory: () => 'http://localhost:3000/api', // Valeur par défaut
})

// Fournir une valeur dans app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: API_URL, useValue: environment.apiUrl },
  ],
}

// Injecter
@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = inject(API_URL) // string directement
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur avec Angular DevTools, onglet "Injector Tree" — montrer l'arbre des injections
> **Expliquer :** Ouvrir Angular DevTools → onglet "Injector Tree". Montrer comment Angular résout les dépendances du haut vers le bas de l'arbre. Injecter le même service dans deux composants différents et montrer que c'est la MÊME instance (modifier l'état dans l'un, voir le changement dans l'autre). C'est ça, le singleton pattern via DI.
---

## Résumé

| Concept | Description | Code |
|---|---|---|
| `@Injectable` | Déclarer un service | `@Injectable({ providedIn: 'root' })` |
| `inject()` | Injecter un service (moderne) | `private svc = inject(MonService)` |
| Constructeur DI | Injecter (classique) | `constructor(private svc: MonService)` |
| `signal()` | État réactif dans un service | `private _state = signal<T>(init)` |
| `asReadonly()` | Exposer en lecture seule | `readonly state = this._state.asReadonly()` |
| `InjectionToken` | Token pour les valeurs non-class | `new InjectionToken<string>('URL')` |

**Prochaine étape :** HttpClient — appels API REST →
