from typing import List, Dict, Callable

from .bancho.constants import ServerPackets


class EventHandler:

    """EventHandler
    ---------------

    This class is used to make it easier to handle packets.

    After a packet has been received from the server,
    it will call every event associated with that packet.

    Example of how a event can be registered and used:
    >>> game = Game(...)
    >>>
    >>> @game.events.register(ServerPackets.SEND_MESSAGE)
    >>> def message_handler(sender, message, target):
    >>>     print(message)
    """

    def __init__(self) -> None:
        self.handlers: Dict[ServerPackets, List[Callable]] = {}

    def register(self, packet: ServerPackets):
        def wrapper(f: Callable):
            if packet in self.handlers:
                self.handlers[packet].append(f)
            else:
                self.handlers[packet] = [f]
            return f

        return wrapper

    def call(self, packet: ServerPackets, *args):
        if packet in self.handlers:
            for handler in self.handlers[packet]:
                handler(*args)
