# 01 — Formulaires : React Hook Form + Zod

## Introduction

Les formulaires contrôlés avec `useState` fonctionnent bien pour les formulaires simples. Pour les formulaires complexes, React Hook Form offre de meilleures performances (pas de re-rendu à chaque frappe) et Zod fournit une validation typée et réutilisable.

---

## Installation

```bash
npm install react-hook-form zod @hookform/resolvers
```

---

## 1. React Hook Form — Les bases

```jsx
import { useForm } from "react-hook-form";

function FormulaireSimple() {
  const {
    register,        // Enregistrer un champ
    handleSubmit,    // Wrapper pour onSubmit
    formState: { errors, isSubmitting, isValid },
    watch,           // Observer la valeur d'un champ
    reset,           // Réinitialiser le formulaire
    setValue,        // Modifier programmatiquement une valeur
    getValues,       // Lire les valeurs sans s'abonner
  } = useForm({
    defaultValues: {
      prenom: "",
      email: "",
      age: 18,
    },
    mode: "onChange", // Quand valider : "onSubmit" | "onBlur" | "onChange" | "all"
  });

  const onSubmit = async (donnees) => {
    // donnees contient toutes les valeurs validées
    console.log("Données valides:", donnees);
    await envoyerDonnees(donnees);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {/* register() lie le champ au formulaire */}
      <div>
        <label htmlFor="prenom">Prénom</label>
        <input
          id="prenom"
          {...register("prenom", {
            required: "Le prénom est obligatoire",
            minLength: { value: 2, message: "Minimum 2 caractères" },
            maxLength: { value: 50, message: "Maximum 50 caractères" },
          })}
        />
        {errors.prenom && <span className="erreur">{errors.prenom.message}</span>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register("email", {
            required: "L'email est obligatoire",
            pattern: {
              value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
              message: "Email invalide",
            },
          })}
        />
        {errors.email && <span className="erreur">{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="age">Âge</label>
        <input
          id="age"
          type="number"
          {...register("age", {
            required: "L'âge est obligatoire",
            min: { value: 18, message: "Vous devez avoir 18 ans minimum" },
            max: { value: 120, message: "Âge invalide" },
            valueAsNumber: true, // Convertit en number (sinon c'est une string)
          })}
        />
        {errors.age && <span className="erreur">{errors.age.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Envoi en cours..." : "Envoyer"}
      </button>

      <button type="button" onClick={() => reset()}>Réinitialiser</button>
    </form>
  );
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Profiler React — comparer les re-rendus d'un formulaire useState (se re-rend à chaque frappe) vs React Hook Form (ne se re-rend que pour les erreurs et la soumission). Montrer visuellement la différence avec un formulaire de 10 champs.
> **Expliquer :** React Hook Form utilise des refs non-contrôlées en interne. La valeur du champ est lue directement depuis le DOM au moment de la soumission. Ça évite des dizaines de re-rendus inutiles par seconde pendant la saisie.

---

## 2. Validation avec Zod

Zod est une bibliothèque de validation et de parsing typée. Elle permet de définir des schémas réutilisables, séparés des composants.

```typescript
// src/schemas/utilisateurSchema.ts
import { z } from "zod";

// Définir le schéma
export const schemaInscription = z
  .object({
    prenom: z
      .string()
      .min(1, "Le prénom est obligatoire")
      .min(2, "Minimum 2 caractères")
      .max(50, "Maximum 50 caractères"),

    nom: z
      .string()
      .min(1, "Le nom est obligatoire")
      .max(100, "Maximum 100 caractères"),

    email: z
      .string()
      .min(1, "L'email est obligatoire")
      .email("Format d'email invalide"),

    motDePasse: z
      .string()
      .min(8, "Minimum 8 caractères")
      .regex(/[A-Z]/, "Doit contenir au moins une majuscule")
      .regex(/[0-9]/, "Doit contenir au moins un chiffre")
      .regex(/[^a-zA-Z0-9]/, "Doit contenir au moins un caractère spécial"),

    confirmationMotDePasse: z.string().min(1, "La confirmation est obligatoire"),

    age: z
      .number({ invalid_type_error: "L'âge doit être un nombre" })
      .int("L'âge doit être un entier")
      .min(18, "Vous devez avoir au moins 18 ans")
      .max(120, "Âge invalide"),

    role: z.enum(["utilisateur", "moderateur", "admin"], {
      errorMap: () => ({ message: "Rôle invalide" }),
    }),

    accepteConditions: z
      .boolean()
      .refine(v => v === true, "Vous devez accepter les conditions"),
  })
  .refine(
    (data) => data.motDePasse === data.confirmationMotDePasse,
    {
      message: "Les mots de passe ne correspondent pas",
      path: ["confirmationMotDePasse"], // Sur quel champ afficher l'erreur
    }
  );

