class Notifier:
    storage = None

    @classmethod
    def notify(cls, symbol, volume, threshold):
        cls.storage.add_log(
            f"ALERT: {symbol} crossed volume {threshold} (Live: {volume})"
        )
