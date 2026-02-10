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

def ingest_for_date(target_date, existing):
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
                    symbol = row.get("TckrSymb", "").strip()
                    series = row.get("SctySrs", "").strip()

                    if series != "EQ":
                        continue

                    if symbol not in NIFTY_SYMBOLS:
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
        return True

    return False

def run_auto_ingest():
    """
    Called on startup. Tries to fetch bhavcopy for the last few business days
    to ensure we have the most recent data.
    """
    print("🚀 Starting auto-ingestion of recent bhavcopy...")
    existing = load_existing()
    today = date.today()
    
    # Try last 5 days until we find a valid business day bhavcopy
    for i in range(1, 6):
        target_date = today - timedelta(days=i)
        success = ingest_for_date(target_date, existing)
        if success:
            print(f"✅ Auto-ingest successful for {target_date}")
            break
    else:
        print("ℹ️ Auto-ingest: No new bhavcopy data found (already up to date or holiday).")

# =====================================================
# BACKFILL CONTROLLER
# =====================================================

def backfill_last_two_months():
    print("Starting bhavcopy backfill")

    existing = load_existing()

    today = date.today()

    for i in range(1, DAYS_TO_BACKFILL + 1):
        target_date = today - timedelta(days=i)
        ingest_for_date(target_date, existing)

    print("✅ Backfill completed")

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    backfill_last_two_months()
