from typing import List, Set, Iterator, Optional
from collections.abc import Iterator

from ..bancho.constants import ClientPackets, PresenceFilter
from ..game import Game

from .lists import LockedSet

from .channel import Channel
from .player import Player


class Players(LockedSet[Player]):
    def __init__(self, game: Game) -> None:
        self.game = game
        super().__init__()

    def __iter__(self) -> Iterator[Player]:
        return super().__iter__()

    @property
    def ids(self) -> Set[int]:
        return {p.id for p in self}

    @property
    def pending(self) -> List[Player]:
        return [p for p in self if not p.name]

    def add(self, player: Player) -> None:
        """Add a player to the collection"""
        return super().add(player)

    def remove(self, player: Player) -> None:
        """Remove a player from the collection"""
        if player in self:
            return super().remove(player)

    def by_id(self, id: int) -> Optional[Player]:
        """Get a player by id"""
        for p in self.copy():
            if p.id == id:
                return p
        return None

    def by_name(self, name: str) -> Optional[Player]:
        """Get a player by name"""
        for p in self.copy():
            if p.name == name:
                return p
        return None

    def load(self):
        # Split players into chunks of 255
        player_chunks = [
            self.pending[i : i + 255] for i in range(0, len(self.pending), 255)
        ]

        for chunk in player_chunks:
            self.game.bancho.request_presence([p.id for p in chunk])

    def request_updates(self, filter=PresenceFilter.All):
        """Change your presence filter and request updates from all players"""
        self.game.bancho.enqueue(
            ClientPackets.RECEIVE_UPDATES, int(filter.value).to_bytes(4, "little")
        )


class Channels(LockedSet[Channel]):
    def __iter__(self) -> Iterator[Channel]:
        return super().__iter__()

    @property
    def joined(self) -> List[Channel]:
        return [c for c in self if c.joined]

    def add(self, channel: Channel) -> None:
        """Add a channel to the collection"""
        return super().add(channel)

    def remove(self, channel: Channel) -> None:
        """Remove a channel to the collection"""
        if channel in self:
            return super().remove(channel)

    def get(self, name: str) -> Optional[Channel]:
        """Get a channel by name"""
        for c in self.copy():
            if c.name == name:
                return c
        return None
