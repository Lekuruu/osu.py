from typing import Optional, Tuple, List
from datetime import datetime
from queue import Queue

from osu.bancho.constants import ClientPackets

from ..bancho.client import BanchoClient as HTTPBanchoClient
from ..bancho.constants import Privileges, ServerPackets
from ..bancho.streams import StreamIn, StreamOut
from ..bancho.packets import Packets

from ..objects.collections import Players, Channels
from ..objects.player import Player
from .game import TcpGame

import logging
import socket
import gzip
import time


class TcpBanchoClient(HTTPBanchoClient):
    def __init__(self, game: TcpGame, ip: str, port: int) -> None:
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

    def get_packet(self) -> Tuple[int, StreamIn]:
        """Get a packet from the server"""
        packet_header = StreamIn(self.socket.recv(7))

        packet_id = packet_header.u16()
        compression = packet_header.bool()
        packet_size = packet_header.u32()
        packet_data = self.socket.recv(packet_size)

        if compression:
            packet_data = gzip.decompress(packet_data)

        return ServerPackets(packet_id), StreamIn(packet_data)

    def enqueue(
        self, packet: ClientPackets, data: bytes = b"", dequeue: bool = True
    ) -> bytes:
        """Send a packet to the queue and dequeue"""
        stream = StreamOut()

        # Construct header
        stream.u16(packet.value)
        stream.bool(False)
        stream.u32(len(data))
        stream.write(data)

        self.logger.debug(f'Sending {packet.name} -> "{data}"')

        # Append to queue
        self.queue.put(stream.get())

        if dequeue:
            self.dequeue()

        return stream.get()

    def dequeue(self) -> None:
        """Send a request to bancho, empty the queue and handle incoming packets"""
        if not self.connected and self.queue.empty():
            return

        data = b""

        while not self.queue.empty():
            data += self.queue.get()

        if data:
            self.socket.send(data)
            self.last_action = datetime.now().timestamp()

        if not self.connected:
            return

        try:
            packet, stream = self.get_packet()
        except OverflowError as e:
            self.logger.error(f'Failed to receive packet: "{e}"')
            self.connected = False
            self.retry = True
            return

        self.logger.debug(f'Received packet {packet.name} -> "{stream.get()}"')

        self.game.packets.packet_received(packet, stream, self.game)

    def exit(self):
        """Send logout packet to bancho, and disconnect."""
        try:
            self.retry = False
            self.connected = False
            self.enqueue(ClientPackets.LOGOUT, int(0).to_bytes(4, "little"))
        except BrokenPipeError:
            pass
