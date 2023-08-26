from typing import Callable, Optional, List

from .constants import Mode, Mods, RankingType, SubmissionStatus
from ..objects.score import Score, ScoreResponse
from ..game import Game

import requests
import logging


class WebAPI:

    """WebAPI
    -----------

    Functions:
        - `check_updates`
        - `connect`
        - `verify`
        - `get_session`
        - `get_backgrounds`
        - `get_friends`
        - `get_scores`
        - `get_star_rating`
        - `get_favourites`
    """

    def __init__(self, game: Game) -> None:
        self.game = game

        self.session = requests.Session()
        self.session.headers = {"User-Agent": "osu!", "osu-version": self.game.version}

        self.logger = logging.getLogger(f"osu!api-{game.version}")

        self.url = f"https://osu.{self.game.server}"

    def connected_to_bancho(self, *args, **kwargs) -> Callable:
        def wrapper(f: Callable):
            if not self.game.bancho.connected:
                return

            return f(*args, **kwargs)

        return wrapper

    def check_updates(self) -> Optional[dict]:
        self.logger.info("Checking for updates...")

        response = self.session.get(
            "https://osu.ppy.sh/web/check-updates.php",
            params={
                "action": "check",
                "stream": self.game.stream.lower(),
                "time": self.game.time,
            },
        )

        if not response.ok:
            self.logger.error(f"Failed to get updates ({response.status_code})")
            return None

        if "fallback" in response.text:
            self.logger.error(f'Failed to get updates: "{response.text}"')
            return None

        return response.json()

    def connect(self, retry=False) -> bool:
        """This will perform a request on `/web/bancho_connect.php`."""

        self.logger.info("Connecting to bancho...")

        response = self.session.get(
            f"{self.url}/web/bancho_connect.php",
            params={
                "v": self.game.version,
                "u": self.game.username,
                "h": self.game.password_hash,
                "fx": "fail",  # dotnet version
                "ch": str(self.game.client.hash),
                "retry": int(retry),
            },
        )

        if not response.ok:
            self.logger.error(
                f"Error on login: {requests.status_codes._codes[response.status_code][0].upper()}"
            )
            self.logger.warning("Ignoring...")
            return True

        if "error" in response.text:
            self.logger.error(
                f'Error on login: {response.text.removeprefix("error: ")}'
            )

            if "verify" in response.text:
                self.verify(str(self.game.client.hash))
                return False

        return True

    def verify(self, hash: str) -> requests.Response:
        """This will print out a url, where the user can verify this client.\n
        After that, it will exit.
        """

        self.logger.info("Verification required.")
        self.logger.info(
            f'{self.url}/p/verify?u={self.game.username.replace(" ", "%20")}&reason=bancho&ch={hash}'
        )
        self.logger.info("You only need to do this once.")
        exit(0)

    def get_session(self) -> requests.Response:
        """Perform a request on `/web/osu-session.php`.\n
        I don't know what this actually does.\n
        My guess is that it checks, if somebody is already online with this account.
        """  # TODO

        response = self.session.post(
            f"{self.url}/web/osu-session.php",
            files={
                "u": self.game.username,
                "h": self.game.password_hash,
                "action": "check",
            },
        )

        return response

    def get_backgrounds(self) -> Optional[dict]:
        """This will perform a request on `/web/osu-getseasonal.php`."""

        response = self.session.get(f"{self.url}/web/osu-getseasonal.php")

        if response.ok:
            return response.json()

    def get_friends(self) -> List[int]:
        """This will perform a request on `/web/osu-getfriends.php`."""

        response = self.session.get(
            f"{self.url}/web/osu-getfriends.php",
            params={"u": self.game.username, "h": self.game.password_hash},
        )

        if response.ok:
            return [int(id) for id in response.text.split("\n") if id.isdigit()]

        return []

    def get_scores(
        self,
        beatmap_checksum: str,
        beatmap_file: str,
        set_id: int,
        mode: Mode = Mode.Osu,
        mods: Optional[Mods] = Mods.NoMod,
        rank_type=RankingType.Top,
        skip_scores: bool = False,
    ) -> Optional[ScoreResponse]:
        """Get top scores for a beatmap

        - `beatmap_checksum`: MD5 hash of the beatmap file
        - `beatmap_file`: Filename of the beatmap
        - `set_id`: BeatmapsetId for the beatmap
        - `mode`: Specify a mode
        - `mods`: Filter by mods (`rank_type` must be set to `SelectedMod`)
        - `rank_type`: osu.api.constants.RankingTy
            - `Top`: Global Ranking
            - `SelectedMod`: Global Ranking (Selected Mods) (Supporter)
            - `Friends`: Friend Ranking (Supporter)
            - `Country`: Country Ranking (Supporter)
        """

        response = self.session.get(
            f"{self.url}/web/osu-osz2-getscores.php",
            params={
                "s": int(skip_scores),
                "vv": 4,  # ?
                "v": rank_type.value,
                "c": beatmap_checksum,
                "f": beatmap_file,
                "m": mode.value,
                "i": set_id,
                "mods": mods.value,
                "a": 0,  # ?
                "us": self.game.username,
                "ha": self.game.password_hash,
            },
        )

        if not response.ok:
            self.logger.error(f"Failed to fetch scores ({response.status_code})")
            return

        return ScoreResponse.from_string(response.text, mode)

    def get_star_rating(
        self, beatmap_id: int, mode: Mode = Mode.Osu, mods: Mods = Mods.NoMod
    ) -> float:
        """Get star rating of a beatmap"""

        response = self.session.post(
            f"{self.url}/difficulty-rating",
            json={
                "beatmap_id": beatmap_id,
                "ruleset_id": mode.value,
                "mods": [{"acronym": acronym} for acronym in mods.acronyms],
            },
        )

        if not response.ok:
            return 0.0

        return float(response.text)

    def get_favourites(self) -> List[int]:
        """Get your beatmap favourites"""

        response = self.session.get(
            f"{self.url}/web/osu-getfavourites.php",
            params={"u": self.game.username, "h": self.game.password_hash},
        )

        if not response.ok:
            return []

        return [
            int(beatmap_id) for beatmap_id in response.text.split("\n") if beatmap_id
        ]
