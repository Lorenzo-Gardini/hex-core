

from typing import Literal
from pydantic import BaseModel

from model.game_model.game_update import GameUpdate
from model.game_model.player_actions import PlayerAction


class GlobalUpdate(BaseModel):
    pass

class UpdateFromModel(GlobalUpdate):
    global_update_type: Literal['update_from_model'] = 'update_from_model'
    update: GameUpdate

class RemainingTurnTime(GlobalUpdate):
    global_update_type: Literal['remaining_turn_time'] = 'remaining_turn_time'
    time: int

class InvalidAction(GlobalUpdate):
    global_update_type: Literal['invalid_action'] = 'invalid_action'
    player_action: PlayerAction

class ValidAction(GlobalUpdate):
    global_update_type: Literal['valid_action'] = 'valid_action'
    Player_action: PlayerAction

type GlobalUpdate = UpdateFromModel | RemainingTurnTime | InvalidAction | ValidAction