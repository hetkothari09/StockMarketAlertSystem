from datetime import datetime

class Storage:
    def __init__(self):
        self.volumes = {}
        self.symbols = {}
        self.alerts = {}
        self.historical = {}
        self.logs = []
        self.alert_hits = set()

    def mark_alert_hit(self, symbol):
        self.alert_hits.add(symbol)

    def is_alert_hit(self, symbol):
        return symbol in self.alert_hits

    def add_log(self, message):
        self.logs.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message
        })
        # if len(self.logs) > 300:
        #     self.logs.pop(0)

    def get_logs(self):
        return self.logs

    def register_stock(self, token, symbol):
        self.symbols[token] = symbol

    def update_volume(self, token, volume):
        self.volumes[token] = volume

    def set_historical_metrics(self, symbol, metrics):
        self.historical[symbol] = metrics

    def get_all_volumes(self):
        result = {}

        for token, volume in self.volumes.items():
            symbol = self.symbols.get(token)
            if not symbol:
                continue

            hist = self.historical.get(symbol, {})

            # overwrite → keeps latest volume per symbol
            result[symbol] = {
                "symbol": symbol,
                "live_volume": volume,
                "prev_day": hist.get("prev_day"),
                "weekly_avg": hist.get("weekly_avg"),
                "monthly_avg": hist.get("monthly_avg"),
                "alert_hit": self.is_alert_hit(symbol)
            }

        return list(result.values())


    def add_alert(self, symbol, alert):
        self.alerts.setdefault(symbol, []).append(alert)

    def get_alerts(self, symbol):
        return self.alerts.get(symbol, [])
