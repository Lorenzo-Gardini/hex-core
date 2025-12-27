from abc import ABC, abstractmethod

from controllers.game_controller.game_controller import GameController


class ParentController(ABC):

    @abstractmethod
    def game_is_over(self, game_controller: GameController):
        pass
