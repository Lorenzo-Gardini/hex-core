from dataclasses import dataclass

from common.common_types import (
    UpdateModelFunction,
    ActionValidationFunction,
    ActionPointCalculationFunction,
    GameStatusFactory,
)


@dataclass(frozen=True)
class GameControllerSetup:
    update_game_status_fn: UpdateModelFunction
    action_validator_fn: ActionValidationFunction
    calculate_action_points_fn: ActionPointCalculationFunction
    game_status_factory: GameStatusFactory
