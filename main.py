# main.py
from memory_reader import MemoryReader
from overlay import Overlay
from input_handler import start_hotkey_listener
import config
import signal
import sys


def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)


def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting osu! Performance Tracker...")
    print(f"Press {config.HOTKEY.upper()} to toggle overlay visibility")
    print("Analysis windows will automatically appear after completing maps!")

    memory_reader = MemoryReader()
    overlay = Overlay(memory_reader)

    # Start hotkey listener
    listener = start_hotkey_listener(overlay.toggle_visibility)

    try:
        overlay.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if listener:
            listener.stop()


if __name__ == "__main__":
    main()