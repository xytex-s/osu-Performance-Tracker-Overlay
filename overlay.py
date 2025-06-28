# overlay.py
import customtkinter as ctk
import config
from analysis_window import AnalysisWindow
import threading
import time


class Overlay:
    def __init__(self, memory_reader):
        self.memory_reader = memory_reader
        self.visible = True
        self.last_update_data = {}
        self.update_counter = 0
        self.last_map_stats = None
        self.last_update_time = 0

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("osu! Performance Tracker")
        self.root.geometry("500x450+300+300")
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
            text_color="lightblue",
            wraplength=450
        )
        self.map_label.pack(anchor="w", pady=5, fill="x")

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

        # Debug info
        self.debug_label = ctk.CTkLabel(
            self.frame,
            text="Debug: Waiting for data...",
            font=("Segoe UI", 10),
            text_color="gray"
        )
        self.debug_label.pack(anchor="w", pady=2)

        # Instructions
        self.help_label = ctk.CTkLabel(
            self.frame,
            text=f"Press {config.HOTKEY.upper()} to toggle visibility",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.help_label.pack(anchor="w", pady=(10, 0))

    def update_display(self):
        current_time = time.time()

        # Check for completed maps first
        try:
            latest_stats = self.memory_reader.get_latest_map_stats()
            if latest_stats:
                self.last_map_stats = latest_stats
                self.analysis_button.configure(state="normal")
                print(f"New map stats available: {latest_stats.map_name}")
                # Show analysis window automatically
                if config._config.auto_show_analysis:
                    self.show_analysis_window(latest_stats)
        except Exception as e:
            print(f"Error checking for map stats: {e}")

        # Update UI at reduced frequency when not playing
        should_update = False
        game_state = self.memory_reader.get_game_state()

        if game_state == "play":
            # Update more frequently during play
            if current_time - self.last_update_time >= 1.0 / config.REFRESH_RATE:
                should_update = True
        else:
            # Update less frequently in menu/results
            if current_time - self.last_update_time >= 0.5:  # 2 FPS
                should_update = True

        if should_update:
            self.last_update_time = current_time

            try:
                # Get current data
                current_data = {
                    'combo': self.memory_reader.get_combo(),
                    'accuracy': self.memory_reader.get_accuracy(),
                    'hp': self.memory_reader.get_hp(),
                    'misses': self.memory_reader.get_misses(),
                    'max_combo': self.memory_reader.get_max_combo(),
                    'connected': self.memory_reader.is_connected(),
                    'state': game_state,
                    'map_info': self.memory_reader.get_map_info()
                }

                # Only update UI if data has actually changed
                if current_data != self.last_update_data:
                    self._update_labels(current_data)
                    self.last_update_data = current_data

            except Exception as e:
                print(f"Error updating display: {e}")
                self.debug_label.configure(text=f"Debug: Error - {str(e)[:50]}")

        # Schedule next update
        update_interval = 50 if game_state == "play" else 200  # 20 FPS or 5 FPS
        self.root.after(update_interval, self.update_display)

    def show_analysis_window(self, map_stats):
        """Show the analysis window for completed map"""
        try:
            def create_analysis():
                try:
                    AnalysisWindow(map_stats)
                    print(f"Analysis window created for: {map_stats.map_name}")
                except Exception as e:
                    print(f"Error creating analysis window: {e}")
                    import traceback
                    traceback.print_exc()

            if threading.current_thread() == threading.main_thread():
                create_analysis()
            else:
                self.root.after(0, create_analysis)
        except Exception as e:
            print(f"Error showing analysis: {e}")

    def show_last_analysis(self):
        """Show the last completed analysis"""
        if self.last_map_stats:
            self.show_analysis_window(self.last_map_stats)
        else:
            print("No analysis data available")

    def toggle_visibility(self):
        if self.visible:
            self.root.withdraw()
            self.visible = False
            print("Overlay hidden")
        else:
            self.root.deiconify()
            self.visible = True
            print("Overlay shown")

    def on_closing(self):
        print("Overlay closing...")
        self.memory_reader.shutdown()
        self.root.quit()
        self.root.destroy()

    def run(self):
        print("Starting overlay...")
        self.update_display()
        self.root.mainloop()

    def _format_map_info(self, map_info):
        """Format map information for display"""
        if not map_info or not isinstance(map_info, dict):
            return "No map selected"

        title = map_info.get('title', 'Unknown')
        artist = map_info.get('artist', 'Unknown')
        difficulty = map_info.get('difficulty', 'Unknown')

        if title == 'Unknown' and artist == 'Unknown':
            return "No map selected"

        return f"{title} - {artist} [{difficulty}]"

    def _update_labels(self, current_data):
        """Update UI labels with current data"""
        try:
            self.combo_label.configure(text=f"Combo: {current_data['combo']}")
            self.max_combo_label.configure(text=f"Max Combo: {current_data['max_combo']}")
            self.acc_label.configure(text=f"Accuracy: {current_data['accuracy']:.2f}%")
            self.miss_label.configure(text=f"Misses: {current_data['misses']}")
            self.hp_label.configure(text=f"HP: {current_data['hp']:.2f}")
            self.state_label.configure(text=f"State: {current_data['state']}")

            if current_data['connected']:
                self.status_label.configure(text="Status: Connected", text_color="green")
                map_text = self._format_map_info(current_data['map_info'])
                self.map_label.configure(text=map_text)
            else:
                self.status_label.configure(text="Status: Disconnected", text_color="red")
                self.map_label.configure(text="No map selected")
                self.analysis_button.configure(state="disabled")

            # Update debug info
            self.debug_label.configure(
                text=f"Debug: Updates #{self.update_counter}, State: {current_data['state']}"
            )
            self.update_counter += 1

        except Exception as e:
            print(f"Error updating labels: {e}")
            self.debug_label.configure(text=f"Debug: Label update error - {str(e)[:30]}")