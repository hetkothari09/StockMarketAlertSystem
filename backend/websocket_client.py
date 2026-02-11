# websocket_client.py

import json
import time
import threading
from websocket import WebSocketApp

from config import WS_URL, LOGIN_ID, PASSWORD, HEARTBEAT_INTERVAL


class MTWebSocketClient:
    def __init__(self, market_handler):
        self.ws = None
        self.market_handler = market_handler
        self.last_activity = time.time()
        self.subscriptions_list = []
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_delay = 60  # Max 60 seconds between reconnects


    def connect_ws(self):
        self.ws = WebSocketApp(
            WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever()

    def on_open(self, ws):
        print("✅ WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.login()
        self.start_heartbeat()
    
    def on_close(self, ws, *args):
        print("⚠️ WebSocket closed!")
        self.is_connected = False
        self.attempt_reconnect()
    
    def on_error(self, ws, error):
        print(f"❌ WebSocket error: {error}")
        self.is_connected = False

    def on_message(self, ws, message):
        self.last_activity = time.time()

        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            print("Invalid message received!", message)
            return
        
        msg_type = msg.get("Type")

        if msg_type == "Login":
            print("Login is successful!")
            self.subscribe_all()

        elif msg_type == "MarketData":
            self.market_handler.handle(msg["Data"])

        elif msg_type == "FeedStatus":
            # print("Feed: ", msg["Data"])
            pass
        else:
            pass

    
    def add_subscription(self, token, exchange, symbol):
        self.subscriptions_list.append({
            "token": str(token),
            "exchange": exchange,
            "symbol": symbol
        })


    def subscribe(self, token, exchange, symbol):
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
        # print(f"Subscribed to {symbol}")


    def subscribe_all(self):
        for stock in self.subscriptions_list:
            self.subscribe(
                stock["token"],
                stock["exchange"],
                stock["symbol"]
            )

    def attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff."""
        if self.reconnect_attempts >= 10:
            print("❌ Max reconnection attempts reached. Giving up.")
            return
        
        # Exponential backoff: 2^attempts seconds, capped at max_reconnect_delay
        delay = min(2 ** self.reconnect_attempts, self.max_reconnect_delay)
        self.reconnect_attempts += 1
        
        print(f"🔄 Reconnecting in {delay} seconds (attempt {self.reconnect_attempts}/10)...")
        time.sleep(delay)
        
        try:
            threading.Thread(target=self.connect_ws, daemon=True).start()
        except Exception as e:
            print(f"❌ Reconnection failed: {e}")
            self.attempt_reconnect()

    def remove_subscription(self, token):
        """Remove a subscription from the list."""
        self.subscriptions_list = [
            sub for sub in self.subscriptions_list 
            if sub["token"] != str(token)
        ]

    def login(self):
        payload = {
            "Type": "Login",
            "Data": {
                "LoginId": LOGIN_ID,
                "Password": PASSWORD
            }
        }
        self.ws.send(json.dumps(payload))
        print("Login Request sent!")

    def start_heartbeat(self):
        def heartbeat_loop():
            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                if self.ws and self.is_connected:
                    try:
                        payload = {
                            "Type": "Info",
                            "Data": {
                                "InfoType": "HB",
                                "InfoMsg": "Heartbeat"
                            }
                        }
                        self.ws.send(json.dumps(payload))
                    except Exception as e:
                        print(f"Heartbeat failed: {e}")
                        self.is_connected = False

        threading.Thread(target=heartbeat_loop, daemon=True).start()