from typing import Union, Literal

from pydantic import BaseModel

from model.board.hexagon_coordinates import HexagonCoordinates
from model.game_model.game_config import game_config
from model.troops import PlayableTroopType


class GameAction(BaseModel):
    action_points_cost: int

    class ConfigDict:
        frozen = True


class MarchTroopAction(GameAction):
    action_points_cost: int = game_config.march_troop_action_points
    player_action_type: Literal["march_troop_action"] = "march_troop_action"
    starting_coordinates: HexagonCoordinates
    destination_coordinates: HexagonCoordinates


class SpawnTroopAction(GameAction):
    action_points_cost: int = game_config.spawn_troop_action_points
    action_type: Literal["spawn_troop_action"] = "spawn_troop_action"
    coordinates: HexagonCoordinates
    troop: PlayableTroopType


GameAction = Union[MarchTroopAction, SpawnTroopAction]
