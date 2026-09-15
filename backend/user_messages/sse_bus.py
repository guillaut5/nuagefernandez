# -- Genre de MQTT local, en memoire... Ne marche que sur un seul process.
#
# Concrètement : `_queues` vit dans la mémoire du process Python. Si gunicorn
# tourne avec plusieurs workers, chacun a sa propre copie de `_queues`, donc
# `publish()` dans un worker ne réveille pas les queues souscrites dans un
# autre. Le déploiement (deploy/roles/application/defaults/main.yml) force
# `gunicorn_workers: 1` pour cette raison. Pour scaler un jour, remplacer ce
# module par un vrai pub/sub partagé (ex: Redis) plutôt que par plus de workers.

from collections import defaultdict
from queue import Queue
from typing import Dict, Set, Any

# user_id -> set de queues (un onglet = une queue)
_queues: Dict[int, Set[Queue]] = defaultdict(set)


def subscribe(user_id: int) -> Queue:
    q = Queue()
    _queues[user_id].add(q)
    return q


def unsubscribe(user_id: int, q: Queue) -> None:
    _queues[user_id].discard(q)


def publish(user_id: int, payload: Any) -> None:
    # envoie à tous les onglets de cet utilisateur
    for q in list(_queues[user_id]):
        q.put(payload)
