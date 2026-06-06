from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..bancho.constants import ClientPackets, PresenceFilter

from .lists import LockedSet
from .channel import Channel
from .match import Match
from .player import Player

if TYPE_CHECKING:
    from ..game import Game


class Players(LockedSet[Player]):
    def __init__(self, game: "Game") -> None:
        self.game = game
        super().__init__()

    def __iter__(self) -> Iterator[Player]:
        return super().__iter__()

    @property
    def ids(self) -> set[int]:
        return {p.id for p in self}

    @property
    def pending(self) -> list[Player]:
        return [p for p in self if not p.name]

    def add(self, item: Player) -> None:
        """Add a player to the collection"""
        return super().add(item)

    def remove(self, item: Player) -> None:
        """Remove a player from the collection"""
        if item in self:
            return super().remove(item)

    def by_id(self, id: int) -> Player | None:
        """Get a player by id"""
        for p in self.snapshot_list():
            if p.id == id:
                return p
        return None

    def by_name(self, name: str) -> Player | None:
        """Get a player by name"""
        for p in self.snapshot_list():
            if p.name == name:
                return p
        return None

    def load(self) -> None:
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
    def joined(self) -> list[Channel]:
        return [c for c in self if c.joined]

    def add(self, item: Channel) -> None:
        """Add a channel to the collection"""
        return super().add(item)

    def remove(self, item: Channel) -> None:
        """Remove a channel to the collection"""
        if item in self:
            return super().remove(item)

    def get(self, name: str) -> Channel | None:
        """Get a channel by name"""
        for c in self.snapshot_list():
            if c.name == name:
                return c
        return None


class Matches(LockedSet[Match]):
    def __init__(self, game: "Game") -> None:
        self.game = game
        super().__init__()

    def __iter__(self) -> Iterator[Match]:
        return super().__iter__()

    def add(self, item: Match) -> None:
        """Add a match to the collection"""
        if existing := self.by_id(item.id):
            super().remove(existing)

        item.game = self.game
        return super().add(item)

    def remove(self, item: Match) -> None:
        """Remove a match from the collection"""
        if item in self:
            return super().remove(item)

    def by_id(self, id: int) -> Match | None:
        """Get a match by id"""
        for match in self.snapshot_list():
            if match.id == id:
                return match
        return None
