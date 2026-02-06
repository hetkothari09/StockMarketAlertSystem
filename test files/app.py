# app.py

import threading
from flask import Flask, jsonify, render_template

from storage import Storage
from marketdata_handler import MarketDataHandler
from websocket_client import MTWebSocketClient
from config import NIFTY50_STOCKS

storage = Storage()
handler = MarketDataHandler(storage)
ws_client = MTWebSocketClient(handler)

# Register stocks + subscriptions
for stock in NIFTY50_STOCKS:
    storage.register_stock(stock["token"], stock["symbol"])
    ws_client.add_subscription(
        stock["token"],
        stock["exchange"],
        stock["symbol"]
    )

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(storage.get_all_volumes())

def start_ws():
    ws_client.connect()

if __name__ == "__main__":
    threading.Thread(target=start_ws, daemon=True).start()
    app.run(debug=False)
