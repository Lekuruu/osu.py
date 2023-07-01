from enum import IntEnum, Enum
from typing import List


class ClientPackets(IntEnum):
    CHANGE_ACTION = 0
    SEND_PUBLIC_MESSAGE = 1
    LOGOUT = 2
    REQUEST_STATUS_UPDATE = 3
    PING = 4
    START_SPECTATING = 16
    STOP_SPECTATING = 17
    SPECTATE_FRAMES = 18
    ERROR_REPORT = 20
    CANT_SPECTATE = 21
    SEND_PRIVATE_MESSAGE = 25
    PART_LOBBY = 29
    JOIN_LOBBY = 30
    CREATE_MATCH = 31
    JOIN_MATCH = 32
    PART_MATCH = 33
    MATCH_CHANGE_SLOT = 38
    MATCH_READY = 39
    MATCH_LOCK = 40
    MATCH_CHANGE_SETTINGS = 41
    MATCH_START = 44
    MATCH_SCORE_UPDATE = 47
    MATCH_COMPLETE = 49
    MATCH_CHANGE_MODS = 51
    MATCH_LOAD_COMPLETE = 52
    MATCH_NO_BEATMAP = 54
    MATCH_NOT_READY = 55
    MATCH_FAILED = 56
    MATCH_HAS_BEATMAP = 59
    MATCH_SKIP_REQUEST = 60
    CHANNEL_JOIN = 63
    BEATMAP_INFO_REQUEST = 68
    MATCH_TRANSFER_HOST = 70
    FRIEND_ADD = 73
    FRIEND_REMOVE = 74
    MATCH_CHANGE_TEAM = 77
    CHANNEL_PART = 78
    RECEIVE_UPDATES = 79
    SET_AWAY_MESSAGE = 82
    IRC_ONLY = 84
    USER_STATS_REQUEST = 85
    MATCH_INVITE = 87
    MATCH_CHANGE_PASSWORD = 90
    TOURNAMENT_MATCH_INFO_REQUEST = 93
    USER_PRESENCE_REQUEST = 97
    USER_PRESENCE_REQUEST_ALL = 98
    TOGGLE_BLOCK_NON_FRIEND_DMS = 99
    TOURNAMENT_JOIN_MATCH_CHANNEL = 108
    TOURNAMENT_LEAVE_MATCH_CHANNEL = 109

    def __repr__(self) -> str:
        return f"<{self.name} ({self.value})>"


class ServerPackets(IntEnum):
    USER_ID = 5
    SEND_MESSAGE = 7
    PONG = 8
    HANDLE_IRC_CHANGE_USERNAME = 9  # unused
    HANDLE_IRC_QUIT = 10
    USER_STATS = 11
    USER_LOGOUT = 12
    SPECTATOR_JOINED = 13
    SPECTATOR_LEFT = 14
    SPECTATE_FRAMES = 15
    VERSION_UPDATE = 19
    SPECTATOR_CANT_SPECTATE = 22
    GET_ATTENTION = 23
    NOTIFICATION = 24
    UPDATE_MATCH = 26
    NEW_MATCH = 27
    DISPOSE_MATCH = 28
    TOGGLE_BLOCK_NON_FRIEND_DMS = 34
    MATCH_JOIN_SUCCESS = 36
    MATCH_JOIN_FAIL = 37
    FELLOW_SPECTATOR_JOINED = 42
    FELLOW_SPECTATOR_LEFT = 43
    ALL_PLAYERS_LOADED = 45
    MATCH_START = 46
    MATCH_SCORE_UPDATE = 48
    MATCH_TRANSFER_HOST = 50
    MATCH_ALL_PLAYERS_LOADED = 53
    MATCH_PLAYER_FAILED = 57
    MATCH_COMPLETE = 58
    MATCH_SKIP = 61
    UNAUTHORIZED = 62  # unused
    CHANNEL_JOIN_SUCCESS = 64
    CHANNEL_INFO = 65
    CHANNEL_KICK = 66
    CHANNEL_AUTO_JOIN = 67
    BEATMAP_INFO_REPLY = 69
    PRIVILEGES = 71
    FRIENDS_LIST = 72
    PROTOCOL_VERSION = 75
    MAIN_MENU_ICON = 76
    MONITOR = 80  # unused
    MATCH_PLAYER_SKIPPED = 81
    USER_PRESENCE = 83
    RESTART = 86
    MATCH_INVITE = 88
    CHANNEL_INFO_END = 89
    MATCH_CHANGE_PASSWORD = 91
    SILENCE_END = 92
    USER_SILENCED = 94
    USER_PRESENCE_SINGLE = 95
    USER_PRESENCE_BUNDLE = 96
    USER_DM_BLOCKED = 100
    TARGET_IS_SILENCED = 101
    VERSION_UPDATE_FORCED = 102
    SWITCH_SERVER = 103
    ACCOUNT_RESTRICTED = 104
    RTX = 105  # unused
    MATCH_ABORT = 106
    SWITCH_TOURNAMENT_SERVER = 107

    def __repr__(self) -> str:
        return f"<{self.name} ({self.value})>"


