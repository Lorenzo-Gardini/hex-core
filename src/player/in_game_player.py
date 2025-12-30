import asyncio
from abc import ABC
from typing import Callable

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from starlette.websockets import WebSocketState

from controllers.game_controller.update import Update
from model.game_model.player_actions import GameAction
from player.base_player import Player
from player.player_request import PlayerRequest, ClearActions


class InGamePlayer(Player, ABC):
    def __init__(
        self,
        player_id: str,
        username: str,
        add_player_action_callback: Callable[["InGamePlayer", GameAction], None],
        clear_player_actions_callback: Callable[["InGamePlayer"], None],
        websocket: WebSocket,
    ):
        self._websocket = websocket
        self._add_player_action_callback = add_player_action_callback
        self._clear_player_actions_callback = clear_player_actions_callback
        asyncio.create_task(self._receive_message_task())
        super().__init__(player_id=player_id, username=username)

    def send_update(self, update: Update):
        try:
            asyncio.create_task(self._websocket.send_json(update.model_dump()))
        except WebSocketDisconnect:
            pass

    def is_game_over(self):
        if self._websocket.client_state == WebSocketState.CONNECTED:
            close_task = asyncio.create_task(self._websocket.close())
            close_task.add_done_callback(lambda _: None)

    async def _receive_message_task(self):
        try:
            while True:
                data = await self._websocket.receive_text()
                action_request = PlayerRequest.validate_json(data)

                match action_request:
                    case ClearActions():
                        await asyncio.to_thread(
                            self._clear_player_actions_callback, self
                        )
                    case _:
                        await asyncio.to_thread(
                            self._add_player_action_callback,
                            self,
                            action_request.action,
                        )
        except ValidationError:
            pass
        except WebSocketDisconnect:
            pass
