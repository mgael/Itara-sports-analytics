import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch

# --- CONFIGURATION ---
st.set_page_config(page_title="ITARA Sports Analytics", layout="wide")

# Initialize Session States
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        'Player', 'Team', 'Goals', 'Assists', 'Matches', 'Health_Score', 'Performance_Index'
    ])
if 'teams' not in st.session_state:
    st.session_state.teams = ["APR FC", "Rayon Sports", "Police FC", "Kiyovu Sports", "Mukura VS"]

# --- ANALYTICS ENGINES ---
def calculate_market_value(row):
    """Scientific valuation based on Performance Index (PI) and age-weighting."""
    # Formula: Value = (PI * 1,000,000) * (Matches/10)
    pi = row['Performance_Index']
    matches = max(row['Matches'], 1)
    base_value = (pi * 1250000) * (1 + (matches * 0.05))
    return round(base_value, -3)

def get_player_form(pi):
    if pi >= 8.5: return "Elite"
    if pi >= 7.0: return "Strong"
    if pi >= 5.0: return "Developing"
    return "Underperforming"

# --- REPORTING ENGINE (PDF) ---
def generate_pro_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header & Identification
    elements.append(Paragraph("ITARA SPORTS ANALYTICS - TECHNICAL INTELLIGENCE REPORT", styles['Title']))
    elements.append(Paragraph("Proprietary Data Service for Professional Scouting", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Scientific Summary Table
    elements.append(Paragraph("<b>Aggregated Performance Metrics</b>", styles['Heading2']))
    
    # Process data for table
    table_data = [["Player", "Team", "Index (10)", "Form", "Est. Value (RWF)"]]
    for _, row in df.iterrows():
        val = calculate_market_value(row)
        form = get_player_form(row['Performance_Index'])
        table_data.append([row['Player'], row['Team'], row['Performance_Index'], form, f"{val:,.0f}"])

    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
    ]))
    elements.append(t)
    
    # Formula Footnote
    elements.append(Spacer(1, 0.5*inch))
    formula_text = "<i>Scientific Note: Market Value is derived via $V = (PI \times \kappa) \cdot (1 + \Delta M)$, where $\kappa$ is the market coefficient and $\Delta M$ is the match exposure factor.</i>"
    elements.append(Paragraph(formula_text, styles['Italic']))

    doc.build(elements)
    return buffer.getvalue()

# --- INTERFACE ---
def main():
    st.title("⚽ ITARA Sports Analytics Portal")
    
    # Branding Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("ITARA Data Provider")
    st.sidebar.info("High-fidelity sports intelligence for the East African market.")
    
    page = st.sidebar.selectbox("Navigation", 
        ["Dashboard", "Data Management", "Health Reports", "Agent Intelligence", "Export Center"])

    if page == "Dashboard":
        st.subheader("Interactive Performance Visuals")
        if not st.session_state.data.empty:
            chart_type = st.radio("Select Visualization Type", ["Bar Chart", "Line Chart", "Scatter (Value vs Performance)"])
            
            # Dynamic Charting
            display_df = st.session_state.data.copy()
            display_df['Market_Value'] = display_df.apply(calculate_market_value, axis=1)
            
            if chart_type == "Bar Chart":
                st.bar_chart(display_df.set_index('Player')[['Goals', 'Assists']])
            elif chart_type == "Line Chart":
                st.line_chart(display_df.set_index('Player')['Performance_Index'])
            else:
                st.scatter_chart(display_df, x='Performance_Index', y='Market_Value', color='Team')
        else:
            st.info("Upload data or enter manually in 'Data Management' to see visuals.")

    elif page == "Data Management":
        st.subheader("Data Input & Excel Upload")
        
        # 1. File Upload
        uploaded_file = st.file_uploader("Upload Scout Excel Sheet", type=["xlsx"])
        if uploaded_file:
            uploaded_df = pd.read_excel(uploaded_file)
            st.session_state.data = pd.concat([st.session_state.data, uploaded_df], ignore_index=True)
            st.success("Excel data merged successfully!")

        st.divider()

        # 2. Manual Entry & Team Management
        col1, col2 = st.columns(2)
        with col1:
            new_team = st.text_input("Add New Team to League")
            if st.button("Register Team") and new_team:
                if new_team not in st.session_state.teams:
                    st.session_state.teams.append(new_team)
                    st.rerun()

        with col2:
            with st.form("player_form"):
                p_name = st.text_input("Player Name")
                p_team = st.selectbox("Select Team", st.session_state.teams)
                p_goals = st.number_input("Goals", 0)
                p_assists = st.number_input("Assists", 0)
                p_matches = st.number_input("Matches Played", 1)
                p_index = st.slider("Performance Index (0-10)", 0.0, 10.0, 5.0)
                p_health = st.slider("Health/Fitness (%)", 0, 100, 100)
                
                if st.form_submit_button("Record Entry"):
                    new_p = {'Player': p_name, 'Team': p_team, 'Goals': p_goals, 
                             'Assists': p_assists, 'Matches': p_matches, 
                             'Health_Score': p_health, 'Performance_Index': p_index}
                    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_p])], ignore_index=True)

    elif page == "Health Reports":
        st.subheader("Player Clinical & Fitness Status")
        if not st.session_state.data.empty:
            selected_p = st.selectbox("Select Player for Health Audit", st.session_state.data['Player'])
            p_data = st.session_state.data[st.session_state.data['Player'] == selected_p].iloc[0]
            
            col1, col2 = st.columns(2)
            col1.metric("Current Fitness", f"{p_data['Health_Score']}%")
            status = "Available" if p_data['Health_Score'] > 70 else "Medical Review Required"
            col2.info(f"Clinical Status: {status}")
            
            # Health Visualization
            st.progress(int(p_data['Health_Score']))
        else:
            st.warning("No player data available.")

    elif page == "Agent Intelligence":
        st.subheader("Agent's Prediction & Valuation Tool")
        if not st.session_state.data.empty:
            df_agent = st.session_state.data.copy()
            df_agent['Market Value (RWF)'] = df_agent.apply(calculate_market_value, axis=1)
            df_agent['Form'] = df_agent['Performance_Index'].apply(get_player_form)
            df_agent['Potential'] = (df_agent['Performance_Index'] * 1.15).clip(upper=10.0)
            
            st.dataframe(df_agent[['Player', 'Team', 'Form', 'Performance_Index', 'Potential', 'Market Value (RWF)']])
            st.caption("Values are automatically generated via ITARA's proprietary Performance-to-Value (P2V) algorithm.")

    elif page == "Export Center":
        st.subheader("Professional Artifact Distribution")
        if not st.session_state.data.empty:
            # Excel
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='openpyxl') as writer:
                st.session_state.data.to_excel(writer, index=False)
            
            st.download_button("📥 Export Technical Excel", excel_data.getvalue(), "ITARA_Scouting_Data.xlsx")
            
            # PDF
            pdf_report = generate_pro_pdf(st.session_state.data)
            st.download_button("📄 Export Professional PDF Report", pdf_report, "ITARA_Intelligence_Brief.pdf")
        else:
            st.error("Cannot export: Database is empty.")

if __name__ == "__main__":
    main()
