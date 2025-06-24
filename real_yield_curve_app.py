import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fredapi import Fred

# Setup
st.set_page_config(page_title="Real Yield Curve", layout="wide")
st.title("Real Yields on US Treasury Securities")
st.caption("YTD and Week-over-Week Real Yield Movement | Data: FRED")

# Load FRED API key securely from Streamlit secrets
fred = Fred(api_key=st.secrets["fred_api_key"])

# Define FRED series IDs for real yields
series_ids = {
    "5 Yr": "DFII5",
    "7 Yr": "DFII7",
    "10 Yr": "DFII10",
    "20 Yr": "DFII20",
    "30 Yr": "DFII30"
}

# Define key dates
today = datetime.today()
this_week = today - timedelta(days=today.weekday())
last_week = this_week - timedelta(weeks=1)
ytd_date = datetime(today.year, 1, 1)

# Format date labels for plotting
label_ytd = ytd_date.strftime("%m/%d/%Y")
label_last = last_week.strftime("%m/%d/%Y")
label_this = this_week.strftime("%m/%d/%Y")

# Helper to fetch nearest yield to a target date
def get_nearest_yield(series_id, target_date):
    data = fred.get_series(series_id)
    data = data[data.index <= target_date]
    return data.iloc[-1] if not data.empty else None

# Build dataframe
data = {"Maturity": [], label_ytd: [], label_last: [], label_this: []}
for label, series_id in series_ids.items():
    data["Maturity"].append(label)
    data[label_ytd].append(get_nearest_yield(series_id, ytd_date))
    data[label_last].append(get_nearest_yield(series_id, last_week))
    data[label_this].append(get_nearest_yield(series_id, this_week))

real_yields_df = pd.DataFrame(data)

# Calculate weekly change (not percent)
try:
    real_yields_df["Weekly Change"] = (
        real_yields_df[label_this] - real_yields_df[label_last]
    ).round(2)
except Exception as e:
    st.warning(f"Could not compute weekly changes: {e}")

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

ax.plot(real_yields_df["Maturity"], real_yields_df[label_ytd], marker='o', color='skyblue', label=f"Real Yield ({label_ytd})")
ax.plot(real_yields_df["Maturity"], real_yields_df[label_last], marker='s', color='orange', label=f"Real Yield ({label_last})")
ax.plot(real_yields_df["Maturity"], real_yields_df[label_this], marker='^', color='lime', label=f"Real Yield ({label_this})")

# Annotate changes
for i, row in real_yields_df.iterrows():
    ax.text(row["Maturity"], row[label_last] + 0.05,
            f"{row['Weekly Change']:+.2f}" if pd.notnull(row['Weekly Change']) else "",
            ha='center', fontsize=9, color='white')

# Style
ax.set_title("Real Yield Curve", color='white', fontsize=16)
ax.set_xlabel("Maturity", color='white')
ax.set_ylabel("Real Yield (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)
legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

st.pyplot(fig)

# Optional: View table
with st.expander("Show Raw Data Table"):
    st.dataframe(real_yields_df.set_index("Maturity").round(3))




