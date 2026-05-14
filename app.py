"""
Medical History Dashboard
A web application to visualize and track medical history data with trend analysis.
Data sourced from MEDICAL_HISTORY_TABLE.md (2026 post-transplant records).
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Medical History Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { background-color: #ffffff; }
    h1 { color: #2c3e50; font-weight: 600; }
    h2 { color: #34495e; }
    .overview-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .overview-card h4 { margin: 0 0 10px 0; color: #2c3e50; }
    .overview-card .value { font-size: 28px; font-weight: bold; }
    .overview-card .date { color: #7f8c8d; font-size: 13px; margin-top: 5px; }
    .overview-card .trend { font-size: 14px; margin-top: 8px; }
    .vitals-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .vital-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .vital-card .label { font-size: 13px; opacity: 0.9; }
    .vital-card .value { font-size: 24px; font-weight: bold; }
    .info-box {
        background-color: #f0f7fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #3498db;
    }
    .info-box h4 { margin-top: 0; color: #2c3e50; }
    .info-box p { margin: 8px 0; color: #555; }
    .info-box ul { margin: 10px 0; padding-left: 20px; }
    .info-box li { margin: 5px 0; color: #555; }
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    .summary-table th, .summary-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    .summary-table th {
        background-color: #3498db;
        color: white;
    }
    .summary-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .procedure-bold {
        font-weight: 600;
        color: #2c3e50;
    }
    .dose-stop {
        color: #e74c3c;
        font-weight: bold;
    }

    /* ── Vertical Timeline ── */
    .tl-wrapper {
        position: relative;
        padding-left: 36px;
        margin-top: 10px;
    }
    .tl-wrapper::before {
        content: '';
        position: absolute;
        left: 10px;
        top: 8px;
        bottom: 8px;
        width: 2px;
        background: #e0e0e0;
        border-radius: 2px;
    }
    .tl-item {
        position: relative;
        margin-bottom: 12px;
    }
    .tl-dot {
        position: absolute;
        left: -30px;
        top: 10px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0 0 0 2px currentColor;
    }
    .tl-dot-surgery  { color: #378ADD; background: #378ADD; }
    .tl-dot-biopsy   { color: #E24B4A; background: #E24B4A; }
    .tl-dot-injection { color: #BA7517; background: #BA7517; }
    .tl-dot-followup { color: #1D9E75; background: #1D9E75; }
    .tl-dot-discharge { color: #534AB7; background: #534AB7; }
    .tl-dot-lab      { color: #D4537E; background: #D4537E; }

    .tl-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        gap: 14px;
        align-items: flex-start;
        transition: box-shadow 0.15s;
    }
    .tl-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
    .tl-date-col {
        min-width: 88px;
        font-size: 12px;
        color: #888;
        padding-top: 2px;
        line-height: 1.5;
    }
    .tl-date-col strong { display: block; font-size: 13px; color: #555; font-weight: 600; }
    .tl-content { flex: 1; }
    .tl-title {
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        line-height: 1.4;
        margin-bottom: 4px;
    }
    .tl-sub {
        font-size: 12px;
        color: #666;
        line-height: 1.5;
        margin-bottom: 6px;
    }
    .tl-pills { display: flex; flex-wrap: wrap; gap: 6px; }
    .tl-pill {
        font-size: 11px;
        padding: 2px 9px;
        border-radius: 99px;
        font-weight: 500;
        white-space: nowrap;
    }
    .pill-blue   { background: #E6F1FB; color: #185FA5; }
    .pill-red    { background: #FCEBEB; color: #A32D2D; }
    .pill-amber  { background: #FAEEDA; color: #854F0B; }
    .pill-teal   { background: #E1F5EE; color: #0F6E56; }
    .pill-purple { background: #EEEDFE; color: #3C3489; }
    .pill-pink   { background: #FBEAF0; color: #72243E; }
    .pill-gray   { background: #F1EFE8; color: #5F5E5A; }
    .tl-badge {
        display: inline-block;
        font-size: 10px;
        padding: 1px 8px;
        border-radius: 99px;
        font-weight: 600;
        margin-left: 8px;
        vertical-align: middle;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-surgery  { background: #E6F1FB; color: #185FA5; }
    .badge-biopsy   { background: #FCEBEB; color: #A32D2D; }
    .badge-injection { background: #FAEEDA; color: #854F0B; }
    .badge-followup { background: #E1F5EE; color: #0F6E56; }
    .badge-discharge { background: #EEEDFE; color: #3C3489; }
    .badge-lab      { background: #FBEAF0; color: #72243E; }
    .tl-month-divider {
        font-size: 12px;
        font-weight: 700;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 20px 0 10px -36px;
        padding-left: 36px;
        border-bottom: 1px solid #eee;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# DATA — sourced directly from MEDICAL_HISTORY_TABLE.md
# Columns: Date | Procedure / Event | Creatinine | Tacrolimus Level |
#          Everolimus Level | Tacrolimus Dose | Everolimus Dose
# ---------------------------------------------------------------------------
RAW_RECORDS = [
    ("07 Jan 2026", "Renal Kidney Transplant — Major transplant surgery performed", None, None, None, None, None),
    ("07 Jan 2026", "ATG Dose 1", 1.22, None, None, None, None),
    ("09 Jan 2026", "ATG Dose 2", 1.28, None, None, None, None),
    ("13 Jan 2026", "Discharge — Patient discharged post-transplant", 1.25, None, None, None, None),
    ("16 Jan 2026", "1st Visit After Transplant", 1.58, None, None, 4.0, None),
    ("19 Jan 2026", "2nd Visit — Dilzem medicine added", 1.73, 4.11, None, 5.0, None),
    ("20 Jan 2026", "Transplant Kidney Biopsy", 1.74, None, None, 5.0, None),
    ("21 Jan 2026", "Biopsy Report Reviewed — Mild interstitial inflammation with mild tubulitis; borderline Acute T-Cell Mediated Rejection suspected", 1.74, None, None, 5.0, None),
    ("22 Jan 2026", "Inj. Solumedrol 500 MG — Dose 1", None, None, None, 5.0, None),
    ("23 Jan 2026", "Inj. Solumedrol 500 MG — Dose 2", 1.93, None, None, 5.0, None),
    ("24 Jan 2026", "Urine Culture — E. Coli Detected (sensitivity noted; treatment started at 2:00 PM)", 1.94, 9.2, None, 5.0, None),
    ("24 Jan 2026", "Inj. Zavicefta 2.5 GM IV STAT → followed by 1.25 GM three times daily", None, None, None, None, None),
    ("24 Jan 2026", "Inj. Aztreonam 2 GM IV STAT → followed by 2 GM three times daily", None, None, None, None, None),
    ("27 Jan 2026", "Follow-Up — Suggested to continue dose for 10 days", 1.68, None, None, 5.0, None),
    ("30 Jan 2026", "Routine Follow-Up", 1.41, None, None, 5.0, None),
    ("03 Feb 2026", "3rd Visit — Stent removal appointment scheduled", 1.45, 8.1, None, 5.0, None),
    ("05 Feb 2026", "Stent Removal Surgery — Performed successfully", None, None, None, None, None),
    ("07 Feb 2026", "Routine Follow-Up", 1.64, 12.1, None, 5.0, None),
    ("12 Feb 2026", "Routine Follow-Up", 1.67, None, None, 4.0, None),
    ("16 Feb 2026", "Routine Follow-Up", 1.87, None, None, 5.0, None),
    ("18 Feb 2026", "Routine Follow-Up", 2.05, None, None, 3.5, None),
    ("21 Feb 2026", "Routine Follow-Up", 1.87, None, None, 3.5, None),
    ("25 Feb 2026", "Transplant Kidney Biopsy (2nd)", 1.97, 10.1, None, 2.5, None),
    ("02 Mar 2026", "Biopsy Report Reviewed — Mild acute tubular injury; no evidence of rejection", 1.93, None, None, 2.5, None),
    ("07 Mar 2026", "Routine Follow-Up", 2.22, None, None, 2.5, None),
    ("10 Mar 2026", "Certican (Everolimus) 0.75 MG Initiated — Tacrolimus stopped", 2.02, None, None, "STOP", 0.75),
    ("14 Mar 2026", "Tacrolimus (Takfa) Discontinued — As per physician direction", 1.84, None, None, None, 0.75),
    ("23 Mar 2026", "Routine Follow-Up", 1.81, None, None, None, 0.75),
    ("31 Mar 2026", "Routine Follow-Up", 1.77, None, 4.4, None, 1.0),
    ("06 Apr 2026", "Routine Follow-Up", 1.75, None, None, None, 1.0),
    ("20 Apr 2026", "Tacrolimus (Takfa) Restarted — As per updated treatment plan", 1.80, None, 5.66, 1.0, 1.0),
    ("24 Apr 2026", "BKV Virus PCR Quantitative — ✅ NOT DETECTED", 1.88, None, None, 1.0, 1.0),
    ("27 Apr 2026", "Transplant Kidney Biopsy (3rd)", 1.93, None, None, 1.0, 1.0),
    ("29 Apr 2026", "Biopsy Report Reviewed — Moderate tubulitis with interstitial inflammation; T-Cell Mediated Rejection Type 1A; mild IFTA (10%)", None, None, None, None, None),
    ("29 Apr 2026", "Inj. Solumedrol 500 MG — Dose 1 (Pulse therapy initiated)", None, None, None, None, None),
    ("30 Apr 2026", "Inj. Solumedrol 500 MG — Dose 2", None, 1.46, 3.13, None, None),
    ("01 May 2026", "Inj. Solumedrol 500 MG — Dose 3", None, None, None, None, None),
    ("04 May 2026", "Revisit", 1.93, None, None, 3.5, "STOP"),
    ("08 May 2026", "Revisit", 1.83, None, None, 3.5, None),
    ("11 May 2026", "Routine Follow-Up", 1.82, 3.13, None, 3.5, None),
    ("13 May 2026", "Inj. ATG 25 MG — Dose 1 & Dilzem 30 MG added (three times daily)", 1.93, None, None, 3.5, None),
]

SUMMARY_EVENTS = [
    (1,  "Renal Kidney Transplant",                          "07 Jan 2026"),
    (2,  "1st Biopsy — Borderline T-Cell Rejection Suspected","20 Jan 2026"),
    (3,  "Solumedrol Pulse Therapy — Round 1",               "22–23 Jan 2026"),
    (4,  "E. Coli UTI Detected & Treated",                   "24 Jan 2026"),
    (5,  "Stent Removal Surgery",                            "05 Feb 2026"),
    (6,  "2nd Biopsy — No Rejection Found",                  "25 Feb 2026"),
    (7,  "Tacrolimus → Certican (Everolimus) Switch",        "10–14 Mar 2026"),
    (8,  "BKV PCR — Not Detected",                           "24 Apr 2026"),
    (9,  "3rd Biopsy — T-Cell Mediated Rejection Type 1A",   "27–29 Apr 2026"),
    (10, "Solumedrol Pulse Therapy — Round 2",               "29 Apr – 01 May 2026"),
    (11, "ATG Re-initiated",                                 "13 May 2026"),
]


@st.cache_data
def build_dataframe():
    """Build the working DataFrame from the embedded markdown records."""
    columns = ["Date", "Procedure / Event", "Creatinine",
               "Tacrolimus Level", "Everolimus Level",
               "Tacrolimus Dose", "Everolimus Dose"]
    df = pd.DataFrame(RAW_RECORDS, columns=columns)

    # Parse dates
    df["_date_parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors="coerce")

    # Numeric columns (exclude Dose cols which may hold "STOP")
    for col in ["Creatinine", "Tacrolimus Level", "Everolimus Level"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Numeric-safe dose columns (STOP → NaN for charting)
    for col in ["Tacrolimus Dose", "Everolimus Dose"]:
        df[f"_{col}_num"] = pd.to_numeric(
            df[col].apply(lambda x: None if x == "STOP" else x), errors="coerce"
        )

    # Sort chronologically, preserving original order for same-day entries
    df = df.sort_values("_date_parsed", kind="stable").reset_index(drop=True)

    # Refresh the human-readable Date column to match sorted order
    df["Date"] = df["_date_parsed"].dt.strftime("%d %b %Y")

    return df


def get_latest_with_date(df, column):
    """Return (value, date_str) of the last non-null entry for a column."""
    col_df = df[["Date", column]].dropna(subset=[column])
    col_df = col_df[col_df[column] != "STOP"]
    col_df[column] = pd.to_numeric(col_df[column], errors="coerce")
    col_df = col_df.dropna(subset=[column])
    if col_df.empty:
        return None, None
    row = col_df.iloc[-1]
    return row[column], row["Date"]


def calculate_trend(df, num_col, periods=3):
    """Calculate recent trend for a numeric column."""
    col_df = df[["Date", num_col]].dropna(subset=[num_col])
    if len(col_df) < 2:
        return None, 0
    recent = col_df.tail(periods)
    change = recent[num_col].iloc[-1] - recent[num_col].iloc[0]
    if abs(change) < 0.05:
        return "stable", 0
    return ("up" if change > 0 else "down"), change


def create_trend_chart(df, num_cols_map, title="Trend Analysis"):
    """
    num_cols_map: dict of {display_label: internal_col_name}
    """
    fig = go.Figure()
    colors = {
        "Creatinine":      "#e74c3c",
        "Tacrolimus Level":"#3498db",
        "Everolimus Level":"#27ae60",
        "Tacrolimus Dose": "#9b59b6",
        "Everolimus Dose": "#f39c12",
    }
    for label, col in num_cols_map.items():
        plot_df = df[["_date_parsed", col]].dropna()
        if plot_df.empty:
            continue
        fig.add_trace(go.Scatter(
            x=plot_df["_date_parsed"],
            y=plot_df[col],
            mode="lines+markers",
            name=label,
            line=dict(color=colors.get(label, "#666"), width=2),
            marker=dict(size=8),
            hovertemplate=f"{label}: %{{y}}<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title="Date", tickangle=45, showgrid=True,
                   gridcolor="rgba(0,0,0,0.1)", tickformat="%d %b %Y"),
        yaxis=dict(title="Value", showgrid=True, gridcolor="rgba(0,0,0,0.1)"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, xanchor="center", x=0.5),
        paper_bgcolor="white",
        plot_bgcolor="rgba(248,249,250,1)",
        height=400,
        margin=dict(t=80, b=60, l=60, r=30)
    )
    return fig


def format_dose_display(val):
    """Format dose value for the display table."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if str(val).strip().upper() == "STOP":
        return "⛔ STOP"
    try:
        num = float(val)
        return f"{int(num) if num == int(num) else num} MG"
    except (ValueError, TypeError):
        return str(val)


