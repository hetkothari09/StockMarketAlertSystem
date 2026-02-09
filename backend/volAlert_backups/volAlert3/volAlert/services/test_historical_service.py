from historical_volume_service import HistoricalVolumeService

DATA_FILE = "data/historical_volumes.json"
service = HistoricalVolumeService(DATA_FILE)

symbol = "INFY"
snapshot = service.get_volume_snapshot(symbol)

print("Snapshot:", snapshot)

assert snapshot["prev_day_volume"] is not None

# These depend on data availability
if snapshot["weekly_avg_volume"] is None:
    print("ℹ️ Weekly average not available yet (insufficient data)")

if snapshot["monthly_avg_volume"] is None:
    print("ℹ️ Monthly average not available yet (insufficient data)")

print("✅ HistoricalVolumeService basic test passed")
