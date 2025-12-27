from typing import Union, Literal, Annotated

from pydantic import BaseModel, Field

from model.tile.hexagon_coordinates import HexagonCoordinates
from model.troops import PlayableTroopType
from player.base_player import BasePlayer


class BasePlayerAction(BaseModel):
    player: BasePlayer

    class ConfigDict:
        frozen = True


class UndoAction(BasePlayerAction):
    player_action_type: Literal["undo_action"] = "undo_action"
    player_action: BasePlayerAction


class SetAction(BasePlayerAction):
    player_action_type: Literal["set_action"] = "set_action"
    player_action: BasePlayerAction


class MarchTroopAction(BasePlayerAction):
    player_action_type: Literal["march_troop_action"] = "march_troop_action"
    starting_coordinates: HexagonCoordinates
    destination_coordinates: HexagonCoordinates


class SpawnTroopAction(BasePlayerAction):
    action_type: Literal["spawn_troop_action"] = "spawn_troop_action"
    coordinates: HexagonCoordinates
    troop: PlayableTroopType


PlayerAction = Annotated[
    Union[MarchTroopAction, SpawnTroopAction, UndoAction, SetAction],
    Field(discriminator="action_type"),
]
