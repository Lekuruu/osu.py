from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from ..bancho.constants import (
    MatchScoringType,
    MatchTeamType,
    MatchType,
    Mode,
    Mods,
    SlotStatus,
    SlotTeam,
)

if TYPE_CHECKING:
    from ..game import Game


MATCH_SLOT_COUNT = 16


@dataclass
class MatchSlot:
    status: SlotStatus = SlotStatus.Open
    team: SlotTeam = SlotTeam.Neutral
    player_id: int = -1
    mods: Mods = Mods.NoMod

    @property
    def has_player(self) -> bool:
        return bool(self.status & SlotStatus.HasPlayer)


@dataclass
class Match:
    id: int = 0
    in_progress: bool = False
    match_type: MatchType = MatchType.Standard
    mods: Mods = Mods.NoMod
    name: str = ""
    password: str = ""
    beatmap_text: str = ""
    beatmap_id: int = -1
    beatmap_checksum: str = ""
    slots: List[MatchSlot] = field(default_factory=list)
    host_id: int = 0
    mode: Mode = Mode.Osu
    scoring_type: MatchScoringType = MatchScoringType.Score
    team_type: MatchTeamType = MatchTeamType.HeadToHead
    freemod: bool = False
    seed: int = 0
    game: Optional["Game"] = None

    def __post_init__(self) -> None:
        self.normalize_slots()

    def __repr__(self) -> str:
        return f'<Match "{self.name}" ({self.id})>'

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Match) and self.id == other.id

    @property
    def password_required(self) -> bool:
        return bool(self.password)

    @property
    def channel_name(self) -> str:
        return f"#multi_{self.id}"

    @property
    def host_slot(self) -> Optional[MatchSlot]:
        for slot in self.slots:
            if slot.player_id == self.host_id:
                return slot
        return None

    @property
    def own_slot(self) -> Optional[MatchSlot]:
        if not self.game:
            return None

        user_id = self.game.bancho.user_id

        for slot in self.slots:
            if slot.player_id == user_id:
                return slot

        return None

    @property
    def used_slots(self) -> List[MatchSlot]:
        return [slot for slot in self.slots if slot.has_player]

    @property
    def open_slots(self) -> List[MatchSlot]:
        return [slot for slot in self.slots if slot.status == SlotStatus.Open]

    @property
    def ready_slots(self) -> List[MatchSlot]:
        return [slot for slot in self.slots if slot.status == SlotStatus.Ready]

    @property
    def playing_slots(self) -> List[MatchSlot]:
        return [slot for slot in self.slots if slot.status & SlotStatus.Playing]

    def normalize_slots(self) -> None:
        if len(self.slots) > MATCH_SLOT_COUNT:
            self.slots = self.slots[:MATCH_SLOT_COUNT]

        while len(self.slots) < MATCH_SLOT_COUNT:
            self.slots.append(MatchSlot())