class LoginError(Enum):
    AUTHENTICATION_ERROR = -1
    UPDATE_NEEDED = -2
    RESTRICTED = -3
    NOT_ACTIVATED = -4
    SERVER_ERROR = -5
    NEED_SUPPORTER = -6
    PASSWORD_RESET = -7
    VERIFICATION_NEEDED = -8

    @property
    def description(self) -> str:
        return {
            LoginError.AUTHENTICATION_ERROR: "Authentication failed. Please check your username/password!",
            LoginError.UPDATE_NEEDED: "It seems like this version of osu! is too old. Please check for any updates!",
            LoginError.RESTRICTED: "You are banned.",
            LoginError.NOT_ACTIVATED: "Your account was either restricted or is not activated.",
            LoginError.SERVER_ERROR: "A server error occured.",
            LoginError.NEED_SUPPORTER: "You need to be a supporter to use tourney clients.",
            LoginError.PASSWORD_RESET: "Your account password has been reset.",
            LoginError.VERIFICATION_NEEDED: "",
        }[self]


class StatusAction(Enum):
    Idle = 0
    Afk = 1
    Playing = 2
    Editing = 3
    Modding = 4
    Multiplayer = 5
    Watching = 6
    Unknown = 7
    Testing = 8
    Submitting = 9
    Paused = 10
    Lobby = 11
    Multiplaying = 12
    OsuDirect = 13


class Mods(Enum):
    NoMods = 0
    NoFail = 1
    Easy = 2
    TouchDevice = 4
    Hidden = 8
    HardRock = 16
    SuddenDeath = 32
    DoubleTime = 64
    Relax = 128
    HalfTime = 256
    Nightcore = 512
    Flashlight = 1024
    Autoplay = 2048
    SpunOut = 4096
    Relax2 = 8192
    Perfect = 16384
    Key4 = 32768
    Key5 = 65536
    Key6 = 131072
    Key7 = 262144
    Key8 = 524288
    FadeIn = 1048576
    Random = 2097152
    Cinema = 4194304
    Target = 8388608
    Key9 = 16777216
    KeyCoop = 33554432
    Key1 = 67108864
    Key3 = 134217728
    Key2 = 268435456
    ScoreV2 = 536870912
    LastMod = 1073741824
    KeyMod = 521109504
    FreeModAllowed = 522171579
    ScoreIncreaseMods = 1049688

    @classmethod
    def pack(cls, values: List[Enum]):
        return sum([mod.value for mod in values])

    @classmethod
    def check_active(cls, values: int, mod: int):
        return (values & mod) > 0

    @classmethod
    def list(cls, values: int):
        return [mod for mod in Mods if cls.check_active(values, mod.value)]


class Privileges(Enum):
    Restriced = 0
    Normal = 1
    BAT = 2
    Supporter = 4
    Peppy = 8
    Admin = 16
    Tournament = 32

    @classmethod
    def pack(cls, values: List[Enum]):
        return sum([p.value for p in values])

    @classmethod
    def check_active(cls, values: int, p: int):
        return (values & p) > 0

    @classmethod
    def list(cls, values: int):
        return [p for p in Privileges if cls.check_active(values, p.value)]


class ButtonState(Enum):
    NoButtons = 0
    Left1 = 1
    Right1 = 2
    Left2 = 4
    Right2 = 8
    Smoke = 16

    @classmethod
    def pack(cls, values: List[Enum]):
        return sum([b.value for b in values])

    @classmethod
    def check_active(cls, values: int, b: int):
        return (values & b) > 0

    @classmethod
    def list(cls, values: int):
        return [b for b in ButtonState if cls.check_active(values, b.value)]


class Mode(Enum):
    Osu = 0
    Taiko = 1
    CatchTheBeat = 2
    OsuMania = 3


class ReplayAction(Enum):
    Standard = 0
    NewSong = 1
    Skip = 2
    Completion = 3
    Fail = 4
    Pause = 5
    Unpause = 6
    SongSelect = 7
    WatchingOther = 8


class PresenceFilter(Enum):
    NoPlayers = 0
    All = 1
    Friends = 2


class Grade(Enum):
    XH = 0
    SH = 1
    X = 2
    S = 3
    A = 4
    B = 5
    C = 6
    D = 7
    F = 8
    N = 9
