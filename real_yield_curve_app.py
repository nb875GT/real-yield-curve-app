import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fredapi import Fred

# -- Config
st.set_page_config(page_title="Real Yield Curve", layout="wide")
st.title("Real Yields on US Treasury Securities")
st.caption("YTD and Week-over-Week Real Yield Movement | Data: FRED")

# -- API Key
fred = Fred(api_key=st.secrets["fred_api_key"])  # or replace with your key in development

# -- Define FRED series IDs for TIPS yields
series_ids = {
    "5 Yr": "DFII5",
    "7 Yr": "DFII7",
    "10 Yr": "DFII10",
    "20 Yr": "DFII20",
    "30 Yr": "DFII30"
}

# -- Target dates
today = datetime.today()
label_ytd = "01/01/2025"
label_ww1 = (today - timedelta(days=7)).strftime("%m/%d/%Y")
label_ww2 = (today - timedelta(days=14)).strftime("%m/%d/%Y")

# -- Fetch nearest real yield data for each date
def get_nearest_yield(series_id, ref_date):
    data = fred.get_series(series_id)
    df = pd.DataFrame(data).dropna()
    df.index = pd.to_datetime(df.index)
    nearest_date = df.index[df.index.get_indexer([ref_date], method='nearest')[0]]
    return df.loc[nearest_date]

# -- Build dataframe
data = { "Maturity": [] }
labels = { "YTD": label_ytd, "W/W -1": label_ww1, "W/W -2": label_ww2 }

for label, date_str in labels.items():
    data[label] = []

# Populate yield data
for maturity, series_id in series_ids.items():
    data["Maturity"].append(maturity)
    for label, date_str in labels.items():
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        yield_val = get_nearest_yield(series_id, date_obj)
        data[label].append(round(float(yield_val), 2))

# Create DataFrame
real_yields_df = pd.DataFrame(data)

# Calculate week-over-week change
real_yields_df["W/W Change"] = (real_yields_df["W/W -1"] - real_yields_df["W/W -2"]).round(2)

# -- Plotting
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Plot lines
ax.plot(real_yields_df["Maturity"], real_yields_df["YTD"], marker='o', color='deepskyblue', label=f"Real Yield ({label_ytd})")
ax.plot(real_yields_df["Maturity"], real_yields_df["W/W -2"], marker='s', color='orange', label=f"Real Yield ({label_ww2})")
ax.plot(real_yields_df["Maturity"], real_yields_df["W/W -1"], marker='^', color='lime', label=f"Real Yield ({label_ww1})")

# Annotate change
for i, row in real_yields_df.iterrows():
    ax.text(row["Maturity"], row["W/W -2"] + 0.05,
            f"{row['W/W Change']:+.2f}", ha='center', fontsize=9, color='white')

# Style
ax.set_title("Real Yield Curve", color='white', fontsize=18)
ax.set_xlabel("Maturity (Years)", color='white')
ax.set_ylabel("Real Yield (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.4)

# Legend
legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

# Show chart
st.pyplot(fig)
