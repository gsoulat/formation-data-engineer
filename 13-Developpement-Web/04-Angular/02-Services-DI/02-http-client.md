# HttpClient — Appels API REST

## Configuration

```typescript
// src/app/app.config.ts
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http'
import { authInterceptor } from './interceptors/auth.interceptor'

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withFetch(),           // Utiliser l'API Fetch moderne (recommandé)
      withInterceptors([authInterceptor]),  // Ajouter les intercepteurs
    ),
  ],
}
```

## Méthodes HTTP de base

```typescript
// src/app/services/api.service.ts
import { Injectable, inject } from '@angular/core'
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http'
import { Observable } from 'rxjs'
import { environment } from '@env/environment'

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient)
  private baseUrl = environment.apiUrl  // 'http://localhost:3000/api'

  // GET — récupérer des données
  get<T>(endpoint: string, params?: Record<string, string>): Observable<T> {
    let httpParams = new HttpParams()
    if (params) {
      Object.entries(params).forEach(([cle, valeur]) => {
        if (valeur !== null && valeur !== undefined) {
          httpParams = httpParams.set(cle, valeur)
        }
      })
    }
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, { params: httpParams })
  }

  // POST — créer une ressource
  post<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body)
  }

  // PUT — remplacer une ressource
  put<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, body)
  }

  // PATCH — modifier partiellement
  patch<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${endpoint}`, body)
  }

  // DELETE — supprimer
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`)
  }
}
```

## Service CRUD complet — UsersService

```typescript
// src/app/features/users/users.service.ts
import { Injectable, inject } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable, map, catchError, throwError } from 'rxjs'
import { environment } from '@env/environment'

export interface User {
  id: number
  prenom: string
  nom: string
  email: string
  role: string
  createdAt: string
}

export interface UserListResponse {
  data: User[]
  total: number
  page: number
  pageSize: number
}

export interface CreateUserDto {
  prenom: string
  nom: string
  email: string
  password: string
  role?: string
}

@Injectable({ providedIn: 'root' })
export class UsersService {
  private http = inject(HttpClient)
  private readonly url = `${environment.apiUrl}/users`

  // Récupérer tous les utilisateurs avec pagination et filtres
  getAll(page = 1, pageSize = 10, recherche?: string): Observable<UserListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString())

    if (recherche?.trim()) {
      params = params.set('search', recherche.trim())
    }

    return this.http.get<UserListResponse>(this.url, { params })
  }

  // Récupérer un utilisateur par ID
  getById(id: number): Observable<User> {
    return this.http.get<User>(`${this.url}/${id}`)
  }

  // Créer un utilisateur
  create(dto: CreateUserDto): Observable<User> {
    return this.http.post<User>(this.url, dto)
  }

  // Modifier un utilisateur
  update(id: number, dto: Partial<CreateUserDto>): Observable<User> {
    return this.http.put<User>(`${this.url}/${id}`, dto)
  }

  // Supprimer un utilisateur
  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`)
  }
}
```

## Utiliser HttpClient dans un composant

```typescript
// src/app/features/users/user-list.component.ts
import { Component, OnInit, signal, inject } from '@angular/core'
import { CommonModule } from '@angular/common'
import { UsersService, User } from './users.service'
import { NotificationService } from '@/core/services/notification.service'

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loading()) {
      <div class="spinner">Chargement...</div>
    } @else if (error()) {
      <div class="error">
        {{ error() }}
        <button (click)="charger()">Réessayer</button>
      </div>
    } @else {
      <div class="list">
        @for (user of users(); track user.id) {
          <div class="user-item">
            <strong>{{ user.prenom }} {{ user.nom }}</strong>
            <span>{{ user.email }}</span>
            <button (click)="supprimer(user.id)">Supprimer</button>
          </div>
        }
      </div>
    }
  `,
})
export class UserListComponent implements OnInit {
  private usersService = inject(UsersService)
  private notifs = inject(NotificationService)

  users = signal<User[]>([])
  loading = signal(false)
  error = signal<string | null>(null)

  ngOnInit(): void {
    this.charger()
  }

  charger(): void {
    this.loading.set(true)
    this.error.set(null)

    // subscribe() pour déclencher la requête HTTP (les Observables sont lazy!)
    this.usersService.getAll().subscribe({
      next: (response) => {
        this.users.set(response.data)
        this.loading.set(false)
      },
      error: (err) => {
        this.error.set(err.message || 'Erreur lors du chargement')
        this.loading.set(false)
      },
    })
  }

  supprimer(id: number): void {
    if (!confirm('Confirmer la suppression ?')) return

    this.usersService.delete(id).subscribe({
      next: () => {
        this.users.update((users) => users.filter((u) => u.id !== id))
        this.notifs.succes('Utilisateur supprimé')
      },
      error: (err) => {
        this.notifs.erreur(`Impossible de supprimer : ${err.message}`)
      },
    })
  }
}
```

