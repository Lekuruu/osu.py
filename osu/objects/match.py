from typing import List, TYPE_CHECKING
from dataclasses import dataclass

from .player import Player
from ..bancho.streams import StreamOut, StreamIn
from ..bancho.constants import (
    MatchScoringTypes,
    MatchTeamTypes,
    ClientPackets,
    SlotStatus,
    MatchType,
    SlotTeam,
    Mods,
    Mode,
)

if TYPE_CHECKING:
    from ..game import Game


@dataclass
class Slot:
    player_id: int = -1
    status: SlotStatus = SlotStatus.Locked
    team: SlotTeam = SlotTeam.Neutral
    mods: Mods = Mods.NoMod

    @property
    def has_player(self) -> bool:
        return SlotStatus.HasPlayer & self.status > 0

    @property
    def is_open(self) -> bool:
        return self.status == SlotStatus.Open

    @property
    def is_ready(self) -> bool:
        return self.status == SlotStatus.Ready


class Match:
    def __init__(
        self, game: "Game", host: Player, password: str = "", amount_slots: int = 16
    ) -> None:
        self.id: int = 0
        self.name: str = f"{host.name}'s Game"
        self.password: str = password
        self.host = host
        self.game = game

        self.freemod: bool = False
        self.in_progress: bool = False
        self.type: MatchType = MatchType.Standard
        self.mods: Mods = Mods.NoMod
        self.mode: Mode = Mode.Osu
        self.scoring_type: MatchScoringTypes = MatchScoringTypes.Score
        self.team_type: MatchTeamTypes = MatchTeamTypes.HeadToHead

        self.beatmap_text: str = ""
        self.beatmap_id: int = -1
        self.beatmap_checksum: str = ""

        self.slots: List[Slot] = [Slot() for _ in range(amount_slots)]
        self.seed: int = 0

    @classmethod
    def create(
        cls, game: "Game", host: Player, password: str = "", amount_slots: int = 16
    ) -> "Match":
        match = cls(game, host, password, amount_slots)
        game.bancho.enqueue(ClientPackets.CREATE_MATCH, match.encode())
        return match

    @classmethod
    def decode(cls, stream: StreamIn, game: "Game", amount_slots: int = 16) -> "Match":
        match = cls(game, game.bancho.player)
        match.id = stream.u16()

        match.in_progress = stream.bool()
        match.type = MatchType(stream.u8())
        match.mods = Mods(stream.u32())

        match.name = stream.string()
        match.password = stream.string()

        match.beatmap_text = stream.string()
        match.beatmap_id = stream.s32()
        match.beatmap_checksum = stream.string()

        slot_status = [SlotStatus(stream.u8()) for _ in range(amount_slots)]
        slot_team = [SlotTeam(stream.u8()) for _ in range(amount_slots)]
        slot_id = [
            stream.s32() if (slot_status[i] & SlotStatus.HasPlayer) > 0 else -1
            for i in range(len(slot_status))
        ]

        match.host = game.bancho.players.by_id(stream.s32())
        match.mode = Mode(stream.u8())

        match.scoring_type = MatchScoringTypes(stream.u8())
        match.team_type = MatchTeamTypes(stream.u8())

        match.freemod = stream.bool()
        slot_mods = [Mods.NoMod for _ in range(amount_slots)]

        if match.freemod:
            slot_mods = [Mods(stream.u32()) for _ in range(amount_slots)]

        match.slots = [
            Slot(slot_id[i], slot_status[i], slot_team[i], slot_mods[i])
            for i in range(amount_slots)
        ]

        match.seed = stream.s32()
        return match

    def encode(self) -> bytes:
        stream = StreamOut()
        stream.u16(self.id)

        stream.bool(self.in_progress)
        stream.u8(self.type.value)
        stream.u32(self.mods.value)

        stream.string(self.name)
        stream.string(self.password)
        stream.string(self.beatmap_text)
        stream.s32(self.beatmap_id)
        stream.string(self.beatmap_checksum)

        [stream.u8(slot.status.value) for slot in self.slots]
        [stream.u8(slot.team.value) for slot in self.slots]
        [stream.s32(slot.player_id) for slot in self.slots if slot.has_player]

        stream.s32(self.host.id)
        stream.u8(self.mode.value)
        stream.u8(self.scoring_type.value)
        stream.u8(self.team_type.value)

        stream.bool(self.freemod)

        if self.freemod:
            [stream.s32(slot.mods.value) for slot in self.slots]

        stream.s32(self.seed)
        return stream.get()

    def update_from_match(self, match: "Match") -> "Match":
        self.id = match.id
        self.in_progress = match.in_progress
        self.type = match.type
        self.mods = match.mods
        self.name = match.name
        self.password = match.password
        self.beatmap_text = match.beatmap_text
        self.beatmap_id = match.beatmap_id
        self.beatmap_checksum = match.beatmap_checksum
        self.host = match.host
        self.mode = match.mode
        self.scoring_type = match.scoring_type
        self.team_type = match.team_type
        self.freemod = match.freemod
        self.slots = match.slots
        self.seed = match.seed
        return self
