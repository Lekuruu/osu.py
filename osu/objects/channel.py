from typing import Optional, TYPE_CHECKING

from ..bancho.constants import ClientPackets
from ..bancho.streams import StreamOut

if TYPE_CHECKING:
    from ..game import Game

import logging


class Channel:
    def __init__(self, name: str, game: "Game", topic: Optional[str] = None) -> None:
        self.name = name
        self.topic = topic
        self.game = game
        self.user_count = 0

        self.joined = False
        self.joining = False

        self.logger = logging.getLogger(self.name)
        self.logger.disabled = game.logger.disabled

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return self.name == other.name

    def join(self) -> None:
        """Join this channel"""
        if self.joined:
            return

        self.joining = True
        self.logger.info("Attempting to join channel...")

        stream = StreamOut()
        stream.string(self.name)

        self.game.bancho.enqueue(ClientPackets.CHANNEL_JOIN, stream.get())

    def leave(self) -> None:
        """Leave this channel"""
        if not self.joined:
            return

        self.joining = False
        self.joined = False

        stream = StreamOut()
        stream.string(self.name)

        self.game.bancho.enqueue(ClientPackets.CHANNEL_PART, stream.get())

    def join_success(self) -> None:
        """Will be called by the server, when you successfully joined a channel"""
        if not self.joined:
            self.logger.info(f"Joined {self.name}!")

        self.joining = False
        self.joined = True

        if self.name == "#osu":
            # Load players
            self.game.bancho.players.load()

    def send_message(self, message: str, force=False) -> None:
        """Send a message inside this channel

        Args:
            message (str): Your message
            force (bool, optional): Sends the message, even if you haven't joined this channel yet
        """
        if not self.joined and not force:
            return

        if not (player := self.game.bancho.player):
            return

        if not self.game.disable_chat:
            self.logger.info(
                f'<{player.name}{f" ({player.id})" if player.id else ""}> [{self.name}]: "{message}"'
            )

        stream = StreamOut()
        stream.string(player.name)
        stream.string(message)
        stream.string(self.name)
        stream.s32(player.id)

        self.game.bancho.enqueue(ClientPackets.SEND_PUBLIC_MESSAGE, stream.get())
