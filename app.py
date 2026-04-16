import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ITARA Sports Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS – dark-green stadium aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}
h1, h2, h3, .stTitle {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
}

/* Main BG */
.main { background-color: #0a0e0a; }
.block-container { padding-top: 1.5rem !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f0d 0%, #071407 100%);
    border-right: 1px solid #1e3d1e;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f2a0f, #152e15);
    border: 1px solid #2d5a2d;
    border-radius: 8px;
    padding: 12px 16px;
}

/* DataFrames */
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a6b1a, #0f4a0f);
    color: #e8f5e8;
    border: 1px solid #2d8a2d;
    border-radius: 6px;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #228b22, #145214);
    border-color: #3daf3d;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45,138,45,0.3);
}

/* Download buttons */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1a3d6b, #0f2a4a) !important;
    color: #e8f0ff !important;
    border: 1px solid #2d5a8a !important;
}

/* Form */
div[data-testid="stForm"] {
    background: #0d1f0d;
    border: 1px solid #1e3d1e;
    border-radius: 10px;
    padding: 16px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1f0d;
    border-radius: 8px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7ab87a;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    background: #1a6b1a !important;
    color: #e8f5e8 !important;
    border-radius: 6px;
}

/* Selectbox / inputs */
div[data-baseweb="select"] { background: #0d1f0d; }

/* Info/warning/success */
div[data-testid="stAlert"] { border-radius: 8px; }

.hero-banner {
    background: linear-gradient(135deg, #0a1a0a 0%, #0f2e0f 50%, #071a07 100%);
    border: 1px solid #2d5a2d;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '⚽';
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 64px;
    opacity: 0.08;
}
.hero-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #7ddf7d;
    letter-spacing: 0.06em;
    line-height: 1.1;
    margin: 0;
}
.hero-sub {
    color: #5a8a5a;
    font-size: 0.95rem;
    margin-top: 6px;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.form-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.8rem;
    font-family: 'Barlow Condensed', sans-serif;
    letter-spacing: 0.06em;
}

.kpi-card {
    background: linear-gradient(135deg, #0f2a0f, #152e15);
    border: 1px solid #2d5a2d;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        'Player', 'Team', 'Position', 'Age', 'Goals', 'Assists',
        'Matches', 'Minutes_Played', 'Shots_on_Target', 'Pass_Accuracy',
        'Dribbles_Completed', 'Tackles_Won', 'Health_Score', 'Performance_Index'
    ])

if 'teams' not in st.session_state:
    st.session_state.teams = ["APR FC", "Rayon Sports", "Police FC", "Kiyovu Sports", "Mukura VS"]

if 'match_results' not in st.session_state:
    st.session_state.match_results = pd.DataFrame(columns=[
        'Home_Team', 'Away_Team', 'Home_Goals', 'Away_Goals', 'Matchday'
    ])

# ─────────────────────────────────────────────
# ANALYTICS ENGINES
# ─────────────────────────────────────────────

def calculate_xG(row):
    """Expected Goals (xG) — simplified model based on shots & accuracy."""
    shots = max(row.get('Shots_on_Target', 0), 0)
    matches = max(row.get('Matches', 1), 1)
    shot_rate = shots / matches
    xG_per_match = shot_rate * 0.32  # average conversion factor
    return round(xG_per_match * matches, 2)

def calculate_xA(row):
    """Expected Assists (xA) — proxy via pass accuracy & assists."""
    assists = row.get('Assists', 0)
    pass_acc = row.get('Pass_Accuracy', 75) / 100
    xA = assists * (1 + (pass_acc - 0.75))
    return round(max(xA, 0), 2)

def calculate_progressive_score(row):
    """Progressive Carrying & Pressing composite (0–10 scale)."""
    dribbles = row.get('Dribbles_Completed', 0)
    tackles = row.get('Tackles_Won', 0)
    matches = max(row.get('Matches', 1), 1)
    prog = ((dribbles / matches) * 0.6 + (tackles / matches) * 0.4) * 1.5
    return round(min(prog, 10), 2)

def calculate_market_value(row):
    """
    FIFA-aligned valuation model:
    V = PI × κ × (1 + ΔM) × age_factor
    κ = RWF 1,250,000 | ΔM = match exposure | age_factor peaks at 24–27
    """
    pi = row['Performance_Index']
    matches = max(row.get('Matches', 1), 1)
    age = row.get('Age', 25)
    age_factor = 1.0 - abs(age - 25) * 0.015
    age_factor = max(0.6, age_factor)
    base_value = (pi * 1_250_000) * (1 + (matches * 0.05)) * age_factor
    return round(base_value, -3)

def calculate_composite_rating(row):
    """
    Composite Player Rating (CPR) — inspired by EA FC / CIES methodology.
    Weights: PI(40%) + Goals/Match(20%) + Assists/Match(15%) +
             Pass Accuracy(10%) + Health(10%) + Progressive(5%)
    """
    matches = max(row.get('Matches', 1), 1)
    g_rate = min(row.get('Goals', 0) / matches * 10, 10)
    a_rate = min(row.get('Assists', 0) / matches * 10, 10)
    pass_norm = row.get('Pass_Accuracy', 75) / 10
    health_norm = row.get('Health_Score', 100) / 10
    prog = calculate_progressive_score(row)
    pi = row.get('Performance_Index', 5)

    cpr = (pi * 0.40 + g_rate * 0.20 + a_rate * 0.15 +
           pass_norm * 0.10 + health_norm * 0.10 + prog * 0.05)
    return round(min(cpr, 10), 2)

def get_player_form(pi):
    if pi >= 8.5: return "Elite"
    if pi >= 7.0: return "Strong"
    if pi >= 5.0: return "Developing"
    return "Underperforming"

def form_color(form):
    return {"Elite": "#00e676", "Strong": "#69f0ae", "Developing": "#ffeb3b", "Underperforming": "#ff5252"}.get(form, "#fff")

def availability_status(health):
    if health >= 85: return "✅ Match Ready"
    if health >= 70: return "⚠️ Light Training"
    if health >= 50: return "🟠 Monitored"
    return "🔴 Unavailable"

# ─────────────────────────────────────────────
# LEAGUE TABLE ENGINE
# ─────────────────────────────────────────────
def compute_league_table(results_df, teams):
    table = {t: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0} for t in teams}

    for _, row in results_df.iterrows():
        ht, at = row['Home_Team'], row['Away_Team']
        hg, ag = int(row['Home_Goals']), int(row['Away_Goals'])

        if ht not in table: table[ht] = {'MP':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
        if at not in table: table[at] = {'MP':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}

        table[ht]['MP'] += 1; table[at]['MP'] += 1
        table[ht]['GF'] += hg; table[ht]['GA'] += ag
        table[at]['GF'] += ag; table[at]['GA'] += hg

        if hg > ag:
            table[ht]['W'] += 1; table[ht]['Pts'] += 3
            table[at]['L'] += 1
        elif hg == ag:
            table[ht]['D'] += 1; table[ht]['Pts'] += 1
            table[at]['D'] += 1; table[at]['Pts'] += 1
        else:
            table[at]['W'] += 1; table[at]['Pts'] += 3
            table[ht]['L'] += 1

    for t in table:
        table[t]['GD'] = table[t]['GF'] - table[t]['GA']

    df = pd.DataFrame(table).T.reset_index().rename(columns={'index': 'Club'})
    df = df.sort_values(['Pts', 'GD', 'GF'], ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = 'Pos'
    return df

# ─────────────────────────────────────────────
# PDF REPORT ENGINE
# ─────────────────────────────────────────────
def generate_pro_pdf(df, league_df=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=0.6*inch, rightMargin=0.6*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'],
                                  fontSize=18, spaceAfter=4, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#1a6b1a'))
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'],
                                fontSize=9, alignment=TA_CENTER,
                                textColor=colors.HexColor('#555555'))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'],
                               fontSize=12, spaceBefore=14, spaceAfter=6,
                               textColor=colors.HexColor('#0f4a0f'))
    note_style = ParagraphStyle('NoteStyle', parent=styles['Normal'],
                                 fontSize=7.5, textColor=colors.HexColor('#666666'))
    elements = []

    elements.append(Paragraph("ITARA SPORTS ANALYTICS", title_style))
    elements.append(Paragraph("Technical Intelligence Report — Proprietary Scouting Data Service", sub_style))
    elements.append(Spacer(1, 0.25*inch))

    # Player table
    elements.append(Paragraph("Aggregated Performance Metrics", h2_style))
    df_copy = df.copy()
    df_copy['CPR'] = df_copy.apply(calculate_composite_rating, axis=1)
    df_copy['xG'] = df_copy.apply(calculate_xG, axis=1)
    df_copy['Form'] = df_copy['Performance_Index'].apply(get_player_form)
    df_copy['Value (RWF)'] = df_copy.apply(calculate_market_value, axis=1)

    header = ["Player", "Team", "Pos", "CPR", "PI", "xG", "Goals", "Assists", "Form", "Value (RWF)"]
    table_data = [header]
    for _, row in df_copy.iterrows():
        table_data.append([
            row.get('Player', ''), row.get('Team', ''), row.get('Position', 'N/A'),
            f"{row['CPR']:.1f}", f"{row['Performance_Index']:.1f}",
            f"{row['xG']:.1f}", int(row.get('Goals', 0)), int(row.get('Assists', 0)),
            row['Form'], f"{int(row['Value (RWF)']):,}"
        ])

    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f4a0f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f0')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)

    # League table
    if league_df is not None and not league_df.empty:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("League Standings", h2_style))
        lt_data = [list(league_df.columns)]
        for _, row in league_df.iterrows():
            lt_data.append([str(v) for v in row.values])
        lt = Table(lt_data, repeatRows=1)
        lt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f4a0f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f0')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(lt)

    elements.append(Spacer(1, 0.3*inch))
    formula_text = (
        "<b>Methodology:</b> CPR = 0.40×PI + 0.20×G/M + 0.15×A/M + 0.10×PassAcc + 0.10×Health + 0.05×ProgScore | "
        "Market Value V = PI × κ × (1+ΔM) × age_factor, κ=RWF 1,250,000 | "
        "xG derived from Shots-on-Target conversion model (λ=0.32)"
    )
    elements.append(Paragraph(formula_text, note_style))

    doc.build(elements)
    return buffer.getvalue()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 8px 0 16px 0;'>
        <div style='font-family:"Barlow Condensed",sans-serif; font-size:1.7rem; font-weight:800;
                    color:#7ddf7d; letter-spacing:0.1em;'>⚽ ITARA</div>
        <div style='color:#4a7a4a; font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase;'>
            Sports Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox("Navigation", [
        "🏠 Dashboard",
        "📊 Data Management",
        "🏆 League Table",
        "⚖️ Player Comparison",
        "🧠 Coach Decision Center",
        "🏥 Health Reports",
        "🤖 Agent Intelligence",
        "📤 Export Center"
    ])

    st.markdown("---")
    total_players = len(st.session_state.data)
    total_teams = len(st.session_state.teams)
    total_matches = len(st.session_state.match_results)
    st.metric("Players Tracked", total_players)
    st.metric("Teams Registered", total_teams)
    st.metric("Matches Logged", total_matches)
    st.markdown("---")
    st.caption("ITARA · East African Football Intelligence")

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

