# Exercice 2 — Application CRUD complète avec API REST

## Objectif

Construire une application Angular complète de gestion de ressources (CRUD) avec : HttpClient, Reactive Forms, Router, Guards, et Signals. Utilise [JSONPlaceholder](https://jsonplaceholder.typicode.com/) comme API de test.

**Durée estimée :** 4h à 5h

## Fonctionnalités

- [ ] Liste des utilisateurs avec pagination et recherche
- [ ] Page détail d'un utilisateur
- [ ] Formulaire de création d'utilisateur (avec validation)
- [ ] Formulaire de modification (pre-rempli)
- [ ] Suppression avec confirmation
- [ ] Guard de confirmation pour quitter un formulaire modifié
- [ ] Intercepteur d'authentification (simulé)
- [ ] Gestion des états : loading, erreur, vide
- [ ] Navigation avec Angular Router

## Structure du projet

```bash
ng new crud-angular --style=scss --standalone
cd crud-angular
ng g s core/services/api
ng g s features/users/users
ng g s core/services/notification
ng g c features/users/user-list
ng g c features/users/user-detail
ng g c features/users/user-form
ng g c shared/components/spinner
ng g c shared/components/empty-state
ng g c shared/components/pagination
ng g guard guards/unsaved-changes
ng g interceptor interceptors/logging
ng g interface models/user
ng g pipe pipes/highlight
```

## Étape 1 — Modèles et configuration

```typescript
// src/app/models/user.ts
export interface User {
  id: number
  name: string
  username: string
  email: string
  phone: string
  website: string
  address: {
    city: string
    street: string
    zipcode: string
  }
  company: {
    name: string
    catchPhrase: string
  }
}

export interface Post {
  id: number
  userId: number
  title: string
  body: string
}

export type CreateUserDto = Omit<User, 'id'>
export type UpdateUserDto = Partial<CreateUserDto>
```

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'https://jsonplaceholder.typicode.com',
}
```

## Étape 2 — Service API générique

```typescript
// src/app/core/services/api.service.ts
import { Injectable, inject } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable } from 'rxjs'
import { environment } from '@env/environment'

@Injectable({ providedIn: 'root' })
export class ApiService {
  protected http = inject(HttpClient)
  protected readonly baseUrl = environment.apiUrl

  protected get<T>(endpoint: string, params?: Record<string, string>): Observable<T> {
    let httpParams = new HttpParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v != null) httpParams = httpParams.set(k, v)
      })
    }
    return this.http.get<T>(`${this.baseUrl}${endpoint}`, { params: httpParams })
  }

  protected post<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, body)
  }

  protected put<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}${endpoint}`, body)
  }

  protected patch<T>(endpoint: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.baseUrl}${endpoint}`, body)
  }

  protected delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}${endpoint}`)
  }
}
```

## Étape 3 — Service UsersService

