from pydantic import Field

from clonable_base_model import ClonableBaseModel
from model.board.board import Board
from model.game_model.core_control_score import CoreControlScore
from model.game_model.player_order import PlayerOrder
from model.troops import PlayableTroopType
from player.base_player import BasePlayer


class GameStatus(ClonableBaseModel):
    turn_number: int = Field(default=0, ge=0)
    player_order: PlayerOrder
    player_to_n_troops: dict[BasePlayer, dict[PlayableTroopType, int]]
    winner: BasePlayer | None = None
    board: Board
    control_score: CoreControlScore

    @property
    def is_game_over(self) -> bool:
        return self.winner is not None
