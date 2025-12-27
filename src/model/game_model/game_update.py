from typing import Union, Literal, Annotated

from pydantic import BaseModel, Field

from model.game_model.game_status import GameStatus
from model.tile.hexagon_coordinates import HexagonCoordinates
from model.troops import PlayableTroopType
from player.base_player import BasePlayer


class GameUpdate(BaseModel):
    pass


class TroopMovedUpdate(GameUpdate):
    update_type: Literal["troop_moved_update"] = "troop_moved_update"
    troop: PlayableTroopType
    from_coordinate: HexagonCoordinates
    to_coordinate: HexagonCoordinates


class TroopRemovedUpdate(GameUpdate):
    update_type: Literal["troop_removed_update"] = "troop_removed_update"
    coordinate: HexagonCoordinates


class TroopSpawnedUpdate(GameUpdate):
    update_type: Literal["troop_spawned_update"] = "troop_spawned_update"
    troop: PlayableTroopType
    coordinate: HexagonCoordinates


class PlayerRemovedUpdate(GameUpdate):
    update_type: Literal["player_removed_update"] = "player_removed_update"
    player: BasePlayer


class GameOverUpdate(GameUpdate):
    update_type: Literal["game_over_update"] = "game_over_update"
    winner: BasePlayer


class GameStatusUpdate(GameUpdate):
    update_type: Literal["game_status_update"] = "game_status_update"
    game_status: GameStatus


class PlanningPhaseTime(GameUpdate):
    update_type: Literal["planning_phase_time"] = "planning_phase_time"
    remaining_time: int


GameUpdate = Annotated[
    Union[
        TroopMovedUpdate,
        TroopRemovedUpdate,
        TroopSpawnedUpdate,
        PlayerRemovedUpdate,
        GameOverUpdate,
        GameStatusUpdate,
        PlanningPhaseTime,
    ],
    Field(discriminator="update_type"),
]
