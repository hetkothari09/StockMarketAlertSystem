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

            # Changed: Include symbols with any data, but mark insufficient if <20 days
            # Changed: Include symbols with any data (even 1 day)
            if len(vols) < 1:  # Allow 1 day of data
                continue
            
            is_insufficient = len(vols) < 20
            
            if is_insufficient:
                # Limited metrics for insufficient data
                metrics[symbol] = {
                    "window_mean": statistics.mean(vols),
                    "window_std": max(statistics.pstdev(vols), 1),
                    "window_p90": sorted(vols)[int(0.9 * len(vols))],
                    "prev_day": vols[-1],
                    "last_date": rows[-1]["date"],
                    "weekly_avg": sum(vols[-min(5, len(vols)):]) / min(5, len(vols)),
                    "monthly_avg": sum(vols) / len(vols),
                    "data_status": "INSUFFICIENT",
                    "available_days": len(vols),
                    "historical_series": [
                        {"time": r["date"], "value": r["volume"]}
                        for r in rows
                    ]
                }
            else:
                # Full metrics for sufficient data
                window_avg = sum(vols[-20:]) / 20
                p90 = sorted(vols)[int(0.9 * len(vols))]

                metrics[symbol] = {
                    "window_mean": statistics.mean(vols[-20:]),
                    "window_std": max(statistics.pstdev(vols[-20:]), 1),  # avoid zero
                    "window_p90": p90,
                    "prev_day": vols[-1],
                    "last_date": rows[-1]["date"],
                    "weekly_avg": sum(vols[-5:]) / 5,
                    "monthly_avg": sum(vols[-20:]) / 20,
                    "data_status": "OK",
                    "available_days": len(vols),
                    "historical_series": [
                        {"time": r["date"], "value": r["volume"]}
                        for r in rows
                    ]
                }

        return metrics