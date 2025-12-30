from pydantic import Field
from pydantic_settings import BaseSettings


class GameConfig(BaseSettings):
    max_turns: int = Field(default=20, gt=1)
    winning_core_control_turns: int = Field(default=3, ge=1)
    random_seed: int = Field(default=1234)
    march_troop_action_points: int = Field(default=1, ge=1)
    spawn_troop_action_points: int = Field(default=2, ge=1)


game_config = GameConfig()
