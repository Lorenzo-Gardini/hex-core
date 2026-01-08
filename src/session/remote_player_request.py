from uuid import UUID

from controller.player_request import PlayerRequest


class RemotePlayerRequest:
    game_id: UUID
    player_request: PlayerRequest
