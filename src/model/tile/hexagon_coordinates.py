"""Hexagon coordinates module. Defines the HexagonCoordinates class for handling hexagonal grid coordinates. Coordinates are represented using axial coordinates (q, r). q is the coordinate along the horizontal axis, and r is the coordinate along the diagonal axis."""


class HexagonCoordinates:
    def __init__(self, q: int, r: int):
        self._q = q
        self._r = r

    @property
    def r(self) -> int:
        return self._r

    @property
    def q(self) -> int:
        return self._q

    def is_nearby(self, other: "HexagonCoordinates") -> bool:
        """Check if another hexagon is adjacent (nearby) to this hexagon.
        Args:
            other (HexagonCoordinates): The other hexagon coordinates to check against.
        Returns:
            bool: True if the other hexagon is adjacent, False otherwise."""

        return (
            max(
                abs(self.q - other.q),
                abs(self.r - other.r),
                abs(-(self.q + self.r) + (other.q + other.r)),
            )
            == 1
        )
