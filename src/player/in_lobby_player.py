import asyncio
from typing import Callable

from fastapi import WebSocket, WebSocketDisconnect

from model.game_model.player_actions import GameAction
from player.base_player import Player
from player.in_game_player import InGamePlayer


class InLobbyPlayer(Player):

    def __init__(
        self,
        player_id: str,
        username: str,
        lobby_leave_callback: Callable[["InLobbyPlayer"], None],
        websocket: WebSocket,
    ):
        self._websocket = websocket
        self._lobby_leave_callback = lobby_leave_callback
        self._disconnection_task = asyncio.create_task(self._is_alive_task())
        super().__init__(player_id=player_id, username=username)

    def to_game_player(
        self,
        add_player_action_callback: Callable[[InGamePlayer, GameAction], None],
        clear_player_actions_callback: Callable[[InGamePlayer], None],
    ) -> InGamePlayer:
        self._disconnection_task.cancel()
        self._disconnection_task.add_done_callback(lambda _: None)

        return InGamePlayer(
            player_id=self.player_id,
            username=self.username,
            websocket=self._websocket,
            add_player_action_callback=add_player_action_callback,
            clear_player_actions_callback=clear_player_actions_callback,
        )

    async def _is_alive_task(self):
        try:
            while True:
                await self._websocket.receive_text()
        except WebSocketDisconnect:
            await asyncio.to_thread(self._lobby_leave_callback, self)
