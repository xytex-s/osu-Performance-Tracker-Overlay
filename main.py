# main.py

from memory_reader import MemoryReader
from overlay import Overlay
from input_handler import start_hotkey_listener

def main():
    memory_reader = MemoryReader()
    overlay = Overlay(memory_reader)
    start_hotkey_listener(overlay.toggle_visibility)
    overlay.run()

if __name__ == "__main__":
    main()
