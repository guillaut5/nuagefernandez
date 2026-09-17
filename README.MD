# 📚 NuageFernandez

**NuageFernandez** est un mini-serveur éducatif à installer sur un Raspberry Pi ou sur PC,  
conçu pour montrer à un enfant comment fonctionnent les échanges sur Internet :

- Envoyer des messages 📨
- Partager des photos 📸
- Comprendre que rien n'est jamais vraiment supprimé 🚨
- Visualiser l'enregistrement des activités côté serveur 📚

---

## 🚀 Fonctionnalités principales

- Envoi de messages entre utilisateurs ou vers des groupes (`Cousins`, `Petitescailloutes`, etc.)
- Envoi de photos soit depuis la galerie soit directement depuis la webcam ou l'appareil photo du smartphone
- Captures automatiques de la localisation (latitude/longitude)
- Suppression douce : les messages sont invisibles pour l'utilisateur mais restent en base et sont visibles par l'admin
- Logging pédagogique de toutes les actions (émetteur, destinataire, texte, image oui/non)
- Interface super simple, adaptée aux enfants (aucune pub, aucune dépendance externe)

---

## ⚙️ Installation rapide (développement)

Le projet a deux parties à lancer séparément en dev : l'API Django (`backend/`) et
l'interface Vue (`frontend/`).

1. Clonez ce projet

```bash
git clone https://github.com/guillaut5/nuagefernandez.git
cd nuagefernandez
```

2. Backend (API Django)

```bash
cd backend
python -m venv ../myvenv
../myvenv/Scripts/activate     # Windows
source ../myvenv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# optionnel en dev (les valeurs par défaut marchent déjà) — voir backend/.env.example
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

3. Frontend (interface Vue), dans un second terminal

```bash
cd frontend
npm install
npm run dev
```

4. Ouvrez [http://localhost:5173/](http://localhost:5173/) — c'est l'interface (le
   frontend redirige automatiquement les appels `/api` vers Django sur le port 8000).
   L'admin Django reste accessible sur [http://localhost:8000/admin/](http://localhost:8000/admin/).

Pour un déploiement réel (Raspberry Pi, domaine public), tout est automatisé via
Ansible — voir [`deploy/README.md`](deploy/README.md).

---

## 🌟 Usage pédagogique

- Créer plusieurs utilisateurs (parents, enfants, cousins...)
- Créer des groupes (`Cousins`, `Petitescailloutes`) depuis l'interface Admin
- Envoyer des messages et/ou prendre des photos
- Se connecter en Admin pour montrer que :
  - Les messages supprimés sont toujours visibles
  - Chaque message est loggé dans le fichier `backend/logs/django.log`
- Expliquer que chaque action sur Internet laisse une trace

---

## 📄 Architecture du projet

| Dossier / fichier | Contenu |
|:---|:---|
| `/backend/` | API Django REST (auth JWT, temps réel SSE) + admin |
| `/backend/user_messages/` | App Django principale (modèles, API des messages et groupes) |
| `/backend/.env.example` | Modèle de config pour la prod (clé secrète, hôtes autorisés…) |
| `/frontend/` | Interface Vue 3 (chat, connexion) — tout ce que voit l'utilisateur |
| `/deploy/` | Installateur Ansible pour Raspberry Pi (voir `deploy/README.md`) |
| `manage.py` | Lancement du serveur Django |
| `backend/logs/django.log` | Fichier de log pédagogique 📚 |

---

## 🔒 Sécurité / Vie privée

- Tout reste en local : ni cloud, ni API externe, ni tracking.
- Une seule exception : l'interface charge ses polices (Baloo 2, Plus Jakarta Sans)
  depuis Google Fonts. Sans accès Internet, l'appli fonctionne quand même (elle
  retombe sur une police système), mais c'est un vrai appel réseau externe — à
  auto-héberger un jour si la promesse "zéro dépendance externe" doit être stricte.
- Parfait pour expliquer ce que serait un Internet privé et responsable
