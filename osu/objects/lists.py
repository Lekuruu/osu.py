from collections.abc import MutableMapping as AbstractMutableMapping
from collections.abc import Set as AbstractSet
from contextlib import contextmanager
from threading import Lock, Condition
from typing import Iterator, Optional, TypeVar, Tuple, Any, Set

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class ReadWriteLock:
    """A read-write lock that allows multiple readers or a single writer"""

    __slots__ = ("lock", "cond", "readers", "writer")

    def __init__(self):
        self.lock = Lock()
        self.cond = Condition(self.lock)
        self.readers = 0
        self.writer = False

    def acquire_read(self):
        with self.cond:
            while self.writer:
                self.cond.wait()
            self.readers += 1

    def acquire_write(self):
        with self.cond:
            while self.writer or self.readers > 0:
                self.cond.wait()
            self.writer = True

    def release_read(self):
        with self.cond:
            if self.readers <= 0:
                raise RuntimeError("release_read without acquire")
            self.readers -= 1
            if self.readers == 0:
                self.cond.notify_all()

    def release_write(self):
        with self.cond:
            if not self.writer:
                raise RuntimeError("release_write without acquire")
            self.writer = False
            self.cond.notify_all()

    @contextmanager
    def read_context(self):
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_context(self):
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()


class LockedSet(AbstractSet[T]):
    """A set that is thread-safe for concurrent read and write operations"""

    __slots__ = ("instance", "lock")

    def __init__(self) -> None:
        self.instance: Set[T] = set()
        self.lock = ReadWriteLock()

    def __iter__(self) -> Iterator[T]:
        return iter(self.snapshot_list())

    def __len__(self) -> int:
        with self.lock.read_context():
            return len(self.instance)

    def __contains__(self, item: object) -> bool:
        with self.lock.read_context():
            return item in self.instance

    def add(self, item: T) -> None:
        with self.lock.write_context():
            self.instance.add(item)

    def update(self, *args, **kwargs) -> None:
        with self.lock.write_context():
            self.instance.update(*args, **kwargs)

    def remove(self, item: T) -> None:
        with self.lock.write_context():
            self.instance.remove(item)

    def snapshot(self) -> Set[T]:
        with self.lock.read_context():
            return set(self.instance)

    def snapshot_list(self) -> list[T]:
        with self.lock.read_context():
            return list(self.instance)

    def snapshot_without(self, excluded: T) -> list[T]:
        with self.lock.read_context():
            return [item for item in self.instance if item != excluded]

    def discard(self, item: T) -> None:
        with self.lock.write_context():
            self.instance.discard(item)
