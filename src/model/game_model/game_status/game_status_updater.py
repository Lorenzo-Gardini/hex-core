from dataclasses import dataclass
from itertools import zip_longest
from typing import Callable

from model.game_model.game_config import game_config
from model.game_model.game_event import (
    GameEvent,
    NoChangesEvent,
    TroopMovedEvent,
    PlayerRemovedEvent,
    TroopSpawnedEvent,
    AttackWonEvent,
    AttackLostEvent,
    FailedSpawnEvent,
    FailedMarchEvent,
)
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_actions import (
    SpawnTroopAction,
    MarchTroopAction,
    GameAction,
)
from model.troops import HomeBaseTroop, BaseTroop
from player.base_player import Player


@dataclass(frozen=True)
class _PlayerDoAction:
    player: Player
    game_action: GameAction


def game_status_updater(
    game_status: GameStatus,
    game_actions: dict[Player, list[GameAction]],
    is_valid_action: Callable[[Player, GameAction, GameStatus], bool],
) -> tuple[list[GameEvent], GameStatus]:
    actions_order = _generate_action_order(
        game_actions, game_status.player_order.players
    )

    new_game_status = game_status
    all_events = []

    for action in actions_order:
        player = action.player
        game_action = action.game_action

        if not is_valid_action(player, game_action, new_game_status):
            all_events.append(NoChangesEvent(player=player, game_action=game_action))
            continue

        if isinstance(game_action, SpawnTroopAction):
            if not is_valid_action(player, game_action, new_game_status):
                all_events.append(
                    FailedSpawnEvent(player=player, game_action=game_action)
                )
                continue
            process_fn = _process_spawn_action
        else:
            if not is_valid_action(player, game_action, new_game_status):
                all_events.append(
                    FailedMarchEvent(player=player, game_action=game_action)
                )
                continue
            process_fn = _process_march_action

        updates, new_game_status = process_fn(player, game_action, new_game_status)
        all_events.append(updates)

    final_game_status = _update_turn_and_check_winner(new_game_status)
    return all_events, final_game_status


def _update_turn_and_check_winner(
    game_status: GameStatus,
) -> GameStatus:
    game_status.turn_number += 1
    board = game_status.board

    # If max turns reached, determine winner by troop count. In case of tie,
    # the player who is earlier in the turn order wins.
    if game_status.turn_number > game_config.max_turns:
        player_to_troop_count = {
            player: sum([count for count in troop_to_count.values()])
            for player, troop_to_count in game_status.board.playable_troop_by_players().items()
        }
        # sort by troop count and player order
        winner_player = max(
            game_status.player_order,
            key=lambda p: (
                player_to_troop_count[p],
                -game_status.player_order.index(p),
            ),
        )
        return game_status.copy_with(
            winner=winner_player, player_to_troop_count=player_to_troop_count
        )

    # Check core control for winning condition. If a player's troop
    # occupies the core for a number of consecutive turns, they win.
    core_troop: BaseTroop | None = board.coordinates_to_tile[
        board.core_coordinates
    ].occupation

    if core_troop is not None:
        new_control_score = game_status.control_score.score_for_troop(core_troop)

        if (
            new_control_score.n_turn_of_control
            >= game_config.winning_core_control_turns
        ):
            return game_status.copy_with(
                winner=core_troop.owner, new_control_score=new_control_score
            )
    else:
        new_control_score = game_status.control_score.clear()

    return game_status.copy_with(
        player_order=game_status.player_order.turn_players_order(),
        new_control_score=new_control_score,
    )


def _process_spawn_action(
    player: Player, spawn_troops_action: SpawnTroopAction, game_status: GameStatus
) -> tuple[GameEvent, GameStatus]:
    spawned_troop = spawn_troops_action.troop
    coordinates = spawn_troops_action.coordinates

    new_game_status = game_status.copy_with(
        board=game_status.board.add_player_troop(spawned_troop, coordinates)
    )
    return (
        TroopSpawnedEvent(
            player=player,
            troop=spawned_troop,
            coordinate=coordinates,
        ),
        new_game_status,
    )


def _process_march_action(
    player: Player, march_troops_action: MarchTroopAction, game_status: GameStatus
) -> tuple[GameEvent, GameStatus]:
    new_board = game_status.board
    new_player_order = game_status.player_order

    moving_troop: BaseTroop = game_status.board.coordinates_to_tile[
        march_troops_action.starting_coordinates
    ]
    defending_troop: BaseTroop | None = game_status.board.coordinates_to_tile[
        march_troops_action.destination_coordinates
    ]

    # destination is empty
    if defending_troop is None:
        new_board = new_board.move_troop(
            march_troops_action.starting_coordinates,
            march_troops_action.destination_coordinates,
        )
        game_update = TroopMovedEvent(
            player=player,
            troop=moving_troop,
            from_coordinate=march_troops_action.starting_coordinates,
            to_coordinate=march_troops_action.destination_coordinates,
        )
    elif isinstance(defending_troop, HomeBaseTroop):
        removed_player = defending_troop.owner
        new_board = new_board.remove_player_troops(defending_troop.owner)
        new_player_order = new_player_order.remove_player(removed_player)
        game_update = PlayerRemovedEvent(player=removed_player)
    # destination is stronger
    elif moving_troop > defending_troop:
        new_board = new_board.move_troop(
            march_troops_action.starting_coordinates,
            march_troops_action.destination_coordinates,
        )
        game_update = AttackWonEvent(
            moving_troop=moving_troop,
            defending_troop=defending_troop,
            from_coordinates=march_troops_action.starting_coordinates,
            to_coordinates=march_troops_action.destination_coordinates,
        )
    # destination is weaker
    elif moving_troop < defending_troop:
        new_board = new_board.remove_troop(march_troops_action.starting_coordinates)
        game_update = AttackLostEvent(
            moving_troop=moving_troop,
            defending_troop=defending_troop,
            from_coordinates=march_troops_action.starting_coordinates,
            to_coordinates=march_troops_action.destination_coordinates,
        )
    # destination is equal no updates
    else:
        game_update = NoChangesEvent()

    return game_update, game_status.copy_with(
        board=new_board, player_order=new_player_order
    )


def _generate_action_order(
    game_actions: dict[Player, list[GameAction]], player_order: list[Player]
) -> list[_PlayerDoAction]:
    actions = [game_actions.get(player, []) for player in player_order]

    result: list[_PlayerDoAction] = []

    for group in zip_longest(*actions, fillvalue=None):
        for player, action in zip(player_order, group):
            if action is not None:
                result.append(_PlayerDoAction(player, action))

    return result
