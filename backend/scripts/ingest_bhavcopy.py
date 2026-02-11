# scripts/ingest_bhavcopy.py

import requests
import zipfile
import io
import csv
import json
import os
from datetime import date, timedelta

# =====================================================
# CONFIG
# =====================================================

DAYS_TO_BACKFILL = 365   # ~2 months

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "historical_volumes.json"
)

# ---- Try to import from project config ----
try:
    from config import NIFTY50_STOCKS
    NIFTY_SYMBOLS = {s["symbol"] for s in NIFTY50_STOCKS}
except ImportError:
    # Fallback if run standalone from scripts/
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        from config import NIFTY50_STOCKS
        NIFTY_SYMBOLS = {s["symbol"] for s in NIFTY50_STOCKS}
    except Exception:
        NIFTY_SYMBOLS = set() # Empty fallback


# =====================================================
# SAFE JSON HELPERS
# =====================================================

def load_existing():
    if not os.path.exists(OUTPUT_FILE):
        return []

    try:
        with open(OUTPUT_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        print("⚠️ Warning: historical_volumes.json invalid, resetting.")
        return []

def save_existing(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =====================================================
# INGESTION (SINGLE DAY)
# =====================================================

def ingest_for_date(target_date, existing, allowed_symbols=None):
    date_str = target_date.strftime("%Y%m%d")

    bhavcopy_url = (
        "https://nsearchives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
    )

    try:
        r = requests.get(bhavcopy_url, headers=HEADERS, timeout=15)
    except Exception:
        return False

    if r.status_code != 200 or "zip" not in r.headers.get("Content-Type", ""):
        return False

    existing_keys = {(r["symbol"], r["date"]) for r in existing}
    new_records = []

    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_name = z.namelist()[0]

            with z.open(csv_name) as csv_file:
                reader = csv.DictReader(io.TextIOWrapper(csv_file))

                for row in reader:
                    symbol = row.get("TckrSymb", "").strip().upper()
                    series = row.get("SctySrs", "").strip().upper()

                    if series != "EQ":
                        continue

                    # If specific symbols allowed, only process those
                    # Otherwise default to NIFTY_SYMBOLS list
                    if allowed_symbols:
                         if symbol not in allowed_symbols:
                             continue
                    elif symbol not in NIFTY_SYMBOLS:
                        continue

                    try:
                        volume = int(row.get("TtlTradgVol"))
                        trade_date = row.get("TradDt")
                    except Exception:
                        continue

                    key = (symbol, trade_date)
                    if key in existing_keys:
                        continue

                    new_records.append({
                        "symbol": symbol,
                        "date": trade_date,
                        "volume": volume
                    })

    except Exception:
        return False

    if new_records:
        existing.extend(new_records)
        save_existing(existing)
        print(f"✅ {target_date} → added {len(new_records)} records")
        if verbose_output:
             print(f"   Sample: {new_records[0]}")
        return True

    return False

# =====================================================
# BACKFILL CONTROLLER
# =====================================================
verbose_output = False

def backfill_last_two_months():
    print("Starting bhavcopy backfill")
    existing = load_existing()
    today = date.today()

    for i in range(1, DAYS_TO_BACKFILL + 1):
        target_date = today - timedelta(days=i)
        ingest_for_date(target_date, existing)

    print("✅ Backfill completed")

def backfill_symbol(symbol, days=30):
    """
    Backfills data for a specific single symbol for the last N trading days.
    Stops searching once N trading days are found.
    Used when a user adds a stock dynamically.
    """
    print(f"🚀 Starting backfill for single symbol: {symbol} ({days} trading days)")
    existing = load_existing()
    today = date.today()
    
    # We pass a set containing just this symbol as allowed
    allowed = {symbol}
    
    global verbose_output
    verbose_output = True

    trading_days_found = 0
    max_search_days = 730  # Cap at 2 years max to prevent infinite loops
    
    for i in range(1, max_search_days + 1):
        target_date = today - timedelta(days=i)
        
        # Check if we found data for this date
        if ingest_for_date(target_date, existing, allowed_symbols=allowed):
            trading_days_found += 1
            print(f"  Found trading day {trading_days_found}/{days} for {target_date}")
            
            # Stop once we have enough trading days
            if trading_days_found >= days:
                print(f"✅ Found {days} trading days, stopping search")
                break
    
    if trading_days_found < days:
        print(f"⚠️ Only found {trading_days_found} trading days (requested: {days})")
    
    # Reload and verify the data
    existing = load_existing()
    symbol_records = [r for r in existing if r["symbol"] == symbol]
    
    if symbol_records:
        # Sort by date descending
        symbol_records.sort(key=lambda x: x["date"], reverse=True)
        print(f"✅ Backfill completed. Total records for {symbol}: {len(symbol_records)}")
    else:
        print(f"⚠️ No data found for {symbol}")
        
    return trading_days_found > 0


def run_auto_ingest():
    """
    Called on startup. Tries to fetch bhavcopy for the last few business days
    to ensure we have the most recent data.
    """
    print("🚀 Starting auto-ingestion of recent bhavcopy...")
    existing = load_existing()
    today = date.today()
    
    # Try last 15 days to ensure we catch all missing business days
    found_any = False
    for i in range(1, 16):
        target_date = today - timedelta(days=i)
        success = ingest_for_date(target_date, existing)
        if success:
            found_any = True
            print(f"✅ Auto-ingest found data for {target_date}")
    
    if not found_any:
        print("ℹ️ Auto-ingest: No new bhavcopy data found in the last 15 days.")


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    backfill_last_two_months()
