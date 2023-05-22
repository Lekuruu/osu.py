
from typing import Set, List

from ..bancho.constants import (
    Privileges,
    Mode
)

from .status import Status

class Player:
    def __init__(self, id: int, name: str = "") -> None:
        self.id = id
        self.name = name

        self.timezone     = 0
        self.country_code = 0
        self.mode         = Mode.Osu
        self.longitude    = 0.0
        self.latitude     = 0.0

        self.status    = Status()
        self.rscore    = 0
        self.acc       = 100.0
        self.playcount = 0
        self.tscore    = 0
        self.rank      = 0
        self.pp        = 0

        self.privileges: List[Privileges] = []
        self.spectators: Set[Player] = set()

        self.cant_spectate = False
        self.silenced      = False
        self.dms_blocked   = False

        self.last_status = Status()

    def __repr__(self) -> str:
        return f'<Player "{self.name}" ({self.id})>'

    def __hash__(self) -> int:
        return self.id
    
    def __eq__(self, other: object) -> bool:
        return self.id == other.id