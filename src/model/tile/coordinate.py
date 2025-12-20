from abc import ABC, abstractmethod
from pydantic import BaseModel


class Coordinate(ABC, BaseModel):
    @abstractmethod
    def distance(self, other: "Coordinate") -> int:
        """Compute the distance between this coordinate and another coordinate.
        Args:
            other (Coordinate): The other coordinates to compute the distance to.
        Returns:
            int: The distance between the two coordinates.
        """
        pass

    def is_nearby(self, other: "Coordinate") -> bool:
        """Check if this coordinate is nearby another coordinate.
        Args:
            other (Coordinate): The other coordinates to check proximity with.
        Returns:
            bool: True if the coordinates are nearby, False otherwise.
        """
        return self.distance(other) == 1

    class Config:
        frozen = True
