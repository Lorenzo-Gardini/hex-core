from model.board.board import Board
from model.board.hexagon_coordinates import HexagonCoordinates
from player.base_player import Player


def generate_pointy_hexagon(radius: int) -> set[HexagonCoordinates]:
    tiles = set()
    for q in range(-radius, radius + 1):
        r_min = max(-radius, -q - radius)
        r_max = min(radius, -q + radius)
        for r in range(r_min, r_max + 1):
            tiles.add(HexagonCoordinates(q=q, r=r))
    return tiles


def generate_flat_top_hexagon(radius: int) -> set[HexagonCoordinates]:
    tiles = set()
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= radius:
                tiles.add(HexagonCoordinates(q=q, r=r))
    return tiles


def generate_triangle(size: int) -> set[HexagonCoordinates]:
    tiles = set()
    for q in range(size):
        for r in range(size - q):
            tiles.add(HexagonCoordinates(q=q, r=r))
    return tiles


def generate_square(size: int) -> set[HexagonCoordinates]:
    tiles = set()
    offset = size // 2
    for r in range(-offset, offset + 1):
        r_offset = r // 2
        for q in range(-offset - r_offset, size - offset - r_offset):
            tiles.add(HexagonCoordinates(q=q, r=r))
    return tiles


def generate_map(n_players: int) -> set[HexagonCoordinates]:
    if n_players == 3:
        return generate_triangle(size=8)
    if n_players == 4:
        return generate_square(size=8)
    if n_players in (5, 6):
        return generate_pointy_hexagon(radius=8)
    if n_players in (7, 8):
        return generate_flat_top_hexagon(radius=8)
    raise ValueError(f"Number of player not supported: {n_players}")


def generate_board(players: set[Player]) -> Board:
    return Board(
        coordinates_to_occupation={
            coordinate: None for coordinate in generate_map(len(players))
        }
    )
