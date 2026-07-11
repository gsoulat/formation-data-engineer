# Securisation des donnees avec Ansible Vault

> Jour 3 - Matin partie 2 (~1h30)

## Table des matieres

1. [Introduction a Ansible Vault](#introduction-a-ansible-vault)
2. [Creation et utilisation de fichiers Vault](#creation-et-utilisation-de-fichiers-vault)
3. [TP : Configurer un playbook utilisant des donnees securisees via Ansible Vault](#tp--configurer-un-playbook-utilisant-des-donnees-securisees-via-ansible-vault)

---

## Introduction a Ansible Vault

### Pourquoi gerer les secrets ?

Dans tout projet d'automatisation, il est necessaire de manipuler des donnees sensibles :

- Mots de passe de bases de donnees
- Cles d'API tierces
- Certificats SSL et cles privees
- Tokens d'authentification
- Identifiants de comptes de service

Stocker ces informations en clair dans un depot Git est une faille de securite majeure. Meme dans un depot prive, toute personne ayant acces au repository peut lire les secrets. De plus, l'historique Git conserve indefiniment les valeurs commitees.

### Qu'est-ce qu'Ansible Vault ?

**Ansible Vault** est l'outil integre a Ansible pour chiffrer et dechiffrer des donnees sensibles. Il utilise le chiffrement symetrique **AES-256** (Advanced Encryption Standard) pour proteger les fichiers et les variables.

**Caracteristiques principales :**

- Chiffrement AES-256 symetrique (une seule cle pour chiffrer et dechiffrer)
- Integre nativement a Ansible (aucune dependance externe)
- Permet de chiffrer des fichiers entiers ou des variables individuelles
- Compatible avec les workflows Git (les fichiers chiffres sont commitables)
- Support de plusieurs mots de passe via les Vault IDs

**Ce que Vault peut chiffrer :**

- Des fichiers YAML complets (group_vars, host_vars, fichiers de variables)
- Des variables individuelles au sein d'un fichier YAML (via `encrypt_string`)
- Des fichiers quelconques (certificats, cles privees, fichiers de configuration)

**Ce que Vault ne fait pas :**

- Il ne gere pas la rotation automatique des secrets
- Il ne remplace pas un gestionnaire de secrets centralise (HashiCorp Vault, AWS Secrets Manager) pour les environnements de production complexes
- Il ne chiffre pas les donnees en transit lors de l'execution des playbooks

---

## Creation et utilisation de fichiers Vault

### Commandes principales

#### Creer un fichier chiffre

```bash
# Creer un nouveau fichier chiffre (ouvre l'editeur par defaut)
ansible-vault create group_vars/all/vault.yml
```

Ansible demande un mot de passe, puis ouvre l'editeur (`$EDITOR` ou `vi` par defaut). Le contenu saisi sera chiffre automatiquement a la sauvegarde.

#### Editer un fichier chiffre

```bash
# Modifier un fichier deja chiffre
ansible-vault edit group_vars/all/vault.yml
```

Le fichier est dechiffre temporairement en memoire, ouvert dans l'editeur, puis re-chiffre a la sauvegarde.

#### Chiffrer un fichier existant

```bash
# Chiffrer un fichier YAML existant (non chiffre)
ansible-vault encrypt group_vars/production/secrets.yml

# Chiffrer plusieurs fichiers d'un coup
ansible-vault encrypt fichier1.yml fichier2.yml fichier3.yml
```

#### Dechiffrer un fichier

```bash
# Dechiffrer un fichier (le remet en clair sur le disque)
ansible-vault decrypt group_vars/all/vault.yml
```

Attention : le fichier sera en clair apres cette commande. A utiliser uniquement de facon temporaire.

#### Voir le contenu sans modifier

```bash
# Afficher le contenu dechiffre sans ouvrir d'editeur
ansible-vault view group_vars/all/vault.yml
```

#### Changer le mot de passe (rekey)

```bash
# Changer le mot de passe de chiffrement
ansible-vault rekey group_vars/all/vault.yml

# Rekey de plusieurs fichiers
ansible-vault rekey fichier1.yml fichier2.yml
```

### Format d'un fichier chiffre

Un fichier chiffre par Vault a cette structure :

```
$ANSIBLE_VAULT;1.1;AES256
38623538653836353765383439633964323030316264363565356131353830333262336538383938
61363733333266623063366231633333356637313535383737326462316339340a63336435346530
...
```

La premiere ligne identifie le format et l'algorithme. Le reste est le contenu chiffre en hexadecimal.

### Chiffrer des variables individuelles avec encrypt_string

Plutot que de chiffrer un fichier entier, il est possible de chiffrer une seule variable. Cela permet de melanger variables chiffrees et non chiffrees dans le meme fichier.

```bash
# Chiffrer une valeur
ansible-vault encrypt_string 'MonMotDePasseSecret' --name 'vault_db_password'

# Resultat a coller dans un fichier YAML :
vault_db_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    62303831626266613035386662373333...
```

```bash
# Chiffrer depuis stdin (utile pour eviter l'historique shell)
echo -n 'MonMotDePasseSecret' | ansible-vault encrypt_string --stdin-name 'vault_db_password'

# Chiffrer avec un vault ID specifique
ansible-vault encrypt_string --vault-id prod@prompt 'MonSecret' --name 'vault_api_key'
```

Exemple de fichier mixte avec variables chiffrees et non chiffrees :

```yaml
# group_vars/production/vars.yml
---
# Variables non sensibles (en clair)
db_host: db.production.local
db_port: 3306
db_name: mon_application
app_version: "2.1.0"

# Variables sensibles (chiffrees individuellement)
db_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    38623538653836353765383439633964...

api_key: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    61363733333266623063366231633333...
```

### Vault IDs : gerer plusieurs mots de passe

Dans un environnement avec plusieurs niveaux (dev, staging, production), il est utile d'avoir des mots de passe differents pour chaque contexte.

```bash
# Creer un fichier avec un vault ID specifique
ansible-vault create --vault-id prod@prompt group_vars/production/vault.yml
ansible-vault create --vault-id staging@prompt group_vars/staging/vault.yml

# Editer avec un vault ID
ansible-vault edit --vault-id prod@prompt group_vars/production/vault.yml

# Chiffrer une variable avec un vault ID
ansible-vault encrypt_string --vault-id prod@prompt 'secret' --name 'vault_api_key'
```

Le format du vault ID est `label@source` ou `source` peut etre :

- `prompt` : demander le mot de passe interactivement
- Un chemin vers un fichier contenant le mot de passe
- Un chemin vers un script executable qui retourne le mot de passe

### vault-password-file : automatiser le mot de passe

Pour eviter de saisir le mot de passe a chaque execution, on peut utiliser un fichier de mot de passe.

**Creer le fichier :**

```bash
# Creer un fichier contenant le mot de passe
echo 'mon-mot-de-passe-vault-tres-long' > .vault_pass
chmod 600 .vault_pass
```

**Ajouter au .gitignore :**

```gitignore
# Ne JAMAIS committer le fichier de mot de passe
.vault_pass
*vault_pass*
```

**Utiliser le fichier de mot de passe :**

```bash
# En ligne de commande
ansible-vault view group_vars/all/vault.yml --vault-password-file .vault_pass

# Ou configurer dans ansible.cfg pour ne plus le specifier
```

**ansible.cfg :**

```ini
[defaults]
vault_password_file = .vault_pass
```

**Variable d'environnement :**

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
```

### Integration dans les playbooks

Ansible dechiffre automatiquement les fichiers et variables Vault lors de l'execution d'un playbook. Il suffit de fournir le mot de passe.

```bash
# Demander le mot de passe interactivement
ansible-playbook -i inventory site.yml --ask-vault-pass

# Utiliser un fichier de mot de passe
ansible-playbook -i inventory site.yml --vault-password-file .vault_pass

# Utiliser plusieurs vault IDs
ansible-playbook -i inventory site.yml \
  --vault-id prod@.vault_pass_prod \
  --vault-id staging@.vault_pass_staging
```

### Structure recommandee pour les secrets

La bonne pratique est de separer les variables normales et les variables chiffrees dans des fichiers distincts, tout en utilisant un prefixe `vault_` pour les secrets :

```
inventory/
└── production/
    ├── hosts.yml
    └── group_vars/
        └── all/
            ├── vars.yml       # Variables non sensibles
            └── vault.yml      # Variables sensibles (chiffre)
```

**vars.yml (non chiffre) :**

```yaml
---
db_host: db.production.local
db_port: 3306
db_name: mon_application

# References vers les variables vault
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
ssl_key: "{{ vault_ssl_key }}"
```

**vault.yml (chiffre) :**

```yaml
---
vault_db_password: SuperSecretP@ssw0rd
vault_api_key: sk-abc123def456ghi789jkl012
vault_ssl_key: |
  -----BEGIN PRIVATE KEY-----
  MIIEvgIBADANBgkqhkiG9w0BAQEFAASC...
  -----END PRIVATE KEY-----
```

Avantages de cette approche :
- On voit quelles variables existent sans dechiffrer le vault
- Les variables non sensibles restent facilement lisibles et modifiables
- Le prefixe `vault_` identifie clairement l'origine d'une variable

---

## TP : Configurer un playbook utilisant des donnees securisees via Ansible Vault

### Objectifs

- Securiser un deploiement en protegeant les mots de passe et cles sensibles avec Ansible Vault
- Maitriser les commandes create, edit, encrypt, decrypt, view et encrypt_string
- Integrer des fichiers Vault dans un playbook fonctionnel
- Tester l'execution avec `--ask-vault-pass` et `--vault-password-file`

### Contexte

Vous devez deployer une application web avec les elements suivants :
- Un serveur Nginx en frontal
- Une base de donnees PostgreSQL avec des identifiants proteges
- Une cle d'API pour un service externe
- Un certificat SSL auto-signe

Toutes les donnees sensibles doivent etre stockees dans un fichier Vault chiffre.

### Prerequis

- Ansible installe sur la machine de controle
- Un hote cible accessible en SSH
- Le TP precedent sur les roles (optionnel mais recommande)

### Etape 1 : Preparer la structure du projet

```bash
# Creer le projet
mkdir -p ansible-tp-vault/{inventory/production/group_vars/all,playbooks,roles}
cd ansible-tp-vault

# Creer l'inventaire
cat > inventory/production/hosts.yml << 'EOF'
---
all:
  children:
    webservers:
      hosts:
        web1:
          ansible_host: 192.168.56.10
          ansible_user: vagrant
    dbservers:
      hosts:
        db1:
          ansible_host: 192.168.56.11
          ansible_user: vagrant
EOF
```

### Etape 2 : Creer le fichier Vault avec les secrets

```bash
# Creer le fichier vault chiffre
ansible-vault create inventory/production/group_vars/all/vault.yml
```

Saisir le mot de passe vault (par exemple : `FormationAnsible2024!`), puis entrer le contenu suivant dans l'editeur :

```yaml
---
# Identifiants PostgreSQL
vault_db_root_password: "Pg@dmin2024!Secure"
vault_db_app_password: "AppUs3r!S3cret#2024"
vault_db_app_user: "app_user"

# Cle d'API externe
vault_api_key: "sk-prod-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
vault_api_secret: "secret-x9y8z7w6v5u4t3s2r1q0"

# Mot de passe du compte admin de l'application
vault_admin_password: "Adm1n!P@ssw0rd#Secure"
```

### Etape 3 : Creer le fichier de variables non sensibles

```bash
cat > inventory/production/group_vars/all/vars.yml << 'EOF'
---
# Configuration de la base de donnees
db_host: db1
db_port: 5432
db_name: mon_application

# References vers les variables vault
db_root_password: "{{ vault_db_root_password }}"
db_app_password: "{{ vault_db_app_password }}"
db_app_user: "{{ vault_db_app_user }}"

# Configuration de l'API externe
api_endpoint: "https://api.service-externe.com/v2"
api_key: "{{ vault_api_key }}"
api_secret: "{{ vault_api_secret }}"

# Configuration de l'application
app_name: "mon-application"
app_port: 8080
admin_user: "admin"
admin_password: "{{ vault_admin_password }}"
EOF
```

### Etape 4 : Tester encrypt_string pour une variable individuelle

```bash
# Chiffrer une variable individuelle
ansible-vault encrypt_string 'MonTokenGitHub12345' --name 'vault_github_token'

# Resultat a ajouter dans un fichier YAML si necessaire :
# vault_github_token: !vault |
#     $ANSIBLE_VAULT;1.1;AES256
#     ...
```

### Etape 5 : Creer le playbook de deploiement

```bash
cat > playbooks/deploy.yml << 'PLAYBOOK'
---
- name: Deployer la base de donnees
  hosts: dbservers
  become: yes

  tasks:
    - name: Installer PostgreSQL
      ansible.builtin.apt:
        name:
          - postgresql
          - postgresql-contrib
          - python3-psycopg2
        state: present
        update_cache: yes

    - name: Demarrer PostgreSQL
      ansible.builtin.service:
        name: postgresql
        state: started
        enabled: yes

    - name: Configurer le mot de passe root PostgreSQL
      become_user: postgres
      community.postgresql.postgresql_user:
        name: postgres
        password: "{{ db_root_password }}"
        state: present
      no_log: true

    - name: Creer l'utilisateur applicatif
      become_user: postgres
      community.postgresql.postgresql_user:
        name: "{{ db_app_user }}"
        password: "{{ db_app_password }}"
        state: present
      no_log: true

    - name: Creer la base de donnees
      become_user: postgres
      community.postgresql.postgresql_db:
        name: "{{ db_name }}"
        owner: "{{ db_app_user }}"
        state: present

    - name: Verifier la connexion a la base (sans afficher le mot de passe)
      ansible.builtin.debug:
        msg: "Base {{ db_name }} prete sur {{ db_host }}:{{ db_port }} pour l'utilisateur {{ db_app_user }}"

- name: Deployer l'application web
  hosts: webservers
  become: yes

  tasks:
    - name: Installer Nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Deployer la configuration de l'application
      ansible.builtin.template:
        src: ../templates/app_config.yml.j2
        dest: /etc/mon-application/config.yml
        owner: root
        group: root
        mode: "0600"
      notify: Redemarrer l'application

    - name: Afficher le resume du deploiement
      ansible.builtin.debug:
        msg: |
          Deploiement termine :
          - Application : {{ app_name }}
          - Port : {{ app_port }}
          - Base de donnees : {{ db_name }}@{{ db_host }}:{{ db_port }}
          - API externe : {{ api_endpoint }}
          (les secrets ne sont pas affiches)

  handlers:
    - name: Redemarrer l'application
      ansible.builtin.debug:
        msg: "L'application serait redemarree ici"
PLAYBOOK
```

### Etape 6 : Creer le template de configuration

```bash
mkdir -p templates

cat > templates/app_config.yml.j2 << 'EOF'
# Configuration generee par Ansible -- Ne pas modifier manuellement
# Fichier sensible : contient des secrets

application:
  name: {{ app_name }}
  port: {{ app_port }}
  admin:
    user: {{ admin_user }}
    password: {{ admin_password }}

database:
  host: {{ db_host }}
  port: {{ db_port }}
  name: {{ db_name }}
  user: {{ db_app_user }}
  password: {{ db_app_password }}

external_api:
  endpoint: {{ api_endpoint }}
  key: {{ api_key }}
  secret: {{ api_secret }}
EOF
```

### Etape 7 : Configurer le fichier de mot de passe automatique

```bash
# Creer le fichier de mot de passe
echo 'FormationAnsible2024!' > .vault_pass
chmod 600 .vault_pass

# Ajouter au .gitignore
echo '.vault_pass' >> .gitignore
echo '*vault_pass*' >> .gitignore

# Configurer ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = inventory/production/hosts.yml
vault_password_file = .vault_pass
host_key_checking = False
stdout_callback = yaml
EOF
```

### Etape 8 : Tester le deploiement

```bash
# Verifier que le vault est accessible
ansible-vault view inventory/production/group_vars/all/vault.yml

# Verifier la syntaxe du playbook
ansible-playbook playbooks/deploy.yml --syntax-check

# Lancer en mode dry-run avec demande de mot de passe (sans le fichier)
ansible-playbook playbooks/deploy.yml --check --ask-vault-pass

# Lancer en mode dry-run avec le fichier de mot de passe
ansible-playbook playbooks/deploy.yml --check --vault-password-file .vault_pass

# Lancer le deploiement reel (le vault_password_file est dans ansible.cfg)
ansible-playbook playbooks/deploy.yml
```

### Etape 9 : Operations de maintenance

```bash
# Voir le contenu du vault
ansible-vault view inventory/production/group_vars/all/vault.yml

# Modifier un secret (par exemple, rotation de mot de passe)
ansible-vault edit inventory/production/group_vars/all/vault.yml

# Changer le mot de passe du vault lui-meme
ansible-vault rekey inventory/production/group_vars/all/vault.yml

# Dechiffrer temporairement pour debug (re-chiffrer immediatement apres)
ansible-vault decrypt inventory/production/group_vars/all/vault.yml
# ... verifications ...
ansible-vault encrypt inventory/production/group_vars/all/vault.yml
```

### Livrables

- Un fichier `vault.yml` chiffre contenant les secrets (mots de passe DB, cles API, mot de passe admin)
- Un fichier `vars.yml` avec les variables non sensibles et les references vers le vault
- Un playbook `deploy.yml` fonctionnel utilisant les secrets de facon transparente
- Un fichier `ansible.cfg` configurant le `vault_password_file`
- La directive `no_log: true` sur toutes les taches manipulant des secrets

### Criteres de validation

| Critere | Attendu |
|---------|---------|
| Chiffrement | Le fichier vault.yml est correctement chiffre (commence par `$ANSIBLE_VAULT;1.1;AES256`) |
| Separation | Les variables sensibles sont dans vault.yml, les non-sensibles dans vars.yml |
| Convention de nommage | Toutes les variables vault sont prefixees par `vault_` |
| no_log | Les taches manipulant des secrets utilisent `no_log: true` |
| Execution avec --ask-vault-pass | Le playbook s'execute correctement en saisissant le mot de passe |
| Execution avec vault-password-file | Le playbook s'execute correctement avec le fichier de mot de passe |
| Securite du fichier de mot de passe | `.vault_pass` a les permissions 600 et est dans le `.gitignore` |
| Aucun secret en clair | `git diff` et `git log` ne revelent aucun secret en clair |

---

## Ressources

- [Documentation officielle -- Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
- [Bonnes pratiques Vault](https://docs.ansible.com/ansible/latest/vault_guide/vault_best_practices.html)
- [encrypt_string](https://docs.ansible.com/ansible/latest/vault_guide/vault_encrypting_content.html#encrypting-individual-variables)

---

**Cours precedent :** [05-Roles-Ansible](../05-Roles-Ansible/README.md)

**Suite du cours :** [07-Tower-Vagrant](../07-Tower-Vagrant/README.md)
