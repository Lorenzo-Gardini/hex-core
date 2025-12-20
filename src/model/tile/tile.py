
from dataclasses import dataclass

class HexagonCoordinates:
    def __init__(self, p: int, q: int):
        self._p = p
        self._q = q

    @property
    def p(self) -> int:
        return self._p
    
    @property
    def q(self) -> int:
        return self._q   


    def is_nearby(self, other: 'HexagonCoordinates') -> bool:
        return max(
            abs(self.p - other.p), 
            abs(self.q - other.q), 
            abs(-(self.p + self.q) + (other.p + other.q))
            ) == 1