from dataclasses import dataclass

from ..bancho.streams import StreamIn, StreamOut
from ..bancho.constants import ButtonState


@dataclass
class ReplayFrame:
    button_state: ButtonState
    time: int
    x: float
    y: float

    def encode(self) -> bytes:
        stream = StreamOut()
        stream.u8(self.button_state.value)
        stream.u8(0)  # unused
        stream.float(self.x)
        stream.float(self.y)
        stream.s32(self.time)
        return stream.get()

    @classmethod
    def decode(cls, stream: StreamIn):
        button_state = ButtonState(stream.u8())

        # This byte is now unused and was replaced by the ButtonState flag
        # It's only kept here, because of legacy replay support
        if stream.u8() > 0:
            if ButtonState.Right1 not in button_state:
                button_state |= ButtonState.Right1

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

    def encode(self) -> bytes:
        stream = StreamOut()
        stream.s32(self.time)
        stream.u8(self.id)
        stream.u16(self.c300)
        stream.u16(self.c100)
        stream.u16(self.c50)
        stream.u16(self.cGeki)
        stream.u16(self.cKatu)
        stream.u16(self.cMiss)
        stream.s32(self.total_score)
        stream.u16(self.max_combo)
        stream.u16(self.current_combo)
        stream.bool(self.perfect)
        stream.u8(self.current_hp)
        stream.u8(self.tag_byte)
        stream.bool(self.score_v2)
        if self.score_v2:
            stream.float(self.combo_portion)
            stream.float(self.bonus_portion)
        return stream.get()

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
