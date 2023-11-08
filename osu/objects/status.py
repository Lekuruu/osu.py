from dataclasses import dataclass

from ..bancho.constants import StatusAction, Mode, Mods


@dataclass
class Status:
    action: StatusAction = StatusAction.Idle
    text: str = ""
    checksum: str = ""
    mods: Mods = Mods.NoMod
    mode: Mode = Mode.Osu
    beatmap_id: int = 0

    def __repr__(self) -> str:
        return f'<{self.action.name}{f" - {self.text}" if self.text else ""}>'

    def reset(self) -> None:
        self.action = StatusAction.Idle
        self.text = ""
        self.checksum = ""
        self.mods = []
        self.mode = Mode.Osu
        self.beatmap_id = 0
