# overlay.py
import customtkinter as ctk
import config
from analysis_window import AnalysisWindow

class Overlay:
    def __init__(self, memory_reader):
        self.memory_reader = memory_reader
        self.visible = True

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("osu! Performance Tracker")
        self.root.geometry("500x450+300+300")  # Bigger for new info
        self.root.resizable(True, True)
        self.root.minsize(350, 300)
        self.root.attributes("-topmost", True)

        # Add protocol handler for clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Connection status
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Status: Connecting...",
            font=("Segoe UI", 14),
            text_color="orange"
        )
        self.status_label.pack(anchor="w", pady=2)

        # Game state
        self.state_label = ctk.CTkLabel(
            self.frame,
            text="State: Menu",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.state_label.pack(anchor="w", pady=2)

        # Map info
        self.map_label = ctk.CTkLabel(
            self.frame,
            text="No map selected",
            font=("Segoe UI", 14),
            text_color="lightblue"
        )
        self.map_label.pack(anchor="w", pady=5)

        # Game stats
        self.combo_label = ctk.CTkLabel(self.frame, text="Combo: 0", font=("Segoe UI", 18))
        self.combo_label.pack(anchor="w", pady=5)

        self.max_combo_label = ctk.CTkLabel(self.frame, text="Max Combo: 0", font=("Segoe UI", 18))
        self.max_combo_label.pack(anchor="w", pady=5)

        self.acc_label = ctk.CTkLabel(self.frame, text="Accuracy: 0.00%", font=("Segoe UI", 18))
        self.acc_label.pack(anchor="w", pady=5)

        self.miss_label = ctk.CTkLabel(self.frame, text="Misses: 0", font=("Segoe UI", 18))
        self.miss_label.pack(anchor="w", pady=5)

        self.hp_label = ctk.CTkLabel(self.frame, text="HP: 1.00", font=("Segoe UI", 18))
        self.hp_label.pack(anchor="w", pady=5)

        # Analysis button
        self.analysis_button = ctk.CTkButton(
            self.frame,
            text="Show Last Analysis",
            command=self.show_last_analysis,
            state="disabled"
        )
        self.analysis_button.pack(pady=10)

        # Instructions
        self.help_label = ctk.CTkLabel(
            self.frame,
            text=f"Press {config.HOTKEY.upper()} to toggle visibility",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.help_label.pack(anchor="w", pady=(10, 0))

    def update_display(self):
        # Update connection status
        if self.memory_reader.is_connected():
            self.status_label.configure(text="Status: Connected", text_color="green")
        else:
            self.status_label.configure(text="Status: Disconnected", text_color="red")

        # Update game state
        state = self.memory_reader.get_game_state()
        state_color = {
            "menu": "gray",
            "play": "green",
            "results": "blue"
        }.get(state, "gray")
        self.state_label.configure(text=f"State: {state.title()}", text_color=state_color)

        # Update map info
        map_info = self.memory_reader.get_map_info()
        if map_info.get("title") != "Unknown":
            map_text = f"{map_info['title']} - {map_info['difficulty']}"
            self.map_label.configure(text=map_text)
        else:
            self.map_label.configure(text="No map selected")

        # Update game data
        self.combo_label.configure(text=f"Combo: {self.memory_reader.get_combo()}")
        self.max_combo_label.configure(text=f"Max Combo: {self.memory_reader.get_max_combo()}")
        self.acc_label.configure(text=f"Accuracy: {self.memory_reader.get_accuracy():.2f}%")
        self.miss_label.configure(text=f"Misses: {self.memory_reader.get_misses()}")
        self.hp_label.configure(text=f"HP: {self.memory_reader.get_hp():.2f}")

        # Check for new analysis
        latest_stats = self.memory_reader.get_latest_map_stats()
        if latest_stats:
            self.show_analysis_window(latest_stats)
            self.analysis_button.configure(state="normal")
            self.last_analysis = latest_stats

        # Schedule next update
        self.root.after(1000 // config.REFRESH_RATE, self.update_display)

    def show_analysis_window(self, map_stats):
        """Show the analysis window for completed map"""
        try:
            AnalysisWindow(map_stats)
        except Exception as e:
            print(f"Error showing analysis: {e}")

    def show_last_analysis(self):
        """Show the last completed analysis"""
        if hasattr(self, 'last_analysis'):
            self.show_analysis_window(self.last_analysis)

    def toggle_visibility(self):
        if self.visible:
            self.root.withdraw()
            self.visible = False
        else:
            self.root.deiconify()
            self.visible = True

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.update_display()
        self.root.mainloop()