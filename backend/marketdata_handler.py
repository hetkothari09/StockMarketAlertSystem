from alert_engine import AlertEngine
from notifier import Notifier

class MarketDataHandler:
    def __init__(self, storage):
        self.storage = storage
        Notifier.storage = storage
        self.alert_engine = AlertEngine(Notifier)

    def handle(self, data):
        try:
            token = str(data.get("Tkn"))
            ttq = data.get("TTQ", 0)

            if not token:
                return

            self.storage.reset_if_new_day()
            self.storage.update_tick(token, ttq)

            # 🕒 Record history for minute-level tracking
            symbol = self.storage.symbols.get(token)
            if symbol:
                self.storage.record_volume(symbol, ttq)

            # Trigger alert evaluation
            row = self.storage.symbol_data.get(symbol)
            if not row:
                return

            self.alert_engine.evaluate(symbol, row, self.storage)
        except Exception as e:
            print(f"Error handling tick: {e}")
