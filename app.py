import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Job Card", layout="wide")
st.title("🏗️ Cloud Job Card System")

# 1. Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Grab the URL from Secrets (This is the secure way)
SHEET_URL = st.secrets["spreadsheet"]

# 3. Rest of your lists...
SITE_LIST = ["Site A", "Site B", "Site C", "Other"]
TECH_LIST = ["John Smith", "Jane Doe", "Alex Rivera"]
MATERIAL_LIST = ["Copper Tubing", "PVC Pipe", "Electrical Wire", "Sealant"]

st.set_page_config(page_title="Cloud Job Card", layout="wide")
st.title("🏗️ Cloud Job Card System")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("job_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        job_date = st.date_input("Date", date.today())
        tech = st.selectbox("Technician", options=TECH_LIST)
    with col2:
        site = st.selectbox("Site", options=SITE_LIST)
    
    work_done = st.text_area("Description of Work")
    materials = st.multiselect("Materials", options=MATERIAL_LIST)
    
    submitted = st.form_submit_button("SAVE TO CLOUD")

    if submitted:
        if not work_done:
            st.error("Please enter work description.")
        else:
            # Prepare new data
            new_entry = pd.DataFrame([{
                "Date": str(job_date),
                "Site": site,
                "Work Done": work_done,
                "Materials": ", ".join(materials),
                "Technician": tech
            }])
            
            # Get existing data, add new row, and update sheet
            existing_data = conn.read(spreadsheet=SHEET_URL)
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
            st.success("✅ Saved to Google Sheets!")

if st.checkbox("Show History"):
    data = conn.read(spreadsheet=SHEET_URL)
    st.dataframe(data.tail(10))