from pydantic import Field
from pydantic_settings import BaseSettings


class LobbyConfig(BaseSettings):
    min_number_of_player: int = Field(default=3, gt=2)
    max_number_of_player: int = Field(default=8, lt=10)


lobby_config = LobbyConfig()
