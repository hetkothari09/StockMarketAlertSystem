from datetime import datetime, time

class Storage:
    def __init__(self):
        self.symbols = {}
        self.last_ttq = {}
        self.symbol_data = {}
        self.logs = []

        self.alerts = {}  # symbol → list[VolumeAlert]

        self.window_alerted_today = set()
        self._last_day = None

    def minutes_since_open(self):
        now = datetime.now()
        window_start = now.replace(hour=14, minute=45, second=0, microsecond=0)
        return max(0, int((now - window_start).total_seconds() / 60))

    def window_minutes(self):
        return 30  # 9:15 → 10:30
    

    def in_window(self):
        now = datetime.now().time()
        return time(14, 45) <= now <= time(15, 15)
    
    def reset_if_new_day(self):
        today = datetime.now().date()
        if self._last_day != today:
            self.window_alerted_today.clear()
            for row in self.symbol_data.values():
                row["window_volume"] = 0
                row["window_alert_hit"] = False
                row["user_alert_hit"] = False
            self._last_day = today

    def register_stock(self, token, symbol):
        self.symbols[token] = symbol
        self.symbol_data.setdefault(symbol, {
            "live_volume": 0,
            "window_volume": 0,
            "window_alert_hit": False,
            "user_alert_hit": False,  
            "window_zscore": None
        })

    def set_historical_metrics(self, symbol, metrics):
        self.symbol_data.setdefault(symbol, {}).update(metrics)

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

    # -------- ALERTS --------

    def add_alert(self, symbol, alert):
        self.alerts.setdefault(symbol, []).append(alert)

    def get_alerts(self, symbol):
        return self.alerts.get(symbol, [])

    # -------- UI --------
    def get_historical_series(self, symbol):
        return self.symbol_data.get(symbol, {}).get("historical_series", [])
    
    def add_log(self, msg):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": msg
        })
        self.logs = self.logs[-300:]

    def get_logs(self):
        return self.logs

    # def get_all_volumes(self):
    #     return [{"symbol": s, **v} for s, v in self.symbol_data.items()]
    def get_all_volumes(self):
        rows = []

        for symbol, row in self.symbol_data.items():
            if row.get("window_alert_hit") or row.get("user_alert_hit"):
                row["status"] = "ALERT"
            else:
                row["status"] = "NORMAL"

            z = row.get("window_zscore")
            if z is None:
                row["volume_intensity"] = "WAITING"
            elif z < 1:
                row["volume_intensity"] = "NORMAL"
            elif z < 2:
                row["volume_intensity"] = "HIGH"
            else:
                row["volume_intensity"] = "SPIKE"

            rows.append({"symbol": symbol, **row})

        return rows