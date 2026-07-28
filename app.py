from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import io
import base64
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

print("Loading CO2 data and generating visualizations...")

url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
df_raw = pd.read_csv(url)

countries_only = df_raw[df_raw['iso_code'].notnull()].copy()
countries_only = countries_only[
    ~countries_only['iso_code'].str.startswith('OWID_') | (countries_only['iso_code'] == 'OWID_KOS')
]

reporting_counts = countries_only.dropna(subset=['co2']).groupby('year').size()
complete_years = reporting_counts[reporting_counts > 150].index
most_recent_complete_year = int(complete_years.max())

world_all = df_raw[
    (df_raw['iso_code'].isin(['OWID_WRL', 'OWID_WLD'])) | 
    (df_raw['country'].isin(['World', 'World Population']))
].sort_values('year')

if len(world_all) == 0:
    world_all = countries_only.groupby('year').agg(
        co2=('co2', 'sum'), co2_per_capita=('co2_per_capita', 'mean'), population=('population', 'sum')
    ).reset_index()

world_available_years = [int(y) for y in world_all['year'].dropna().tolist()]
while most_recent_complete_year not in world_available_years and most_recent_complete_year > 2000:
    most_recent_complete_year -= 1

start_year = most_recent_complete_year - 9
world_data = world_all[(world_all['year'] >= start_year) & (world_all['year'] <= most_recent_complete_year)]
world_recent = world_data[world_data['year'] == most_recent_complete_year].iloc[0]
world_prev = world_data[world_data['year'] == (most_recent_complete_year - 1)].iloc[0]

df_10y = countries_only[(countries_only['year'] >= start_year) & (countries_only['year'] <= most_recent_complete_year)]
recent_year_data = df_10y[df_10y['year'] == most_recent_complete_year]
top_50_iso = recent_year_data.nlargest(50, 'co2')['iso_code'].tolist()
df_top50 = df_10y[df_10y['iso_code'].isin(top_50_iso)].copy()

if 'gdp' in df_top50.columns:
    df_top50['Emissions_Intensity'] = df_top50['co2'] / (df_top50['gdp'] / 1e9)
df_top50.sort_values(by=['iso_code', 'year'], inplace=True)
df_top50['Year_over_Year_Change_Pct'] = df_top50.groupby('iso_code')['co2'].pct_change() * 100

def calculate_cagr(start_val, end_val, periods=9):
    if start_val <= 0 or pd.isna(start_val) or pd.isna(end_val): return np.nan
    return ((end_val / start_val) ** (1/periods) - 1) * 100

start_data = df_top50[df_top50['year'] == start_year][['iso_code', 'co2']]
end_data = df_top50[df_top50['year'] == most_recent_complete_year][['iso_code', 'country', 'co2']]
compliance_df = pd.merge(start_data, end_data, on='iso_code', suffixes=('_start', '_end'))
periods = most_recent_complete_year - start_year
compliance_df['CO2_CAGR'] = compliance_df.apply(lambda r: calculate_cagr(r['co2_start'], r['co2_end'], periods), axis=1)

def classify(cagr):
    if pd.isna(cagr): return "Insufficient Data"
    if cagr < -2.0: return "Ahead of Target"
    elif cagr <= 0.0: return "On Track"
    elif cagr <= 1.0: return "Slightly Off Track"
    elif cagr <= 3.0: return "Significantly Off Track"
    else: return "Critically Off Track"

compliance_df['Compliance_Status'] = compliance_df['CO2_CAGR'].apply(classify)
compliance_df = compliance_df.sort_values('CO2_CAGR')

global_co2 = world_recent['co2']
global_co2_pc = world_recent['co2_per_capita']
global_yoy = ((global_co2 / world_prev['co2']) - 1) * 100 if world_prev['co2'] > 0 else 0

status_colors = {"Ahead of Target":"#22c55e","On Track":"#eab308","Slightly Off Track":"#f97316","Significantly Off Track":"#ef4444","Critically Off Track":"#7f1d1d","Insufficient Data":"#6b7280"}
summary_counts = compliance_df['Compliance_Status'].value_counts().to_dict()
countries = sorted(compliance_df['country'].tolist())

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='#0a0a0f')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    buf.close()
    return img

fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor='#0a0a0f')
ax1.set_facecolor('#0a0a0f')
ax1.plot(world_data['year'], world_data['co2'], color='#3b82f6', marker='o', linewidth=3, markersize=8)
ax1.set_title('Global CO2 Emissions Trajectory', color='white', fontsize=14)
ax1.set_ylabel('Million Tonnes', color='white')
ax1.tick_params(colors='white')
ax1.grid(color='#1f2937', linestyle='--', alpha=0.5)
chart1 = fig_to_b64(fig1)

