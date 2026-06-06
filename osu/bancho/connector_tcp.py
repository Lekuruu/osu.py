from datetime import datetime

from .connector import BanchoConnector
from .constants import ServerPackets
from .streams import StreamIn

import socket
import select
import gzip


class TcpBanchoConnector(BanchoConnector):
    dequeue_on_enqueue = False

    def __init__(self, ip: str, port: int = 13381) -> None:
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

    def connect(self) -> None:
        """Perform the initial connection to the server."""
        login_data = (
            f"{self.game.username}\r\n"
            f"{self.game.password_hash}\r\n"
            f"{self.game.client}\r\n"
        )

        try:
            self.socket.connect((self.ip, self.port))
            self.socket.send(login_data.encode())
            self.bancho.connected = True
        except ConnectionRefusedError:
            self.bancho.connected = False
            self.bancho.retry = True
            self.bancho.logger.error("Connection refused by the server.")

    def send(self, data: bytes, dequeue: bool) -> None:
        if not self.bancho.connected:
            return

        self.socket.sendall(data)
        self.bancho.last_action = datetime.now().timestamp()

        if dequeue:
            self.receive()

    def process_packets(self) -> None:
        """Process incoming packets from the server."""
        packet_header = StreamIn(self.socket.recv(7, socket.MSG_WAITALL))

        if packet_header.eof():
            self.bancho.connected = False
            return

        packet_id = packet_header.u16()
        compression = packet_header.bool()
        packet_size = packet_header.u32()
        packet_data = self.socket.recv(packet_size, socket.MSG_WAITALL)

        if compression:
            packet_data = gzip.decompress(packet_data)

        packet, stream = ServerPackets(packet_id), StreamIn(packet_data)

        self.bancho.logger.debug(f'Received packet {packet.name} -> "%s"', packet_data)
        self.game.packets.packet_received(packet, stream, self.game)

    def receive(self) -> None:
        """Process incoming packets from the server."""
        if not self.bancho.connected:
            return

        try:
            self.process_packets()

            while self.bancho.connected and self.has_pending_data():
                self.process_packets()
        except OverflowError as exc:
            self.bancho.logger.error(f'Failed to process packets: "{exc}"')
            self.bancho.connected = False
            self.bancho.retry = True

    def has_pending_data(self) -> bool:
        readable, _, _ = select.select([self.socket], [], [], 0)
        return bool(readable)

    def close(self) -> None:
        try:
            self.socket.close()
        except OSError:
            pass
