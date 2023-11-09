from ..bancho.constants import Mods, Mode

from enum import IntEnum, Enum


class RankingType(IntEnum):
    Top = 1
    SelectedMod = 2
    Friends = 3
    Country = 4


class SubmissionStatus(IntEnum):
    Unknown = 0
    NotSubmitted = 1
    Pending = 2
    EditableCutoff = 3
    Ranked = 4
    Approved = 5
    Qualified = 6


class CommentTarget(str, Enum):
    Map = "map"
    Song = "song"
    Replay = "replay"


class DisplayMode(IntEnum):
    Ranked = 0
    # TODO: 1
    Pending = 2
    Qualified = 3
    All = 4
    Graveyard = 5
    # TODO: 6
    RankedPlayed = 7


class ModeSelect(IntEnum):
    All = -1
    Osu = 0
    Taiko = 1
    CatchTheBeat = 2
    OsuMania = 3
