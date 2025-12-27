from pydantic import Field
from pydantic_settings import BaseSettings


class PlayerConfig(BaseSettings):
    username_min_length: int = Field(default=3)
    username_max_length: int = Field(default=8)


player_config = PlayerConfig()
