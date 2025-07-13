from src.client.main import GameClient
import asyncio


async def main():
    client = GameClient()
    client.run()


asyncio.run(main())
