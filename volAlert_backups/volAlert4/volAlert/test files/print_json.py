import json


out_file = r"C:\Users\SMARTTOUCH\Downloads\contracts_nsefo.json"


with open(out_file, 'rb') as f:
    data = json.load(f)

    print(json.dumps(data, indent=4))