def format_num_display(val):
    """Format numeric lab value for display."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    try:
        return f"{float(val):.2f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return "—"


def main():
    st.title("🏥 Medical History Dashboard")
    st.markdown("### Kidney Transplant Post-Operative Monitoring — Jan–May 2026")

    df = build_dataframe()

    # Sidebar navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["📊 Overview", "📋 Medical Records", "🕐 Vertical Timeline", "📈 Trend Analysis"]
    )

    # Numeric column map (display label → internal DataFrame column)
    METRIC_MAP = {
        "Creatinine":       "Creatinine",
        "Tacrolimus Level": "Tacrolimus Level",
        "Everolimus Level": "Everolimus Level",
        "Tacrolimus Dose":  "_Tacrolimus Dose_num",
        "Everolimus Dose":  "_Everolimus Dose_num",
    }

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    if page == "📊 Overview":
        st.header("Patient Overview — Latest Readings")

        st.subheader("🩺 Current Vital Signs")
        st.markdown("""
        <div class="vitals-grid">
            <div class="vital-card"><div class="label">⚖️ Weight</div><div class="value">75 kg</div></div>
            <div class="vital-card"><div class="label">💓 Blood Pressure</div><div class="value">125/81</div></div>
            <div class="vital-card"><div class="label">🫁 SPO2</div><div class="value">98%</div></div>
            <div class="vital-card"><div class="label">❤️ Pulse Rate</div><div class="value">95 bpm</div></div>
        </div>
        """, unsafe_allow_html=True)

         # Fluid Balance
        st.subheader("💧 Fluid Balance")
        st.markdown("""
        <div class="vitals-grid">
            <div class="vital-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="label">🥤 Fluid Intake</div>
                <div class="value">4.7 L</div>
            </div>
            <div class="vital-card" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
                <div class="label">🚽 Fluid Output</div>
                <div class="value">~4 L</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Current Medications
        st.subheader("💊 Current Medications")
        st.markdown("""
        <div class="info-box" style="border-left-color: #27ae60;">
            <ul style="margin: 0; padding-left: 20px;">
                <li><b>TAB. WYSOLONE 5MG</b> — Once daily at 8 AM</li>
                <li><b>TAB. TAKFA 3.5MG</b> — Twice daily at 7 AM and 7 PM</li>
                <li><b>TAB. DILZEM 30MG</b> — 1 tab three times daily at 6 AM, 12 PM and 6 PM</li>
                <li><b>TAB. MYCOFIT-S 360MG</b> — 2 tabs daily at 10 AM AND 2 tabs daily at 9 PM</li>
                <li><b>TAB. PAN 40MG</b> — Once daily at 6 AM (before breakfast)</li>
                <li><b>TAB. SEPTRAN 480MG</b> — Once daily at 2 PM (to continue)</li>
                <li><b>TAB. BISONEXT 2.5MG</b> — 1 tab 1-0-1 (morning-afternoon-night)</li>
                <li><b>TAB. VALGAMAX 450MG</b> — Once daily after lunch × 1 month</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("---")
        st.subheader("📊 Medical Metrics — Latest Values")

        metrics_info = [
            ("Creatinine",       "Creatinine",       "mg/dL", "0.7–1.3",  "#e74c3c"),
            ("Tacrolimus Level", "Tacrolimus Level",  "ng/mL", "5–15",     "#3498db"),
            ("Everolimus Level", "Everolimus Level",  "ng/mL", "3–8",      "#27ae60"),
            ("Tacrolimus Dose",  "_Tacrolimus Dose_num","mg",  "—",        "#9b59b6"),
            ("Everolimus Dose",  "_Everolimus Dose_num","mg",  "—",        "#f39c12"),
        ]

        for label, col, unit, normal, color in metrics_info:
            value, date_str = get_latest_with_date(df, col)
            trend_dir, trend_val = calculate_trend(df, col)
            trend_symbol = "↑" if trend_dir == "up" else "↓" if trend_dir == "down" else "→"
            trend_text = f"{trend_symbol} {'Increased' if trend_dir == 'up' else 'Decreased' if trend_dir == 'down' else 'Stable'}"

            st.markdown(f"""
            <div class="overview-card" style="border-left: 5px solid {color};">
                <h4>{label} <span style="color:#7f8c8d;font-weight:normal;font-size:14px;">(Normal: {normal} {unit})</span></h4>
                <div class="value" style="color:{color};">
                    {f'{value:.2f}' if value is not None else 'N/A'} {unit}
                </div>
                <div class="date">📅 Latest reading: {date_str if date_str else 'No data'}</div>
                <div class="trend">{trend_text} by {abs(trend_val):.2f} {unit} (last 3 readings)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ── 1. BIOPSY SUMMARY ────────────────────────────────────────────────
        st.subheader("🔬 Biopsy Reports")

        BIOPSIES = [
            {
                "no":     1,
                "biopsy_date": "20 Jan 2026",
                "report_date": "21 Jan 2026",
                "creatinine":  1.74,
                "finding": "Mild interstitial inflammation with mild tubulitis — borderline Acute T-Cell Mediated Rejection suspected.",
                "outcome": "⚠️ Borderline Rejection",
                "outcome_color": "#f39c12",
                "file": "data/biopsy_1.pdf",
            },
            {
                "no":     2,
                "biopsy_date": "25 Feb 2026",
                "report_date": "02 Mar 2026",
                "creatinine":  1.97,
                "finding": "Mild acute tubular injury — no evidence of rejection.",
                "outcome": "✅ No Rejection",
                "outcome_color": "#27ae60",
                "file": "data/biopsy_2.pdf",
            },
            {
                "no":     3,
                "biopsy_date": "27 Apr 2026",
                "report_date": "29 Apr 2026",
                "creatinine":  1.93,
                "finding": "Moderate tubulitis with interstitial inflammation — T-Cell Mediated Rejection Type 1A; mild IFTA (10%).",
                "outcome": "🔴 Rejection Type 1A",
                "outcome_color": "#e74c3c",
                "file": "data/biopsy_3.pdf",
            },
        ]

        st.markdown(
            f"**Total biopsies performed: {len(BIOPSIES)}**",
        )

        for b in BIOPSIES:
            # Check if the PDF exists on disk
            import os
            pdf_exists = os.path.isfile(b["file"])

            card_html = f"""
            <div class="overview-card" style="border-left: 5px solid {b['outcome_color']};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                    <div>
                        <h4 style="margin:0 0 6px 0;">
                            Biopsy #{b['no']}
                            <span style="font-size:13px; font-weight:normal; color:#7f8c8d; margin-left:10px;">
                                Performed: {b['biopsy_date']} &nbsp;|&nbsp; Report: {b['report_date']}
                            </span>
                        </h4>
                        <div style="font-size:13px; color:#555; margin-bottom:6px;">
                            🧫 <b>Finding:</b> {b['finding']}
                        </div>
                        <div style="font-size:13px; color:#555;">
                            💧 <b>Creatinine at biopsy:</b> {b['creatinine']} mg/dL
                            &nbsp;&nbsp;
                            <span style="color:{b['outcome_color']}; font-weight:600;">{b['outcome']}</span>
                        </div>
                    </div>
                    <div style="font-size:28px; opacity:0.15; align-self:center;">🔬</div>
                </div>
                {'<div style="margin-top:8px;"><span style="font-size:12px;color:#aaa;">📄 PDF not found</span></div>' if not pdf_exists else ''}
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # Render download button only once if PDF exists
            if pdf_exists:
                st.download_button(
                    label="📄 Download Report",
                    data=open(b["file"], "rb").read(),
                    file_name=f"biopsy_{b['no']}.pdf",
                    mime="application/pdf",
                    key=f"biopsy_dl_{b['no']}",
                )

        # ── 2. ATG DOSE SUMMARY ──────────────────────────────────────────────
        st.markdown("---")
        st.subheader("💉 ATG Doses")

        ATG_DOSES = [
            {"dose": 1, "date": "07 Jan 2026", "detail": "ATG Dose 1 — post-transplant immunosuppression induction", "cr": 1.22},
            {"dose": 2, "date": "09 Jan 2026", "detail": "ATG Dose 2 — continued induction therapy",                "cr": 1.28},
            {"dose": 3, "date": "13 May 2026", "detail": "Inj. ATG 25 MG — re-initiated for rejection management, Dilzem 30 MG added", "cr": 1.93},
        ]

        st.markdown(f"**Total ATG doses administered: {len(ATG_DOSES)}**")

        # Create ATG doses as cards using Streamlit columns instead of HTML table
        for i, d in enumerate(ATG_DOSES):
            bg_color = "#e8f4f8" if i % 2 == 0 else "#ffffff"
            st.markdown(f"""
            <div style="background:{bg_color};border-radius:8px;padding:15px;margin:8px 0;border-left:4px solid #3498db;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                    <div>
                        <span style="font-weight:600;color:#2c3e50;font-size:15px;">Dose {d['dose']}</span>
                        <span style="color:#7f8c8d;margin-left:12px;font-size:13px;">📅 {d['date']}</span>
                    </div>
                    <span style="background:#E6F1FB;color:#185FA5;padding:4px 12px;border-radius:99px;font-weight:500;font-size:13px;">{d['cr']} mg/dL</span>
                </div>
                <div style="color:#555;font-size:13px;margin-top:6px;">{d['detail']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── 3. SOLUMEDROL DOSE SUMMARY ────────────────────────────────────────
        st.markdown("---")
        st.subheader("💊 Solumedrol (Methylprednisolone) Doses")

        SOLUMEDROL_ROUNDS = [
            {
                "round": 1,
                "reason": "Borderline T-Cell Mediated Rejection (Biopsy #1)",
                "doses": [
                    {"dose": 1, "date": "22 Jan 2026"},
                    {"dose": 2, "date": "23 Jan 2026"},
                ],
            },
            {
                "round": 2,
                "reason": "T-Cell Mediated Rejection Type 1A (Biopsy #3)",
                "doses": [
                    {"dose": 1, "date": "29 Apr 2026"},
                    {"dose": 2, "date": "30 Apr 2026"},
                    {"dose": 3, "date": "01 May 2026"},
                ],
            },
        ]

        total_sol = sum(len(r["doses"]) for r in SOLUMEDROL_ROUNDS)
        st.markdown(f"**Total Solumedrol 500 MG doses: {total_sol} across {len(SOLUMEDROL_ROUNDS)} treatment rounds**")

        for r in SOLUMEDROL_ROUNDS:
            dose_list = "".join(
                f'<li style="margin:4px 0;color:#555;">Dose {d["dose"]} — 📅 {d["date"]}</li>'
                for d in r["doses"]
            )
            st.markdown(f"""
            <div class="overview-card" style="border-left: 5px solid #9b59b6;">
                <h4 style="margin:0 0 6px 0;">
                    Round {r['round']}
                    <span style="font-size:13px;font-weight:normal;color:#7f8c8d;margin-left:8px;">
                        {len(r['doses'])} doses &nbsp;·&nbsp; 500 MG IV each
                    </span>
                </h4>
                <div style="font-size:13px;color:#555;margin-bottom:8px;">
                    ⚠️ <b>Reason:</b> {r['reason']}
                </div>
                <ul style="margin:0;padding-left:20px;font-size:13px;">
                    {dose_list}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # ── Recent Trends ─────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📈 Recent Trends Overview")
        trend_df = df[df["_date_parsed"].notna()].tail(15)
        fig = create_trend_chart(
            trend_df,
            {"Creatinine": "Creatinine", "Tacrolimus Level": "Tacrolimus Level"},
            "Key Metrics Trend"
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # ── MEDICAL RECORDS ───────────────────────────────────────────────────────
    elif page == "📋 Medical Records":
        st.header("Complete Treatment Timeline")

        st.markdown("""
        <div class="info-box">
            <h4>📖 Understanding Your Medical Records</h4>
            <p>This table shows the complete post-transplant medical history from January to May 2026,
               sourced from <b>MEDICAL_HISTORY_TABLE.md</b>.</p>
            <ul>
                <li><b>Date</b> — Date of the visit / procedure</li>
                <li><b>Procedure / Event</b> — Medical procedures, tests, treatments, or notes</li>
                <li><b>Creatinine</b> — Kidney function test (Normal: 0.7–1.3 mg/dL)</li>
                <li><b>Tacrolimus Level</b> — Immunosuppressant drug level (Target: 5–15 ng/mL)</li>
                <li><b>Everolimus Level</b> — Immunosuppressant drug level (Target: 3–8 ng/mL)</li>
                <li><b>Tacrolimus Dose</b> — Daily dose in mg (⛔ STOP = discontinued)</li>
                <li><b>Everolimus Dose</b> — Daily dose in mg (⛔ STOP = discontinued)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Build display table matching the markdown layout exactly
        display_rows = []
        for _, row in df.iterrows():
            display_rows.append({
                "Date":                    row["Date"],
                "Procedure / Event":       row["Procedure / Event"],
                "Creatinine (mg/dL)":      format_num_display(row["Creatinine"]),
                "Tacrolimus Level":        format_num_display(row["Tacrolimus Level"]),
                "Everolimus Level":        format_num_display(row["Everolimus Level"]),
                "Suggested Tacrolimus Dose": format_dose_display(row["Tacrolimus Dose"]),
                "Suggested Everolimus Dose": format_dose_display(row["Everolimus Dose"]),
            })

        display_df = pd.DataFrame(display_rows)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Procedure / Event": st.column_config.TextColumn(width="large"),
                "Date": st.column_config.TextColumn(width="small"),
            }
        )

        st.markdown(f"**Total Records:** {len(display_df)}")

        # Summary of Key Clinical Events
        st.markdown("---")
        st.header("Summary of Key Clinical Events")

        rows_html = "".join(
            f"<tr><td>{num}</td><td>{event}</td><td>{date}</td></tr>"
            for num, event, date in SUMMARY_EVENTS
        )
        st.markdown(f"""
        <table class="summary-table">
            <tr><th>#</th><th>Event</th><th>Date</th></tr>
            {rows_html}
        </table>
        """, unsafe_allow_html=True)

    # ── VERTICAL TIMELINE ─────────────────────────────────────────────────────
    elif page == "🕐 Vertical Timeline":
        st.header("🕐 Vertical Timeline")
        st.markdown("Chronological view of all procedures, visits, and clinical events — Jan to May 2026.")

        # Sidebar filter
        st.sidebar.subheader("Filter by category")
        all_categories = ["Surgery", "Biopsy", "Injection", "Follow-up", "Discharge", "Lab / Test"]
        selected_cats = st.sidebar.multiselect("Show categories", all_categories, default=all_categories)

        def classify(proc):
            p = proc.lower()
            if any(k in p for k in ["transplant", "removal surgery", "stent removal"]):
                return "Surgery"
            if "biopsy" in p:
                return "Biopsy"
            if any(k in p for k in ["inj.", "inj ", "atg", "solumedrol", "zavicefta", "aztreonam"]):
                return "Injection"
            if "discharge" in p:
                return "Discharge"
            if any(k in p for k in ["culture", "pcr", "report reviewed", "biopsy report"]):
                return "Lab / Test"
            return "Follow-up"

        # Per-category: dot color, badge bg, badge text
        CAT_STYLE = {
            "Surgery":    {"dot": "#378ADD", "bg": "#E6F1FB", "fg": "#185FA5"},
            "Biopsy":     {"dot": "#E24B4A", "bg": "#FCEBEB", "fg": "#A32D2D"},
            "Injection":  {"dot": "#BA7517", "bg": "#FAEEDA", "fg": "#854F0B"},
            "Follow-up":  {"dot": "#1D9E75", "bg": "#E1F5EE", "fg": "#0F6E56"},
            "Discharge":  {"dot": "#534AB7", "bg": "#EEEDFE", "fg": "#3C3489"},
            "Lab / Test": {"dot": "#D4537E", "bg": "#FBEAF0", "fg": "#72243E"},
        }

        PILL_STYLE = {
            "blue":   ("Cr",  "#E6F1FB", "#185FA5"),
            "amber":  ("Tac", "#FAEEDA", "#854F0B"),
            "teal":   ("Eve", "#E1F5EE", "#0F6E56"),
            "purple": ("",    "#EEEDFE", "#3C3489"),
            "pink":   ("",    "#FBEAF0", "#72243E"),
        }

        def pill(bg, fg, text):
            return (
                f'<span style="font-size:11px;padding:2px 9px;border-radius:99px;'
                f'font-weight:500;white-space:nowrap;background:{bg};color:{fg};">'
                f'{text}</span>'
            )

        def lab_pills(row):
            pills = []
            if pd.notna(row["Creatinine"]):
                pills.append(pill("#E6F1FB", "#185FA5", f'Cr: {row["Creatinine"]:.2f}'))
            if pd.notna(row["Tacrolimus Level"]):
                pills.append(pill("#FAEEDA", "#854F0B", f'Tac: {row["Tacrolimus Level"]}'))
            if pd.notna(row["Everolimus Level"]):
                pills.append(pill("#E1F5EE", "#0F6E56", f'Eve: {row["Everolimus Level"]}'))
            td = row["Tacrolimus Dose"]
            if td is not None and not (isinstance(td, float) and pd.isna(td)):
                lbl = "⛔ Tac STOP" if str(td).upper() == "STOP" else f"Tac dose: {td} MG"
                pills.append(pill("#EEEDFE", "#3C3489", lbl))
            ed = row["Everolimus Dose"]
            if ed is not None and not (isinstance(ed, float) and pd.isna(ed)):
                lbl = "⛔ Eve STOP" if str(ed).upper() == "STOP" else f"Eve dose: {ed} MG"
                pills.append(pill("#FBEAF0", "#72243E", lbl))
            return pills

        # ── Build self-contained HTML ──────────────────────────────────────────
        current_month = None
        items_html = ""
        total_shown = 0

        for _, row in df.iterrows():
            proc = str(row["Procedure / Event"]).strip()
            cat  = classify(proc)
            if cat not in selected_cats:
                continue
            total_shown += 1
            s = CAT_STYLE[cat]

            # Month divider
            month_label = row["_date_parsed"].strftime("%B %Y") if pd.notna(row["_date_parsed"]) else ""
            if month_label and month_label != current_month:
                current_month = month_label
                items_html += f"""
                <div style="font-size:12px;font-weight:700;color:#999;text-transform:uppercase;
                            letter-spacing:0.1em;margin:20px 0 10px 0;padding-bottom:6px;
                            border-bottom:1px solid #eee;">{month_label}</div>
                """

            # Title / description split
            parts      = proc.split(" — ", 1)
            title_text = parts[0].strip()
            desc_text  = parts[1].strip() if len(parts) > 1 else ""

            pills_html  = "".join(lab_pills(row))
            pills_block = (
                f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">'
                f'{pills_html}</div>'
            ) if pills_html else ""
            desc_block = (
                f'<div style="font-size:12px;color:#666;line-height:1.5;margin-bottom:4px;">'
                f'{desc_text}</div>'
            ) if desc_text else ""

            badge = (
                f'<span style="display:inline-block;font-size:10px;padding:1px 8px;'
                f'border-radius:99px;font-weight:600;margin-left:8px;vertical-align:middle;'
                f'text-transform:uppercase;letter-spacing:0.04em;'
                f'background:{s["bg"]};color:{s["fg"]};">{cat}</span>'
            )

            items_html += f"""
            <div style="position:relative;margin-bottom:10px;">
              <div style="position:absolute;left:-26px;top:12px;width:12px;height:12px;
                          border-radius:50%;background:{s["dot"]};
                          border:2px solid #fff;box-shadow:0 0 0 2px {s["dot"]};"></div>
              <div style="background:#fff;border:1px solid #e8e8e8;border-radius:10px;
                          padding:12px 16px;display:flex;gap:14px;align-items:flex-start;">
                <div style="min-width:90px;font-size:12px;color:#888;padding-top:2px;line-height:1.5;">
                  <strong style="display:block;font-size:13px;color:#555;font-weight:600;">
                    {row['Date']}
                  </strong>
                  {cat}
                </div>
                <div style="flex:1;">
                  <div style="font-size:14px;font-weight:600;color:#2c3e50;
                              line-height:1.4;margin-bottom:4px;">
                    {title_text}{badge}
                  </div>
                  {desc_block}
                  {pills_block}
                </div>
              </div>
            </div>
            """

        if total_shown == 0:
            st.info("No records match the selected categories.")
        else:
            full_html = f"""
            <div style="position:relative;padding-left:36px;margin-top:10px;font-family:sans-serif;">
              <div style="position:absolute;left:10px;top:8px;bottom:8px;
                          width:2px;background:#e0e0e0;border-radius:2px;"></div>
              {items_html}
            </div>
            """
            components.html(full_html, height=len(df) * 95, scrolling=True)

        # Legend
        st.markdown("---")
        st.markdown(
            "**Legend &nbsp;** "
            "🔵 Surgery &nbsp;&nbsp; "
            "🔴 Biopsy &nbsp;&nbsp; "
            "🟡 Injection &nbsp;&nbsp; "
            "🟢 Follow-up &nbsp;&nbsp; "
            "🟣 Discharge &nbsp;&nbsp; "
            "🩷 Lab / Test"
        )

    # ── TREND ANALYSIS ────────────────────────────────────────────────────────
    elif page == "📈 Trend Analysis":
        st.header("Medical Metrics Trend Analysis")

        st.sidebar.subheader("Chart Settings")
        display_labels = list(METRIC_MAP.keys())
        selected_labels = st.sidebar.multiselect(
            "Select metrics to display",
            display_labels,
            default=["Creatinine", "Tacrolimus Level"]
        )

        date_options = ["All Time", "Last 10", "Last 20", "Last 30"]
        selected_range = st.sidebar.selectbox("Date Range", date_options, index=0)

        trend_df = df[df["_date_parsed"].notna()].copy()
        if "10" in selected_range:
            trend_df = trend_df.tail(10)
        elif "20" in selected_range:
            trend_df = trend_df.tail(20)
        elif "30" in selected_range:
            trend_df = trend_df.tail(30)

        if selected_labels:
            selected_map = {lbl: METRIC_MAP[lbl] for lbl in selected_labels}
            fig = create_trend_chart(trend_df, selected_map, "Medical Metrics Over Time")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Individual Metric Trends")

        tab_labels = ["Creatinine", "Tacrolimus Level", "Everolimus Level",
                      "Tacrolimus Dose", "Everolimus Dose"]
        tabs = st.tabs(tab_labels)

        infos = {
            "Creatinine":       "💡 **Normal Range**: 0.7–1.3 mg/dL — Kidney function marker",
            "Tacrolimus Level": "💡 **Target Range**: 5–15 ng/mL — Immunosuppressant level",
            "Everolimus Level": "💡 **Target Range**: 3–8 ng/mL — Immunosuppressant level",
            "Tacrolimus Dose":  "💡 Tacrolimus (Takfa) daily dose in mg",
            "Everolimus Dose":  "💡 Certican (Everolimus) daily dose in mg",
        }

        for tab, label in zip(tabs, tab_labels):
            with tab:
                col = METRIC_MAP[label]
                fig = create_trend_chart(trend_df, {label: col}, f"{label} Trend")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                st.info(infos[label])

    # Footer
    st.markdown("---")
    st.markdown("*Medical History Dashboard — For informational purposes only. Consult your healthcare provider.*")


if __name__ == "__main__":
    main()