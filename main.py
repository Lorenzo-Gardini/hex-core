from fastapi import FastAPI, WebSocket
from pydantic import BaseModel, Field

from controllers.games_controller.games_controller_impl import GameControllerImpl
from controllers.lobby.lobbies_controller import LobbiesController
from controllers.lobby.lobby_config import lobby_config
from model.game_model.game_status_updater import GameStatusUpdater
from player.base_player import BasePlayer
from player.in_lobby_player import InLobbyPlayer
from player.player_config import player_config

games_controller = GameControllerImpl(GameStatusUpdater(), lambda x: x)
lobby_controller = LobbiesController(games_controller)
app = FastAPI()


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    params = websocket.query_params
    lobby_size = params.get("lobby_size")
    join_request = _JoinRequest(
        lobby_size=int(lobby_size) if lobby_size is not None else None,
        username=params.get("username"),
    )

    await websocket.accept()

    callback = lambda player: lobby_controller.remove_player_from_lobby(
        join_request.lobby_size, player
    )

    lobby_controller.add_player_in_lobby(
        join_request.lobby_size,
        InLobbyPlayer(
            player_id=BasePlayer.random_id(),
            username=join_request.username,
            lobby_leave_callback=callback,
            websocket=websocket,
        ),
    )
