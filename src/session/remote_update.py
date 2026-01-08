from dataclasses import dataclass
from uuid import UUID

from controller.game_update import GameUpdate


@dataclass(frozen=True)
class RemoteGameUpdate:
    game_id: UUID
    update: GameUpdate
