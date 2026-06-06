from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..bancho.constants import (
    ClientPackets,
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
    from .player import Player
    from .replays import ScoreFrame


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
    slots: list[MatchSlot] = field(default_factory=list)
    host_id: int = 0
    mode: Mode = Mode.Osu
    scoring_type: MatchScoringType = MatchScoringType.Score
    team_type: MatchTeamType = MatchTeamType.HeadToHead
    freemod: bool = False
    seed: int = 0
    game: "Game | None" = None

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
    def host_slot(self) -> MatchSlot | None:
        for slot in self.slots:
            if slot.player_id == self.host_id:
                return slot
        return None

    @property
    def own_slot(self) -> MatchSlot | None:
        if not self.game:
            return None

        user_id = self.game.bancho.user_id

        for slot in self.slots:
            if slot.player_id == user_id:
                return slot

        return None

    @property
    def used_slots(self) -> list[MatchSlot]:
        return [slot for slot in self.slots if slot.has_player]

    @property
    def open_slots(self) -> list[MatchSlot]:
        return [slot for slot in self.slots if slot.status == SlotStatus.Open]

    @property
    def ready_slots(self) -> list[MatchSlot]:
        return [slot for slot in self.slots if slot.status == SlotStatus.Ready]

    @property
    def playing_slots(self) -> list[MatchSlot]:
        return [slot for slot in self.slots if slot.status & SlotStatus.Playing]

    def normalize_slots(self) -> None:
        if len(self.slots) > MATCH_SLOT_COUNT:
            self.slots = self.slots[:MATCH_SLOT_COUNT]

        while len(self.slots) < MATCH_SLOT_COUNT:
            self.slots.append(MatchSlot())

    def join(self, password: str = "") -> None:
        """Join this multiplayer match"""
        if not self.game:
            return

        self.game.bancho.join_match(self, password)

    def leave(self) -> None:
        """Leave this multiplayer match"""
        if not self.game:
            return

        self.game.bancho.leave_match()

    def change_slot(self, slot_id: int) -> None:
        """Change your slot in this multiplayer match"""
        self._enqueue_slot(ClientPackets.MATCH_CHANGE_SLOT, slot_id)

    def lock_slot(self, slot_id: int) -> None:
        """Toggle the lock status for a slot in this multiplayer match"""
        self._enqueue_slot(ClientPackets.MATCH_LOCK, slot_id)

    def ready(self) -> None:
        """Mark yourself as ready in this multiplayer match"""
        self._enqueue(ClientPackets.MATCH_READY)

    def not_ready(self) -> None:
        """Mark yourself as not ready in this multiplayer match"""
        self._enqueue(ClientPackets.MATCH_NOT_READY)

    def change_settings(self) -> None:
        """Change this multiplayer match's settings"""
        self._enqueue(ClientPackets.MATCH_CHANGE_SETTINGS, self.encode())

    def change_mods(self, mods: Mods) -> None:
        """Change your mods in this multiplayer match"""
        self.mods = mods

        if self.freemod and self.own_slot:
            self.own_slot.mods = mods

        stream = StreamOut()
        stream.u32(mods.value)

        self._enqueue(ClientPackets.MATCH_CHANGE_MODS, stream.get())

    def change_password(self, password: str) -> None:
        """Change this multiplayer match's password"""
        self.password = password
        self._enqueue(ClientPackets.MATCH_CHANGE_PASSWORD, self.encode())

    def start(self) -> None:
        """Start this multiplayer match"""
        self._enqueue(ClientPackets.MATCH_START)

    def load_complete(self) -> None:
        """Signal that you finished loading the beatmap"""
        self._enqueue(ClientPackets.MATCH_LOAD_COMPLETE)

    def no_beatmap(self) -> None:
        """Signal that you don't have this match's beatmap"""
        self._enqueue(ClientPackets.MATCH_NO_BEATMAP)

    def has_beatmap(self) -> None:
        """Signal that you have this match's beatmap"""
        self._enqueue(ClientPackets.MATCH_HAS_BEATMAP)

    def send_score(self, score_frame: "ScoreFrame") -> None:
        """Send a score update for this multiplayer match"""
        self._enqueue(ClientPackets.MATCH_SCORE_UPDATE, score_frame.encode())

    def complete(self) -> None:
        """Signal that you finished playing"""
        self._enqueue(ClientPackets.MATCH_COMPLETE)

    def fail(self) -> None:
        """Signal that you failed while playing"""
        self._enqueue(ClientPackets.MATCH_FAILED)

    def skip(self) -> None:
        """Request to skip the beatmap intro"""
        self._enqueue(ClientPackets.MATCH_SKIP_REQUEST)

    def transfer_host(self, slot_id: int) -> None:
        """Transfer host to another slot"""
        self._enqueue_slot(ClientPackets.MATCH_TRANSFER_HOST, slot_id)

    def change_team(self) -> None:
        """Change your team in this multiplayer match"""
        self._enqueue(ClientPackets.MATCH_CHANGE_TEAM)

    def invite(self, player: "Player | int") -> None:
        """Invite a player to this multiplayer match"""
        stream = StreamOut()
        stream.s32(player if isinstance(player, int) else player.id)

        self._enqueue(ClientPackets.MATCH_INVITE, stream.get())

    def _enqueue(self, packet: ClientPackets, data: bytes = b"") -> None:
        if not self.game:
            return

        self.game.bancho.enqueue(packet, data)

    def _enqueue_slot(self, packet: ClientPackets, slot_id: int) -> None:
        if slot_id < 0 or slot_id >= MATCH_SLOT_COUNT:
            if self.game:
                self.game.logger.warning(f"Invalid multiplayer slot: {slot_id}")
            return

        stream = StreamOut()
        stream.s32(slot_id)

        self._enqueue(packet, stream.get())

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
    def decode(cls, stream: StreamIn, game: "Game | None" = None) -> "Match":
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
            MatchSlot(status=SlotStatus(stream.u8())) for _ in range(MATCH_SLOT_COUNT)
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
