from datetime import datetime
from inspect import signature
from typing import Any

from .connector import BanchoConnector


class WebsocketBanchoConnector(BanchoConnector):
    dequeue_on_enqueue = False

    def __init__(
        self,
        url: str | None = None,
        *,
        path: str = "/",
        secure: bool = True,
        headers: dict[str, str] | None = None,
        open_timeout: float | None = 10,
        ping_interval: float | None = 20,
        ping_timeout: float | None = 20,
        close_timeout: float | None = 10,
    ) -> None:
        super().__init__()
        self.path = path
        self.secure = secure
        self.headers = headers or {}
        self.open_timeout = open_timeout
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.close_timeout = close_timeout
        self.url = url or ""
        self.websocket: Any | None = None

    def bind(self, bancho) -> None:
        super().bind(bancho)

        if self.url:
            # Url was set manually
            return

        scheme = "wss" if self.secure else "ws"
        path = self.path if self.path.startswith("/") else f"/{self.path}"
        self.url = f"{scheme}://c.{self.game.server}{path}"

    def connect(self) -> None:
        """Perform the initial connection to the websocket server."""
        WebSocketException = self.load_websocket_exception()
        connect = self.load_connect()

        try:
            headers = {
                "osu-version": self.game.version or "",
                **self.headers,
            }
            self.websocket = connect(
                self.url,
                headers,
                open_timeout=self.open_timeout,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout,
            )
        except (OSError, TimeoutError, WebSocketException) as exc:
            self.bancho.connected = False
            self.bancho.retry = True
            self.bancho.logger.error(
                f"[{self.url}]: Websocket connection was refused: {exc}"
            )
            return

        login_data = (
            f"{self.game.username}\r\n"
            f"{self.game.password_hash}\r\n"
            f"{self.game.client}\r\n"
        )
        self.websocket.send(login_data.encode())
        self.bancho.connected = True

    def send(self, data: bytes, dequeue: bool) -> None:
        if not self.bancho.connected or not self.websocket:
            return

        self.websocket.send(data)
        self.bancho.last_action = datetime.now().timestamp()

        if dequeue:
            self.receive()

    def receive(self) -> None:
        """Process incoming websocket messages from the server."""
        if not self.bancho.connected or not self.websocket:
            return

        ConnectionClosed = self.load_connection_closed()

        try:
            self.process_message()

            while self.bancho.connected:
                try:
                    self.process_message(timeout=0)
                except TimeoutError:
                    break
        except ConnectionClosed as exc:
            self.bancho.connected = False
            self.bancho.retry = True
            self.bancho.logger.error(
                f"[{self.url}]: Websocket connection closed: {exc}"
            )

    def process_message(self, timeout: float | None = None) -> None:
        if not self.websocket:
            return

        message = self.websocket.recv(timeout=timeout)
        data = message.encode() if isinstance(message, str) else bytes(message)

        if not data:
            return

        self.game.packets.data_received(data, self.game)

    def close(self) -> None:
        if not self.websocket:
            return

        try:
            self.websocket.close()
        finally:
            self.websocket = None

    @staticmethod
    def load_connect():
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise RuntimeError(
                "WebsocketBanchoConnector requires the optional websockets "
                "dependency. Install it with `pip install osu[websockets]`."
            ) from exc

        def wrapper(url: str, headers: dict[str, str], **kwargs):
            parameters = signature(connect).parameters

            if "additional_headers" in parameters:
                kwargs["additional_headers"] = headers
            else:
                kwargs["extra_headers"] = headers

            if "user_agent_header" in parameters:
                kwargs["user_agent_header"] = "osu!"

            return connect(url, **kwargs)

        return wrapper

    @staticmethod
    def load_connection_closed():
        try:
            from websockets.exceptions import ConnectionClosed
        except ImportError as exc:
            raise RuntimeError(
                "WebsocketBanchoConnector requires the optional websockets "
                "dependency. Install it with `pip install osu[websockets]`."
            ) from exc

        return ConnectionClosed

    @staticmethod
    def load_websocket_exception():
        try:
            from websockets.exceptions import WebSocketException
        except ImportError as exc:
            raise RuntimeError(
                "WebsocketBanchoConnector requires the optional websockets "
                "dependency. Install it with `pip install osu[websockets]`."
            ) from exc

        return WebSocketException