// Inférer le type TypeScript depuis le schéma Zod
export type DonneesInscription = z.infer<typeof schemaInscription>;
// DonneesInscription = {
//   prenom: string;
//   nom: string;
//   email: string;
//   motDePasse: string;
//   confirmationMotDePasse: string;
//   age: number;
//   role: "utilisateur" | "moderateur" | "admin";
//   accepteConditions: boolean;
// }
```

## 3. React Hook Form + Zod ensemble

```tsx
// src/components/FormulaireInscription.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { schemaInscription, type DonneesInscription } from "../schemas/utilisateurSchema";

function FormulaireInscription() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, touchedFields, dirtyFields },
    watch,
    reset,
  } = useForm<DonneesInscription>({
    resolver: zodResolver(schemaInscription), // Connecter Zod à RHF
    defaultValues: {
      prenom: "",
      nom: "",
      email: "",
      motDePasse: "",
      confirmationMotDePasse: "",
      age: 18,
      role: "utilisateur",
      accepteConditions: false,
    },
    mode: "onBlur", // Valider quand on quitte un champ
  });

  // Observer la valeur du mot de passe pour la jauge de force
  const motDePasse = watch("motDePasse");

  const forceMdp = calculerForce(motDePasse);

  const onSubmit = async (donnees: DonneesInscription) => {
    // Ici, donnees est entièrement typé et validé par Zod
    try {
      await fetch("/api/inscription", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(donnees),
      });
      reset();
      alert("Inscription réussie !");
    } catch (err) {
      console.error("Erreur d'inscription:", err);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="formulaire">
      {/* Groupe prénom + nom */}
      <div className="champs-ligne">
        <ChampFormulaire
          label="Prénom"
          erreur={errors.prenom?.message}
          touche={touchedFields.prenom}
        >
          <input id="prenom" {...register("prenom")} />
        </ChampFormulaire>

        <ChampFormulaire
          label="Nom"
          erreur={errors.nom?.message}
          touche={touchedFields.nom}
        >
          <input id="nom" {...register("nom")} />
        </ChampFormulaire>
      </div>

      <ChampFormulaire label="Email" erreur={errors.email?.message} touche={touchedFields.email}>
        <input id="email" type="email" {...register("email")} />
      </ChampFormulaire>

      <ChampFormulaire label="Mot de passe" erreur={errors.motDePasse?.message} touche={touchedFields.motDePasse}>
        <input id="motDePasse" type="password" {...register("motDePasse")} />
        <JaugeForceMdp force={forceMdp} />
      </ChampFormulaire>

      <ChampFormulaire
        label="Confirmer le mot de passe"
        erreur={errors.confirmationMotDePasse?.message}
        touche={touchedFields.confirmationMotDePasse}
      >
        <input id="confirmation" type="password" {...register("confirmationMotDePasse")} />
      </ChampFormulaire>

      <ChampFormulaire label="Âge" erreur={errors.age?.message} touche={touchedFields.age}>
        <input
          id="age"
          type="number"
          {...register("age", { valueAsNumber: true })}
        />
      </ChampFormulaire>

      <ChampFormulaire label="Rôle" erreur={errors.role?.message} touche={touchedFields.role}>
        <select id="role" {...register("role")}>
          <option value="utilisateur">Utilisateur</option>
          <option value="moderateur">Modérateur</option>
          <option value="admin">Administrateur</option>
        </select>
      </ChampFormulaire>

      <div className="champ-checkbox">
        <label>
          <input type="checkbox" {...register("accepteConditions")} />
          J'accepte les <a href="/conditions">conditions d'utilisation</a>
        </label>
        {errors.accepteConditions && (
          <span className="erreur">{errors.accepteConditions.message}</span>
        )}
      </div>

      <div className="actions">
        <button type="submit" disabled={isSubmitting} className="btn-primaire">
          {isSubmitting ? "Inscription en cours..." : "S'inscrire"}
        </button>
        <button type="button" onClick={() => reset()} className="btn-secondaire">
          Effacer
        </button>
      </div>
    </form>
  );
}

