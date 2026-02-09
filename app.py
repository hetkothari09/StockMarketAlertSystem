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

@app.route("/alerts")
def get_alerts():
    result = []
    for symbol, alerts in storage.alerts.items():
        for a in alerts:
            result.append({
                "id": a.id,
                "symbol": a.symbol,
                "operator": a.operator,
                "right_type": a.right_type,
                "right_value": a.right_value,
                "triggered": a.triggered
            })
    return jsonify(result)


@app.route("/remove-alert", methods=["POST"])
def remove_alert():
    data = request.json
    alert_id = data.get("id")

    if not alert_id:
        return jsonify({"ok": False}), 400

    ok = storage.remove_alert(alert_id)
    return jsonify({"ok": ok})

@app.route("/historical/<symbol>")
def historical(symbol):
    row = storage.symbol_data.get(symbol)

    if not row:
        return jsonify([])

    series = row.get("historical_series")
    if not series:
        storage.add_log(f"No historical data for {symbol}")
    if not isinstance(series, list):
        return jsonify([])

    return jsonify(series)

@app.route("/data")
def data():
    return jsonify(storage.get_all_volumes())

def start_ws():
    ws.connect_ws()

if __name__ == "__main__":
    threading.Thread(target=start_ws, daemon=True).start()
    app.run(debug=False)