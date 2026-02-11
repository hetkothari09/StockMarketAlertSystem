import xml.etree.ElementTree as ET
import os

# NSECM.xml path (Make sure it exists)
NSE_XML_PATH = r"C:\Users\SMARTTOUCH\Downloads\NSECM.xml"

def get_token_details(target_symbol):
    """
    Searches NSECM.xml for the given symbol and returns its details.
    Returns None if not found or file missing.
    """
    if not os.path.exists(NSE_XML_PATH):
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

if __name__ == "__main__":
    # Test
    res = get_token_details("ZOMATO")
    print(res)
