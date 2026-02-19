import requests
import datetime

target_date = datetime.date(2026, 2, 13)
date_str = target_date.strftime("%Y%m%d")

bhavcopy_url = (
    "https://nsearchives.nseindia.com/content/cm/"
    f"BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

print(f"Testing URL: {bhavcopy_url}")
try:
    r = requests.get(bhavcopy_url, headers=HEADERS, timeout=15)
    print(f"Status Code: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Content-Length: {len(r.content)} bytes")
    
    if r.status_code == 200:
        print("✅ Download successful!")
    else:
        print("❌ Download failed.")
except Exception as e:
    print(f"❌ Exception: {e}")
