from collections import Counter
from typing import Callable

from model.game_model.game_config import game_config_instance
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
    BasePlayerAction,
    SpawnTroopAction,
    MarchTroopAction,
    PlayerAction,
)
from model.troops import HomeBaseTroop, BaseTroop
from player.base_player import BasePlayer

PlayerInput = dict[BasePlayer, list[BasePlayerAction]]
Stack = list


class GameStatusUpdater:
    def __call__(
        self,
        game_status: GameStatus,
        valid_input_actions: PlayerInput,
    ) -> tuple[list[GameUpdate], GameStatus]:
        spawn_updates, new_game_status = self._process_player_action_by_type(
            valid_input_actions,
            game_status,
            SpawnTroopAction,
            self._process_spawn_action,
        )
        march_updates, new_game_status = self._process_player_action_by_type(
            valid_input_actions,
            new_game_status,
            MarchTroopAction,
            self._process_march_action,
        )
        turn_updates, new_game_status = self._update_turn_and_check_game_over(
            new_game_status
        )

        return [*spawn_updates, *march_updates, *turn_updates], new_game_status

    @staticmethod
    def _update_turn_and_check_game_over(
        game_status: GameStatus,
    ) -> tuple[GameUpdate, GameStatus]:
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
                    -game_status.player_order.index(p),
                ),
            )
            return GameOverUpdate(winner=winner_player), game_status.copy_with(
                winner=winner_player
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
                >= game_config_instance.winning_core_control_turns
            ):
                return GameOverUpdate(winner=core_troop.owner), game_status.copy_with(
                    winner=core_troop.owner, new_control_score=new_control_score
                )
        else:
            new_control_score = game_status.control_score.clear()

        return GameStatusUpdate(game_status=game_status), game_status.copy_with(
            player_order=game_status.player_order.turn_players_order(),
            new_control_score=new_control_score,
        )

    @staticmethod
    def _process_player_action_by_type(
        input_actions: PlayerInput,
        game_status: GameStatus,
        action_type: type[PlayerAction],
        action_fn: Callable[
            [PlayerAction, GameStatus],
            tuple[list[GameUpdate] | GameUpdate, GameStatus],
        ],
    ) -> tuple[list[GameUpdate], GameStatus]:
        total_updates = []

        new_game_status = game_status
        for action in filter(lambda x: isinstance(x, action_type), input_actions):
            updates, new_game_status = action_fn(action, new_game_status)
            total_updates.extend(updates if isinstance(updates, list) else [updates])

        return total_updates, game_status

    @staticmethod
    def _process_spawn_action(
        spawn_troops_action: SpawnTroopAction, game_status: GameStatus
    ) -> tuple[GameUpdate, GameStatus]:
        spawned_troop = spawn_troops_action.troop
        coordinates = spawn_troops_action.coordinates
        new_game_status = game_status.copy_with(
            board=game_status.board.add_player_troop(spawned_troop, coordinates)
        )
        return (
            TroopSpawnedUpdate(
                troop=spawned_troop,
                coordinate=coordinates,
            ),
            new_game_status,
        )

    @staticmethod
    def _process_march_action(
        march_troops_action: MarchTroopAction, game_status: GameStatus
    ) -> tuple[list[GameUpdate], GameStatus]:
        game_updates: list[GameUpdate] = []
        new_board = game_status.board
        new_player_order = game_status.player_order

        moving_troop: BaseTroop = game_status.board.coordinates_to_tile[
            march_troops_action.starting_coordinates
        ]
        defending_troop: BaseTroop | None = game_status.board.coordinates_to_tile[
            march_troops_action.destination_coordinates
        ]

        if defending_troop is None or moving_troop > defending_troop:
            new_board = new_board.move_troop(
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
                new_board = new_board.remove_player_troops(defending_troop.owner)
                new_player_order = new_player_order.remove_player(removed_player)
                game_updates.append(PlayerRemovedUpdate(player=removed_player))

        elif moving_troop < defending_troop:
            new_board = new_board.remove_troop(march_troops_action.starting_coordinates)
            game_updates.append(
                TroopRemovedUpdate(march_troops_action.starting_coordinates)
            )

        return game_updates, game_status.copy_with(
            board=new_board, player_order=new_player_order
        )
