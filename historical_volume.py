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

            if len(vols) < 5:
                continue

            metrics[symbol] = {
                # ---- Existing metrics (alerts depend on these) ----
                "prev_day": vols[-1],
                "weekly_avg": sum(vols[-5:]) // min(5, len(vols)),
                "monthly_avg": sum(vols[-20:]) // min(20, len(vols)),
                "window_mean": statistics.mean(vols),
                "window_std": statistics.stdev(vols) if len(vols) > 1 else 0,
                "window_p90": sorted(vols)[int(0.9 * len(vols))],

                # ---- 🔥 REQUIRED FOR CHART ----
                "historical_series": [
                    {
                        "time": r["date"],   # YYYY-MM-DD (REQUIRED)
                        "value": r["volume"]
                    }
                    for r in rows
                ]
            }

        return metrics