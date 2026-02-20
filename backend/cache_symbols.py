import json
import os
import token_lookup

# We will generate a lightweight JSON from the large XML
output_path = os.path.join(os.path.dirname(__file__), "data", "all_symbols.json")

print("Generating cached symbols from XML...")
symbols = token_lookup.get_all_symbols()

if symbols:
    with open(output_path, "w") as f:
        json.dump(symbols, f)
    print(f"Successfully cached {len(symbols)} symbols to {output_path}")
else:
    print("Failed to extract symbols")
