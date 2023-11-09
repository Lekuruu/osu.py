from ..bancho.constants import Grade, Mode
from ..bancho.streams import StreamIn

from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BeatmapInfo:
    id: int
    beatmap_id: int
    beatmapset_id: int
    thread_id: int
    ranked: int
    osu_rank: Grade
    fruits_rank: Grade
    taiko_rank: Grade
    mania_rank: Grade
    checksum: str

    @classmethod
    def decode(cls, stream: StreamIn):
        return BeatmapInfo(
            stream.s16(),
            stream.s32(),
            stream.s32(),
            stream.s32(),
            stream.u8(),
            Grade(stream.u8()),
            Grade(stream.u8()),
            Grade(stream.u8()),
            Grade(stream.u8()),
            stream.string(),
        )


@dataclass
class OnlineBeatmap:
    osz_filename: str
    artist: str
    title: str
    creator: str
    status: int
    rating: float
    last_update: datetime
    set_id: int
    thread_id: int
    has_video: bool
    has_storyboard: bool
    filesize: int
    filesize_novideo: Optional[int]
    difficulties: List[Tuple[str, Mode]]

    @classmethod
    def parse(cls, string: str):
        args = string.split("|")
        return OnlineBeatmap(
            args[0],
            args[1],
            args[2],
            args[3],
            int(args[4]),
            float(args[5]),
            datetime.fromisoformat(args[6]),
            int(args[7]),
            int(args[8]),
            args[9] == "1",
            args[10] == "1",
            int(args[11]),
            int(args[12]) if args[12] else None,
            [
                (difficulty.split("@")[0], Mode(int(difficulty.split("@")[-1])))
                for difficulty in args[13].split(",")
            ],
        )
