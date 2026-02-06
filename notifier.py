class Notifier:
    storage = None

    @classmethod
    def notify(cls, symbol, message):
        cls.storage.add_log(f"ALERT [{symbol}]: {message}")
