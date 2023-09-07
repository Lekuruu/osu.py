from typing import List, Callable, Optional
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class Task:
    function: Callable
    interval: float
    loop: bool
    last_call: datetime
    threaded: bool


class TaskManager:
    """### TaskManager

    Used to run any task syncronously or asyncronously inside a thread.\n
    Example of registering a task that runs every minute:
    >>> @game.tasks.register(minutes=1, loop=True)
    >>> def example_task():
    >>>     ...
    """

    def __init__(self, game) -> None:
        self.logger = logging.getLogger("tasks")
        self.tasks: List[Task] = []
        self.game = game

    def register(self, *, seconds=0, minutes=0, hours=0, loop=False, threaded=False):
        """Register a task

        `seconds`, `minutes`, `hours`: Specify when this task should run

        `loop`: If set to `True`, the task will loop itself in the specified time interval

        `threaded`: This will run the task inside a thread.
            Note that this is **not recommended**, since interactions with the game client were not designed to be done asyncronous.
            I will try to fix this issue in the future.
        """

        def wrapper(f: Callable):
            total = (seconds) + (minutes * 60) + (hours * 60 * 60)
            self.tasks.append(
                Task(
                    function=f,
                    interval=total,
                    loop=loop,
                    last_call=datetime.now(),
                    threaded=threaded,
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

                if not task.loop:
                    self.tasks.remove(task)

                try:
                    self.logger.debug(f"Trying to run task: '{task.function.__name__}'")

                    if not task.threaded:
                        task.function()
                        self.logger.debug(
                            f"Task '{task.function.__name__}' was successfully executed."
                        )
                        continue

                    # if (
                    #     task.current_thread is not None
                    #     and not task.current_thread.done()
                    # ):
                    # Thread is still running
                    # TODO

                    future = self.game.executor.submit(task.function)
                    future.add_done_callback(self._thread_callback)

                    self.logger.debug(
                        f"Task '{task.function.__name__}' was submitted to executor."
                    )

                except Exception as exc:
                    self.logger.error(
                        f"Failed to run '{task.function.__name__}' task: {exc}",
                        exc_info=exc,
                    )

        self.logger.debug("Done.")

    def _thread_callback(self, future: Future) -> None:
        ...  # TODO
