from typing import Callable, Optional, Iterator, List, TYPE_CHECKING

from .constants import Mode, Mods, RankingType, CommentTarget, DisplayMode, ModeSelect
from ..objects.beatmap import OnlineBeatmap
from ..objects.score import ScoreResponse
from ..objects.comment import Comment

if TYPE_CHECKING:
    from ..game import Game

import requests
import logging


class WebAPI:
    """WebAPI
    -----------
    This class provides access to the client api endpoints, which includes:
        - Leaderboards
        - Comments
        - Friends
        - Replays
        - Avatars
        - Beatmap Star Ratings
        - Seasonal Backgrounds

    with the exception being score submission for obvious reasons.

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
        - `add_favourite`
        - `get_comments`
        - `post_comment`
        - `get_replay`
        - `get_avatar`
        - `get_beatmap_thumbnail`
        - `get_beatmap_preview`
        - `search_beatmapsets`
        - `download_osz`
    """

    def __init__(self, game: "Game") -> None:
        self.game = game

        self.session = requests.Session()
        self.session.headers = {"User-Agent": "osu!", "osu-version": self.game.version}

        self.logger = logging.getLogger(f"osu!api-{game.version}")
        self.logger.disabled = game.logger.disabled

        self.url = f"https://osu.{self.game.server}"
        self.asset_url = f"https://assets.{self.game.server}"

    @property
    def verification_url(self) -> str:
        return (
            f"{self.url}/p/verify"
            f'?u={self.game.username.replace(" ", "%20")}'
            f"&reason=bancho"
            f"&ch={self.game.client.hash}"
        )

    def connected_to_bancho(self, *args, **kwargs) -> Callable:
        """Can be used as a class wrapper to ensure that the client is connected"""

        def wrapper(f: Callable):
            if not self.game.bancho.connected:
                return

            return f(*args, **kwargs)

        return wrapper

    def check_updates(self) -> Optional[List[dict]]:
        """This will a request on `/web/check-updates.php`

        Returns:
            Optional[list]: When the request was successful, it will return a list of dicts with the following attributes:
                            file_version, filename, file_hash, filesize, timestamp, patch_id, url_full
        """
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
        """This will perform a request on `/web/bancho_connect.php`.

        Returns:
            bool: If the request was successful
        """

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
            if self.game.server == "ppy.sh":
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
                self.verify()
                return False

        return True

    def verify(self, exit_after: bool = True) -> None:
        """This will print out a url, where the user can verify this client."""
        self.logger.info("Verification required.")
        self.logger.info(self.verification_url)
        self.logger.info("You only need to do this once.")

        if exit_after:
            exit(0)

    def get_session(self) -> requests.Response:
        """Perform a request on `/web/osu-session.php`.\n
        I don't know what this actually does.
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

    def get_backgrounds(self) -> Optional[list]:
        """This will perform a request on `/web/osu-getseasonal.php`.

        Returns:
            Optional[list]: List of urls for the seasonal background images
        """

        response = self.session.get(f"{self.url}/web/osu-getseasonal.php")

        if response.ok:
            return response.json()

    def get_menu_content(self) -> Optional[dict]:
        """This will perform a request on `/web/osu-getcurrent.php`.

        Returns:
            Optional[dict]: The menu content
        """

        response = self.session.get(f"{self.asset_url}/menu-content.json")

        if response.ok:
            return response.json()

    def get_friends(self) -> List[int]:
        """This will perform a request on `/web/osu-getfriends.php`.

        Returns:
            List[int]: The user ids of your friends
        """

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

        Args:
            beatmap_checksum (str): MD5 hash of the beatmap file
            beatmap_file (str): Filename of the beatmap
            set_id (int): BeatmapsetId for the beatmap
            mode (Mode, optional): Specify a mode
            mods (Mods, optional): Filter by mods (`rank_type` must be set to `SelectedMod`)
            rank_type (RankingType, optional): Select the leaderboard type

        Returns:
            Optional[ScoreResponse]
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
        """Get star rating of a beatmap

        Args:
            beatmap_id (int): Beatmap ID
            mode (Mode, optional): Mode
            mods (Mods, optional): Mods

        Returns: float
        """

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
        """Get your beatmap favourites

        Returns:
            List[int]: List of beatmapset ids
        """

        response = self.session.get(
            f"{self.url}/web/osu-getfavourites.php",
            params={"u": self.game.username, "h": self.game.password_hash},
        )

        if not response.ok:
            return []

        return [
            int(beatmap_id) for beatmap_id in response.text.split("\n") if beatmap_id
        ]

    def add_favourite(self, beatmapset_id: int) -> str:
        """Add a beatmap to your favourites list

        Args:
            beatmapset_id (int)

        Returns:
            str: A human-readable response string. e.g. "Added to favourites! You have a total of 2 favourites."
        """

        response = self.session.get(
            f"{self.url}/web/osu-addfavourite.php",
            params={
                "u": self.game.username,
                "h": self.game.password_hash,
                "a": beatmapset_id,
            },
        )

        return response.text

    def get_comments(
        self,
        beatmap_id: Optional[int] = None,
        set_id: Optional[int] = None,
        replay_id: Optional[int] = None,
        mode: Mode = Mode.Osu,
    ) -> List[Comment]:
        """Get comments for a beatmap, set or replay

        Args:
            beatmap_id (int, optional): Get comments from this map
            set_id (int, optional): Get comments from this set
            replay_id (int, optional): Get comments from this replay
            mode (Mode, optional): Specify the mode

        Returns:
            List[Comment]
        """

        if all([beatmap_id is None, set_id is None, replay_id is None]):
            return []

        response = self.session.post(
            f"{self.url}/web/osu-comment.php",
            files={
                "u": (None, self.game.username),
                "p": (None, self.game.password_hash),
                "b": (None, beatmap_id),
                "s": (None, set_id),
                "r": (None, replay_id),
                "m": (None, mode.value),
                "a": (None, "get"),
            },
        )

        if not response.ok:
            self.logger.error(f"Failed to fetch comments ({response.status_code})")
            return []

        if not response.text:
            return []

        return [Comment.from_string(line) for line in response.text.split("\n") if line]

    def post_comment(
        self,
        text: str,
        time: int,
        target: CommentTarget = CommentTarget.Map,
        beatmap_id: Optional[int] = None,
        replay_id: Optional[int] = None,
        set_id: Optional[int] = None,
        mode: Mode = Mode.Osu,
    ) -> None:
        """Post a comment to a map, song or replay

        Args:
            text (str): The content of your comment
            time (int): The time you want this comment to appear inside the map
            target (CommentTarget): Specify where this comment should appear.
            mode (Mode, optional): Specify the mode
            beatmap_id (Optional[int], optional): Set the beatmap id, if you set the target to "Map"
            replay_id (Optional[int], optional): Set the replay id, if you set the target to "Replay"
            set_id (Optional[int], optional): Set the set it, if you set the target to "Song"
        """

        if all([beatmap_id is None, set_id is None, replay_id is None]):
            return

        target_id = {
            CommentTarget.Map: beatmap_id,
            CommentTarget.Song: set_id,
            CommentTarget.Replay: replay_id,
        }[target]

        if target_id is None:
            return

        self.session.post(
            f"{self.url}/web/osu-comment.php",
            files={
                "u": (None, self.game.username),
                "p": (None, self.game.password_hash),
                "b": (None, beatmap_id),
                "s": (None, set_id),
                "r": (None, replay_id),
                "m": (None, mode.value),
                "a": (None, "post"),
                "starttime": (None, time),
                "comment": (None, text),
                "target": (None, target.value),
            },
        )

    def get_replay(self, replay_id: int, mode: Mode = Mode.Osu) -> Optional[bytes]:
        """Get raw replay data by id (not osr!)

        Args:
            replay_id (int): The score/replay id
            mode (Mode, optional): The mode of this score

        Returns:
            Optional[bytes]: The raw replay data, compressed with lzma

        Please view this page for more information: https://osu.ppy.sh/wiki/de/Client/File_formats/osr_%28file_format%29
        """

        response = self.session.get(
            f"{self.url}/web/osu-getreplay.php",
            params={
                "u": self.game.username,
                "h": self.game.password_hash,
                "m": mode.value,
                "c": replay_id,
            },
        )

        if not response.ok:
            self.logger.error(f"Failed to fetch replay ({response.status_code})")
            return

        return response.content

    def get_avatar(self, user_id: int) -> Optional[bytes]:
        """Get avatar by user id"""

        return self.session.get(f"https://a.{self.game.server}/{user_id}").content

    def get_beatmap_thumbnail(
        self, beatmapset_id: int, large: bool = False
    ) -> Optional[bytes]:
        """Get the background thumbnail of a beatmap"""

        response = self.session.get(
            f"https://b.{self.game.server}/thumb/{beatmapset_id}{'l' if large else ''}.jpg"
        )

        return response.content if response.ok else None

    def get_beatmap_preview(self, beatmapset_id: int) -> Optional[bytes]:
        """Get the preview to a song of a beatmap"""

        response = self.session.get(
            f"https://b.{self.game.server}/preview/{beatmapset_id}.mp3"
        )

        return response.content if response.ok else None

    def download_osz(
        self, beatmapset_id: int, no_video: bool = False
    ) -> Optional[Iterator[bytes]]:
        """Download an osz file

        Args:
            beatmapset_id (int): The beatmapset id
            no_video (bool, optional): Specify if the osz should contain a video

        Returns:
            Optional[Iterator[bytes]]: An iterator of bytes, which contains the osz
        """

        response = self.session.get(
            f"https://osu.ppy.sh/d/{beatmapset_id}{'n' if no_video else ''}",
            allow_redirects=True,
            stream=True,
            params={
                "u": self.game.username,
                "h": self.game.password_hash,
                "vv": 2,  # what is this lol
            },
        )

        if not response.ok:
            return

        return response.iter_content(1024)

    def search_beatmapsets(
        self, query: str, display_mode=DisplayMode.Ranked, mode=ModeSelect.All, page=0
    ) -> Optional[List[OnlineBeatmap]]:
        """Get a list of beatmapsets, aka. osu! direct search

        Args:
            query (str): Search for beatmaps
            display_mode (DisplayMode): Filter maps by their status
            mode (ModeSelect): Filter maps by their mode
            page (int): Specify an offset/page

        Returns:
            Optional[List[OnlineBeatmap]]
        """

        response = self.session.get(
            f"https://osu.ppy.sh/web/osu-search.php",
            params={
                "u": self.game.username,
                "h": self.game.password_hash,
                "q": query,
                "r": display_mode.value,
                "m": mode.value,
                "p": page,
            },
        )

        lines = response.text.splitlines()
        status = int(lines[0])

        if status < 0:
            self.logger.error(f'Failed to get beatmapsets: "{lines[1]}"')
            return

        return [OnlineBeatmap.parse(line) for line in lines[1:]]
