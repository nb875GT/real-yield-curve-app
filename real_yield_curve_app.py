import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fredapi import Fred

# --- CONFIG ---
st.set_page_config(page_title="Real Yield Curve", layout="wide")
st.title("Real Yields on US Treasury Securities")
st.caption("YTD and Week-over-Week Real Yield Movement | Data: FRED")

# --- API KEY ---
fred = Fred(api_key=st.secrets["fred_api_key"])

# --- SERIES IDS FOR REAL YIELDS FROM FRED ---
series_ids = {
    "5 Yr": "DFII5",
    "7 Yr": "DFII7",
    "10 Yr": "DFII10",
    "20 Yr": "DFII20",
    "30 Yr": "DFII30",
}

# --- DATE LOGIC ---
today = datetime.today()
date_1 = "01/01/2025"
date_2 = (today - timedelta(days=14)).strftime("%m/%d/%Y")  # 1 week ago
latest_date = (today - timedelta(days=7)).strftime("%m/%d/%Y")  # most recent week (with FRED lag)

# --- FETCH DATA ---
real_yields = {"Maturity": []}
labels = ["01/01/2025", date_2, latest_date]

for label in labels:
    real_yields[label] = []

for label, fred_id in series_ids.items():
    real_yields["Maturity"].append(label)
    for date_label in labels:
        date = datetime.strptime(date_label, "%m/%d/%Y")
        try:
            series = fred.get_series(fred_id, start=date - timedelta(days=5), end=date + timedelta(days=5))
            value = series.dropna().iloc[-1] if not series.empty else float("nan")
        except:
            value = float("nan")
        real_yields[date_label].append(value)

# --- BUILD DATAFRAME ---
real_yields_df = pd.DataFrame(real_yields)
real_yields_df["Weekly Change"] = (
    pd.to_numeric(real_yields_df[latest_date], errors="coerce") -
    pd.to_numeric(real_yields_df[date_2], errors="coerce")
).round(2)

# --- PLOTTING ---
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

colors = ['skyblue', 'orange', 'lime']
markers = ['o', 's', '^']

for i, date_label in enumerate(labels):
    ax.plot(real_yields_df["Maturity"], real_yields_df[date_label],
            marker=markers[i], color=colors[i], label=f"Real Yield ({date_label})")

# --- ANNOTATE CHANGE ---
for i, row in real_yields_df.iterrows():
    ax.text(row["Maturity"], row[latest_date] + 0.05,
            f"{row['Weekly Change']:+.2f}", ha='center', fontsize=9, color='white')

# --- STYLE ---
ax.set_title("Real Yield Curve", color='white', fontsize=16)
ax.set_xlabel("Maturity (Years)", color='white')
ax.set_ylabel("Real Yield (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)
legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

st.pyplot(fig)

# --- OPTIONAL TABLE VIEW ---
with st.expander("Show Data Table"):
    st.dataframe(real_yields_df.round(2))




