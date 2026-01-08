from typing import Callable

from model.game_model.game_event import GameEvent
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_actions import GameAction
from player.player import Player

UpdateModelFunction = Callable[
    [
        GameStatus,
        dict[Player, list[GameAction]],
        Callable[[Player, GameAction, GameStatus], bool],
    ],
    tuple[list[GameEvent], GameStatus],
]

ActionValidationFunction = Callable[[Player, GameAction, GameStatus], bool]

ActionPointCalculationFunction = Callable[[list[GameAction]], int]

GameStatusFactory = Callable[[set[Player]], GameStatus]
