import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set up Streamlit layout
st.set_page_config(page_title="Real Yield Curve", layout="wide")
st.title("Real Yields on US Treasury Securities")
st.caption("Manually input real yields for 01/01/2025, 03/28/2025, and 04/04/2025")

# Define maturities
maturities = ["5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr"]

# ------------------------------
# 🔢 MANUAL REAL YIELD INPUTS
# ------------------------------

# Real yields on each date (replace values here as needed)
yields_0101 = {
    "5 Yr": 2.00,
    "7 Yr": 2.13,
    "10 Yr": 2.24,
    "20 Yr": 2.41,
    "30 Yr": 2.48
}

yields_0328 = {
    "5 Yr": 1.40,
    "7 Yr": 1.68,
    "10 Yr": 1.90,
    "20 Yr": 2.22,
    "30 Yr": 2.37
}

yields_0404 = {
    "5 Yr": 1.38,
    "7 Yr": 1.63,
    "10 Yr": 1.83,
    "20 Yr": 2.14,
    "30 Yr": 2.28
}

# Build dataframe
real_yields_df = pd.DataFrame({
    "Maturity": maturities,
    "01/01/2025": [yields_0101[m] for m in maturities],
    "03/28/2025": [yields_0328[m] for m in maturities],
    "04/04/2025": [yields_0404[m] for m in maturities],
})

# Week-over-week nominal change (not %)
real_yields_df["Weekly Change"] = (
    real_yields_df["03/28/2025"] - real_yields_df["04/04/2025"]
).round(2)

# ------------------------------
# 📊 Plotting
# ------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# Plot each curve
ax.plot(real_yields_df["Maturity"], real_yields_df["01/01/2025"], marker='o', color='skyblue', label="Real Yield (01/01/2025)")
ax.plot(real_yields_df["Maturity"], real_yields_df["03/28/2025"], marker='s', color='orange', label="Real Yield (03/28/2025)")
ax.plot(real_yields_df["Maturity"], real_yields_df["04/04/2025"], marker='^', color='lime', label="Real Yield (04/04/2025)")

# Annotate nominal week-over-week change
for i, row in real_yields_df.iterrows():
    ax.text(row["Maturity"], row["03/28/2025"] + 0.05,
            f"{row['Weekly Change']:+.2f}", ha='center', fontsize=9, color='white')

# Style
ax.set_title("Real Yield Curve", color='white', fontsize=16)
ax.set_xlabel("Maturity (Years)", color='white')
ax.set_ylabel("Real Yield (%)", color='white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)

# Legend styling
legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")

# Show chart
st.pyplot(fig)




