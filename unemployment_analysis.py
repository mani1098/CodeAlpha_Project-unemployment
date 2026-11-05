"""Unemployment analysis for India (CMIE data): cleaning, exploration, Covid-19 impact, seasonality.

Usage: python3 -I unemployment_analysis.py <data_dir> <out_dir>
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

data_dir = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)

RATE, EMP, LPR = "Unemployment Rate (%)", "Employed", "Labour Participation Rate (%)"


def clean(df):
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Estimated Unemployment Rate (%)": RATE,
        "Estimated Employed": EMP,
        "Estimated Labour Participation Rate (%)": LPR,
    })
    df = df.dropna(how="all").copy()
    for c in df.select_dtypes("object"):
        df[c] = df[c].str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df["Month"] = df["Date"].dt.to_period("M")
    return df


# ---------- 1. Load & clean ----------
a = pd.read_csv(data_dir / "Unemployment_in_India.csv", encoding="utf-8-sig")
raw_a = len(a)
a = clean(a).drop_duplicates()
b = pd.read_csv(data_dir / "Unemployment_Rate_upto_11_2020.csv", encoding="utf-8-sig")
b.columns = [c.strip() for c in b.columns]
b = b.rename(columns={b.columns[6]: "Zone"})            # duplicate 'Region' column = macro region
b = b.drop(columns=["longitude", "latitude"])           # columns are swapped in the source; not needed
b = clean(b)
b["Frequency"] = "Monthly"

print(f"Dataset A: {raw_a} raw rows -> {len(a)} after dropping blank rows; "
      f"{a['Date'].min():%b %Y} to {a['Date'].max():%b %Y}; {a['Region'].nunique()} states; areas={sorted(a['Area'].unique())}")
print(f"Dataset B: {len(b)} rows; {b['Date'].min():%b %Y} to {b['Date'].max():%b %Y}; {b['Region'].nunique()} states")
print("Missing values A:", a.isna().sum().sum(), "| B:", b.isna().sum().sum())
print("Rate range A:", a[RATE].min(), a[RATE].max(), "| B:", b[RATE].min(), b[RATE].max())

# Zone lookup (from B) applied to A
zone = b.drop_duplicates("Region").set_index("Region")["Zone"]
a["Zone"] = a["Region"].map(zone)
print("States in A without zone:", sorted(a.loc[a["Zone"].isna(), "Region"].unique()))


def national(df):
    """Labour-force weighted national rate: sum(unemployed) / sum(labour force)."""
    d = df.copy()
    d["Unemp"] = d[EMP] * d[RATE] / (100 - d[RATE])
    g = d.groupby("Month").agg(Emp=(EMP, "sum"), Unemp=("Unemp", "sum"))
    g["Rate"] = 100 * g["Unemp"] / (g["Unemp"] + g["Emp"])
    return g


# ---------- 2. National trend ----------
nat_a = national(a)
nat_b = national(b)
nat_a.to_csv(out / "national_monthly_2019_2020_areaSplit.csv")
nat_b.to_csv(out / "national_monthly_2020_stateLevel.csv")
print("\nNational weighted rate, dataset B (states, Jan-Oct 2020):")
print(nat_b["Rate"].round(2).to_string())
print("\nNational weighted rate, dataset A (Rural+Urban, May 2019-Jun 2020):")
print(nat_a["Rate"].round(2).to_string())

fig, ax = plt.subplots(figsize=(11, 5))
xa = nat_a.index.to_timestamp()
xb = nat_b.index.to_timestamp()
ax.plot(xa, nat_a["Rate"], marker="o", label="Dataset A (rural+urban, to Jun 2020)")
ax.plot(xb, nat_b["Rate"], marker="s", label="Dataset B (state level, Jan-Oct 2020)")
ax.axvspan(pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31"), color="red", alpha=0.1, label="Strict lockdown (approx.)")
ax.set(title="Unemployment rate in India (labour-force weighted)", ylabel="%", xlabel="")
ax.legend()
fig.autofmt_xdate()
fig.tight_layout(); fig.savefig(out / "01_national_trend.png", dpi=150); plt.close(fig)

# ---------- 3. Covid impact (dataset B, Jan-Oct 2020) ----------
def phase(m):
    m = m.to_timestamp()
    if m <= pd.Timestamp("2020-03-01"): return "1 Pre-Covid (Jan-Mar)"
    if m <= pd.Timestamp("2020-05-01"): return "2 Lockdown (Apr-May)"
    return "3 Recovery (Jun-Oct)"

b["Phase"] = b["Month"].map(phase)
ph = b.groupby("Phase").apply(lambda d: pd.Series({
    "avg_rate_weighted": 100 * (d[EMP] * d[RATE] / (100 - d[RATE])).sum() /
        ((d[EMP] * d[RATE] / (100 - d[RATE])).sum() + d[EMP].sum()),
    "avg_LPR": d[LPR].mean()}), include_groups=False)
print("\nPhase summary (B):\n", ph.round(2))

pre = b[b["Phase"].str.startswith("1")].groupby("Region")[[RATE, EMP, LPR]].mean()
lock = b[b["Month"].isin([pd.Period("2020-04"), pd.Period("2020-05")])].groupby("Region")[[RATE, EMP, LPR]].mean()
oct_ = b[b["Month"] == pd.Period("2020-10")].set_index("Region")[[RATE, EMP, LPR]]
peak = b.loc[b.groupby("Region")[RATE].idxmax(), ["Region", "Month", RATE]].set_index("Region")
imp = pd.DataFrame({
    "pre_rate": pre[RATE], "lockdown_rate": lock[RATE], "oct_rate": oct_[RATE],
    "rate_change_pp": lock[RATE] - pre[RATE],
    "recovery_gap_pp": oct_[RATE] - pre[RATE],
    "employed_drop_pct": 100 * (lock[EMP] / pre[EMP] - 1),
    "peak_month": peak["Month"].astype(str), "peak_rate": peak[RATE],
}).sort_values("rate_change_pp", ascending=False)
imp.round(2).to_csv(out / "state_covid_impact.csv")
print("\nTop 8 states by rise in unemployment rate (lockdown vs pre-Covid, pp):\n", imp.head(8).round(1).to_string())
print("\nBottom 5:\n", imp.tail(5).round(1).to_string())

emp_nat = b.groupby("Month")[EMP].sum()
print("\nTotal employed (B states, millions):\n", (emp_nat / 1e6).round(1).to_string())
print(f"Employed drop Mar->Apr 2020: {100*(emp_nat[pd.Period('2020-04')]/emp_nat[pd.Period('2020-03')]-1):.1f}%")

# Bar chart top 12
top = imp.head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top.index, top["pre_rate"], label="Pre-Covid avg (Jan-Mar)")
ax.barh(top.index, top["rate_change_pp"], left=top["pre_rate"], color="firebrick", label="Increase during lockdown (Apr-May avg)")
ax.set(title="States most hit: unemployment rate before vs during lockdown", xlabel="Unemployment rate (%)")
ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(out / "02_state_covid_impact.png", dpi=150); plt.close(fig)

# Heatmap
pv = b.pivot(index="Region", columns="Month", values=RATE)
pv = pv.loc[imp.index]
pv.columns = [str(c) for c in pv.columns]
fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(pv, cmap="YlOrRd", annot=True, fmt=".0f", cbar_kws={"label": "Unemployment rate (%)"}, ax=ax, annot_kws={"size": 7})
ax.set(title="State-wise unemployment rate by month, 2020 (sorted by lockdown impact)", ylabel="", xlabel="")
fig.tight_layout(); fig.savefig(out / "03_state_heatmap.png", dpi=150); plt.close(fig)

# Zone view
zt = b.groupby(["Zone", "Month"]).apply(lambda d: 100 * (d[EMP] * d[RATE] / (100 - d[RATE])).sum() /
        ((d[EMP] * d[RATE] / (100 - d[RATE])).sum() + d[EMP].sum()), include_groups=False).unstack(0)
zt.to_csv(out / "zone_monthly_2020.csv")
print("\nZone weighted rates 2020:\n", zt.round(1).to_string())
fig, ax = plt.subplots(figsize=(10, 5))
for z in zt.columns:
    ax.plot(zt.index.to_timestamp(), zt[z], marker="o", label=z)
ax.set(title="Unemployment rate by zone, 2020", ylabel="%"); ax.legend(); fig.autofmt_xdate()
fig.tight_layout(); fig.savefig(out / "04_zone_trend.png", dpi=150); plt.close(fig)

# ---------- 4. Rural vs Urban (dataset A) ----------
ru = a.groupby(["Area", "Month"]).apply(lambda d: 100 * (d[EMP] * d[RATE] / (100 - d[RATE])).sum() /
        ((d[EMP] * d[RATE] / (100 - d[RATE])).sum() + d[EMP].sum()), include_groups=False).unstack(0)
ru.to_csv(out / "rural_urban_monthly.csv")
print("\nRural vs Urban weighted rate (A):\n", ru.round(1).to_string())
fig, ax = plt.subplots(figsize=(10, 5))
for c in ru.columns:
    ax.plot(ru.index.to_timestamp(), ru[c], marker="o", label=c)
ax.axvspan(pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31"), color="red", alpha=0.1)
ax.set(title="Rural vs urban unemployment (to Jun 2020)", ylabel="%"); ax.legend(); fig.autofmt_xdate()
fig.tight_layout(); fig.savefig(out / "05_rural_urban.png", dpi=150); plt.close(fig)

# ---------- 5. Labour participation ----------
lp = b.groupby("Month")[LPR].mean()
print("\nMean LPR by month (B):\n", lp.round(1).to_string())

# ---------- 6. Seasonality / patterns ----------
a_pre = a[a["Date"] < "2020-03-01"]
mon = a_pre.groupby(a_pre["Date"].dt.month).apply(lambda d: 100 * (d[EMP] * d[RATE] / (100 - d[RATE])).sum() /
        ((d[EMP] * d[RATE] / (100 - d[RATE])).sum() + d[EMP].sum()), include_groups=False)
print("\nPre-Covid monthly national rate, May 2019-Feb 2020 (A):\n", mon.round(2).to_string())
print("Pre-Covid range (pp):", round(mon.max() - mon.min(), 2), "| std:", round(mon.std(), 2))

yoy = {}
for m in (5, 6):
    r19 = nat_a.loc[pd.Period(f"2019-{m:02d}"), "Rate"]
    r20 = nat_a.loc[pd.Period(f"2020-{m:02d}"), "Rate"]
    yoy[m] = (r19, r20)
print("Year-on-year (A): ", {k: tuple(round(x, 2) for x in v) for k, v in yoy.items()})

# Volatility: state-level std in pre-covid months
vol = a_pre.groupby("Region")[RATE].agg(["mean", "std"]).sort_values("mean", ascending=False)
print("\nHighest pre-Covid mean unemployment (A):\n", vol.head(6).round(1).to_string())
print("Lowest:\n", vol.tail(4).round(1).to_string())

fig, ax = plt.subplots(figsize=(9, 4.5))
sns.lineplot(x=mon.index, y=mon.values, marker="o", ax=ax)
ax.set(title="Pre-Covid national unemployment by calendar month (May 2019-Feb 2020)", xlabel="Calendar month", ylabel="%")
fig.tight_layout(); fig.savefig(out / "06_pre_covid_monthly.png", dpi=150); plt.close(fig)

# Recovery chart: LPR vs unemployment (B)
fig, ax = plt.subplots(figsize=(9, 5))
sc = ax.scatter(b[LPR], b[RATE], c=b["Month"].map(lambda m: m.month), cmap="viridis", alpha=0.7)
plt.colorbar(sc, label="Month (2020)")
ax.set(title="Labour participation vs unemployment, state-months 2020", xlabel=LPR, ylabel=RATE)
fig.tight_layout(); fig.savefig(out / "07_lpr_vs_unemp.png", dpi=150); plt.close(fig)
print("Corr(LPR, rate) B:", round(b[[LPR, RATE]].corr().iloc[0, 1], 2))

# cleaned data export
a.to_csv(out / "cleaned_dataset_A.csv", index=False)
b.to_csv(out / "cleaned_dataset_B.csv", index=False)
print("\nDone.")
