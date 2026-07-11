# Creation de Playbooks Complexes

**Jour 2 - Apres-midi (~3h30)**

## Table des matieres

1. [Conditions](#conditions)
2. [Boucles](#boucles)
3. [Variables](#variables)
4. [Organisation des taches](#organisation-des-taches)
5. [TP : Configurer un environnement multi-services](#tp--configurer-un-environnement-multi-services)

---

## Conditions

Les conditions permettent d'executer des taches de maniere selective en fonction de l'etat du systeme, de variables ou de resultats precedents.

### La directive `when`

La directive `when` accepte une expression Jinja2 (sans les doubles accolades `{{ }}`).

```yaml
---
- name: Playbook avec conditions
  hosts: all
  become: yes
  tasks:
    # Condition sur le systeme d'exploitation
    - name: Installer Nginx sur Debian/Ubuntu
      apt:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"

    - name: Installer Nginx sur RedHat/CentOS
      yum:
        name: nginx
        state: present
      when: ansible_os_family == "RedHat"
```

### Tester les variables

**Variable definie ou non :**

```yaml
# Verifier qu'une variable est definie
- name: Configurer le port si defini
  debug:
    msg: "Le port est {{ http_port }}"
  when: http_port is defined

# Verifier qu'une variable n'est PAS definie
- name: Utiliser le port par defaut
  debug:
    msg: "Aucun port specifie, utilisation du port 80"
  when: http_port is not defined
```

**Valeurs true/false :**

```yaml
vars:
  ssl_enabled: true
  debug_mode: false

tasks:
  # Tester un booleen
  - name: Configurer SSL
    debug:
      msg: "SSL active"
    when: ssl_enabled

  # Tester false (deux syntaxes)
  - name: Desactiver le mode debug
    debug:
      msg: "Debug desactive"
    when: not debug_mode
```

**Tester le contenu d'une chaine :**

```yaml
- name: Verifier la version d'Ubuntu
  debug:
    msg: "Ubuntu 22.04 detecte"
  when: ansible_distribution == "Ubuntu" and ansible_distribution_version == "22.04"

- name: Verifier si l'hote est un serveur de production
  debug:
    msg: "Serveur de production"
  when: "'prod' in inventory_hostname"
```

### Combiner les conditions

**Operateur `and` :**

```yaml
# Les deux conditions doivent etre vraies
- name: Installer sur Ubuntu 22.04 uniquement
  apt:
    name: nginx
    state: present
  when:
    - ansible_distribution == "Ubuntu"
    - ansible_distribution_version == "22.04"
  # Equivalent a : when: ansible_distribution == "Ubuntu" and ansible_distribution_version == "22.04"
```

Lorsque `when` recoit une liste, les conditions sont combinees avec `and`.

**Operateur `or` :**

```yaml
# Au moins une condition doit etre vraie
- name: Installer sur Debian ou Ubuntu
  apt:
    name: nginx
    state: present
  when: ansible_distribution == "Debian" or ansible_distribution == "Ubuntu"
```

**Combinaisons complexes :**

```yaml
- name: Deployer uniquement en production sur Ubuntu
  template:
    src: app.conf.j2
    dest: /etc/app/config.conf
  when:
    - environment == "production"
    - ansible_distribution == "Ubuntu" or ansible_distribution == "Debian"
    - http_port is defined
```

### Conditions avec des variables registered

```yaml
- name: Verifier si le fichier de configuration existe
  stat:
    path: /etc/app/config.yml
  register: config_file

- name: Creer la configuration si absente
  template:
    src: config.yml.j2
    dest: /etc/app/config.yml
  when: not config_file.stat.exists

- name: Verifier l'etat du service
  command: systemctl is-active nginx
  register: nginx_status
  changed_when: false
  failed_when: false

- name: Demarrer Nginx s'il n'est pas actif
  service:
    name: nginx
    state: started
  when: nginx_status.rc != 0
```

### Imports conditionnels

```yaml
# Importer des taches selon l'OS
- name: Importer les taches specifiques Debian
  include_tasks: debian.yml
  when: ansible_os_family == "Debian"

- name: Importer les taches specifiques RedHat
  include_tasks: redhat.yml
  when: ansible_os_family == "RedHat"
```

---

## Boucles

Les boucles permettent de repeter une tache pour plusieurs elements sans dupliquer le code.

### La directive `loop`

```yaml
- name: Creer plusieurs utilisateurs
  user:
    name: "{{ item }}"
    state: present
    shell: /bin/bash
  loop:
    - alice
    - bob
    - charlie
```

La variable speciale `{{ item }}` contient l'element courant de la boucle.

### `with_items` (syntaxe historique)

```yaml
# Equivalent a loop, syntaxe plus ancienne
- name: Installer plusieurs packages
  apt:
    name: "{{ item }}"
    state: present
  with_items:
    - nginx
    - curl
    - vim
    - git

# Note : pour installer plusieurs packages, il est plus efficace de passer une liste directement
- name: Installer plusieurs packages (optimise)
  apt:
    name:
      - nginx
      - curl
      - vim
      - git
    state: present
```

### Boucles sur des dictionnaires

**`loop` avec des dictionnaires :**

```yaml
- name: Creer des utilisateurs avec details
  user:
    name: "{{ item.nom }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groupes }}"
    shell: "{{ item.shell }}"
    state: present
  loop:
    - { nom: alice, uid: 1001, groupes: "sudo,docker", shell: "/bin/bash" }
    - { nom: bob, uid: 1002, groupes: "docker", shell: "/bin/bash" }
    - { nom: charlie, uid: 1003, groupes: "developers", shell: "/bin/zsh" }
```

**`with_dict` :**

```yaml
vars:
  applications:
    web:
      port: 80
      user: www-data
    api:
      port: 8080
      user: api-user
    worker:
      port: 9000
      user: worker-user

tasks:
  - name: Afficher la configuration de chaque application
    debug:
      msg: "App {{ item.key }} : port={{ item.value.port }}, user={{ item.value.user }}"
    with_dict: "{{ applications }}"
```

### `with_fileglob`

Parcourir des fichiers correspondant a un pattern :

```yaml
- name: Copier tous les fichiers de configuration
  copy:
    src: "{{ item }}"
    dest: /etc/app/conf.d/
    owner: root
    group: root
    mode: '0644'
  with_fileglob:
    - "files/config/*.conf"

- name: Deployer tous les scripts
  copy:
    src: "{{ item }}"
    dest: /usr/local/bin/
    mode: '0755'
  with_fileglob:
    - "files/scripts/*.sh"
```

### Controle des boucles

**`label` : personnaliser l'affichage :**

```yaml
- name: Creer des utilisateurs
  user:
    name: "{{ item.nom }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groupes }}"
  loop:
    - { nom: alice, uid: 1001, groupes: "sudo", mot_de_passe: "secret123" }
    - { nom: bob, uid: 1002, groupes: "docker", mot_de_passe: "secret456" }
  loop_control:
    label: "{{ item.nom }}"    # Affiche seulement le nom, pas le mot de passe
```

**`pause` : introduire un delai entre les iterations :**

```yaml
- name: Redemarrer les services un par un
  service:
    name: "{{ item }}"
    state: restarted
  loop:
    - nginx
    - php-fpm
    - redis
  loop_control:
    pause: 5    # Attendre 5 secondes entre chaque iteration
```

**`index_var` : acceder a l'index de la boucle :**

```yaml
- name: Creer des fichiers numerotes
  copy:
    content: "Fichier numero {{ idx }}"
    dest: "/tmp/fichier_{{ idx }}.txt"
  loop:
    - premier
    - deuxieme
    - troisieme
  loop_control:
    index_var: idx    # idx vaut 0, 1, 2
```

### Boucles avec conditions

```yaml
- name: Installer les packages optionnels
  apt:
    name: "{{ item.nom }}"
    state: present
  loop:
    - { nom: nginx, requis: true }
    - { nom: nodejs, requis: false }
    - { nom: curl, requis: true }
    - { nom: docker, requis: false }
  when: item.requis
```

### Boucles avec `register`

```yaml
- name: Verifier l'etat de plusieurs services
  command: systemctl is-active {{ item }}
  register: resultats_services
  changed_when: false
  failed_when: false
  loop:
    - nginx
    - mysql
    - redis

- name: Afficher l'etat de chaque service
  debug:
    msg: "{{ item.item }} est {{ 'actif' if item.rc == 0 else 'inactif' }}"
  loop: "{{ resultats_services.results }}"
```

---

## Variables

Les variables rendent les playbooks dynamiques et reutilisables. Comprendre les differents types et leur precedence est essentiel pour ecrire des playbooks maintenables.

### Types de variables

**1. Variables de playbook (`vars`) :**

```yaml
- name: Playbook avec variables
  hosts: webservers
  vars:
    http_port: 80
    app_name: monapp
    packages:
      - nginx
      - curl
  tasks:
    - name: Afficher la configuration
      debug:
        msg: "Application {{ app_name }} sur le port {{ http_port }}"
```

**2. Variables d'inventaire :**

```ini
# inventory.ini
[webservers]
web1 ansible_host=192.168.1.10 http_port=80
web2 ansible_host=192.168.1.11 http_port=8080

[webservers:vars]
app_name=monapp
environment=production
```

**3. Variables en ligne de commande (extra vars) :**

```bash
# Passer des variables via -e ou --extra-vars
ansible-playbook site.yml -e "app_version=2.0.0"
ansible-playbook site.yml -e "environment=staging http_port=8080"
ansible-playbook site.yml -e "@vars/production.yml"   # Depuis un fichier
```

Les extra vars ont la **plus haute priorite** et ecrasent toutes les autres.

**4. Variables registered :**

```yaml
- name: Capturer la sortie d'une commande
  command: cat /etc/hostname
  register: hostname_result
  changed_when: false

- name: Utiliser le resultat
  debug:
    msg: "Le hostname est {{ hostname_result.stdout }}"
```

**5. Facts (variables automatiques) :**

```yaml
- name: Utiliser les facts systeme
  debug:
    msg: |
      OS : {{ ansible_distribution }} {{ ansible_distribution_version }}
      IP : {{ ansible_default_ipv4.address }}
      CPU : {{ ansible_processor_vcpus }} vCPUs
      RAM : {{ ansible_memtotal_mb }} Mo
```

### Precedence des variables (apercu)

Ansible applique les variables selon un ordre de priorite strict. De la plus basse a la plus haute :

```
1.  Role defaults (defaults/main.yml)
2.  Inventory group_vars/all
3.  Inventory group_vars/*
4.  Inventory host_vars/*
5.  Play vars
6.  Play vars_files
7.  Role vars (vars/main.yml)
8.  Block vars
9.  Task vars
10. set_facts / registered vars
11. Extra vars (-e)                   <-- Plus haute priorite
```

**Regle pratique a retenir :**

```
Defaults < Inventory < Playbook < Extra Vars
   |          |           |           |
 Faible                           Haute
priorite                        priorite
```

### `set_fact`

Definir des variables dynamiquement pendant l'execution :

```yaml
- name: Collecter des informations
  command: cat /opt/app/VERSION
  register: version_result
  changed_when: false

- name: Definir la version comme fact
  set_fact:
    app_version: "{{ version_result.stdout }}"
    is_recent: "{{ version_result.stdout is version('2.0', '>=') }}"

- name: Utiliser les facts definis
  debug:
    msg: "Version {{ app_version }} - Recente : {{ is_recent }}"
```

### Valeurs par defaut

Utiliser le filtre `default` pour fournir une valeur de repli :

```yaml
- name: Configurer avec valeur par defaut
  debug:
    msg: "Port : {{ http_port | default(80) }}"

- name: Utiliser une variable optionnelle
  template:
    src: config.j2
    dest: /etc/app/config.yml
  vars:
    log_level: "{{ custom_log_level | default('info') }}"
    workers: "{{ custom_workers | default(ansible_processor_vcpus) }}"
```

### `group_vars` et `host_vars`

Organisation recommandee pour centraliser les variables :

```
projet/
  inventory/
    hosts.yml
    group_vars/
      all.yml              # Variables pour tous les hotes
      webservers.yml       # Variables pour le groupe webservers
      databases.yml        # Variables pour le groupe databases
      databases/
        vault.yml          # Secrets chiffres (Ansible Vault)
    host_vars/
      web1.yml             # Variables specifiques a web1
      db1.yml              # Variables specifiques a db1
```

**group_vars/all.yml :**

```yaml
---
# Variables globales
ansible_user: ubuntu
ansible_python_interpreter: /usr/bin/python3

common_packages:
  - vim
  - curl
  - htop
  - git

ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
```

**group_vars/webservers.yml :**

```yaml
---
nginx_port: 80
nginx_worker_processes: auto
app_user: www-data
log_level: info
```

**host_vars/web1.yml :**

```yaml
---
# Configuration specifique a web1
nginx_worker_processes: 4
custom_vhosts:
  - server_name: app1.example.com
    port: 80
  - server_name: app2.example.com
    port: 8080
```

---

## Organisation des taches

### Blocks

Les **blocks** permettent de regrouper des taches et de leur appliquer des directives communes (`when`, `become`, `tags`).

```yaml
tasks:
  - name: Configuration Nginx
    block:
      - name: Installer Nginx
        apt:
          name: nginx
          state: present

      - name: Copier la configuration
        copy:
          src: nginx.conf
          dest: /etc/nginx/nginx.conf

      - name: Demarrer Nginx
        service:
          name: nginx
          state: started
    when: ansible_os_family == "Debian"
    become: yes
    tags: nginx
```

### Gestion des erreurs avec `block/rescue/always`

Ce mecanisme est l'equivalent d'un try/catch/finally dans les langages de programmation.

```yaml
tasks:
  - name: Deployer l'application avec rollback
    block:
      - name: Arreter l'application
        service:
          name: monapp
          state: stopped

      - name: Deployer la nouvelle version
        copy:
          src: app-v2.tar.gz
          dest: /opt/monapp/

      - name: Extraire l'archive
        unarchive:
          src: /opt/monapp/app-v2.tar.gz
          dest: /opt/monapp/
          remote_src: yes

      - name: Demarrer l'application
        service:
          name: monapp
          state: started

      - name: Verifier la sante de l'application
        uri:
          url: http://localhost:8080/health
          status_code: 200
        retries: 5
        delay: 10

    rescue:
      - name: Echec du deploiement - Rollback
        debug:
          msg: "Le deploiement a echoue, retour a la version precedente"

      - name: Restaurer la sauvegarde
        copy:
          src: /opt/monapp/backup/
          dest: /opt/monapp/
          remote_src: yes

      - name: Redemarrer l'ancienne version
        service:
          name: monapp
          state: restarted

    always:
      - name: Nettoyer les fichiers temporaires
        file:
          path: /opt/monapp/app-v2.tar.gz
          state: absent

      - name: Envoyer une notification
        debug:
          msg: "Deploiement termine (succes ou rollback)"
```

**Points importants :**

- `block` : contient les taches principales
- `rescue` : s'execute **uniquement si** une tache du block echoue
- `always` : s'execute **toujours**, que le block ait reussi ou echoue

### `include_tasks` vs `import_tasks`

Les deux directives permettent de decouper un playbook en fichiers, mais avec des differences importantes.

**`import_tasks` (statique) :**

```yaml
# Les taches sont importees au moment du parsing (avant execution)
- name: Configurer les serveurs web
  hosts: webservers
  tasks:
    - import_tasks: tasks/install.yml
    - import_tasks: tasks/configure.yml
    - import_tasks: tasks/deploy.yml
```

- Les tags, `when` et autres directives sont herites par chaque tache importee
- Les variables sont resolues au moment du parsing
- Ne peut pas etre utilise dans une boucle

**`include_tasks` (dynamique) :**

```yaml
# Les taches sont incluses au moment de l'execution
- name: Configurer selon l'OS
  hosts: all
  tasks:
    - include_tasks: "tasks/{{ ansible_os_family | lower }}.yml"

    - include_tasks: tasks/optional.yml
      when: feature_enabled
```

- Les taches sont incluses au moment de l'execution (dynamique)
- Peut utiliser des variables dans le nom du fichier
- Peut etre utilise dans une boucle
- Les tags ne sont pas automatiquement herites

**Quand utiliser quoi ?**

| Critere | `import_tasks` | `include_tasks` |
|---------|---------------|-----------------|
| Moment de resolution | Parsing (avant execution) | Execution |
| Nom de fichier dynamique | Non | Oui |
| Utilisable dans une boucle | Non | Oui |
| Heritage des tags | Oui | Non (sauf `apply`) |
| Performance | Meilleure | Legerement moindre |

### Strategies d'organisation

**Organisation par fonction :**

```
tasks/
  install.yml        # Installation des packages
  configure.yml      # Configuration des services
  deploy.yml         # Deploiement de l'application
  verify.yml         # Verification post-deploiement
```

**Organisation par OS :**

```
tasks/
  debian.yml         # Taches specifiques Debian/Ubuntu
  redhat.yml         # Taches specifiques RedHat/CentOS
  common.yml         # Taches communes a tous les OS
```

**Exemple complet :**

```yaml
---
# site.yml
- name: Configurer les serveurs
  hosts: all
  become: yes
  tasks:
    - name: Taches communes
      import_tasks: tasks/common.yml
      tags: common

    - name: Taches specifiques a l'OS
      include_tasks: "tasks/{{ ansible_os_family | lower }}.yml"
      tags: os-specific

    - name: Installation
      import_tasks: tasks/install.yml
      tags: install

    - name: Configuration
      import_tasks: tasks/configure.yml
      tags: config

    - name: Deploiement
      import_tasks: tasks/deploy.yml
      tags: deploy
```

**tasks/common.yml :**

```yaml
---
- name: Installer les packages communs
  package:
    name: "{{ common_packages }}"
    state: present

- name: Configurer le fuseau horaire
  timezone:
    name: Europe/Paris

- name: Configurer NTP
  template:
    src: ntp.conf.j2
    dest: /etc/ntp.conf
  notify: Redemarrer NTP
```

---

## TP : Configurer un environnement multi-services

### Objectifs

- Developper un playbook complexe utilisant conditions, boucles, variables et blocks
- Configurer un environnement complet avec serveur web, base de donnees et application
- Mettre en pratique la gestion d'erreurs avec `block/rescue/always`
- Organiser les taches de maniere maintenable

### Prerequis

- Avoir suivi le module "Introduction aux Playbooks"
- Un ou plusieurs managed nodes accessibles via SSH
- Fichier d'inventaire fonctionnel

### Etape 1 : Structure du projet

Creer l'arborescence du projet :

```bash
mkdir -p tp-multiservices/{tasks,files,templates,group_vars,host_vars}
cd tp-multiservices
```

### Etape 2 : Definir les variables

**group_vars/all.yml :**

```yaml
---
# Configuration globale
environment_name: development
timezone: Europe/Paris

# Utilisateurs a creer
app_users:
  - nom: webadmin
    uid: 2001
    groupes: "sudo,www-data"
    shell: /bin/bash
  - nom: dbadmin
    uid: 2002
    groupes: "sudo"
    shell: /bin/bash
  - nom: deployer
    uid: 2003
    groupes: "www-data"
    shell: /bin/bash

# Packages communs a tous les serveurs
common_packages:
  - vim
  - curl
  - htop
  - git
  - unzip
  - wget

# Configuration web
web_server: nginx
web_port: 80
web_root: /var/www/app

# Configuration base de donnees
db_server: mysql
db_port: 3306
db_name: myapp_db
db_user: app_user
db_password: "ChangeMe123!"

# Configuration application
app_name: monapp
app_version: "1.0.0"
app_port: 8080
```

### Etape 3 : Creer les fichiers de taches

**tasks/users.yml :**

```yaml
---
# Creer les utilisateurs avec une boucle
- name: Creer les utilisateurs de l'application
  user:
    name: "{{ item.nom }}"
    uid: "{{ item.uid }}"
    groups: "{{ item.groupes }}"
    shell: "{{ item.shell }}"
    create_home: yes
    state: present
  loop: "{{ app_users }}"
  loop_control:
    label: "{{ item.nom }}"

- name: Configurer les cles SSH pour les utilisateurs
  authorized_key:
    user: "{{ item.nom }}"
    state: present
    key: "{{ lookup('file', 'files/ssh_keys/' + item.nom + '.pub') }}"
  loop: "{{ app_users }}"
  loop_control:
    label: "{{ item.nom }}"
  when: lookup('file', 'files/ssh_keys/' + item.nom + '.pub', errors='ignore') is not none
  ignore_errors: yes
```

**tasks/common.yml :**

```yaml
---
- name: Mettre a jour le cache des packages
  apt:
    update_cache: yes
    cache_valid_time: 3600
  when: ansible_os_family == "Debian"

- name: Mettre a jour le cache YUM
  yum:
    update_cache: yes
  when: ansible_os_family == "RedHat"

- name: Installer les packages communs (Debian)
  apt:
    name: "{{ common_packages }}"
    state: present
  when: ansible_os_family == "Debian"

- name: Installer les packages communs (RedHat)
  yum:
    name: "{{ common_packages }}"
    state: present
  when: ansible_os_family == "RedHat"

- name: Configurer le fuseau horaire
  timezone:
    name: "{{ timezone }}"
```

**tasks/webserver.yml :**

```yaml
---
# Installation et configuration du serveur web
- name: Installation du serveur web
  block:
    - name: Installer {{ web_server }}
      apt:
        name: "{{ web_server }}"
        state: present
      when: ansible_os_family == "Debian"

    - name: Creer le repertoire racine du site
      file:
        path: "{{ web_root }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'

    - name: Deployer la configuration du virtual host
      copy:
        content: |
          server {
              listen {{ web_port }};
              server_name {{ app_name }}.local;
              root {{ web_root }};
              index index.html;

              location / {
                  try_files $uri $uri/ =404;
              }

              location /api {
                  proxy_pass http://127.0.0.1:{{ app_port }};
                  proxy_set_header Host $host;
                  proxy_set_header X-Real-IP $remote_addr;
              }

              access_log /var/log/nginx/{{ app_name }}_access.log;
              error_log /var/log/nginx/{{ app_name }}_error.log;
          }
        dest: /etc/nginx/sites-available/{{ app_name }}
        owner: root
        group: root
        mode: '0644'
      notify: Redemarrer Nginx

    - name: Activer le site
      file:
        src: /etc/nginx/sites-available/{{ app_name }}
        dest: /etc/nginx/sites-enabled/{{ app_name }}
        state: link
      notify: Redemarrer Nginx

    - name: Desactiver le site par defaut
      file:
        path: /etc/nginx/sites-enabled/default
        state: absent
      notify: Redemarrer Nginx

    - name: Deployer la page d'accueil
      copy:
        content: |
          <!DOCTYPE html>
          <html lang="fr">
          <head>
              <meta charset="UTF-8">
              <title>{{ app_name }} - {{ environment_name }}</title>
          </head>
          <body>
              <h1>{{ app_name }} v{{ app_version }}</h1>
              <p>Environnement : {{ environment_name }}</p>
              <p>Serveur : {{ inventory_hostname }}</p>
          </body>
          </html>
        dest: "{{ web_root }}/index.html"
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Demarrer et activer {{ web_server }}
      service:
        name: "{{ web_server }}"
        state: started
        enabled: yes

  rescue:
    - name: Echec de la configuration web
      debug:
        msg: "La configuration du serveur web a echoue. Verification necessaire."

    - name: Collecter les logs d'erreur
      command: journalctl -u {{ web_server }} --no-pager -n 20
      register: web_logs
      changed_when: false
      failed_when: false

    - name: Afficher les logs
      debug:
        msg: "{{ web_logs.stdout_lines }}"
      when: web_logs.stdout_lines is defined

  tags: webserver
```

**tasks/database.yml :**

```yaml
---
# Installation et configuration de la base de donnees
- name: Configuration de la base de donnees
  block:
    - name: Installer les packages MySQL
      apt:
        name:
          - mysql-server
          - mysql-client
          - python3-pymysql
        state: present
      when: ansible_os_family == "Debian"

    - name: Demarrer et activer MySQL
      service:
        name: mysql
        state: started
        enabled: yes

    - name: Creer la base de donnees
      mysql_db:
        name: "{{ db_name }}"
        state: present
        login_unix_socket: /var/run/mysqld/mysqld.sock
      become: yes

    - name: Creer l'utilisateur de la base de donnees
      mysql_user:
        name: "{{ db_user }}"
        password: "{{ db_password }}"
        priv: "{{ db_name }}.*:ALL"
        host: "localhost"
        state: present
        login_unix_socket: /var/run/mysqld/mysqld.sock
      become: yes

  rescue:
    - name: Echec de la configuration de la base de donnees
      debug:
        msg: "La configuration MySQL a echoue. Verification necessaire."

    - name: Collecter les logs MySQL
      command: journalctl -u mysql --no-pager -n 20
      register: db_logs
      changed_when: false
      failed_when: false

    - name: Afficher les logs
      debug:
        msg: "{{ db_logs.stdout_lines }}"
      when: db_logs.stdout_lines is defined

  always:
    - name: Verifier l'etat de MySQL
      command: systemctl is-active mysql
      register: mysql_status
      changed_when: false
      failed_when: false

    - name: Afficher l'etat de MySQL
      debug:
        msg: "MySQL est {{ 'actif' if mysql_status.rc == 0 else 'inactif' }}"

  tags: database
```

**tasks/verify.yml :**

```yaml
---
# Verification post-deploiement
- name: Verifier l'etat de tous les services
  command: systemctl is-active {{ item }}
  register: resultats_services
  changed_when: false
  failed_when: false
  loop:
    - "{{ web_server }}"
    - mysql

- name: Afficher l'etat des services
  debug:
    msg: "{{ item.item }} : {{ 'ACTIF' if item.rc == 0 else 'INACTIF' }}"
  loop: "{{ resultats_services.results }}"
  loop_control:
    label: "{{ item.item }}"

- name: Verifier l'acces au serveur web
  uri:
    url: "http://localhost:{{ web_port }}"
    status_code: 200
  register: web_check
  ignore_errors: yes

- name: Resultat de la verification web
  debug:
    msg: "Serveur web : {{ 'ACCESSIBLE' if web_check.status == 200 else 'INACCESSIBLE' }}"
  when: web_check is defined

- name: Resume du deploiement
  debug:
    msg: |
      === Resume du deploiement ===
      Application : {{ app_name }} v{{ app_version }}
      Environnement : {{ environment_name }}
      Serveur web : {{ web_server }} sur le port {{ web_port }}
      Base de donnees : {{ db_server }} sur le port {{ db_port }}
      Repertoire web : {{ web_root }}
```

### Etape 4 : Assembler le playbook principal

**site.yml :**

```yaml
---
# site.yml - Playbook multi-services
- name: Configurer un environnement multi-services
  hosts: all
  become: yes
  vars_files:
    - group_vars/all.yml

  tasks:
    # --- Taches communes ---
    - name: Charger les taches communes
      import_tasks: tasks/common.yml
      tags: common

    # --- Gestion des utilisateurs ---
    - name: Creer les utilisateurs
      import_tasks: tasks/users.yml
      tags: users

    # --- Serveur web ---
    - name: Configurer le serveur web
      import_tasks: tasks/webserver.yml
      tags: webserver

    # --- Base de donnees ---
    - name: Configurer la base de donnees
      import_tasks: tasks/database.yml
      tags: database

    # --- Verification ---
    - name: Verifier le deploiement
      import_tasks: tasks/verify.yml
      tags: verify

  handlers:
    - name: Redemarrer Nginx
      service:
        name: nginx
        state: restarted

    - name: Redemarrer MySQL
      service:
        name: mysql
        state: restarted
```

### Etape 5 : Executer le playbook

```bash
# Verifier la syntaxe
ansible-playbook site.yml -i inventory.ini --syntax-check

# Simuler l'execution complete
ansible-playbook site.yml -i inventory.ini --check --diff

# Executer l'ensemble du playbook
ansible-playbook site.yml -i inventory.ini

# Executer uniquement la partie web
ansible-playbook site.yml -i inventory.ini --tags webserver

# Executer uniquement la base de donnees
ansible-playbook site.yml -i inventory.ini --tags database

# Executer avec des variables surchargees
ansible-playbook site.yml -i inventory.ini -e "environment_name=production app_version=2.0.0"

# Executer la verification uniquement
ansible-playbook site.yml -i inventory.ini --tags verify
```

### Livrables

1. **Playbook multi-services fonctionnel** (`site.yml`) avec fichiers de taches separes
2. **Variables centralisees** dans `group_vars/all.yml`
3. **Gestion d'erreurs** avec `block/rescue/always` sur les services critiques
4. **Conditions** pour gerer les differences d'OS
5. **Boucles** pour la creation d'utilisateurs et l'installation de packages
6. **Tags** pour permettre l'execution partielle

### Criteres de validation

| Critere | Description |
|---------|-------------|
| Structure | Le projet est organise en fichiers separes (tasks/, group_vars/) |
| Variables | Les variables sont centralisees et utilisees correctement |
| Conditions | Le playbook gere au moins deux familles d'OS (Debian, RedHat) |
| Boucles | Au moins une boucle est utilisee (utilisateurs ou packages) |
| Blocks | `block/rescue/always` est utilise pour la gestion d'erreurs |
| Handlers | Les handlers gerent le redemarrage des services |
| Tags | Le playbook peut etre execute par sections avec `--tags` |
| Idempotence | La deuxieme execution affiche `changed=0` |
| Verification | Les taches de verification confirment que les services sont actifs |

---

## Prochaines etapes

Vous maitrisez maintenant la creation de playbooks complexes. Les prochains modules aborderont :

- **Les roles** : structurer et reutiliser du code Ansible
- **Les templates Jinja2** : generer des fichiers de configuration dynamiques
- **Ansible Vault** : gerer les secrets de maniere securisee
- **Les inventaires dynamiques** : gerer des infrastructures cloud

---

**"La complexite d'un playbook doit etre dans la logique metier, pas dans la structure du code. Organisez, decoupez, reutilisez."**
