from typing import Literal
from pydantic import BaseModel
from model.player import Player


class Troop(BaseModel):
    owner: Player

    class Config:
        frozen = True


class TriangleTroop(Troop):
    troop_type: Literal["triangle_troop"] = "triangle_troop"

    def __gt__(self, other: Troop) -> bool:
        return isinstance(other, PentagonTroop)

    def __lt__(self, other: Troop) -> bool:
        return isinstance(other, SquareTroop)

    def __eq__(self, other: Troop) -> bool:
        return isinstance(other, TriangleTroop)


class SquareTroop(Troop):
    troop_type: Literal["square_troop"] = "square_troop"

    def __gt__(self, other: Troop) -> bool:
        return isinstance(other, TriangleTroop)

    def __lt__(self, other: Troop) -> bool:
        return isinstance(other, PentagonTroop)

    def __eq__(self, other: Troop) -> bool:
        return isinstance(other, SquareTroop)


class PentagonTroop(Troop):
    troop_type: Literal["pentagon_troop"] = "pentagon_troop"

    def __gt__(self, other: Troop) -> bool:
        return isinstance(other, SquareTroop)

    def __lt__(self, other: Troop) -> bool:
        return isinstance(other, TriangleTroop)

    def __eq__(self, other: Troop) -> bool:
        return isinstance(other, PentagonTroop)


class HomeBaseTroop(Troop):
    troop_type: Literal["home_base_troop"] = "home_base_troop"

    def __gt__(self, _: Troop) -> bool:
        return False

    def __lt__(self, _: Troop) -> bool:
        return True

    def __eq__(self, _: Troop) -> bool:
        return False


type PlayableTroopTypes = TriangleTroop | SquareTroop | PentagonTroop
type Troop = TriangleTroop | SquareTroop | PentagonTroop | HomeBaseTroop
