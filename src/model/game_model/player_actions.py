from pydantic import BaseModel
from model.player import Player
from model.troops.troops import PlayableTroopTypes
from model.tile.hexagon_coordinates import HexagonCoordinates


class PlayerAction(BaseModel):
    player: Player

    class Config:
        frozen = True


class MarchTroopAction(PlayerAction):
    starting_coordinates: HexagonCoordinates
    destination_coordinates: HexagonCoordinates


class SpawnTroopAction(PlayerAction):
    coordinates: HexagonCoordinates
    troop: PlayableTroopTypes

    class Config:
        arbitrary_types_allowed = True
