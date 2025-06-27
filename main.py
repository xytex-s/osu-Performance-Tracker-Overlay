# main.py

from memory_reader import MemoryReader
from overlay import Overlay
from input_handler import start_hotkey_listener

def main():
    # Initialize the osu! memory reader
    memory_reader = MemoryReader()

    # Initialize the overlay UI, passing the memory reader to it
    overlay = Overlay(memory_reader)

    # Start the hotkey listener for toggling overlay visibility
    start_hotkey_listener(overlay.toggle_visibility)

    # Start the overlay (main loop)
    overlay.run()

if __name__ == "__main__":
    main()