```typescript
// src/app/features/users/users.service.ts
import { Injectable, signal, computed } from '@angular/core'
import { Observable, tap, catchError, throwError } from 'rxjs'
import { ApiService } from '@/core/services/api.service'
import { User, CreateUserDto, UpdateUserDto } from '@/models/user'
import { NotificationService } from '@/core/services/notification.service'

@Injectable({ providedIn: 'root' })
export class UsersService extends ApiService {
  private notifs = inject(NotificationService)

  // État interne
  private _users = signal<User[]>([])
  private _loading = signal(false)
  private _error = signal<string | null>(null)
  private _totalUsers = signal(0)

  // API publique
  readonly users = this._users.asReadonly()
  readonly loading = this._loading.asReadonly()
  readonly error = this._error.asReadonly()

  readonly usersFiltres = computed(() => {
    // Filtrage côté client pour la démo (JSONPlaceholder ne supporte pas la pagination server-side)
    return this._users()
  })

  chargerTous(): Observable<User[]> {
    this._loading.set(true)
    this._error.set(null)

    return this.get<User[]>('/users').pipe(
      tap((users) => {
        this._users.set(users)
        this._totalUsers.set(users.length)
        this._loading.set(false)
      }),
      catchError((err) => {
        this._error.set('Impossible de charger les utilisateurs')
        this._loading.set(false)
        return throwError(() => err)
      })
    )
  }

  chargerParId(id: number): Observable<User> {
    return this.get<User>(`/users/${id}`)
  }

  chargerPostsUser(userId: number): Observable<Post[]> {
    return this.get<Post[]>(`/users/${userId}/posts`)
  }

  creer(dto: CreateUserDto): Observable<User> {
    return this.post<User>('/users', dto).pipe(
      tap((user) => {
        this._users.update((users) => [user, ...users])
        this.notifs.succes(`Utilisateur "${user.name}" créé`)
      })
    )
  }

  modifier(id: number, dto: UpdateUserDto): Observable<User> {
    return this.put<User>(`/users/${id}`, dto).pipe(
      tap((user) => {
        this._users.update((users) =>
          users.map((u) => (u.id === id ? { ...u, ...user } : u))
        )
        this.notifs.succes(`Utilisateur mis à jour`)
      })
    )
  }

  supprimer(id: number): Observable<void> {
    return this.delete<void>(`/users/${id}`).pipe(
      tap(() => {
        this._users.update((users) => users.filter((u) => u.id !== id))
        this.notifs.succes('Utilisateur supprimé')
      })
    )
  }
}
```

## Étape 4 — Routes

```typescript
// src/app/app.routes.ts
import { Routes } from '@angular/router'
import { unsavedChangesGuard } from './guards/unsaved-changes.guard'

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'users',
    pathMatch: 'full',
  },
  {
    path: 'users',
    loadComponent: () =>
      import('./features/users/user-list/user-list.component').then(
        (m) => m.UserListComponent
      ),
    title: 'Utilisateurs',
  },
  {
    path: 'users/new',
    loadComponent: () =>
      import('./features/users/user-form/user-form.component').then(
        (m) => m.UserFormComponent
      ),
    title: 'Nouvel utilisateur',
    canDeactivate: [unsavedChangesGuard],
  },
  {
    path: 'users/:id',
    loadComponent: () =>
      import('./features/users/user-detail/user-detail.component').then(
        (m) => m.UserDetailComponent
      ),
    title: 'Détail utilisateur',
  },
  {
    path: 'users/:id/edit',
    loadComponent: () =>
      import('./features/users/user-form/user-form.component').then(
        (m) => m.UserFormComponent
      ),
    title: 'Modifier utilisateur',
    canDeactivate: [unsavedChangesGuard],
  },
  {
    path: '**',
    loadComponent: () =>
      import('./pages/not-found/not-found.component').then(
        (m) => m.NotFoundComponent
      ),
  },
]
```

## Étape 5 — Formulaire CRUD

