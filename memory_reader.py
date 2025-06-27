# memory_reader.py

import random
import time

class MemoryReader:
    def __init__(self):
        self.combo = 0
        self.accuracy = 100.0
        self.start_time = time.time()

    def get_combo(self):
        # Simulate combo building up over time
        elapsed = int(time.time() - self.start_time)
        self.combo = (elapsed * 25) % 1000  # loop after 1000
        return self.combo

    def get_accuracy(self):
        # Simulate slight accuracy fluctuation
        base_acc = 98.5
        return base_acc + random.uniform(-1.0, 0.3)
