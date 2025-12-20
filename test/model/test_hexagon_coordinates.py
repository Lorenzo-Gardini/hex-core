from model.tile.hexagon_coordinates import HexagonCoordinates


def test_hexagon_are_nearby():
    center = HexagonCoordinates(0, 0)
    west = HexagonCoordinates(-1, 0)
    east = HexagonCoordinates(1, 0)
    north_west = HexagonCoordinates(0, -1)
    north_east = HexagonCoordinates(1, -1)
    south_west = HexagonCoordinates(-1, 1)
    south_east = HexagonCoordinates(0, 1)

    assert all(
        center.is_nearby(tile)
        for tile in [
            west,
            east,
            north_west,
            north_east,
            south_west,
            south_east,
        ]
    )


def test_hexagon_are_outside_nearby():
    center = HexagonCoordinates(0, 0)
    outer_tile_1 = HexagonCoordinates(1, 1)
    outer_tile_2 = HexagonCoordinates(-1, -1)
    outer_tile_3 = HexagonCoordinates(2, 0)
    assert not any(
        center.is_nearby(tile)
        for tile in [
            outer_tile_1,
            outer_tile_2,
            outer_tile_3,
        ]
    )


def test_hexagon_properties():
    q = 3
    r = -2
    hexagon = HexagonCoordinates(q, r)
    assert hexagon.q == q
    assert hexagon.r == r


def test_hexagon_distance():
    hexagon_a = HexagonCoordinates(0, 0)
    hexagon_b = HexagonCoordinates(1, -1)
    hexagon_c = HexagonCoordinates(3, -2)

    assert hexagon_a.distance(hexagon_a) == 0
    assert hexagon_a.distance(hexagon_b) == 1
    assert hexagon_a.distance(hexagon_c) == 3
    assert hexagon_b.distance(hexagon_c) == 2
