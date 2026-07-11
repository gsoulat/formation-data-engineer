# Introduction aux Roles Ansible

> Jour 3 - Matin partie 1 (~2h)

## Table des matieres

1. [Structure des roles](#structure-des-roles)
2. [Deploiement et utilisation des roles](#deploiement-et-utilisation-des-roles)
3. [TP : Creer un role Ansible pour une application specifique](#tp--creer-un-role-ansible-pour-une-application-specifique)

---

## Structure des roles

### Qu'est-ce qu'un role ?

Un **role** Ansible est une structure organisee de fichiers qui regroupe des taches, des variables, des templates et des handlers dans un format standardise et reutilisable. Les roles permettent de decomposer une configuration complexe en unites logiques independantes.

### Arborescence d'un role

Chaque role suit une convention de repertoires stricte :

```
roles/
└── mon_role/
    ├── tasks/           # Taches principales du role
    │   └── main.yml     # Point d'entree automatique
    ├── handlers/        # Handlers (actions declenchees par notify)
    │   └── main.yml
    ├── templates/       # Templates Jinja2 (.j2)
    │   └── config.conf.j2
    ├── files/           # Fichiers statiques a copier tels quels
    │   └── index.html
    ├── vars/            # Variables du role (haute priorite)
    │   └── main.yml
    ├── defaults/        # Variables par defaut (basse priorite)
    │   └── main.yml
    ├── meta/            # Metadonnees et dependances
    │   └── main.yml
    ├── tests/           # Playbooks et inventaires de test
    │   ├── inventory
    │   └── test.yml
    └── README.md        # Documentation du role
```

### La convention main.yml

Ansible charge automatiquement le fichier `main.yml` dans chaque sous-repertoire du role. C'est le **point d'entree** par defaut. Il n'est pas necessaire de specifier le chemin complet dans le playbook : Ansible sait ou chercher.

```yaml
# roles/nginx/tasks/main.yml
---
# Ce fichier est charge automatiquement quand le role est appele
- name: Installer Nginx
  ansible.builtin.apt:
    name: nginx
    state: present

- name: Demarrer le service
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: yes
```

Il est possible de decouper les taches en plusieurs fichiers et de les inclure depuis `main.yml` :

```yaml
# roles/nginx/tasks/main.yml
---
- name: Inclure les taches d'installation
  ansible.builtin.include_tasks: install.yml

- name: Inclure les taches de configuration
  ansible.builtin.include_tasks: configure.yml

- name: Inclure les taches de service
  ansible.builtin.include_tasks: service.yml
```

### defaults/ vs vars/ : comprendre la priorite

La distinction entre `defaults/` et `vars/` est fondamentale pour bien concevoir un role.

**defaults/main.yml** -- Priorite basse :
- Contient les valeurs par defaut du role
- Facilement ecrasees par l'utilisateur du role
- Servent de "valeurs raisonnables" si rien n'est specifie

```yaml
# roles/nginx/defaults/main.yml
---
nginx_port: 80
nginx_server_name: localhost
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_user: www-data
nginx_group: www-data
nginx_web_root: /var/www/html
```

**vars/main.yml** -- Priorite haute :
- Contient les variables internes au role
- Difficilement ecrasees (il faut utiliser `-e` en ligne de commande)
- Reservees aux valeurs qui ne doivent pas etre modifiees par l'utilisateur

```yaml
# roles/nginx/vars/main.yml
---
nginx_config_path: /etc/nginx
nginx_log_path: /var/log/nginx
nginx_pid_path: /run/nginx.pid
nginx_package_name: nginx
```

**Regle generale :** tout ce que l'utilisateur du role peut vouloir personnaliser va dans `defaults/`. Tout ce qui est interne et fixe va dans `vars/`.

### Description des autres repertoires

**handlers/main.yml** -- Actions conditionnelles declenchees par `notify` :

```yaml
# roles/nginx/handlers/main.yml
---
- name: Recharger Nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded

- name: Redemarrer Nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

**templates/** -- Fichiers Jinja2 dynamiques :

```jinja
{# roles/nginx/templates/nginx.conf.j2 #}
user {{ nginx_user }};
worker_processes {{ nginx_worker_processes }};
pid {{ nginx_pid_path }};

events {
    worker_connections {{ nginx_worker_connections }};
}

http {
    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log {{ nginx_log_path }}/access.log;
    error_log {{ nginx_log_path }}/error.log;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

**files/** -- Fichiers statiques copies tels quels (pas de templating) :

```yaml
- name: Copier la page d'accueil par defaut
  ansible.builtin.copy:
    src: index.html        # Cherche dans files/index.html
    dest: /var/www/html/index.html
```

**meta/main.yml** -- Metadonnees et dependances :

```yaml
# roles/nginx/meta/main.yml
---
galaxy_info:
  author: votre_nom
  description: Installation et configuration de Nginx
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: Debian
      versions:
        - bullseye
        - bookworm
  galaxy_tags:
    - nginx
    - web
    - webserver

dependencies: []
```

---

## Deploiement et utilisation des roles

### Creer un role avec ansible-galaxy init

La commande `ansible-galaxy init` genere automatiquement l'arborescence complete d'un role :

```bash
# Creer un role dans le repertoire courant
ansible-galaxy init nginx

# Creer un role dans un repertoire specifique
ansible-galaxy init roles/nginx

# Resultat :
# nginx/
# ├── README.md
# ├── defaults/
# │   └── main.yml
# ├── files/
# ├── handlers/
# │   └── main.yml
# ├── meta/
# │   └── main.yml
# ├── tasks/
# │   └── main.yml
# ├── templates/
# ├── tests/
# │   ├── inventory
# │   └── test.yml
# └── vars/
#     └── main.yml
```

Il est aussi possible de creer la structure manuellement :

```bash
mkdir -p roles/nginx/{tasks,handlers,templates,files,vars,defaults,meta,tests}
touch roles/nginx/{tasks,handlers,vars,defaults,meta}/main.yml
touch roles/nginx/README.md
```

### Utiliser un role dans un playbook

La maniere la plus simple est d'utiliser la directive `roles:` dans un play :

```yaml
# site.yml
---
- name: Configurer les serveurs web
  hosts: webservers
  become: yes
  roles:
    - nginx
```

Avec des variables personnalisees :

```yaml
---
- name: Configurer les serveurs web
  hosts: webservers
  become: yes
  roles:
    - role: nginx
      vars:
        nginx_port: 8080
        nginx_server_name: mon-site.fr
```

Avec des tags et des conditions :

```yaml
---
- name: Configurer l'infrastructure
  hosts: all
  become: yes

  pre_tasks:
    - name: Mettre a jour le cache apt
      ansible.builtin.apt:
        update_cache: yes

  roles:
    - common

    - role: nginx
      tags: web

    - role: mysql
      tags: database
      when: "'dbservers' in group_names"

  post_tasks:
    - name: Verifier que les services sont actifs
      ansible.builtin.service:
        name: "{{ item }}"
        state: started
      loop:
        - nginx
```

### include_role vs import_role

Ansible propose deux facons d'appeler un role depuis la section `tasks:` :

**import_role -- Importation statique :**

```yaml
tasks:
  - name: Importer le role nginx
    ansible.builtin.import_role:
      name: nginx
    vars:
      nginx_port: 8080
    tags: web
```

- Le role est charge **au moment de la lecture du playbook** (parsing)
- Les tags sont herites par toutes les taches du role
- Les conditions `when` s'appliquent a chaque tache individuellement
- Plus performant mais moins flexible

**include_role -- Inclusion dynamique :**

```yaml
tasks:
  - name: Inclure le role nginx si necessaire
    ansible.builtin.include_role:
      name: nginx
    vars:
      nginx_port: 8080
    when: deployer_nginx | bool
```

- Le role est charge **au moment de l'execution**
- Les tags ne sont pas herites
- La condition `when` s'applique a l'inclusion elle-meme
- Plus flexible mais un peu plus lent

**Tableau comparatif :**

| Critere | import_role | include_role |
|---------|-------------|--------------|
| Moment du chargement | A la lecture (parsing) | A l'execution |
| Tags | Herites par les taches | Non herites |
| Condition when | Appliquee a chaque tache | Appliquee a l'inclusion |
| Variables dynamiques | Non | Oui |
| Cas d'usage | Role toujours execute | Role conditionnel |

### Dependances de roles

Un role peut declarer des dependances vers d'autres roles dans `meta/main.yml`. Ces dependances sont executees automatiquement avant le role principal.

```yaml
# roles/webapp/meta/main.yml
---
dependencies:
  - role: common

  - role: nginx
    vars:
      nginx_port: 80

  - role: mysql
    vars:
      mysql_root_password: "{{ vault_mysql_password }}"
```

**Ordre d'execution** pour un playbook qui appelle le role `webapp` :

```
1. common    (dependance de webapp)
2. nginx     (dependance de webapp)
3. mysql     (dependance de webapp)
4. webapp    (role principal)
```

Par defaut, si plusieurs roles declarent la meme dependance, celle-ci n'est executee qu'une seule fois. Pour forcer la re-execution :

```yaml
# meta/main.yml
dependencies:
  - role: common
    allow_duplicates: yes
```

### Installer des roles depuis Ansible Galaxy

```bash
# Rechercher un role
ansible-galaxy search nginx

# Installer un role depuis Galaxy
ansible-galaxy install geerlingguy.nginx

# Installer une version specifique
ansible-galaxy install geerlingguy.nginx,4.1.0

# Installer depuis un fichier requirements.yml
ansible-galaxy install -r requirements.yml
```

**requirements.yml :**

```yaml
---
roles:
  - name: geerlingguy.nginx
    version: "4.1.0"
  - name: geerlingguy.mysql
    version: "4.0.0"
  - src: https://github.com/user/ansible-role-custom.git
    name: custom
    version: main
```

```bash
# Installer toutes les dependances
ansible-galaxy install -r requirements.yml

# Forcer la reinstallation
ansible-galaxy install -r requirements.yml --force

# Lister les roles installes
ansible-galaxy list

# Supprimer un role
ansible-galaxy remove geerlingguy.nginx
```

---

## TP : Creer un role Ansible pour une application specifique

### Objectifs

- Creer un role Ansible complet pour deployer et configurer Nginx
- Maitriser la structure standard d'un role (tasks, handlers, templates, defaults, meta)
- Produire un role fonctionnel, reutilisable et parametrable

### Prerequis

- Ansible installe sur la machine de controle
- Un ou plusieurs hotes cibles accessibles en SSH (ou un environnement Vagrant/Docker)
- Connaissances de base sur les playbooks Ansible

### Etape 1 : Initialiser la structure du role

```bash
# Creer le repertoire du projet
mkdir -p ansible-tp-roles/roles
cd ansible-tp-roles

# Initialiser le role nginx
ansible-galaxy init roles/nginx_custom

# Verifier la structure creee
tree roles/nginx_custom/
```

Resultat attendu :

```
roles/nginx_custom/
├── README.md
├── defaults/
│   └── main.yml
├── files/
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
├── templates/
├── tests/
│   ├── inventory
│   └── test.yml
└── vars/
    └── main.yml
```

### Etape 2 : Definir les variables par defaut

Editer `roles/nginx_custom/defaults/main.yml` :

```yaml
---
# Port d'ecoute HTTP
nginx_port: 80

# Nom du serveur
nginx_server_name: localhost

# Racine du site web
nginx_web_root: /var/www/html

# Parametres de performance
nginx_worker_processes: auto
nginx_worker_connections: 1024

# Utilisateur systeme
nginx_user: www-data
nginx_group: www-data

# Activer SSL (par defaut non)
nginx_ssl_enabled: false
nginx_ssl_port: 443

# Page d'index personnalisee
nginx_index_content: "<h1>Bienvenue sur {{ nginx_server_name }}</h1>"
```

### Etape 3 : Definir les variables internes

Editer `roles/nginx_custom/vars/main.yml` :

```yaml
---
# Variables internes au role (ne pas modifier)
nginx_config_path: /etc/nginx
nginx_sites_available: /etc/nginx/sites-available
nginx_sites_enabled: /etc/nginx/sites-enabled
nginx_log_path: /var/log/nginx
nginx_pid_path: /run/nginx.pid
```

### Etape 4 : Ecrire les taches

Editer `roles/nginx_custom/tasks/main.yml` :

```yaml
---
- name: Installer Nginx
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: yes
  tags: install

- name: Creer le repertoire racine du site
  ansible.builtin.file:
    path: "{{ nginx_web_root }}"
    state: directory
    owner: "{{ nginx_user }}"
    group: "{{ nginx_group }}"
    mode: "0755"
  tags: config

- name: Deployer la configuration principale Nginx
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: "{{ nginx_config_path }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
    validate: "nginx -t -c %s"
  notify: Recharger Nginx
  tags: config

- name: Deployer la configuration du virtual host
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "{{ nginx_sites_available }}/{{ nginx_server_name }}.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Recharger Nginx
  tags: config

- name: Activer le virtual host
  ansible.builtin.file:
    src: "{{ nginx_sites_available }}/{{ nginx_server_name }}.conf"
    dest: "{{ nginx_sites_enabled }}/{{ nginx_server_name }}.conf"
    state: link
  notify: Recharger Nginx
  tags: config

- name: Supprimer la configuration par defaut
  ansible.builtin.file:
    path: "{{ nginx_sites_enabled }}/default"
    state: absent
  notify: Recharger Nginx
  tags: config

- name: Deployer la page d'index
  ansible.builtin.copy:
    content: |
      <!DOCTYPE html>
      <html>
      <head><title>{{ nginx_server_name }}</title></head>
      <body>
        {{ nginx_index_content }}
      </body>
      </html>
    dest: "{{ nginx_web_root }}/index.html"
    owner: "{{ nginx_user }}"
    group: "{{ nginx_group }}"
    mode: "0644"
  tags: config

- name: Demarrer et activer Nginx
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: yes
  tags: service
```

### Etape 5 : Creer les templates

**roles/nginx_custom/templates/nginx.conf.j2 :**

```jinja
user {{ nginx_user }};
worker_processes {{ nginx_worker_processes }};
pid {{ nginx_pid_path }};

events {
    worker_connections {{ nginx_worker_connections }};
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include {{ nginx_config_path }}/mime.types;
    default_type application/octet-stream;

    access_log {{ nginx_log_path }}/access.log;
    error_log {{ nginx_log_path }}/error.log;

    gzip on;
    gzip_vary on;
    gzip_min_length 256;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    include {{ nginx_config_path }}/conf.d/*.conf;
    include {{ nginx_sites_enabled }}/*;
}
```

**roles/nginx_custom/templates/vhost.conf.j2 :**

```jinja
server {
    listen {{ nginx_port }};
    server_name {{ nginx_server_name }};

    root {{ nginx_web_root }};
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }

{% if nginx_ssl_enabled %}
    listen {{ nginx_ssl_port }} ssl;
    ssl_certificate /etc/ssl/certs/{{ nginx_server_name }}.crt;
    ssl_certificate_key /etc/ssl/private/{{ nginx_server_name }}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
{% endif %}

    access_log {{ nginx_log_path }}/{{ nginx_server_name }}.access.log;
    error_log {{ nginx_log_path }}/{{ nginx_server_name }}.error.log;
}
```

### Etape 6 : Definir les handlers

Editer `roles/nginx_custom/handlers/main.yml` :

```yaml
---
- name: Recharger Nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded

- name: Redemarrer Nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

### Etape 7 : Configurer les metadonnees

Editer `roles/nginx_custom/meta/main.yml` :

```yaml
---
galaxy_info:
  author: votre_nom
  description: Role pour installer et configurer Nginx avec virtual host personnalise
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: Debian
      versions:
        - bullseye
        - bookworm
  galaxy_tags:
    - nginx
    - web
    - webserver

dependencies: []
```

### Etape 8 : Creer le playbook principal

Creer le fichier `site.yml` a la racine du projet :

```yaml
# site.yml
---
- name: Deployer Nginx avec le role personnalise
  hosts: webservers
  become: yes

  roles:
    - role: nginx_custom
      vars:
        nginx_port: 8080
        nginx_server_name: mon-application.local
        nginx_index_content: "<h1>Application deployee avec Ansible</h1><p>Role nginx_custom operationnel.</p>"
```

Creer un inventaire de test `inventory.ini` :

```ini
[webservers]
web1 ansible_host=192.168.56.10
web2 ansible_host=192.168.56.11

[webservers:vars]
ansible_user=vagrant
ansible_ssh_private_key_file=~/.vagrant.d/insecure_private_key
```

### Etape 9 : Tester le role

```bash
# Verifier la syntaxe
ansible-playbook -i inventory.ini site.yml --syntax-check

# Lancer en mode dry-run
ansible-playbook -i inventory.ini site.yml --check --diff

# Executer le role
ansible-playbook -i inventory.ini site.yml

# Verifier le resultat
curl http://192.168.56.10:8080
```

### Livrables

- Un role `nginx_custom` complet avec tous les sous-repertoires remplis
- Un fichier `site.yml` qui utilise le role avec des variables personnalisees
- Un inventaire de test fonctionnel
- Le service Nginx actif et accessible sur le port configure

### Criteres de validation

| Critere | Attendu |
|---------|---------|
| Structure du role | Tous les repertoires standard presents (tasks, handlers, templates, files, vars, defaults, meta) |
| Variables par defaut | Valeurs raisonnables dans defaults/main.yml, personnalisables par l'utilisateur |
| Templates | nginx.conf.j2 et vhost.conf.j2 fonctionnels avec variables Jinja2 |
| Handlers | Reload et restart definis et correctement notifies |
| Idempotence | Executer le playbook deux fois ne produit pas de changement a la seconde execution |
| Fonctionnalite | Nginx repond sur le port configure avec le contenu attendu |
| Reutilisabilite | Le role peut etre appele avec des variables differentes pour deployer plusieurs sites |

---

## Ressources

- [Documentation officielle -- Roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Bonnes pratiques de structure de projet](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)

---

**Suite du cours :** [06-Ansible-Vault](../06-Ansible-Vault/README.md)
