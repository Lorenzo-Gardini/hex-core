from model.game_model.game_config import game_config
from model.game_model.player_actions import GameAction


def calculate_action_points(
    player_actions: list[GameAction],
) -> bool:
    remaining_action_points = game_config.default_action_points - sum(
        action.action_points_cost for action in player_actions
    )

    return remaining_action_points >= 0
