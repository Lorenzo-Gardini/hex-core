import copy
import math
import threading
import time
from collections import defaultdict
from threading import Lock
from typing import Callable
from typing import DefaultDict

from controllers.game_controller.controller_config import controller_config
from controllers.game_controller.update import (
    Update,
    GameStatusUpdate,
    PlanningPhaseTimeUpdate,
    InsufficientActionPointsUpdate,
    IllegalActionUpdate,
    ApprovedActionUpdate,
    RemainingActionPointsUpdate,
    GameOverUpdate,
)
from model.game_model.game_event import GameEvent
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_actions import GameAction
from player.base_player import Player
from player.in_game_player import InGamePlayer
from player.in_lobby_player import InLobbyPlayer


class GameController:
    _THREAD_COUNTER = 2  # one for game loop the other for operations

    def __init__(
        self,
        update_game_status_fn: Callable[
            [GameStatus, dict[Player, list[GameAction]]],
            tuple[list[GameEvent], GameStatus],
        ],
        action_validator_fn: Callable[[Player, GameAction, GameStatus], bool],
        calculate_action_points: Callable[[list[GameAction]], int],
        game_status_factory: Callable[[set[Player]], GameStatus],
        in_lobby_players: set[InLobbyPlayer],
    ):
        self._update_game_status_fn = update_game_status_fn
        self._action_validator_fn = action_validator_fn
        self._calculate_action_points = calculate_action_points
        self._players_actions: DefaultDict[Player, list[GameAction]] = defaultdict(list)
        self._in_game_players = self._convert_to_in_game_players(in_lobby_players)
        self._game_status = game_status_factory(self._in_game_players)
        self._thread = threading.Thread(target=self._game_loop)
        self._lock = Lock()

    def start(self):
        self._thread.start()

    def _game_loop(self):
        while True:
            self._action_selection_phase()
            self._game_update_phase()

            with self._lock:
                winner = self._game_status.winner

            if winner is not None:
                for player in self._in_game_players:
                    player.send_update(GameOverUpdate(winner=winner))
                    player.is_game_over()
                return

    def _action_selection_phase(self):
        duration = controller_config.turn_preparation_time
        start = time.monotonic()

        with self._lock:
            self._players_actions.clear()
            current_game_status = self._game_status.just_copy()

        self._broadcast_update(GameStatusUpdate(game_status=current_game_status))
        self._broadcast_update(
            RemainingActionPointsUpdate(controller_config.default_action_points)
        )

        while True:
            elapsed = time.monotonic() - start
            remaining = math.ceil(duration - elapsed)

            self._broadcast_update(PlanningPhaseTimeUpdate(max(remaining, 0)))
            time.sleep(1 - (elapsed % 1))

            if remaining <= 0:
                break

    def _game_update_phase(self):
        with self._lock:
            current_actions = copy.deepcopy(self._players_actions)
            current_game_status = self._game_status.just_copy()

        game_events, new_game_status = self._update_game_status_fn(
            current_game_status, current_actions
        )

        with self._lock:
            self._game_status = new_game_status

        for game_update in game_events:
            time.sleep(2)
            self._broadcast_update(game_update)

        time.sleep(2)

    def process_player_action_request(
        self, player: InGamePlayer, game_action: GameAction
    ):
        with self._lock:
            player_actions = [
                action_with_id.action
                for action_with_id in self._players_actions[player]
            ]
            current_game_status = self._game_status.just_copy()

        remaining_action_points = self._calculate_action_points(
            player_actions + [game_action]
        )

        if remaining_action_points < 0:
            player.send_update(InsufficientActionPointsUpdate())
            return

        if not self._action_validator_fn(player, game_action, current_game_status):
            player.send_update(IllegalActionUpdate(game_action=game_action))
            return

        with self._lock:
            self._players_actions[player].append(game_action)
            player.send_update(ApprovedActionUpdate(selected_action=game_action))
            player.send_update(RemainingActionPointsUpdate(remaining_action_points))

    def clear_player_actions(self, player: InGamePlayer):
        with self._lock:
            self._players_actions[player].clear()

        player.send_update(
            RemainingActionPointsUpdate(controller_config.default_action_points)
        )

    def _broadcast_update(self, update: Update):
        for player in self._in_game_players:
            player.send_update(update)

    def _convert_to_in_game_players(self, in_lobby_players: set[InLobbyPlayer]):
        return {
            player.to_game_player(
                self.process_player_action_request, self.clear_player_actions
            )
            for player in in_lobby_players
        }
