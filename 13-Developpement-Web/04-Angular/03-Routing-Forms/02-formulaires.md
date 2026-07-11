# Formulaires Réactifs Angular (Reactive Forms)

## Template-driven vs Reactive Forms

Angular propose deux approches pour les formulaires :

| | Template-driven | Reactive Forms |
|---|---|---|
| Définition | Dans le template (HTML) | Dans le TypeScript |
| Module | `FormsModule` | `ReactiveFormsModule` |
| Testabilité | Difficile | Facile (pas de DOM nécessaire) |
| Complexité | Simple | Plus verbeux mais puissant |
| Validation | Directives HTML | Validators TypeScript |
| Typage TypeScript | Limité | Excellent (TypedForms Angular 14+) |
| **Utilisation recommandée** | Formulaires simples | Formulaires complexes, production |

**Dans ce cours, nous utilisons les Reactive Forms** — c'est la méthode recommandée pour les projets professionnels.

## Setup — `ReactiveFormsModule`

```typescript
// Dans chaque composant qui utilise Reactive Forms
import { ReactiveFormsModule } from '@angular/forms'

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  // ...
})
```

## `FormControl` — Contrôle individuel

```typescript
import { Component, OnInit, inject } from '@angular/core'
import { FormControl, Validators, ReactiveFormsModule } from '@angular/forms'

@Component({
  selector: 'app-simple-input',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <div>
      <input [formControl]="email" type="email" placeholder="Email" />

      <!-- Afficher les erreurs -->
      @if (email.invalid && (email.dirty || email.touched)) {
        <div class="erreurs">
          @if (email.errors?.['required']) {
            <span>L'email est requis.</span>
          }
          @if (email.errors?.['email']) {
            <span>Format d'email invalide.</span>
          }
          @if (email.errors?.['minlength']) {
            <span>Minimum {{ email.errors?.['minlength'].requiredLength }} caractères.</span>
          }
        </div>
      }

      <p>Valeur : {{ email.value }}</p>
      <p>Statut : {{ email.status }}</p>  <!-- VALID, INVALID, PENDING -->
      <p>Modifié : {{ email.dirty }}</p>
      <p>Touché : {{ email.touched }}</p>
    </div>
  `,
})
export class SimpleInputComponent implements OnInit {
  // FormControl avec valeur initiale et validators
  email = new FormControl('', {
    validators: [
      Validators.required,
      Validators.email,
      Validators.minLength(5),
    ],
  })

  ngOnInit(): void {
    // Observer les changements
    this.email.valueChanges.subscribe((valeur) => {
      console.log('Email modifié :', valeur)
    })

    // Modifier programmatiquement
    this.email.setValue('alice@example.com')   // Remplace la valeur
    this.email.patchValue('test@')             // Idem pour FormControl
    this.email.reset()                          // Remet à la valeur initiale
    this.email.disable()                        // Désactiver
    this.email.enable()                         // Réactiver
  }
}
```

## `FormGroup` — Groupe de contrôles

```typescript
import { Component, inject } from '@angular/core'
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms'
import { CommonModule } from '@angular/common'

