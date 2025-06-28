# memory_reader.py
import asyncio
import threading
import websockets
import json
import time
import config
from stats_tracker import StatsTracker


class MemoryReader:
    def __init__(self):
        self.combo = 0
        self.max_combo = 0
        self.misses = 0
        self.accuracy = 100.0
        self.hp = 1.0
        self.connected = False
        self.game_state = "menu"  # menu, playing, results
        self.map_info = {}

        # Stats tracking
        self.stats_tracker = StatsTracker()
        self.last_sample_time = 0
        self.was_playing = False

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_with_retry())

    async def connect_with_retry(self):
        while True:
            try:
                await self.connect()
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in {config.RECONNECT_DELAY} seconds...")
                self.connected = False
                await asyncio.sleep(config.RECONNECT_DELAY)

    async def connect(self):
        try:
            async with websockets.connect(config.WEBSOCKET_URI) as websocket:
                print("Connected to Tosu!")
                self.connected = True

                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        self.update_data(data)
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed by server")
                        break
                    except json.JSONDecodeError:
                        print("Invalid JSON received")
                        continue

        except Exception as e:
            print(f"Websocket error: {e}")
            self.connected = False
            raise

    def update_data(self, data):
        gameplay = data.get("gameplay", {})
        menu = data.get("menu", {})
        state = menu.get("state", {})

        # Update basic stats
        self.combo = gameplay.get("combo", {}).get("current", 0)
        self.max_combo = gameplay.get("combo", {}).get("max", 0)
        self.accuracy = gameplay.get("accuracy", 100.0)
        self.hp = gameplay.get("hp", {}).get("smooth", 1.0)
        self.misses = gameplay.get("hits", {}).get("0", 0)

        # Update game state
        new_state = state.get("name", "menu")

        # Update map info
        if "bm" in menu:
            bm = menu["bm"]
            self.map_info = {
                "title": bm.get("metadata", {}).get("title", "Unknown"),
                "artist": bm.get("metadata", {}).get("artist", "Unknown"),
                "difficulty": bm.get("metadata", {}).get("difficulty", "Unknown"),
                "mapper": bm.get("metadata", {}).get("mapper", "Unknown")
            }

        # Handle state changes
        if new_state != self.game_state:
            self._handle_state_change(self.game_state, new_state)
            self.game_state = new_state

        # Track data during gameplay
        if self.game_state == "play" and self.stats_tracker.is_playing:
            current_time = time.time() * 1000  # Convert to milliseconds
            if current_time - self.last_sample_time >= config.SAMPLE_INTERVAL:
                self.stats_tracker.add_data_point(
                    self.combo, self.accuracy, self.hp, self.misses,
                    gameplay.get("unstable_rate", 0.0)
                )
                self.last_sample_time = current_time

    def _handle_state_change(self, old_state, new_state):
        """Handle game state changes for tracking"""
        if old_state != "play" and new_state == "play":
            # Started playing
            self.stats_tracker.start_tracking(self.map_info)
            self.was_playing = True
        elif old_state == "play" and new_state in ["results", "menu"]:
            # Finished playing
            if self.was_playing:
                map_stats = self.stats_tracker.finish_map(
                    self.combo, self.accuracy, self.hp, self.misses
                )
                if map_stats:
                    # Show analysis window
                    self._show_analysis(map_stats)
                self.was_playing = False

    def _show_analysis(self, map_stats):
        """Show the analysis window in the main thread"""
        # This will be called from the analysis window
        self.latest_map_stats = map_stats

    def get_combo(self):
        return self.combo

    def get_max_combo(self):
        return self.max_combo

    def get_accuracy(self):
        return self.accuracy

    def get_misses(self):
        return self.misses

    def get_hp(self):
        return self.hp

    def is_connected(self):
        return self.connected

    def get_game_state(self):
        return self.game_state

    def get_map_info(self):
        return self.map_info

    def get_latest_map_stats(self):
        """Get and clear the latest completed map stats"""
        if hasattr(self, 'latest_map_stats'):
            stats = self.latest_map_stats
            delattr(self, 'latest_map_stats')
            return stats
        return None