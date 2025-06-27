# overlay.py

import tkinter as tk
import config

class Overlay:
    def __init__(self, memory_reader):
        self.memory_reader = memory_reader
        self.visible = True

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")


        self.root.geometry(f"400x120+{self.root.winfo_screenwidth() - 410}+50")

        self.combo_label = tk.Label(self.root, text="Combo: 0", fg="white", bg="black",
                                    font=("Consolas", 20, "bold"), width=22, anchor="w")
        self.combo_label.pack(padx=10, pady=(10, 0))

        self.acc_label = tk.Label(self.root, text="Accuracy: 100.00%", fg="white", bg="black",
                                  font=("Consolas", 20), width=22, anchor="w")
        self.acc_label.pack(padx=10, pady=(5, 10))


    def update_display(self):
        combo = self.memory_reader.get_combo()
        acc = self.memory_reader.get_accuracy()

        self.combo_label.config(text=f"Combo: {combo}")
        self.acc_label.config(text=f"Accuracy: {acc:.2f}%")

        if self.visible:
            self.root.after(1000 // config.REFRESH_RATE, self.update_display)

    def toggle_visibility(self):
        if self.visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.visible = not self.visible

    def run(self):
        self.update_display()
        self.root.mainloop()



