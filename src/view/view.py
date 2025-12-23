from abc import ABC, abstractmethod

from model.game_model.game_update import GameUpdate


class View(ABC):
    @abstractmethod
    def show_remaining_time(remaining_time: int):
        pass

    @abstractmethod
    def process_updates(game_updates: list[GameUpdate]):
        pass
