from typing import Literal, Union

from pydantic import BaseModel

from model.game_model.player_actions import GameAction
from player.player import Player


class PlayerRequest(BaseModel):
    player: Player


class ClearActions(PlayerRequest):
    request_type: Literal["clear_actions_request"] = "clear_actions_request"
    pass


class PerformActionRequest(PlayerRequest):
    request_type: Literal["save_action_request"] = "save_action_request"
    game_action: GameAction


PlayerRequest = Union[ClearActions, PerformActionRequest]
