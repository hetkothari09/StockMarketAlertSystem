import json
import statistics
from collections import defaultdict


class HistoricalVolumeLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        with open(self.filepath, "r") as f:
            raw = json.load(f)

        grouped = defaultdict(list)

        # Group by symbol
        for row in raw:
            grouped[row["symbol"]].append({
                "date": row["date"],
                "volume": row["volume"]
            })

        metrics = {}

        for symbol, rows in grouped.items():
            # Sort by date
            rows.sort(key=lambda x: x["date"])
            vols = [r["volume"] for r in rows]

            if len(vols) < 20:
                continue

            window_avg = sum(vols[-20:]) / 20
            p90 = sorted(vols)[int(0.9 * len(vols))]

            metrics[symbol] = {
                "window_mean": statistics.mean(vols[-20:]),
                "window_std": max(statistics.pstdev(vols[-20:]), 1),  # avoid zero
                "window_p90": p90,
                "prev_day": vols[-1],
                "last_date": rows[-1]["date"],  # Store the recency
                "weekly_avg": sum(vols[-5:]) / 5,
                "monthly_avg": sum(vols[-20:]) / 20,
                "historical_series": [
                    {"time": r["date"], "value": r["volume"]}
                    for r in rows
                ]
            }

        return metrics