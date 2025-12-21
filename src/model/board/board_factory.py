from model.tile.hexagon_coordinates import HexagonCoordinates


def generate_pointy_hexagon(radius: int) -> list[HexagonCoordinates]:
    tiles = []
    for q in range(-radius, radius + 1):
        r_min = max(-radius, -q - radius)
        r_max = min(radius, -q + radius)
        for r in range(r_min, r_max + 1):
            tiles.append(HexagonCoordinates(q, r))
    return tiles


def generate_flat_top_hexagon(radius: int) -> list[HexagonCoordinates]:
    tiles = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= radius:
                tiles.append(HexagonCoordinates(q, r))
    return tiles


def generate_triangle(size: int) -> list[HexagonCoordinates]:
    tiles = []
    for q in range(size):
        for r in range(size - q):
            tiles.append(HexagonCoordinates(q, r))
    return tiles


def generate_square(size: int) -> list[HexagonCoordinates]:
    tiles = []
    offset = size // 2
    for r in range(-offset, offset + 1):
        r_offset = r // 2
        for q in range(-offset - r_offset, size - offset - r_offset):
            tiles.append(HexagonCoordinates(q, r))
    return tiles


def generate_map(players: int) -> set[HexagonCoordinates]:
    if players == 3:
        return generate_triangle(size=8)
    if players == 4:
        return generate_square(size=8)
    if players in (5, 6):
        return generate_pointy_hexagon(radius=8)
    if players in (7, 8):
        return generate_flat_top_hexagon(radius=8)
    raise ValueError(f"Number of player not supported: {players}")