// Composant helper pour les champs
function ChampFormulaire({ label, erreur, touche, children }) {
  return (
    <div className={`champ ${erreur && touche ? "champ-erreur" : ""} ${!erreur && touche ? "champ-valide" : ""}`}>
      <label>{label}</label>
      {children}
      {erreur && <span className="message-erreur">{erreur}</span>}
    </div>
  );
}

// Jauge de force du mot de passe
function calculerForce(mdp = "") {
  let score = 0;
  if (mdp.length >= 8) score++;
  if (/[A-Z]/.test(mdp)) score++;
  if (/[0-9]/.test(mdp)) score++;
  if (/[^a-zA-Z0-9]/.test(mdp)) score++;
  return score;
}

function JaugeForceMdp({ force }) {
  const labels = ["", "Faible", "Moyen", "Fort", "Très fort"];
  const couleurs = ["", "#ef4444", "#f59e0b", "#22c55e", "#15803d"];

  if (!force) return null;

  return (
    <div className="jauge-force">
      <div className="barres">
        {[1, 2, 3, 4].map(n => (
          <div
            key={n}
            style={{
              height: 4,
              borderRadius: 2,
              background: n <= force ? couleurs[force] : "#e2e8f0",
              flex: 1,
            }}
          />
        ))}
      </div>
      <span style={{ color: couleurs[force], fontSize: "0.8rem" }}>
        {labels[force]}
      </span>
    </div>
  );
}
```

---

## 4. Formulaires dynamiques avec useFieldArray

```jsx
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schemaEquipe = z.object({
  nomEquipe: z.string().min(1, "Nom de l'équipe obligatoire"),
  membres: z.array(
    z.object({
      nom: z.string().min(1, "Nom obligatoire"),
      email: z.string().email("Email invalide"),
      role: z.enum(["lead", "dev", "qa"]),
    })
  ).min(1, "Au moins un membre requis"),
});

function FormulaireEquipe() {
  const { register, control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schemaEquipe),
    defaultValues: {
      nomEquipe: "",
      membres: [{ nom: "", email: "", role: "dev" }],
    },
  });

  // useFieldArray pour les listes dynamiques
  const { fields, append, remove, move } = useFieldArray({
    control,
    name: "membres",
  });

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <input
        placeholder="Nom de l'équipe"
        {...register("nomEquipe")}
      />
      {errors.nomEquipe && <span>{errors.nomEquipe.message}</span>}

      <h3>Membres</h3>
      {fields.map((champ, index) => (
        <div key={champ.id} className="membre-ligne">
          <input
            placeholder="Nom"
            {...register(`membres.${index}.nom`)}
          />
          {errors.membres?.[index]?.nom && (
            <span>{errors.membres[index].nom.message}</span>
          )}

          <input
            type="email"
            placeholder="Email"
            {...register(`membres.${index}.email`)}
          />
          {errors.membres?.[index]?.email && (
            <span>{errors.membres[index].email.message}</span>
          )}

          <select {...register(`membres.${index}.role`)}>
            <option value="dev">Développeur</option>
            <option value="lead">Tech Lead</option>
            <option value="qa">QA</option>
          </select>

          <button type="button" onClick={() => remove(index)} disabled={fields.length === 1}>
            Supprimer
          </button>
        </div>
      ))}

      {errors.membres?.root && <span>{errors.membres.root.message}</span>}

      <button
        type="button"
        onClick={() => append({ nom: "", email: "", role: "dev" })}
      >
        + Ajouter un membre
      </button>

      <button type="submit">Créer l'équipe</button>
    </form>
  );
}
```

---

## Récapitulatif

| Concept | Code | Utilité |
|---|---|---|
| Enregistrer un champ | `{...register("champ", regles)}` | Lie le champ au formulaire |
| Valider à la soumission | `handleSubmit(onSubmit)` | Valide puis appelle onSubmit |
| Erreurs | `errors.champ?.message` | Message d'erreur du champ |
| État du formulaire | `formState.isSubmitting` | Pendant la soumission |
| Observer | `watch("champ")` | Réagir aux changements |
| Réinitialiser | `reset()` | Vider le formulaire |
| Zod resolver | `zodResolver(schema)` | Connecter Zod à RHF |
| Liste dynamique | `useFieldArray` | Ajouter/supprimer des champs |
