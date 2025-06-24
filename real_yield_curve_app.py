import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests

# Streamlit layout
st.set_page_config(page_title="Real Yield Curve", layout="wide")
st.title("Real Yields on US Treasury Securities")
st.caption("Real yield data pulled from FRED: YTD, current week, and previous week")

# FRED API key
FRED_API_KEY = '1f7c12c2608de8d360efcc8c4e7febda'  # Replace with your actual FRED API key

# Define FRED series for real yields
fred_series = {
    "5 Yr": "DFII5",
    "7 Yr": "DFII7",
    "10 Yr": "DFII10",
    "20 Yr": "DFII20",
    "30 Yr": "DFII30"
}

# Define date points
today = datetime.today()
current_week = today - timedelta(days=today.weekday())
last_week = current_week - timedelta(days=7)
year_start = datetime(today.year, 1, 1)

# Format for labels
date_label_1 = year_start.strftime("%m/%d/%Y")
date_label_2 = last_week.strftime("%m/%d/%Y")
date_label_3 = current_week.strftime("%m/%d/%Y")

# Fetch FRED data
def fetch_fred_yield(series_id, date):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": (date - timedelta(days=10)).strftime('%Y-%m-%d'),
        "observation_end": (date + timedelta(days=10)).strftime('%Y-%m-%d')
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        observations = data.get("observations", [])
        # Find closest non-null observation
        for obs in observations:
            value = obs.get("value")
            if value not in [".", None]:
                return round(float(value), 2)
        return None
    except Exception as e:
        st.warning(f"FRED API error for {series_id} on {date.strftime('%Y-%m-%d')}: {e}")
        return None

# Build DataFrame
data = {
    "Maturity": [],
    date_label_1: [],
    date_label_2: [],
    date_label_3: []
}

for maturity, series_id in fred_series.items():
    data["Maturity"].append(maturity)
    data[date_label_1].append(fetch_fred_yield(series_id, year_start))
    data[date_label_2].append(fetch_fred_yield(series_id, last_week))
    data[date_label_3].append(fetch_fred_yield(series_id, current_week))

real_yields_df = pd.DataFrame(data)
real_yields_df["Weekly Change"] = (real_yields_df[date_label_3] - real_yields_df[date_label_2]).round(2)
real_yields_df["YTD Change"] = (real_yields_df[date_label_3] - real_yields_df[date_label_1]).round(2)

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

ax.plot(real_yields_df["Maturity"], real_yields_df[date_label_1], marker='o', color='skyblue', label=f"{date_label_1} (YTD Start)")
ax.plot(real_yields_df["Maturity"], real_yields_df[date_label_2], marker='s', color='orange', label=f"{date_label_2} (Last Week)")
ax.plot(real_yields_df["Maturity"], real_yields_df[date_label_3], marker='^', color='lime', label=f"{date_label_3} (This Week)")

# Annotate week-over-week change
for i, row in real_yields_df.iterrows():
    ax.text(row["Maturity"], row[date_label_2] + 0.05,
            f"{row['Weekly Change']:+.2f}", ha='center', fontsize=9, color='white')

# Styling
ax.set_title("Real Yield Curve (FRED Data)", color='white', fontsize=16)
ax.set_xlabel("Maturity (Years)", color='white')
ax.set_ylabel("Real Yield (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)

legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

st.pyplot(fig)
st.dataframe(real_yields_df.set_index("Maturity"))




