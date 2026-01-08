import logging
import uuid
from typing import Callable, override

from controller.game_controller import GameController
from controller.game_update import GameUpdate, PersonalUpdate
from controller.player_request import PlayerRequest
from player.player import Player, PlayerID
from session.pub_sub import pub_sub
from session.session import Session

logger = logging.getLogger(__name__)


class GameSession(Session):
    def __init__(
        self,
        players: set[Player],
        game_controller_factory: Callable[[set[Player], Session], GameController],
    ):
        self._game_controller = None
        self._players_id = {player.id for player in players}
        self._game_id = uuid.uuid4()
        self._players = players
        self._game_controller_factory = game_controller_factory

    @staticmethod
    def request_topic(player_id: PlayerID):
        return f"{str(player_id)}-request"

    @staticmethod
    def update_topic(player_id: PlayerID):
        return f"{str(player_id)}-update"

    @override
    def start(self):
        for player_id in self._players_id:
            pub_sub.subscribe(self.request_topic(player_id), self._on_player_request)

        self._game_controller = self._game_controller_factory(self._players, self)
        self._game_controller.start()

    def _on_player_request(self, player_request: PlayerRequest):
        if self._game_controller is not None:
            self._game_controller.process_player_request(player_request)

    @override
    def game_is_over(self):
        for player_id in self._players_id:
            pub_sub.unsubscribe(self.request_topic(player_id), self._on_player_request)

    @override
    def send_private_update(self, player_id: PlayerID, update: PersonalUpdate):
        pub_sub.publish(self.update_topic(player_id), update)

    @override
    def send_broadcast_update(self, update: GameUpdate):
        for player_id in self._players_id:
            pub_sub.publish(self.update_topic(player_id), update)
            logger.info("send update")
