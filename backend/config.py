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

# Hardcoded NIFTY 50 Symbols (to ensure clean default state)
NIFTY_50_SYMBOLS = {
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN", "HINDUNILVR", "ITC", 
    "BHARTIARTL", "L&T", "KOTAKBANK", "AXISBANK", "HCLTECH", "ADANIENT", "MARUTI", 
    "SUNPHARMA", "TATAMOTORS", "ULTRACEMCO", "TITAN", "ONGC", "NTPC", "POWERGRID", 
    "M&M", "ADANIPORTS", "COALINDIA", "BAJFINANCE", "WIPRO", "BPCL", "TATASTEEL", 
    "HDFCLIFE", "SBILIFE", "DRREDDY", "HINDALCO", "TATACONSUM", "TECHM", "GRASIM", 
    "CIPLA", "DIVISLAB", "HEROMOTOCO", "APOLLOHOSP", "BRITANNIA", "EICHERMOT", "UPL", 
    "BAJAJFINSV", "NESTLEIND", "ASIANPAINT", "INDUSINDBK", "BAJAJ-AUTO", "JSWSTEEL", 
    "TRENT", "BEL", "TATACHEM" 
}

with open(out_file, 'rb') as f:
    data = json.load(f)

for contract in data:
    symbol = contract['s'].strip().upper()
    
    # Strict filter: Only allow actual NIFTY 50 symbols
    if symbol in NIFTY_50_SYMBOLS:
        token = contract['t']
        NIFTY50_STOCKS.append({"symbol": symbol, "token": token, "exchange": "NSECM"})
