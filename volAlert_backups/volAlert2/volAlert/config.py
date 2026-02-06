import json

WS_URL = "ws://115.242.15.134:19101" # WebSocket URL
LOGIN_ID = "het"
PASSWORD = "het"

HEARTBEAT_INTERVAL = 60  # Heartbeat interval in seconds
NIFTY50_STOCKS = []


out_file = r"C:\Users\SMARTTOUCH\Downloads\contracts_nsefo.json"

with open(out_file, 'rb') as f:
    data = json.load(f)

for contract in data:
    symbol = contract['s']
    token = contract['t']
    NIFTY50_STOCKS.append({"symbol": symbol, "token": token, "exchange": "NSECM"})
    NIFTY50_STOCKS.append({"symbol": "RELIANCE", "token": "2885", "exchange": "NSECM"})

print(NIFTY50_STOCKS)

# NIFTY50_STOCKS = [
#     {"symbol": "RELIANCE", "token": "2885", "exchange": "NSECM"},
#     {"symbol": "TCS", "token": "11536", "exchange": "NSECM"},
#     # {"symbol": "INFY", "token": "1594", "exchange": "NSECM"},
#     # {"symbol": "HDFCBANK", "token": "3417", "exchange": "NSECM"},
#     # {"symbol": "HDFC", "token": "5020", "exchange": "NSECM"},
#     # {"symbol": "SBIN", "token": "3045", "exchange": "NSECM"},   
#     # {"symbol": "MARUTI", "token": "5633", "exchange": "NSECM"},
#     # {"symbol": "HCLTECH", "token": "1270", "exchange": "NSECM"}
#     ]