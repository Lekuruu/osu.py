from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from queue import Queue

from osu.bancho.constants import ClientPackets

from ..bancho.client import BanchoClient as HTTPBanchoClient
from ..bancho.constants import Privileges, ServerPackets
from ..bancho.streams import StreamIn, StreamOut
from ..bancho.packets import Packets

from ..objects.collections import Players, Channels
from ..objects.player import Player

if TYPE_CHECKING:
    from .game import TcpGame

import logging
import socket
import gzip
import time


class TcpBanchoClient(HTTPBanchoClient):
    def __init__(self, game: "TcpGame", ip: str, port: int) -> None:
        self.game = game

        self.logger = logging.getLogger(f"tcp-bancho-{game.version}")
        self.logger.disabled = game.logger.disabled

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.ip = ip

        self.user_id = -1
        self.connected = False
        self.retry = True

        self.spectating: Optional[Player] = None
        self.player: Optional[Player] = None

        self.channels = Channels()
        self.players = Players(game)
        self.queue = Queue()

        self.ping_count = 0
        self.protocol = 0

        self.privileges: Privileges = Privileges.Normal
        self.friends: List[int] = []

        self.last_action = datetime.now().timestamp()
        self.silenced = False
        self.in_lobby = False

    def run(self):
        """Run the client loop"""
        self.connect()

        while self.connected:
            try:
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

    def connect(self):
        """Perform the initial connection to the server"""
        login_data = f"{self.game.username}\r\n{self.game.password_hash}\r\n{self.game.client}\r\n"

        try:
            self.socket.connect((self.ip, self.port))
            self.socket.send(login_data.encode())
            self.connected = True
        except ConnectionRefusedError:
            self.logger.error("Connection refused by the server.")

    def process_packets(self) -> None:
        """Process incoming packets from the server"""
        packet_header = StreamIn(self.socket.recv(7))

        if packet_header.eof():
            return

        packet_id = packet_header.u16()
        compression = packet_header.bool()
        packet_size = packet_header.u32()
        packet_data = self.socket.recv(packet_size)

        if compression:
            packet_data = gzip.decompress(packet_data)

        packet, stream = ServerPackets(packet_id), StreamIn(packet_data)

        self.logger.debug(f'Received packet {packet.name} -> "{stream.get()}"')
        self.game.packets.packet_received(packet, stream, self.game)

    def enqueue(
        self, packet: ClientPackets, data: bytes = b"", dequeue: bool = False
    ) -> bytes:
        """Send a packet to the server and dequeue"""
        stream = StreamOut()

        # Construct header
        stream.u16(packet.value)
        stream.bool(False)
        stream.u32(len(data))
        stream.write(data)

        self.logger.debug(f'Sending {packet.name} -> "{data}"')
        self.socket.send(stream.get())
        self.last_action = datetime.now().timestamp()

        if dequeue:
            self.dequeue()

        return stream.get()

    def dequeue(self) -> None:
        """Process all incoming packets from the server"""
        if not self.connected:
            return

        try:
            self.process_packets()
        except OverflowError as e:
            self.logger.error(f'Failed to process packets: "{e}"')
            self.connected = False
            self.retry = True

    def exit(self):
        """Send logout packet to bancho, and disconnect."""
        try:
            self.retry = False
            self.connected = False
            self.enqueue(ClientPackets.LOGOUT, int(0).to_bytes(4, "little"))
        except BrokenPipeError:
            pass
