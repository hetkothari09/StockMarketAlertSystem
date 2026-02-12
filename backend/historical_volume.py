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

            # Include symbols with any data (even 1 day)
            if len(vols) < 1:
                continue
            
            # Use ALL available data for calculations (up to 1 year)
            metrics[symbol] = {
                "window_mean": statistics.mean(vols),
                "window_std": max(statistics.pstdev(vols), 1),  # avoid zero
                "window_p90": sorted(vols)[int(0.9 * len(vols))],
                "prev_day": vols[-1],
                "last_date": rows[-1]["date"],
                "weekly_avg": sum(vols[-5:]) / min(5, len(vols)),
                "monthly_avg": sum(vols) / len(vols), # Now represents total average
                "data_status": "OK" if len(vols) >= 20 else "INSUFFICIENT",
                "available_days": len(vols),
                "historical_series": [
                    {"time": r["date"], "value": r["volume"]}
                    for r in rows
                ]
            }

        return metrics