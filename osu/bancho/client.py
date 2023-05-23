
from typing import Optional, List
from datetime import datetime

from ..objects.collections import Players
from ..objects.player      import Player
from ..objects.status      import Status

from ..game import Game

from .constants import ClientPackets, Privileges
from .streams   import StreamOut

import requests
import logging
import time

class BanchoClient:

    """BanchoClient
    ---------------

    Parameters:
        `user_id`: int
            User id associated with this account.
            (Sent in logout packet)

        `player`: osu.objects.player.Player
            Player associated with this account

        `spectating`: osu.objects.player.Player
            Player that is currently being spectated

        `players`: osu.objects.collections.Players
            All players that are currently online

        `privileges`: list[osu.bancho.constants.Privileges]
            Privileges for this account

        `friends`: list[int]

        `game`: osu.game.Game

        `connected`: bool

        `retry`: bool
    
    Functions:
        TODO
    """

    def __init__(self, game: Game) -> None:
        self.game = game

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'osu!',
            'osu-version': self.game.version
        }

        self.logger = logging.getLogger(f'bancho-{game.version}')

        self.url = f'https://c.{game.server}'

        self.user_id = -1
        self.connected = False
        self.retry = True
        self.token = ''

        self.spectating: Optional[Player] = None
        self.player:     Optional[Player] = None

        self.players = Players()

        self.ping_count = 0
        self.protocol   = 0

        self.privileges: List[Privileges] = []
        self.friends: List[int] = []

        self.last_action = datetime.now().timestamp()
        self.fast_read = False

        self.silenced = False

        self.min_idletime = 1
        self.max_idletime = 5

        self.queue = []

    @property
    def status(self) -> Status:
        if not self.player:
            return Status()
        return self.player.status
    
    @property
    def idle_time(self) -> float:
        """Time between now and the last request"""
        return datetime.now().timestamp() - self.last_action

    @property
    def request_interval(self) -> int:
        """Time between requests"""

        if self.fast_read:
            return 0

        interval = 1

        if self.game.tourney:
            return interval

        if not self.spectating:
            interval *= 1 + self.idle_time / 10
            interval *= 1 + self.ping_count

        interval = min(self.max_idletime, max(self.min_idletime, interval))

        return interval
    
    def run(self):
        self.connect()

        while self.connected:
            time.sleep(self.request_interval)
            self.dequeue()

        if self.retry:
            self.logger.error('Retrying in 15 seconds...')
            time.sleep(15)
            self.game.run(retry=True)

    def connect(self):
        data = f'{self.game.username}\r\n{self.game.password_hash}\r\n{self.game.client}\r\n'

        response = self.session.post(self.url, data=data.encode())
        
        if not response.ok:
            # Connection was refused
            self.connected = False
            self.retry = True
            self.logger.error(f'[{response.url}]: Connection was refused ({response.status_code})')
            return
        
        if not (token := response.headers.get('cho-token')):
            # Failed to get token
            self.connected = False
            self.retry     = False
            # Get error message
            self.game.packets.data_received(response.content, self.game)
            return
        
        self.connected = True
        self.token = token

        self.session.headers['osu-token'] = self.token

        self.game.packets.data_received(response.content, self.game)

    def dequeue(self) -> Optional[requests.Response]:
        """Send a request to bancho, empty the queue and handle incoming packets"""

        if not self.connected:
            return
        
        if not self.queue:
            # Queue is empty, sending ping
            self.ping()
            self.ping_count += 1
        else:
            self.ping_count = 0

        response = self.session.post(self.url, data=b''.join(self.queue))

        if not response.ok:
            # Connection was refused
            self.connected = False
            self.retry = True
            self.logger.error(f'[{response.request.url}]: Connection was refused ({response.status_code})')
            return

        self.game.packets.data_received(response.content, self.game)

        if len(response.content) > 10000:
            self.fast_read = True
        else:
            self.fast_read = False
        
        # DEBUG: Should be removed
        self.logger.debug(f'Interval: {self.request_interval}')
        self.logger.debug(f'Ping count: {self.ping_count}')
        self.logger.debug(f'Idle time: {self.idle_time}')
        self.logger.debug(f'Content length: {len(response.content)}')

        self.last_action = datetime.now().timestamp()
        self.queue = []

        return response

    def exit(self):
        """Send logout packet to bancho, and disconnect."""

        self.enqueue(
            ClientPackets.LOGOUT, 
            int(0).to_bytes(4, 'little')
        )
        self.dequeue()
        self.connected = False
        self.retry     = False

    def enqueue(self, packet: ClientPackets, data: bytes = b'') -> bytes:
        """Send a packet to the queue
        
        Args:
            `packet`: osu.bancho.constants.ClientPackets

            `data`: bytes
        """

        stream = StreamOut()

        # Construct header
        stream.u16(packet.value)
        stream.bool(False)
        stream.u32(len(data))

        # Write payload
        stream.write(data)

        self.logger.debug(f'Sending {packet.name} -> "{data}"')

        # Append to queue
        self.queue.append(stream.get())

        return stream.get()

    def unsilence(self):
        if not self.silenced:
            return

        self.player.silenced = False
        self.silenced = False

        self.logger.info('You can now talk again.')

    def ping(self):
        self.enqueue(ClientPackets.PING)

    def request_presence(self, ids: List[int]):
        stream = StreamOut()
        stream.intlist(ids)

        self.enqueue(ClientPackets.USER_PRESENCE_REQUEST, stream.get())
        self.dequeue()

    def request_stats(self, ids: List[int]):
        stream = StreamOut()
        stream.intlist(ids)

        self.enqueue(ClientPackets.USER_STATS_REQUEST, stream.get())
        self.dequeue()
