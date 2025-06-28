import time
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import config

MAX_DATA_POINTS = 10000  # Limit to prevent memory issues


@dataclass
class DataPoint:
    timestamp: float
    combo: int
    accuracy: float
    hp: float
    misses: int
    unstable_rate: float = 0.0


@dataclass
class MapStats:
    start_time: float
    end_time: float
    map_name: str
    artist: str
    difficulty: str
    max_combo: int
    final_accuracy: float
    total_misses: int
    final_hp: float
    play_duration: float
    data_points: List[DataPoint]

    # Calculated stats
    avg_accuracy: float = 0.0
    accuracy_variance: float = 0.0
    hp_drops: int = 0
    combo_breaks: int = 0
    peak_combo: int = 0
    consistency_score: float = 0.0


class StatsTracker:
    def __init__(self):
        self.is_playing = False
        self.current_session: List[DataPoint] = []
        self.last_combo = 0
        self.last_miss_count = 0
        self.session_start_time = None
        self.map_info = {}
        self.completed_maps: List[MapStats] = []

    def start_tracking(self, map_info: Dict[str, Any]):
        """Start tracking a new map"""
        self.is_playing = True
        self.current_session = []
        self.session_start_time = time.time()
        self.last_combo = 0
        self.last_miss_count = 0
        self.map_info = map_info
        print(f"Started tracking: {map_info.get('title', 'Unknown')} - {map_info.get('difficulty', 'Unknown')}")

    # In stats_tracker.py - Add data validation
    def add_data_point(self, combo: int, accuracy: float, hp: float, misses: int, unstable_rate: float = 0.0):
        """Add a data point with validation"""
        if not self.is_playing:
            return

        self.current_session.append(data_point)

        # Limit data points to prevent memory issues
        if len(self.current_session) > MAX_DATA_POINTS:
            # Keep every nth point to maintain timeline
            step = len(self.current_session) // (MAX_DATA_POINTS // 2)
            self.current_session = self.current_session[::step]

        # Validate inputs
        combo = max(0, int(combo)) if combo is not None else 0
        accuracy = max(0.0, min(100.0, float(accuracy))) if accuracy is not None else 0.0
        hp = max(0.0, min(1.0, float(hp))) if hp is not None else 0.0
        misses = max(0, int(misses)) if misses is not None else 0
        unstable_rate = max(0.0, float(unstable_rate)) if unstable_rate is not None else 0.0

        data_point = DataPoint(
            timestamp=time.time() - self.session_start_time,
            combo=combo,
            accuracy=accuracy,
            hp=hp,
            misses=misses,
            unstable_rate=unstable_rate
        )
        self.current_session.append(data_point)

    def finish_map(self, final_combo: int, final_accuracy: float, final_hp: float, total_misses: int):
        """Finish tracking and calculate statistics"""
        if not self.is_playing or not self.current_session:
            return None

        end_time = time.time()
        play_duration = end_time - self.session_start_time

        # Only process if play was long enough
        if play_duration < config.MIN_PLAY_DURATION:
            self.is_playing = False
            return None

        map_stats = MapStats(
            start_time=self.session_start_time,
            end_time=end_time,
            map_name=self.map_info.get('title', 'Unknown'),
            artist=self.map_info.get('artist', 'Unknown'),
            difficulty=self.map_info.get('difficulty', 'Unknown'),
            max_combo=max(dp.combo for dp in self.current_session) if self.current_session else 0,
            final_accuracy=final_accuracy,
            total_misses=total_misses,
            final_hp=final_hp,
            play_duration=play_duration,
            data_points=self.current_session.copy()
        )

        # Calculate advanced statistics
        self._calculate_advanced_stats(map_stats)

        self.completed_maps.append(map_stats)
        self.is_playing = False

        # Save to file
        self._save_map_stats(map_stats)

        return map_stats

    def _calculate_advanced_stats(self, map_stats: MapStats):
        """Calculate comprehensive statistics"""
        if not map_stats.data_points:
            return

        # Average accuracy
        accuracies = [dp.accuracy for dp in map_stats.data_points]
        map_stats.avg_accuracy = sum(accuracies) / len(accuracies)

        # Accuracy variance (consistency)
        variance = sum((acc - map_stats.avg_accuracy) ** 2 for acc in accuracies) / len(accuracies)
        map_stats.accuracy_variance = variance

        # Count combo breaks and HP drops
        last_combo = 0
        last_hp = 1.0

        for dp in map_stats.data_points:
            if dp.combo < last_combo and last_combo > 20:  # Combo break (ignore small combos)
                map_stats.combo_breaks += 1
            if dp.hp < last_hp - 0.1:  # Significant HP drop
                map_stats.hp_drops += 1

            last_combo = dp.combo
            last_hp = dp.hp

        # Peak combo
        map_stats.peak_combo = max(dp.combo for dp in map_stats.data_points)

        # Consistency score (lower variance = higher consistency)
        map_stats.consistency_score = max(0, 100 - (variance * 10))

        # Additional metrics
        map_stats.accuracy_trend = self._calculate_accuracy_trend(map_stats.data_points)
        map_stats.stamina_score = self._calculate_stamina_score(map_stats.data_points)
        map_stats.reaction_time_avg = self._calculate_avg_reaction_time(map_stats.data_points)
        map_stats.difficulty_spikes = self._detect_difficulty_spikes(map_stats.data_points)

    def _save_map_stats(self, map_stats: MapStats):
        """Save map statistics to JSON file"""
        timestamp = datetime.fromtimestamp(map_stats.start_time).strftime("%Y%m%d_%H%M%S")
        filename = f"stats_{timestamp}_{map_stats.map_name.replace(' ', '_')}.json"

        #def _calculate_accuracy_trend(self, data_points):
            """Calculate if accuracy is improving, declining, or stable"""
            if len(data_points) < 2:
                return "insufficient_data"

            # Linear regression on accuracy over time
            timestamps = [dp.timestamp for dp in data_points]
            accuracies = [dp.accuracy for dp in data_points]

            # Simple linear regression
            n = len(data_points)
            sum_x = sum(timestamps)
            sum_y = sum(accuracies)
            sum_xy = sum(t * a for t, a in zip(timestamps, accuracies))
            sum_x2 = sum(t * t for t in timestamps)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            if slope > 0.1:
                return "improving"
            elif slope < -0.1:
                return "declining"
            else:
                return "stable"

        # Convert to serializable format
        data = asdict(map_stats)

        try:
            os.makedirs("play_stats", exist_ok=True)
            filepath = os.path.join("play_stats", filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Stats saved to {filepath}")
        except Exception as e:
            print(f"Failed to save stats: {e}")