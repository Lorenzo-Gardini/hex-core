import copy
from collections import defaultdict
from typing import DefaultDict

from pydantic import BaseModel, field_serializer

from model.board.hexagon_coordinates import HexagonCoordinates
from model.troops import Troop, PlayableTroopType, HomeBaseTroop
from player.player import Player


class Board(BaseModel):
    coordinates_to_occupation: dict[HexagonCoordinates, Troop | None]

    @field_serializer("coordinates_to_occupation")
    def serialize_coordinates_to_occupation(
        self, coordinates_to_occupation: dict[HexagonCoordinates, Troop | None]
    ):

        return [
            (coord.q, coord.r, troop)
            for coord, troop in coordinates_to_occupation.items()
        ]

    def add_player_troop(self, troop: Troop, coordinate: HexagonCoordinates) -> "Board":
        new_board_state = copy.deepcopy(self.coordinates_to_occupation)
        new_board_state[coordinate] = troop
        return Board(coordinates_to_occupation=new_board_state)

    def move_troop(
        self,
        starting_coordinate: HexagonCoordinates,
        destination_coordinate: HexagonCoordinates,
    ) -> "Board":
        new_board_state = copy.deepcopy(self.coordinates_to_occupation)
        troop = new_board_state[starting_coordinate]
        new_board_state[destination_coordinate] = troop
        new_board_state[starting_coordinate] = None
        return Board(coordinates_to_occupation=new_board_state)

    def remove_troop(self, coordinate: HexagonCoordinates) -> "Board":
        new_board_state = copy.deepcopy(self.coordinates_to_occupation)
        new_board_state[coordinate] = None
        return Board(coordinates_to_occupation=new_board_state)

    def playable_troop_by_players(self) -> dict[Player, dict[PlayableTroopType, int]]:
        count: DefaultDict[Player, DefaultDict[PlayableTroopType, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for occupation in self.coordinates_to_occupation.values():
            if occupation is not None and not isinstance(occupation, HomeBaseTroop):
                count[occupation.owner][occupation] += 1

        return dict(count)

    def remove_player_troops(self, player: Player) -> "Board":
        new_board_state = copy.deepcopy(self.coordinates_to_occupation)
        for coordinate in new_board_state.keys():

            if (
                new_board_state[coordinate] is not None
                and new_board_state[coordinate].owner == player
            ):
                new_board_state[coordinate] = None

        return Board(coordinates_to_occupation=new_board_state)
