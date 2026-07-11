# Exercice 1 — Application Todo Angular

## Objectif

Construire une application Todo complète avec Angular 17+, TypeScript strict, Reactive Forms, Signals et services Angular. Parallèle à l'exercice Vue pour comparer les deux approches.

**Durée estimée :** 2h30 à 3h30

## Fonctionnalités à implémenter

- [ ] Ajouter une tâche avec titre, description et priorité (Reactive Form)
- [ ] Marquer une tâche comme terminée (toggle)
- [ ] Supprimer une tâche avec confirmation
- [ ] Modifier une tâche (mode édition inline)
- [ ] Filtrer par statut : Toutes / En cours / Terminées
- [ ] Trier par priorité / date
- [ ] Compteur de tâches restantes
- [ ] Persistance dans localStorage
- [ ] Animation à l'ajout/suppression (`@defer` ou CSS)

## Étape 1 — Créer le projet

```bash
ng new todo-angular --style=scss --standalone --ssr=false
cd todo-angular
ng serve
```

## Étape 2 — Modèles et types

```typescript
// src/app/models/todo.model.ts
export type Priorite = 'haute' | 'moyenne' | 'basse'
export type Statut = 'toutes' | 'en_cours' | 'terminees'

export interface Todo {
  id: number
  titre: string
  description: string
  termine: boolean
  priorite: Priorite
  createdAt: Date
}

export interface NouveauTodoDto {
  titre: string
  description: string
  priorite: Priorite
}

export const PRIORITES: Array<{ value: Priorite; label: string; couleur: string }> = [
  { value: 'haute', label: 'Haute', couleur: '#e53e3e' },
  { value: 'moyenne', label: 'Moyenne', couleur: '#f6ad55' },
  { value: 'basse', label: 'Basse', couleur: '#68d391' },
]
```

## Étape 3 — Service TodoService

```typescript
// src/app/services/todo.service.ts
import { Injectable, signal, computed, effect } from '@angular/core'
import { Todo, NouveauTodoDto, Priorite, Statut } from '../models/todo.model'

@Injectable({ providedIn: 'root' })
export class TodoService {
  private readonly STORAGE_KEY = 'angular-todos'

  // Charger depuis localStorage au démarrage
  private _todos = signal<Todo[]>(this.chargerDepuisStorage())
  private _statut = signal<Statut>('toutes')
  private _prioriteFiltree = signal<Priorite | 'toutes'>('toutes')

  // Auto-sauvegarde dans localStorage à chaque changement
  constructor() {
    effect(() => {
      const todos = this._todos()
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(todos))
    })
  }

  // Getters (read-only)
  readonly todos = this._todos.asReadonly()
  readonly statut = this._statut.asReadonly()
  readonly prioriteFiltree = this._prioriteFiltree.asReadonly()

  // Computed signals
  readonly todosFiltres = computed(() => {
    let result = this._todos()

    // Filtre statut
    if (this._statut() === 'en_cours') {
      result = result.filter((t) => !t.termine)
    } else if (this._statut() === 'terminees') {
      result = result.filter((t) => t.termine)
    }

    // Filtre priorité
    if (this._prioriteFiltree() !== 'toutes') {
      result = result.filter((t) => t.priorite === this._prioriteFiltree())
    }

    // Tri : haute > moyenne > basse, puis non terminées en premier
    const prioriteOrdre: Record<Priorite, number> = { haute: 0, moyenne: 1, basse: 2 }
    return [...result].sort((a, b) => {
      if (a.termine !== b.termine) return a.termine ? 1 : -1
      return prioriteOrdre[a.priorite] - prioriteOrdre[b.priorite]
    })
  })

  readonly nombreRestants = computed(
    () => this._todos().filter((t) => !t.termine).length
  )

  readonly nombreTerminees = computed(
    () => this._todos().filter((t) => t.termine).length
  )

  readonly toutesTerminees = computed(
    () => this._todos().length > 0 && this._todos().every((t) => t.termine)
  )

  // Actions
  ajouter(dto: NouveauTodoDto): void {
    const nouveau: Todo = {
      id: Date.now(),
      titre: dto.titre.trim(),
      description: dto.description.trim(),
      termine: false,
      priorite: dto.priorite,
      createdAt: new Date(),
    }
    this._todos.update((todos) => [nouveau, ...todos])
  }

  toggleTermine(id: number): void {
    this._todos.update((todos) =>
      todos.map((t) => (t.id === id ? { ...t, termine: !t.termine } : t))
    )
  }

  modifier(id: number, modifications: Partial<Pick<Todo, 'titre' | 'description' | 'priorite'>>): void {
    this._todos.update((todos) =>
      todos.map((t) => (t.id === id ? { ...t, ...modifications } : t))
    )
  }

  supprimer(id: number): void {
    this._todos.update((todos) => todos.filter((t) => t.id !== id))
  }

  supprimerTerminees(): void {
    this._todos.update((todos) => todos.filter((t) => !t.termine))
  }

  toggleToutes(): void {
    const toutes = this.toutesTerminees()
    this._todos.update((todos) => todos.map((t) => ({ ...t, termine: !toutes })))
  }

  setStatut(statut: Statut): void {
    this._statut.set(statut)
  }

  setPrioriteFiltree(priorite: Priorite | 'toutes'): void {
    this._prioriteFiltree.set(priorite)
  }

  private chargerDepuisStorage(): Todo[] {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY)
      if (!data) return []
      const todos = JSON.parse(data) as Todo[]
      // Reconvertir les dates string en Date objects
      return todos.map((t) => ({ ...t, createdAt: new Date(t.createdAt) }))
    } catch {
      return []
    }
  }
}
```

