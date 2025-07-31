import pandas as pd
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .utils import list_option_files, SPOT_CSV
from .greeks import compute_greeks
from .iv import implied_volatility

def dashboard(request):
    files = list_option_files()
    expiry = files[0]['expiry'] if files else 'Unknown'
    return render(request, 'dashboard2.html', {'expiry': expiry})

def get_greeks(request):
    print("getting greeks...")
    r = float(request.GET.get('r', 0.15))
    files = list_option_files()
    spot_df = pd.read_csv(SPOT_CSV, parse_dates=['datetime'])

    # Round spot datetimes to exact minute
    spot_df['datetime'] = pd.to_datetime(spot_df['datetime']).dt.round('min')

    # Target times per day
    allowed_times = ['09:15', '10:15', '11:15', '12:15', '13:15', '15:15']

    result = {}

    for f in files:
        option_df = pd.read_csv(f['path'], parse_dates=['datetime'])
        option_df['datetime'] = pd.to_datetime(option_df['datetime']).dt.round('min')
        option_df['time_only'] = option_df['datetime'].dt.strftime('%H:%M')
        option_df['date_only'] = option_df['datetime'].dt.date

        # Filter only selected timestamps
        option_filtered = option_df[option_df['time_only'].isin(allowed_times)]

        # Remove duplicates (e.g., if multiple same time rows)
        option_filtered = option_filtered.drop_duplicates(subset=['datetime'])

        # Merge with spot
        merged = pd.merge(option_filtered, spot_df[['datetime', 'close']], on='datetime', how='inner', suffixes=('', '_spot'))
        greeks_data = []

        for _, row in merged.iterrows():
            S = row['close_spot']
            K = f['strike']
            T = (datetime.strptime(f['expiry'], "%Y-%m-%d") - row['datetime']).days / 365
            if T <= 0: continue

            premium = row['close']
            iv = implied_volatility(S, K, T, r, premium, f['type'])
            if pd.isna(iv): continue

            g = compute_greeks(S, K, T, r, iv, f['type'])
            g['datetime'] = row['datetime'].strftime('%Y-%m-%d %H:%M')
            greeks_data.append(g)

        result[f"{f['strike']}_{f['type']}"] = greeks_data
        print("greeks for", f['strike'], f['type'], "done")

    return JsonResponse({'data': result})


def get_ivs(request):
    spot = float(request.GET.get('spot', 0))
    r = float(request.GET.get('r', 0.15))
    files = list_option_files()
    data = {'call': [], 'put': []}

    for f in files:
        df = pd.read_csv(f['path'])
        close_price = df['close'].iloc[0]
        expiry = datetime.strptime(f['expiry'], "%Y-%m-%d")
        now = df['datetime'].iloc[0]
        T = (expiry - datetime.strptime(now[:10], "%Y-%m-%d")).days / 365
        iv = implied_volatility(spot, f['strike'], T, r, close_price, f['type'])
        if pd.isna(iv): continue
        data[f['type']].append({
            'strike': f['strike'],
            'time': round(T, 4),
            'iv': round(iv, 4)
        })

    return JsonResponse(data)
