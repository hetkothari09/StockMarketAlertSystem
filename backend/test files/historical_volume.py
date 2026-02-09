import csv
import json
import statistics
from collections import defaultdict

INPUT_FILE = "historical_volumes.json"
OUTPUT_FILE = "historical_metrics.json"

def build_historical_metrics():
    with open(INPUT_FILE, "r") as f:
        rows = json.load(f)

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["symbol"]].append(r["volume"])

    metrics = {}

    for symbol, vols in grouped.items():
        if len(vols) < 20:
            continue

        daily_mean = statistics.mean(vols[-20:])
        daily_std = max(statistics.pstdev(vols[-20:]), 1)

        metrics[symbol] = {
            "daily_mean": daily_mean,
            "daily_std": daily_std,
            "prev_day": vols[-1],
            "weekly_avg": statistics.mean(vols[-5:]),
            "monthly_avg": statistics.mean(vols[-20:])
        }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Generated historical metrics for {len(metrics)} symbols")

if __name__ == "__main__":
    build_historical_metrics()