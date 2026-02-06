# websocket_client.py

import json
import time
import threading
from websocket import WebSocketApp

from config import WS_URL, LOGIN_ID, PASSWORD, HEARTBEAT_INTERVAL


class MTWebSocketClient:
    def __init__(self, marketdata_handler):
        self.ws = None
        self.marketdata_handler = marketdata_handler
        self.last_activity = time.time()

        # store all subscriptions here
        self.subscriptions = []

    def add_subscription(self, exchange, token, symbol):
        """
        Register a stock to subscribe after login
        """
        self.subscriptions.append({
            "exchange": exchange,
            "token": token,
            "symbol": symbol
        })

    def connect(self):
        """
        Connect to WebSocket (blocking call)
        """
        self.ws = WebSocketApp(
            WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever()


    def on_open(self, ws):
        print("WebSocket connected")
        self.send_login()
        self.start_heartbeat()

    def on_close(self, ws, *args):
        print("WebSocket closed")

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_message(self, ws, message):
        self.last_activity = time.time()

        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            print("Invalid JSON:", message)
            return

        msg_type = msg.get("Type")

        if msg_type == "Login":
            print("Login successful")
            self.subscribe_all()

        elif msg_type == "MarketData":
            self.marketdata_handler.handle(msg["Data"])

        elif msg_type == "FeedStatus":
            print("Feed status:", msg["Data"])

        elif msg_type == "Info":
            pass  # heartbeat / info messages

        else:
            pass  # ignore other message types for now


    def send_login(self):
        payload = {
            "Type": "Login",
            "Data": {
                "LoginId": "het",
                "Password": "het"
            }
        }
        self.ws.send(json.dumps(payload))
        print("Login request sent")

    def subscribe(self, exchange, token, symbol):
        payload = {
            "Type": "TokenRequest",
            "Data": {
                "SubType": True,
                "FeedType": 1,  # MarketData
                "quotes": [
                    {
                        "Xchg": exchange,
                        "Tkn": token,
                        "Symbol": symbol
                    }
                ]
            }
        }
        self.ws.send(json.dumps(payload))
        print(f"📡 Subscribed to {symbol}")

    def subscribe_all(self):

        for stock in self.subscriptions:
            self.subscribe(
                stock["exchange"],
                stock["token"],
                stock["symbol"]
            )

    def send_heartbeat(self):
        payload = {
            "Type": "Info",
            "Data": {
                "InfoType": "HB",
                "InfoMsg": "Heartbeat"
            }
        }
        self.ws.send(json.dumps(payload))
        print("Heartbeat sent")


    def start_heartbeat(self):
        def heartbeat_loop():
            while True:
                time.sleep(HEARTBEAT_INTERVAL) # sleep for 60 seconds
                if time.time() - self.last_activity >= HEARTBEAT_INTERVAL:
                    self.send_heartbeat()

        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()

