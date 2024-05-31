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


class MatchType(IntEnum):
    Standard = 0
    Powerplay = 1


class MatchScoringTypes(IntEnum):
    Score = 0
    Accuracy = 1
    Combo = 2
    ScoreV2 = 3


class MatchTeamTypes(IntEnum):
    HeadToHead = 0
    TagCoop = 1
    TeamVs = 2
    TagTeamVs = 3


class SlotStatus(IntFlag):
    Open = 1
    Locked = 2
    NotReady = 4
    Ready = 8
    NoMap = 16
    Playing = 32
    Complete = 64
    Quit = 128

    HasPlayer = NotReady | Ready | NoMap | Playing | Complete


class SlotTeam(IntEnum):
    Neutral = 0
    Blue = 1
    Red = 2


CountryCodes = {
    "XX": "Unknown",
    "OC": "Oceania",
    "EU": "Europe",
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AG": "Antigua and Barbuda",
    "AI": "Anguilla",
    "AL": "Albania",
    "AM": "Armenia",
    "AN": "Netherlands Antilles",
    "AO": "Angola",
    "AQ": "Antarctica",
    "AR": "Argentina",
    "AS": "American Samoa",
    "AT": "Austria",
    "AU": "Australia",
    "AW": "Aruba",
    "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina",
    "BB": "Barbados",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BF": "Burkina Faso",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BI": "Burundi",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BN": "Brunei Darussalam",
    "BO": "Bolivia",
    "BR": "Brazil",
    "BS": "The Bahamas",
    "BT": "Bhutan",
    "BV": "Bouvet Island",
    "BW": "Botswana",
    "BY": "Belarus",
    "BZ": "Belize",
    "CA": "Canada",
    "CC": "Cocos (Keeling) Islands",
    "CD": "Democratic Republic of the Congo",
    "CF": "Central African Republic",
    "CG": "Republic of the Congo",
    "CH": "Switzerland",
    "CI": "Côte d'Ivoire",
    "CK": "Cook Islands",
    "CL": "Chile",
    "CM": "Cameroon",
    "CN": "China",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CV": "Cape Verde",
    "CX": "Christmas Island",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DK": "Denmark",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "EH": "Western Sahara",
    "ER": "Eritrea",
    "ES": "Spain",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FK": "Falkland Islands (Malvinas)",
    "FM": "Micronesia, Federated States of Micronesia",
    "FO": "Faroe Islands",
    "FR": "France",
    "FX": "France, Metropolitan",
    "GA": "Gabon",
    "GB": "United Kingdom",
    "GD": "Grenada",
    "GE": "Georgia",
    "GF": "French Guiana",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GL": "Greenland",
    "GM": "Gambia",
    "GN": "Guinea",
    "GP": "Guadeloupe",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GS": "South Georgia and the South Sandwich Islands",
    "GT": "Guatemala",
    "GU": "Guam",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HK": "Hong Kong",
    "HM": "Heard Island and McDonald Islands",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IO": "British Indian Ocean Territory",
    "IQ": "Iraq",
    "IR": "Iran, Islamic Republic of Iran",
    "IS": "Iceland",
    "IT": "Italy",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KM": "Comoros",
    "KN": "Saint Kitts and Nevis",
    "KP": "Korea, Democratic People's Republic of Korea",
    "KR": "Korea, Republic of Korea",
    "KW": "Kuwait",
    "KY": "Cayman Islands",
    "KZ": "Kazakhstan",
    "LA": "Lao People's Democratic Republic",
    "LB": "Lebanon",
    "LC": "Saint Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LR": "Liberia",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "LY": "Libyan Arab Jamahiriya",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova, Republic of Moldova",
    "MG": "Madagascar",
    "MH": "Marshall Islands",
    "MK": "Macedonia, the Former Yugoslav Republic of Macedonia",
    "ML": "Mali",
    "MM": "Myanmar",
    "MN": "Mongolia",
    "MO": "Macau",
    "MP": "Northern Mariana Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MS": "Montserrat",
    "MT": "Malta",
    "MU": "Mauritius",
    "MV": "Maldives",
    "MW": "Malawi",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NC": "New Caledonia",
    "NE": "Niger",
    "NF": "Norfolk Island",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NU": "Niue",
    "NZ": "New Zealand",
    "OM": "Oman",
    "PA": "Panama",
    "PE": "Peru",
    "PF": "French Polynesia",
    "PG": "Papua New Guinea",
    "PH": "Philippines",
    "PK": "Pakistan",
    "PL": "Poland",
    "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn",
    "PR": "Puerto Rico",
    "PS": "Palestinian Territory, Occupied",
    "PT": "Portugal",
    "PW": "Palau",
    "PY": "Paraguay",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RU": "Russian Federation",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SB": "Solomon Islands",
    "SC": "Seychelles",
    "SD": "Sudan",
    "SE": "Sweden",
    "SG": "Singapore",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "SI": "Slovenia",
    "SJ": "Svalbard and Jan Mayen",
    "SK": "Slovakia",
    "SL": "Sierra Leone",
    "SM": "San Marino",
    "SN": "Senegal",
    "SO": "Somalia",
    "SR": "Suriname",
    "ST": "Sao Tome and Principe",
    "SV": "El Salvador",
    "SY": "Syrian Arab Republic",
    "SZ": "Eswatini",
    "TC": "Turks and Caicos Islands",
    "TD": "Chad",
    "TF": "French Southern Territories",
    "TG": "Togo",
    "TH": "Thailand",
    "TJ": "Tajikistan",
    "TK": "Tokelau",
    "TM": "Turkmenistan",
    "TN": "Tunisia",
    "TO": "Tonga",
    "TL": "Timor-Leste",
    "TR": "Turkey",
    "TT": "Trinidad and Tobago",
    "TV": "Tuvalu",
    "TW": "Taiwan, Province of China",
    "TZ": "Tanzania, United Republic of Tanzania",
    "UA": "Ukraine",
    "UG": "Uganda",
    "UM": "United States Minor Outlying Islands",
    "US": "United States",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VA": "Holy See (Vatican City State)",
    "VC": "Saint Vincent and the Grenadines",
    "VE": "Venezuela, Bolivarian Republic of Venezuela",
    "VG": "Virgin Islands, British",
    "VI": "Virgin Islands, U.S.",
    "VN": "Viet Nam",
    "VU": "Vanuatu",
    "WF": "Wallis and Futuna",
    "WS": "Samoa",
    "YE": "Yemen",
    "YT": "Mayotte",
    "RS": "Serbia",
    "ZA": "South Africa",
    "ZM": "Zambia",
    "ME": "Montenegro",
    "ZW": "Zimbabwe",
    "XX": "Unknown",
    "SP": "Satellite Provider",
    "XX": "Other",
    "AX": "Åland Islands",
    "GG": "Guernsey",
    "IM": "Isle of Man",
    "JE": "Jersey",
    "BL": "Saint Barthélemy",
    "MF": "Saint Martin (French part)",
}
