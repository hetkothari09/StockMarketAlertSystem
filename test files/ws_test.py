import websocket

WS_URL = "ws://115.242.15.134:19101"  # public test websocket

def on_open(ws):
    print("✅ WebSocket connected")
    ws.send("Hello WebSocket!")

def on_message(ws, message):
    print("📩 Message received:", message)
    ws.close()

def on_error(ws, error):
    print("❌ Error:", error)

def on_close(ws):
    print("🔌 WebSocket closed")

ws = websocket.WebSocketApp(
    WS_URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()