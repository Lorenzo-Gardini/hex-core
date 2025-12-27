import copy
import math
import threading
import time
from collections import defaultdict
from threading import Lock
from typing import Callable
from typing import DefaultDict

from controllers.game_controller.controller_config import controller_config
from controllers.games_controller.parent_controller import ParentController
from model.game_model.game_status import GameStatus
from model.game_model.game_status_updater import PlayerInput
from model.game_model.game_update import GameUpdate, PlanningPhaseTime
from model.game_model.player_action_validator import is_valid_action
from model.game_model.player_actions import BasePlayerAction
from player.base_player import BasePlayer
from player.in_game_player import InGamePlayer


class GameController:
    _THREAD_COUNTER = 2  # one for game loop the other for operations

    def __init__(
        self,
        update_game_status_fn: Callable[
            [GameStatus, PlayerInput], tuple[list[GameUpdate], GameStatus]
        ],
        game_status_factory: Callable[[list[BasePlayer]], GameStatus],
        lobby_to_game_player_mapper: Callable[["GameController"], list[InGamePlayer]],
        parent_controller: ParentController,
    ):
        self._player_actions: DefaultDict[BasePlayer, list[BasePlayerAction]] = (
            defaultdict(list)
        )
        self._players = lobby_to_game_player_mapper(self)
        self._update_game_status_fn = update_game_status_fn
        self._game_status = game_status_factory(self._players)
        self._thread = threading.Thread(target=self._game_loop)
        self._parent_controller = parent_controller
        self._lock = Lock()

    def start(self):
        self._thread.start()

    def _game_loop(self):
        while True:
            self._action_selection_phase()
            self._move_phase()
            with self._lock:
                if self._game_status.is_game_over:
                    self._parent_controller.game_is_over(self)
                    return

    def _action_selection_phase(self):
        duration = controller_config.turn_preparation_time
        start = time.monotonic()

        while True:
            elapsed = time.monotonic() - start
            remaining = math.ceil(duration - elapsed)

            self._broadcast_update(PlanningPhaseTime(max(remaining, 0)))
            time.sleep(1 - (elapsed % 1))

            if remaining <= 0:
                break

    def _move_phase(self):
        with self._lock:
            current_actions = copy.deepcopy(self._player_actions)
            self._player_actions.clear()
            current_game_status = self._game_status.just_copy()

        validated_player_actions = {
            player: [
                action
                for action in actions
                if self._is_valid_player_action(action, current_game_status)
            ]
            for player, actions in current_actions.items()
        }
        capped_player_actions = {
            player: actions[: controller_config.action_points]
            for player, actions in validated_player_actions.items()
        }

        game_updates, new_game_status = self._update_game_status_fn(
            current_game_status, capped_player_actions
        )

        with self._lock:
            self._game_status = new_game_status

        for game_update in game_updates:
            self._broadcast_update(game_update)

    def add_player_action(self, player_action: BasePlayerAction):
        with self._lock:
            self._player_actions[player_action.player] = player_action

    def remove_player_action(self, player_action: BasePlayerAction):
        with self._lock:
            player_actions = self._player_actions[player_action.player]
            if player_action in player_actions:
                player_actions.remove(player_action)

    @staticmethod
    def _is_valid_player_action(
        player_action: BasePlayerAction, current_game_status: GameStatus
    ) -> bool:
        return is_valid_action(player_action, current_game_status)

    def is_valid_player_action(self, player_action: BasePlayerAction) -> bool:
        with self._lock:
            current_game_status = self._game_status
        return self._is_valid_player_action(player_action, current_game_status)

    def _broadcast_update(self, update: GameUpdate):
        for player in self._players:
            player.send_update(update)