fig2, ax2 = plt.subplots(figsize=(10, 5), facecolor='#0a0a0f')
ax2.set_facecolor('#0a0a0f')
top15_comp = compliance_df.head(15).sort_values('CO2_CAGR', ascending=True)
ax2.barh(top15_comp['country'], top15_comp['CO2_CAGR'], color=[status_colors.get(s,'#6b7280') for s in top15_comp['Compliance_Status']])
ax2.axvline(x=0, color='white', linewidth=1)
ax2.set_title('Paris Agreement Compliance (Top 15 Emitters)', color='white', fontsize=14)
ax2.set_xlabel('CO2 CAGR (%)', color='white')
ax2.tick_params(colors='white')
ax2.grid(axis='x', color='#1f2937', linestyle='--', alpha=0.5)
chart2 = fig_to_b64(fig2)

print(f"Ready. {len(df_top50)} rows, {len(compliance_df)} countries analyzed.")

PAGE_CSS = """
:root{--bg:#0a0a0f;--card:#12121a;--border:#252540;--text:#e8e8f0;--muted:#9898b0;--green:#22c55e;--red:#ef4444;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif;line-height:1.6;}
.wrap{max-width:1100px;margin:0 auto;padding:40px 24px;}
header{border-bottom:1px solid var(--border);padding-bottom:24px;margin-bottom:32px;}
h1{font-size:2rem;font-weight:700;margin-bottom:6px;}
.sub{color:var(--muted);font-size:14px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:28px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;}
.card .k{font-family:monospace;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);margin-bottom:8px;}
.card .v{font-family:monospace;font-size:28px;font-weight:700;}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:28px 0;}
label{font-family:monospace;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);}
select{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:10px 14px;font-size:15px;min-width:240px;}
.chart-section{margin-top:30px;}
.chart-section h2{color:var(--text);font-size:18px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.chart-section img{width:100%;border-radius:10px;border:1px solid var(--border);margin-bottom:20px;}
.badge{display:inline-block;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;}
footer{margin-top:48px;padding-top:20px;border-top:1px solid var(--border);color:var(--muted);font-size:12px;text-align:center;}
"""

@app.route("/")
def index():
    selected = request.args.get("country", countries[0])
    if selected not in countries: selected = countries[0]
    row = compliance_df[compliance_df['country'] == selected].iloc[0]
    status = row['Compliance_Status']
    cagr = row['CO2_CAGR']
    color = status_colors.get(status, '#6b7280')
    options = "".join(f'<option value="{c}"{" selected" if c == selected else ""}>{c}</option>' for c in countries)
    summary_html = "".join(f'<div class="card"><div class="k">{s}</div><div class="v">{c}</div></div>' for s, c in summary_counts.items())
    
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Carbon Emissions Tracker</title>
<style>{PAGE_CSS}</style>
</head><body><div class="wrap">
<header><h1>Carbon Emissions and Climate Policy Tracker</h1>
<p class="sub">Our World in Data CO2 dataset. {len(compliance_df)} countries from {start_year} to {most_recent_complete_year}.</p></header>
<div class="grid">
  <div class="card"><div class="k">Global CO2 ({most_recent_complete_year})</div><div class="v" style="font-size:22px;">{global_co2:,.0f} Mt</div></div>
  <div class="card"><div class="k">Per Capita</div><div class="v">{global_co2_pc:.2f} <span style="font-size:14px;color:var(--muted);">tonnes</span></div></div>
  <div class="card"><div class="k">YoY Change</div><div class="v" style="color:{'var(--red)' if global_yoy > 0 else 'var(--green)'};">{global_yoy:+.2f}%</div></div>
  <div class="card"><div class="k">Countries</div><div class="v">{len(compliance_df)}</div></div>
</div>
<form method="get" class="controls">
  <label for="country">Country</label>
  <select id="country" name="country" onchange="this.form.submit()">{options}</select>
</form>
<div class="grid">
  <div class="card"><div class="k">Compliance Status</div><div style="margin-top:6px;"><span class="badge" style="background:{color}20;color:{color};border:1px solid {color}40;">{status}</span></div></div>
  <div class="card"><div class="k">CO2 CAGR (10yr)</div><div class="v" style="font-size:22px;color:{color};">{cagr:+.2f}%</div></div>
</div>
<div class="chart-section"><h2>Global CO2 Emissions Trajectory</h2><img src="data:image/png;base64,{chart1}" alt="Global CO2 Trend"></div>
<div class="chart-section"><h2>Paris Agreement Compliance (Top 15)</h2><img src="data:image/png;base64,{chart2}" alt="Paris Compliance"></div>
<footer>Data: Our World in Data CO2 Dataset | Sources: Global Carbon Project, BP, UNFCCC | {len(compliance_df)} countries tracked</footer>
</div></body></html>"""

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
