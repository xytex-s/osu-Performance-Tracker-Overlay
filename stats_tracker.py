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
    accuracy_trend: float = 0.0
    stamina_score: float = 0.0
    reaction_time_avg: float = 0.0
    difficulty_spikes: int = 0


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

    def add_data_point(self, combo: int, accuracy: float, hp: float, misses: int, unstable_rate: float = 0.0):
        """Add a data point with validation"""
        if not self.is_playing:
            return

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

        # Save to file if enabled
        if config._config.save_stats:
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

    def _calculate_accuracy_trend(self, data_points: List[DataPoint]) -> float:
        """Calculate if accuracy is improving or declining over time"""
        if len(data_points) < 2:
            return 0.0

        # Simple linear regression to find trend
        n = len(data_points)
        x_values = list(range(n))
        y_values = [dp.accuracy for dp in data_points]

        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _calculate_stamina_score(self, data_points: List[DataPoint]) -> float:
        """Calculate stamina based on accuracy decline over time"""
        if len(data_points) < 10:
            return 100.0

        # Compare first and last 25% of the play
        first_quarter = data_points[:len(data_points) // 4]
        last_quarter = data_points[len(data_points) * 3 // 4:]

        if not first_quarter or not last_quarter:
            return 100.0

        first_avg = sum(dp.accuracy for dp in first_quarter) / len(first_quarter)
        last_avg = sum(dp.accuracy for dp in last_quarter) / len(last_quarter)

        # Calculate stamina as percentage of accuracy maintained
        stamina = (last_avg / first_avg) * 100 if first_avg > 0 else 100.0
        return min(100.0, max(0.0, stamina))

    def _calculate_avg_reaction_time(self, data_points: List[DataPoint]) -> float:
        """Calculate average reaction time based on unstable rate"""
        if not data_points:
            return 0.0

        unstable_rates = [dp.unstable_rate for dp in data_points if dp.unstable_rate > 0]
        if not unstable_rates:
            return 0.0

        return sum(unstable_rates) / len(unstable_rates)

    def _detect_difficulty_spikes(self, data_points: List[DataPoint]) -> int:
        """Detect sections where accuracy drops significantly"""
        if len(data_points) < 5:
            return 0

        spikes = 0
        window_size = 5
        threshold = 5.0  # 5% accuracy drop

        for i in range(window_size, len(data_points) - window_size):
            before = data_points[i - window_size:i]
            after = data_points[i:i + window_size]

            before_avg = sum(dp.accuracy for dp in before) / len(before)
            after_avg = sum(dp.accuracy for dp in after) / len(after)

            if before_avg - after_avg > threshold:
                spikes += 1

        return spikes

    def _save_map_stats(self, map_stats: MapStats):
        """Save map statistics to JSON file"""
        try:
            # Create stats directory if it doesn't exist
            stats_dir = config._config.stats_directory
            if not os.path.exists(stats_dir):
                os.makedirs(stats_dir)

            timestamp = datetime.fromtimestamp(map_stats.start_time).strftime("%Y%m%d_%H%M%S")
            safe_map_name = "".join(c for c in map_stats.map_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{stats_dir}/stats_{timestamp}_{safe_map_name.replace(' ', '_')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(asdict(map_stats), f, indent=2, ensure_ascii=False)
            print(f"Map stats saved to {filename}")

        except Exception as e:
            print(f"Error saving map stats: {e}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.completed_maps:
            return {}

        total_maps = len(self.completed_maps)
        avg_accuracy = sum(stats.final_accuracy for stats in self.completed_maps) / total_maps
        total_playtime = sum(stats.play_duration for stats in self.completed_maps)

        return {
            "total_maps": total_maps,
            "avg_accuracy": avg_accuracy,
            "total_playtime": total_playtime,
            "best_accuracy": max(stats.final_accuracy for stats in self.completed_maps),
            "best_combo": max(stats.max_combo for stats in self.completed_maps)
        }