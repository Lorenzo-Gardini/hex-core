"""Hexagon coordinates module. Defines the HexagonCoordinates class for handling hexagonal grid coordinates. Coordinates are represented using axial coordinates (q, r). q is the coordinate along the horizontal axis, and r is the coordinate along the diagonal axis."""

from typing import override

from model.board.coordinate import Coordinate


class HexagonCoordinates(Coordinate):
    q: int
    r: int

    @override
    def distance(self, other: "HexagonCoordinates") -> int:
        """Compute the distance between this hexagon and another hexagon.
        Args:
            other (HexagonCoordinates): The other hexagon coordinates to compute the distance to.
        Returns:

            int: The distance between the two hexagons.
        """
        x1, z1 = self.q, self.r
        y1 = -x1 - z1
        x2, z2 = other.q, other.r
        y2 = -x2 - z2
        return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))
