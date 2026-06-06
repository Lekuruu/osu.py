from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from datetime import datetime
from queue import Queue

from .constants import ServerPackets
from .streams import StreamIn

if TYPE_CHECKING:
    from .client import BanchoClient

import requests
import socket
import gzip
import time


class BanchoConnector(ABC):
    """Transport layer used by BanchoClient."""

    dequeue_on_enqueue = True

    def __init__(self) -> None:
        self._bancho: BanchoClient | None = None

    def bind(self, bancho: "BanchoClient") -> None:
        self._bancho = bancho

    @property
    def bancho(self) -> "BanchoClient":
        if self._bancho is None:
            raise RuntimeError("BanchoConnector must be bound to a BanchoClient")

        return self._bancho

    @property
    def game(self):
        return self.bancho.game

    def wait(self) -> None:
        """Wait until the next receive cycle."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to bancho."""

    @abstractmethod
    def send(self, data: bytes, dequeue: bool) -> None:
        """Push packet data to bancho."""

    @abstractmethod
    def receive(self) -> None:
        """Receive packets from bancho."""

    def close(self) -> None:
        """Close transport resources."""
