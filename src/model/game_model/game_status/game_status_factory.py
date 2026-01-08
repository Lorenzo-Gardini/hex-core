import copy
import random
from typing import Callable

from model.board.board import Board
from model.game_model.core_control_score import CoreControlScore
from model.game_model.game_config import game_config
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_order import PlayerOrder
from player.player import Player

random.seed(game_config.random_seed)


def generate_game_status(
    players: set[Player], board_generator: Callable[[list[Player]], Board]
) -> GameStatus:
    players_copy = copy.deepcopy(list(players))
    random.shuffle(players_copy)

    return GameStatus(
        turn_number=1,
        player_order=PlayerOrder(players=players_copy),
        winner=None,
        board=board_generator(players_copy),
        control_score=CoreControlScore(troop=None, n_turn_of_control=0),
    )
