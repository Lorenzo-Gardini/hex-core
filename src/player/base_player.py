import uuid

from pydantic import BaseModel, Field

from player.player_config import player_config


class Player(BaseModel):
    player_id: str = Field(
        ...,
        min_length=player_config.username_min_length,
        max_length=player_config.username_max_length,
    )
    username: str

    @staticmethod
    def random_id() -> str:
        return str(uuid.uuid4())

    class ConfigDict:
        frozen = True
