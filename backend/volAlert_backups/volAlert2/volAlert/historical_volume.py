
import json
from collections import defaultdict
import statistics

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

        for symbol, volumes in grouped.items():
            if not volumes:
                continue

            metrics[symbol] = {
                "prev_day": volumes[-1],
                "weekly_avg": sum(volumes[-5:]) // min(5, len(volumes)),
                "monthly_avg": sum(volumes[-20:]) // min(20, len(volumes)),
                "window_mean": statistics.mean(volumes),
                "window_std": statistics.stdev(volumes) if len(volumes) > 1 else 0,
                "window_p90": sorted(volumes)[int(0.9 * len(volumes))],
                "historical_series": [
                    {"date": row["date"], "volume": row["volume"]}
                    for row in data if row["symbol"] == symbol
                ]
            }

        return metrics
