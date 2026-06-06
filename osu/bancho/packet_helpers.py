from typing import TYPE_CHECKING

from ..objects.channel import Channel
from ..objects.player import Player
from ..objects.match import Match
from .streams import StreamIn

if TYPE_CHECKING:
    from ..game import Game


def resolve_match(stream: StreamIn, game: "Game") -> Match:
    match = Match.decode(stream, game)
    missing_players = []

    for slot in match.used_slots:
        if slot.player_id <= 0:
            continue

        if game.bancho.players.by_id(slot.player_id):
            continue

        game.bancho.players.add(Player(slot.player_id, name="", game=game))
        missing_players.append(slot.player_id)

    if missing_players:
        game.bancho.request_presence(missing_players)

    game.bancho.matches.add(match)
    return match


def resolve_message(stream: StreamIn, game: "Game"):
    sender_name = stream.string()
    message = stream.string()
    target_name = stream.string()
    sender_id = stream.s32()

    # Find player
    player = game.bancho.players.by_id(sender_id)

    if not player:
        # Try to find sender by name
        player = game.bancho.players.by_name(sender_name)

    if not player:
        player = Player(sender_id, sender_name, game)

        if sender_id:
            game.bancho.players.add(player)
            game.bancho.request_presence([sender_id])

    if not player.loaded:
        # Presence missing
        player.request_presence()

    sender = player

    # Find target
    if target_name.startswith("#"):
        # Public message
        target = game.bancho.channels.get(target_name) or Channel(target_name, game)
        return sender, message, target

    # Private message
    target = game.bancho.players.by_name(target_name)

    if not target and game.bancho.player and target_name == game.bancho.player.name:
        target = game.bancho.player

    if not target:
        target = Player(0, target_name, game)

    if not target.loaded:
        # Presence missing
        target.request_presence()

    return sender, message, target
