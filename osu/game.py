from collections.abc import Callable
from datetime import datetime
from copy import copy

from .bancho.constants import ServerPackets
from .objects.client import ClientInfo
from .tasks import Task

from .exceptions import ClientInitializationError, ClientConnectionError
from .bancho import BanchoClient, Packets
from .events import EventHandler
from .tasks import TaskManager
from .api import WebAPI

import requests
import hashlib
import logging


class Game:
    """osu! game client
    --------------------
    This class will emulate the online functionality of the osu! stable client.
    It will provide interaction with bancho, as well as the client api.
    """

    def __init__(
        self,
        username: str,
        password: str,
        server="ppy.sh",
        stream="stable40",
        version: int | float | None = None,
        executable_hash: str | None = None,
        tournament: bool = False,
        events: dict[ServerPackets, list[Callable]] | None = None,
        tasks: list[Task] | None = None,
        force_linux_emulation: bool = True,
        disable_chat_logging: bool = False,
        disable_logging: bool = False,
    ) -> None:
        """Parameters
        -------------

        `username`: str
            Your bancho username

        `password`: str
            Your bancho password

        `server`: str
            Server endpoint
            (`ppy.sh`)

        `stream`: str
            Release stream
            (`stable40`)

        `version`: int/float, optional
            Set a custom version
            (Will fetch the latest version automatically)

        `tournament`: bool
            This allows for multiple clients at the same time (supporter only)

        `events`: dict, optional
            Allows to pass in events, instead of registering them normally

        `tasks`: list, optional
            Allows to pass in pre-defined tasks, just like the `events` parameter

        `force_linux_emulation`: bool
            This flag will force osu.py to use a linux client hash, regardless of the operating system.

        `disable_chat_logging`: bool
            Disables the logging of chat messages

        `disable_logging`: bool
            Disables all logging entirely
        """

        self.version = f"b{version}" if version else None
        self.tourney = tournament

        if self.version and self.tourney:
            self.version = f"b{version}tourney"

        self.username = username
        self.password = password
        self.server = server
        self.stream = stream
        self.version_number = version
        self.disable_chat = disable_chat_logging
        self.force_linux_emulation = force_linux_emulation

        self.logger = logging.getLogger("osu!")
        self.logger.disabled = disable_logging

        self.resolve_version()
        assert self.version is not None, "Failed to resolve client version"

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "osu!", "osu-version": self.version})
        self.logger.name = f"osu!-{self.version}"

        self.packets = copy(Packets)
        self.events = EventHandler()
        self.bancho = BanchoClient(self)
        self.tasks = TaskManager(self)
        self.api = WebAPI(self)

        if events:
            self.events.handlers = events

        if tasks:
            self.tasks.tasks = tasks

        if not self.version or not self.version_number:
            raise ClientInitializationError("Failed to resolve client version")

        if executable_hash:
            self.client = ClientInfo(self.version, executable_hash)
            return

        if not (updates := self.api.check_updates()):
            # Updates are required because of the executable hash
            raise ClientInitializationError(
                "Failed to receive latest executable checksum"
            )

        self.client = ClientInfo.from_updates(self.version, updates)

    def __repr__(self) -> str:
        return f"<osu! {self.version}>"

    @property
    def password_hash(self) -> str:
        """Return md5 hashed password"""
        return hashlib.md5(self.password.encode()).hexdigest()

    @property
    def time(self) -> int:
        """Return current time as ticks"""
        return int((datetime.now() - datetime(1, 1, 1)).total_seconds() * 10000000)

    def run(self, exit_on_interrupt=False) -> None:
        try:
            if self.force_linux_emulation:
                self.client.hash.adapters = "runningunderwine"

            self.api.get_backgrounds()
            self.api.get_menu_content()

            if not self.api.connect():
                return

            self.bancho.run()

        except KeyboardInterrupt:
            pass

        finally:
            self.logger.warning("Exiting...")
            self.bancho.exit()
            self.logger.warning("Stopping tasks...")
            self.events.executor.shutdown()
            self.tasks.executor.shutdown()

        if exit_on_interrupt:
            exit(0)

    def resolve_version(self) -> None:
        """Ensure the client version is set"""
        if self.version_number:
            return

        # Fetch latest client version
        self.version = self.fetch_version(self.stream)

    def fetch_version(self, stream: str = "stable40") -> str | None:
        """
        Fetch the latest version of the client from:
        <https://osu.ppy.sh/home/changelog>
        """

        self.logger.info("Fetching client version...")

        response = requests.get(
            f"https://osu.ppy.sh/home/changelog/{stream}",
            allow_redirects=True,
            headers={"User-Agent": "osu!"},
        )

        if not response.ok:
            self.logger.error(f"Failed to get client version ({response.status_code}).")
            self.logger.error(
                "Please check your release stream or provide a custom version!"
            )
            return None

        # Parse url (e.g.: https://osu.ppy.sh/home/changelog/stable40/20230326)
        version = response.url.removesuffix("/").split("/")[-1]

        if not version.replace(".", "").isdigit():
            self.logger.error(
                f'Failed to get client version ("{version}" is not an integer).'
            )
            self.logger.error("Please provide a custom version!")
            return None

        self.logger.debug(f"Version: b{version}{'tourney' if self.tourney else ''}")

        try:
            self.version_number = int(version)
        except ValueError:
            self.version_number = float(version)

        return f"b{version}{'tourney' if self.tourney else ''}"
