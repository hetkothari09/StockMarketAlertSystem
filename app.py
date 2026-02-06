import threading
from flask import Flask, jsonify, render_template, request

from storage import Storage
from websocket_client import MTWebSocketClient
from marketdata_handler import MarketDataHandler
from config import NIFTY50_STOCKS
from alert_engine import VolumeAlert
from historical_volume import HistoricalVolumeLoader

storage = Storage()
handler = MarketDataHandler(storage=storage)
ws = MTWebSocketClient(market_handler=handler)

# ---- Load historical data ----
loader = HistoricalVolumeLoader("data/historical_volumes.json")
hist = loader.load()

for symbol, metrics in hist.items():
    storage.set_historical_metrics(symbol, metrics)

for stock in NIFTY50_STOCKS:
    token = stock["token"]
    symbol = stock["symbol"]
    exchange = stock["exchange"]

    storage.register_stock(symbol=symbol, token=token)
    ws.add_subscription(symbol=symbol, token=token, exchange=exchange)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def logs():
    return jsonify(storage.get_logs())

@app.route("/add-alert", methods=["POST"])
def add_alert():
    data = request.json

    alert = VolumeAlert(
        symbol=data["symbol"],
        operator=data["operator"],
        right_type=data["right_type"],
        right_value=data.get("right_value")
    )

    storage.add_alert(data["symbol"], alert)

    row = storage.symbol_data.get(data["symbol"])

    # 🔥 IMMEDIATE EVALUATION (FIXED)
    if row and alert.should_trigger(row["live_volume"], row):
        alert.mark_triggered()
        row["user_alert_hit"] = True
        row["is_red_alert"] = True

        storage.add_log(
            f"ALERT TRIGGERED IMMEDIATELY: {data['symbol']}"
        )

    storage.add_log(
        f"ALERT CREATED: {data['symbol']} {data['operator']} {data['right_type']}"
    )

    return jsonify({"status": "ok"})

@app.route("/historical/<symbol>")
def historical(symbol):
    return jsonify(storage.get_historical_series(symbol))

@app.route("/data")
def data():
    return jsonify(storage.get_all_volumes())

def start_ws():
    ws.connect_ws()

if __name__ == "__main__":
    threading.Thread(target=start_ws, daemon=True).start()
    app.run(debug=False)