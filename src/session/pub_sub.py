import logging
from threading import Lock
from typing import Set, Callable, Any, DefaultDict

from black.trans import defaultdict

logger = logging.getLogger(__name__)


class PubSubManager:
    def __init__(self):
        self._topics: DefaultDict[str, Set[Callable[..., None]]] = defaultdict(set)
        self._lock = Lock()  # ✅ FIXED: threading.Lock, not multiprocessing.Lock

    def subscribe(self, topic: str, callback: Callable[..., None]):
        with self._lock:
            self._topics[topic].add(callback)

    def unsubscribe(self, topic: str, callback: Callable[..., None]):
        with self._lock:
            if topic in self._topics:
                self._topics[topic].discard(callback)

    def publish(self, topic: str, *messages: Any, **kwargs: Any):
        with self._lock:
            callbacks = list(self._topics.get(topic, []))

        # Execute callbacks outside the lock to prevent deadlocks
        for callback in callbacks:
            try:
                callback(*messages, **kwargs)
            except Exception as e:
                logger.error(f"Error in callback for topic {topic}: {e}", exc_info=True)


pub_sub = PubSubManager()
