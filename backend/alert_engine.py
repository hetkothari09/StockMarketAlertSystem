import uuid
from datetime import datetime

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
            avg = historical.get("weekly_avg")
            if avg is not None and self.right_value is not None:
                return avg * self.right_value
            return None
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

    def evaluate_window_spike(self, symbol, row, storage):
        if symbol in storage.window_alerted_today:
            return

        now = datetime.now().time()
        start = storage.window_start_time
        end = storage.window_end_time

        if not start or not end:
            return

        # If we haven't reached the start yet, show WAITING
        if now < start:
            row["volume_intensity"] = "WAITING"
            return

        # If we are past the end, clamp to the end of the window
        calc_now = min(now, end) if now >= start else start
        
        # Convert times to minutes from midnight for easier subtraction
        now_minutes = calc_now.hour * 60 + calc_now.minute
        start_minutes = start.hour * 60 + start.minute
        elapsed_in_window = max(1, now_minutes - start_minutes)

        total_window = storage.window_minutes()
        if not total_window or total_window == 0:
            return

        mean = row.get("window_mean")
        std = row.get("window_std")
        vol = row.get("window_volume")

        if not mean or not std or std == 0:
            return

        # Expected volume for this specific window duration
        # Logic: We expect the FULL Daily Average to occur within this window
        # (User's preferred logic from prev_files)
        # fraction_of_window = elapsed_in_window / total_window
        
        # Actually, prev_files logic was: expected_volume = mean * (elap    sed / total_window)
        # This implies 'mean' is the expected volume for the *entire window*.
        # In historical_volume.py, 'window_mean' is the DAILY mean.
        # So this formula implies: Expected_Current = Daily_Mean * (Elapsed_In_Window / Window_Duration)
        # This means if Window is 30 mins, we expect the Full Daily Volume to happen in 30 mins? 
        # That seems aggressive, but that's what the formula says: mean * ratio.
        # If ratio reaches 1 (end of window), expected = mean (daily mean).
        # Yes, this assumes the user wants to see if the stock does its Daily Avg Volume within the selected Window.
        
        expected_volume = mean * (elapsed_in_window / total_window)
        
        # Use daily standard deviation without time scaling (per prev_files logic)
        expected_std = std 

        if expected_std == 0:
            z_time = 0
        else:
            z_time = (vol - expected_volume) / expected_std

        row["window_zscore"] = round(z_time, 2)

        # Adjusted thresholds for better sensitivity
        if z_time < 0.5:
            row["volume_intensity"] = "NORMAL"
        elif z_time < 1.5:
            row["volume_intensity"] = "HIGH"
        else:
            row["volume_intensity"] = "VERY HIGH"

        # print(f"DEBUG: {symbol} z={z_time:.2f} intensity={row['volume_intensity']}")

        # Trigger the alert state but only notify if we are inside the window
        if z_time >= 2.0:
            row["window_alert_hit"] = True
            
            # 🔥 ONLY notify if we are actually currently inside the window (live monitoring)
            # This prevents "past alerts" from spamming when settings are applied at 15:41 PM
            if now <= end and symbol not in storage.window_alerted_today:
                storage.window_alerted_today.add(symbol)
                self.notifier.notify(
                    symbol,
                    f"UNUSUAL VOLUME | z={z_time:.2f} | vol={vol:,.0f}"
                )

    # ---------------- USER ALERTS ----------------

    def evaluate_user_alerts(self, symbol, row, storage):
        alerts = storage.get_alerts(symbol)
        if not alerts:
            return

        settings = storage.alert_settings
        for alert in alerts:
            # Skip if the corresponding alert type is disabled globally
            if alert.right_type == "PREV_DAY" and not settings.get("above_prev_day"):
                continue
            if alert.right_type == "WEEKLY_AVG" and not settings.get("above_weekly_avg"):
                continue
            if alert.right_type == "MONTHLY_AVG" and not settings.get("above_monthly_avg"):
                continue
            if alert.right_type == "MULTIPLIER_WEEKLY" and not settings.get("above_weekly_avg"):
                continue

            if alert.should_trigger(row["live_volume"], row):
                alert.mark_triggered()
                row["user_alert_hit"] = True
                row["status"] = "ALERT"

                self.notifier.notify(
                    symbol,
                    f"USER ALERT TRIGGERED | {alert.operator} {alert.right_type}"
                )