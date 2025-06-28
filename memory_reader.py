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

        self._data_lock = threading.RLock()
        self._shutdown_event = threading.Event()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_with_retry())

    async def connect_with_retry(self):
        while not self._shutdown_event.is_set():
            try:
                await self.connect()
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in {config.RECONNECT_DELAY} seconds...")
                self.connected = False
                await asyncio.sleep(config.RECONNECT_DELAY)

    async def connect(self):
        try:
            async with websockets.connect(
                    config.WEBSOCKET_URI,
                    ping_interval=20,
                    ping_timeout=10
            ) as websocket:
                print("Connected to Tosu!")
                self.connected = True

                while not self._shutdown_event.is_set():
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        self.update_data(data)
                    except asyncio.TimeoutError:
                        # Send ping to check connection
                        await websocket.ping()
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed by server")
                        break
                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON received: {e}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error in connect: {e}")
                        break

        except ConnectionRefusedError:
            print("Tosu is not running or not accessible")
            raise
        except Exception as e:
            print(f"Websocket error: {e}")
            self.connected = False
            raise

    def update_data(self, data):
        """Update data with better error handling and data validation"""
        try:
            with self._data_lock:
                # Validate that data is a dictionary
                if not isinstance(data, dict):
                    print(f"⚠️ Invalid data type received: {type(data)}")
                    return

                # Extract gameplay data safely
                gameplay = data.get("gameplay", {})
                if not isinstance(gameplay, dict):
                    gameplay = {}

                menu = data.get("menu", {})
                if not isinstance(menu, dict):
                    menu = {}

                state = menu.get("state", {})
                if not isinstance(state, dict):
                    state = {}

                # Update game stats with validation
                combo_data = gameplay.get("combo", {})
                if isinstance(combo_data, dict):
                    self.combo = combo_data.get("current", 0) or 0
                    self.max_combo = combo_data.get("max", 0) or 0
                else:
                    self.combo = combo_data if isinstance(combo_data, int) else 0

                self.accuracy = gameplay.get("accuracy", 100.0) or 100.0

                hp_data = gameplay.get("hp", {})
                if isinstance(hp_data, dict):
                    self.hp = hp_data.get("smooth", 1.0) or 1.0
                else:
                    self.hp = hp_data if isinstance(hp_data, (int, float)) else 1.0

                hits_data = gameplay.get("hits", {})
                if isinstance(hits_data, dict):
                    self.misses = hits_data.get("0", 0) or 0
                else:
                    self.misses = 0

                # Get game state
                new_state = state.get("name", "menu") or "menu"

                # Handle map info
                if "bm" in menu and isinstance(menu["bm"], dict):
                    bm = menu["bm"]
                    metadata = bm.get("metadata", {})

                    if isinstance(metadata, dict):
                        self.map_info = {
                            "title": metadata.get("title", "Unknown") or "Unknown",
                            "artist": metadata.get("artist", "Unknown") or "Unknown",
                            "difficulty": metadata.get("difficulty", "Unknown") or "Unknown",
                            "mapper": metadata.get("mapper", "Unknown") or "Unknown"
                        }
                    else:
                        print(f"⚠️ Invalid metadata type: {type(metadata)}")
                        self.map_info = {
                            "title": "Unknown",
                            "artist": "Unknown",
                            "difficulty": "Unknown",
                            "mapper": "Unknown"
                        }

                # Handle state changes
                if new_state != self.game_state:
                    print(f"State change: {self.game_state} -> {new_state}")
                    self._handle_state_change(self.game_state, new_state)
                    self.game_state = new_state

                # Sample data during play
                if self.game_state == "play" and self.stats_tracker.is_playing:
                    current_time = time.time() * 1000
                    if current_time - self.last_sample_time >= config.SAMPLE_INTERVAL:
                        unstable_rate = gameplay.get("unstable_rate", 0.0) or 0.0
                        self.stats_tracker.add_data_point(
                            self.combo, self.accuracy, self.hp, self.misses, unstable_rate
                        )
                        self.last_sample_time = current_time

        except Exception as e:
            print(f"Error in update_data: {e}")
            import traceback
            traceback.print_exc()

    def _handle_state_change(self, old_state, new_state):
        """Handle game state changes for tracking"""
        try:
            if old_state != "play" and new_state == "play":
                # Started playing
                print(f"Started playing: {self.map_info}")
                self.stats_tracker.start_tracking(self.map_info)
                self.was_playing = True
            elif old_state == "play" and new_state in ["results", "menu"]:
                # Finished playing
                if self.was_playing:
                    print("Finished playing, calculating stats...")
                    map_stats = self.stats_tracker.finish_map(
                        self.combo, self.accuracy, self.hp, self.misses
                    )
                    if map_stats:
                        print(f"Map stats generated for: {map_stats.map_name}")
                        self.latest_map_stats = map_stats
                    self.was_playing = False
        except Exception as e:
            print(f"Error in state change handling: {e}")

    def get_combo(self):
        with self._data_lock:
            return self.combo

    def get_max_combo(self):
        with self._data_lock:
            return self.max_combo

    def get_accuracy(self):
        with self._data_lock:
            return self.accuracy

    def get_misses(self):
        with self._data_lock:
            return self.misses

    def get_hp(self):
        with self._data_lock:
            return self.hp

    def is_connected(self):
        return self.connected

    def get_game_state(self):
        with self._data_lock:
            return self.game_state

    def get_map_info(self):
        with self._data_lock:
            return self.map_info.copy()

    def shutdown(self):
        """Graceful shutdown"""
        print("Shutting down memory reader...")
        self._shutdown_event.set()
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    def get_latest_map_stats(self):
        """Get and clear the latest completed map stats"""
        if hasattr(self, 'latest_map_stats'):
            stats = self.latest_map_stats
            delattr(self, 'latest_map_stats')
            return stats
        return None