import json
import statistics
from collections import defaultdict

class HistoricalVolumeLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        with open(self.filepath, "r") as f:
            data = json.load(f)

        grouped = defaultdict(list)

        for row in data:
            grouped[row["symbol"]].append(row["volume"])

        metrics = {}

        for symbol, vols in grouped.items():
            if len(vols) < 5:
                continue

            metrics[symbol] = {
                "prev_day": vols[-1],
                "weekly_avg": sum(vols[-5:]) // min(5, len(vols)),
                "monthly_avg": sum(vols[-20:]) // min(20, len(vols)),
                "window_mean": statistics.mean(vols),
                "window_std": statistics.stdev(vols) if len(vols) > 1 else 0,
                "window_p90": sorted(vols)[int(0.9 * len(vols))]
            }

        return metrics
