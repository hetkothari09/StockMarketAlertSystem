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
        print("WebSocket is connected")
        self.login()
        self.heartbeat()
    
    def on_close(self, ws, *args):
        print("WebSocket is closed!")
    
    def on_error(self, ws, error):
        print("Error occured ", error)

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
            "token": token,
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

    def login(self):
        payload = {
            "Type": "Login",
            "Data": {
                "LoginId": "het",
                "Password": "het"
            }
        }
        self.ws.send(json.dumps(payload))
        print("Login Request sent!")

    def heartbeat(self):
        payload = {
            "Type": "Info",
            "Data": {
                "InfoType": "HB",
                "InfoMsg": "Heartbeat"
            }
        }
        self.ws.send(json.dumps(payload))
        print("Heartbeat Sent!")

    def start_heartbeat(self):
        def heartbeat_loop():
            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                if time.time() - self.last_activity >= HEARTBEAT_INTERVAL:
                    self.heartbeat()
        
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()            