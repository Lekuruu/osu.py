# osu.py

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/Lekuruu/osu.py/blob/main/LICENSE)

osu.py is a python library that emulates part of the online functionality of the osu! stable client.

**IMPORTANT:**
Use this library at your own risk! I am not responsible for any unexpected behavior of the client or anything that can happen to your account. If you want to test it out on a custom server, you can set the `server` attribute when initializing the client.

You can install this package with pip:

```shell
pip install osu
```

Or build it manually:

```shell
git clone https://github.com/Lekuruu/osu.py.git
cd osu.py
pip install setuptools
python setup.py install
```

## Features

- [x] Receiving player stats
- [x] Sending/Receiving chat messages
- [x] Spectating
- [x] Avatars
- [x] Comments
- [x] Replays
- [x] Scores/Leaderboards
- [x] Tournament client behaviour
- [x] Direct Search
- [x] Direct Download
- [ ] Multiplayer
- [ ] Documentation

## Example

Here is a small example of how to use this package:

```python
from osu.bancho.constants import ServerPackets
from osu.objects import Player
from osu import Game
import logging

# Enable extended logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s'
)

# Initialize the game class
game = Game(
  USERNAME,
  PASSWORD
)

# Simple message handler
@game.events.register(ServerPackets.SEND_MESSAGE)
def on_message(sender: Player, message: str, target: Player):
  if message.startswith('?ping'):
    sender.send_message('pong!')

# Run the game
game.run()
```

You can also run tasks, independent of server actions:

```python
# Example of a task, running every minute
@game.tasks.register(minutes=1, loop=True)
def example_task():
  ...
```

For a more in-depth example, please view [this project](https://github.com/lekuruu/osu-recorder).

---

If you have any questions, feel free to contact me on discord: `lekuru`
