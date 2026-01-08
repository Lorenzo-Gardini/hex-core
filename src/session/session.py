from abc import abstractmethod, ABC

from controller.game_update import PersonalUpdate, GameUpdate
from player.player import PlayerID


class Session(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def send_private_update(self, player_id: PlayerID, update: PersonalUpdate):
        pass

    @abstractmethod
    def send_broadcast_update(self, update: GameUpdate):
        pass

    @abstractmethod
    def game_is_over(self) -> None:
        pass
