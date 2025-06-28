# config.py
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

# Legacy constants for backwards compatibility
HOTKEY = 'f8'
RECONNECT_DELAY = 5
WEBSOCKET_URI = "ws://localhost:24050/ws"
SAMPLE_INTERVAL = 100
REFRESH_RATE = 30  # Reduced from 60 to improve performance
MIN_PLAY_DURATION = 10

@dataclass
class Config:
    refresh_rate: int = 30  # Reduced default
    hotkey: str = "f8"
    websocket_uri: str = "ws://localhost:24050/ws"
    reconnect_delay: int = 5
    sample_interval: int = 100
    min_play_duration: int = 10
    max_data_points: int = 5000  # Reduced from 10000
    auto_show_analysis: bool = True
    save_stats: bool = True
    stats_directory: str = "play_stats"
    debug_mode: bool = False  # New debug option


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
            print(f"Config loaded from {config_path}")
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")

    # Update legacy constants for backwards compatibility
    global HOTKEY, RECONNECT_DELAY, WEBSOCKET_URI, SAMPLE_INTERVAL, REFRESH_RATE, MIN_PLAY_DURATION
    HOTKEY = config.hotkey
    RECONNECT_DELAY = config.reconnect_delay
    WEBSOCKET_URI = config.websocket_uri
    SAMPLE_INTERVAL = config.sample_interval
    REFRESH_RATE = config.refresh_rate
    MIN_PLAY_DURATION = config.min_play_duration

    return config


def save_config(config: Config, config_path: str = "config.json"):
    """Save configuration to file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(asdict(config), f, indent=2)
        print(f"Config saved to {config_path}")
    except Exception as e:
        print(f"Error saving config: {e}")


def create_default_config():
    """Create a default config file"""
    config = Config()
    save_config(config)
    return config


# Initialize config on import
try:
    _config = load_config()
except Exception as e:
    print(f"Failed to load config, creating default: {e}")
    _config = create_default_config()