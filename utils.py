# utils.py
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


def save_session_stats(combo, max_combo, accuracy, misses, hp):
    """Save current session stats to a JSON file"""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "combo": combo,
        "max_combo": max_combo,
        "accuracy": accuracy,
        "misses": misses,
        "hp": hp
    }

    filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Session stats saved to {filename}")
    except Exception as e:
        print(f"Failed to save stats: {e}")


def load_config(config_file="config.json"):
    """Load configuration from JSON file if it exists"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    return {}


def format_time(seconds):
    """Format seconds into MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def create_comparison_chart(map_stats_list):
    """Create a comparison chart for multiple map performances"""
    if not map_stats_list:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#212121')

    map_names = [f"{stats.map_name[:20]}..." if len(stats.map_name) > 20 else stats.map_name
                 for stats in map_stats_list]
    accuracies = [stats.final_accuracy for stats in map_stats_list]
    max_combos = [stats.max_combo for stats in map_stats_list]

    # Accuracy comparison
    bars1 = ax1.bar(range(len(map_names)), accuracies, color='#1f77b4', alpha=0.7)
    ax1.set_title('Accuracy Comparison', color='white', fontsize=14)
    ax1.set_xlabel('Maps', color='white')
    ax1.set_ylabel('Accuracy (%)', color='white')
    ax1.set_xticks(range(len(map_names)))
    ax1.set_xticklabels(map_names, rotation=45, ha='right', color='white')
    ax1.set_facecolor('#2b2b2b')
    ax1.tick_params(colors='white')
    ax1.grid(True, alpha=0.3)

    # Max combo comparison
    bars2 = ax2.bar(range(len(map_names)), max_combos, color='#ff7f0e', alpha=0.7)
    ax2.set_title('Max Combo Comparison', color='white', fontsize=14)
    ax2.set_xlabel('Maps', color='white')
    ax2.set_ylabel('Max Combo', color='white')
    ax2.set_xticks(range(len(map_names)))
    ax2.set_xticklabels(map_names, rotation=45, ha='right', color='white')
    ax2.set_facecolor('#2b2b2b')
    ax2.tick_params(colors='white')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def export_stats_csv(map_stats_list, filename="performance_export.csv"):
    """Export map statistics to CSV for external analysis"""
    import csv

    if not map_stats_list:
        print("No stats to export")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'map_name', 'artist', 'difficulty', 'final_accuracy',
                'avg_accuracy', 'max_combo', 'total_misses', 'play_duration',
                'combo_breaks', 'hp_drops', 'consistency_score', 'timestamp'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for stats in map_stats_list:
                writer.writerow({
                    'map_name': stats.map_name,
                    'artist': stats.artist,
                    'difficulty': stats.difficulty,
                    'final_accuracy': stats.final_accuracy,
                    'avg_accuracy': stats.avg_accuracy,
                    'max_combo': stats.max_combo,
                    'total_misses': stats.total_misses,
                    'play_duration': stats.play_duration,
                    'combo_breaks': stats.combo_breaks,
                    'hp_drops': stats.hp_drops,
                    'consistency_score': stats.consistency_score,
                    'timestamp': datetime.fromtimestamp(stats.start_time).isoformat()
                })

        print(f"Stats exported to {filename}")
    except Exception as e:
        print(f"Failed to export stats: {e}")