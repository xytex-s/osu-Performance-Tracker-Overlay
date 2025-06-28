# input_handler.py
from pynput import keyboard
import config

def start_hotkey_listener(toggle_callback):
    def on_press(key):
        try:
            # Handle function keys properly
            if hasattr(key, 'name') and key.name.lower() == config.HOTKEY.lower():
                toggle_callback()
            # Handle character keys
            elif hasattr(key, 'char') and key.char and key.char.lower() == config.HOTKEY.lower():
                toggle_callback()
        except AttributeError:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener