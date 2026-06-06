from typing import TYPE_CHECKING
from datetime import datetime

from .constants import ClientPackets, ReplayAction, StatusAction, Privileges
from .connector_http import HttpBanchoConnector
from .connector import BanchoConnector
from .streams import StreamOut

from ..objects.replays import ReplayFrame, ScoreFrame
from ..objects.collections import Players, Channels, Matches
from ..objects.match import Match
from ..objects.player import Player
from ..objects.status import Status

if TYPE_CHECKING:
    from ..game import Game

import logging
import time


class BanchoClient:
    """BanchoClient
    ---------------
    To interact with bancho, you can set event listeners on server packets.

    Here is an example for the message packet:
    ```
    @game.events.register(ServerPackets.SEND_MESSAGE)
    def on_message(sender: Player, message: str, target: Channel|Player):
        print(f"Received message from {sender.name} on {target.name}: {message}")
    ```
    Please refer to `osu.bancho.packets.py`, to find the arguments that are being passed into the event.

    You can also create tasks, that run in specific intervals:
    ```
    @game.tasks.register(minutes=1, loop=True)
    def example_task():
        # This code runs every minute
        ...
    ```

    Attributes:
        `player`: osu.objects.Player

        `spectating`: osu.objects.Player

        `match`: osu.objects.Match

        `players`: osu.objects.Players

        `matches`: osu.objects.Matches

        `channels`: osu.objects.Channels

        `privileges`: osu.bancho.constants.Privileges

        `friends`: list[int]

        `game`: osu.game.Game

        `connected`: bool

        `retry`: bool

        `min_idletime`: int (Minimum time between requests)

        `max_idletime`: int (Maximum time between requests)

        `connector`: osu.bancho.connectors.BanchoConnector

    Functions:
        `set_connector`: Set the transport connector used by the client

        `enqueue`: Send a bancho packet to the server

        `ping`: Send a ping packet

        `request_presence`: Request a presence update for a list of players

        `request_stats`: Request a stats update for a list of players

        `request_status`: Request a status update for your account

        `update_status`: Update `player.status`

        `start_spectating`: Start spectating a player

        `stop_spectating`: Stop spectating

        `cant_spectate`: Is sent when the player does not have the beatmap for spectating

        `send_frames`: Send replay frames to your spectators

        `join_lobby`: Join the lobby

        `leave_lobby`: Leave the lobby

        `create_match`: Create a multiplayer match

        `join_match`: Join a multiplayer match

        `leave_match`: Leave the current multiplayer match
    """

    def __init__(self, game: "Game") -> None:
        self.game = game

        self.logger = logging.getLogger(f"bancho-{game.version}")
        self.logger.disabled = game.logger.disabled

        self.user_id = -1
        self.connected = False
        self.retry = True

        self.player: Player
        self.match: Match | None = None
        self.spectating: Player | None = None

        self.channels = Channels()
        self.matches = Matches(game)
        self.players = Players(game)

        self.ping_count = 0
        self.protocol = 0

        self.privileges: Privileges = Privileges.Normal
        self.friends: list[int] = []

        self.last_action = datetime.now().timestamp()
        self.fast_read = False
        self.silenced = False
        self.in_lobby = False

        self.min_idletime = 1
        self.max_idletime = 2.5
        self.connector: BanchoConnector
        self.set_connector(HttpBanchoConnector())

    @property
    def status(self) -> Status:
        """Status of the connected player"""
        if not self.player:
            return Status()
        return self.player.status

    @property
    def idle_time(self) -> float:
        """Time between now and the last request"""
        return datetime.now().timestamp() - self.last_action

    @property
    def request_interval(self) -> int | float:
        """Time between requests"""
        if self.fast_read:
            return 0

        interval: int | float = 1

        if not self.spectating:
            interval *= 1 + self.idle_time / 10
            interval *= self.ping_count

        return min(self.max_idletime, max(self.min_idletime, interval))

    def run(self) -> None:
        """Run the client loop"""
        self.connect()

        while self.connected:
            try:
                self.connector.wait()
                self.dequeue()
                self.game.tasks.execute()
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                self.logger.fatal(f"Unhandled Exception: {exc}", exc_info=exc)

        if self.retry:
            self.logger.error("Retrying in 15 seconds...")
            time.sleep(15)
            self.game.run(retry=True)

    def connect(self) -> None:
        """Perform the initial connection to the bancho server."""
        self.connector.connect()

    def dequeue(self) -> None:
        """Receive packets and flush any connector-specific queue."""
        self.connector.receive()

    def exit(self) -> None:
        """Send logout packet to bancho, and disconnect."""
        if self.connected:
            try:
                self.enqueue(ClientPackets.LOGOUT, int(0).to_bytes(4, "little"))
            except OSError:
                pass

        self.connected = False
        self.retry = False
        self.connector.close()

    def set_connector(self, connector: BanchoConnector) -> None:
        """Set the connector used to communicate with bancho."""
        if not isinstance(connector, BanchoConnector):
            raise TypeError("connector must be an instance of BanchoConnector")

        if self.connected:
            raise RuntimeError("Cannot change connector while connected")

        if hasattr(self, "connector"):
            self.connector.close()

        self.connector = connector
        self.connector.bind(self)

    def enqueue(
        self, packet: ClientPackets, data: bytes = b"", dequeue: bool | None = None
    ) -> bytes:
        """Send a packet through the active connector."""

        stream = StreamOut()

        # Construct header
        stream.u16(packet.value)
        stream.bool(False)
        stream.u32(len(data))
        stream.write(data)

        self.logger.debug(f'Sending {packet.name} -> "%s"', data)

        packet_data = stream.get()

        if dequeue is None:
            dequeue = self.connector.dequeue_on_enqueue

        self.connector.send(packet_data, dequeue)

        return packet_data

    def unsilence(self) -> None:
        """Will be called when the connected player gets unsilenced by the server"""
        if not self.silenced:
            return

        self.player.silenced = False
        self.silenced = False
        self.logger.info("You can now talk again.")

    def ping(self) -> None:
        """Send a ping to the server"""
        self.enqueue(ClientPackets.PING)

    def request_presence(self, ids: list[int]) -> None:
        """Request the presence of a list of players"""
        stream = StreamOut()
        stream.intlist(ids)

        self.enqueue(ClientPackets.USER_PRESENCE_REQUEST, stream.get())

    def request_stats(self, ids: list[int]) -> None:
        """Request the stats of a list of players"""
        stream = StreamOut()
        stream.intlist(ids)

        self.enqueue(ClientPackets.USER_STATS_REQUEST, stream.get())

    def request_status(self) -> None:
        """Request a status update for the connected player"""
        self.enqueue(ClientPackets.REQUEST_STATUS_UPDATE)

    def update_status(self) -> None:
        """Send current player status to the server

        You can change your status by updating the `game.bancho.player.status` attributes.\n
        For example:
            >>> status = game.bancho.player.status
            >>>
            >>> status.action = StatusAction.Playing
            >>> status.text = "UNDEAD CORPORATION - Everything will freeze [Time Freeze]"
            >>> status.checksum = "a84050da9b68ca1bd8e2d1700b9c6ca5" # .osu file checksum
            >>> status.mods = Mods.Hidden|Mods.HardRock
            >>> status.mode = GameMode.Osu
            >>> status.beatmap_id = 555797
            >>>
            >>> game.bancho.update_status()
        """

        if not self.player:
            return

        stream = StreamOut()
        stream.u8(self.player.status.action.value)
        stream.string(self.player.status.text)
        stream.string(self.player.status.checksum)
        stream.u32(self.player.status.mods.value)
        stream.u8(self.player.mode.value)
        stream.s32(self.player.status.beatmap_id)

        self.enqueue(ClientPackets.CHANGE_ACTION, stream.get())

    def start_spectating(self, target: Player) -> None:
        """Start spectating a player

        You will receive `ServerPackets.SPECTATE_FRAMES` packets that contain replay data.\n
        You can use osu-recorder (https://github.com/Lekuruu/osu-recorder) as a reference for that.
        """
        if self.spectating:
            self.stop_spectating()

        self.enqueue(
            ClientPackets.START_SPECTATING,
            int(target.id).to_bytes(4, "little"),
            dequeue=False,
        )

        self.spectating = target

        target.request_presence()
        target.request_stats()

        self.status.action = StatusAction.Watching
        self.status.text = target.status.text
        self.status.checksum = target.status.checksum
        self.status.mods = target.status.mods
        self.status.mode = target.status.mode
        self.status.beatmap_id = target.status.beatmap_id

        self.update_status()

    def stop_spectating(self) -> None:
        """Stop spectating a player"""
        if not self.spectating:
            return

        self.logger.info(f"Stopped spectating {self.spectating.name}.")

        self.enqueue(ClientPackets.STOP_SPECTATING, dequeue=False)
        self.spectating = None

        self.status.reset()
        self.update_status()

    def cant_spectate(self) -> None:
        """Sends a packet to let other spectators know that you have a missing beatmap"""
        self.enqueue(ClientPackets.CANT_SPECTATE)

    def send_frames(
        self,
        action: ReplayAction,
        frames: list[ReplayFrame],
        score_frame: ScoreFrame | None = None,
        seed: int = 0,
    ) -> None:
        """
        This will send a `SPECTATE_FRAMES` packet to the server, which gets broadcasted to all of your spectators.
        Note that this will not work, if nobody is spectating you.
        """
        if not self.player.spectators:
            self.logger.warning(
                "Failed to send frames, because no spectators were found."
            )
            return

        if self.spectating:
            action = ReplayAction.WatchingOther
            extra = self.spectating.id
        else:
            extra = seed

        stream = StreamOut()
        stream.s32(extra)
        stream.u16(len(frames))
        [stream.write(frame.encode()) for frame in frames]
        stream.u8(action.value)

        if score_frame:
            stream.write(score_frame.encode())

        self.enqueue(ClientPackets.SPECTATE_FRAMES, stream.get())

    def join_lobby(self) -> None:
        """Join the multiplayer lobby"""
        if self.in_lobby:
            return

        self.enqueue(ClientPackets.JOIN_LOBBY)
        self.in_lobby = True

    def leave_lobby(self) -> None:
        """Leave the multiplayer lobby"""
        if not self.in_lobby:
            return

        self.enqueue(ClientPackets.PART_LOBBY)
        self.in_lobby = False

    def create_match(self, match: Match) -> None:
        """Create a multiplayer match"""
        match.game = self.game
        self.enqueue(ClientPackets.CREATE_MATCH, match.encode())

    def join_match(self, match: Match | int, password: str = "") -> None:
        """Join a multiplayer match"""
        stream = StreamOut()
        stream.s32(match.id if isinstance(match, Match) else match)
        stream.string(password)

        self.enqueue(ClientPackets.JOIN_MATCH, stream.get())

    def leave_match(self) -> None:
        """Leave the current multiplayer match"""
        if not self.match:
            return

        self.enqueue(ClientPackets.PART_MATCH)
        self.match = None
