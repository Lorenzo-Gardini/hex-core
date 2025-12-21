from pydantic import BaseModel

from model.game_model.game_status import GameStatus
from model.player import Player
from model.tile.hexagon_coordinates import HexagonCoordinates
from model.troops.troops import PlayableTroopTypes


class GameUpdate(BaseModel):
    pass


class TroopMovedUpdate(GameUpdate):
    troop: PlayableTroopTypes
    from_coordinate: HexagonCoordinates
    to_coordinate: HexagonCoordinates


class TroopRemovedUpdate(GameUpdate):
    coordinate: HexagonCoordinates


class TroopSpawnedUpdate(GameUpdate):
    troop: PlayableTroopTypes
    coordinate: HexagonCoordinates


class PlayerRemovedUpdate(GameUpdate):
    player: Player


class GameOverUpdate(GameUpdate):
    winner: Player


class GameStatusUpdate(GameUpdate):
    game_status: GameStatus


type GameUpdate = (
    TroopMovedUpdate
    | TroopRemovedUpdate
    | TroopSpawnedUpdate
    | PlayerRemovedUpdate
    | GameOverUpdate
    | GameStatusUpdate
)
