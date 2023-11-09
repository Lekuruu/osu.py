from typing import List, Dict, Callable
from copy import copy

from ..objects.replays import ScoreFrame, ReplayFrame
from ..objects.beatmap import BeatmapInfo
from ..objects.channel import Channel
from ..objects.player import Player
from ..game import Game

from .streams import StreamIn
from .constants import (
    ServerPackets,
    ReplayAction,
    StatusAction,
    LoginError,
    Privileges,
    Mode,
    Mods,
)

import threading
import zlib
import time


class PacketHandler:
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

    def data_received(self, data: bytes, game: Game):
        stream = StreamIn(data)

        while not stream.eof():
            packet = ServerPackets(stream.u16())
            compression = stream.bool()  # unused
            data = stream.read(stream.u32())

            if compression:
                # Compression was used in very early versions of bancho
                data = zlib.decompress(data)

            game.logger.debug(f'Received packet {packet.name} -> "{data}"')

            # Handling packet
            self.packet_received(packet, StreamIn(data), game)

            # Reset stream
            stream = StreamIn(stream.readall())

    def packet_received(self, packet: ServerPackets, data: StreamIn, game: Game):
        if packet in self.handlers:
            for handler in self.handlers[packet]:
                try:
                    # TODO: Add threading
                    handler(data, game)
                except Exception as exc:
                    game.logger.error(
                        f"Error while executing {handler}: {exc}", exc_info=exc
                    )
        else:
            game.logger.warning(f'No handler found for "{packet.name}"')


Packets = PacketHandler()


@Packets.register(ServerPackets.PROTOCOL_VERSION)
def protocol_version(stream: StreamIn, game: Game):
    game.bancho.protocol = stream.s32()
    game.events.call(ServerPackets.PROTOCOL_VERSION, game.bancho.protocol)


@Packets.register(ServerPackets.RESTART)
def server_restart(stream: StreamIn, game: Game):
    timeout = stream.s32() / 1000

    game.logger.warning(f"Bancho is restarting. Retrying in {timeout} seconds...")
    game.bancho.connected = False
    game.bancho.retry = True

    game.events.call(ServerPackets.RESTART, game.bancho.protocol)

    time.sleep(timeout)


@Packets.register(ServerPackets.USER_ID)
def login_reply(stream: StreamIn, game: Game):
    response = stream.s32()

    if response < 0:
        # Got a login error
        try:
            error = LoginError(response)
        except ValueError:
            error = None

        game.logger.error(f"Login error: {error.name}")
        game.logger.error(error.description)
        game.bancho.connected = False
        game.bancho.retry = False

        if error == LoginError.SERVER_ERROR:
            game.bancho.retry = True

        elif error == LoginError.VERIFICATION_NEEDED:
            game.api.verify(game.client.hash)

        return

    game.logger.info(f"Logged in with id: {response}")
    game.bancho.user_id = response

    game.bancho.player = Player(response, game.username, game)
    game.bancho.players.add(game.bancho.player)

    game.bancho.fast_read = True

    game.events.call(ServerPackets.USER_ID, response)


@Packets.register(ServerPackets.PONG)
def pong(stream: StreamIn, game: Game):
    game.events.call(ServerPackets.PONG)


@Packets.register(ServerPackets.ACCOUNT_RESTRICTED)
def restricted(stream: StreamIn, game: Game):
    game.logger.error("You have been banned.")
    game.events.call(ServerPackets.ACCOUNT_RESTRICTED)
    game.bancho.connected = False
    game.bancho.retry = False


@Packets.register(ServerPackets.PRIVILEGES)
def privileges(stream: StreamIn, game: Game):
    game.bancho.privileges = Privileges(stream.s32())
    game.events.call(ServerPackets.PRIVILEGES, game.bancho.privileges)


@Packets.register(ServerPackets.FRIENDS_LIST)
def friends(stream: StreamIn, game: Game):
    game.bancho.friends = stream.intlist()
    game.events.call(ServerPackets.FRIENDS_LIST, game.bancho.friends)


@Packets.register(ServerPackets.MAIN_MENU_ICON)
def menu_icon(stream: StreamIn, game: Game):
    image, link = stream.string().split("|")
    game.events.call(ServerPackets.MAIN_MENU_ICON, image, link)


@Packets.register(ServerPackets.VERSION_UPDATE)
def version_update(stream: StreamIn, game: Game):
    game.logger.info("Bancho requested a version update.")
    game.events.call(ServerPackets.VERSION_UPDATE)


@Packets.register(ServerPackets.VERSION_UPDATE_FORCED)
def version_update_forced(stream: StreamIn, game: Game):
    game.logger.warning("Bancho forced a version update.")
    game.events.call(ServerPackets.VERSION_UPDATE_FORCED)


@Packets.register(ServerPackets.GET_ATTENTION)
def attension(stream: StreamIn, game: Game):
    game.events.call(ServerPackets.GET_ATTENTION)


