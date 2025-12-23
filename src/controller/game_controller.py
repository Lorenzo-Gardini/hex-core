from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Callable
from model.game_model.game_status import GameStatus
from model.game_model.game_status_updater import PlayerInputs
from model.game_model.game_update import GameUpdate
from model.game_model.player_action_validator import validate_action
from model.game_model.player_actions import PlayerAction
from model.player import Player
from controller.controller_config import controller_config
from view.view import View


class GameController:
    def __init__(
        self,
        view: View,
        update_game_status_fn: Callable[[GameStatus, PlayerInputs], list[GameUpdate]],
        create_game_status_fn: Callable[[int], GameStatus],
        players: list[Player],
    ):
        self._view = view
        self._player_actions: dict[Player, list[PlayerAction]] = defaultdict(list)
        self._update_game_status_fn = update_game_status_fn
        self._game_status = create_game_status_fn(players)
        self._executor = ThreadPoolExecutor(1)

    def start_game(self):
        self._game_loop()

    def _game_loop(self):
        is_game_over = False

        while not is_game_over:
            self._action_selection_phase()
            is_game_over = self._player_move_phase()
        self._executor.shutdown()

    def _player_move_phase(self) -> bool:
        game_updates: list[GameUpdate]
        game_status: GameStatus
        game_updates, game_status = self._process_player_actions()
        self._view.process_updates(game_updates)
        self._player_actions.clear()
        return game_status.winner is not None

    def _action_selection_phase(self):
        remaining_time = controller_config.turn_preparation_time
        while remaining_time > 0:
            self._view.show_remaining_time(remaining_time)
            time.sleep(1)
            remaining_time -= 1

    def _process_player_action(self) -> tuple[list[GameUpdate], GameStatus]:
        validated_player_actions = {
            player: list(filter(self.is_valid_player_action, actions))
            for player, actions in self._player_actions.items()
        }
        capped_player_actions = {
            player: actions[: controller_config.action_points]
            for player, actions in validated_player_actions.items()
        }
        return self._update_game_status_fn(self._game_status, capped_player_actions)

    def add_player_action(self, player_action: PlayerAction):
        def _async_add_player_action():
            self._player_actions[player_action.player] = player_action

        self._executor.submit(_async_add_player_action)

    def remove_player_action(self, player_action: PlayerAction):
        def async_remove_player_action():
            player_actions = self._player_actions[player_action.player]
            if player_action in player_actions:
                player_actions.remove(player_actions)

        self._executor.submit(async_remove_player_action)

    def is_valid_player_action(self, player_action: PlayerAction) -> bool:
        def async_is_valid_player_action():
            return validate_action(player_action, self._game_status)

        self._executor.submit(async_is_valid_player_action)
