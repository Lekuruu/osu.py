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
from ..bancho.streams import StreamIn, StreamOut

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

    def encode(self) -> bytes:
        self.normalize_slots()

        stream = StreamOut()
        stream.s16(self.id)
        stream.bool(self.in_progress)
        stream.u8(self.match_type.value)
        stream.u32(self.mods.value)
        stream.string(self.name)
        stream.string(self.password)
        stream.string(self.beatmap_text)
        stream.s32(self.beatmap_id)
        stream.string(self.beatmap_checksum)

        for slot in self.slots:
            stream.u8(slot.status.value)

        for slot in self.slots:
            stream.u8(slot.team.value)

        for slot in self.slots:
            if slot.has_player:
                stream.s32(slot.player_id)

        stream.s32(self.host_id)
        stream.u8(self.mode.value)
        stream.u8(self.scoring_type.value)
        stream.u8(self.team_type.value)
        stream.bool(self.freemod)

        if self.freemod:
            for slot in self.slots:
                stream.s32(slot.mods.value)

        stream.s32(self.seed)
        return stream.get()

    @classmethod
    def decode(cls, stream: StreamIn, game: Optional["Game"] = None) -> "Match":
        match = Match(
            id=stream.s16(),
            in_progress=stream.bool(),
            match_type=MatchType(stream.u8()),
            mods=Mods(stream.u32()),
            name=stream.string(),
            password=stream.string(),
            beatmap_text=stream.string(),
            beatmap_id=stream.s32(),
            beatmap_checksum=stream.string(),
            game=game,
        )

        match.slots = [
            MatchSlot(status=SlotStatus(stream.u8()))
            for _ in range(MATCH_SLOT_COUNT)
        ]

        for slot in match.slots:
            slot.team = SlotTeam(stream.u8())

        for slot in match.slots:
            if slot.has_player:
                slot.player_id = stream.s32()

        match.host_id = stream.s32()
        match.mode = Mode(max(0, min(3, stream.u8())))
        match.scoring_type = MatchScoringType(stream.u8())
        match.team_type = MatchTeamType(stream.u8())
        match.freemod = stream.bool()

        if match.freemod:
            for slot in match.slots:
                slot.mods = Mods(stream.s32())

        match.seed = stream.s32()
        return match
