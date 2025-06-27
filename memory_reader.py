# memory_reader.py

import asyncio
import threading
import websockets
import json

class MemoryReader:
    def __init__(self):
        self.combo = 0
        self.accuracy = 100.0

        # Start async WebSocket in background thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        uri = "ws://localhost:24050/ws"
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    self.combo = data.get("gameplay", {}).get("combo", 0)
                    self.accuracy = data.get("gameplay", {}).get("accuracy", 100.0)
        except Exception as e:
            print("Tosu connection error:", e)

    def get_combo(self):
        return self.combo

    def get_accuracy(self):
        return self.accuracy
