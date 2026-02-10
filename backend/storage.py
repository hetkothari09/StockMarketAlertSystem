from datetime import datetime, time
import random

class Storage:
    def __init__(self):
        self.symbols = {}
        self.last_ttq = {}
        self.symbol_data = {}
        self.logs = []

        # 🔥 USER-SELECTED TIME RANGE
        self.window_start_time = time(9, 15)   # Default start
        self.window_end_time = time(15, 30)     # Default end

        # 🕒 MINUTE-LEVEL HISTORY (Built live)
        # Format: { symbol: [ { "time": datetime, "vol": int }, ... ] }
        self.volume_history = {}

        self.alerts = {}
        self.window_alerted_today = set()
        self._last_day = None

        # 🔥 ALERT SETTINGS (Toggles)
        self.alert_settings = {
            "above_prev_day": True,
            "above_weekly_avg": True,
            "above_monthly_avg": True
        }

    # ---------------- HISTORY ----------------

    def record_volume(self, symbol, volume, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        
        # Round to nearest minute for storage
        dt_minute = timestamp.replace(second=0, microsecond=0)
        
        history = self.volume_history.setdefault(symbol, [])
        
        # Avoid duplicate entries for same minute (keep latest)
        if history and history[-1]["time"] == dt_minute:
            history[-1]["vol"] = volume
        else:
            history.append({"time": dt_minute, "vol": volume})
            
            # Keep last 400 points (~1 trading day)
            if len(history) > 400:
                history.pop(0)

    def get_volume_at(self, symbol, target_time):
        """
        Find volume at specific time (or closest previous point)
        target_time: datetime.time object
        """
        history = self.volume_history.get(symbol)
        if not history:
            return 0
            
        # Create full datetime for comparison
        target_dt = datetime.combine(datetime.today(), target_time)
        
        # Find closest point <= target_dt
        closest_vol = 0
        for point in history:
            if point["time"] <= target_dt:
                closest_vol = point["vol"]
            else:
                break # sorted by time, so we can stop
                
        return closest_vol

    # ---------------- TIME ----------------

    def minutes_since_open(self):
        """
        Correct market open reference (09:15)
        """
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        return max(1, int((now - market_open).total_seconds() / 60))

    def window_minutes(self):
        """
        Derived window length from selected time range
        """
        if not self.window_start_time or not self.window_end_time:
            return None

        start = datetime.combine(datetime.today(), self.window_start_time)
        end = datetime.combine(datetime.today(), self.window_end_time)
        return int((end - start).total_seconds() / 60)

    def in_selected_time_window(self):
        """
        Check if current time is inside user-selected range
        """
        if not self.window_start_time or not self.window_end_time:
            return True  # no restriction

        now = datetime.now().time()
        return self.window_start_time <= now <= self.window_end_time

    def set_time_range(self, start_str: str, end_str: str):
        """
        Set user-defined time range (HH:MM → HH:MM)
        """
        h1, m1 = map(int, start_str.split(":"))
        h2, m2 = map(int, end_str.split(":"))

        self.window_start_time = time(h1, m1)
        self.window_end_time = time(h2, m2)

        print(f"DEBUG: Timerange set to {self.window_start_time} - {self.window_end_time}")

        # 🔥 RESET WINDOW STATE INTELLIGENTLY
        for symbol, row in self.symbol_data.items():
            live_vol = row.get("live_volume", 0)
            
            # Find what the volume was at the start of the window
            # If we have history, we can subtract it.
            start_vol = self.get_volume_at(symbol, self.window_start_time)
            
            # If window start is 09:15, start_vol should be 0 (market open)
            if self.window_start_time == time(9, 15):
                start_vol = 0
            
            # Window Volume = Today's Total - Volume at Window Start
            # (If negative, means data reset or mismatch, limit to 0)
            row["window_volume"] = max(0, live_vol - start_vol)
            
            row["window_zscore"] = None
            row["window_alert_hit"] = False

        self.window_alerted_today.clear()

        self.add_log(f"TIME WINDOW SET: {start_str} → {end_str}")

    # ---------------- RESET ----------------

    def reset_if_new_day(self):
        today = datetime.now().date()
        if self._last_day != today:
            self.window_alerted_today.clear()
            for row in self.symbol_data.values():
                row["window_volume"] = 0
                row["window_alert_hit"] = False
                row["user_alert_hit"] = False
                row["is_red_alert"] = False
                row["window_zscore"] = None
                row["last_status"] = None
            self._last_day = today

    # ---------------- REGISTRATION ----------------

    def register_stock(self, token, symbol):
        self.symbols[token] = symbol
        self.symbol_data.setdefault(symbol, {
            "live_volume": 0,
            "window_volume": 0,
            "window_alert_hit": False,
            "user_alert_hit": False,
            "is_red_alert": False,
            "window_zscore": None,
            "volume_intensity": "WAITING",
            "status": "NORMAL",
            "last_status": None,
        })

    def set_historical_metrics(self, symbol, metrics):
        self.symbol_data.setdefault(symbol, {}).update(metrics)

    # ---------------- TICKS ----------------

    def update_tick(self, token, ttq):
        symbol = self.symbols.get(token)
        if not symbol:
            return

        row = self.symbol_data[symbol]

        if ttq == 0:
            prev_val = self.last_ttq.get(token, random.randint(1_000_000, 3_000_000))
            ttq = prev_val + random.randint(20_000, 150_000)

        prev = self.last_ttq.get(token, 0)
        delta = max(ttq - prev, 0)
        self.last_ttq[token] = ttq

        # live_volume always updates
        row["live_volume"] = ttq

        # window_volume ONLY adds delta if we are currently inside the window
        # (This ensures it freezes once the window ends)
        now = datetime.now().time()
        is_inside = True
        if self.window_start_time and self.window_end_time:
            is_inside = self.window_start_time <= now <= self.window_end_time
            
        if is_inside:
            row["window_volume"] += delta

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
                    self.add_log(f"ALERT REMOVED: {symbol}")
                    
                    # Re-evaluate status immediately
                    row = self.symbol_data.get(symbol)
                    if row:
                        any_hit = any(alert.evaluate(row) for alert in alerts)
                        if not any_hit:
                            row["user_alert_hit"] = False
                            if row.get("status") == "ALERT":
                                row["status"] = "BELOW AVERAGES" # Reset to default
                    return True
        return False

    # ---------------- LOGS ----------------

    def add_log(self, msg):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": msg
        })
        self.logs = self.logs[-300:]

    def get_logs(self):
        return self.logs

    # ---------------- UI DATA ----------------

    def get_all_volumes(self):
        rows = []

        for symbol, row in self.symbol_data.items():
            lv = row.get("live_volume", 0)

            # ================= STATUS (RELATIVE LEVELS) =================
            status_parts = []

            if self.alert_settings.get("above_prev_day") and row.get("prev_day") and lv >= row["prev_day"]:
                status_parts.append("ABOVE PREV DAY")

            if self.alert_settings.get("above_weekly_avg") and row.get("weekly_avg") and lv >= row["weekly_avg"]:
                status_parts.append("ABOVE WEEKLY AVG")

            if self.alert_settings.get("above_monthly_avg") and row.get("monthly_avg") and lv >= row["monthly_avg"]:
                status_parts.append("ABOVE MONTHLY AVG")

            if row.get("user_alert_hit"):
                row["status"] = "ALERT"
            elif status_parts:
                row["status"] = " | ".join(status_parts)
            else:
                row["status"] = "BELOW AVERAGES"

            prev = row.get("last_status")
            curr = row["status"]

            if prev is not None and prev != curr:
                self.add_log(f"[{symbol}]: {prev} → {curr}")

            row["last_status"] = curr

            # ================= VOLUME MOVEMENT =================
            z = row.get("window_zscore")

            if z is None:
                row["volume_intensity"] = "WAITING"
            elif z < 1:
                row["volume_intensity"] = "NORMAL"
            elif z < 2:
                row["volume_intensity"] = "HIGH"

            row["is_red_alert"] = bool(
                row.get("window_alert_hit") or row.get("user_alert_hit")
            )

            rows.append({"symbol": symbol, **row})

        return rows