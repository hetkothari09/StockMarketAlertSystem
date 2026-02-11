import threading
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from storage import Storage
from websocket_client import MTWebSocketClient
from marketdata_handler import MarketDataHandler
from config import NIFTY50_STOCKS
from alert_engine import VolumeAlert
from historical_volume import HistoricalVolumeLoader

storage = Storage()
handler = MarketDataHandler(storage=storage)
ws = MTWebSocketClient(market_handler=handler)

from scripts.ingest_bhavcopy import run_auto_ingest, backfill_symbol
import token_lookup
import extract_token_no

# ---- Load historical data ----
loader = HistoricalVolumeLoader("data/historical_volumes.json")
hist = loader.load()

monitored_symbols = {s["symbol"].strip().upper() for s in NIFTY50_STOCKS}
for symbol, metrics in hist.items():
    clean_sym = symbol.strip().upper()
    if clean_sym in monitored_symbols:
        storage.set_historical_metrics(clean_sym, metrics)

for stock in NIFTY50_STOCKS:
    token = stock["token"]
    symbol = stock["symbol"]
    exchange = stock["exchange"]

    storage.register_stock(symbol=symbol, token=token, log=False)
    ws.add_subscription(symbol=symbol, token=token, exchange=exchange)

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "service": "VolAlert Backend API",
        "version": "2.0.0",
        "port": 7000
    })

@app.route("/logs")
def logs():
    return jsonify(storage.get_logs())

@app.route("/add-alert", methods=["POST"])
def add_alert():
    try:
        from datetime import datetime
        data = request.json
        if not data or "symbol" not in data:
            return jsonify({"status": "error", "message": "Missing symbol"}), 400

        symbol = data["symbol"]
        
        alert = VolumeAlert(
            symbol=symbol,
            operator=data.get("operator", ">"),
            right_type=data.get("right_type", "FIXED"),
            right_value=data.get("right_value")
        )

        storage.add_alert(symbol, alert)
        
        row = storage.symbol_data.get(symbol)

        # Defensive check for immediate trigger
        if row and row.get("live_volume") is not None:
            try:
                if alert.should_trigger(row["live_volume"], row):
                    alert.mark_triggered()
                    row["user_alert_hit"] = True
                    row["is_red_alert"] = True
                    storage.add_log(f"ALERT TRIGGERED IMMEDIATELY: {symbol}")
            except Exception as eval_err:
                print(f"Error evaluating immediate trigger: {eval_err}")

        storage.add_log(f"ALERT CREATED: {symbol}")
        return jsonify({"status": "ok"})

    except Exception as e:
        import traceback
        import json
        from datetime import datetime
        err_detail = traceback.format_exc()
        error_msg = f"CRITICAL ERROR IN /add-alert: {str(e)}\n{err_detail}"
        print(error_msg)
        try:
            with open("backend_debug.log", "a") as f:
                f.write(f"\n--- {datetime.now()} ---\n{error_msg}\n")
        except: pass
        return jsonify({"status": "error", "message": str(e)}), 500

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

@app.route("/set-time-range", methods=["POST"])
def set_time_range():
    data = request.json
    start = data.get("start")
    end = data.get("end")

    if not start or not end:
        return jsonify({"ok": False}), 400

    storage.set_time_range(start, end)
    return jsonify({"ok": True, "start": start, "end": end})

@app.route("/alert-settings", methods=["GET", "POST"])
def alert_settings():
    if request.method == "POST":
        data = request.json
        storage.alert_settings["above_prev_day"] = data.get("above_prev_day", storage.alert_settings["above_prev_day"])
        storage.alert_settings["above_weekly_avg"] = data.get("above_weekly_avg", storage.alert_settings["above_weekly_avg"])
        storage.alert_settings["above_monthly_avg"] = data.get("above_monthly_avg", storage.alert_settings["above_monthly_avg"])
        storage.add_log(f"ALERT SETTINGS UPDATED: {storage.alert_settings}")
        return jsonify({"ok": True, "settings": storage.alert_settings})
    
    return jsonify(storage.alert_settings)

@app.route("/data")
def data():
    return jsonify(storage.get_all_volumes())

