from model.board.board import Board
from model.game_model.game_status import GameStatus
from model.game_model.player_actions import (
    PlayerAction,
    MarchTroopAction,
    SpawnTroopAction,
)
from model.player import Player
from model.tile.hexagon_coordinates import HexagonCoordinates
from model.troops.troops import (
    HomeBaseTroop,
    Troop,
    SquareTroop,
    TriangleTroop,
    PentagonTroop,
)


def _troop_not_present(board: Board, coordinates: HexagonCoordinates) -> bool:
    return board.coordinates_to_tile[coordinates].occupation is not None


def _coordinates_out_of_board(board: Board, coordinates: HexagonCoordinates) -> bool:
    return coordinates in board.coordinates_to_tile


def _is_tile_of_player(
    board: Board, coordinates: HexagonCoordinates, player: Player
) -> bool:
    occupation = board.coordinates_to_tile[coordinates].occupation
    return occupation is not None and occupation.owner == player


def _is_valid_troop(troop: Troop) -> bool:
    return isinstance(troop, (SquareTroop, PentagonTroop, TriangleTroop))


def _is_not_occupied_yet(board: Board, coordinates: HexagonCoordinates) -> bool:
    return board.coordinates_to_tile[coordinates].occupation is None


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


def validate_action(player_action: PlayerAction, game_status: GameStatus) -> bool:
    board = game_status.board
    match player_action:
        case MarchTroopAction(
            player=player,
            starting_coordinates=starting_coordinates,
            destination_coordinates=destination_coordinates,
        ):
            conditions = [
                lambda: _coordinates_out_of_board(board, starting_coordinates),
                lambda: _coordinates_out_of_board(board, destination_coordinates),
                lambda: _troop_not_present(board, starting_coordinates),
                lambda: not _is_tile_of_player(board, starting_coordinates, player),
                lambda: _is_tile_of_player(board, destination_coordinates, player),
            ]
            return not any(condition() for condition in conditions)

        case SpawnTroopAction(player=player, coordinates=coordinates, troop=troop):
            conditions = [
                lambda: _coordinates_out_of_board(board, coordinates),
                lambda: _is_not_occupied_yet(board, coordinates),
                lambda: _is_near_player_home_base(board, coordinates, player),
                lambda: _is_valid_troop(troop),
            ]
            return not any(condition() for condition in conditions)
        case _:
            raise ValueError("Invalid PlayerAction provided")
