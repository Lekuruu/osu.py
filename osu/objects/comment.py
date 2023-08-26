from osu.api.constants import CommentTarget
from dataclasses import dataclass


@dataclass
class Comment:
    time: int
    target: CommentTarget
    format: str
    text: str

    @classmethod
    def from_string(cls, string: str):
        line = string.split("\t")
        return Comment(int(line[0]), CommentTarget(line[1]), line[2], line[3])