## Intercepteurs HTTP

Les intercepteurs permettent d'intercepter toutes les requêtes et réponses HTTP pour ajouter des en-têtes, gérer les erreurs globalement, etc.

### Intercepteur d'authentification

```typescript
// src/app/interceptors/auth.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http'
import { inject } from '@angular/core'
import { catchError, throwError } from 'rxjs'
import { Router } from '@angular/router'
import { AuthService } from '@/core/services/auth.service'

// Syntaxe fonctionnelle (Angular 15+)
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService)
  const router = inject(Router)

  const token = authService.getToken()

  // Cloner la requête et ajouter le header Authorization
  const reqAvecToken = token
    ? req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`),
      })
    : req

  return next(reqAvecToken).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) {
        // Token expiré ou invalide — déconnecter
        authService.logout()
        router.navigate(['/login'])
      }

      if (err.status === 403) {
        router.navigate(['/forbidden'])
      }

      return throwError(() => err)
    })
  )
}
```

### Intercepteur de logging

```typescript
// src/app/interceptors/logging.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http'
import { tap, finalize } from 'rxjs/operators'

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const debut = Date.now()
  console.log(`[HTTP] → ${req.method} ${req.url}`)

  return next(req).pipe(
    tap({
      next: (event) => {
        // 'response' uniquement (pas les 'sent' events)
      },
      error: (err) => {
        console.error(`[HTTP] ✗ ${req.method} ${req.url} — ${err.status}: ${err.message}`)
      },
    }),
    finalize(() => {
      const duree = Date.now() - debut
      console.log(`[HTTP] ← ${req.method} ${req.url} — ${duree}ms`)
    })
  )
}
```

### Intercepteur de cache

```typescript
// src/app/interceptors/cache.interceptor.ts
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http'
import { of, tap } from 'rxjs'

const cache = new Map<string, HttpResponse<unknown>>()
const CACHE_DURATION_MS = 60_000 // 1 minute

interface CacheEntry {
  response: HttpResponse<unknown>
  expiresAt: number
}

const cacheStore = new Map<string, CacheEntry>()

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  // Ne cacher que les GET
  if (req.method !== 'GET') return next(req)

  const entree = cacheStore.get(req.url)
  if (entree && Date.now() < entree.expiresAt) {
    console.log(`[Cache] HIT: ${req.url}`)
    return of(entree.response.clone())
  }

  return next(req).pipe(
    tap((event) => {
      if (event instanceof HttpResponse) {
        cacheStore.set(req.url, {
          response: event.clone(),
          expiresAt: Date.now() + CACHE_DURATION_MS,
        })
        console.log(`[Cache] MISS (stored): ${req.url}`)
      }
    })
  )
}
```

### Enregistrer plusieurs intercepteurs

```typescript
// src/app/app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http'
import { authInterceptor } from './interceptors/auth.interceptor'
import { loggingInterceptor } from './interceptors/logging.interceptor'
import { cacheInterceptor } from './interceptors/cache.interceptor'

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        loggingInterceptor,  // 1er intercepté (avant)
        authInterceptor,     // 2ème intercepté
        cacheInterceptor,    // 3ème intercepté
        // Ordre : avant la requête → 1→2→3→serveur→3→2→1 ← après la réponse
      ])
    ),
  ],
}
```

## Gestion avancée des erreurs

```typescript
// src/app/services/error-handler.service.ts
import { Injectable, inject, ErrorHandler } from '@angular/core'
import { HttpErrorResponse } from '@angular/common/http'
import { NotificationService } from './notification.service'
import { Router } from '@angular/router'

@Injectable({ providedIn: 'root' })
export class ApiErrorHandlerService {
  private notifs = inject(NotificationService)
  private router = inject(Router)

