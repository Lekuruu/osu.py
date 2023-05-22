
from typing import Set, Iterator, Optional

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
