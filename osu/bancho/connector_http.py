from typing import TYPE_CHECKING
from datetime import datetime
from queue import Queue

from .connector import BanchoConnector
from .constants import ServerPackets
from .streams import StreamIn

if TYPE_CHECKING:
    from .client import BanchoClient

import requests
import gzip
import time


class HttpBanchoConnector(BanchoConnector):
    def __init__(self, domain: str | None = None) -> None:
        super().__init__()
        self._domain = domain
        self.domain = domain or ""
        self.url = f"https://{self.domain}" if self.domain else ""
        self.session = requests.Session()
        self.queue: Queue[bytes] = Queue()
        self.token = ""

    def bind(self, bancho: "BanchoClient") -> None:
        super().bind(bancho)

        self.domain = self._domain or f"c.{self.game.server}"
        self.url = f"https://{self.domain}"
        self.token = ""
        self.session.headers.pop("osu-token", None)
        self.session.headers.update(
            {
                "osu-version": self.game.version or "",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "osu!",
                "Host": self.domain,
            }
        )

    def wait(self) -> None:
        time.sleep(self.bancho.request_interval)

    def connect(self) -> None:
        """Perform the initial connection to get a connection token."""
        data = f"{self.game.username}\n{self.game.password_hash}\n{self.game.client}\n"

        response = self.session.post(self.url, data=data)

        if not response.ok:
            self.bancho.connected = False
            self.bancho.retry = True
            self.bancho.logger.error(
                f"[{response.url}]: Connection was refused ({response.status_code})"
            )
            return

        if not (token := response.headers.get("cho-token")):
            self.bancho.logger.debug("Connection token missing from login response")
            self.bancho.connected = False
            self.bancho.retry = False
            self.game.packets.data_received(response.content, self.game)
            return

        self.bancho.logger.debug(f"Received session token: {token}")
        self.bancho.connected = True
        self.token = token

        self.session.headers["osu-token"] = self.token
        self.game.packets.data_received(response.content, self.game)

    def send(self, data: bytes, dequeue: bool) -> None:
        self.queue.put(data)

        if dequeue:
            self.receive()

    def receive(self) -> None:
        """Send queued packets and handle incoming packets."""
        if not self.bancho.connected:
            return

        if self.queue.empty():
            self.bancho.ping_count += 1
            return self.bancho.ping()

        if self.queue.qsize() > 1:
            self.bancho.ping_count = 0

        packets: list[bytes] = []

        while not self.queue.empty():
            packets.append(self.queue.get())

        response = self.session.post(self.url, data=b"".join(packets))

        if not response.ok:
            self.bancho.connected = False
            self.bancho.retry = True
            self.bancho.logger.error(
                f"[{response.request.url}]: Connection was refused ({response.status_code})"
            )
            return

        self.bancho.fast_read = False
        self.game.packets.data_received(response.content, self.game)
        self.bancho.last_action = datetime.now().timestamp()

    def close(self) -> None:
        self.session.close()
