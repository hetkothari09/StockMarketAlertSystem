from datetime import datetime
import random

class Storage:
    def __init__(self):
        self.symbols = {}
        self.last_ttq = {}
        self.symbol_data = {}
        self.logs = []
        self.alerts = {}
        self.window_alerted_today = set()
        self._last_day = None

    def reset_if_new_day(self):
        today = datetime.now().date()
        if self._last_day != today:
            self.window_alerted_today.clear()
            for row in self.symbol_data.values():
                row["window_volume"] = 0
                row["window_alert_hit"] = False
                row["user_alert_hit"] = False
                row["window_zscore"] = None
            self._last_day = today

    # ---------------- TIME ----------------

    # def minutes_since_open(self):
    #     now = datetime.now()
    #     window_start = now.replace(hour=15, minute=00, second=0, microsecond=0)
    #     return max(1, int((now - window_start).total_seconds() / 60))

    # def window_minutes(self):
    #     return 30

    # def in_window(self):
    #     return True  # dev-safe

    # ---------------- RESET ----------------

    # def reset_if_new_day(self):
    #     today = datetime.now().date()
    #     if self._last_day != today:
    #         self.window_alerted_today.clear()
    #         for row in self.symbol_data.values():
    #             row["window_volume"] = 0
    #             row["window_alert_hit"] = False
    #             row["user_alert_hit"] = False
    #             row["is_red_alert"] = False
    #             row["window_zscore"] = None
    #         self._last_day = today

    # ---------------- REGISTRATION ----------------

    def register_stock(self, token, symbol):
        self.symbols[token] = symbol
        self.symbol_data.setdefault(symbol, {
            "live_volume": 0,
            "window_volume": 0,
            "window_alert_hit": False,
            "user_alert_hit": False,
            "window_zscore": None,
            "status": "BELOW AVERAGES",
            "volume_intensity": "WAITING"
        })

    def set_historical_metrics(self, symbol, metrics):
        self.symbol_data.setdefault(symbol, {}).update(metrics)

    def update_tick(self, token, ttq):
        symbol = self.symbols.get(token)
        if not symbol:
            return

        row = self.symbol_data[symbol]

        if ttq == 0:
            prev = self.last_ttq.get(token, random.randint(1_000_000, 3_000_000))
            ttq = prev + random.randint(20_000, 150_000)

        prev = self.last_ttq.get(token, 0)
        delta = max(ttq - prev, 0)
        self.last_ttq[token] = ttq

        row["live_volume"] = ttq
        row["window_volume"] += delta

    def add_log(self, msg):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": msg
        })
        self.logs = self.logs[-300]

    def get_logs(self):
        return self.logs

    # ---------------- ALERTS ----------------

    def add_alert(self, symbol, alert):
        self.alerts.setdefault(symbol, []).append(alert)

    def get_alerts(self, symbol):
        return self.alerts.get(symbol, [])

    def remove_alert(self, alert_id):
        for symbol, alerts in self.alerts.items():
            for a in list(alerts):
                if a.id == alert_id:
                    alerts.remove(a)

                    # 🔥 RESET SYMBOL ALERT STATE
                    row = self.symbol_data.get(symbol)
                    if row:
                        row["user_alert_hit"] = False

                        # recompute status cleanly
                        if row.get("window_alert_hit"):
                            row["status"] = "SPIKE"
                        else:
                            row["status"] = "BELOW AVERAGES"
                    
                    self.add_log(f"ALERT REMOVED: {symbol}")
                    return True
        return False
    # ---------------- LOGS ----------------

    # def add_log(self, msg):
    #     self.logs.append({
    #         "time": datetime.now().strftime("%H:%M:%S"),
    #         "message": msg
    #     })
    #     self.logs = self.logs[-300:]

    # def get_logs(self):
    #     return self.logs

    # ---------------- UI DATA ----------------

    def get_all_volumes(self):
        rows = []

        for symbol, row in self.symbol_data.items():
            lv = row.get("live_volume", 0)

            # ================= STATUS (RELATIVE LEVELS) =================
            status_parts = []

            if row.get("prev_day") and lv >= row["prev_day"]:
                status_parts.append("ABOVE PREV DAY")

            if row.get("weekly_avg") and lv >= row["weekly_avg"]:
                status_parts.append("ABOVE WEEKLY AVG")

            if row.get("monthly_avg") and lv >= row["monthly_avg"]:
                status_parts.append("ABOVE MONTHLY AVG")

            # ALERT OVERRIDES
            if row.get("user_alert_hit"):
                row["status"] = "ALERT"
            # elif row.get("window_alert_hit"):
            #     row["status"] = "SPIKE"
            elif status_parts:
                row["status"] = " | ".join(status_parts)
            else:
                row["status"] = "BELOW AVERAGES"


            prev = row.get("last_status")
            curr = row["status"]

            # 🔥 LOG ONLY REAL TRANSITIONS
            if prev is not None and prev != curr:
                self.add_log(
                    f"[{symbol}]: {prev} → {curr}"
                )

            row["last_status"] = curr

            # ================= VOLUME MOVEMENT (INTENSITY) =================
            z = row.get("window_zscore")

            if z is None:
                row["volume_intensity"] = "WAITING"
            elif z < 1:
                row["volume_intensity"] = "NORMAL"
            elif z < 2:
                row["volume_intensity"] = "HIGH"
            # else:
            #     row["volume_intensity"] = "SPIKE"

            row["is_red_alert"] = bool(
                row.get("window_alert_hit") or row.get("user_alert_hit")
            )

            rows.append({"symbol": symbol, **row})

        return rows