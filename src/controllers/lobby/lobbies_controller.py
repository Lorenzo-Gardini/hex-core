from collections import defaultdict
from dataclasses import dataclass
from queue import Queue
from typing import DefaultDict

from controllers.games_controller.games_controller import GamesController
from player.in_lobby_player import InLobbyPlayer


@dataclass(frozen=True)
class _LobbyRequest:
    lobby_size: int
    player: InLobbyPlayer
    to_delete: bool


class LobbiesController:
    def __init__(self, games_controller: GamesController):
        self._lobby_requests_queue: Queue[_LobbyRequest] = Queue()
        self._games_controller = games_controller
        self._active_lobbies: DefaultDict[int, list[InLobbyPlayer]] = defaultdict(list)

    def _check_players(self):
        ready_lobbies = filter(
            lambda k: len(self._active_lobbies[k]) >= k,
            list(self._active_lobbies.keys()),
        )
        for lobby_size in ready_lobbies:
            if len(self._active_lobbies[lobby_size]) >= lobby_size:
                self._active_lobbies[lobby_size] = self._active_lobbies[lobby_size][
                    :lobby_size
                ]
                in_game_players = self._active_lobbies[lobby_size][:lobby_size]
                self._games_controller.start_new_game(in_game_players)

    def _process_player_in_queue(self):
        while True:
            lobby_request = self._lobby_requests_queue.get()
            lobby_size = lobby_request.lobby_size
            player = lobby_request.player
            if lobby_request.to_delete and player in self._active_lobbies[lobby_size]:
                self._active_lobbies[lobby_size].remove(player)
            else:
                self._active_lobbies[lobby_size].append(player)
            self._check_players()

    def add_player_in_lobby(self, lobby_size: int, player: InLobbyPlayer):
        self._lobby_requests_queue.put(
            _LobbyRequest(lobby_size=lobby_size, player=player, to_delete=False)
        )

    def remove_player_from_lobby(self, lobby_size: int, player: InLobbyPlayer):
        self._lobby_requests_queue.put(
            _LobbyRequest(lobby_size=lobby_size, player=player, to_delete=True)
        )
