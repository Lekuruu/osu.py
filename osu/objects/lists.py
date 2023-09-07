from typing import Iterable, Iterator, Set, Any
from threading import Lock


class LockedSet(set):
    """A set where add(), remove(), and 'in' operator are thread-safe"""

    def __init__(self, *args, **kwargs):
        self._lock = Lock()
        super(LockedSet, self).__init__(*args, **kwargs)

    def __len__(self) -> int:
        with self._lock:
            return super(LockedSet, self).__len__()

    def __iter__(self) -> Iterator:
        with self._lock:
            return super(LockedSet, self).__iter__()

    def __or__(self, __value: Set) -> Set[Any]:
        with self._lock:
            return super(LockedSet, self).__or__(__value)

    def __contains__(self, obj: object) -> bool:
        with self._lock:
            return super(LockedSet, self).__contains__(obj)

    def add(self, element: Any) -> None:
        with self._lock:
            return super(LockedSet, self).add(element)

    def remove(self, element: Any) -> None:
        with self._lock:
            super(LockedSet, self).remove(element)

    def update(self, *s: Iterable) -> None:
        with self._lock:
            super(LockedSet, self).update(*s)
