"""
WebSocket Server - Real-time communication with browser extension.

Provides WebSocket support for live updates between the server
and connected browser clients.
"""

import asyncio
import json
import logging
from typing import Set

try:
    import websockets
    from websockets.server import serve
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

logger = logging.getLogger("nj_ide_copier.websocket")


class WebSocketServer:
    """WebSocket server for real-time client communication."""

    def __init__(self):
        self.clients: Set = set()
        self.message_handlers = {}

    async def register(self, websocket):
        """Register a new WebSocket client."""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_message(self, websocket, message):
        """Process an incoming WebSocket message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "")

            # Route to handler
            handler = self.message_handlers.get(msg_type)
            if handler:
                response = await handler(data)
                await websocket.send(json.dumps(response))
            else:
                # Echo back for unknown types
                await websocket.send(json.dumps({
                    "type": "ack",
                    "original_type": msg_type,
                    "status": "received",
                }))
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON",
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e),
            }))

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if self.clients:
            msg = json.dumps(message)
            await asyncio.gather(
                *[client.send(msg) for client in self.clients],
                return_exceptions=True,
            )

    def register_handler(self, message_type: str, handler):
        """Register a handler for a specific message type."""
        self.message_handlers[message_type] = handler


async def start_websocket_server(host: str = "localhost", port: int = 8766):
    """Start a WebSocket server."""
    if not HAS_WEBSOCKETS:
        logger.warning("websockets library not installed. WebSocket server not started.")
        return

    server = WebSocketServer()

    async with serve(server.register, host, port):
        logger.info(f"WebSocket server started on ws://{host}:{port}")
        await asyncio.Future()  # Run forever
