import logging
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

from lobby.lobby_config import lobby_config
from player.player import PlayerID, Player
from session.pub_sub import pub_sub
from session.session import Session

logger = logging.getLogger(__name__)


class LobbiesController:
    REMOVE_PLAYER_TOPIC = "remove_player_lobby"
    ADD_PLAYER_TOPIC = "add_player_lobby"

    def __init__(
        self,
        game_session_factory: Callable[[set[Player]], Session],
    ):
        self._session_factory = game_session_factory
        self._active_lobbies: dict[int, deque[PlayerID]] = self._create_lobbies()
        self._player_to_lobby: dict[PlayerID, int] = dict()
        self._player_id_to_player: dict[PlayerID, Player] = dict()
        self._executor = ThreadPoolExecutor(max_workers=1)

        pub_sub.subscribe(self.REMOVE_PLAYER_TOPIC, self.remove_player_from_lobby)
        pub_sub.subscribe(self.ADD_PLAYER_TOPIC, self.add_player_in_lobby)

    def add_player_in_lobby(self, lobby_size: int, player: Player):
        def _add_player_in_lobby():
            if player.id not in self._active_lobbies[lobby_size]:
                player_id = player.id
                self._active_lobbies[lobby_size].append(player_id)
                self._player_to_lobby[player_id] = lobby_size
                self._player_id_to_player[player_id] = player
                self._check_lobbies()

        self._executor.submit(_add_player_in_lobby)

    def remove_player_from_lobby(self, player_id: PlayerID):
        def _remove_player_from_lobby():
            if player_id in self._player_to_lobby:
                lobby_size = self._player_to_lobby[player_id]
                self._active_lobbies[lobby_size].remove(player_id)
                del self._player_to_lobby[player_id]
                del self._player_id_to_player[player_id]

        self._executor.submit(_remove_player_from_lobby)

    def _check_lobbies(self):
        # select ready lobbies
        ready_lobbies_sizes = filter(
            lambda k: len(self._active_lobbies[k]) >= k,
            self._active_lobbies.keys(),
        )

        # pop players in queue and start new game
        for lobby_size in ready_lobbies_sizes:
            in_lobby_ids = {
                self._active_lobbies[lobby_size].popleft() for _ in range(lobby_size)
            }

            # get players
            players = set(map(self._player_id_to_player.get, in_lobby_ids))

            # remove from other dicts
            for player_id in in_lobby_ids:
                del self._player_to_lobby[player_id]
                del self._player_id_to_player[player_id]

            # crate session
            logger.info(f"Start Game with size {lobby_size} and players: {players}")
            session = self._session_factory(players)
            session.start()

    @staticmethod
    def _create_lobbies() -> dict[int, deque[PlayerID]]:
        return {
            lobby_size: deque()
            for lobby_size in range(
                lobby_config.min_number_of_player, lobby_config.max_number_of_player + 1
            )
        }
