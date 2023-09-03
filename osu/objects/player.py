from typing import Set, List, Optional

from .status import Status
from ..game import Game

from ..bancho.streams import StreamOut
from ..bancho.constants import ClientPackets, Privileges, Mode

import logging


class Player:
    def __init__(self, id: int, name: str = "", game: Optional[Game] = None) -> None:
        self.id = id
        self.name = name
        self.game = game

        self.timezone = 0
        self.country_code = 0
        self.mode = Mode.Osu
        self.longitude = 0.0
        self.latitude = 0.0

        self.status = Status()
        self.rscore = 0
        self.acc = 100.0
        self.playcount = 0
        self.tscore = 0
        self.rank = 0
        self.pp = 0

        self.privileges: Privileges = Privileges.Normal
        self.spectators: Set[Player] = set()

        self.cant_spectate = False
        self.silenced = False
        self.dms_blocked = False

        self.last_status = Status()

        self.logger = logging.getLogger(self.name)

    def __repr__(self) -> str:
        return f'<Player "{self.name}" ({self.id})>'

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: object) -> bool:
        return self.id == other.id

    @property
    def loaded(self) -> bool:
        return bool(self.name)

    def request_presence(self):
        self.game.bancho.request_presence([self.id])

    def request_stats(self):
        self.game.bancho.request_stats([self.id])

    def avatar(self) -> Optional[bytes]:
        return self.game.api.get_avatar(self.id)

    def send_message(self, message: str):
        """Send a PM to this player"""

        if not (player := self.game.bancho.player):
            return

        if not self.loaded:
            # Presence missing
            self.request_presence()

        stream = StreamOut()
        stream.string(player.name)
        stream.string(message)
        stream.string(self.name)
        stream.s32(player.id)

        self.logger.info(
            f'<{player.name}{f" ({player.id})" if player.id else ""}> [{self.name}]: "{message}"'
        )

        self.game.bancho.enqueue(ClientPackets.SEND_PRIVATE_MESSAGE, stream.get())

    def add_friend(self):
        if self.id in self.game.bancho.friends:
            self.game.logger.warning(
                f"Tried to add friend, but you are already friends with {self.name}."
            )
            return

        self.game.logger.info(f"You are now friends with {self.name}.")

        self.game.bancho.enqueue(
            ClientPackets.FRIEND_ADD, int(self.id).to_bytes(4, "little")
        )

    def remove_friend(self):
        if self.id not in self.game.bancho.friends:
            self.game.logger.warning(
                f"Tried to remove friend, but you are not friends with {self.name}."
            )
            return

        self.game.logger.info(f"You are no longer friends with {self.name}.")

        self.game.bancho.enqueue(
            ClientPackets.FRIEND_REMOVE, int(self.id).to_bytes(4, "little")
        )
