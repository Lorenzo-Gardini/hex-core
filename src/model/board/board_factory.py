import math
from typing import Callable

from model.board.board import Board
from model.board.hexagon_coordinates import HexagonCoordinates
from model.troops import HomeBaseTroop, Troop
from player.player import Player


def generate_board(
    players: list[Player], map_generator: Callable[[int], set[HexagonCoordinates]]
) -> Board:
    n_players = len(players)
    points = map_generator(n_players)
    coordinates_to_occupation: dict[HexagonCoordinates, Troop | None] = {
        coordinate: None for coordinate in points
    }
    for player, vertice in zip(players, _find_vertices(points, n_players)):
        coordinates_to_occupation[vertice] = HomeBaseTroop(owner=player)

    return Board(coordinates_to_occupation=coordinates_to_occupation)


def _angle(coordinates: HexagonCoordinates) -> float:
    x, y = coordinates.to_xy()
    return math.atan2(x, y)


def _dist2(coordinates: HexagonCoordinates) -> float:
    x, y = coordinates.to_xy()
    return x * x + y * y


def _find_vertices(points, n_players) -> list[HexagonCoordinates]:
    buckets = [[] for _ in range(n_players)]
    step = 2 * math.pi / n_players

    for p in points:
        a = _angle(p)
        idx = int((a + math.pi) // step) % n_players
        buckets[idx].append(p)

    vertices = []
    for bucket in buckets:
        if not bucket:
            continue
        v = max(bucket, key=_dist2)
        vertices.append(v)

    return vertices
