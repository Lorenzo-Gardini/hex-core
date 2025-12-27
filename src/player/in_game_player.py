import asyncio
from abc import ABC
from typing import Callable

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter

from model.game_model.game_update import GameUpdate, GameOverUpdate
from model.game_model.player_actions import BasePlayerAction, PlayerAction
from player.base_player import BasePlayer

_type_adapter = TypeAdapter(PlayerAction)


class InGamePlayer(BasePlayer, ABC):
    def __init__(
        self,
        player_id: str,
        username: str,
        player_action_callback: Callable[[BasePlayerAction], None],
        websocket: WebSocket,
    ):
        self._websocket = websocket
        self._player_action_callback = player_action_callback
        asyncio.create_task(self._receive_message_task())
        super().__init__(player_id=player_id, username=username)

    def send_update(self, event: GameUpdate):
        try:
            asyncio.create_task(self._websocket.send_json(event.model_dump()))
            if isinstance(event, GameOverUpdate):
                asyncio.get_running_loop().run_until_complete(self._websocket.close())
        except WebSocketDisconnect:
            pass

    async def _receive_message_task(self):
        try:
            while True:
                data = await self._websocket.receive_text()
                game_action = _type_adapter.validate_json(data)
                await asyncio.to_thread(self._player_action_callback, game_action)
        except WebSocketDisconnect:
            pass
