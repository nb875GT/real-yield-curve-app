import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fredapi import Fred

# Load FRED API key from Streamlit secrets
fred = Fred(api_key=st.secrets["fred_api_key"])

# Define FRED series IDs for real yields
series_ids = {
    "5yr": "DFII5",
    "7yr": "DFII7",
    "10yr": "DFII10",
    "20yr": "DFII20",
    "30yr": "DFII30"
}

def get_nearest_yield(series_id, target_date, max_days=10):
    """Return the closest yield value to a target date, searching ±max_days."""
    for offset in range(max_days + 1):
        for direction in [-1, 1]:
            check_date = target_date + timedelta(days=offset * direction)
            try:
                val = fred.get_series(series_id, check_date, check_date)
                if not val.empty:
                    return float(val.values[0])
            except Exception:
                continue
    return None

# Set up the dates
today = datetime.today()
this_monday = today - timedelta(days=today.weekday())
last_monday = this_monday - timedelta(weeks=1)
ytd_start = datetime(today.year, 1, 1)

# Format date labels
label_today = this_monday.strftime('%m/%d/%Y')
label_last = last_monday.strftime('%m/%d/%Y')
label_ytd = ytd_start.strftime('%m/%d/%Y')

# Retrieve and structure the data
maturities = []
yields_ytd = []
yields_last = []
yields_today = []

for maturity, series_id in series_ids.items():
    maturities.append(maturity)
    yields_ytd.append(get_nearest_yield(series_id, ytd_start))
    yields_last.append(get_nearest_yield(series_id, last_monday))
    yields_today.append(get_nearest_yield(series_id, this_monday))

# Build dataframe
real_yields_df = pd.DataFrame({
    'Maturity': maturities,
    label_ytd: yields_ytd,
    label_last: yields_last,
    label_today: yields_today
})
real_yields_df["Weekly Change"] = (
    real_yields_df[label_today] - real_yields_df[label_last]
).round(2)

# Streamlit display
st.title("Real Yields on US Treasury Securities")
st.caption("YTD and Week-over-Week Real Yield Movement | Data: FRED")

# Yield Curve Plot
plt.style.use("dark_background")
fig, ax = plt.subplots()
ax.plot(real_yields_df["Maturity"], real_yields_df[label_ytd], label=f"Real Yield ({label_ytd})", marker='o')
ax.plot(real_yields_df["Maturity"], real_yields_df[label_last], label=f"Real Yield ({label_last})", marker='s')
ax.plot(real_yields_df["Maturity"], real_yields_df[label_today], label=f"Real Yield ({label_today})", marker='^')
ax.set_title("Real Yield Curve")
ax.set_ylabel("Real Yield (%)")
ax.legend()
st.pyplot(fig)

# Data Table Output
st.subheader("Real Yield Weekly Change")
st.dataframe(real_yields_df)
