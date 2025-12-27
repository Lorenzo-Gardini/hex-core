from pydantic import Field

from clonable_base_model import ClonableBaseModel
from model.troops import BaseTroop


class CoreControlScore(ClonableBaseModel):
    troop: BaseTroop | None = None
    n_turn_of_control: int = Field(..., ge=0)

    def score_for_troop(self, troop: BaseTroop) -> "CoreControlScore":
        if self.troop == troop:
            return self.copy_with(n_turn_of_control=self.n_turn_of_control + 1)
        else:
            return CoreControlScore(troop=troop, n_turn_of_control=1)

    @staticmethod
    def clear() -> "CoreControlScore":
        return CoreControlScore(troop=None, n_turn_of_control=0)