## Étape 4 — Composant FormulaireAjout

```typescript
// src/app/components/formulaire-ajout/formulaire-ajout.component.ts
import { Component, inject, output } from '@angular/core'
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms'
import { CommonModule } from '@angular/common'
import { TodoService } from '../../services/todo.service'
import { PRIORITES, NouveauTodoDto } from '../../models/todo.model'

@Component({
  selector: 'app-formulaire-ajout',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()" class="form-ajout">
      <div class="field">
        <input
          formControlName="titre"
          placeholder="Titre de la tâche *"
          class="input-titre"
          [class.error]="champInvalide('titre')"
        />
        @if (champInvalide('titre')) {
          <span class="error-msg">Le titre est requis (min. 3 caractères)</span>
        }
      </div>

      <div class="field">
        <textarea
          formControlName="description"
          placeholder="Description (optionnel)"
          rows="2"
        ></textarea>
      </div>

      <div class="row">
        <select formControlName="priorite" class="select-priorite">
          @for (p of priorites; track p.value) {
            <option [value]="p.value">{{ p.label }}</option>
          }
        </select>

        <button type="submit" [disabled]="form.invalid" class="btn-ajouter">
          Ajouter
        </button>
      </div>
    </form>
  `,
})
export class FormulaireAjoutComponent {
  private fb = inject(FormBuilder)
  private todoService = inject(TodoService)

  priorites = PRIORITES

  form = this.fb.group({
    titre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
    description: ['', Validators.maxLength(500)],
    priorite: ['moyenne' as const],
  })

  champInvalide(champ: string): boolean {
    const ctrl = this.form.get(champ)!
    return ctrl.invalid && (ctrl.dirty || ctrl.touched)
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched()
      return
    }

    this.todoService.ajouter(this.form.value as NouveauTodoDto)
    this.form.reset({ priorite: 'moyenne' })
  }
}
```

## Étape 5 — Composant TodoItem

```typescript
// src/app/components/todo-item/todo-item.component.ts
import { Component, inject, input, signal } from '@angular/core'
import { CommonModule } from '@angular/common'
import { ReactiveFormsModule, FormControl, Validators } from '@angular/forms'
import { Todo } from '../../models/todo.model'
import { TodoService } from '../../services/todo.service'

