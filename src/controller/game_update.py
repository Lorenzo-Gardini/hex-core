from typing import Literal, Union

from pydantic import BaseModel

from model.game_model.game_event import GameEvent
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_actions import GameAction
from player.player import Player


class GameUpdate(BaseModel):
    pass


class GameStatusUpdate(GameUpdate):
    update_type: Literal["game_status_update"] = "game_status_update"
    game_status: GameStatus


class GameEventUpdate(GameUpdate):
    update_type: Literal["game_event_update"] = "game_event_update"
    event: GameEvent


class GameOverUpdate(GameUpdate):
    update_type: Literal["game_over_update"] = "game_over_update"
    winner: Player


class PlanningPhaseTimeUpdate(GameUpdate):
    update_type: Literal["planning_phase_time_update"] = "planning_phase_time_update"
    remaining_time: float


class PersonalUpdate(BaseModel):
    pass


class RemainingActionPointsUpdate(PersonalUpdate):
    update_type: Literal["remaining_action_points_update"] = (
        "remaining_action_points_update"
    )
    remaining_action_points: int


class ApprovedActionUpdate(PersonalUpdate):
    update_type: Literal["approved_action_update"] = "approved_action_update"
    selected_action: GameAction


class InsufficientActionPointsUpdate(PersonalUpdate):
    update_type: Literal["insufficient_action_points_update"] = (
        "insufficient_action_points_update"
    )


class IllegalActionUpdate(PersonalUpdate):
    update_type: Literal["illegal_action_update"] = "illegal_action_update"
    game_action: GameAction


GameUpdate = Union[
    GameStatusUpdate,
    GameEventUpdate,
    GameOverUpdate,
    PlanningPhaseTimeUpdate,
]

PersonalUpdate = Union[
    RemainingActionPointsUpdate,
    ApprovedActionUpdate,
    InsufficientActionPointsUpdate,
    IllegalActionUpdate,
]

Update = Union[
    GameUpdate,
    PersonalUpdate,
]
