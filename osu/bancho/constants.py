from enum import IntEnum, Enum, IntFlag
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


LevelGraph = [
    0,
    30000,
    130000,
    340000,
    700000,
    1250000,
    2030000,
    3080000,
    4440000,
    6150000,
    8250000,
    10780000,
    13780000,
    17290000,
    21350000,
    26000000,
    31280000,
    37230000,
    43890000,
    51300000,
    59500000,
    68530000,
    78430000,
    89240000,
    101000000,
    113750000,
    127530000,
    142380000,
    158340000,
    175450000,
    193750000,
    213280000,
    234080000,
    256190000,
    279650000,
    304500000,
    330780000,
    358530000,
    387790000,
    418600000,
    451000000,
    485030000,
    520730000,
    558140000,
    597300000,
    638250000,
    681030000,
    725680000,
    772240000,
    820750000,
    871250000,
    923780000,
    978380000,
    1035090000,
    1093950000,
    1155000000,
    1218280000,
    1283830000,
    1351690001,
    1421900001,
    1494500002,
    1569530004,
    1647030007,
    1727040013,
    1809600024,
    1894750043,
    1982530077,
    2072980138,
    2166140248,
    2262050446,
    2360750803,
    2462281446,
    2566682603,
    2673994685,
    2784258433,
    2897515180,
    3013807324,
    3133179183,
    3255678529,
    3381359353,
    3510286835,
    3642546304,
    3778259346,
    3917612824,
    4060911082,
    4208669948,
    4361785907,
    4521840633,
    4691649139,
    4876246450,
    5084663609,
    5333124496,
    5650800094,
    6090166168,
    6745647103,
    7787174786,
    9520594614,
    12496396305,
    17705429349,
    26931190829,
]


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


class Mods(IntFlag):
    NoMod = 0
    NoFail = 1 << 0
    Easy = 1 << 1
    NoVideo = 1 << 2
    Hidden = 1 << 3
    HardRock = 1 << 4
    SuddenDeath = 1 << 5
    DoubleTime = 1 << 6
    Relax = 1 << 7
    HalfTime = 1 << 8
    Nightcore = 1 << 9
    Flashlight = 1 << 10
    Autoplay = 1 << 11
    SpunOut = 1 << 12
    Autopilot = 1 << 13
    Perfect = 1 << 14
    Key4 = 1 << 15
    Key5 = 1 << 16
    Key6 = 1 << 17
    Key7 = 1 << 18
    Key8 = 1 << 19
    FadeIn = 1 << 20
    Random = 1 << 21
    Cinema = 1 << 22
    Target = 1 << 23
    Key9 = 1 << 24
    KeyCoop = 1 << 25
    Key1 = 1 << 26
    Key3 = 1 << 27
    Key2 = 1 << 28
    ScoreV2 = 1 << 29
    LastMod = 1 << 30
    ScoreIncreaseMods = Hidden | HardRock | DoubleTime | Flashlight | FadeIn
    KeyMod = Key1 | Key2 | Key3 | Key4 | Key5 | Key6 | Key7 | Key8 | Key9 | KeyCoop
    FreeModAllowed = (  # black coding style be like
        NoFail
        | Easy
        | Hidden
        | HardRock
        | SuddenDeath
        | Flashlight
        | FadeIn
        | Relax
        | Autopilot
        | SpunOut
        | KeyMod
    )

    @property
    def members(self) -> list:
        return [flag for flag in Mods if self & flag]

    @property
    def acronyms(self) -> List[str]:
        return [
            {
                Mods.NoFail: "NF",
                Mods.Easy: "EZ",
                Mods.Hidden: "HD",
                Mods.HardRock: "HR",
                Mods.SuddenDeath: "SD",
                Mods.DoubleTime: "DT",
                Mods.Relax: "Relax",
                Mods.HalfTime: "HT",
                Mods.Nightcore: "NC",
                Mods.Flashlight: "FL",
                Mods.SpunOut: "SO",
                Mods.Autopilot: "AP",
                Mods.Perfect: "PF",
                Mods.Key1: "K1",
                Mods.Key2: "K2",
                Mods.Key3: "K3",
                Mods.Key4: "K4",
                Mods.Key5: "K5",
                Mods.Key6: "K6",
                Mods.Key7: "K7",
                Mods.Key8: "K8",
                Mods.KeyCoop: "2P",
                Mods.FadeIn: "FI",
                Mods.Random: "RD",
                Mods.ScoreV2: "ScoreV2",
                Mods.Cinema: "Cinema",
                Mods.Autoplay: "Auto",
                Mods.Target: "TP",
            }[mod]
            for mod in self.members
            if mod
            not in [
                Mods.ScoreIncreaseMods,
                Mods.FreeModAllowed,
                Mods.LastMod,
                Mods.KeyMod,
                Mods.NoMod,
            ]
        ]


class Privileges(IntFlag):
    Restriced = 0
    Normal = 1
    BAT = 2
    Supporter = 4
    Peppy = 8
    Admin = 16
    Tournament = 32


