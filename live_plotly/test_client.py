import asyncio
import random
import json
import websockets


async def send_data():
    uri = "ws://localhost:5001/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            data_point = random.uniform(0, 100)
            await websocket.send(json.dumps({"msg": data_point}))
            print(f"Sent: {data_point}")
            ## receive message
            # response = await websocket.recv()
            # print(f"response: {response}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(send_data())