  handle(err: HttpErrorResponse): string {
    let message: string

    if (!navigator.onLine) {
      message = 'Pas de connexion Internet. Vérifiez votre réseau.'
    } else if (err.status === 0) {
      message = 'Impossible de contacter le serveur.'
    } else if (err.status === 400) {
      // Erreur de validation — message du serveur
      message = err.error?.message || 'Données invalides.'
    } else if (err.status === 401) {
      message = 'Session expirée. Veuillez vous reconnecter.'
    } else if (err.status === 403) {
      message = 'Accès refusé. Permissions insuffisantes.'
    } else if (err.status === 404) {
      message = 'Ressource introuvable.'
    } else if (err.status === 409) {
      message = err.error?.message || 'Conflit : la ressource existe déjà.'
    } else if (err.status >= 500) {
      message = 'Erreur serveur. Réessayez dans quelques instants.'
    } else {
      message = err.error?.message || `Erreur ${err.status}.`
    }

    this.notifs.erreur(message)
    return message
  }
}
```

```typescript
// Utilisation dans un service avec gestion d'erreur centralisée
import { catchError, throwError } from 'rxjs'

@Injectable({ providedIn: 'root' })
export class ProduitsService {
  private http = inject(HttpClient)
  private errorHandler = inject(ApiErrorHandlerService)
  private url = `${environment.apiUrl}/products`

  getAll(): Observable<Produit[]> {
    return this.http.get<Produit[]>(this.url).pipe(
      catchError((err: HttpErrorResponse) => {
        this.errorHandler.handle(err)
        return throwError(() => err)
      })
    )
  }
}
```

## Upload de fichiers

```typescript
// Upload avec progress tracking
uploadFichier(fichier: File): Observable<{ progress: number; url?: string }> {
  const formData = new FormData()
  formData.append('file', fichier, fichier.name)

  return this.http
    .post<{ url: string }>('/api/upload', formData, {
      reportProgress: true,          // Activer les événements de progression
      observe: 'events',             // Observer tous les événements (pas juste la réponse)
    })
    .pipe(
      map((event) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progress = Math.round(
              (100 * (event.loaded ?? 0)) / (event.total ?? 1)
            )
            return { progress }
          case HttpEventType.Response:
            return { progress: 100, url: event.body!.url }
          default:
            return { progress: 0 }
        }
      })
    )
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Onglet Network de Chrome DevTools avec les requêtes HTTP en cours, montrer les headers Authorization
> **Expliquer :** Ouvrir DevTools → Network → XHR/Fetch. Faire une requête API et montrer : la requête (URL, méthode, corps), la réponse (status, body), et les headers (dont le Authorization: Bearer xxx ajouté par l'intercepteur). Montrer aussi une requête échouante (404 ou 401) et observer le comportement de l'intercepteur.
---

## Utiliser le `async` pipe — meilleure pratique

```typescript
// RECOMMANDÉ : ne pas subscribe() dans le composant
// Laisser Angular gérer les subscriptions avec le async pipe

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, AsyncPipe],
  template: `
    <!-- async pipe gère subscribe/unsubscribe automatiquement -->
    @if (users$ | async; as users) {
      @for (user of users; track user.id) {
        <p>{{ user.nom }}</p>
      }
    }

    <!-- Avec ngIf et as pour avoir la valeur -->
    <ng-container *ngIf="users$ | async as users">
      <p>{{ users.length }} utilisateurs</p>
    </ng-container>
  `,
})
export class UsersComponent implements OnInit {
  private usersService = inject(UsersService)

  // Observable — pas de subscribe() ici
  users$!: Observable<User[]>

  ngOnInit(): void {
    this.users$ = this.usersService.getAll().pipe(
      map((response) => response.data)
    )
  }
}
```

## Résumé

| Concept | Description | Code |
|---|---|---|
| `HttpClient` | Client HTTP Angular | `inject(HttpClient)` |
| `.get<T>()` | Requête GET | `this.http.get<User[]>('/api/users')` |
| `.post<T>()` | Requête POST | `this.http.post<User>('/api/users', body)` |
| `subscribe()` | Déclencher la requête | `.subscribe({ next, error, complete })` |
| `async pipe` | Subscribe auto dans template | `users$ \| async` |
| Intercepteur | Middleware HTTP | `HttpInterceptorFn` |
| `HttpParams` | Query parameters | `new HttpParams().set('page', '1')` |

**Prochaine étape :** Routing Angular — navigation et guards →
