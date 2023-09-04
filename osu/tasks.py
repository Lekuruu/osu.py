from typing import List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging


@dataclass
class Task:
    function: Callable
    interval: float
    loop: bool
    last_call: datetime


class TaskManager:
    """### TaskManager

    Used to run any task syncronously, because threading can mess up the game sometimes.\n
    Example of registering a task that runs every minute:
    >>> @game.tasks.register(minutes=1, loop=True)
    >>> def example_task():
    >>>     ...
    """

    def __init__(self, game) -> None:
        self.logger = logging.getLogger("tasks")
        self.tasks: List[Task] = []
        self.game = game

    def register(self, *, seconds=0, minutes=0, hours=0, loop=True, args=[], kwargs={}):
        """Register a task"""

        def wrapper(f: Callable):
            total = (seconds) + (minutes * 60) + (hours * 60 * 60)
            self.tasks.append(
                Task(
                    function=f,
                    interval=total,
                    loop=loop,
                    last_call=datetime.now(),
                )
            )
            return f

        return wrapper

    def execute(self) -> None:
        """Execute every currently registered task"""
        if not self.game.bancho.connected:
            return

        self.logger.debug("Running tasks...")

        for task in self.tasks:
            last_call = (datetime.now() - task.last_call).total_seconds()

            if last_call >= task.interval:
                task.last_call = datetime.now()

                try:
                    self.logger.debug(f"Trying to run task: {task.function}")
                    task.function()
                except Exception as exc:
                    self.logger.error(f"Failed to run task: {exc}", exc_info=exc)

        self.logger.debug("Done.")
