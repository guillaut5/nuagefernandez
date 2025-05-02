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

## ⚙️ Installation rapide

1. Clonez ce projet

```bash
git clone https://github.com/toncompte/nuagefernandez.git
cd nuagefernandez
```

2. Créez et activez un environnement Python

```bash
python -m venv venv
source venv/bin/activate  # (Linux/Mac)
venv\Scripts\activate.bat  # (Windows)
```

3. Installez les dépendances

```bash
pip install -r requirements.txt
```

4. Configurez la base

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Lancez le serveur

```bash
python manage.py runserver 0.0.0.0:8000
```

Accédez ensuite à [http://localhost:8000/](http://localhost:8000/) ou depuis votre réseau.

---

## 🌟 Usage pédagogique

- Créer plusieurs utilisateurs (parents, enfants, cousins...)
- Créer des groupes (`Cousins`, `Petitescailloutes`) depuis l'interface Admin
- Envoyer des messages et/ou prendre des photos
- Se connecter en Admin pour montrer que :
  - Les messages supprimés sont toujours visibles
  - Chaque message est loggé dans le fichier `user_messages.log`
- Expliquer que chaque action sur Internet laisse une trace

---

## 📄 Architecture du projet

| Dossier / fichier | Contenu |
|:---|:---|
| `/user_messages/` | App Django principale (messages, groupes personnalisés) |
| `/templates/` | Templates HTML simples et légers |
| `/static/` | Futurs fichiers CSS et JS |
| `manage.py` | Lancement du serveur Django |
| `user_messages.log` | Fichier de log pédagogique 📚 |

---

## 🔒 Sécurité / Vie privée

- Le projet ne dépend d'aucun service externe.
- Tout reste en local : ni cloud, ni API, ni tracking.
- Parfait pour expliquer ce que serait un Internet privé et responsable
