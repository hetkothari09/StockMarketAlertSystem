from alert_engine import AlertEngine
from notifier import Notifier


class MarketDataHandler:
    def __init__(self, storage):
        self.storage = storage
        Notifier.storage = storage
        self.alert_engine = AlertEngine(Notifier)

    def handle(self, data):
        token = data["Tkn"]
        volume = data["TTQ"]

        self.storage.update_volume(token, volume)

        symbol = self.storage.symbols.get(token)
        if not symbol:
            return

        hist = self.storage.historical.get(symbol, {})

        alerts = self.storage.get_alerts(symbol)
        if alerts:
            hit = self.alert_engine.evaluate(
                symbol,
                volume,
                hist,
                alerts
            )
            if hit:
                self.storage.mark_alert_hit(symbol)

