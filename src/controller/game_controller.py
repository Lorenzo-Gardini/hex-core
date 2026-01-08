import time
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor
from typing import DefaultDict

from controller.controller_config import controller_config
from controller.game_controller_setup import GameControllerSetup
from controller.game_update import (
    GameStatusUpdate,
    RemainingActionPointsUpdate,
    PlanningPhaseTimeUpdate,
    GameOverUpdate,
    InsufficientActionPointsUpdate,
    ApprovedActionUpdate,
    IllegalActionUpdate,
)
from model.game_model.player_actions import GameAction
from player.player import Player
from session.session import Session


class GameController:
    def __init__(
        self,
        setup: GameControllerSetup,
        players: set[Player],
        session: Session,
    ):
        self._setup = setup
        self._players_actions: DefaultDict[Player, list[GameAction]] = defaultdict(list)
        self._game_status = setup.game_status_factory(players)
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._is_in_selection_phase = True
        self._session = session

    def start(self):
        self._executor.submit(self._send_status_phase)

    # 1
    def _send_status_phase(self):
        self._session.send_broadcast_update(
            GameStatusUpdate(game_status=self._game_status)
        )

        for player in self._game_status.player_order.players:
            self._session.send_private_update(
                player.id,
                RemainingActionPointsUpdate(
                    remaining_action_points=controller_config.default_action_points,
                ),
            )
        self._executor.submit(self._action_selection_phase_setup)

    # 2
    def _action_selection_phase_setup(self):
        duration = controller_config.turn_preparation_time
        self._is_in_selection_phase = True
        start = time.monotonic()
        self._players_actions.clear()
        self._executor.submit(self._action_selection_phase, start, duration)

    # 3
    def _action_selection_phase(self, start_time: float, duration: int):
        elapsed = time.monotonic() - start_time
        remaining = round(duration - elapsed, 2)

        self._session.send_broadcast_update(
            PlanningPhaseTimeUpdate(remaining_time=max(remaining, 0))
        )

        # if > 0.2, sleep 0.2, if 0 <= remaining < 0.2 sleep remaining, if < 0 sleep 0
        time.sleep(min(max(0.0, remaining), 0.2))

        if remaining <= 0:
            self._executor.submit(self._game_update_phase)
        else:
            self._executor.submit(self._action_selection_phase, start_time, duration)

    # 4
    def _game_update_phase(self):
        self._is_in_selection_phase = False

        game_events, new_game_status = self._setup.update_game_status_fn(
            self._game_status, self._players_actions, self._setup.action_validator_fn
        )

        for game_update in game_events:
            time.sleep(controller_config.send_update_ration)
            self._session.send_broadcast_update(game_update)

        time.sleep(controller_config.send_update_ration)

        self._executor.submit(self._check_game_over)

    # 5
    def _check_game_over(self):
        winner = self._game_status.winner
        if winner is not None:
            self._session.send_broadcast_update(GameOverUpdate(winner=winner))
            self._session.game_is_over()
        else:
            self._executor.submit(self._send_status_phase)

    def process_player_request(self, player: Player, game_action: GameAction):
        def _process_player_request():

            previous_player_actions = [
                action_with_id.action
                for action_with_id in self._players_actions[player]
            ]

            remaining_action_points = self._setup.calculate_action_points_fn(
                previous_player_actions + [game_action]
            )

            # no action points
            if remaining_action_points < 0:
                self._session.send_private_update(
                    player.id, InsufficientActionPointsUpdate()
                )
                return

            # invalid action
            if not self._setup.action_validator_fn(
                player, game_action, self._game_status
            ):
                self._session.send_private_update(
                    player.id, IllegalActionUpdate(game_action=game_action)
                )
                return

            # save action and send updates
            self._players_actions[player].append(game_action)

            self._session.send_private_update(
                player.id, ApprovedActionUpdate(game_action=game_action)
            )
            self._session.send_private_update(
                player.id,
                RemainingActionPointsUpdate(
                    remaining_action_points=remaining_action_points
                ),
            )

        if not self._is_in_selection_phase:
            return

        self._executor.submit(_process_player_request)

    def clear_player_actions(self, player: Player):
        def _clear_player_actions():
            self._players_actions[player].clear()

            player.send_update(
                RemainingActionPointsUpdate(controller_config.default_action_points)
            )

        if not self._is_in_selection_phase:
            return

        self._executor.submit(_clear_player_actions)
