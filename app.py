import streamlit as st
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="ITARA Sports Analytics", layout="wide")

if 'data' not in st.session_state:
    # Initializing with template structure for Rwanda Premier League stats
    st.session_state.data = pd.DataFrame(columns=[
        'Player', 'Team', 'Goals', 'Assists', 'Matches_Played', 'Injuries', 'Market_Value'
    ])

# --- HELPER FUNCTIONS ---
def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ITARA_Report')
    return output.getvalue()

def generate_pdf_report(df):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "ITARA SPORTS ANALYTICS - PERFORMANCE REPORT")
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Total Players Analyzed: {len(df)}")
    
    # Simple table-like output for PDF
    y = 700
    for i, row in df.iterrows():
        if y < 50: # New page if bottom reached
            p.showPage()
            y = 750
        p.drawString(100, y, f"{row['Player']} ({row['Team']}): {row['Goals']} G | {row['Assists']} A")
        y -= 20
    
    p.save()
    return buffer.getvalue()

# --- MAIN APP INTERFACE ---
def main():
    st.title("⚽ ITARA Sports Analytics Portal")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "League Data Entry", "Financial Audit", "Reports"])

    if page == "Dashboard":
        st.subheader("High-Level Performance Overview")
        if not st.session_state.data.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Top Scorer", st.session_state.data.loc[st.session_state.data['Goals'].idxmax()]['Player'])
            col2.metric("Total Goals in System", st.session_state.data['Goals'].sum())
            col3.metric("Avg Market Value", f"{st.session_state.data['Market_Value'].mean():,.0f} RWF")
            
            st.bar_chart(st.session_state.data.set_index('Player')[['Goals', 'Assists']])
        else:
            st.info("No data available. Please upload or enter data in 'League Data Entry'.")

    elif page == "League Data Entry":
        st.subheader("Update Rwanda Premier League Stats")
        
        with st.form("entry_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Player Name")
            team = col2.selectbox("Team", ["APR FC", "Rayon Sports", "Police FC", "Kiyovu Sports", "Mukura VS", "Other"])
            goals = col1.number_input("Goals", min_value=0, step=1)
            assists = col2.number_input("Assists", min_value=0, step=1)
            val = st.number_input("Market Value (RWF)", min_value=0)
            
            submit = st.form_submit_button("Add to ITARA Database")
            
            if submit:
                new_entry = {
                    'Player': name, 'Team': team, 'Goals': goals, 
                    'Assists': assists, 'Matches_Played': 1, 
                    'Injuries': 0, 'Market_Value': val
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
                st.success(f"Added {name} successfully!")

    elif page == "Financial Audit":
        st.subheader("Leakage & Revenue Auditing")
        st.write("This module monitors ticket sales vs. stadium capacity to identify financial leakages.")
        capacity = st.number_input("Stadium Capacity", value=30000)
        tickets_sold = st.number_input("Tickets Sold", value=25000)
        if tickets_sold > capacity:
            st.error("Error: Tickets sold cannot exceed capacity.")
        else:
            leakage = ((capacity - tickets_sold) / capacity) * 100
            st.metric("Estimated Attendance Gap", f"{leakage:.2f}%")

    elif page == "Reports":
        st.subheader("Generate Professional Artifacts")
        if not st.session_state.data.empty:
            excel_data = export_to_excel(st.session_state.data)
            st.download_button(
                label="📥 Download League Data (Excel)",
                data=excel_data,
                file_name="ITARA_League_Stats_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            pdf_data = generate_pdf_report(st.session_state.data)
            st.download_button(
                label="📄 Download Professional PDF Report",
                data=pdf_data,
                file_name="ITARA_Technical_Report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("No data found to export.")

if __name__ == "__main__":
    main()
