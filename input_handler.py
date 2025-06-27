# input_handler.py

from pynput import keyboard
import config

def start_hotkey_listener(toggle_callback):
    def on_press(key):
        try:
            if key.char == config.HOTKEY.lower():
                toggle_callback()
        except AttributeError:
            # Handle special keys like F1, F8, etc.
            if key == getattr(keyboard.Key, config.HOTKEY.lower(), None):
                toggle_callback()

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True  # So it closes when main program exits
    listener.start()
