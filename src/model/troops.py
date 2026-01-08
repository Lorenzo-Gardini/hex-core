from abc import ABC, abstractmethod
from typing import Literal, Union

from pydantic import BaseModel

from player.player import Player


class BaseTroop(BaseModel, ABC):
    owner: Player

    @abstractmethod
    def __gt__(self, other: "BaseTroop") -> bool:
        pass

    @abstractmethod
    def __lt__(self, other: "BaseTroop") -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: "BaseTroop") -> bool:
        pass

    class ConfigDict:
        frozen = True


class TriangleTroop(BaseTroop):
    troop_type: Literal["triangle_troop"] = "triangle_troop"

    def __gt__(self, other: BaseTroop) -> bool:
        return isinstance(other, PentagonTroop)

    def __lt__(self, other: BaseTroop) -> bool:
        return isinstance(other, SquareTroop)

    def __eq__(self, other: BaseTroop) -> bool:
        return isinstance(other, TriangleTroop)


class SquareTroop(BaseTroop):
    troop_type: Literal["square_troop"] = "square_troop"

    def __gt__(self, other: BaseTroop) -> bool:
        return isinstance(other, TriangleTroop)

    def __lt__(self, other: BaseTroop) -> bool:
        return isinstance(other, PentagonTroop)

    def __eq__(self, other: BaseTroop) -> bool:
        return isinstance(other, SquareTroop)


class PentagonTroop(BaseTroop):
    troop_type: Literal["pentagon_troop"] = "pentagon_troop"

    def __gt__(self, other: BaseTroop) -> bool:
        return isinstance(other, SquareTroop)

    def __lt__(self, other: BaseTroop) -> bool:
        return isinstance(other, TriangleTroop)

    def __eq__(self, other: BaseTroop) -> bool:
        return isinstance(other, PentagonTroop)


class HomeBaseTroop(BaseTroop):
    troop_type: Literal["home_base_troop"] = "home_base_troop"

    def __gt__(self, _: BaseTroop) -> bool:
        return False

    def __lt__(self, _: BaseTroop) -> bool:
        return True

    def __eq__(self, _: BaseTroop) -> bool:
        return False


PlayableTroopType = Union[TriangleTroop, SquareTroop, PentagonTroop]

Troop = Union[TriangleTroop, SquareTroop, PentagonTroop, HomeBaseTroop]
