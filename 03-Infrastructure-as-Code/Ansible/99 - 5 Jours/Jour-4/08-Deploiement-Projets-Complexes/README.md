# Deploiement de Projets Complexes

> Jour 4 - Matin partie 1 (~2h)

## Table des matieres

1. [Bonnes pratiques pour structurer des projets Ansible](#bonnes-pratiques-pour-structurer-des-projets-ansible)
2. [Deploiement d'un projet complexe avec plusieurs hotes et services](#deploiement-dun-projet-complexe-avec-plusieurs-hotes-et-services)
3. [TP : Realiser un projet de bout en bout avec Ansible](#tp--realiser-un-projet-de-bout-en-bout-avec-ansible)

---

## Bonnes pratiques pour structurer des projets Ansible

### Structure de repertoires recommandee

Un projet Ansible bien organise suit une convention de nommage et une arborescence qui facilitent la maintenance, la collaboration et le passage d'un environnement a l'autre.

```
projet-ansible/
├── ansible.cfg                     # Configuration globale du projet
├── requirements.yml                # Dependances Galaxy (roles, collections)
├── .ansible-lint                   # Configuration du linter
├── README.md                       # Documentation du projet
│
├── inventories/
│   ├── production/
│   │   ├── hosts.yml               # Inventaire production
│   │   ├── group_vars/
│   │   │   ├── all/
│   │   │   │   ├── vars.yml        # Variables communes (non sensibles)
│   │   │   │   └── vault.yml       # Secrets chiffres (Ansible Vault)
│   │   │   ├── webservers.yml
│   │   │   ├── databases.yml
│   │   │   └── loadbalancers.yml
│   │   └── host_vars/
│   │       ├── web01.yml
│   │       └── db01.yml
│   │
│   ├── staging/
│   │   ├── hosts.yml
│   │   ├── group_vars/
│   │   │   └── all/
│   │   │       ├── vars.yml
│   │   │       └── vault.yml
│   │   └── host_vars/
│   │
│   └── development/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
│
├── playbooks/
│   ├── site.yml                    # Playbook principal (orchestre tout)
│   ├── webservers.yml              # Playbook par couche
│   ├── databases.yml
│   ├── loadbalancers.yml
│   ├── deploy.yml                  # Deploiement applicatif
│   └── maintenance/
│       ├── backup.yml
│       ├── update.yml
│       └── rollback.yml
│
├── roles/
│   ├── common/                     # Role de base pour tous les serveurs
│   ├── nginx/
│   ├── haproxy/
│   ├── mysql/
│   ├── app/
│   └── monitoring/
│
├── files/                          # Fichiers statiques globaux
│   └── ssl/
│
├── templates/                      # Templates globaux
│   └── motd.j2
│
├── filter_plugins/                 # Plugins de filtres personnalises
├── library/                        # Modules personnalises
│
└── scripts/                        # Scripts utilitaires
    ├── deploy.sh
    └── vault-pass.sh
```

### Conventions de nommage

```yaml
# Nommage des roles : minuscules, tirets pour separer
roles/
  common/
  nginx-proxy/
  mysql-server/

# Nommage des variables : prefixe par le role
# Role nginx :
nginx_port: 80
nginx_worker_processes: auto
nginx_log_path: /var/log/nginx

# Role mysql :
mysql_port: 3306
mysql_root_password: "{{ vault_mysql_root_password }}"
mysql_max_connections: 500

# Nommage des tasks : verbe d'action en anglais, descriptif
- name: Install nginx package
- name: Configure nginx virtual host
- name: Ensure nginx service is running
```

### Separation des responsabilites

Chaque role ne doit gerer qu'un seul service ou une seule responsabilite :

```yaml
# site.yml - Le playbook principal orchestre les roles
---
- name: Configurer tous les serveurs
  hosts: all
  roles:
    - common

- name: Configurer les serveurs de base de donnees
  hosts: databases
  roles:
    - mysql

- name: Configurer les serveurs web
  hosts: webservers
  roles:
    - nginx
    - app

- name: Configurer le load balancer
  hosts: loadbalancers
  roles:
    - haproxy
```

### Gestion des environnements

La gestion multi-environnement repose sur la separation des inventaires. Les playbooks et roles restent identiques, seules les variables changent.

```bash
# Deployer en staging
ansible-playbook -i inventories/staging/hosts.yml playbooks/site.yml

# Deployer en production
ansible-playbook -i inventories/production/hosts.yml playbooks/site.yml

# Deployer en production avec Vault
ansible-playbook -i inventories/production/hosts.yml playbooks/site.yml --vault-password-file .vault_pass
```

**Variables par environnement :**

```yaml
# inventories/staging/group_vars/all/vars.yml
---
environment: staging
app_debug: true
app_log_level: debug
app_replicas: 1
mysql_max_connections: 100

# inventories/production/group_vars/all/vars.yml
---
environment: production
app_debug: false
app_log_level: warn
app_replicas: 3
mysql_max_connections: 500
```

### ansible.cfg optimise pour un projet

```ini
[defaults]
inventory = inventories/production/hosts.yml
roles_path = ./roles:~/.ansible/roles
collections_paths = ./collections:~/.ansible/collections

# Performance
forks = 20
gathering = smart
fact_caching = jsonfile
fact_caching_connection = .ansible_cache
fact_caching_timeout = 86400

# Sortie
stdout_callback = yaml
callbacks_enabled = profile_tasks, timer

# Logs
log_path = ./ansible.log

[privilege_escalation]
become = True
become_method = sudo

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=3600s
```

---

## Deploiement d'un projet complexe avec plusieurs hotes et services

### Strategies de deploiement multi-tier

Lorsqu'on deploie une infrastructure a plusieurs couches (load balancer, serveurs web, base de donnees), l'ordre des operations et la gestion de la parallelisation sont essentiels.

### Le mot-cle `serial`

Le mot-cle `serial` controle combien de serveurs sont traites simultanement. C'est la base des **rolling updates** (mises a jour progressives).

```yaml
---
# Mise a jour progressive : 1 serveur a la fois
- name: Rolling update des serveurs web
  hosts: webservers
  serial: 1
  become: yes

  tasks:
    - name: Retirer le serveur du load balancer
      haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy/admin.sock
        backend: http_back
      delegate_to: "{{ groups['loadbalancers'][0] }}"

    - name: Deployer la nouvelle version
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_dir }}"
        version: "{{ app_version }}"

    - name: Redemarrer le service applicatif
      systemd:
        name: "{{ app_service }}"
        state: restarted

    - name: Attendre que le service soit pret
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
      retries: 10
      delay: 5

    - name: Remettre le serveur dans le load balancer
      haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        socket: /var/run/haproxy/admin.sock
        backend: http_back
      delegate_to: "{{ groups['loadbalancers'][0] }}"
```

On peut aussi utiliser `serial` avec un pourcentage ou une liste progressive :

```yaml
# Deployer d'abord 1 serveur (canary), puis 50%, puis le reste
- hosts: webservers
  serial:
    - 1
    - "50%"
    - "100%"
  tasks:
    - name: Deployer l'application
      include_role:
        name: app
```

### Delegation avec `delegate_to`

La delegation permet d'executer une tache sur un hote different de celui en cours de traitement :

```yaml
- name: Creer un enregistrement DNS pour le serveur
  community.general.nsupdate:
    server: "{{ dns_server }}"
    zone: "example.com"
    record: "{{ inventory_hostname }}"
    type: A
    value: "{{ ansible_default_ipv4.address }}"
  delegate_to: localhost

- name: Verifier la replication MySQL depuis le slave
  mysql_replication:
    mode: getreplica
    login_user: root
    login_password: "{{ mysql_root_password }}"
  delegate_to: "{{ groups['database_slave'][0] }}"
  register: slave_status
```

### Execution unique avec `run_once`

`run_once` garantit qu'une tache n'est executee qu'une seule fois, quel que soit le nombre de serveurs dans le groupe :

```yaml
- name: Executer les migrations de base de donnees
  command: "{{ app_dir }}/manage.py migrate"
  run_once: true

- name: Notifier l'equipe du deploiement
  uri:
    url: "{{ slack_webhook }}"
    method: POST
    body_format: json
    body:
      text: "Deploiement v{{ app_version }} en cours sur {{ environment }}"
  run_once: true
  delegate_to: localhost
```

### Taches asynchrones

Pour les taches longues, les operations asynchrones permettent de ne pas bloquer l'execution :

```yaml
- name: Lancer un backup complet de la base de donnees
  command: mysqldump --all-databases > /backup/full_backup.sql
  async: 3600       # Timeout de 1 heure
  poll: 0           # Ne pas attendre (fire and forget)
  register: backup_job

- name: Continuer avec d'autres taches...
  debug:
    msg: "Le backup tourne en arriere-plan"

- name: Verifier que le backup est termine
  async_status:
    jid: "{{ backup_job.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 60
  delay: 30
```

### Utilisation de plusieurs inventaires

On peut combiner plusieurs inventaires pour des deploiements cross-environnement :

```bash
# Utiliser plusieurs inventaires simultanement
ansible-playbook playbooks/site.yml \
  -i inventories/production/hosts.yml \
  -i inventories/monitoring/hosts.yml

# Limiter a un sous-ensemble de serveurs
ansible-playbook playbooks/site.yml \
  -i inventories/production/hosts.yml \
  --limit webservers

# Limiter a un seul serveur (test avant deploiement complet)
ansible-playbook playbooks/site.yml \
  -i inventories/production/hosts.yml \
  --limit web01
```

### Gestion des erreurs dans un deploiement multi-tier

```yaml
---
- name: Deploiement complet de l'infrastructure
  hosts: all
  any_errors_fatal: true    # Arreter tout si un serveur echoue
  max_fail_percentage: 0    # Aucune marge d'erreur

  pre_tasks:
    - name: Verifier la connectivite
      ping:

  tasks:
    - name: Appliquer le role common
      include_role:
        name: common

  post_tasks:
    - name: Verifier l'etat du serveur
      uri:
        url: "http://{{ inventory_hostname }}:{{ health_port }}/health"
        status_code: 200
      ignore_errors: no
```

---

## TP : Realiser un projet de bout en bout avec Ansible

### Objectifs

- Structurer un projet Ansible complet selon les bonnes pratiques
- Deployer une infrastructure multi-tier avec web, base de donnees et load balancer
- Utiliser les roles, variables par environnement, templates Jinja2 et Vault
- Mettre en oeuvre un rolling update

### Architecture cible

```
                    ┌──────────────────────────────┐
                    │     Load Balancer (HAProxy)   │
                    │     lb01 - 192.168.56.10      │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
            ┌───────▼────────┐            ┌───────▼────────┐
            │  Web Server 1  │            │  Web Server 2  │
            │  Nginx + App   │            │  Nginx + App   │
            │  192.168.56.11 │            │  192.168.56.12 │
            └───────┬────────┘            └───────┬────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │     Base de donnees (MySQL)   │
                    │     db01 - 192.168.56.20      │
                    └──────────────────────────────┘
```

### Etape 1 : Initialiser la structure du projet (15 min)

Creer l'arborescence complete du projet :

```bash
mkdir -p projet-deploiement/{inventories/{production,staging}/{group_vars/all,host_vars},playbooks/maintenance,roles,files,templates,scripts}
cd projet-deploiement
touch ansible.cfg requirements.yml .ansible-lint
```

Creer le fichier `ansible.cfg` :

```ini
[defaults]
inventory = inventories/production/hosts.yml
roles_path = ./roles
forks = 10
gathering = smart
fact_caching = jsonfile
fact_caching_connection = .ansible_cache
fact_caching_timeout = 86400
stdout_callback = yaml
callbacks_enabled = profile_tasks, timer
log_path = ./ansible.log

[privilege_escalation]
become = True
become_method = sudo

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=3600s
```

### Etape 2 : Creer les inventaires (15 min)

**`inventories/production/hosts.yml`** :

```yaml
---
all:
  children:
    loadbalancers:
      hosts:
        lb01:
          ansible_host: 192.168.56.10
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.56.11
        web02:
          ansible_host: 192.168.56.12
    databases:
      hosts:
        db01:
          ansible_host: 192.168.56.20
```

**`inventories/staging/hosts.yml`** :

```yaml
---
all:
  children:
    loadbalancers:
      hosts:
        lb-staging:
          ansible_host: 192.168.57.10
    webservers:
      hosts:
        web-staging:
          ansible_host: 192.168.57.11
    databases:
      hosts:
        db-staging:
          ansible_host: 192.168.57.20
```

### Etape 3 : Configurer les variables (20 min)

**`inventories/production/group_vars/all/vars.yml`** :

```yaml
---
environment: production
app_name: monapp
app_version: "1.0.0"
app_port: 8080
app_user: www-data
app_dir: "/var/www/{{ app_name }}"

# Base de donnees
db_host: 192.168.56.20
db_port: 3306
db_name: "{{ app_name }}_db"
db_user: "{{ app_name }}_user"
db_password: "{{ vault_db_password }}"

# Load balancer
haproxy_frontend_port: 80
haproxy_stats_port: 8404
haproxy_stats_user: admin
haproxy_stats_password: "{{ vault_haproxy_stats_password }}"
```

**Creer le fichier Vault :**

```bash
ansible-vault create inventories/production/group_vars/all/vault.yml
```

**Contenu du fichier Vault :**

```yaml
---
vault_db_password: "Pr0duct1on_S3cur3_P@ss"
vault_db_root_password: "R00t_Pr0d_P@ssw0rd!"
vault_haproxy_stats_password: "St@ts_S3cur3"
```

### Etape 4 : Creer les roles (45 min)

**Role `common` :**

```bash
ansible-galaxy init roles/common
```

**`roles/common/tasks/main.yml`** :

```yaml
---
- name: Mettre a jour le cache apt
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Installer les paquets de base
  apt:
    name:
      - vim
      - curl
      - wget
      - htop
      - git
      - ufw
      - unzip
    state: present

- name: Configurer le timezone
  timezone:
    name: Europe/Paris

- name: Configurer le firewall - autoriser SSH
  ufw:
    rule: allow
    port: "22"
    proto: tcp

- name: Activer le firewall
  ufw:
    state: enabled
    policy: deny
```

**Role `mysql` :**

```bash
ansible-galaxy init roles/mysql
```

**`roles/mysql/tasks/main.yml`** :

```yaml
---
- name: Installer MySQL et les dependances Python
  apt:
    name:
      - mysql-server
      - python3-pymysql
    state: present

- name: Demarrer et activer MySQL
  systemd:
    name: mysql
    state: started
    enabled: yes

- name: Definir le mot de passe root MySQL
  mysql_user:
    name: root
    password: "{{ vault_db_root_password }}"
    login_unix_socket: /var/run/mysqld/mysqld.sock
    check_implicit_admin: yes

- name: Creer la base de donnees applicative
  mysql_db:
    name: "{{ db_name }}"
    encoding: utf8mb4
    collation: utf8mb4_unicode_ci
    login_user: root
    login_password: "{{ vault_db_root_password }}"
    state: present

- name: Creer l'utilisateur applicatif
  mysql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
    priv: "{{ db_name }}.*:ALL"
    host: "192.168.56.%"
    login_user: root
    login_password: "{{ vault_db_root_password }}"
    state: present

- name: Deployer la configuration MySQL
  template:
    src: my.cnf.j2
    dest: /etc/mysql/mysql.conf.d/custom.cnf
  notify: Redemarrer MySQL

- name: Ouvrir le port MySQL dans le firewall
  ufw:
    rule: allow
    port: "{{ db_port }}"
    proto: tcp
    src: 192.168.56.0/24
```

**`roles/mysql/templates/my.cnf.j2`** :

```jinja
# {{ ansible_managed }}

[mysqld]
bind-address = 0.0.0.0
port = {{ db_port }}
max_connections = {{ mysql_max_connections | default(200) }}

{% if ansible_memtotal_mb > 4096 %}
innodb_buffer_pool_size = {{ (ansible_memtotal_mb * 0.5) | int }}M
{% else %}
innodb_buffer_pool_size = {{ (ansible_memtotal_mb * 0.3) | int }}M
{% endif %}

slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

**`roles/mysql/handlers/main.yml`** :

```yaml
---
- name: Redemarrer MySQL
  systemd:
    name: mysql
    state: restarted
```

**Role `nginx` :**

```bash
ansible-galaxy init roles/nginx
```

**`roles/nginx/tasks/main.yml`** :

```yaml
---
- name: Installer Nginx
  apt:
    name: nginx
    state: present

- name: Creer le repertoire de l'application
  file:
    path: "{{ app_dir }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    mode: "0755"

- name: Deployer la page d'accueil de l'application
  template:
    src: index.html.j2
    dest: "{{ app_dir }}/index.html"
    owner: "{{ app_user }}"
    group: "{{ app_user }}"

- name: Deployer la configuration du virtual host Nginx
  template:
    src: vhost.conf.j2
    dest: "/etc/nginx/sites-available/{{ app_name }}"
    validate: "nginx -t -c /dev/null || true"
  notify: Recharger Nginx

- name: Activer le virtual host
  file:
    src: "/etc/nginx/sites-available/{{ app_name }}"
    dest: "/etc/nginx/sites-enabled/{{ app_name }}"
    state: link
  notify: Recharger Nginx

- name: Supprimer le site par defaut
  file:
    path: /etc/nginx/sites-enabled/default
    state: absent
  notify: Recharger Nginx

- name: Demarrer et activer Nginx
  systemd:
    name: nginx
    state: started
    enabled: yes

- name: Ouvrir le port HTTP dans le firewall
  ufw:
    rule: allow
    port: "80"
    proto: tcp
```

**`roles/nginx/templates/vhost.conf.j2`** :

```jinja
# {{ ansible_managed }}

server {
    listen 80;
    server_name {{ inventory_hostname }};
    root {{ app_dir }};
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /health {
        access_log off;
        return 200 '{"status": "ok", "server": "{{ inventory_hostname }}"}';
        add_header Content-Type application/json;
    }

    access_log /var/log/nginx/{{ app_name }}_access.log;
    error_log /var/log/nginx/{{ app_name }}_error.log;
}
```

**`roles/nginx/templates/index.html.j2`** :

```html
<!DOCTYPE html>
<html>
<head><title>{{ app_name }} - {{ environment }}</title></head>
<body>
    <h1>{{ app_name }} v{{ app_version }}</h1>
    <p>Serveur : {{ inventory_hostname }}</p>
    <p>Environnement : {{ environment }}</p>
</body>
</html>
```

**`roles/nginx/handlers/main.yml`** :

```yaml
---
- name: Recharger Nginx
  systemd:
    name: nginx
    state: reloaded
```

**Role `haproxy` :**

```bash
ansible-galaxy init roles/haproxy
```

**`roles/haproxy/tasks/main.yml`** :

```yaml
---
- name: Installer HAProxy
  apt:
    name: haproxy
    state: present

- name: Deployer la configuration HAProxy
  template:
    src: haproxy.cfg.j2
    dest: /etc/haproxy/haproxy.cfg
    validate: "haproxy -c -f %s"
  notify: Redemarrer HAProxy

- name: Demarrer et activer HAProxy
  systemd:
    name: haproxy
    state: started
    enabled: yes

- name: Ouvrir les ports dans le firewall
  ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - "{{ haproxy_frontend_port }}"
    - "{{ haproxy_stats_port }}"
```

**`roles/haproxy/templates/haproxy.cfg.j2`** :

```jinja
# {{ ansible_managed }}

global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend http_front
    bind *:{{ haproxy_frontend_port }}
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
{% for host in groups['webservers'] %}
    server {{ host }} {{ hostvars[host]['ansible_host'] }}:80 check inter 2000 rise 2 fall 3
{% endfor %}

listen stats
    bind *:{{ haproxy_stats_port }}
    stats enable
    stats uri /stats
    stats refresh 30s
{% if haproxy_stats_user is defined %}
    stats auth {{ haproxy_stats_user }}:{{ haproxy_stats_password }}
{% endif %}
```

**`roles/haproxy/handlers/main.yml`** :

```yaml
---
- name: Redemarrer HAProxy
  systemd:
    name: haproxy
    state: restarted
```

### Etape 5 : Creer le playbook principal (15 min)

**`playbooks/site.yml`** :

```yaml
---
- name: Appliquer la configuration commune a tous les serveurs
  hosts: all
  roles:
    - common

- name: Configurer le serveur de base de donnees
  hosts: databases
  roles:
    - mysql

- name: Configurer les serveurs web
  hosts: webservers
  roles:
    - nginx

- name: Configurer le load balancer
  hosts: loadbalancers
  roles:
    - haproxy
```

**`playbooks/maintenance/rolling-update.yml`** :

```yaml
---
- name: Rolling update des serveurs web
  hosts: webservers
  serial: 1
  become: yes

  tasks:
    - name: Deployer la nouvelle version de l'application
      template:
        src: "../../roles/nginx/templates/index.html.j2"
        dest: "{{ app_dir }}/index.html"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"

    - name: Recharger Nginx
      systemd:
        name: nginx
        state: reloaded

    - name: Verifier que le serveur repond
      uri:
        url: "http://localhost/health"
        status_code: 200
      retries: 5
      delay: 3
```

### Etape 6 : Deployer et valider (30 min)

```bash
# 1. Verifier la syntaxe
ansible-playbook playbooks/site.yml --syntax-check

# 2. Dry-run (mode check)
ansible-playbook playbooks/site.yml --check --diff

# 3. Deployer d'abord sur un seul serveur
ansible-playbook playbooks/site.yml --limit web01

# 4. Deployer l'ensemble
ansible-playbook playbooks/site.yml --vault-password-file .vault_pass

# 5. Verifier le deploiement
curl http://192.168.56.10              # Via le load balancer
curl http://192.168.56.11/health       # Health check web01
curl http://192.168.56.12/health       # Health check web02
curl http://192.168.56.10:8404/stats   # Page stats HAProxy

# 6. Tester le rolling update
ansible-playbook playbooks/maintenance/rolling-update.yml
```

### Livrables

- Projet structure selon les bonnes pratiques (inventaires, roles, playbooks separes)
- 4 roles fonctionnels : common, mysql, nginx, haproxy
- Inventaires production et staging avec variables separees
- Secrets chiffres avec Ansible Vault
- Playbook de rolling update
- Infrastructure deployee et accessible via le load balancer

### Criteres de validation

| Critere | Points |
|---------|--------|
| Structure du projet conforme aux bonnes pratiques | 20% |
| Roles correctement implementes et idempotents | 25% |
| Variables externalisees et secrets dans Vault | 15% |
| Templates Jinja2 fonctionnels | 15% |
| Deploiement complet operationnel (LB + Web + DB) | 15% |
| Rolling update fonctionnel | 10% |

---

**Retour au sommaire Jour 4 :** [../README.md](../README.md)
