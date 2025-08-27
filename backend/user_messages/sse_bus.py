# -- Genre de MQTT local, en memoire... Ne marche que sur un seul process.

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
