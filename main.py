import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel, Field, ValidationError

from controller.action_point_calculator import calculate_action_points
from controller.game_controller import GameController
from controller.game_controller_setup import GameControllerSetup
from controller.level_loader import LevelLoader
from lobby.lobbies_controller import LobbiesController
from lobby.lobby_config import lobby_config
from model.board.board_factory import generate_board
from model.game_model.game_status.game_status_factory import generate_game_status
from model.game_model.game_status.game_status_updater import update_game_status
from model.game_model.player_action_validator import is_valid_action
from player.player import Player
from player.player_config import player_config
from session.game_session import GameSession
from session.remote_player_interface import RemotePlayerInterface
from session.session import Session

level_loader = LevelLoader(level_folder_path="src/resources/")
level_loader.load_levels()


def _board_factory(players: list[Player]):
    return generate_board(players, level_loader.get_level)


def _game_status_factory(players: set[Player]):
    return generate_game_status(players, _board_factory)


def _game_controller_factory(players: set[Player], session: Session) -> GameController:
    return GameController(
        GameControllerSetup(
            update_game_status,
            is_valid_action,
            calculate_action_points,
            _game_status_factory,
        ),
        players,
        session,
    )


def _session_factory(players: set[Player]) -> Session:
    return GameSession(players, _game_controller_factory)


class _JoinRequest(BaseModel):
    lobby_size: int | None = Field(
        default=5,
        ge=lobby_config.min_number_of_player,
        le=lobby_config.max_number_of_player,
    )
    username: str = Field(
        ...,
        min_length=player_config.username_min_length,
        max_length=player_config.username_max_length,
    )


player_interface = RemotePlayerInterface()
lobbies_controller = LobbiesController(_session_factory)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_):
    """Application lifespan - startup and shutdown"""
    # Startup
    player_interface.start()
    yield
    # Shutdown
    player_interface.shutdown()


app = FastAPI(lifespan=lifespan)


@app.websocket("/hex-core")
async def websocket_endpoint(websocket: WebSocket):
    params = websocket.query_params
    lobby_size = params.get("lobby_size")
    try:
        join_request = _JoinRequest(
            lobby_size=int(lobby_size) if lobby_size is not None else None,
            username=params.get("username"),
        )
        player_id = Player.random_id()

        await player_interface.new_connection(
            player_id, join_request.username, join_request.lobby_size, websocket
        )

    except ValidationError:
        await websocket.close(code=400)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
