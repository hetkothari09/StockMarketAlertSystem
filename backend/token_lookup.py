import xml.etree.ElementTree as ET
import os

# # NSECM.xml path (Make sure it exists)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NSE_XML_PATH = os.path.join(BASE_DIR, "data", "NSECM.xml")

# Cache for all symbols
_all_symbols_cache = None

def get_token_details(target_symbol):
    """
    Searches NSECM.xml for the given symbol and returns its details.
    Returns None if not found or file missing.
    """
    if not os.path.exists(NSE_XML_PATH):
        # Check for zip file
        zip_path = NSE_XML_PATH.replace(".xml", ".zip")
        if os.path.exists(zip_path):
            print(f"📦 Unzipping {zip_path}...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(NSE_XML_PATH))
            print(f"✅ Extracted to {NSE_XML_PATH}")
        else:
            print(f"Error: NSECM.xml not found at {NSE_XML_PATH}")
            return None

    target_symbol = target_symbol.strip().upper()
    
    # Check simple cache first if needed? No, user wants on-the-go. 
    # Parsing 500MB might be slow, but let's try iterparse.
    
    try:
        context = ET.iterparse(NSE_XML_PATH, events=('end',))
        
        for event, elem in context:
            if elem.tag.endswith("NSECM"): # Ensure we are looking at correct records
                data = {}
                for child in elem:
                    # Remove namespace if any
                    tag = child.tag.split('}')[-1]
                    data[tag] = (child.text or "").strip()
                
                symbol = data.get('Symbol', '').strip().upper()
                series = data.get('Series', '').strip().upper()

                # ONLY look for Equity series (EQ, BE, BZ etc. usually EQ is main)
                # But let's just match Symbol and return mostly EQ if available
                
                if symbol == target_symbol and series == "EQ":
                    token = data.get('TokenNo')
                    
                    result = {
                        "symbol": symbol,
                        "token": token,
                        "exchange": "NSECM",
                        "series": series
                    }
                    elem.clear()
                    return result

                # Clean up to save memory
                elem.clear()
                
    except Exception as e:
        print(f"Error parsing NSECM.xml: {e}")
        return None

    return None

def get_all_symbols():
    """
    Returns a list of all EQ series symbols from NSECM.xml.
    Results are cached after first call.
    """
    global _all_symbols_cache
    
    # Return cached data if available
    if _all_symbols_cache is not None:
        return _all_symbols_cache
    
    if not os.path.exists(NSE_XML_PATH):
        print(f"Error: NSECM.xml not found at {NSE_XML_PATH}")
        return []
    
    symbols = []
    
    try:
        print("🔍 Parsing NSECM.xml for all symbols (this may take a moment)...")
        context = ET.iterparse(NSE_XML_PATH, events=('end',))
        
        for event, elem in context:
            if elem.tag.endswith("NSECM"):
                data = {}
                for child in elem:
                    tag = child.tag.split('}')[-1]
                    data[tag] = (child.text or "").strip()
                
                symbol = data.get('Symbol', '').strip().upper()
                series = data.get('Series', '').strip().upper()
                
                # Only include EQ (Equity) series
                if series == "EQ" and symbol:
                    token = data.get('TokenNo')
                    name = data.get('Name', symbol)
                    
                    symbols.append({
                        "symbol": symbol,
                        "name": name,
                        "token": token
                    })
                
                elem.clear()
        
        # Cache the results
        _all_symbols_cache = symbols
        print(f"✅ Found {len(symbols)} EQ symbols")
        
    except Exception as e:
        print(f"Error parsing NSECM.xml: {e}")
        return []
    
    return symbols

if __name__ == "__main__":
    # Test
    res = get_token_details("ZOMATO")
    print(res)
