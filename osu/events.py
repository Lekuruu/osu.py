from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable

from .bancho.constants import ServerPackets


class EventHandler:

    """EventHandler
    ---------------

    This class is used to make it easier to handle packets.

    After a packet has been received from the server,
    it will call every event associated with that packet.

    Example of how an event can be registered and used:
    >>> game = Game(...)
    >>>
    >>> @game.events.register(ServerPackets.SEND_MESSAGE)
    >>> def message_handler(sender: Player, message: str, target: Player|Channel):
    >>>     print(message)
    """

    def __init__(self) -> None:
        self.handlers: Dict[ServerPackets, List[Callable]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

    def register(self, packet: ServerPackets, threaded: bool = False):
        """Register an event, that will be executed once the given server packet has been received."""

        def wrapper(f: Callable):
            if threaded:
                f = self._submit_future(f)
            if packet in self.handlers:
                self.handlers[packet].append(f)
            else:
                self.handlers[packet] = [f]
            return f

        return wrapper

    def call(self, packet: ServerPackets, *args):
        """Call all events for the given packet"""
        if packet in self.handlers:
            for handler in self.handlers[packet]:
                handler(*args)

    def _submit_future(self, f: Callable) -> Callable:
        def execute(*args):
            if self.executor._shutdown:
                return
            future = self.executor.submit(f, *args)
            return future

        return execute
