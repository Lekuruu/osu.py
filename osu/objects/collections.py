
from typing import List, Set, Iterator, Optional
from collections.abc import Iterator

from .channel import Channel
from .player import Player

class Players(Set[Player]):
    def __iter__(self) -> Iterator[Player]:
        return super().__iter__()
    
    @property
    def ids(self) -> Set[int]:
        return {p.id for p in self}
    
    def add(self, player: Player) -> None:
        return super().add(player)
    
    def remove(self, player: Player) -> None:
        if player in self: return super().remove(player)

    def by_id(self, id: int) -> Optional[Player]:
        for p in self:
            if p.id == id:
                return p
        return None

    def by_name(self, name: str) -> Optional[Player]:
        for p in self:
            if p.name == name:
                return p
        return None

class Channel(Set[Channel]):
    def __iter__(self) -> Iterator[Channel]:
        return super().__iter__()

    @property
    def joined(self) -> List[Channel]:
        return [c for c in self if c.joined]

    def add(self, channel: Channel) -> None:
        return super().add(channel)
    
    def remove(self, channel: Channel) -> None:
        if channel in self: return super().remove(channel)

    def get(self, name: str) -> Optional[Channel]:
        for c in self:
            if c.name == name:
                return c
        return None