@Component({
  selector: 'app-todo-item',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="todo-item" [class.termine]="todo().termine">
      <!-- Checkbox -->
      <input
        type="checkbox"
        [checked]="todo().termine"
        (change)="todoService.toggleTermine(todo().id)"
      />

      <!-- Affichage ou édition -->
      @if (!enEdition()) {
        <div class="content" (dblclick)="commencerEdition()">
          <span class="titre" [class]="'priorite-' + todo().priorite">
            {{ todo().titre }}
          </span>
          @if (todo().description) {
            <small class="description">{{ todo().description }}</small>
          }
        </div>
      } @else {
        <div class="edition">
          <input
            [formControl]="titreEdition"
            (blur)="sauvegarder()"
            (keyup.enter)="sauvegarder()"
            (keyup.escape)="annulerEdition()"
            class="input-edition"
          />
        </div>
      }

      <!-- Badges et actions -->
      <div class="meta">
        <span class="badge" [class]="'badge-' + todo().priorite">
          {{ todo().priorite }}
        </span>
        <span class="date">{{ todo().createdAt | date:'dd/MM' }}</span>
      </div>

      <div class="actions">
        <button (click)="commencerEdition()" title="Modifier" *ngIf="!enEdition()">✎</button>
        <button (click)="confirmerSuppression()" title="Supprimer" class="btn-delete">×</button>
      </div>
    </div>
  `,
})
export class TodoItemComponent {
  // Input Signal (Angular 17.1+)
  todo = input.required<Todo>()

  todoService = inject(TodoService)
  enEdition = signal(false)
  titreEdition = new FormControl('', [Validators.required, Validators.minLength(3)])

  commencerEdition(): void {
    if (this.todo().termine) return
    this.titreEdition.setValue(this.todo().titre)
    this.enEdition.set(true)

    // Focus automatique après le rendu
    setTimeout(() => {
      const input = document.querySelector('.input-edition') as HTMLInputElement
      input?.focus()
      input?.select()
    })
  }

  sauvegarder(): void {
    if (this.titreEdition.valid && this.titreEdition.value!.trim()) {
      this.todoService.modifier(this.todo().id, {
        titre: this.titreEdition.value!.trim(),
      })
    }
    this.enEdition.set(false)
  }

  annulerEdition(): void {
    this.enEdition.set(false)
  }

  confirmerSuppression(): void {
    if (confirm(`Supprimer "${this.todo().titre}" ?`)) {
      this.todoService.supprimer(this.todo().id)
    }
  }
}
```

## Étape 6 — Composant AppComponent

```typescript
// src/app/app.component.ts
import { Component, inject } from '@angular/core'
import { CommonModule } from '@angular/common'
import { TodoService } from './services/todo.service'
import { FormulaireAjoutComponent } from './components/formulaire-ajout/formulaire-ajout.component'
import { TodoItemComponent } from './components/todo-item/todo-item.component'
import { Statut, Priorite } from './models/todo.model'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormulaireAjoutComponent, TodoItemComponent],
  template: `
    <div class="app">
      <header class="app-header">
        <h1>
          ✅ Todo Angular
          @if (todoService.nombreRestants() > 0) {
            <span class="badge-count">{{ todoService.nombreRestants() }}</span>
          }
        </h1>
      </header>

      <main class="app-main">
        <app-formulaire-ajout />

        <!-- Filtres -->
        <div class="filtres">
          <div class="filtres-statut">
            @for (f of filtresStatut; track f.valeur) {
              <button
                (click)="todoService.setStatut(f.valeur)"
                [class.actif]="todoService.statut() === f.valeur"
                class="btn-filtre"
              >
                {{ f.label }}
              </button>
            }
          </div>

          <select
            [value]="todoService.prioriteFiltree()"
            (change)="onPrioriteChange($event)"
          >
            <option value="toutes">Toutes priorités</option>
            <option value="haute">Haute</option>
            <option value="moyenne">Moyenne</option>
            <option value="basse">Basse</option>
          </select>
        </div>

        <!-- Actions globales -->
        @if (todoService.todos().length > 0) {
          <div class="actions-globales">
            <label>
              <input
                type="checkbox"
                [checked]="todoService.toutesTerminees()"
                (change)="todoService.toggleToutes()"
              />
              Tout cocher/décocher
            </label>
            @if (todoService.nombreTerminees() > 0) {
              <button
                (click)="todoService.supprimerTerminees()"
                class="btn-secondary"
              >
                Supprimer les {{ todoService.nombreTerminees() }} terminées
              </button>
            }
          </div>
        }

        <!-- Liste -->
        <div class="todo-list">
          @for (todo of todoService.todosFiltres(); track todo.id) {
            <app-todo-item [todo]="todo" />
          } @empty {
            <div class="empty-state">
              @if (todoService.todos().length === 0) {
                <p>Aucune tâche — ajoutez-en une ci-dessus !</p>
              } @else {
                <p>Aucune tâche correspondant aux filtres.</p>
              }
            </div>
          }
        </div>
      </main>
    </div>
  `,
})
export class AppComponent {
  todoService = inject(TodoService)

  filtresStatut: Array<{ valeur: Statut; label: string }> = [
    { valeur: 'toutes', label: 'Toutes' },
    { valeur: 'en_cours', label: 'En cours' },
    { valeur: 'terminees', label: 'Terminées' },
  ]

  onPrioriteChange(event: Event): void {
    const valeur = (event.target as HTMLSelectElement).value as Priorite | 'toutes'
    this.todoService.setPrioriteFiltree(valeur)
  }
}
```

## Critères d'évaluation

| Fonctionnalité | Points |
|---|---|
| Ajout via Reactive Form avec validation | 3 |
| Toggle terminée + suppression | 2 |
| Édition inline | 2 |
| Filtres statut + priorité | 2 |
| Service avec Signals | 3 |
| Persistance localStorage avec effect() | 2 |
| TypeScript strict (aucun any) | 2 |
| Composants standalone correctement configurés | 2 |
| Design cohérent (SCSS) | 2 |
| **Total** | **20** |

## Comparer avec Vue 3

Après avoir terminé cet exercice, identifiez les différences principales avec la version Vue :

| Aspect | Vue 3 | Angular |
|---|---|---|
| Réactivité | `ref()` / Pinia | Signals / Services |
| Formulaires | `v-model` | Reactive Forms |
| Template | `v-if`, `v-for` | `@if`, `@for` |
| DI | `inject()` (Composables) | `inject()` (Services) |
| TypeScript | Optionnel | Obligatoire |
| Boilerplate | Moins | Plus |
