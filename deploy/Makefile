.PHONY: ping install logs restart nginx-reload

# Ping Ansible (vérifie que tout est ok en local)
ping:
	ansible -m ping nuage

# Installation / mise à jour complète
install:
	ansible-playbook site.yml -K

# Voir les logs gunicorn
logs:
	sudo journalctl -u nuage -e

# Redémarrer le service gunicorn
restart:
	sudo systemctl restart nuage

# Recharger la config Nginx
nginx-reload:
	sudo nginx -t && sudo systemctl reload nginx
