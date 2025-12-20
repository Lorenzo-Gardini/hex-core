from pydantic import BaseModel
from model.troops.troops import Troop


class Tile(BaseModel):
    occupation: Troop | None = None

    class Config:
        frozen = True
