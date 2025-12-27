from pydantic import Field
from pydantic_settings import BaseSettings


class LobbyConfig(BaseSettings):
    min_number_of_player: int = Field(default=3)
    max_number_of_player: int = Field(default=8)


lobby_config = LobbyConfig()
