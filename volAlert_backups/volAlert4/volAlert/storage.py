from datetime import datetime, time

class Storage:
    def __init__(self):
        self.symbols = {}              # token → symbol
        self.last_ttq = {}             # token → last TTQ
        self.symbol_data = {}          # symbol → all metrics
        self.logs = []
        self.window_alerted_today = set()
        self._last_day = None

    def in_window(self):
        now = datetime.now().time()
        return time(9, 15) <= now <= time(10, 30)

    def reset_if_new_day(self):
        today = datetime.now().date()
        if self._last_day != today:
            self.window_alerted_today.clear()
            for s in self.symbol_data.values():
                s["window_volume"] = 0
                s["window_alert_hit"] = False
            self._last_day = today

    def add_log(self, msg):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": msg
        })
        if len(self.logs) > 300:
            self.logs.pop(0)

    def get_logs(self):
        return self.logs

    def register_stock(self, token, symbol):
        self.symbols[token] = symbol
        self.symbol_data.setdefault(symbol, {
            "live_volume": 0,
            "window_volume": 0,
            "window_alert_hit": False
        })

    def set_historical_metrics(self, symbol, metrics):
        self.symbol_data.setdefault(symbol, {}).update(metrics)

    # live updates
    def update_tick(self, token, ttq):
        symbol = self.symbols.get(token)
        if not symbol:
            return

        prev = self.last_ttq.get(token, 0)
        delta = max(ttq - prev, 0)
        self.last_ttq[token] = ttq

        row = self.symbol_data[symbol]
        row["live_volume"] = ttq

        if self.in_window():
            row["window_volume"] += delta

    # ui 
    def get_all_volumes(self):
        return [
            {"symbol": s, **v}
            for s, v in self.symbol_data.items()
        ]