# ── DASHBOARD ──
if page == "🏠 Dashboard":
    st.markdown("""
    <div class='hero-banner'>
        <div class='hero-title'>ITARA SPORTS ANALYTICS</div>
        <div class='hero-sub'>East African Football Intelligence Platform · Season 2024/25</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.data.empty:
        df = st.session_state.data.copy()
        df['CPR'] = df.apply(calculate_composite_rating, axis=1)
        df['Market_Value'] = df.apply(calculate_market_value, axis=1)
        df['xG'] = df.apply(calculate_xG, axis=1)
        df['Form'] = df['Performance_Index'].apply(get_player_form)

        # KPI Row
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("⚽ Total Goals", int(df['Goals'].sum()))
        c2.metric("🎯 Avg CPR", f"{df['CPR'].mean():.2f}")
        c3.metric("📈 Avg xG", f"{df['xG'].mean():.2f}")
        c4.metric("💰 Top Value (RWF)", f"{df['Market_Value'].max():,.0f}")
        c5.metric("❤️ Avg Fitness", f"{df['Health_Score'].mean():.0f}%")

        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📊 Performance Visuals", "🌐 Radar Analysis", "📋 Squad Overview"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df.sort_values('CPR', ascending=False).head(10),
                             x='Player', y='CPR', color='Team',
                             title='Top 10 Players — Composite Rating (CPR)',
                             color_discrete_sequence=px.colors.sequential.Greens_r)
                fig.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                  paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                  title_font_size=13)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig2 = px.scatter(df, x='Performance_Index', y='Market_Value',
                                  color='Form', size='Matches', hover_data=['Player', 'Team'],
                                  title='Market Value vs Performance Index',
                                  color_discrete_map={
                                      'Elite': '#00e676', 'Strong': '#69f0ae',
                                      'Developing': '#ffeb3b', 'Underperforming': '#ff5252'
                                  })
                fig2.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                   paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                   title_font_size=13)
                st.plotly_chart(fig2, use_container_width=True)

            col3, col4 = st.columns(2)
            with col3:
                fig3 = px.bar(df.groupby('Team')[['Goals', 'Assists']].sum().reset_index(),
                              x='Team', y=['Goals', 'Assists'], barmode='group',
                              title='Goals & Assists by Team',
                              color_discrete_sequence=['#2e7d32', '#81c784'])
                fig3.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                   paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                   title_font_size=13)
                st.plotly_chart(fig3, use_container_width=True)

            with col4:
                fig4 = px.histogram(df, x='Health_Score', nbins=10, color='Team',
                                    title='Fitness Distribution Across Squad',
                                    color_discrete_sequence=px.colors.sequential.Greens)
                fig4.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                   paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                   title_font_size=13)
                st.plotly_chart(fig4, use_container_width=True)

        with tab2:
            selected_player = st.selectbox("Select player for radar analysis", df['Player'].unique())
            p = df[df['Player'] == selected_player].iloc[0]
            matches = max(p.get('Matches', 1), 1)

            categories = ['Scoring', 'Creativity', 'Passing', 'Physical', 'Fitness', 'Overall Rating']
            values = [
                min((p.get('Goals', 0) / matches) * 10, 10),
                min((p.get('Assists', 0) / matches) * 10, 10),
                p.get('Pass_Accuracy', 75) / 10,
                calculate_progressive_score(p),
                p.get('Health_Score', 100) / 10,
                p.get('Performance_Index', 5)
            ]
            values_rounded = [round(v, 2) for v in values]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values_rounded + [values_rounded[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(45,138,45,0.25)',
                line=dict(color='#2d8a2d', width=2),
                name=selected_player
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='#0d1f0d',
                    radialaxis=dict(visible=True, range=[0, 10], color='#4a7a4a',
                                   gridcolor='#1e3d1e'),
                    angularaxis=dict(color='#7ddf7d', gridcolor='#1e3d1e')
                ),
                paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                title=dict(text=f"Attribute Radar — {selected_player}", font_size=15),
                showlegend=False, height=420
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with tab3:
            display = df[['Player', 'Team', 'Position', 'Age', 'Goals', 'Assists',
                           'Matches', 'CPR', 'Performance_Index', 'Form', 'Health_Score']].copy()
            display.columns = ['Player', 'Team', 'Pos', 'Age', 'G', 'A', 'MP',
                                'CPR', 'PI', 'Form', 'Fit%']
            st.dataframe(display.style.background_gradient(subset=['CPR', 'PI'], cmap='Greens'),
                         use_container_width=True)
    else:
        st.info("⬅️ Go to **Data Management** to add players or upload an Excel sheet to get started.")

# ── DATA MANAGEMENT ──
elif page == "📊 Data Management":
    st.subheader("📊 Data Input & Management")

    tab1, tab2, tab3 = st.tabs(["📂 Upload Excel", "✏️ Manual Entry", "⚽ Log Match Result"])

    with tab1:
        st.markdown("Upload a scout Excel sheet with columns matching the player schema.")
        uploaded_file = st.file_uploader("Upload Scout Excel Sheet (.xlsx)", type=["xlsx"])
        if uploaded_file:
            uploaded_df = pd.read_excel(uploaded_file)
            for col in ['Position', 'Age', 'Minutes_Played', 'Shots_on_Target',
                        'Pass_Accuracy', 'Dribbles_Completed', 'Tackles_Won']:
                if col not in uploaded_df.columns:
                    uploaded_df[col] = 0 if col != 'Position' else 'MF'
                    if col == 'Age': uploaded_df[col] = 24
                    if col == 'Pass_Accuracy': uploaded_df[col] = 75
            st.session_state.data = pd.concat(
                [st.session_state.data, uploaded_df], ignore_index=True
            ).drop_duplicates(subset=['Player', 'Team'])
            st.success(f"✅ {len(uploaded_df)} records merged successfully!")
            st.dataframe(uploaded_df.head(), use_container_width=True)

    with tab2:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("**Register New Team**")
            new_team = st.text_input("Team Name")
            if st.button("➕ Add Team") and new_team:
                if new_team not in st.session_state.teams:
                    st.session_state.teams.append(new_team)
                    st.success(f"Team '{new_team}' registered!")
                    st.rerun()
                else:
                    st.warning("Team already exists.")

            st.markdown("**Registered Teams**")
            for t in st.session_state.teams:
                st.markdown(f"• {t}")

        with col2:
            with st.form("player_form"):
                st.markdown("**Player Profile Entry**")
                r1c1, r1c2 = st.columns(2)
                p_name = r1c1.text_input("Player Name")
                p_team = r1c2.selectbox("Team", st.session_state.teams)
                r2c1, r2c2, r2c3 = st.columns(3)
                p_pos = r2c1.selectbox("Position", ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"])
                p_age = r2c2.number_input("Age", 15, 45, 24)
                p_matches = r2c3.number_input("Matches", 1, 100, 10)

                r3c1, r3c2, r3c3 = st.columns(3)
                p_goals = r3c1.number_input("Goals", 0, 100, 0)
                p_assists = r3c2.number_input("Assists", 0, 100, 0)
                p_minutes = r3c3.number_input("Minutes Played", 0, 9000, 900)

                r4c1, r4c2, r4c3 = st.columns(3)
                p_shots = r4c1.number_input("Shots on Target", 0, 200, 5)
                p_pass = r4c2.number_input("Pass Accuracy (%)", 0, 100, 75)
                p_dribbles = r4c3.number_input("Dribbles Completed", 0, 300, 10)

                r5c1, r5c2, r5c3 = st.columns(3)
                p_tackles = r5c1.number_input("Tackles Won", 0, 300, 10)
                p_index = r5c2.slider("Performance Index (0–10)", 0.0, 10.0, 5.0, 0.1)
                p_health = r5c3.slider("Fitness Score (%)", 0, 100, 100)

                if st.form_submit_button("💾 Record Player"):
                    if p_name:
                        new_p = {
                            'Player': p_name, 'Team': p_team, 'Position': p_pos, 'Age': p_age,
                            'Goals': p_goals, 'Assists': p_assists, 'Matches': p_matches,
                            'Minutes_Played': p_minutes, 'Shots_on_Target': p_shots,
                            'Pass_Accuracy': p_pass, 'Dribbles_Completed': p_dribbles,
                            'Tackles_Won': p_tackles, 'Health_Score': p_health,
                            'Performance_Index': p_index
                        }
                        st.session_state.data = pd.concat(
                            [st.session_state.data, pd.DataFrame([new_p])], ignore_index=True
                        )
                        st.success(f"✅ {p_name} added successfully!")
                    else:
                        st.error("Player name is required.")

    with tab3:
        st.markdown("**Log a Match Result** (used to compute the League Table)")
        with st.form("match_form"):
            mc1, mc2, mc3 = st.columns(3)
            home = mc1.selectbox("Home Team", st.session_state.teams, key="home_sel")
            matchday = mc2.number_input("Matchday", 1, 50, 1)
            away = mc3.selectbox("Away Team", [t for t in st.session_state.teams], key="away_sel")
            sc1, sc2 = st.columns(2)
            hg = sc1.number_input("Home Goals", 0, 20, 0)
            ag = sc2.number_input("Away Goals", 0, 20, 0)
            if st.form_submit_button("📝 Log Result"):
                if home != away:
                    new_match = {
                        'Home_Team': home, 'Away_Team': away,
                        'Home_Goals': hg, 'Away_Goals': ag, 'Matchday': matchday
                    }
                    st.session_state.match_results = pd.concat(
                        [st.session_state.match_results, pd.DataFrame([new_match])], ignore_index=True
                    )
                    st.success(f"✅ {home} {hg}–{ag} {away} logged!")
                else:
                    st.error("Home and Away teams must be different.")

        if not st.session_state.match_results.empty:
            st.dataframe(st.session_state.match_results, use_container_width=True)

# ── LEAGUE TABLE ──
elif page == "🏆 League Table":
    st.subheader("🏆 League Standings — FIFA/UEFA Points System")

    if not st.session_state.match_results.empty:
        league_df = compute_league_table(
            st.session_state.match_results, st.session_state.teams
        )

        # Styled table with position badges
        st.markdown("**W=3pts · D=1pt · L=0pt · Ranked by Pts → GD → GF**")

        def style_table(df):
            styled = df.style.apply(
                lambda row: [
                    'background-color: #0a3d0a; color: #7ddf7d; font-weight: bold'
                    if row.name == 1 else
                    'background-color: #0a2a0a; color: #a5d6a7'
                    if row.name <= 4 else
                    'background-color: #3d0a0a; color: #ef9a9a'
                    if row.name >= len(df) - 1 else ''
                    for _ in row
                ], axis=1
            )
            return styled

        st.dataframe(style_table(league_df), use_container_width=True, height=300)

        # Form chart
        st.markdown("---")
        fig_pts = px.bar(
            league_df.reset_index(), x='Club', y='Pts',
            color='Pts', color_continuous_scale='Greens',
            title='Points Tally by Club',
            text='Pts'
        )
        fig_pts.update_traces(textposition='outside')
        fig_pts.update_layout(
            template='plotly_dark', plot_bgcolor='#0a1a0a',
            paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
            showlegend=False, title_font_size=14
        )
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pts, use_container_width=True)
        with col2:
            fig_gd = px.bar(
                league_df.reset_index(), x='Club', y='GD',
                color='GD', color_continuous_scale='RdYlGn',
                title='Goal Difference by Club', text='GD'
            )
            fig_gd.update_traces(textposition='outside')
            fig_gd.update_layout(
                template='plotly_dark', plot_bgcolor='#0a1a0a',
                paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                showlegend=False, title_font_size=14
            )
            st.plotly_chart(fig_gd, use_container_width=True)

        # Results grid
        st.markdown("---")
        st.markdown("**📅 Match Results Log**")
        st.dataframe(st.session_state.match_results, use_container_width=True)

    else:
        st.info("No match results yet. Log results in **Data Management → Log Match Result**.")

# ── PLAYER COMPARISON ──
elif page == "⚖️ Player Comparison":
    st.subheader("⚖️ Head-to-Head Player Comparison")

    if len(st.session_state.data) >= 2:
        df = st.session_state.data.copy()
        df['CPR'] = df.apply(calculate_composite_rating, axis=1)
        df['xG'] = df.apply(calculate_xG, axis=1)
        df['xA'] = df.apply(calculate_xA, axis=1)
        df['Market_Value'] = df.apply(calculate_market_value, axis=1)
        df['Form'] = df['Performance_Index'].apply(get_player_form)

        col1, col2 = st.columns(2)
        with col1:
            p1_name = st.selectbox("Select Player A", df['Player'].unique(), key='p1')
        with col2:
            remaining = [p for p in df['Player'].unique() if p != p1_name]
            p2_name = st.selectbox("Select Player B", remaining, key='p2')

        p1 = df[df['Player'] == p1_name].iloc[0]
        p2 = df[df['Player'] == p2_name].iloc[0]

        st.markdown("---")

        # Stat cards side by side
        metrics = [
            ('CPR (0–10)', 'CPR', 2),
            ('Performance Index', 'Performance_Index', 1),
            ('xG', 'xG', 2),
            ('xA', 'xA', 2),
            ('Goals', 'Goals', 0),
            ('Assists', 'Assists', 0),
            ('Matches Played', 'Matches', 0),
            ('Pass Accuracy (%)', 'Pass_Accuracy', 1),
            ('Fitness (%)', 'Health_Score', 0),
            ('Market Value (RWF)', 'Market_Value', 0),
        ]

        c1, c2, c3 = st.columns([2, 1, 2])
        c2.markdown("<div style='text-align:center; padding-top:32px; color:#7ddf7d; font-family:Barlow Condensed,sans-serif; font-size:1.4rem; font-weight:800;'>VS</div>", unsafe_allow_html=True)

        for label, field, dec in metrics:
            v1 = float(p1.get(field, 0))
            v2 = float(p2.get(field, 0))
            fmt = f"{{:,.{dec}f}}"
            delta1 = round(v1 - v2, dec)
            delta2 = round(v2 - v1, dec)
            c1.metric(label=label, value=fmt.format(v1),
                      delta=f"{'+' if delta1 > 0 else ''}{fmt.format(delta1)} vs {p2_name}")
            c3.metric(label=label, value=fmt.format(v2),
                      delta=f"{'+' if delta2 > 0 else ''}{fmt.format(delta2)} vs {p1_name}")

        # Radar overlay
        st.markdown("---")
        st.markdown("**📡 Attribute Radar Overlay**")

        def player_radar_vals(p):
            m = max(p.get('Matches', 1), 1)
            return [
                round(min(p.get('Goals', 0) / m * 10, 10), 2),
                round(min(p.get('Assists', 0) / m * 10, 10), 2),
                round(p.get('Pass_Accuracy', 75) / 10, 2),
                round(calculate_progressive_score(p), 2),
                round(p.get('Health_Score', 100) / 10, 2),
                round(p.get('Performance_Index', 5), 2),
            ]

        cats = ['Scoring', 'Creativity', 'Passing', 'Physical', 'Fitness', 'Overall']
        v1_vals = player_radar_vals(p1)
        v2_vals = player_radar_vals(p2)

        fig_compare = go.Figure()
        for vals, name, color in [(v1_vals, p1_name, '#2d8a2d'), (v2_vals, p2_name, '#1565c0')]:
            fig_compare.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', name=name,
                line=dict(color=color, width=2),
                fillcolor=color.replace(')', ',0.15)').replace('rgb', 'rgba') if 'rgb' in color else f"{color}26"
            ))
        fig_compare.update_layout(
            polar=dict(
                bgcolor='#0d1f0d',
                radialaxis=dict(visible=True, range=[0, 10], color='#4a7a4a', gridcolor='#1e3d1e'),
                angularaxis=dict(color='#7ddf7d', gridcolor='#1e3d1e')
            ),
            paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
            title=dict(text=f"Radar Comparison: {p1_name} vs {p2_name}", font_size=14),
            height=420, legend=dict(bgcolor='#0d1f0d', bordercolor='#2d5a2d', borderwidth=1)
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        # Verdict
        st.markdown("---")
        st.markdown("**🧮 ITARA Verdict**")
        cpr1 = float(p1['CPR']); cpr2 = float(p2['CPR'])
        if cpr1 > cpr2:
            winner, loser, margin = p1_name, p2_name, round(cpr1 - cpr2, 2)
        elif cpr2 > cpr1:
            winner, loser, margin = p2_name, p1_name, round(cpr2 - cpr1, 2)
        else:
            winner = None

        if winner:
            st.success(f"**{winner}** leads by **{margin} CPR points** over {loser}. "
                       f"Form: {get_player_form(float(p1['Performance_Index']))} vs "
                       f"{get_player_form(float(p2['Performance_Index']))}")
        else:
            st.info("Both players are rated equally by CPR.")
    else:
        st.warning("Add at least 2 players in **Data Management** to use this feature.")

# ── COACH DECISION CENTER ──
elif page == "🧠 Coach Decision Center":
    st.subheader("🧠 Coach Decision Center")
    st.caption("Data-driven squad selection powered by ITARA's CPR algorithm.")

    if not st.session_state.data.empty:
        df = st.session_state.data.copy()
        df['CPR'] = df.apply(calculate_composite_rating, axis=1)
        df['xG'] = df.apply(calculate_xG, axis=1)
        df['Form'] = df['Performance_Index'].apply(get_player_form)
        df['Availability'] = df['Health_Score'].apply(availability_status)
        df['Market_Value'] = df.apply(calculate_market_value, axis=1)

        tab1, tab2, tab3 = st.tabs([
            "📋 Starting XI Selector",
            "📉 Risk Analysis",
            "📊 Position Reports"
        ])

        with tab1:
            st.markdown("**Configure your selection criteria:**")
            col1, col2, col3 = st.columns(3)
            min_fitness = col1.slider("Min. Fitness (%)", 0, 100, 70)
            min_cpr = col2.slider("Min. CPR Score", 0.0, 10.0, 4.0, 0.1)
            formation_positions = col3.multiselect(
                "Positions to fill",
                ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"],
                default=["GK", "CB", "CB", "CM", "ST"]
            )

            eligible = df[
                (df['Health_Score'] >= min_fitness) &
                (df['CPR'] >= min_cpr)
            ].sort_values('CPR', ascending=False)

            st.markdown(f"**{len(eligible)} eligible players** match your criteria:")

            if not eligible.empty:
                display_cols = ['Player', 'Team', 'Position', 'CPR', 'Performance_Index',
                                'Goals', 'Assists', 'Health_Score', 'Form', 'Availability']
                styled = eligible[display_cols].style.background_gradient(
                    subset=['CPR'], cmap='Greens'
                ).applymap(
                    lambda v: 'color: #00e676; font-weight: bold' if v == 'Elite'
                    else 'color: #ffeb3b' if v == 'Developing'
                    else 'color: #ff5252' if v == 'Underperforming' else '',
                    subset=['Form']
                )
                st.dataframe(styled, use_container_width=True)

                # Auto-select best XI
                st.markdown("---")
                st.markdown("**🤖 ITARA Auto-Select: Best Available Starting XI**")
                best_xi = eligible.head(11)
                if len(best_xi) > 0:
                    xi_display = best_xi[['Player', 'Team', 'Position', 'CPR',
                                          'Form', 'Availability']].reset_index(drop=True)
                    xi_display.index = xi_display.index + 1
                    xi_display.index.name = '#'
                    st.dataframe(xi_display, use_container_width=True)

                    avg_cpr = best_xi['CPR'].mean()
                    avg_fit = best_xi['Health_Score'].mean()
                    st.success(
                        f"**Squad Strength:** Avg CPR {avg_cpr:.2f} | "
                        f"Avg Fitness {avg_fit:.0f}% | "
                        f"{'Strong lineup ✅' if avg_cpr >= 6 else 'Developing lineup ⚠️'}"
                    )
            else:
                st.warning("No players meet the current criteria. Try lowering the thresholds.")

        with tab2:
            st.markdown("**Injury & Performance Risk Flags**")
            risk = df.copy()
            risk['Risk_Level'] = risk.apply(lambda r: (
                "🔴 HIGH" if r['Health_Score'] < 50 or r['Performance_Index'] < 3 else
                "🟠 MEDIUM" if r['Health_Score'] < 70 or r['Performance_Index'] < 5 else
                "🟢 LOW"
            ), axis=1)

            risk_display = risk[['Player', 'Team', 'Position', 'Health_Score',
                                  'Performance_Index', 'CPR', 'Risk_Level', 'Availability']]
            st.dataframe(risk_display.sort_values('Health_Score'), use_container_width=True)

            # Risk distribution chart
            risk_counts = risk['Risk_Level'].value_counts().reset_index()
            risk_counts.columns = ['Risk', 'Count']
            fig_risk = px.pie(risk_counts, names='Risk', values='Count',
                              title='Squad Risk Distribution',
                              color_discrete_sequence=['#00e676', '#ffeb3b', '#ff5252'])
            fig_risk.update_layout(template='plotly_dark', paper_bgcolor='#0a1a0a',
                                   font_color='#c8e6c9', title_font_size=13)
            st.plotly_chart(fig_risk, use_container_width=True)

        with tab3:
            st.markdown("**Position-by-Position Strength Report**")
            if 'Position' in df.columns:
                pos_report = df.groupby('Position').agg(
                    Players=('Player', 'count'),
                    Avg_CPR=('CPR', 'mean'),
                    Avg_Fitness=('Health_Score', 'mean'),
                    Total_Goals=('Goals', 'sum'),
                    Total_Assists=('Assists', 'sum')
                ).round(2).reset_index()
                st.dataframe(pos_report, use_container_width=True)

                fig_pos = px.bar(pos_report, x='Position', y='Avg_CPR',
                                 color='Avg_Fitness', color_continuous_scale='RdYlGn',
                                 title='Average CPR by Position (colored by avg fitness)',
                                 text='Avg_CPR')
                fig_pos.update_traces(textposition='outside')
                fig_pos.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                      paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                      title_font_size=13)
                st.plotly_chart(fig_pos, use_container_width=True)
    else:
        st.warning("No player data available. Add players in **Data Management**.")

# ── HEALTH REPORTS ──
elif page == "🏥 Health Reports":
    st.subheader("🏥 Player Health & Fitness Monitor")

    if not st.session_state.data.empty:
        df = st.session_state.data.copy()

        col1, col2 = st.columns([1, 3])
        with col1:
            selected_p = st.selectbox("Select Player", df['Player'].unique())
        
        p_data = df[df['Player'] == selected_p].iloc[0]

        with col2:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Fitness Score", f"{p_data['Health_Score']}%")
            c2.metric("Performance Index", f"{p_data['Performance_Index']:.1f}/10")
            c3.metric("Matches Played", int(p_data.get('Matches', 0)))
            c4.metric("Minutes", int(p_data.get('Minutes_Played', 0)))

        status = availability_status(p_data['Health_Score'])
        if p_data['Health_Score'] >= 85:
            st.success(f"**Clinical Status:** {status}")
        elif p_data['Health_Score'] >= 70:
            st.warning(f"**Clinical Status:** {status}")
        else:
            st.error(f"**Clinical Status:** {status}")

        st.progress(int(p_data['Health_Score']) / 100)

        # Team health overview
        st.markdown("---")
        st.markdown("**🏥 Full Squad Health Overview**")
        health_df = df[['Player', 'Team', 'Health_Score', 'Matches']].copy()
        health_df['Status'] = health_df['Health_Score'].apply(availability_status)
        health_df = health_df.sort_values('Health_Score', ascending=False)

        fig_health = px.bar(health_df, x='Player', y='Health_Score',
                            color='Health_Score', color_continuous_scale='RdYlGn',
                            title='Squad Fitness Levels',
                            range_color=[0, 100], text='Health_Score')
        fig_health.update_traces(textposition='outside')
        fig_health.add_hline(y=70, line_dash='dash', line_color='orange',
                              annotation_text='Review Threshold (70%)')
        fig_health.add_hline(y=85, line_dash='dash', line_color='green',
                              annotation_text='Match Ready Threshold (85%)')
        fig_health.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                  paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                  title_font_size=13)
        st.plotly_chart(fig_health, use_container_width=True)
        st.dataframe(health_df, use_container_width=True)
    else:
        st.warning("No player data available.")

# ── AGENT INTELLIGENCE ──
elif page == "🤖 Agent Intelligence":
    st.subheader("🤖 Agent Intelligence — Prediction & Valuation")

    if not st.session_state.data.empty:
        df = st.session_state.data.copy()
        df['CPR'] = df.apply(calculate_composite_rating, axis=1)
        df['xG'] = df.apply(calculate_xG, axis=1)
        df['xA'] = df.apply(calculate_xA, axis=1)
        df['Market_Value_RWF'] = df.apply(calculate_market_value, axis=1)
        df['Form'] = df['Performance_Index'].apply(get_player_form)
        df['Potential_Rating'] = (df['Performance_Index'] * 1.12).clip(upper=10.0).round(2)
        df['Progressive_Score'] = df.apply(calculate_progressive_score, axis=1)

        st.caption("Values generated via ITARA's proprietary CPR, P2V, and xG/xA algorithms.")
        
        view_cols = ['Player', 'Team', 'Position', 'Age', 'CPR', 'Form',
                     'Performance_Index', 'Potential_Rating', 'xG', 'xA',
                     'Progressive_Score', 'Market_Value_RWF']
        
        st.dataframe(
            df[view_cols].style.background_gradient(subset=['CPR', 'Market_Value_RWF'], cmap='Greens'),
            use_container_width=True
        )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fig_val = px.bar(df.sort_values('Market_Value_RWF', ascending=False).head(10),
                             x='Player', y='Market_Value_RWF', color='Team',
                             title='Top 10 — Estimated Market Value (RWF)',
                             color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_val.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                   paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                   title_font_size=13)
            st.plotly_chart(fig_val, use_container_width=True)

        with col2:
            fig_pot = px.scatter(df, x='Performance_Index', y='Potential_Rating',
                                 color='Form', size='CPR', hover_data=['Player', 'Team'],
                                 title='Current PI vs Potential Rating',
                                 color_discrete_map={
                                     'Elite': '#00e676', 'Strong': '#69f0ae',
                                     'Developing': '#ffeb3b', 'Underperforming': '#ff5252'
                                 })
            fig_pot.update_layout(template='plotly_dark', plot_bgcolor='#0a1a0a',
                                   paper_bgcolor='#0a1a0a', font_color='#c8e6c9',
                                   title_font_size=13)
            st.plotly_chart(fig_pot, use_container_width=True)
    else:
        st.warning("No data available.")

# ── EXPORT CENTER ──
elif page == "📤 Export Center":
    st.subheader("📤 Export Center — Professional Artifact Distribution")

    if not st.session_state.data.empty:
        df = st.session_state.data.copy()
        df['CPR'] = df.apply(calculate_composite_rating, axis=1)
        df['xG'] = df.apply(calculate_xG, axis=1)
        df['Market_Value_RWF'] = df.apply(calculate_market_value, axis=1)
        df['Form'] = df['Performance_Index'].apply(get_player_form)

        league_df = None
        if not st.session_state.match_results.empty:
            league_df = compute_league_table(
                st.session_state.match_results, st.session_state.teams
            ).reset_index()

        col1, col2, col3 = st.columns(3)

        # Excel export
        excel_data = io.BytesIO()
        with pd.ExcelWriter(excel_data, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Player Data', index=False)
            if league_df is not None:
                league_df.to_excel(writer, sheet_name='League Table', index=False)
            if not st.session_state.match_results.empty:
                st.session_state.match_results.to_excel(writer, sheet_name='Match Results', index=False)

        col1.download_button(
            "📥 Export Excel (Full Data)",
            excel_data.getvalue(),
            "ITARA_Scouting_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        col1.caption("Includes Player Data, League Table & Match Results sheets.")

        # PDF export
        pdf_report = generate_pro_pdf(df, league_df)
        col2.download_button(
            "📄 Export PDF Report",
            pdf_report,
            "ITARA_Intelligence_Brief.pdf",
            mime="application/pdf"
        )
        col2.caption("Professional scouting brief with CPR, xG, xA & market values.")

        # CSV export
        csv_data = df.to_csv(index=False).encode('utf-8')
        col3.download_button(
            "📊 Export CSV",
            csv_data,
            "ITARA_Players.csv",
            mime="text/csv"
        )
        col3.caption("Raw player data in CSV format.")

        st.markdown("---")
        st.markdown("**📋 Data Preview**")
        st.dataframe(df[['Player', 'Team', 'Position', 'CPR', 'xG',
                          'Performance_Index', 'Form', 'Market_Value_RWF']],
                     use_container_width=True)
    else:
        st.error("⚠️ Cannot export: Database is empty. Add players in Data Management first.")
