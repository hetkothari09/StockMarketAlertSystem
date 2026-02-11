import json

WS_URL = "ws://115.242.15.134:19102" # WebSocket URL
LOGIN_ID = "test"
PASSWORD = "test"

HEARTBEAT_INTERVAL = 60  # Heartbeat interval in seconds
NIFTY50_STOCKS = []


out_file = r"C:\Users\SMARTTOUCH\Downloads\contracts_nsefo.json"

# Tasks for UI/UX improvements
# - [/] Feature: Refine Dynamic Stock Addition <!-- id: 64 -->
#     - [x] Add backend validation for live data availability <!-- id: 65 -->
#     - [x] Refine `AddStockModal` UI (Glassmorphism & Centering) <!-- id: 66 -->
#     - [x] Optimize "Add Stock" button placement <!-- id: 67 -->
# - [/] UI Polish: Compact Sidebar Filters <!-- id: 68 -->
#     - [ ] Reduce padding and gaps in `.toggle-group` <!-- id: 69 -->
#     - [ ] Shrink `.toggle-switch` and font sizes in `.toggle-item` <!-- id: 70 -->
#     - [ ] Tighten up sidebar panel spacing <!-- id: 71 -->
# - [/] UI Polish: Shrink Movement Filters <!-- id: 72 -->
#     - [ ] Reduce padding and gaps in `.movement-filter-group` <!-- id: 73 -->
#     - [ ] Shrink `.movement-filter-item` and font sizes <!-- id: 74 -->
# - [/] UI Polish: Shrink Alert Settings <!-- id: 75 -->
#     - [ ] Reduce padding and gaps in `.alert-settings-group` <!-- id: 76 -->
#     - [ ] Shrink `.alert-setting-item` and font sizes <!-- id: 77 -->
# - [x] Feature: Dynamic Stock Addition <!-- id: 58 -->

with open(out_file, 'rb') as f:
    data = json.load(f)

for contract in data:
    symbol = contract['s'].strip().upper()
    # Filter out TATAMOTORS and any variations like TATAMOTORS-EQ
    if "TATAMOTORS" in symbol:
        continue
    token = contract['t']
    NIFTY50_STOCKS.append({"symbol": symbol, "token": token, "exchange": "NSECM"})


# print(NIFTY50_STOCKS)

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