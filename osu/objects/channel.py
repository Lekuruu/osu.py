from ..bancho.constants import ClientPackets
from ..bancho.streams import StreamOut
from ..game import Game

from typing import Optional

import logging


class Channel:
    def __init__(self, name: str, game: Game, topic: Optional[str] = None) -> None:
        self.name = name
        self.topic = topic
        self.game = game
        self.user_count = 0

        self.joined = False
        self.joining = False

        self.logger = logging.getLogger(self.name)

    def __hash__(self) -> int:
        return int(self.name.encode().hex(), 16)

    def __eq__(self, other: object) -> bool:
        return self.name == other.name

    def join(self):
        if self.joined:
            return

        self.joining = True
        self.logger.info("Attempting to join channel...")

        stream = StreamOut()
        stream.string(self.name)

        self.game.bancho.enqueue(ClientPackets.CHANNEL_JOIN, stream.get())

    def leave(self):
        if not self.joined:
            return

        self.joining = False
        self.joined = False

        stream = StreamOut()
        stream.string(self.name)

        self.game.bancho.enqueue(ClientPackets.CHANNEL_PART, stream.get())

    def join_success(self):
        self.joining = False
        self.joined = True

        self.logger.info(f"Joined {self.name}!")

        if self.name == "#osu":
            # Load players
            self.game.bancho.players.load()

    def send_message(self, message: str, force=False):
        if not self.joined and not force:
            return

        if not (player := self.game.bancho.player):
            return

        self.logger.info(
            f'<{player.name}{f" ({player.id})" if player.id else ""}> [{self.name}]: "{message}"'
        )

        stream = StreamOut()
        stream.string(player.name)
        stream.string(message)
        stream.string(self.name)
        stream.s32(player.id)

        self.game.bancho.enqueue(ClientPackets.SEND_PUBLIC_MESSAGE, stream.get())
