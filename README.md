# osu.py

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL%203.0-green)](https://github.com/Lekuruu/osu.py/blob/main/LICENSE)

osu.py is a python library that emulates part of the online functionality of the osu! stable client.
This is still a work in progress, but I decided to release it anyways.

**IMPORTANT:**
Use this library at your own risk! I am not responsible for anything that can happen to your account. If you want to test it out on a private server, you can set the `server` attribute when initializing the client.

You can install this package with pip:

```shell
pip install osu
```

Or build it manually:

```shell
git clone https://github.com/Lekuruu/osu.py.git
cd osu.py
python setup.py install
```

## Features

- [x] Receiving player stats
- [x] Sending/Receiving chat messages
- [x] Up to 12 clients (Tournament Client)
- [x] Spectating
- [x] Avatars
- [x] Comments
- [x] Replays
- [x] Scores/Leaderboards
- [ ] osu!direct
- [ ] Documentation
- [ ] (Multiplayer)

## Example

Here is a small example of how to use this package:

```python
from osu.constants import ServerPackets
from osu.objects import Player
from osu import Game

# Initialize the game class
game = Game(
  USERNAME,
  PASSWORD
)

# Simple message handler
@game.events.register(ServerPackets.SEND_MESSAGE)
def on_message(sender: Player, message: str, target: Player):
  if message.startswith('!ping'):
    sender.send_message('pong!')

# Run the game
game.run()
```

[This project](https://github.com/Lekuruu/osu-recorder) is also a good example
and it was also the reason why I even started this project.

---

If you have any questions, feel free to contact me on discord: `lekuru`
