import copy
import random

from model.board.board_factory import generate_board
from model.game_model.core_control_score import CoreControlScore
from model.game_model.game_config import game_config
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_order import PlayerOrder
from player.base_player import Player

random.seed(game_config.random_seed)


def game_status_factory(players: set[Player]) -> GameStatus:
    players_copy = copy.deepcopy(list(players))
    random.shuffle(players_copy)

    return GameStatus(
        turn_number=1,
        player_order=PlayerOrder(players=players_copy),
        winner=None,
        board=generate_board(players),
        control_score=CoreControlScore(troop=None, n_turn_of_control=0),
    )
