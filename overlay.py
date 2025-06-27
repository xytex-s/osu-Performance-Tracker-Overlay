# overlay.py

import tkinter as tk
import config

class Overlay:
    def __init__(self, memory_reader):
        self.memory_reader = memory_reader
        self.visible = True

        # Create transparent, always-on-top tkinter window
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # No window borders
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        # Set window size and position (top right corner)
        self.root.geometry(f"250x100+{self.root.winfo_screenwidth() - 260}+50")

        # Combo label
        self.combo_label = tk.Label(self.root, text="Combo: 0", fg="white", bg="black", font=("Segoe UI", 20, "bold"))
        self.combo_label.pack()

        # Accuracy label
        self.acc_label = tk.Label(self.root, text="Accuracy: 0.00%", fg="white", bg="black", font=("Segoe UI", 20))
        self.acc_label.pack()

    def update_display(self):
        combo = self.memory_reader.get_combo()
        accuracy = self.memory_reader.get_accuracy()

        self.combo_label.config(text=f"Combo: {combo}")
        self.acc_label.config(text=f"Accuracy: {accuracy:.2f}%")

        if self.visible:
            self.root.after(1000 // config.REFRESH_RATE, self.update_display)

    def toggle_visibility(self):
        if self.visible:
            self.root.withdraw()  # Hide
        else:
            self.root.deiconify()  # Show
        self.visible = not self.visible

    def run(self):
        self.update_display()
        self.root.mainloop()
