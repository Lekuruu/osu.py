from ..bancho.streams import StreamIn
from ..bancho.constants import Grade

from dataclasses import dataclass


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
