from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

from ..api.constants import SubmissionStatus, Mods, Mode

if TYPE_CHECKING:
    from ..game import Game


@dataclass
class Score:
    id: int
    username: str
    total_score: int
    max_combo: int
    c50: int
    c100: int
    c300: int
    cMiss: int
    cKatu: int
    cGeki: int
    perfect: bool
    mods: Mods
    user_id: int
    rank: Optional[int]
    date: Optional[datetime]
    mode: Mode
    has_replay: bool

    @classmethod
    def from_string(cls, string: str, mode: Mode) -> "Score":
        lines = string.split("|")

        return Score(
            int(lines[0]),
            lines[1],
            int(lines[2]),
            int(lines[3]),
            int(lines[4]),
            int(lines[5]),
            int(lines[6]),
            int(lines[7]),
            int(lines[8]),
            int(lines[9]),
            lines[10] == "1",
            Mods(int(lines[11])),
            int(lines[12]),
            int(lines[13]) if len(lines[13]) > 0 else 0,
            datetime.fromtimestamp(int(lines[14])),
            mode,
            lines[15] == "1",
        )

    def get_comments(self, game: "Game"):
        return game.api.get_comments(replay_id=self.id, mode=self.mode)

    def get_replay(self, game: "Game"):
        return game.api.get_replay(replay_id=self.id, mode=self.mode)


@dataclass
class ScoreResponse:
    status: SubmissionStatus
    beatmap_id: Optional[int]
    set_id: Optional[int]
    total_scores: int
    global_offset: int
    beatmap_format: Optional[str]
    rating: float
    personal_best: Optional[Score]
    scores: List[Score]
    has_osz2: bool = False
    featured_artist_track_id: Optional[int] = None
    featured_artist_license_text: Optional[str] = None

    @classmethod
    def from_string(cls, string: str, mode: Mode) -> "ScoreResponse":
        result = string.split("\n")

        if len(result) <= 0:
            return

        status_results = result[0].split("|")
        beatmap_status = {
            "-1": SubmissionStatus.NotSubmitted,
            "0": SubmissionStatus.Pending,
            "1": SubmissionStatus.Unknown,
            "2": SubmissionStatus.Ranked,
            "3": SubmissionStatus.Approved,
            "4": SubmissionStatus.Qualified,
            "5": SubmissionStatus.Loved,
        }[status_results[0]]

        beatmap_id = None
        beatmapset_id = None
        total_scores = 0
        featured_artist_track_id = None
        featured_artist_license_text = None
        has_osz2 = status_results[1] == "true"

        if len(status_results) > 2:
            beatmap_id = int(status_results[2])
            beatmapset_id = int(status_results[3])
            total_scores = int(status_results[4] or "0")

        if len(status_results) > 5:
            featured_artist_track_id = int(status_results[5] or "0") or None
            featured_artist_license_text = status_results[6] or None

        offset = 0
        beatmap_format = None
        rating = 0.0

        if len(result) > 1:
            offset = int(result[1])
            beatmap_format = result[2]
            rating = float(result[3])

        personal_best = None
        scores = []

        if len(result) > 4:
            if len(result[4]) > 0:
                personal_best = Score.from_string(result[4], mode)

            for score in result[5:]:
                if not score:
                    continue

                scores.append(Score.from_string(score, mode))

        return ScoreResponse(
            beatmap_status,
            beatmap_id,
            beatmapset_id,
            total_scores,
            offset,
            beatmap_format,
            rating,
            personal_best,
            scores,
            has_osz2,
            featured_artist_track_id,
            featured_artist_license_text,
        )
