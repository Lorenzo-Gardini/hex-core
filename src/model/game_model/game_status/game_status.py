from pydantic import Field

from clonable_base_model import ClonableBaseModel
from model.board.board import Board
from model.game_model.core_control_score import CoreControlScore
from model.game_model.player_order import PlayerOrder
from player.base_player import Player


class GameStatus(ClonableBaseModel):
    turn_number: int = Field(default=0, ge=0)
    player_order: PlayerOrder
    winner: Player | None = None
    board: Board
    control_score: CoreControlScore
