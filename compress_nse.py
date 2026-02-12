import zipfile
import os

source = "backend/data/NSECM.xml"
dest = "backend/data/NSECM.zip"

if os.path.exists(source):
    print(f"Compressing {source} to {dest}...")
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(source, arcname="NSECM.xml")
    print("Compression complete.")
    fs = os.path.getsize(dest)
    print(f"New size: {fs / (1024*1024):.2f} MB")
else:
    print(f"Source file {source} not found!")
