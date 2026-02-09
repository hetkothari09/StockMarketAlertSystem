import uuid
from datetime import datetime, time

SPIKE_THRESHOLD = 2.0


class VolumeAlert:
    def __init__(self, symbol, operator, right_type, right_value=None):
        self.symbol = symbol
        self.operator = operator
        self.right_type = right_type
        self.right_value = right_value
        self.triggered = False
        self.id = str(uuid.uuid4())

    def _resolve_rhs(self, current_volume, historical):
        if self.right_type == "FIXED":
            return self.right_value
        if self.right_type == "PREV_DAY":
            return historical.get("prev_day")
        if self.right_type == "WEEKLY_AVG":
            return historical.get("weekly_avg")
        if self.right_type == "MONTHLY_AVG":
            return historical.get("monthly_avg")
        if self.right_type == "MULTIPLIER_WEEKLY":
            return historical.get("weekly_avg") * self.right_value
        return None

    def should_trigger(self, current_volume, historical):
        if self.triggered:
            return False

        rhs = self._resolve_rhs(current_volume, historical)
        if rhs is None:
            return False

        if self.operator == ">":
            return current_volume > rhs
        if self.operator == ">=":
            return current_volume >= rhs

        return False

    def mark_triggered(self):
        self.triggered = True


class AlertEngine:
    def __init__(self, notifier):
        self.notifier = notifier

    def evaluate(self, symbol, row, storage):
        self.evaluate_window_spike(symbol, row, storage)
        self.evaluate_user_alerts(symbol, row, storage)

    # ---------------- WINDOW SPIKE ----------------

    def evaluate_window_spike(self):
        now = datetime.now().time()

        # Only evaluate during market hours
        if now < time(9, 15) or now > time(15, 30):
            return

        for symbol, row in self.storage.symbol_data.items():
            actual = row.get("window_volume", 0)
            mean = row.get("daily_mean")
            std = row.get("daily_std")

            if mean is None or std is None or std <= 0:
                continue

            # 🔥 FULL-DAY COMPARISON
            z = (actual - mean) / std
            z = max(min(z, 5), -5)  # safety clamp

            row["window_zscore"] = z

            if z >= SPIKE_THRESHOLD:
                if not row.get("window_alert_hit"):
                    row["window_alert_hit"] = True
                    self.storage.add_log(
                        f"ALERT [{symbol}]: EARLY DAY VOLUME SPIKE | z={round(z,2)} | vol={int(actual)}"
                    )

    # ---------------- USER ALERTS ----------------

    def evaluate_user_alerts(self, symbol, row, storage):
        alerts = storage.get_alerts(symbol)
        if not alerts:
            return

        for alert in alerts:
            if alert.should_trigger(row["live_volume"], row):
                alert.mark_triggered()
                row["user_alert_hit"] = True
                row["status"] = "ALERT"

                self.notifier.notify(
                    symbol,
                    f"USER ALERT TRIGGERED | {alert.operator} {alert.right_type}"
                )