@app.route("/available-symbols")
def available_symbols():
    """
    Returns all available NSE EQ symbols from NSECM.xml.
    Results are cached for performance.
    """
    try:
        symbols = token_lookup.get_all_symbols()
        return jsonify({
            "status": "ok",
            "count": len(symbols),
            "symbols": symbols
        })
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/add-stock", methods=["POST"])
def add_stock():
    try:
        data = request.json
        symbol = data.get("symbol", "").strip().upper()
        days = data.get("days", 30)  # Default to 30 days if not specified
        
        if not symbol:
            return jsonify({"status": "error", "message": "Symbol is required"}), 400
        
        # Get token details
        token_info = token_lookup.get_token_details(symbol)
        if not token_info:
            return jsonify({
                "status": "error", 
                "message": f"Symbol {symbol} not found in NSE contracts."
            }), 404
        
        token = token_info["token"]
        exchange = "NSECM"  # Default exchange for NSE stocks

        # Check if already monitoring - if so, just extend the historical data
        is_existing = symbol in storage.symbols.values()
        
        if is_existing:
            storage.add_log(f"📊 {symbol}: Extending historical data to {days} days")
        else:
            # 2. Immediately register in Storage & WebSocket for new symbols
            # This allows the stock to appear in the UI right away
            storage.register_stock(symbol=symbol, token=token)
            ws.add_subscription(symbol=symbol, token=token, exchange=exchange)
            storage.add_log(f"STOCK ADDED: {symbol} (backfilling {days} days in background)")
        
        
        # 3. Launch background thread for backfill and validation
        def background_backfill():
            try:
                print(f"🚀 Background backfill started for {symbol} ({days} days)")
                success = backfill_symbol(symbol, days=days)
                
                if not success:
                    storage.add_log(f"❌ {symbol}: Backfill failed - no data found")
                    # Only remove if it's a NEW symbol (not existing)
                    if not is_existing:
                        token_removed = storage.remove_stock(symbol)
                        if token_removed:
                            ws.remove_subscription(token_removed)
                    return
                
                # Reload and validate
                new_hist = loader.load()
                metrics = new_hist.get(symbol)
                
                if not metrics:
                    storage.add_log(f"⚠️ {symbol}: No historical data found after backfill")
                    # Only remove if it's a NEW symbol
                    if not is_existing:
                        token_removed = storage.remove_stock(symbol)
                        if token_removed:
                            ws.remove_subscription(token_removed)
                    return
                
                # Recency check - ONLY for new symbols
                if not is_existing:
                    all_dates = [m.get("last_date") for m in new_hist.values() if m.get("last_date")]
                    if all_dates:
                        max_market_date = max(all_dates)
                        symbol_last_date = metrics.get("last_date")
                        
                        if symbol_last_date:
                            d1 = datetime.strptime(max_market_date, "%Y-%m-%d")
                            d2 = datetime.strptime(symbol_last_date, "%Y-%m-%d")
                            
                            if (d1 - d2).days > 7:
                                storage.add_log(f"⚠️ {symbol}: Appears inactive (last trade: {symbol_last_date})")
                                token_removed = storage.remove_stock(symbol)
                                if token_removed:
                                    ws.remove_subscription(token_removed)
                                return
                
                # Success - update metrics
                storage.set_historical_metrics(symbol, metrics)
                storage.add_log(f"✅ {symbol}: Historical data loaded ({days} days)")
                print(f"✅ Background backfill completed for {symbol}")
                
            except Exception as e:
                storage.add_log(f"❌ {symbol}: Backfill failed - {str(e)}")
                print(f"Error in background backfill for {symbol}: {e}")
                # Only remove NEW symbols on critical failure
                if not is_existing:
                    try:
                        token_removed = storage.remove_stock(symbol)
                        if token_removed:
                            ws.remove_subscription(token_removed)
                    except Exception as cleanup_error:
                        print(f"Error cleaning up {symbol}: {cleanup_error}")
        
        # Start background thread
        threading.Thread(target=background_backfill, daemon=True).start()
        
        return jsonify({
            "status": "ok", 
            "message": f"Added {symbol}. Fetching {days} days of history in background...",
            "token_info": token_info
        })

    except Exception as e:
        print(f"Error adding stock: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/verify-window")
def verify_window():
    import datetime
    now = datetime.datetime.now().time()
    return jsonify({
        "current_server_time": str(now),
        "window_start": str(storage.window_start_time),
        "window_end": str(storage.window_end_time),
        "in_window": storage.in_selected_time_window(),
        "sample_stock": list(storage.symbol_data.items())[0] if storage.symbol_data else "NO DATA"
    })

def start_ws():
    # Run auto-ingest in background before connecting WS
    try:
        run_auto_ingest()
    except Exception as e:
        print(f"⚠️ Background auto-ingest failed: {e}")
    ws.connect_ws()

if __name__ == "__main__":
    threading.Thread(target=start_ws, daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=7000)