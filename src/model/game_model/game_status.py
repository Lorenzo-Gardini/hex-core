from pydantic import BaseModel

from model.board.board import Board
from model.player import Player
from model.troops.troops import PlayableTroopTypes


class GameStatus(BaseModel):
    turn_number: int = 0
    player_order: list[Player]
    player_to_troops: dict[Player, dict[PlayableTroopTypes, int]]
    winner: Player | None = None
    board: Board
    control_score: dict[PlayableTroopTypes, int]
