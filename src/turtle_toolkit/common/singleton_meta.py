"""singleton_meta.py - Thread-safe singleton meta class
Author: Tom Riley
Date: 2025-05-04
"""

import threading
from typing import Any, ClassVar, Dict, Generic, TypeVar

T = TypeVar("T")


class SingletonMeta(type, Generic[T]):
    """Thread-safe singleton meta class."""

    _instances: Dict["SingletonMeta"[T], T] = {}
    _lock: ClassVar = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> T:
        """Create a new instance of the singleton class if it doesn't exist."""
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
