class VolumeAlert:
    def __init__(
        self,
        symbol,
        operator,
        right_type,
        right_value=None
    ):
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

    def evaluate(self, symbol, current_volume, historical, alerts):
        hit = False
        for alert in alerts:
            if alert.should_trigger(current_volume, historical):
                self.notifier.notify(
                    symbol,
                    current_volume,
                    f"{alert.operator} {alert.right_type}"
                )
                alert.mark_triggered()
                hit = True
        return hit
