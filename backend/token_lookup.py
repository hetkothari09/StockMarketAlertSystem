import os
import json

# Path to the cached JSON file
SYMBOLS_CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "all_symbols.json")

# Cache for all symbols
_all_symbols_cache = None

def get_all_symbols():
    """
    Returns a list of all EQ series symbols from the cached JSON file.
    Results are cached after first call.
    """
    global _all_symbols_cache
    
    # Return cached data if available
    if _all_symbols_cache is not None:
        return _all_symbols_cache
    
    if not os.path.exists(SYMBOLS_CACHE_PATH):
        print(f"Error: Cached symbols JSON not found at {SYMBOLS_CACHE_PATH}")
        return []
    
    try:
        with open(SYMBOLS_CACHE_PATH, "r") as f:
            symbols = json.load(f)
            _all_symbols_cache = symbols
            return symbols
    except Exception as e:
        print(f"Error reading symbols cache: {e}")
        return []

def get_token_details(target_symbol):
    """
    Searches the cached JSON for the given symbol and returns its details.
    Returns None if not found or file missing.
    """
    target_symbol = target_symbol.strip().upper()
    
    symbols = get_all_symbols()
    if not symbols:
        return None
        
    for item in symbols:
        if item.get("symbol", "").strip().upper() == target_symbol:
            return {
                "symbol": item["symbol"],
                "token": item["token"],
                "exchange": "NSECM",
                "series": "EQ"
            }
            
    return None

if __name__ == "__main__":
    # Test
    res = get_token_details("ZOMATO")
    print(res)
