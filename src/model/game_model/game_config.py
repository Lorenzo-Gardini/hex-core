from pydantic import Field
from pydantic_settings import BaseSettings


class GameConfig(BaseSettings):
    max_turns: int = Field(..., default=20)
    winning_core_control_turns: int = Field(..., default=3)


game_config_instance = GameConfig()
