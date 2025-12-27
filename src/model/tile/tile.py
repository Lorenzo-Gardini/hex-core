from pydantic import BaseModel

from model.troops import BaseTroop


class Tile(BaseModel):
    occupation: BaseTroop | None = None

    class ConfigDict:
        frozen = True
