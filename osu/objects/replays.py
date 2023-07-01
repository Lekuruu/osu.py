from dataclasses import dataclass
from typing import List

from ..bancho.constants import ButtonState
from ..bancho.streams import StreamIn


@dataclass
class ReplayFrame:
    button_state: List[ButtonState]
    time: int
    x: float
    y: float

    @classmethod
    def decode(cls, stream: StreamIn):
        button_state = ButtonState.list(stream.u8())

        # idk what this does tbh
        if stream.s8() > 0:
            if ButtonState.Right1 not in button_state:
                button_state.append(ButtonState.Right1)

        x = stream.float()
        y = stream.float()
        time = stream.s32()

        return ReplayFrame(button_state, time, x, y)


@dataclass
class ScoreFrame:
    time: int
    id: int
    c300: int
    c100: int
    c50: int
    cGeki: int
    cKatu: int
    cMiss: int
    total_score: int
    max_combo: int
    current_combo: int
    perfect: bool
    current_hp: int
    tag_byte: int
    score_v2: bool = False
    combo_portion: float = 0.0
    bonus_portion: float = 0.0

    @property
    def total_hits(self) -> int:
        return self.c50 + self.c100 + self.c300 + self.cMiss

    @classmethod
    def decode(cls, stream: StreamIn):
        return ScoreFrame(
            stream.s32(),
            stream.u8(),
            stream.u16(),
            stream.u16(),
            stream.u16(),
            stream.u16(),
            stream.u16(),
            stream.u16(),
            stream.s32(),
            stream.u16(),
            stream.u16(),
            stream.bool(),
            stream.u8(),
            stream.u8(),
            v2 := stream.bool(),
            stream.float() if v2 else 0.0,
            stream.float() if v2 else 0.0,
        )
