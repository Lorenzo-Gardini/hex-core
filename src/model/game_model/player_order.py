from clonable_base_model import ClonableBaseModel
from player.base_player import Player


class PlayerOrder(ClonableBaseModel):
    players: list[Player]

    def remove_player(self, player: Player) -> "PlayerOrder":
        return PlayerOrder(
            players=[
                not_removed for not_removed in self.players if not_removed != player
            ]
        )

    def turn_players_order(self) -> "PlayerOrder":
        new_order = self.players[1:] + self.players[:1]
        return PlayerOrder(players=new_order)