@Packets.register(ServerPackets.NOTIFICATION)
def notification(stream: StreamIn, game: Game):
    message = stream.string()
    game.logger.info(f'Notification from bancho: "{message}"')
    game.events.call(ServerPackets.NOTIFICATION, message)


@Packets.register(ServerPackets.USER_PRESENCE)
def presence(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        # Add new player, if not found in collection
        game.bancho.players.add(player := Player(user_id, game=game))

    player.name = stream.string()
    player.timezone = stream.u8() - 24
    player.country_code = stream.u8()

    b = stream.u8()  # Contains privileges and play mode

    player.privileges = Privileges(b & -255)
    player.status.mode = Mode(max(0, min(3, (b & 224) >> 5)))

    player.longitude = stream.float()
    player.latitude = stream.float()
    player.rank = stream.s32()

    game.bancho.fast_read = True

    game.events.call(ServerPackets.USER_PRESENCE, player)


@Packets.register(ServerPackets.USER_STATS)
def stats(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        # Add new player, if not found in collection
        game.bancho.request_presence([user_id])
        game.bancho.players.add(player := Player(user_id, game=game))

    player.last_status = copy(player.status)

    # Status
    player.status.action = StatusAction(stream.u8())
    player.status.text = stream.string()
    player.status.checksum = stream.string()
    player.status.mods = Mods(stream.u32())
    player.status.mode = Mode(max(0, min(3, stream.u8())))
    player.status.beatmap_id = stream.s32()

    # Stats
    player.rscore = stream.s64()
    player.acc = stream.float()
    player.playcount = stream.s32()
    player.tscore = stream.s64()
    player.rank = stream.s32()
    player.pp = stream.s16()

    game.bancho.fast_read = True

    game.events.call(ServerPackets.USER_STATS, player)


@Packets.register(ServerPackets.USER_PRESENCE_BUNDLE)
def presence_bundle(stream: StreamIn, game: Game):
    user_ids = stream.intlist()

    for id in user_ids:
        if not (game.bancho.players.by_id(id)):
            # Add player if not found
            game.bancho.players.add(Player(id, game=game))

    game.bancho.fast_read = True

    game.events.call(ServerPackets.USER_PRESENCE_BUNDLE, user_ids)


@Packets.register(ServerPackets.USER_PRESENCE_SINGLE)
def presence_single(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (game.bancho.players.by_id(user_id)):
        # Add player if not found
        game.bancho.players.add(Player(user_id, game=game))

    game.events.call(ServerPackets.USER_PRESENCE_SINGLE, user_id)


@Packets.register(ServerPackets.USER_LOGOUT)
def logout(stream: StreamIn, game: Game):
    if not (player := game.bancho.players.by_id(stream.s32())):
        return

    if player is game.bancho.spectating:
        game.logger.info(f"Stopped spectating {player.name}.")
        game.bancho.spectating = None

    game.bancho.players.remove(player)

    game.events.call(ServerPackets.USER_LOGOUT, player)


@Packets.register(ServerPackets.SEND_MESSAGE)
def message(stream: StreamIn, game: Game):
    sender = stream.string()
    message = stream.string()
    target = stream.string()
    sender_id = stream.s32()

    # Find player
    if not (player := game.bancho.players.by_id(sender_id)):
        # Try to find sender by name
        if not (player := game.bancho.players.by_name(sender)):
            return

    if not player.loaded:
        # Presence missing
        player.request_presence()

    sender = player

    # Find target
    if target.startswith("#"):
        # Public message
        if not (channel := game.bancho.channels.get(target)):
            return

        target = channel
    else:
        # Private message
        if not (player := game.bancho.players.by_name(target)):
            return

        if not player.loaded:
            # Presence missing
            player.request_presence()

        target = player

    if not game.disable_chat:
        target.logger.info(
            f'<{sender.name}{f" ({sender_id})" if sender_id else ""}> [{target.name}]: "{message}"'
        )

    game.bancho.fast_read = True
    game.events.call(ServerPackets.SEND_MESSAGE, sender, message, target)


@Packets.register(ServerPackets.SPECTATOR_JOINED)
def spectator_joined(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    player.cant_spectate = False

    game.bancho.player.spectators.add(player)

    game.events.call(ServerPackets.SPECTATOR_JOINED, player)


@Packets.register(ServerPackets.SPECTATOR_LEFT)
def spectator_left(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    if player not in game.bancho.player.spectators:
        return

    game.bancho.player.spectators.remove(player)

    game.events.call(ServerPackets.SPECTATOR_LEFT, player)


@Packets.register(ServerPackets.FELLOW_SPECTATOR_JOINED)
def fellow_spectator_joined(stream: StreamIn, game: Game):
    if not game.bancho.spectating:
        return

    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    game.bancho.spectating.spectators.add(player)

    game.events.call(ServerPackets.FELLOW_SPECTATOR_JOINED, player)


@Packets.register(ServerPackets.FELLOW_SPECTATOR_LEFT)
def fellow_spectator_left(stream: StreamIn, game: Game):
    if not game.bancho.spectating:
        return

    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    if player not in game.bancho.spectating.spectators:
        return

    game.bancho.spectating.spectators.remove(player)

    game.events.call(ServerPackets.SPECTATOR_LEFT, player)


@Packets.register(ServerPackets.SPECTATE_FRAMES)
def frames(stream: StreamIn, game: Game):
    if not game.bancho.spectating:
        return

    extra = stream.s32()
    frames = [ReplayFrame.decode(stream) for _ in range(stream.u16())]
    action = ReplayAction(stream.u8())

    try:
        score_frame = ScoreFrame.decode(stream)
    except OverflowError:
        score_frame = None

    game.events.call(ServerPackets.SPECTATE_FRAMES, action, frames, score_frame, extra)


@Packets.register(ServerPackets.SPECTATOR_CANT_SPECTATE)
def cant_spectate(stream: StreamIn, game: Game):
    if not game.bancho.spectating:
        return

    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    player.cant_spectate = True

    game.events.call(ServerPackets.SPECTATOR_CANT_SPECTATE, player)


@Packets.register(ServerPackets.CHANNEL_INFO)
def channel_info(stream: StreamIn, game: Game):
    name = stream.string()
    topic = stream.string()
    user_count = stream.s16()

    if not (c := game.bancho.channels.get(name)):
        game.bancho.channels.add(c := Channel(name, game, topic))

    c.user_count = user_count
    c.topic = topic

    if c.name == "#osu" and not c.joined:
        c.join()

    game.events.call(ServerPackets.CHANNEL_INFO, c)


@Packets.register(ServerPackets.CHANNEL_AUTO_JOIN)
def channel_autojoin(stream: StreamIn, game: Game):
    name = stream.string()
    topic = stream.string()
    user_count = stream.s16()

    if not (c := game.bancho.channels.get(name)):
        game.bancho.channels.add(c := Channel(name, game, topic))

    c.user_count = user_count
    c.topic = topic
    c.join_success()

    game.events.call(ServerPackets.CHANNEL_AUTO_JOIN, c)


@Packets.register(ServerPackets.CHANNEL_INFO_END)
def channel_info_end(stream: StreamIn, game: Game):
    game.events.call(ServerPackets.CHANNEL_INFO_END)


@Packets.register(ServerPackets.CHANNEL_JOIN_SUCCESS)
def channel_join_success(stream: StreamIn, game: Game):
    name = stream.string()

    if not (c := game.bancho.channels.get(name)):
        game.bancho.channels.add(c := Channel(name=name, game=game))

    c.join_success()

    game.events.call(ServerPackets.CHANNEL_JOIN_SUCCESS, c)


@Packets.register(ServerPackets.CHANNEL_KICK)
def channel_revoked(stream: StreamIn, game: Game):
    name = stream.string()

    if not (c := game.bancho.channels.get(name)):
        return

    game.bancho.channels.remove(c)
    game.logger.info(f"Kicked out of channel: {name}")

    game.events.call(ServerPackets.CHANNEL_KICK, c)


@Packets.register(ServerPackets.BEATMAP_INFO_REPLY)
def beatmapinfo_reply(stream: StreamIn, game: Game):
    beatmaps = [BeatmapInfo.decode(stream) for beatmap in range(stream.s32())]

    game.events.call(ServerPackets.BEATMAP_INFO_REPLY, beatmaps)


@Packets.register(ServerPackets.SILENCE_END)
def silence_info(stream: StreamIn, game: Game):
    if (remaining_silence := stream.s32()) > 0:
        game.bancho.player.silenced = True
        game.bancho.silenced = True

        game.logger.warning(f"You have been silenced for {remaining_silence} seconds.")

        threading.Timer(remaining_silence, game.bancho.unsilence)
    else:
        game.bancho.unsilence()

    game.events.call(ServerPackets.SILENCE_END, remaining_silence)


@Packets.register(ServerPackets.USER_SILENCED)
def user_silenced(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])

    if not player.loaded:
        game.bancho.request_presence([user_id])

    player.silenced = True

    game.logger.info(f"{player} has been silenced.")
    game.events.call(ServerPackets.USER_SILENCED, player)


@Packets.register(ServerPackets.TARGET_IS_SILENCED)
def target_silenced(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])

    if not player.loaded:
        game.bancho.request_presence([user_id])

    player.silenced = True

    game.logger.info(
        f"{player.name} has been silenced and is unable to respond to your messages right now."
    )
    game.events.call(ServerPackets.TARGET_IS_SILENCED, player)


@Packets.register(ServerPackets.USER_DM_BLOCKED)
def dms_blocked(stream: StreamIn, game: Game):
    user_id = stream.s32()

    if not (player := game.bancho.players.by_id(user_id)):
        game.bancho.request_presence([user_id])
        return

    player.dms_blocked = True

    game.logger.info(f"{player} blocked their dms.")
    game.events.call(ServerPackets.USER_DM_BLOCKED, player)
