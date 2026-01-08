import uuid

from pydantic import BaseModel, field_serializer

PlayerID = uuid.UUID


class Player(BaseModel):
    id: PlayerID
    username: str

    def __hash__(self):
        return hash((self.id, self.username))

    def __eq__(self, other):
        return (self.id, self.username) == (other.id, other.username)

    @field_serializer("id")
    def serialize_id(self, player_id: PlayerID):
        return str(player_id)

    @staticmethod
    def random_id() -> PlayerID:
        return uuid.uuid4()

    class ConfigDict:
        frozen = True
