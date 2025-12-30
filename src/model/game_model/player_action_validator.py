from model.board.board import Board
from model.board.hexagon_coordinates import HexagonCoordinates
from model.game_model.game_status.game_status import GameStatus
from model.game_model.player_actions import (
    MarchTroopAction,
    SpawnTroopAction,
    GameAction,
)
from model.troops import (
    HomeBaseTroop,
    BaseTroop,
    SquareTroop,
    TriangleTroop,
    PentagonTroop,
)
from player.base_player import Player


def _troop_is_present(board: Board, coordinates: HexagonCoordinates) -> bool:
    return board.coordinates_to_tile[coordinates].occupation is not None


def _coordinates_out_of_board(board: Board, coordinates: HexagonCoordinates) -> bool:
    return coordinates not in board.coordinates_to_tile


def _is_tile_of_player(
    board: Board, coordinates: HexagonCoordinates, player: Player
) -> bool:
    occupation = board.coordinates_to_tile[coordinates].occupation
    return occupation is not None and occupation.owner == player


def _is_valid_troop(troop: BaseTroop) -> bool:
    return isinstance(troop, (SquareTroop, PentagonTroop, TriangleTroop))


def _is_occupied(board: Board, coordinates: HexagonCoordinates) -> bool:
    return board.coordinates_to_tile[coordinates].occupation is not None


def _is_near_player_home_base(
    board: Board, coordinates: HexagonCoordinates, player: Player
) -> bool:
    home_base_coordinates = next(
        (
            coordinates
            for coordinates, tile in board.coordinates_to_tile.items()
            if tile.occupation is not None
            and isinstance(tile.occupation, HomeBaseTroop)
            and tile.occupation.owner == player
        ),
        None,
    )
    return (
        home_base_coordinates.is_nearby(coordinates)
        if home_base_coordinates is not None
        else False
    )


def is_valid_action(
    player: Player, action: GameAction, game_status: GameStatus
) -> bool:
    board = game_status.board
    match action:
        case MarchTroopAction(
            starting_coordinates=starting_coordinates,
            destination_coordinates=destination_coordinates,
        ):
            conditions = [
                lambda: _coordinates_out_of_board(board, starting_coordinates),
                lambda: _coordinates_out_of_board(board, destination_coordinates),
                lambda: not _troop_is_present(board, starting_coordinates),
                lambda: not _is_tile_of_player(board, starting_coordinates, player),
                # lambda: _is_tile_of_player(board, destination_coordinates, player),
            ]
            return not any(condition() for condition in conditions)

        case SpawnTroopAction(coordinates=coordinates, troop=troop):
            conditions = [
                lambda: _coordinates_out_of_board(board, coordinates),
                lambda: _is_occupied(board, coordinates),
                lambda: not _is_near_player_home_base(board, coordinates, player),
                lambda: not _is_valid_troop(troop),
            ]
            return not any(condition() for condition in conditions)
        case _:
            raise ValueError("Invalid PlayerAction provided")
