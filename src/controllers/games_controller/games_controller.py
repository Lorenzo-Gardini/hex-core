from abc import ABC, abstractmethod

from player.in_lobby_player import InLobbyPlayer


class GamesController(ABC):

    @abstractmethod
    def start_new_game(
        self,
        in_lobby_players: list[InLobbyPlayer],
    ):
        pass
