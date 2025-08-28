# Installateur local (Ansible) --- nuagefernandez

Ce dossier contient un installateur basé sur **Ansible**, à lancer
**directement sur le serveur**.\
Pas besoin de clé SSH ni de poste de contrôle séparé : tout se fait en
**local**.

------------------------------------------------------------------------

## ⚙️ Prérequis côté serveur

-   Debian 12 (recommandé)
-   Un utilisateur (ex. `py`) avec **sudo** fonctionnel
-   Git installé\
    *(si besoin : `sudo apt-get install -y git`)*

------------------------------------------------------------------------

## 🚀 Installation

### 1. Récupérer le projet

``` bash
git clone https://github.com/guillaut5/nuagefernandez.git
cd nuagefernandez
git checkout restructure-backend
```

> Si le dépôt est privé : utiliser un **token GitHub** avec l'URL
> HTTPS.\
> *(aucune clé SSH nécessaire ni incluse dans le repo)*

------------------------------------------------------------------------

### 2. Installer Ansible (si absent)

``` bash
sudo apt-get update
sudo apt-get install -y ansible python3-venv python3-pip
```

------------------------------------------------------------------------

### 3. Lancer l'installateur

``` bash
cd deploy

# Vérifier la connexion locale
ansible -m ping nuage

# Lancer l’installation complète
ansible-playbook site.yml -K
```

-   `-K` demandera le mot de passe sudo de l'utilisateur courant (ex.
    `py`).
-   Le playbook déploie automatiquement :
    -   backend (Django + venv + migrations)
    -   frontend (Node/npm + build)
    -   gunicorn (service systemd)
    -   nginx (reverse proxy en HTTP)

------------------------------------------------------------------------

## 📦 Variables implicites

Chemins et réglages par défaut :

-   Racine projet : `/opt/nuagefernandez/`
-   Backend : `backend/`
-   Frontend : `front_end/`
-   Utilisateur système créé : `nuage`
-   Service systemd : `nuage`
-   Socket gunicorn : `/opt/nuagefernandez/gunicorn.sock`
-   Domaine nginx : `_` (répond sur l'IP, port 80)

------------------------------------------------------------------------

## 🔄 Mise à jour

``` bash
cd /opt/nuagefernandez
sudo -u nuage git pull
cd deploy
ansible-playbook site.yml -K
```

------------------------------------------------------------------------

## 🛠️ Dépannage rapide

-   Logs gunicorn :

    ``` bash
    journalctl -u nuage -e
    ```

-   Vérifier/recharger Nginx :

    ``` bash
    sudo nginx -t && sudo systemctl reload nginx
    ```

-   Vérifier Python/venv :

    ``` bash
    /opt/nuagefernandez/venv/bin/python -V
    ```
