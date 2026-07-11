# Introduction aux Playbooks Ansible

**Jour 2 - Matin (~3h30)**

## Table des matieres

1. [Structure des Playbooks](#structure-des-playbooks)
2. [Syntaxe YAML](#syntaxe-yaml)
3. [Ecriture des premiers Playbooks](#ecriture-des-premiers-playbooks)
4. [TP : Deployer un service web avec un Playbook](#tp--deployer-un-service-web-avec-un-playbook)

---

## Structure des Playbooks

Un **playbook** est un fichier YAML qui decrit l'etat souhaite de votre infrastructure. C'est le coeur d'Ansible : il permet de passer d'une approche imperative (commandes ad-hoc) a une approche declarative, reproductible et versionnee.

### Anatomie d'un Play

Un playbook est compose d'un ou plusieurs **plays**. Chaque play cible un ensemble d'hotes et execute une serie de taches.

```yaml
---
# site.yml - Un playbook avec deux plays
- name: Configurer les serveurs web        # Nom du play (descriptif)
  hosts: webservers                        # Hotes cibles
  become: yes                              # Elevation de privileges (sudo)
  vars:                                    # Variables du play
    http_port: 80

  tasks:                                   # Liste des taches
    - name: Installer Nginx
      apt:
        name: nginx
        state: present

    - name: Demarrer Nginx
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:                                # Taches declenchees par notify
    - name: Redemarrer Nginx
      service:
        name: nginx
        state: restarted

- name: Configurer les bases de donnees    # Deuxieme play
  hosts: databases
  become: yes
  tasks:
    - name: Installer MySQL
      apt:
        name: mysql-server
        state: present
```

### Composants d'un Play

**1. `name` (optionnel mais fortement recommande)**

Le nom decrit l'intention du play. Il s'affiche dans la sortie d'execution et facilite le debug.

```yaml
- name: Deployer l'application web en production
```

**2. `hosts` (obligatoire)**

Definit les machines ciblees. Accepte des groupes, des patterns ou des combinaisons.

```yaml
# Un groupe d'inventaire
hosts: webservers

# Plusieurs groupes
hosts: webservers:databases

# Tous les hotes
hosts: all

# Pattern avec wildcard
hosts: web*.example.com

# Exclusion d'un hote
hosts: webservers:!web3

# Intersection de groupes
hosts: webservers:&production
```

**3. `become` (elevation de privileges)**

Permet d'executer les taches avec des privileges root (sudo).

```yaml
# Au niveau du play : toutes les taches en sudo
- name: Configuration systeme
  hosts: all
  become: yes
  become_user: root       # Utilisateur cible (root par defaut)
  become_method: sudo     # Methode (sudo par defaut)

  tasks:
    - name: Installer un package
      apt:
        name: nginx
        state: present

    # Au niveau d'une tache specifique
    - name: Executer en tant qu'utilisateur app
      command: /opt/app/start.sh
      become_user: appuser
```

**4. `tasks` (liste de taches)**

Chaque tache appelle un **module** Ansible avec des parametres. L'ordre d'execution est sequentiel.

```yaml
tasks:
  - name: Mettre a jour le cache APT
    apt:
      update_cache: yes
      cache_valid_time: 3600

  - name: Installer les packages requis
    apt:
      name:
        - nginx
        - curl
        - vim
      state: present

  - name: Copier la configuration
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
      owner: root
      group: root
      mode: '0644'
```

**5. `handlers` (taches conditionnelles)**

Les handlers sont des taches speciales qui ne s'executent que lorsqu'elles sont notifiees par une autre tache via `notify`.

```yaml
tasks:
  - name: Copier la configuration Nginx
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
    notify: Recharger Nginx      # Declenche le handler si changement

handlers:
  - name: Recharger Nginx        # S'execute seulement si notifie
    service:
      name: nginx
      state: reloaded
```

Points importants sur les handlers :

- Ils s'executent **a la fin du play**, pas immediatement apres la notification
- Ils ne s'executent qu'**une seule fois**, meme s'ils sont notifies plusieurs fois
- Ils s'executent dans l'**ordre de definition** dans la section `handlers`
- On peut forcer leur execution immediate avec `meta: flush_handlers`

```yaml
tasks:
  - name: Copier la config principale
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
    notify: Redemarrer Nginx

  - name: Forcer l'execution des handlers maintenant
    meta: flush_handlers

  - name: Verifier que Nginx repond
    uri:
      url: http://localhost
      status_code: 200
```

**Plusieurs notifications :**

```yaml
  - name: Modifier la configuration SSL
    template:
      src: ssl.conf.j2
      dest: /etc/nginx/conf.d/ssl.conf
    notify:
      - Redemarrer Nginx
      - Envoyer notification

handlers:
  - name: Redemarrer Nginx
    service:
      name: nginx
      state: restarted

  - name: Envoyer notification
    debug:
      msg: "Configuration SSL mise a jour"
```

### Modules courants

**Gestion de packages :**

```yaml
# APT (Debian/Ubuntu)
- name: Installer Nginx
  apt:
    name: nginx
    state: present
    update_cache: yes

# YUM (RHEL/CentOS)
- name: Installer Apache
  yum:
    name: httpd
    state: present

# Package (abstraction multi-OS)
- name: Installer un package
  package:
    name: nginx
    state: present
```

**Gestion de services :**

```yaml
- name: Demarrer et activer Nginx
  service:
    name: nginx
    state: started      # started, stopped, restarted, reloaded
    enabled: yes        # Demarrage automatique au boot
```

**Gestion de fichiers :**

```yaml
# Copier un fichier
- name: Copier la configuration
  copy:
    src: app.conf
    dest: /etc/app/config.conf
    owner: root
    group: root
    mode: '0644'

# Creer un repertoire
- name: Creer le repertoire web
  file:
    path: /var/www/html
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'

# Copier du contenu inline
- name: Creer la page d'accueil
  copy:
    content: |
      <!DOCTYPE html>
      <html>
      <body><h1>Bienvenue</h1></body>
      </html>
    dest: /var/www/html/index.html
```

**Execution de commandes :**

```yaml
# Command (simple, sans shell)
- name: Verifier le temps d'activite
  command: uptime

# Shell (avec pipes, redirections)
- name: Compter les connexions actives
  shell: netstat -an | grep ESTABLISHED | wc -l

# Script distant
- name: Executer un script
  script: scripts/setup.sh
```

---

## Syntaxe YAML

YAML (YAML Ain't Markup Language) est le format utilise par Ansible pour les playbooks. Une bonne maitrise de YAML est indispensable.

### Scalaires

Les valeurs simples : chaines de caracteres, nombres, booleens.

```yaml
# Chaines de caracteres
nom: "Jean Dupont"
message: Hello World
chemin: /etc/nginx/nginx.conf

# Nombres
port: 80
timeout: 30.5
version: 2

# Booleens
active: true
debug: false
ssl_enabled: yes    # Equivalent a true
backup: no          # Equivalent a false
```

### Listes

```yaml
# Style bloc (recommande)
packages:
  - nginx
  - curl
  - vim
  - git

# Style inline
packages: [nginx, curl, vim, git]

# Liste de dictionnaires
utilisateurs:
  - nom: alice
    role: admin
  - nom: bob
    role: developpeur
```

### Dictionnaires

```yaml
# Style bloc (recommande)
serveur:
  nom: web1
  ip: 192.168.1.10
  port: 80
  actif: true

# Style inline
serveur: {nom: web1, ip: 192.168.1.10, port: 80}

# Dictionnaires imbriques
application:
  nom: monapp
  config:
    database:
      host: localhost
      port: 3306
    cache:
      type: redis
      host: cache.local
```

### Chaines multi-lignes

```yaml
# Bloc litteral (|) : conserve les sauts de ligne
script: |
  #!/bin/bash
  echo "Ligne 1"
  echo "Ligne 2"
  exit 0

# Bloc replie (>) : fusionne les lignes en une seule
description: >
  Ceci est une tres longue
  description qui sera fusionnee
  en une seule ligne.

# Avec strip (-) : supprime le saut de ligne final
contenu: |-
  Ligne 1
  Ligne 2
```

### Ancres et aliases

Les ancres permettent de reutiliser des blocs YAML pour eviter la duplication.

```yaml
# Definir une ancre avec &
defaults: &defaults_app
  restart: always
  timeout: 30
  retries: 3

# Reutiliser avec *
service_web:
  <<: *defaults_app       # Insere toutes les cles de defaults_app
  name: nginx
  port: 80

service_api:
  <<: *defaults_app
  name: gunicorn
  port: 8000
```

### Pieges courants

**1. Indentation incorrecte :**

```yaml
# CORRECT : 2 espaces
- name: Installer Nginx
  apt:
    name: nginx
    state: present

# INCORRECT : tabulations ou indentation inconsistante
- name: Installer Nginx
	apt:
	    name: nginx
```

Regle d'or : utiliser **toujours 2 espaces**, jamais de tabulations.

**2. Variables Jinja2 sans quotes :**

```yaml
# CORRECT : quotes autour de la valeur Jinja2
message: "{{ ma_variable }}"

# INCORRECT : sans quotes quand la valeur commence par {{
message: {{ ma_variable }}    # Erreur de parsing YAML
```

**3. Caracteres speciaux non echappes :**

```yaml
# CORRECT
message: "Le port est : 80"
chemin: "C:\\Users\\admin"

# INCORRECT
message: Le port est : 80    # Le ":" peut poser probleme
```

**4. Booleens involontaires :**

```yaml
# Attention : YAML interprete certaines valeurs comme booleens
pays: no        # Interprete comme false !
pays: "no"      # Chaine de caracteres "no"

version: 1.0    # Interprete comme nombre flottant
version: "1.0"  # Chaine de caracteres "1.0"
```

---

## Ecriture des premiers Playbooks

### Hello World

Le playbook le plus simple pour verifier que tout fonctionne :

```yaml
---
# hello.yml
- name: Mon premier playbook
  hosts: all
  tasks:
    - name: Afficher un message
      debug:
        msg: "Bonjour depuis Ansible !"

    - name: Afficher des informations sur l'hote
      debug:
        msg: "Je suis execute sur {{ inventory_hostname }}"
```

```bash
# Executer le playbook
ansible-playbook hello.yml -i inventory.ini
```

### Installer un package

```yaml
---
# install-nginx.yml
- name: Installer et configurer Nginx
  hosts: webservers
  become: yes
  tasks:
    - name: Mettre a jour le cache APT
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Installer Nginx
      apt:
        name: nginx
        state: present
```

### Gerer un service

```yaml
---
# manage-service.yml
- name: Gerer le service Nginx
  hosts: webservers
  become: yes
  tasks:
    - name: S'assurer que Nginx est installe
      apt:
        name: nginx
        state: present

    - name: Demarrer Nginx
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Verifier que le port 80 est ouvert
      wait_for:
        port: 80
        timeout: 10
```

### Utiliser les handlers

```yaml
---
# configure-nginx.yml
- name: Configurer Nginx avec handlers
  hosts: webservers
  become: yes
  vars:
    server_name: monsite.local

  tasks:
    - name: Installer Nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Deployer la configuration du site
      copy:
        content: |
          server {
              listen 80;
              server_name {{ server_name }};
              root /var/www/{{ server_name }};
              index index.html;
          }
        dest: /etc/nginx/sites-available/{{ server_name }}
        owner: root
        group: root
        mode: '0644'
      notify: Recharger Nginx

    - name: Activer le site
      file:
        src: /etc/nginx/sites-available/{{ server_name }}
        dest: /etc/nginx/sites-enabled/{{ server_name }}
        state: link
      notify: Recharger Nginx

    - name: Creer le repertoire web
      file:
        path: /var/www/{{ server_name }}
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'

    - name: Deployer la page d'accueil
      copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head><title>{{ server_name }}</title></head>
          <body>
            <h1>Bienvenue sur {{ server_name }}</h1>
            <p>Deploye avec Ansible</p>
          </body>
          </html>
        dest: /var/www/{{ server_name }}/index.html
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Demarrer et activer Nginx
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Recharger Nginx
      service:
        name: nginx
        state: reloaded
```

### Idempotence

L'**idempotence** est un principe fondamental d'Ansible : executer un playbook plusieurs fois produit toujours le meme resultat.

```
Etat initial : Package absent
  |
  v
Run 1 : Installer le package  --> changed=true
  |
  v
Etat : Package installe
  |
  v
Run 2 : Package deja present  --> changed=false (ok)
  |
  v
Etat : Package installe (identique)
```

**Modules idempotents (la majorite) :**

```yaml
# Idempotent : ne change rien si nginx est deja installe
- name: S'assurer que Nginx est installe
  apt:
    name: nginx
    state: present

# Idempotent : ne change rien si le repertoire existe deja
- name: S'assurer que le repertoire existe
  file:
    path: /var/www/html
    state: directory
    owner: www-data
```

**Modules NON idempotents par defaut (command, shell) :**

```yaml
# NON idempotent : s'execute a chaque run
- name: Ajouter du texte
  shell: echo "ligne" >> /tmp/fichier.txt

# Rendu idempotent avec creates
- name: Extraire l'archive
  command: tar -xzf /tmp/archive.tar.gz -C /opt/
  args:
    creates: /opt/dossier_extrait

# Rendu idempotent avec changed_when
- name: Verifier un service
  command: systemctl is-active nginx
  register: resultat
  changed_when: false
  failed_when: resultat.rc not in [0, 3]
```

**Tester l'idempotence :**

```bash
# Premier run : des changements sont attendus
ansible-playbook site.yml
# PLAY RECAP: changed=5

# Deuxieme run : aucun changement = idempotent
ansible-playbook site.yml
# PLAY RECAP: changed=0
```

### Check mode et diff mode

Le **check mode** (dry-run) simule l'execution sans appliquer de changements.

```bash
# Simuler l'execution (dry-run)
ansible-playbook site.yml --check

# Afficher les differences de fichiers
ansible-playbook site.yml --diff

# Combiner les deux (ideal pour la revue)
ansible-playbook site.yml --check --diff
```

```yaml
# Forcer l'execution d'une tache meme en check mode
- name: Collecter des informations
  command: cat /etc/os-release
  check_mode: no
  register: os_info
  changed_when: false

# Empecher l'execution d'une tache en mode normal
- name: Operation dangereuse (uniquement en check)
  command: rm -rf /tmp/old_data
  check_mode: yes
```

### Tags

Les **tags** permettent d'executer selectivement certaines parties d'un playbook.

```yaml
---
- name: Configuration complete
  hosts: webservers
  become: yes
  tasks:
    - name: Installer les packages
      apt:
        name:
          - nginx
          - curl
        state: present
      tags:
        - install
        - packages

    - name: Copier la configuration
      copy:
        src: nginx.conf
        dest: /etc/nginx/nginx.conf
      tags:
        - config

    - name: Deployer l'application
      copy:
        src: app/
        dest: /var/www/app/
      tags:
        - deploy
```

```bash
# Executer seulement les taches avec le tag "install"
ansible-playbook site.yml --tags install

# Executer plusieurs tags
ansible-playbook site.yml --tags "install,config"

# Tout executer sauf un tag
ansible-playbook site.yml --skip-tags deploy

# Lister les tags disponibles
ansible-playbook site.yml --list-tags

# Lister les taches pour un tag
ansible-playbook site.yml --tags install --list-tasks
```

**Tags speciaux :**

```yaml
# always : s'execute toujours, meme avec --tags
- name: Verifier les prerequis
  command: which python3
  tags: always

# never : ne s'execute jamais, sauf si appele explicitement
- name: Nettoyage dangereux
  file:
    path: /var/data/old
    state: absent
  tags: never
```

---

## TP : Deployer un service web avec un Playbook

### Objectifs

- Creer un playbook Ansible complet et fonctionnel
- Deployer un serveur web (Nginx ou Apache) avec une page HTML personnalisee
- Utiliser les handlers pour gerer le redemarrage du service
- Valider le deploiement et verifier l'accessibilite du site

### Prerequis

- Un ou plusieurs managed nodes accessibles via SSH
- Ansible installe sur le control node
- Un fichier d'inventaire fonctionnel

### Etape 1 : Preparer la structure du projet

Creer l'arborescence du projet :

```bash
mkdir -p tp-webserver/files
cd tp-webserver
```

Creer le fichier d'inventaire :

```ini
# inventory.ini
[webservers]
web1 ansible_host=192.168.56.10 ansible_user=vagrant
```

### Etape 2 : Creer la page HTML

Creer le fichier `files/index.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TP Ansible - Deploiement Web</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f0f4f8;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2d3748; }
        p { color: #718096; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Deploiement reussi !</h1>
        <p>Cette page a ete deployee avec Ansible.</p>
        <p>Serveur : {{ ansible_hostname }}</p>
    </div>
</body>
</html>
```

### Etape 3 : Ecrire le playbook

Creer le fichier `deploy-webserver.yml` :

```yaml
---
# deploy-webserver.yml
- name: Deployer un serveur web avec une page personnalisee
  hosts: webservers
  become: yes
  vars:
    site_name: tp-ansible
    document_root: /var/www/{{ site_name }}
    http_port: 80

  tasks:
    # --- Installation ---
    - name: Mettre a jour le cache APT
      apt:
        update_cache: yes
        cache_valid_time: 3600
      tags: install

    - name: Installer Nginx
      apt:
        name: nginx
        state: present
      tags: install

    # --- Configuration ---
    - name: Creer le repertoire du site
      file:
        path: "{{ document_root }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
      tags: config

    - name: Deployer la page HTML
      template:
        src: files/index.html
        dest: "{{ document_root }}/index.html"
        owner: www-data
        group: www-data
        mode: '0644'
      tags:
        - config
        - deploy

    - name: Deployer la configuration du virtual host
      copy:
        content: |
          server {
              listen {{ http_port }};
              server_name {{ site_name }};
              root {{ document_root }};
              index index.html;

              location / {
                  try_files $uri $uri/ =404;
              }

              access_log /var/log/nginx/{{ site_name }}_access.log;
              error_log /var/log/nginx/{{ site_name }}_error.log;
          }
        dest: /etc/nginx/sites-available/{{ site_name }}
        owner: root
        group: root
        mode: '0644'
      notify: Redemarrer Nginx
      tags: config

    - name: Activer le site (lien symbolique)
      file:
        src: /etc/nginx/sites-available/{{ site_name }}
        dest: /etc/nginx/sites-enabled/{{ site_name }}
        state: link
      notify: Redemarrer Nginx
      tags: config

    - name: Supprimer le site par defaut
      file:
        path: /etc/nginx/sites-enabled/default
        state: absent
      notify: Redemarrer Nginx
      tags: config

    # --- Service ---
    - name: Demarrer et activer Nginx
      service:
        name: nginx
        state: started
        enabled: yes
      tags: service

    # --- Verification ---
    - name: Forcer l'execution des handlers
      meta: flush_handlers
      tags: verify

    - name: Verifier que Nginx repond sur le port {{ http_port }}
      uri:
        url: "http://localhost:{{ http_port }}"
        status_code: 200
      register: resultat_verification
      tags: verify

    - name: Afficher le resultat de la verification
      debug:
        msg: "Le serveur web est accessible et repond avec le code {{ resultat_verification.status }}"
      tags: verify

  handlers:
    - name: Redemarrer Nginx
      service:
        name: nginx
        state: restarted
```

### Etape 4 : Executer le playbook

```bash
# Verifier la syntaxe
ansible-playbook deploy-webserver.yml -i inventory.ini --syntax-check

# Simuler l'execution (dry-run)
ansible-playbook deploy-webserver.yml -i inventory.ini --check --diff

# Executer le playbook
ansible-playbook deploy-webserver.yml -i inventory.ini

# Executer seulement l'installation
ansible-playbook deploy-webserver.yml -i inventory.ini --tags install

# Executer seulement la verification
ansible-playbook deploy-webserver.yml -i inventory.ini --tags verify
```

### Etape 5 : Verifier le deploiement

```bash
# Depuis le control node, verifier l'acces au site
curl http://192.168.56.10

# Verifier l'idempotence (deuxieme execution)
ansible-playbook deploy-webserver.yml -i inventory.ini
# Resultat attendu : changed=0
```

### Livrables

1. **Playbook fonctionnel** (`deploy-webserver.yml`) qui deploie Nginx avec une page HTML personnalisee
2. **Page web accessible** depuis le navigateur ou via `curl`
3. **Execution idempotente** : la deuxieme execution ne produit aucun changement

### Criteres de validation

| Critere | Description |
|---------|-------------|
| Syntaxe valide | `--syntax-check` passe sans erreur |
| Installation | Nginx est installe sur le(s) managed node(s) |
| Configuration | Le virtual host est correctement configure |
| Page HTML | La page personnalisee est accessible via le navigateur |
| Handlers | Le handler de redemarrage fonctionne (uniquement si changement) |
| Idempotence | La deuxieme execution affiche `changed=0` |
| Tags | Le playbook peut etre execute par sections avec `--tags` |

---

## Prochaines etapes

Maintenant que vous maitrisez les bases des playbooks, passez au module suivant :

**[04-Playbooks-Complexes](../04-Playbooks-Complexes/README.md)**

Vous allez apprendre a :
- Utiliser les conditions (`when`)
- Creer des boucles (`loop`, `with_items`)
- Gerer les variables et leur precedence
- Organiser les taches avec les blocks et l'error handling

---

**"Un playbook est la recette de votre infrastructure. Rendez-le clair, idempotent et reutilisable."**
