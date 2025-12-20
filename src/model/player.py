from pydantic import BaseModel


class Player(BaseModel):
    player_id: int
    username: str

    class Config:
        frozen = True
