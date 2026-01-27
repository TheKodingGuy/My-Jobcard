import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Job Card", layout="wide")
st.title("🏗️ Cloud Job Card System")

# 1. Create connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Grab the URL from Secrets
SHEET_URL = st.secrets["spreadsheet"]

# 3. Dropdown Lists
SITE_LIST = ["Site A", "Site B", "Site C", "Other"]
TECH_LIST = ["John Smith", "Jane Doe", "Alex Rivera"]
MATERIAL_LIST = ["Copper Tubing", "PVC Pipe", "Electrical Wire", "Sealant", "Screws", "Brackets"]

with st.form("job_form", clear_on_submit=True):
    # Section 1: Job Details
    col_a, col_b = st.columns(2)
    with col_a:
        job_date = st.date_input("Date", date.today())
        tech = st.selectbox("Technician", options=TECH_LIST)
    with col_b:
        site = st.selectbox("Site", options=SITE_LIST)
    
    work_done = st.text_area("Description of Work Done")
    
    st.markdown("---")
    st.subheader("🛠️ Materials Used")
    
    # Section 2: Material Slots (Item + Number)
    # We create 5 rows for materials
    materials_data = []
    
    # Create a header for the columns
    h1, h2 = st.columns([3, 1])
    h1.caption("Select Material Item")
    h2.caption("Quantity")

    for i in range(5): # This provides 5 slots
        c1, c2 = st.columns([3, 1])
        with c1:
            # We add "None" so they don't have to fill every slot
            item = st.selectbox(f"Slot {i+1}", options=["None"] + MATERIAL_LIST, key=f"item_{i}", label_visibility="collapsed")
        with c2:
            qty = st.number_input(f"Qty {i+1}", min_value=0, step=1, key=f"qty_{i}", label_visibility="collapsed")
        
        # Only save if an item was actually selected and quantity is > 0
        if item != "None" and qty > 0:
            materials_data.append(f"{item} (x{qty})")

    st.markdown("---")
    submitted = st.form_submit_button("SAVE TO CLOUD")

    if submitted:
        if not work_done:
            st.error("Please enter work description.")
        else:
            # 1. READ FRESH DATA
            existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
            
            # 2. Combine the list of materials into one readable string
            # Example: "PVC Pipe (x5), Sealant (x2)"
            material_string = ", ".join(materials_data) if materials_data else "None Used"
            
            # 3. Prepare new row
            new_entry = pd.DataFrame([{
                "Date": str(job_date),
                "Site": site,
                "Work Done": work_done,
                "Materials": material_string,
                "Technician": tech
            }])
            
            # 4. Combine and Update
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
            st.success(f"✅ Saved! Logged {len(materials_data)} materials for {site}.")

if st.checkbox("Show History"):
    data = conn.read(spreadsheet=SHEET_URL, ttl=0)
    st.dataframe(data.tail(10))