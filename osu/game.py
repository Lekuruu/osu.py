from typing import Optional, Callable, Dict, List
from datetime import datetime
from copy import copy

from .bancho.constants import ServerPackets
from .objects.client import ClientInfo

import traceback
import requests
import hashlib
import logging


class Game:

    """osu! game client
    --------------------
    This class will try to emulate the online functionality of the osu! stable client.
    """

    def __init__(
        self,
        username: str,
        password: str,
        server="ppy.sh",
        stream="stable40",
        version: Optional[int] = None,
        tournament=False,
        events: Optional[Dict[ServerPackets, List[Callable]]] = {},
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

        `version`: int, optional
            Set a custom version
            (Will fetch the latest version automatically)

        `tournament`: bool
            This allows for multiple clients at the same time (supporter only)

        `events`: dict, optional
            Allows to pass in events, instead of registering them normally.
        """

        self.username = username
        self.password = password
        self.server = server
        self.stream = stream
        self.version = version
        self.tourney = tournament

        self.version_number = version

        self.logger = logging.getLogger("osu!")

        if not version:
            # Fetch latest client version
            self.version = self.fetch_version(stream)

            if not self.version:
                # Failed to get version
                exit(1)
        else:
            # Custom client version was set
            self.version = f"b{self.version}"

            if self.tourney:
                self.version = f"{self.version}tourney"

        self.session = requests.Session()
        self.session.headers = {"User-Agent": "osu!", "osu-version": self.version}

        self.logger.name = f"osu!-{self.version}"

        from .bancho import BanchoClient, Packets
        from .events import EventHandler
        from .api import WebAPI

        self.packets = copy(Packets)
        self.events = EventHandler()
        self.bancho = BanchoClient(self)
        self.api = WebAPI(self)

        if events:
            self.events.handlers = events

        if not (updates := self.api.check_updates()):
            # Updates are required because of the executable hash
            # TODO: Custom executable hash?
            exit(1)

        self.client = ClientInfo(self.version, updates)

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

    def run(self, retry=False, exit_on_interrupt=False) -> None:
        if retry:
            # Reinitialize game
            self.__init__(
                self.username,
                self.password,
                self.server,
                self.stream,
                self.version_number,
                self.tourney,
                self.events.handlers,
            )

        try:
            if not retry:
                self.api.get_session()
                self.api.get_backgrounds()

            if not self.api.connect(retry):
                exit(1)

            self.bancho.run()

        except KeyboardInterrupt:
            pass

        except Exception as e:
            traceback.print_exc()
            self.logger.fatal(f"Unhandled exception: {e}")

        finally:
            self.logger.warning("Exiting...")
            self.bancho.exit()

        if exit_on_interrupt:
            exit(0)

    def fetch_version(self, stream: str = "stable40") -> Optional[str]:
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
