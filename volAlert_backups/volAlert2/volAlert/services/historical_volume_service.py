import json
import os
from collections import defaultdict
from statistics import mean

class HistoricalVolumeService:
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self._data = []
        self._symbol_map = defaultdict(list)

        self._load_data()
        self._index_data()

    # Load raw JSON
    def _load_data(self):
        if not os.path.exists(self.data_file_path):
            raise FileNotFoundError(
                f"Historical data file not found: {self.data_file_path}"
            )

        with open(self.data_file_path, "r") as f:
            content = f.read().strip()
            if not content:
                self._data = []
            else:
                self._data = json.loads(content)

    # Index by symbol and sort by date

    def _index_data(self):
        for record in self._data:
            self._symbol_map[record["symbol"]].append(record)

        for symbol in self._symbol_map:
            self._symbol_map[symbol].sort(
                key=lambda r: r["date"],
                reverse=True
            )

    # Public APIs

    def get_previous_day_volume(self, symbol):
        records = self._symbol_map.get(symbol, [])
        if not records:
            return None
        return records[0]["volume"]

    def get_weekly_average(self, symbol, days=5):
        records = self._symbol_map.get(symbol, [])
        if len(records) < days:
            return None

        volumes = [r["volume"] for r in records[:days]]
        return int(mean(volumes))

    def get_monthly_average(self, symbol, days=20):
        records = self._symbol_map.get(symbol, [])
        if len(records) < days:
            return None

        volumes = [r["volume"] for r in records[:days]]
        return int(mean(volumes))

    def get_volume_snapshot(self, symbol):

        return {
            "symbol": symbol,
            "prev_day_volume": self.get_previous_day_volume(symbol),
            "weekly_avg_volume": self.get_weekly_average(symbol),
            "monthly_avg_volume": self.get_monthly_average(symbol)
        }
