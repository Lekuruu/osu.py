
from typing import Optional, List

from ..game import Game

import requests
import logging

class WebAPI:

    """WebAPI
    -----------

    Functions:
        - `check_updates`
        - `connect`
        - `verify`
        - `get_session`
        - `get_backgrounds`
        - `get_friends`

    `Note`: I do not plan on adding score/beatmap submission!
    """

    def __init__(self, game: Game) -> None:
        """
        Args:
            `game`: osu.game.Game
        """

        self.game = game

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'osu!',
            'osu-version': self.game.version
        }

        self.logger = logging.getLogger(f'osu!api-{game.version}')

        self.url = f'https://osu.{self.game.server}'

    def check_updates(self) -> Optional[dict]:
        self.logger.info('Checking for updates...')

        response = self.session.get('https://osu.ppy.sh/web/check-updates.php', params={
            'action': 'check',
            'stream': self.game.stream.lower(),
            'time': self.game.time
        })

        if not response.ok:
            self.logger.error(f'Failed to get updates ({response.status_code})')
            return None

        if 'fallback' in response.text:
            self.logger.error(f'Failed to get updates: "{response.text}"')
            return None

        return response.json()
    
    def connect(self, retry=False) -> bool:
        """This will perform a request on `/web/bancho_connect.php`.

        Args:
            `retry`: bool
                Used inside the request as a parameter (optional)

        Returns -> bool
            If the connection was successful.
        """
        
        self.logger.info('Connecting to bancho...')

        response = self.session.get(f'{self.url}/web/bancho_connect.php', params={
            'v': self.game.version,
            'u': self.game.username,
            'h': self.game.password_hash,
            'fx': 'fail', # dotnet version
            'ch': str(self.game.client.hash),
            'retry': int(retry)
        })

        if not response.ok:
            self.logger.error(f'Error on login: {requests.status_codes._codes[response.status_code][0].capitalize()}')
            return False

        if 'error' in response.text:
            self.logger.error(f'Error on login: {response.text.removeprefix("error: ")}')

            if 'verify' in response.text:
                self.verify(str(self.game.client.hash))
                return False

        return True

    def verify(self, hash: str) -> requests.Response:
        """This will print out a url, where the user can verify this client.\n
        After that, it will exit.

        Args:
            `hash`: str
                The client hash, that will be passed to the url.
        """

        self.logger.info('Verification required.')
        self.logger.info(f'{self.url}/p/verify?u={self.game.username.replace(" ", "%20")}&reason=bancho&ch={hash}')
        self.logger.info('You only need to do this once.')
        exit(0)

    def get_session(self) -> requests.Response:
        """Perform a request on `/web/osu-session.php`.\n
        I don't know what this actually does.\n
        My guess is that it checks, if somebody is already online with this account.
        """ # TODO

        response = self.session.post(f'{self.url}/web/osu-session.php', files={
            'u': self.game.username,
            'h': self.game.password_hash,
            'action': 'check'
        })

        return response
    
    def get_backgrounds(self) -> Optional[dict]:
        """This will perform a request on `/web/osu-getseasonal.php`."""

        response = self.session.get(f'{self.url}/web/osu-getseasonal.php')

        if response.ok:
            return response.json()

    def get_friends(self) -> List[int]:
        """This will perform a request on `/web/osu-getfriends.php`."""

        response = self.session.get(f'{self.url}/web/osu-getfriends.php', params={
            'u': self.game.username,
            'h': self.game.password_hash
        })

        if response.ok:
            return [
                int(id) 
                for id in response.text.split('\n')
                if id.isdigit()
            ]

        return []
