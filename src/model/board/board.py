from pydantic import BaseModel
from model.troops.troops import Troop
from model.player import Player
from model.tile.tile import Tile
from model.tile.hexagon_coordinates import HexagonCoordinates


class Board(BaseModel):
    coordinates_to_tile: dict[HexagonCoordinates, Tile]

    def add_player_troop(self, troop: Troop, coordinate: HexagonCoordinates):
        self.coordinates_to_tile[coordinate].occupation = troop

    def move_troop(
        self,
        starting_coordinate: HexagonCoordinates,
        destination_coordinate: HexagonCoordinates,
    ):
        troop = self.coordinates_to_tile[starting_coordinate].occupation
        self.coordinates_to_tile[destination_coordinate].occupation = troop
        self.coordinates_to_tile[starting_coordinate].occupation = None

    def remove_troop(self, coordinate: HexagonCoordinates):
        self.coordinates_to_tile[coordinate].occupation = None

    def remove_player_troops(self, player: Player):
        for tile in self.coordinates_to_tile.values():
            if tile.occupation is not None and tile.occupation.owner == player:
                tile.occupation = None
