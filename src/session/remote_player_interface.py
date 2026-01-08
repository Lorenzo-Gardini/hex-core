import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Thread, Event

from fastapi import WebSocket
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from controller.game_update import Update
from lobby.lobbies_controller import LobbiesController
from player.player import PlayerID, Player
from session.game_session import GameSession
from session.pub_sub import pub_sub

logger = logging.getLogger(__name__)


class RemotePlayerInterface:

    def __init__(self):
        self._players_to_websocket: dict[PlayerID, WebSocket] = dict()  # PlayerID
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: Thread | None = None
        self._support_executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
        self._loop_ready = Event()

    def start(self):
        """Start the event loop in a separate thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            # Wait for the loop to be ready (with timeout)
            if not self._loop_ready.wait(timeout=5.0):
                raise RuntimeError("Event loop failed to start within 5 seconds")
            logger.info("RemotePlayerInterface event loop started")

    def _run_loop(self):
        """Run the asyncio event loop in a separate thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        logger.info("Event loop running in separate thread")
        self._loop.run_forever()

    async def new_connection(
        self, player_id: PlayerID, username: str, lobby_size: int, websocket: WebSocket
    ):
        """
        Handle new WebSocket connection.
        This should be called from FastAPI's event loop.
        """
        if self._loop is None:
            raise RuntimeError("Event loop not started. Call start() first.")

        future = asyncio.run_coroutine_threadsafe(
            self._handle_connection(player_id, username, lobby_size, websocket),
            self._loop,
        )

        # This will block until the WebSocket disconnects
        try:
            await asyncio.wrap_future(future)
        except Exception as e:
            logger.error(
                f"Error in connection for player {player_id}: {e}", exc_info=True
            )
            raise

    async def _handle_connection(
        self, player_id: PlayerID, username: str, lobby_size: int, websocket: WebSocket
    ):
        """
        Internal method that runs in the separate event loop.
        Handles the entire lifecycle of a WebSocket connection.
        """
        await websocket.accept()
        self._players_to_websocket[player_id] = websocket
        logger.info(f"Player {player_id} connected")

        # Create subscription callback
        player_subscription = partial(self._sync_send_update, websocket)

        # Subscribe for player's updates (pub_sub is sync, so use executor)
        await self._loop.run_in_executor(
            self._support_executor,
            pub_sub.subscribe,
            GameSession.update_topic(player_id),  # GameSession.update_topic(player_id)
            player_subscription,
        )

        await self._loop.run_in_executor(
            self._support_executor,
            pub_sub.publish,
            LobbiesController.ADD_PLAYER_TOPIC,
            lobby_size,
            Player(id=player_id, username=username),
        )

        try:
            while True:
                try:
                    data = await websocket.receive_json()
                    # Assuming PlayerRequest validation
                    # validated_data = PlayerRequest.model_validate(data)

                    # Publish player request (pub_sub is sync, so use executor)
                    await self._loop.run_in_executor(
                        self._support_executor,
                        pub_sub.publish,
                        GameSession.request_topic(player_id),
                        data,  # validated_data
                    )
                except ValidationError as e:
                    logger.warning(f"Invalid request from {player_id}: {e}")
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": "invalid_request",
                        }
                    )
        except WebSocketDisconnect:
            logger.info(f"Player {player_id} disconnected")
        except Exception as e:
            logger.error(f"Unexpected error for player {player_id}: {e}", exc_info=True)
        finally:
            # Cleanup
            logger.info(f"Cleaning up player {player_id}")

            # Publish disconnect event
            await self._loop.run_in_executor(
                self._support_executor,
                pub_sub.publish,
                LobbiesController.REMOVE_PLAYER_TOPIC,
                player_id,
            )

            # Unsubscribe
            await self._loop.run_in_executor(
                self._support_executor,
                pub_sub.unsubscribe,
                GameSession.update_topic(player_id),
                player_subscription,
            )

            # Remove from tracking
            self._players_to_websocket.pop(player_id, None)

    def _sync_send_update(self, websocket: WebSocket, update: Update):
        """
        Called from pub_sub (sync context) when game sends updates.
        Schedules the actual send on the event loop.
        """
        if self._loop is None:
            logger.error("Cannot send update: event loop not running")
            return

        async def _async_send_update():
            try:
                await websocket.send_json(update.model_dump())
            except WebSocketDisconnect:
                logger.debug("WebSocket already disconnected during send")
            except Exception as e:
                logger.error(f"Error sending update: {e}", exc_info=True)

        # Schedule on the event loop
        future = asyncio.run_coroutine_threadsafe(_async_send_update(), self._loop)

        # Add error handler
        def _handle_result(fut):
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Failed to send update: {e}", exc_info=True)

        future.add_done_callback(_handle_result)

    def shutdown(self):
        """Clean shutdown of the event loop"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5.0)
        self._support_executor.shutdown(wait=True)