```typescript
// src/app/features/users/user-form/user-form.component.ts
import { Component, OnInit, inject } from '@angular/core'
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms'
import { ActivatedRoute, Router, RouterLink } from '@angular/router'
import { CommonModule } from '@angular/common'
import { switchMap, of } from 'rxjs'
import { UsersService } from '../users.service'

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, RouterLink],
  template: `
    <div class="form-container">
      <div class="form-header">
        <a routerLink="/users">← Retour</a>
        <h2>{{ isEditing ? 'Modifier l\'utilisateur' : 'Nouvel utilisateur' }}</h2>
      </div>

      <form [formGroup]="form" (ngSubmit)="soumettre()">
        <div class="form-section">
          <h3>Informations personnelles</h3>

          <div class="field">
            <label>Nom complet *</label>
            <input formControlName="name" placeholder="Ex: Alice Dupont" />
            @if (err('name', 'required')) {
              <span class="error">Requis</span>
            }
          </div>

          <div class="row">
            <div class="field">
              <label>Nom d'utilisateur *</label>
              <input formControlName="username" placeholder="alicedupont" />
            </div>
            <div class="field">
              <label>Email *</label>
              <input formControlName="email" type="email" />
              @if (err('email', 'email')) {
                <span class="error">Email invalide</span>
              }
            </div>
          </div>

          <div class="row">
            <div class="field">
              <label>Téléphone</label>
              <input formControlName="phone" />
            </div>
            <div class="field">
              <label>Site web</label>
              <input formControlName="website" placeholder="exemple.com" />
            </div>
          </div>
        </div>

        <div class="form-section" formGroupName="address">
          <h3>Adresse</h3>
          <div class="row">
            <div class="field">
              <label>Rue</label>
              <input formControlName="street" />
            </div>
            <div class="field">
              <label>Ville</label>
              <input formControlName="city" />
            </div>
            <div class="field">
              <label>Code postal</label>
              <input formControlName="zipcode" />
            </div>
          </div>
        </div>

        <div class="form-actions">
          <a routerLink="/users" class="btn-cancel">Annuler</a>
          <button type="submit" [disabled]="form.invalid || loading">
            {{ loading ? 'Enregistrement...' : (isEditing ? 'Mettre à jour' : 'Créer') }}
          </button>
        </div>
      </form>
    </div>
  `,
})
export class UserFormComponent implements OnInit {
  private fb = inject(FormBuilder)
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private usersService = inject(UsersService)

  isEditing = false
  userId: number | null = null
  loading = false
  formModified = false  // Pour le guard

  form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    phone: [''],
    website: [''],
    address: this.fb.group({
      street: [''],
      city: [''],
      zipcode: [''],
    }),
  })

  ngOnInit(): void {
    const id = this.route.snapshot.params['id']
    if (id) {
      this.isEditing = true
      this.userId = Number(id)
      this.chargerUser(this.userId)
    }

    // Détecter les modifications
    this.form.valueChanges.subscribe(() => {
      this.formModified = true
    })
  }

  chargerUser(id: number): void {
    this.loading = true
    this.usersService.chargerParId(id).subscribe({
      next: (user) => {
        this.form.patchValue(user)
        this.loading = false
        this.formModified = false // Reset après chargement
      },
      error: () => {
        this.loading = false
        this.router.navigate(['/users'])
      },
    })
  }

  err(champ: string, type: string): boolean {
    const ctrl = this.form.get(champ)!
    return !!(ctrl.errors?.[type] && (ctrl.dirty || ctrl.touched))
  }

  soumettre(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched()
      return
    }

    this.loading = true
    const valeurs = this.form.value

    const requete$ = this.isEditing && this.userId
      ? this.usersService.modifier(this.userId, valeurs)
      : this.usersService.creer(valeurs as any)

    requete$.subscribe({
      next: (user) => {
        this.formModified = false
        this.router.navigate(['/users', user.id])
      },
      error: () => { this.loading = false },
    })
  }

  // Méthode pour le guard unsavedChanges
  hasUnsavedChanges(): boolean {
    return this.formModified
  }
}
```

## Critères d'évaluation

| Fonctionnalité | Points |
|---|---|
| Liste utilisateurs avec loading/error/empty | 2 |
| Page détail avec posts de l'utilisateur | 2 |
| Formulaire création avec validation complète | 3 |
| Formulaire modification (pre-rempli) | 2 |
| Suppression avec confirmation | 1 |
| Navigation Router (5 routes) | 2 |
| Guard unsavedChanges | 1 |
| HttpClient + service API générique | 3 |
| Signals pour la gestion d'état | 2 |
| TypeScript strict | 2 |
| **Total** | **20** |

## Défi bonus

1. Ajouter une fonctionnalité de recherche/filtrage en temps réel avec RxJS `debounceTime`
2. Créer un pipe `highlight` pour surligner le terme de recherche dans les résultats
3. Implémenter la pagination côté client
4. Ajouter des animations Angular ([@trigger] et AnimationBuilder)
