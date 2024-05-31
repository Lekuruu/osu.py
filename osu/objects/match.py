from dataclasses import dataclass
from typing import List

from .player import Player
from ..game import Game
from ..bancho.streams import StreamOut
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


@dataclass(slots=True)
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
        self, game: Game, host: Player, password: str = "", amount_slots: int = 16
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
        cls, game: Game, host: Player, password: str = "", amount_slots: int = 16
    ) -> "Match":
        match = cls(game, host, password, amount_slots)
        game.bancho.enqueue(ClientPackets.CREATE_MATCH, match.serialize())
        return match

    def serialize(self) -> bytes:
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