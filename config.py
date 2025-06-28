# config.py
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

HOTKEY = 'f8'
RECONNECT_DELAY = 5  # Number of seconds to wait before retrying connection
WEBSOCKET_URI = "ws://localhost:24050/ws" # Default websocket URI

@dataclass
class Config:
    refresh_rate: int = 60
    hotkey: str = "f8"
    websocket_uri: str = "ws://localhost:24050/ws"
    reconnect_delay: int = 5
    sample_interval: int = 100
    min_play_duration: int = 10
    max_data_points: int = 10000
    auto_show_analysis: bool = True
    save_stats: bool = True
    stats_directory: str = "play_stats"


def load_config(config_path: str = "config.json") -> Config:
    """Load configuration from file with defaults"""
    config = Config()

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")

    return config


def save_config(config: Config, config_path: str = "config.json"):
    """Save configuration to file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")