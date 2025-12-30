from pydantic import Field
from pydantic_settings import BaseSettings


class ControllerConfig(BaseSettings):
    turn_preparation_time: int = Field(default=30, gt=0)
    default_action_points: int = Field(default=3, gt=0)


controller_config = ControllerConfig()
