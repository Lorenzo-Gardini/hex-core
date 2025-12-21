from model.game_model.game_status import GameStatus
from model.game_model.game_update import (
    GameOverUpdate,
    GameStatusUpdate,
    GameUpdate,
    PlayerRemovedUpdate,
    TroopMovedUpdate,
    TroopRemovedUpdate,
    TroopSpawnedUpdate,
)
from model.game_model.player_actions import (
    PlayerAction,
    SpawnTroopAction,
    MarchTroopAction,
)
from typing import Callable
from collections import Counter

from model.player import Player
from model.game_model.game_config import game_config_instance
from model.troops.troops import HomeBaseTroop, Troop

type PlayerInputs = dict[Player, list[PlayerAction]]
type Stack = list


class GameStatusUpdater:
    def __call__(
        self,
        game_status: GameStatus,
        valid_input_actions: PlayerInputs,
    ) -> list[GameUpdate]:
        spawn_updates = self._process_player_action_by_type(
            valid_input_actions,
            game_status,
            SpawnTroopAction,
            self._process_spawn_action,
        )
        march_updates = self._process_player_action_by_type(
            valid_input_actions,
            game_status,
            MarchTroopAction,
            self._process_march_action,
        )
        turn_updates = self._update_turn_and_check_game_over(game_status)

        return [*spawn_updates, *march_updates, *turn_updates]

    def _update_turn_and_check_game_over(self, game_status: GameStatus) -> GameUpdate:
        game_status.turn_number += 1
        board = game_status.board

        # If max turns reached, determine winner by troop count. In case of tie,
        # the player who is earlier in the turn order wins.
        if game_status.turn_number > game_config_instance.max_turns:
            player_to_troop_count = Counter(
                tile.occupation.owner
                for tile in board.coordinates_to_tile.values()
                if tile.occupation is not None
            )
            # sort by troop count and player order
            winner_player = max(
                game_status.player_order,
                key=lambda p: (
                    player_to_troop_count[p],
                    -game_status.player_order.index[p],
                ),
            )
            game_status.winner = winner_player
            return GameOverUpdate(winner=winner_player)

        # Check core control for winning condition. If a player's troop
        # occupies the core for a number of consecutive turns, they win.
        core_troop: Troop | None = board.coordinates_to_tile[
            board.core_coordinates
        ].occupation

        if core_troop is not None:
            control_score = game_status.control_score
            if core_troop not in control_score:
                control_score[core_troop] = 1
            else:
                control_score[core_troop] += 1

            if (
                control_score[core_troop]
                >= game_config_instance.winning_core_control_turns
            ):
                game_status.winner = core_troop.owner
                return GameOverUpdate(winner=core_troop.owner)
        else:
            game_status.control_score.clear()

        old_player_order = game_status.player_order
        game_status.player_order = old_player_order[1:] + old_player_order[:1]
        return GameStatusUpdate(game_status=game_status)

    def _process_player_action_by_type(
        input_actions: PlayerInputs,
        game_status: GameStatus,
        action_type: type[PlayerAction],
        action_fn: Callable[[PlayerAction], GameUpdate],
    ) -> list[GameUpdate]:
        def as_list(x):
            return x if isinstance(x, list) else [x]

        return [
            update
            for action in input_actions
            if isinstance(action, action_type)
            for update in as_list(action_fn(action, game_status))
        ]

    def _process_spawn_action(
        self, spawn_troops_action: SpawnTroopAction, game_status: GameStatus
    ) -> GameUpdate:
        game_status.board.add_player_troop(
            spawn_troops_action.troop,
            spawn_troops_action.coordinates,
        )
        return TroopSpawnedUpdate(
            troop=spawn_troops_action.troop,
            coordinate=spawn_troops_action.coordinates,
        )

    def _process_march_action(
        self, march_troops_action: MarchTroopAction, game_status: GameStatus
    ) -> list[GameUpdate]:
        game_updates: list[GameUpdate] = []

        moving_troop: Troop = game_status.board.coordinates_to_tile[
            march_troops_action.starting_coordinates
        ]
        defending_troop: Troop | None = game_status.board.coordinates_to_tile[
            march_troops_action.destination_coordinates
        ]

        if defending_troop is None or moving_troop > defending_troop:
            game_status.board.move_troop(
                march_troops_action.starting_coordinates,
                march_troops_action.destination_coordinates,
            )
            game_updates.extend(
                [
                    TroopRemovedUpdate(
                        troop=defending_troop,
                        coordinate=march_troops_action.destination_coordinates,
                    ),
                    TroopMovedUpdate(
                        troop=moving_troop,
                        from_coordinate=march_troops_action.starting_coordinates,
                        to_coordinate=march_troops_action.destination_coordinates,
                    ),
                ]
            )
            if isinstance(defending_troop, HomeBaseTroop):
                removed_player = defending_troop.owner
                game_status.board.remove_player_troops(defending_troop.owner)
                game_status.player_order.remove(removed_player)
                game_updates.append(PlayerRemovedUpdate(player=removed_player))

        elif moving_troop < defending_troop:
            game_status.board.remove_troop(march_troops_action.starting_coordinates)
            game_updates.append(
                TroopRemovedUpdate(march_troops_action.starting_coordinates)
            )

        return game_updates