class ButtonState(IntFlag):
    NoButtons = 0
    Left1 = 1
    Right1 = 2
    Left2 = 4
    Right2 = 8
    Smoke = 16


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


# fmt: off
CountryCodes = {
    "oc": 1,   "eu": 2,   "ad": 3,   "ae": 4,   "af": 5,   "ag": 6,   "ai": 7,   "al": 8,
    "am": 9,   "an": 10,  "ao": 11,  "aq": 12,  "ar": 13,  "as": 14,  "at": 15,  "au": 16,
    "aw": 17,  "az": 18,  "ba": 19,  "bb": 20,  "bd": 21,  "be": 22,  "bf": 23,  "bg": 24,
    "bh": 25,  "bi": 26,  "bj": 27,  "bm": 28,  "bn": 29,  "bo": 30,  "br": 31,  "bs": 32,
    "bt": 33,  "bv": 34,  "bw": 35,  "by": 36,  "bz": 37,  "ca": 38,  "cc": 39,  "cd": 40,
    "cf": 41,  "cg": 42,  "ch": 43,  "ci": 44,  "ck": 45,  "cl": 46,  "cm": 47,  "cn": 48,
    "co": 49,  "cr": 50,  "cu": 51,  "cv": 52,  "cx": 53,  "cy": 54,  "cz": 55,  "de": 56,
    "dj": 57,  "dk": 58,  "dm": 59,  "do": 60,  "dz": 61,  "ec": 62,  "ee": 63,  "eg": 64,
    "eh": 65,  "er": 66,  "es": 67,  "et": 68,  "fi": 69,  "fj": 70,  "fk": 71,  "fm": 72,
    "fo": 73,  "fr": 74,  "fx": 75,  "ga": 76,  "gb": 77,  "gd": 78,  "ge": 79,  "gf": 80,
    "gh": 81,  "gi": 82,  "gl": 83,  "gm": 84,  "gn": 85,  "gp": 86,  "gq": 87,  "gr": 88,
    "gs": 89,  "gt": 90,  "gu": 91,  "gw": 92,  "gy": 93,  "hk": 94,  "hm": 95,  "hn": 96,
    "hr": 97,  "ht": 98,  "hu": 99,  "id": 100, "ie": 101, "il": 102, "in": 103, "io": 104,
    "iq": 105, "ir": 106, "is": 107, "it": 108, "jm": 109, "jo": 110, "jp": 111, "ke": 112,
    "kg": 113, "kh": 114, "ki": 115, "km": 116, "kn": 117, "kp": 118, "kr": 119, "kw": 120,
    "ky": 121, "kz": 122, "la": 123, "lb": 124, "lc": 125, "li": 126, "lk": 127, "lr": 128,
    "ls": 129, "lt": 130, "lu": 131, "lv": 132, "ly": 133, "ma": 134, "mc": 135, "md": 136,
    "mg": 137, "mh": 138, "mk": 139, "ml": 140, "mm": 141, "mn": 142, "mo": 143, "mp": 144,
    "mq": 145, "mr": 146, "ms": 147, "mt": 148, "mu": 149, "mv": 150, "mw": 151, "mx": 152,
    "my": 153, "mz": 154, "na": 155, "nc": 156, "ne": 157, "nf": 158, "ng": 159, "ni": 160,
    "nl": 161, "no": 162, "np": 163, "nr": 164, "nu": 165, "nz": 166, "om": 167, "pa": 168,
    "pe": 169, "pf": 170, "pg": 171, "ph": 172, "pk": 173, "pl": 174, "pm": 175, "pn": 176,
    "pr": 177, "ps": 178, "pt": 179, "pw": 180, "py": 181, "qa": 182, "re": 183, "ro": 184,
    "ru": 185, "rw": 186, "sa": 187, "sb": 188, "sc": 189, "sd": 190, "se": 191, "sg": 192,
    "sh": 193, "si": 194, "sj": 195, "sk": 196, "sl": 197, "sm": 198, "sn": 199, "so": 200,
    "sr": 201, "st": 202, "sv": 203, "sy": 204, "sz": 205, "tc": 206, "td": 207, "tf": 208,
    "tg": 209, "th": 210, "tj": 211, "tk": 212, "tm": 213, "tn": 214, "to": 215, "tl": 216,
    "tr": 217, "tt": 218, "tv": 219, "tw": 220, "tz": 221, "ua": 222, "ug": 223, "um": 224,
    "us": 225, "uy": 226, "uz": 227, "va": 228, "vc": 229, "ve": 230, "vg": 231, "vi": 232,
    "vn": 233, "vu": 234, "wf": 235, "ws": 236, "ye": 237, "yt": 238, "rs": 239, "za": 240,
    "zm": 241, "me": 242, "zw": 243, "xx": 244, "a2": 245, "o1": 246, "ax": 247, "gg": 248,
    "im": 249, "je": 250, "bl": 251, "mf": 252,
}
# fmt: on