@Component({
  selector: 'app-login-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="form">
      <div class="form-group">
        <label for="email">Email *</label>
        <input
          id="email"
          type="email"
          formControlName="email"
          [class.invalid]="isInvalid('email')"
          placeholder="votre@email.com"
        />
        @if (isInvalid('email')) {
          <div class="error-messages">
            @if (getControl('email').errors?.['required']) {
              <p>L'email est requis.</p>
            }
            @if (getControl('email').errors?.['email']) {
              <p>Format d'email invalide.</p>
            }
          </div>
        }
      </div>

      <div class="form-group">
        <label for="password">Mot de passe *</label>
        <input
          id="password"
          type="password"
          formControlName="password"
          [class.invalid]="isInvalid('password')"
        />
        @if (isInvalid('password')) {
          <div class="error-messages">
            @if (getControl('password').errors?.['required']) {
              <p>Le mot de passe est requis.</p>
            }
            @if (getControl('password').errors?.['minlength']) {
              <p>Minimum {{ getControl('password').errors?.['minlength'].requiredLength }} caractères.</p>
            }
          </div>
        }
      </div>

      <!-- Bouton désactivé si le formulaire est invalide ou en cours de soumission -->
      <button type="submit" [disabled]="loginForm.invalid || isLoading">
        {{ isLoading ? 'Connexion...' : 'Se connecter' }}
      </button>
    </form>
  `,
})
export class LoginFormComponent {
  // FormBuilder — façon plus concise de créer des formulaires
  private fb = inject(FormBuilder)

  isLoading = false

  // Créer le formulaire avec FormBuilder
  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    rememberMe: [false],
  })

  // Helpers
  isInvalid(champ: string): boolean {
    const control = this.loginForm.get(champ)!
    return control.invalid && (control.dirty || control.touched)
  }

  getControl(champ: string) {
    return this.loginForm.get(champ)!
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      this.loginForm.markAllAsTouched()
      return
    }

    this.isLoading = true
    const { email, password } = this.loginForm.value
    console.log('Connexion avec :', email, password)

    // Appel API...
  }
}
```

## `FormBuilder` — Syntaxe concise recommandée

```typescript
import { inject } from '@angular/core'
import { FormBuilder, Validators } from '@angular/forms'

// FormBuilder est un service injectable qui simplif la création de formulaires
const fb = inject(FormBuilder)

// Équivalences :
const f1 = fb.control('valeur', Validators.required)
// ≡ new FormControl('valeur', Validators.required)

const f2 = fb.group({
  nom: ['', Validators.required],
  email: ['', [Validators.required, Validators.email]],
})
// ≡ new FormGroup({ nom: new FormControl('', ...), ... })

const f3 = fb.array([
  fb.group({ item: '' }),
  fb.group({ item: '' }),
])
// ≡ new FormArray([...])

// Nouvelle syntaxe typée (Angular 14+) — Recommandée
const formTypé = fb.group({
  prenom: fb.nonNullable.control('', Validators.required),
  age: fb.nonNullable.control(0, [Validators.min(0), Validators.max(150)]),
})
// formTypé.value est maintenant automatiquement typé { prenom: string, age: number }
```

## Validators — Validation des données

### Validators built-in

```typescript
import { Validators } from '@angular/forms'

const controles = this.fb.group({
  nom: ['', [
    Validators.required,              // Non vide
    Validators.minLength(2),           // Min 2 caractères
    Validators.maxLength(50),          // Max 50 caractères
  ]],
  email: ['', [
    Validators.required,
    Validators.email,                  // Format email valide
  ]],
  age: [null, [
    Validators.required,
    Validators.min(0),                 // Valeur minimum
    Validators.max(150),               // Valeur maximum
  ]],
  siteWeb: ['', [
    Validators.pattern('https?://.+'), // Regex
  ]],
  codePostal: ['', [
    Validators.required,
    Validators.pattern(/^\d{5}$/),     // 5 chiffres exactement
  ]],
})
```

### Validators personnalisés

```typescript
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms'

// Validator simple — vérifie que deux champs sont identiques
export function motsDePasseIdentiques(
  champMdp: string,
  champConfirmation: string
): ValidatorFn {
  return (formGroup: AbstractControl): ValidationErrors | null => {
    const mdp = formGroup.get(champMdp)
    const confirm = formGroup.get(champConfirmation)

    if (!mdp || !confirm) return null

    if (mdp.value !== confirm.value) {
      // Définir une erreur sur le champ de confirmation
      confirm.setErrors({ ...confirm.errors, motsDePasse: true })
      return { motsDePasse: true }
    } else {
      // Supprimer l'erreur si les mots de passe correspondent
      const { motsDePasse, ...autresErreurs } = confirm.errors || {}
      confirm.setErrors(Object.keys(autresErreurs).length ? autresErreurs : null)
      return null
    }
  }
}

// Validator asynchrone — vérifier si l'email existe déjà en BDD
import { AsyncValidatorFn } from '@angular/forms'
import { Observable, map, debounceTime, distinctUntilChanged } from 'rxjs'

export function emailUniqueValidator(
  userService: UserService
): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    return userService.checkEmailExists(control.value).pipe(
      debounceTime(400),           // Attendre 400ms après la dernière frappe
      distinctUntilChanged(),       // Éviter les appels redondants
      map((exists) => (exists ? { emailExiste: true } : null))
    )
  }
}
```

```typescript
// Utilisation des validators personnalisés
@Component({ ... })
export class RegisterFormComponent {
  private fb = inject(FormBuilder)
  private userService = inject(UserService)

  form = this.fb.group(
    {
      email: [
        '',
        [Validators.required, Validators.email],
        [emailUniqueValidator(this.userService)],  // 3ème param = async validators
      ],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
    },
    {
      validators: [motsDePasseIdentiques('password', 'confirmPassword')],
    }
  )
}
```

## `FormArray` — Listes dynamiques

```typescript
import { Component, inject } from '@angular/core'
import { FormBuilder, FormArray, Validators, ReactiveFormsModule } from '@angular/forms'
import { CommonModule } from '@angular/common'

@Component({
  selector: 'app-dynamic-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <h3>Compétences</h3>

      <!-- formArrayName connecte le tableau au template -->
      <div formArrayName="competences">
        @for (ctrl of competencesArray.controls; track $index) {
          <div class="competence-row">
            <!-- Chaque élément utilise son index -->
            <input [formControlName]="$index" placeholder="Ex: Python" />
            <button type="button" (click)="supprimerCompetence($index)">-</button>
          </div>
        }
      </div>

      <button type="button" (click)="ajouterCompetence()">+ Ajouter une compétence</button>

      <!-- FormGroup imbriqué dans FormArray -->
      <h3>Expériences professionnelles</h3>
      <div formArrayName="experiences">
        @for (exp of experiencesArray.controls; track $index) {
          <div [formGroupName]="$index" class="experience-block">
            <input formControlName="poste" placeholder="Intitulé du poste" />
            <input formControlName="entreprise" placeholder="Entreprise" />
            <input formControlName="annees" type="number" placeholder="Années" />
            <button type="button" (click)="supprimerExperience($index)">Supprimer</button>
          </div>
        }
      </div>
      <button type="button" (click)="ajouterExperience()">+ Ajouter une expérience</button>

      <button type="submit" [disabled]="form.invalid">Enregistrer</button>
    </form>
  `,
})
export class DynamicFormComponent {
  private fb = inject(FormBuilder)

