from typing import Set, Optional, TYPE_CHECKING

from ..bancho.constants import ClientPackets, CountryCodes, LevelGraph, Privileges, Mode
from ..bancho.streams import StreamOut

from .status import Status

if TYPE_CHECKING:
    from ..game import Game

import logging


class Player:
    def __init__(self, id: int, name: str = "", game: Optional["Game"] = None) -> None:
        self.id = id
        self.name = name
        self.game = game

        self.timezone = 0
        self.country_code = 0
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
        self.logger.disabled = game.logger.disabled

    def __repr__(self) -> str:
        return f'<Player "{self.name}" ({self.id})>'

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: object) -> bool:
        return self.id == other.id

    @property
    def mode(self) -> Mode:
        return self.status.mode

    @mode.setter
    def mode(self, value: Mode):
        self.status.mode = value

    @property
    def loaded(self) -> bool:
        return bool(self.name)

    @property
    def country(self) -> str:
        return list(CountryCodes.keys())[self.country_code]

    @property
    def level(self) -> int:
        if self.tscore <= 0:
            return 1

        if self.tscore >= LevelGraph[-1]:
            return 100 + int((self.tscore - LevelGraph[99]) / 100000000000)

        for idx, v in enumerate(LevelGraph, start=0):
            if v > self.tscore:
                return idx

        return 1

    def request_presence(self) -> None:
        """Request a presence update for this player"""
        self.game.bancho.request_presence([self.id])

    def request_stats(self) -> None:
        """Request a stats update for this player"""
        self.game.bancho.request_stats([self.id])

    def avatar(self) -> Optional[bytes]:
        """Get the avatar for this player"""
        return self.game.api.get_avatar(self.id)

    def send_message(self, message: str) -> None:
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

        if not self.game.disable_chat:
            self.logger.info(
                f'<{player.name}{f" ({player.id})" if player.id else ""}> [{self.name}]: "{message}"'
            )

        self.game.bancho.enqueue(ClientPackets.SEND_PRIVATE_MESSAGE, stream.get())

    def add_friend(self) -> None:
        """Add this player to the friends list"""
        if self.id in self.game.bancho.friends:
            self.game.logger.warning(
                f"Tried to add friend, but you are already friends with {self.name}."
            )
            return

        self.game.logger.info(f"You are now friends with {self.name}.")

        self.game.bancho.friends.add(self.id)
        self.game.bancho.enqueue(
            ClientPackets.FRIEND_ADD, int(self.id).to_bytes(4, "little")
        )

    def remove_friend(self) -> None:
        """Remove this player from the friends list"""
        if self.id not in self.game.bancho.friends:
            self.game.logger.warning(
                f"Tried to remove friend, but you are not friends with {self.name}."
            )
            return

        self.game.logger.info(f"You are no longer friends with {self.name}.")

        self.game.bancho.friends.remove(self.id)
        self.game.bancho.enqueue(
            ClientPackets.FRIEND_REMOVE, int(self.id).to_bytes(4, "little")
        )
