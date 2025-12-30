from typing import Union, Literal

from pydantic import BaseModel

from model.board.hexagon_coordinates import HexagonCoordinates
from model.game_model.player_actions import (
    GameAction,
    MarchTroopAction,
    SpawnTroopAction,
)
from model.troops import PlayableTroopType


class GameEvent(BaseModel):
    pass


class TroopMovedEvent(GameEvent):
    update_type: Literal["troop_moved_event"] = "troop_moved_event"
    troop: PlayableTroopType
    from_coordinates: HexagonCoordinates
    to_coordinates: HexagonCoordinates


class AttackWonEvent(GameEvent):
    update_type: Literal["attack_won_event"] = "attack_won_event"
    moving_troop: PlayableTroopType
    defending_troop: PlayableTroopType
    from_coordinates: HexagonCoordinates
    to_coordinates: HexagonCoordinates


class AttackLostEvent(GameEvent):
    update_type: Literal["attack_lost_event"] = "attack_lost_event"
    moving_troop: PlayableTroopType
    defending_troop: PlayableTroopType
    from_coordinates: HexagonCoordinates
    to_coordinates: HexagonCoordinates


class FailedMarchEvent(GameEvent):
    update_type: Literal["failed_attack_event"] = "failed_attack_event"
    attack_action: MarchTroopAction


class FailedSpawnEvent(GameEvent):
    update_type: Literal["failed_spawn_event"] = "failed_spawn_event"
    spawn_action: SpawnTroopAction


class TroopSpawnedEvent(GameEvent):
    update_type: Literal["troop_spawned_event"] = "troop_spawned_event"
    troop: PlayableTroopType
    coordinates: HexagonCoordinates


class PlayerRemovedEvent(GameEvent):
    update_type: Literal["player_removed_event"] = "player_removed_event"


class NoChangesEvent(GameEvent):
    update_type: Literal["no_changes_event"] = "no_changes_event"
    game_action: GameAction


GameEvent = Union[
    TroopMovedEvent,
    AttackWonEvent,
    TroopSpawnedEvent,
    PlayerRemovedEvent,
]