  form = this.fb.group({
    nom: ['', Validators.required],
    competences: this.fb.array([
      this.fb.control('TypeScript', Validators.required),
    ]),
    experiences: this.fb.array([]),
  })

  // Accéder au FormArray
  get competencesArray(): FormArray {
    return this.form.get('competences') as FormArray
  }

  get experiencesArray(): FormArray {
    return this.form.get('experiences') as FormArray
  }

  ajouterCompetence(): void {
    this.competencesArray.push(this.fb.control('', Validators.required))
  }

  supprimerCompetence(index: number): void {
    this.competencesArray.removeAt(index)
  }

  ajouterExperience(): void {
    this.experiencesArray.push(
      this.fb.group({
        poste: ['', Validators.required],
        entreprise: ['', Validators.required],
        annees: [0, [Validators.required, Validators.min(0)]],
      })
    )
  }

  supprimerExperience(index: number): void {
    this.experiencesArray.removeAt(index)
  }

  onSubmit(): void {
    if (this.form.valid) {
      console.log('Formulaire soumis :', this.form.value)
    } else {
      this.form.markAllAsTouched()
    }
  }
}
```

## Formulaire d'inscription complet — exemple réaliste

```typescript
@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="soumettre()" class="register-form">
      <h2>Créer un compte</h2>

      <!-- Informations personnelles -->
      <fieldset formGroupName="personnel">
        <legend>Informations personnelles</legend>

        <div class="row">
          <div class="field">
            <label>Prénom *</label>
            <input formControlName="prenom" />
            @if (fieldError('personnel.prenom', 'required')) {
              <span class="error">Requis</span>
            }
          </div>
          <div class="field">
            <label>Nom *</label>
            <input formControlName="nom" />
          </div>
        </div>

        <div class="field">
          <label>Date de naissance</label>
          <input formControlName="dateNaissance" type="date" />
        </div>
      </fieldset>

      <!-- Informations de connexion -->
      <fieldset formGroupName="connexion">
        <legend>Connexion</legend>

        <div class="field">
          <label>Email *</label>
          <input formControlName="email" type="email" />
          @if (fieldError('connexion.email', 'emailExiste')) {
            <span class="error">Cet email est déjà utilisé.</span>
          }
          <!-- Indicateur de chargement pour la validation async -->
          @if (form.get('connexion.email')?.pending) {
            <span class="pending">Vérification...</span>
          }
        </div>

        <div class="field">
          <label>Mot de passe *</label>
          <input formControlName="password" type="password" />
          <div class="force-indicateur">
            Force : {{ forceMotDePasse }}
          </div>
        </div>

        <div class="field">
          <label>Confirmer le mot de passe *</label>
          <input formControlName="confirmPassword" type="password" />
          @if (fieldError('connexion.confirmPassword', 'motsDePasse')) {
            <span class="error">Les mots de passe ne correspondent pas.</span>
          }
        </div>
      </fieldset>

      <!-- CGU -->
      <div class="field">
        <label>
          <input formControlName="accepteCgu" type="checkbox" />
          J'accepte les conditions générales d'utilisation *
        </label>
        @if (fieldError('accepteCgu', 'requiredTrue')) {
          <span class="error">Vous devez accepter les CGU.</span>
        }
      </div>

      <button type="submit" [disabled]="form.invalid || isLoading">
        {{ isLoading ? 'Inscription en cours...' : 'Créer mon compte' }}
      </button>

      <pre *ngIf="showDebug">{{ form.value | json }}</pre>
    </form>
  `,
})
export class RegisterComponent {
  private fb = inject(FormBuilder)
  private userService = inject(UsersService)

  isLoading = false
  showDebug = false

  form = this.fb.group({
    personnel: this.fb.group({
      prenom: ['', [Validators.required, Validators.minLength(2)]],
      nom: ['', [Validators.required, Validators.minLength(2)]],
      dateNaissance: [''],
    }),
    connexion: this.fb.group(
      {
        email: [
          '',
          [Validators.required, Validators.email],
          [emailUniqueValidator(this.userService)],
        ],
        password: ['', [
          Validators.required,
          Validators.minLength(8),
          Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/),
        ]],
        confirmPassword: ['', Validators.required],
      },
      { validators: [motsDePasseIdentiques('password', 'confirmPassword')] }
    ),
    accepteCgu: [false, Validators.requiredTrue],
  })

  get forceMotDePasse(): string {
    const pwd = this.form.get('connexion.password')?.value || ''
    if (pwd.length === 0) return '—'
    if (pwd.length < 8) return 'Faible'
    if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!]).+$/.test(pwd)) return 'Très fort'
    if (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/.test(pwd)) return 'Fort'
    return 'Moyen'
  }

  fieldError(chemin: string, erreur: string): boolean {
    const ctrl = this.form.get(chemin)
    return !!(ctrl?.errors?.[erreur] && (ctrl.dirty || ctrl.touched))
  }

  soumettre(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched()
      return
    }
    this.isLoading = true
    // Envoyer au serveur...
  }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur avec le formulaire d'inscription, Angular DevTools ouvert sur le FormGroup
> **Expliquer :** Ouvrir Angular DevTools → sélectionner le composant du formulaire → dans le panneau de droite, montrer le FormGroup avec l'état de chaque contrôle (valid, invalid, dirty, touched, errors). Soumettre le formulaire avec des données invalides et montrer que markAllAsTouched() déclenche l'affichage de toutes les erreurs. Montrer le pending state pendant la validation asynchrone (appel API en cours).
---

## Résumé

| Classe | Description | Utilisation |
|---|---|---|
| `FormControl` | Un champ individuel | `new FormControl('', Validators.required)` |
| `FormGroup` | Groupe de contrôles | `fb.group({ champ: ['', V.required] })` |
| `FormArray` | Liste dynamique de contrôles | `fb.array([fb.control('')])` |
| `FormBuilder` | Factory pour créer les formulaires | `inject(FormBuilder)` |
| `Validators` | Validations built-in | `Validators.required`, `.email`, `.min(0)` |
| `ValidatorFn` | Validation custom synchrone | `(ctrl) => errors \| null` |
| `AsyncValidatorFn` | Validation custom asynchrone | `(ctrl) => Observable<errors \| null>` |

**Prochaine étape :** RxJS — programmation réactive avancée →
