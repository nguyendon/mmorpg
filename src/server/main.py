import asyncio
import websockets

class GameServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    # Handle client messages here
                    print(f"Received message: {message}")
                    # Echo back for now
                    await websocket.send(f"Server received: {message}")
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    print(f"Error handling message: {e}")
                    await websocket.send(f"Error: {str(e)}")
        except websockets.exceptions.ConnectionClosed:
            print("Client connection closed unexpectedly")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            await self.unregister(websocket)

    async def run(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    server = GameServer()
    asyncio.run(server.run())
