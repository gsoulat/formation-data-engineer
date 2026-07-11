# Optimisation et Depannage des Playbooks

> Jour 4 - Matin partie 2 (~1h30)

## Table des matieres

1. [Detection et resolution des erreurs courantes](#detection-et-resolution-des-erreurs-courantes)
2. [Optimisation des performances](#optimisation-des-performances)
3. [Filtres et templates Jinja2](#filtres-et-templates-jinja2)
4. [Bonnes pratiques](#bonnes-pratiques)
5. [TP : Resoudre des erreurs simulees dans des playbooks existants](#tp--resoudre-des-erreurs-simulees-dans-des-playbooks-existants)

---

## Detection et resolution des erreurs courantes

### Mode verbose

Ansible propose plusieurs niveaux de verbosite pour faciliter le diagnostic :

```bash
# Niveau 1 : informations de base sur les taches
ansible-playbook site.yml -v

# Niveau 2 : parametres des modules et resultats
ansible-playbook site.yml -vv

# Niveau 3 : debug complet (connexions, fichiers temporaires)
ansible-playbook site.yml -vvv

# Niveau 4 : debug SSH complet (utile pour les problemes de connexion)
ansible-playbook site.yml -vvvv
```

### Erreurs courantes et leur resolution

**Erreur SSH - Connexion refusee :**

```
fatal: [web01]: UNREACHABLE! => {"msg": "Failed to connect to the host via ssh: ssh: connect to host 192.168.1.11 port 22: Connection refused"}
```

Solutions :
- Verifier que le serveur est accessible : `ping 192.168.1.11`
- Verifier que SSH est actif : `ssh user@192.168.1.11`
- Verifier la cle SSH : `ssh-copy-id user@192.168.1.11`
- Verifier dans `ansible.cfg` : `host_key_checking = False`

**Erreur de permissions :**

```
fatal: [web01]: FAILED! => {"msg": "Missing sudo password"}
```

Solutions :
- Ajouter `become: yes` dans le playbook ou la tache
- Verifier la configuration sudo sur le serveur distant
- Utiliser `--ask-become-pass` ou configurer le sudoers sans mot de passe

**Erreur de syntaxe YAML :**

```
ERROR! Syntax Error while loading YAML.
  mapping values are not allowed in this context
```

Solutions :
- Verifier l'indentation (utiliser des espaces, jamais des tabulations)
- Utiliser `ansible-playbook site.yml --syntax-check`
- Utiliser un linter YAML

**Erreur de variable non definie :**

```
fatal: [web01]: FAILED! => {"msg": "The task includes an option with an undefined variable. The error was: 'db_password' is undefined"}
```

Solutions :
- Verifier que la variable est definie dans `group_vars`, `host_vars` ou le playbook
- Utiliser le filtre `default` : `{{ db_password | default('') }}`
- Utiliser le filtre `mandatory` : `{{ db_password | mandatory }}`

**Erreur de module :**

```
fatal: [web01]: FAILED! => {"msg": "Unsupported parameters for (apt) module: nome. Supported parameters include: ..."}
```

Solutions :
- Verifier les noms des parametres dans la documentation du module
- Utiliser `ansible-doc apt` pour voir les parametres disponibles

### Module `debug`

```yaml
- name: Afficher la valeur d'une variable
  debug:
    var: ansible_default_ipv4.address

- name: Afficher un message formate
  debug:
    msg: "Le serveur {{ inventory_hostname }} a {{ ansible_memtotal_mb }}MB de RAM"

- name: Afficher une structure complexe
  debug:
    msg: "{{ ansible_mounts | to_nice_json }}"
    verbosity: 2    # Affiche seulement avec -vv ou plus
```

### Module `assert`

```yaml
- name: Verifier les prerequis du serveur
  assert:
    that:
      - ansible_memtotal_mb >= 2048
      - ansible_processor_vcpus >= 2
      - ansible_distribution == 'Ubuntu'
      - ansible_distribution_major_version | int >= 20
    fail_msg: "Le serveur {{ inventory_hostname }} ne respecte pas les prerequis minimum"
    success_msg: "Tous les prerequis sont valides"
```

### Module `fail`

```yaml
- name: Recuperer le statut du service
  command: systemctl is-active nginx
  register: nginx_status
  ignore_errors: yes

- name: Echouer si Nginx n'est pas actif
  fail:
    msg: "Nginx n'est pas en cours d'execution sur {{ inventory_hostname }}. Statut : {{ nginx_status.stdout }}"
  when: nginx_status.rc != 0
```

### Mode check (dry-run)

```bash
# Verifier ce qui serait modifie sans rien appliquer
ansible-playbook site.yml --check

# Avec le diff pour voir les changements dans les fichiers
ansible-playbook site.yml --check --diff
```

---

## Optimisation des performances

### Fact caching

Par defaut, Ansible collecte les facts a chaque execution. Le caching permet de reutiliser les facts precedemment collectes.

**Cache en fichier JSON :**

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout = 86400    # 24 heures en secondes
```

**Cache Redis (pour les environnements distribues) :**

```ini
# ansible.cfg
[defaults]
gathering = smart
fact_caching = redis
fact_caching_connection = localhost:6379:0
fact_caching_timeout = 86400
```

Installation : `pip install redis`

### Pipelining SSH

Le pipelining reduit le nombre d'operations SSH en executant les modules directement via la connexion SSH, sans copier de fichiers temporaires.

```ini
# ansible.cfg
[ssh_connection]
pipelining = True
```

Gain : jusqu'a 5 fois plus rapide sur les taches simples.

**Prerequis :** l'option `requiretty` ne doit pas etre activee dans le fichier sudoers des machines distantes.

### ControlPersist

Reutilise les connexions SSH existantes pour eviter de renegocier a chaque tache.

```ini
# ansible.cfg
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=3600s -o PreferredAuthentications=publickey
```

### Forks (parallelisme)

Par defaut, Ansible traite 5 serveurs en parallele. Augmenter cette valeur accelere les deploiements sur de grands parcs.

```ini
# ansible.cfg
[defaults]
forks = 20    # 20 serveurs en parallele
```

### Strategie `free`

Par defaut (strategie `linear`), Ansible attend que tous les serveurs terminent une tache avant de passer a la suivante. La strategie `free` permet a chaque serveur d'avancer a son propre rythme.

```yaml
- hosts: webservers
  strategy: free
  tasks:
    - name: Installer les paquets
      apt:
        name: nginx
        state: present

    - name: Configurer le service
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
```

### Taches asynchrones

Pour les taches longues (compilation, telechargement, backup) :

```yaml
- name: Telecharger un fichier volumineux
  get_url:
    url: "https://example.com/gros-fichier.tar.gz"
    dest: /tmp/gros-fichier.tar.gz
  async: 600     # Timeout de 10 minutes
  poll: 0        # Ne pas attendre
  register: download_task

# ... autres taches ...

- name: Attendre la fin du telechargement
  async_status:
    jid: "{{ download_task.ansible_job_id }}"
  register: result
  until: result.finished
  retries: 30
  delay: 20
```

### Mitogen

Mitogen est un plugin qui accelere considerablement Ansible en eliminant les transferts de fichiers temporaires.

```bash
pip install mitogen
```

```ini
# ansible.cfg
[defaults]
strategy_plugins = /chemin/vers/mitogen/ansible_mitogen/plugins/strategy
strategy = mitogen_linear
```

Gain : jusqu'a 7 fois plus rapide sur certaines operations.

### Limiter la collecte des facts

```yaml
# Ne pas collecter les facts du tout
- hosts: all
  gather_facts: no
  tasks: [...]

# Collecter uniquement un sous-ensemble
- hosts: all
  gather_facts: yes
  gather_subset:
    - network
    - hardware
  tasks: [...]

# Sous-ensembles disponibles :
# all, min, hardware, network, virtual, ohai, facter
```

---

## Filtres et templates Jinja2

### Filtres essentiels

**`default` et `mandatory` :**

```yaml
# Valeur par defaut si la variable n'est pas definie
http_port: "{{ custom_port | default(80) }}"

# Forcer la presence d'une variable (erreur si absente)
db_password: "{{ vault_db_password | mandatory }}"
```

**`combine` (fusion de dictionnaires) :**

```yaml
vars:
  default_config:
    log_level: info
    max_connections: 100
    timeout: 30
  custom_config:
    log_level: debug
    max_connections: 500

tasks:
  - name: Fusionner les configurations
    debug:
      msg: "{{ default_config | combine(custom_config) }}"
    # Resultat : {log_level: debug, max_connections: 500, timeout: 30}
```

**`regex_replace` :**

```yaml
- name: Nettoyer un nom de fichier
  debug:
    msg: "{{ 'Mon Fichier (v2).txt' | regex_replace('[^a-zA-Z0-9.]', '_') }}"
    # Resultat : Mon_Fichier__v2_.txt
```

**Conversion JSON/YAML :**

```yaml
- name: Convertir en JSON
  debug:
    msg: "{{ ma_variable | to_json }}"

- name: Convertir en YAML
  debug:
    msg: "{{ ma_variable | to_yaml }}"

- name: Parser du JSON
  set_fact:
    resultat: "{{ json_string | from_json }}"

- name: Convertir en JSON lisible
  debug:
    msg: "{{ ma_variable | to_nice_json(indent=2) }}"
```

### Debogage des templates

Pour tester un template sans l'appliquer :

```bash
# Verifier le rendu d'un template
ansible all -m template -a "src=templates/nginx.conf.j2 dest=/dev/null" --check --diff -i inventories/production/hosts.yml --limit web01
```

Dans un template, on peut utiliser des commentaires Jinja2 pour le debogage :

```jinja
{# DEBUG : ansible_default_ipv4 = {{ ansible_default_ipv4 | to_nice_json }} #}

server {
    listen {{ nginx_port | default(80) }};
    server_name {{ server_name | default(inventory_hostname) }};
}
```

### Lookup plugins

Les lookups permettent d'acceder a des donnees externes :

```yaml
# Lire un fichier
- name: Charger une cle SSH
  set_fact:
    ssh_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"

# Lire une variable d'environnement
- name: Recuperer le token CI
  set_fact:
    ci_token: "{{ lookup('env', 'CI_TOKEN') }}"

# Generer un mot de passe aleatoire
- name: Generer un mot de passe
  set_fact:
    random_password: "{{ lookup('password', '/dev/null length=20 chars=ascii_letters,digits') }}"

# Lire un fichier CSV
- name: Charger les utilisateurs depuis un CSV
  debug:
    msg: "{{ lookup('csvfile', 'john file=users.csv delimiter=, col=2') }}"
```

---

## Bonnes pratiques

### ansible-lint

ansible-lint analyse les playbooks et roles pour detecter les mauvaises pratiques.

```bash
# Installation
pip install ansible-lint

# Analyser un playbook
ansible-lint playbooks/site.yml

# Analyser tous les playbooks et roles
ansible-lint

# Avec correction automatique
ansible-lint --fix playbooks/site.yml
```

**Configuration `.ansible-lint` :**

```yaml
---
exclude_paths:
  - .cache/
  - .github/
  - .venv/

skip_list:
  - yaml[line-length]

enable_list:
  - fqcn-builtins      # Utiliser les noms complets des modules
  - no-changed-when     # Les taches command/shell doivent avoir changed_when
```

### Molecule pour tester les roles

Molecule permet de tester les roles Ansible dans des conteneurs Docker isoles.

```bash
# Installation
pip install molecule molecule-docker

# Initialiser dans un role
cd roles/nginx
molecule init scenario default --driver-name docker

# Lancer les tests
molecule test

# Cycle de developpement iteratif
molecule converge    # Appliquer le role
molecule verify      # Verifier le resultat
molecule destroy     # Nettoyer
```

### Tests d'idempotence

Un playbook idempotent ne doit rien modifier a la deuxieme execution.

```bash
# Premiere execution : des changements sont attendus
ansible-playbook site.yml

# Deuxieme execution : aucun changement ne doit apparaitre
ansible-playbook site.yml
# Verifier que "changed=0" pour tous les serveurs
```

### Documentation

Chaque role doit contenir un fichier `README.md` avec :
- Description du role
- Variables requises et optionnelles avec leurs valeurs par defaut
- Dependances
- Exemples d'utilisation

Chaque template doit contenir la mention `ansible_managed` :

```jinja
# {{ ansible_managed }}
# Ce fichier est gere par Ansible. Ne pas modifier manuellement.
```

---

## TP : Resoudre des erreurs simulees dans des playbooks existants

### Objectifs

- Diagnostiquer des erreurs dans des playbooks Ansible
- Utiliser les outils de debogage (verbose, debug, check mode)
- Corriger 5 types d'erreurs differentes
- Comprendre les messages d'erreur Ansible

### Consignes generales

Pour chaque playbook ci-dessous :
1. Lire le playbook et identifier l'erreur (ou les erreurs)
2. Executer le playbook avec `--syntax-check` et/ou en mode verbose pour confirmer le diagnostic
3. Corriger l'erreur
4. Verifier que le playbook fonctionne avec `--check`

---

### Playbook 1 : Erreur YAML (indentation et syntaxe)

**Comportement attendu :** Installer Nginx et deployer un fichier de configuration.

**Comportement observe :** Le playbook ne se charge pas, Ansible affiche une erreur de syntaxe.

**Fichier `playbook_erreur_1.yml` :**

```yaml
---
- name: Installer et configurer Nginx
  hosts: webservers
  become: yes

  tasks:
    - name: Installer Nginx
      apt:
        name: nginx
        state: present

    - name: Copier la configuration
      template:
        src: nginx.conf.j2
         dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: Recharger Nginx

    - name: Demarrer Nginx
      systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
  - name: Recharger Nginx
    systemd:
      name: nginx
      state: reloaded
```

**Indice :** Observer attentivement l'indentation de chaque parametre du module `template` et l'indentation du bloc `handlers`.

---

### Playbook 2 : Variable non definie

**Comportement attendu :** Creer un utilisateur applicatif et deployer un fichier de configuration avec les informations de connexion a la base de donnees.

**Comportement observe :** Ansible echoue avec l'erreur `'database_password' is undefined`.

**Fichier `playbook_erreur_2.yml` :**

```yaml
---
- name: Configurer l'application
  hosts: webservers
  become: yes

  vars:
    app_name: monapp
    app_user: appuser
    app_dir: /opt/monapp
    database_host: 192.168.1.20
    database_port: 3306
    database_name: monapp_db
    database_user: monapp_user
    # database_password: manquant !

  tasks:
    - name: Creer l'utilisateur applicatif
      user:
        name: "{{ app_user }}"
        system: yes
        shell: /bin/bash
        home: "{{ app_dir }}"

    - name: Creer le repertoire de l'application
      file:
        path: "{{ app_dir }}"
        state: directory
        owner: "{{ app_user }}"
        mode: '0755'

    - name: Deployer le fichier de configuration
      copy:
        content: |
          [database]
          host = {{ database_host }}
          port = {{ database_port }}
          name = {{ database_name }}
          user = {{ database_user }}
          password = {{ database_password }}

          [application]
          name = {{ app_name }}
          debug = false
        dest: "{{ app_dir }}/config.ini"
        owner: "{{ app_user }}"
        mode: '0600'
```

**Indice :** La variable `database_password` n'est definie nulle part. Il faut soit la definir dans `vars`, soit utiliser le filtre `default` ou `mandatory` pour gerer ce cas proprement. En production, cette variable devrait provenir d'Ansible Vault.

---

### Playbook 3 : Module mal utilise (mauvais parametre)

**Comportement attendu :** Installer des paquets, creer un utilisateur et configurer un cron job.

**Comportement observe :** Ansible echoue avec des erreurs de parametres invalides sur plusieurs taches.

**Fichier `playbook_erreur_3.yml` :**

```yaml
---
- name: Configurer le serveur de monitoring
  hosts: monitoring
  become: yes

  tasks:
    - name: Installer les paquets necessaires
      apt:
        nome:
          - prometheus
          - grafana
          - node-exporter
        state: present
        update_cache: yes

    - name: Creer l'utilisateur prometheus
      user:
        name: prometheus
        system: yes
        shell: /bin/false
        create_home: no
        home_directory: /var/lib/prometheus

    - name: Creer le repertoire de donnees
      file:
        path: /var/lib/prometheus
        state: directory
        owner: prometheus
        group: prometheus
        permissions: '0755'

    - name: Configurer le cron de backup
      cron:
        name: "Backup Prometheus"
        user: root
        minutes: 0
        hours: 2
        job: "/usr/local/bin/backup-prometheus.sh"

    - name: Demarrer Prometheus
      systemd:
        name: prometheus
        state: started
        enabled: yes
```

**Indice :** Verifier les noms des parametres de chaque module. Utiliser `ansible-doc apt`, `ansible-doc user`, `ansible-doc file` et `ansible-doc cron` pour trouver les noms corrects. Les erreurs sont :
- `nome` au lieu de `name` dans le module `apt`
- `home_directory` au lieu de `home` dans le module `user`
- `permissions` au lieu de `mode` dans le module `file`
- `minutes` et `hours` au lieu de `minute` et `hour` dans le module `cron`

---

### Playbook 4 : Probleme de permissions (become manquant)

**Comportement attendu :** Installer des paquets, modifier des fichiers systeme et redemarrer des services.

**Comportement observe :** Les taches echouent avec des erreurs de permissions (`Permission denied`).

**Fichier `playbook_erreur_4.yml` :**

```yaml
---
- name: Configurer le serveur web
  hosts: webservers
  # become: yes   <-- MANQUANT au niveau global

  tasks:
    - name: Mettre a jour le cache apt
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Installer Nginx et les outils
      apt:
        name:
          - nginx
          - curl
          - vim
        state: present

    - name: Deployer la configuration Nginx
      copy:
        content: |
          server {
              listen 80;
              server_name example.com;
              root /var/www/html;
          }
        dest: /etc/nginx/sites-available/example.conf
        owner: root
        group: root
        mode: '0644'

    - name: Activer le site
      file:
        src: /etc/nginx/sites-available/example.conf
        dest: /etc/nginx/sites-enabled/example.conf
        state: link

    - name: Ouvrir le port 80 dans le firewall
      ufw:
        rule: allow
        port: '80'
        proto: tcp

    - name: Redemarrer Nginx
      systemd:
        name: nginx
        state: restarted

    - name: Afficher un message de confirmation
      debug:
        msg: "Le serveur {{ inventory_hostname }} est configure"
```

**Indice :** Toutes les taches qui interagissent avec le systeme (installation de paquets, modification de fichiers dans `/etc`, gestion des services, configuration du firewall) necessitent des privileges root. Il faut ajouter `become: yes` soit au niveau du play, soit au niveau de chaque tache qui le necessite. Attention : la tache `debug` n'a pas besoin de `become`.

La bonne pratique est d'ajouter `become: yes` uniquement sur les taches qui le necessitent (principe du moindre privilege) :

```yaml
    - name: Mettre a jour le cache apt
      apt:
        update_cache: yes
      become: yes

    # La tache debug n'a PAS besoin de become
    - name: Afficher un message
      debug:
        msg: "Pas besoin de sudo ici"
```

Alternativement, pour simplifier, on peut mettre `become: yes` au niveau du play entier.

---

### Playbook 5 : Erreur logique (condition incorrecte et handler non declenche)

**Comportement attendu :** Installer MySQL, deployer une configuration personnalisee, redemarrer le service, puis creer la base de donnees.

**Comportement observe :** Le handler `Redemarrer MySQL` n'est jamais declenche malgre la modification du fichier de configuration. De plus, la tache conditionnelle de creation de la base de donnees ne s'execute jamais.

**Fichier `playbook_erreur_5.yml` :**

```yaml
---
- name: Configurer le serveur MySQL
  hosts: databases
  become: yes

  vars:
    mysql_port: 3306
    mysql_max_connections: 200
    mysql_root_password: "SuperSecret123"
    create_database: true
    db_name: application_db

  tasks:
    - name: Installer MySQL
      apt:
        name:
          - mysql-server
          - python3-pymysql
        state: present

    - name: Demarrer MySQL
      systemd:
        name: mysql
        state: started
        enabled: yes

    - name: Deployer la configuration MySQL personnalisee
      copy:
        content: |
          [mysqld]
          port = {{ mysql_port }}
          max_connections = {{ mysql_max_connections }}
          bind-address = 0.0.0.0
        dest: /etc/mysql/mysql.conf.d/custom.cnf
        owner: root
        group: root
        mode: '0644'
      notify: Restart MySQL

    - name: Definir le mot de passe root
      mysql_user:
        name: root
        password: "{{ mysql_root_password }}"
        login_unix_socket: /var/run/mysqld/mysqld.sock
        check_implicit_admin: yes

    - name: Creer la base de donnees
      mysql_db:
        name: "{{ db_name }}"
        state: present
        login_user: root
        login_password: "{{ mysql_root_password }}"
      when: create_database == "true"

  handlers:
    - name: Redemarrer MySQL
      systemd:
        name: mysql
        state: restarted
```

**Indice :** Ce playbook contient deux erreurs logiques :

1. **Le handler n'est pas declenche** car le nom dans `notify` (`Restart MySQL`) ne correspond pas au nom du handler (`Redemarrer MySQL`). Les noms doivent etre strictement identiques (sensible a la casse et aux accents).

2. **La condition `when` ne fonctionne pas** car `create_database` est un booleen (`true`) mais la condition le compare a la chaine de caracteres `"true"`. En Ansible/Jinja2, `true != "true"`. La condition correcte est `when: create_database` ou `when: create_database | bool`.

**Corrections a apporter :**

```yaml
    # Correction 1 : Aligner le nom du notify avec le handler
    - name: Deployer la configuration MySQL personnalisee
      copy:
        # ...
      notify: Redemarrer MySQL     # <-- Doit correspondre exactement au handler

    # Correction 2 : Utiliser le booleen directement
    - name: Creer la base de donnees
      mysql_db:
        # ...
      when: create_database        # <-- Sans les guillemets, test booleen direct
```

---

### Recapitulatif des erreurs

| Playbook | Type d'erreur | Outil de diagnostic |
|----------|--------------|---------------------|
| 1 | Syntaxe YAML (indentation) | `--syntax-check` |
| 2 | Variable non definie | `-vvv`, module `debug` |
| 3 | Parametres de module incorrects | `ansible-doc`, `-v` |
| 4 | Permissions manquantes (`become`) | `-vvv`, logs serveur |
| 5 | Logique (handler + condition) | `--check --diff`, `debug` |

### Livrables

- 5 playbooks corriges et fonctionnels
- Pour chaque playbook : explication ecrite de l'erreur trouvee et de la correction appliquee
- Demonstration que chaque playbook passe le `--syntax-check` apres correction

### Criteres de validation

| Critere | Points |
|---------|--------|
| Playbook 1 corrige (indentation YAML) | 15% |
| Playbook 2 corrige (variable non definie) | 20% |
| Playbook 3 corrige (parametres de modules) | 20% |
| Playbook 4 corrige (permissions) | 20% |
| Playbook 5 corrige (logique handler + condition) | 25% |

---

**Retour au sommaire Jour 4 :** [../README.md](../README.md)
