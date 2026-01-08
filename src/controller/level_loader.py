import json
from pathlib import Path

from model.board.hexagon_coordinates import HexagonCoordinates


class LevelLoader:
    def __init__(self, level_folder_path: str) -> None:
        self._level_folder_path = level_folder_path
        self._levels = dict()

    def load_levels(self):
        for filename in Path(self._level_folder_path).iterdir():
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._levels[int(filename.stem)] = {
                HexagonCoordinates.model_validate(coordinate) for coordinate in data
            }

    def get_level(self, participants_number: int) -> set[HexagonCoordinates]:
        return self._levels.get(participants_number, set())
