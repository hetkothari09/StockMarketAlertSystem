class VolumeAlert:
    def __init__(self, symbol, operator, right_type, right_value=None):
        self.symbol = symbol
        self.operator = operator
        self.right_type = right_type
        self.right_value = right_value
        self.triggered = False

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

    # ---------------- WINDOW SPIKE (INSTITUTIONAL) ----------------

    def evaluate_window_spike(self, symbol, row, storage):
        if symbol in storage.window_alerted_today:
            return

        mean = row.get("window_mean")
        std = row.get("window_std")
        p90 = row.get("window_p90")
        vol = row.get("window_volume")

        if not mean or not std or std == 0:
            return

        elapsed = storage.minutes_since_open()
        total_window = storage.window_minutes()

        if elapsed < 10:
            return

        expected_volume = mean * (elapsed / total_window)
        z_time = (vol - expected_volume) / std

        row["window_zscore"] = round(z_time, 2)

        if z_time < 1:
            row["volume_intensity"] = "NORMAL"
        elif z_time < 2:
            row["volume_intensity"] = "HIGH"
        else:
            row["volume_intensity"] = "SPIKE"

        if z_time >= 2.5 or vol >= p90 * (elapsed / total_window):
            storage.window_alerted_today.add(symbol)
            row["window_alert_hit"] = True

            self.notifier.notify(
                symbol,
                f"INSTITUTIONAL VOLUME | z={z_time:.2f} | vol={vol}"
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
                row["status"] = "ALERT"  # ✅ ONLY user alerts set status

                self.notifier.notify(
                    symbol,
                    f"USER ALERT TRIGGERED | {alert.operator} {alert.right_type}"
                )