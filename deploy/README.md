# Installateur local (Ansible) --- nuagefernandez

Ce dossier contient un installateur basé sur **Ansible**, à lancer
**directement sur le serveur**.  
Pas besoin de clé SSH ni de poste de contrôle séparé : tout se fait en
**local**.

---

## ⚙️ Prérequis côté serveur

- Debian 12 (recommandé)
- Un utilisateur (ex. `py`) avec **sudo** fonctionnel
- Git installé  
  *(si besoin : `sudo apt-get install -y git`)*

---

## 🚀 Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/guillaut5/nuagefernandez.git
cd nuagefernandez
git checkout restructure-backend
```

> Si le dépôt est privé : utiliser un **token GitHub** avec l'URL HTTPS.  
> *(aucune clé SSH nécessaire ni incluse dans le repo)*

---

### 2. Installer Ansible (si absent)

```bash
sudo apt-get update
sudo apt-get install -y ansible python3-venv python3-pip
```

---

### 3. Déploiement global (backend + frontend)

```bash
cd deploy

# Vérifier la connexion locale
ansible -m ping nuage

# Lancer l’installation complète
ansible-playbook site.yml -K
```

- `-K` demandera le mot de passe sudo de l'utilisateur courant (ex. `py`).
- Le playbook déploie automatiquement :
  - backend (Django + venv + migrations)
  - frontend (Node/npm + build)
  - gunicorn (service systemd)
  - nginx (reverse proxy en HTTP **uniquement**)

---

### 4. Configuration du domaine DuckDNS + HTTPS

> ⚠️ Cette étape est **manuelle + spécifique** :  
> il faut d’abord créer un domaine sur [https://www.duckdns.org](https://www.duckdns.org), récupérer son **token**, puis lancer le playbook dédié.

Deux méthodes possibles :

#### a) **Avec fichier de variables**

Créer `vars/duckdns.yml` :

```yaml
duckdns_domain: "monprojet.duckdns.org"
duckdns_token: "abcdef1234567890"
use_https: true
```

Puis lancer :

```bash
ansible-playbook -i inventory deploy_duckdns.yml -K
```

#### b) **Avec assistant interactif**

Si aucune variable n’est définie, Ansible demandera automatiquement :  
- le domaine DuckDNS  
- le token  
- l’activation HTTPS  

Lancement :

```bash
ansible-playbook -i inventory deploy_duckdns.yml -K
```

➡️ Le rôle va :
- Installer le client DuckDNS (cron job toutes les 5 min).
- Vérifier que le domaine pointe bien sur la box.
- Lancer **certbot** avec le plugin Nginx.
- Activer automatiquement la redirection **HTTP → HTTPS**.

---

## 📦 Variables implicites

Chemins et réglages par défaut :

- Racine projet : `/opt/nuagefernandez/`
- Backend : `backend/`
- Frontend : `front_end/`
- Utilisateur système créé : `nuage`
- Service systemd : `nuage`
- Socket gunicorn : `/opt/nuagefernandez/gunicorn.sock`
- Domaine nginx : `_` (répond sur l'IP, port 80, avant DuckDNS/HTTPS)

---

## 🔄 Mise à jour

```bash
cd /opt/nuagefernandez
sudo -u nuage git pull
cd deploy
ansible-playbook site.yml -K
```

Si le domaine DuckDNS ou le certificat a changé :

```bash
ansible-playbook -i inventory deploy_duckdns.yml -K
```

---

## 🛠️ Dépannage rapide

- Logs gunicorn :

  ```bash
  journalctl -u nuage -e
  ```

- Vérifier/recharger Nginx :

  ```bash
  sudo nginx -t && sudo systemctl reload nginx
  ```

- Vérifier Python/venv :

  ```bash
  /opt/nuagefernandez/venv/bin/python -V
  ```
