from osu import Game
import logging

logging.basicConfig(
    level=logging.DEBUG, format="[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s"
)

logger = logging.getLogger("tests")
logger.info("Performing tests...")

game = Game(
    username="testuser",
    password="testpass",
    version=1337,
    server="ppy.sh",
    stream="stable40",
)

async_task_success = False
task_success = False


def tasks():
    logger.info("Testing tasks...")

    @game.tasks.register(seconds=0)
    def test_task():
        global task_success
        task_success = True

    @game.tasks.register(seconds=0, threaded=True)
    def test_task_async():
        global async_task_success
        async_task_success = True

    # Bancho needs to be connected for tasks to run
    game.bancho.connected = True

    # Execute test_task
    game.tasks.execute()

    if not task_success:
        logger.error("Syncronous task failed.")
        exit(1)

    # Execute test_task_async
    game.tasks.execute()

    # Wait for thread
    for thread in game.tasks.executor._threads:
        thread.join(timeout=1)

    if not async_task_success:
        logger.error("Asyncronous task failed.")
        exit(1)

    logger.info("Tasks were executed successfully.")
    game.bancho.connected = False


def packets():
    logger.info("Simulating login reply packet...")
    game.packets.data_received(
        data=b"\x05\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00", game=game
    )

    if game.bancho.player.id != 1:
        logger.error("Login reply packet failed.")
        exit(1)

    # TODO: More packets?


tasks()
packets()
