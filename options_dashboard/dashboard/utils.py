import os
from datetime import datetime

# CHANGE THESE
DATA_DIR = r"D:\Pallav\Projects\Options Fiesta\12Dec-Nifty"
SPOT_CSV = r"D:\Pallav\Projects\Options Fiesta\nifty_underlying.csv"

def list_option_files():
    files = []
    for file in os.listdir(DATA_DIR):
        if not file.endswith('.csv'):
            continue

        parts = file.replace('.csv', '').split('_')
        if len(parts) != 3:
            continue

        try:
            strike = int(parts[0])
            opt_type = parts[1].lower()
            expiry = parts[2]
            if opt_type not in ['call', 'put']:
                continue

            files.append({
                'path': os.path.join(DATA_DIR, file),
                'strike': strike,
                'type': opt_type,
                'expiry': expiry,
                'filename': file
            })
        except:
            continue
    return files
