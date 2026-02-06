import threading
from flask import Flask, jsonify, render_template

from storage import Storage
from websocket_client import MTWebSocketClient
from marketdata_handler import MarketDataHandler
from config import NIFTY50_STOCKS
from alert_engine import VolumeAlert
from historical_volume import HistoricalVolumeLoader
from flask import request

storage = Storage()
handler = MarketDataHandler(storage=storage)
ws = MTWebSocketClient(market_handler=handler)

# ---- Load historical data ----
loader = HistoricalVolumeLoader("data/historical_volumes.json")
hist = loader.load()

for symbol, metrics in hist.items():
    storage.set_historical_metrics(symbol, metrics)

    
# storage.add_alert("ADANIENT", VolumeAlert("ADANIENT", 4_38_000))
# storage.add_alert("APOLLOHOSP", VolumeAlert("APOLLOHOSP", 93090))
# storage.add_alert("INFY", VolumeAlert("INFY", 2_000_000))


for stock in NIFTY50_STOCKS:
    token=stock['token']
    symbol=stock['symbol']
    exchange = stock['exchange']

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
    storage.add_log(
        f"ALERT CREATED: {data['symbol']} {data['operator']} {data['right_type']}"
    )

    return jsonify({"status": "ok"})


@app.route("/data")
def data():
    return jsonify(storage.get_all_volumes())

def start_ws():
    ws.connect_ws()

if __name__ == "__main__":
    threading.Thread(target=start_ws, daemon=True).start()
    app.run(debug=False)
