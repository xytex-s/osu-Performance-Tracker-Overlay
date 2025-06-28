import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from stats_tracker import MapStats
import tkinter as tk


class AnalysisWindow:
    def __init__(self, map_stats: MapStats):
        self.map_stats = map_stats
        self.setup_window()
        self.create_analysis()

    def setup_window(self):
        self.window = ctk.CTkToplevel()
        self.window.title(f"Analysis: {self.map_stats.map_name}")
        self.window.geometry("1200x800")
        self.window.attributes("-topmost", True)

        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.window)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_analysis(self):
        # Title section
        title_frame = ctk.CTkFrame(self.scroll_frame)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text=f"{self.map_stats.map_name} - {self.map_stats.difficulty}",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(pady=10)

        artist_label = ctk.CTkLabel(title_frame, text=f"by {self.map_stats.artist}", font=("Segoe UI", 16))
        artist_label.pack()

        # Summary statistics
        self.create_summary_stats()

        # Performance graphs
        self.create_performance_graphs()

        # Detailed analysis
        self.create_detailed_analysis()

    def create_summary_stats(self):
        stats_frame = ctk.CTkFrame(self.scroll_frame)
        stats_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(stats_frame, text="Performance Summary", font=("Segoe UI", 18, "bold")).pack(pady=(10, 5))

        # Create grid of stats
        grid_frame = ctk.CTkFrame(stats_frame)
        grid_frame.pack(padx=20, pady=(0, 20), fill="x")

        stats = [
            ("Final Accuracy", f"{self.map_stats.final_accuracy:.2f}%"),
            ("Average Accuracy", f"{self.map_stats.avg_accuracy:.2f}%"),
            ("Max Combo", str(self.map_stats.max_combo)),
            ("Total Misses", str(self.map_stats.total_misses)),
            ("Play Duration", f"{self.map_stats.play_duration:.1f}s"),
            ("Combo Breaks", str(self.map_stats.combo_breaks)),
            ("HP Drops", str(self.map_stats.hp_drops)),
            ("Consistency Score", f"{self.map_stats.consistency_score:.1f}/100")
        ]

        for i, (label, value) in enumerate(stats):
            row = i // 4
            col = i % 4

            stat_frame = ctk.CTkFrame(grid_frame)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            grid_frame.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(stat_frame, text=label, font=("Segoe UI", 12)).pack(pady=(5, 0))
            ctk.CTkLabel(stat_frame, text=value, font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))

    def create_performance_graphs(self):
        graph_frame = ctk.CTkFrame(self.scroll_frame)
        graph_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(graph_frame, text="Performance Graphs", font=("Segoe UI", 18, "bold")).pack(pady=(10, 5))

        # Create matplotlib figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor('#212121')

        # Extract data
        timestamps = [dp.timestamp for dp in self.map_stats.data_points]
        accuracies = [dp.accuracy for dp in self.map_stats.data_points]
        combos = [dp.combo for dp in self.map_stats.data_points]
        hps = [dp.hp for dp in self.map_stats.data_points]

        # Accuracy over time
        ax1.plot(timestamps, accuracies, color='#1f77b4', linewidth=2)
        ax1.set_title('Accuracy Over Time', color='white', fontsize=12)
        ax1.set_xlabel('Time (s)', color='white')
        ax1.set_ylabel('Accuracy (%)', color='white')
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='white')

        # Combo over time
        ax2.plot(timestamps, combos, color='#ff7f0e', linewidth=2)
        ax2.set_title('Combo Over Time', color='white', fontsize=12)
        ax2.set_xlabel('Time (s)', color='white')
        ax2.set_ylabel('Combo', color='white')
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='white')

        # HP over time
        ax3.plot(timestamps, hps, color='#2ca02c', linewidth=2)
        ax3.set_title('HP Over Time', color='white', fontsize=12)
        ax3.set_xlabel('Time (s)', color='white')
        ax3.set_ylabel('HP', color='white')
        ax3.grid(True, alpha=0.3)
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')

        # Accuracy distribution
        ax4.hist(accuracies, bins=20, color='#d62728', alpha=0.7, edgecolor='white')
        ax4.set_title('Accuracy Distribution', color='white', fontsize=12)
        ax4.set_xlabel('Accuracy (%)', color='white')
        ax4.set_ylabel('Frequency', color='white')
        ax4.set_facecolor('#2b2b2b')
        ax4.tick_params(colors='white')

        plt.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)

    def create_detailed_analysis(self):
        analysis_frame = ctk.CTkFrame(self.scroll_frame)
        analysis_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(analysis_frame, text="Detailed Analysis", font=("Segoe UI", 18, "bold")).pack(pady=(10, 5))

        # Performance insights
        insights = self.generate_insights()

        for insight in insights:
            insight_frame = ctk.CTkFrame(analysis_frame)
            insight_frame.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                insight_frame,
                text=f"• {insight}",
                font=("Segoe UI", 12),
                wraplength=1000,
                justify="left"
            ).pack(anchor="w", padx=10, pady=5)

    def generate_insights(self):
        """Generate performance insights based on statistics"""
        insights = []

        # Accuracy analysis
        if self.map_stats.final_accuracy >= 95:
            insights.append("Excellent accuracy! You maintained very high precision throughout the map.")
        elif self.map_stats.final_accuracy >= 90:
            insights.append("Good accuracy, but there's room for improvement in precision.")
        else:
            insights.append("Consider focusing on accuracy over speed in practice sessions.")

        # Consistency analysis
        if self.map_stats.consistency_score >= 80:
            insights.append("Very consistent performance with minimal accuracy fluctuation.")
        elif self.map_stats.consistency_score >= 60:
            insights.append("Moderate consistency. Try to maintain steady rhythm throughout maps.")
        else:
            insights.append("Accuracy was quite inconsistent. Focus on rhythm and timing practice.")

        # Combo analysis
        if self.map_stats.combo_breaks == 0:
            insights.append("Perfect combo! No combo breaks detected.")
        elif self.map_stats.combo_breaks <= 2:
            insights.append(f"Only {self.map_stats.combo_breaks} combo break(s). Great combo maintenance!")
        else:
            insights.append(
                f"{self.map_stats.combo_breaks} combo breaks. Work on maintaining focus throughout the map.")

        # HP analysis
        if self.map_stats.hp_drops <= 2:
            insights.append("Excellent HP management with minimal health drops.")
        else:
            insights.append(
                f"{self.map_stats.hp_drops} significant HP drops detected. Consider easier difficulties to build consistency.")

        return insights