from collections import deque
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Callable

from controllers.game_controller.game_controller import GameController
from controllers.lobby.lobby_config import lobby_config
from player.in_lobby_player import InLobbyPlayer


@dataclass(frozen=True)
class _LobbyRequest:
    lobby_size: int
    player: InLobbyPlayer
    to_delete: bool


class LobbiesController:
    def __init__(
        self,
        game_controller_factory: Callable[[set[InLobbyPlayer]], GameController],
    ):
        self._lobby_requests_queue: Queue[_LobbyRequest] = Queue()
        self._games_controller_factory = game_controller_factory
        self._active_lobbies: dict[int, deque[InLobbyPlayer]] = self._create_lobbies()
        Thread(target=self._process_player_in_queue).start()

    def _process_player_in_queue(self):
        while True:
            lobby_request = self._lobby_requests_queue.get()
            lobby_size = lobby_request.lobby_size
            player = lobby_request.player
            if lobby_request.to_delete and player in self._active_lobbies[lobby_size]:
                self._active_lobbies[lobby_size].remove(player)
            elif (
                not lobby_request.to_delete
                and player not in self._active_lobbies[lobby_size]
            ):
                self._active_lobbies[lobby_size].append(player)
                self._check_lobbies()

    def _check_lobbies(self):
        # select ready lobbies
        ready_lobbies_sizes = filter(
            lambda k: len(self._active_lobbies[k]) >= k,
            self._active_lobbies.keys(),
        )

        # pop players in queue and start new game
        for lobby_size in ready_lobbies_sizes:
            in_lobby_players = {
                self._active_lobbies[lobby_size].popleft() for _ in range(lobby_size)
            }
            self._crete_new_game(in_lobby_players)

    def _crete_new_game(self, in_lobby_players: set[InLobbyPlayer]):
        self._games_controller_factory(in_lobby_players).start()

    def add_player_in_lobby(self, lobby_size: int, player: InLobbyPlayer):
        self._lobby_requests_queue.put(
            _LobbyRequest(lobby_size=lobby_size, player=player, to_delete=False)
        )

    def remove_player_from_lobby(self, lobby_size: int, player: InLobbyPlayer):
        self._lobby_requests_queue.put(
            _LobbyRequest(lobby_size=lobby_size, player=player, to_delete=True)
        )

    @staticmethod
    def _create_lobbies() -> dict[int, deque[InLobbyPlayer]]:
        return {
            lobby_size: deque()
            for lobby_size in range(
                lobby_config.min_number_of_player, lobby_config.max_number_of_player + 1
            )
        }
