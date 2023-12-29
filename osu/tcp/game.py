from typing import Optional, Callable, Dict, List
from datetime import datetime
from copy import copy

from ..bancho.constants import ServerPackets
from ..objects.client import ClientInfo
from ..tasks import Task

import requests
import hashlib
import logging


class TcpGame:

    """osu! game client (tcp)
    --------------------
    This class is a modified version of the "Game" class, that uses the TCP protocol instead of the HTTP protocol.
    Please don't use this class unless you know what you're doing.
    """

    def __init__(
        self,
        username: str,
        password: str,
        server: str,
        version: int,
        executable_hash: str,
        bancho_ip: str,
        bancho_port: int = 13381,
        tournament: bool = False,
        events: Optional[Dict[ServerPackets, List[Callable]]] = {},
        tasks: Optional[List[Task]] = [],
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
            The server to connect to (e.g. `ppy.sh`)

        `version`: int/float
            Set a custom version
            (b20130815 is the latest known version to work with this protocol)

        `executable_hash`: str
            The hash of your osu!.exe file

        `bancho_ip`: str
            The ip of the bancho server

        `bancho_port`: int
            The port of the bancho server (default: 13381)

        `tournament`: bool
            This allows for multiple clients at the same time (supporter only)

        `events`: dict, optional
            Allows to pass in events, instead of registering them normally

        `tasks`: list, optional
            Allows to pass in pre-defined tasks, just like the `events` parameter

        `disable_logging`: bool
            Disable the logging
        """

        self.username = username
        self.password = password
        self.server = server
        self.version = version
        self.tourney = tournament
        self.disable_chat = disable_chat_logging

        self.version_number = version

        self.logger = logging.getLogger("osu!")
        self.logger.disabled = disable_logging

        self.version = f"b{self.version}"

        if self.tourney:
            self.version = f"{self.version}tourney"

        self.session = requests.Session()
        self.session.headers = {"User-Agent": "osu!", "osu-version": self.version}

        self.logger.name = f"osu!-{self.version}"

        from .bancho import TcpBanchoClient, Packets
        from ..events import EventHandler
        from ..tasks import TaskManager
        from ..api import WebAPI

        self.packets = copy(Packets)
        self.events = EventHandler()
        self.bancho = TcpBanchoClient(self, bancho_ip, bancho_port)
        self.tasks = TaskManager(self)
        self.api = WebAPI(self)

        if events:
            self.events.handlers = events

        if tasks:
            self.tasks.tasks = tasks

        self.client = ClientInfo(self.version, executable_hash)

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
                self.version_number,
                self.client.hash,
                self.bancho.ip,
                self.bancho.port,
                self.tourney,
                self.events.handlers,
                self.tasks.tasks,
                self.logger.disabled,
            )

        try:
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
