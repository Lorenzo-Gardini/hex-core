from threading import Lock
from typing import Callable

from controllers.game_controller.game_controller import GameController
from controllers.games_controller.games_controller import GamesController
from controllers.games_controller.parent_controller import ParentController
from model.game_model.game_status import GameStatus
from model.game_model.game_status_updater import PlayerInput
from model.game_model.game_update import GameUpdate
from player.base_player import BasePlayer
from player.in_lobby_player import InLobbyPlayer


class GameControllerImpl(GamesController, ParentController):
    def __init__(
        self,
        update_game_status_fn: Callable[
            [GameStatus, PlayerInput], tuple[list[GameUpdate], GameStatus]
        ],
        game_status_factory: Callable[[list[BasePlayer]], GameStatus],
    ):
        self._update_game_status_fn = update_game_status_fn
        self._game_status_factory = game_status_factory
        self._games = set()
        self._lock = Lock()

    def start_new_game(
        self,
        in_lobby_players: list[InLobbyPlayer],
    ):
        new_game = GameController(
            self._update_game_status_fn,
            self._game_status_factory,
            lobby_to_game_player_mapper,
            self,
        )
        with self._lock:
            self._games.add(new_game)
        new_game.start()

    def game_is_over(self, game_controller: GameController):
        with self._lock:
            self._games.remove(game_controller)
