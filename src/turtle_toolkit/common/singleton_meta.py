"""singleton_meta.py - Thread-safe singleton meta class
Author: Tom Riley
Date: 2025-05-04
"""

import threading


class SingletonMeta(type):
    """Thread-safe singleton meta class."""

    _instances: dict[str, "SingletonMeta"] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
