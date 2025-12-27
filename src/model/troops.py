from abc import ABC, abstractmethod
from typing import Literal, Union, Annotated

from pydantic import BaseModel, Field

from player.base_player import BasePlayer


class BaseTroop(BaseModel, ABC):
    owner: BasePlayer

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


PlayableTroopType = Annotated[
    Union[TriangleTroop, SquareTroop, PentagonTroop], Field(discriminator="troop_type")
]

Troop = Annotated[
    Union[TriangleTroop, SquareTroop, PentagonTroop, HomeBaseTroop],
    Field(discriminator="troop_type"),
]
