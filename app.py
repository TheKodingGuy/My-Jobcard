import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Job Card", layout="wide")
st.title("🏗️ Cloud Job Card System")

# 1. Create connection
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["spreadsheet"]

# 2. Lists
SITE_LIST = ["Site A", "Site B", "Site C", "Other"]

TECH_LIST = [
    "Denver", "Randell", "Wynand", "Lionel", "Austin", "Audrine", 
    "Sam", "Wayne", "Ernest", "Denzel", "James", "Brad", 
    "Sylvester", "Elvin", "Daniello"
]

# Added PVC Conduit to the list
MATERIAL_LIST = ["PVC Conduit", "Copper Tubing", "PVC Pipe", "Electrical Wire", "Sealant", "Screws", "Brackets"]
# Define the measurement units
UNIT_LIST = ["Units", "Meters", "Boxes", "Liters", "Rolls"]

# 3. Initialize Session State for the temporary list
if "temp_materials" not in st.session_state:
    st.session_state.temp_materials = []

# --- UI LAYOUT ---
col_a, col_b = st.columns(2)
with col_a:
    job_date = st.date_input("Date", date.today())
    tech = st.selectbox("Technician", options=TECH_LIST)
with col_b:
    site = st.selectbox("Site", options=SITE_LIST)

work_done = st.text_area("Description of Work Done")

st.markdown("---")
st.subheader("🛠️ Materials Used")

# Adjusted layout to include Material, Quantity, and Unit
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    selected_item = st.selectbox("Pick Material", options=MATERIAL_LIST)
with c2:
    selected_qty = st.number_input("Amount", min_value=0.1, step=0.1, value=1.0)
with c3:
    # Logic to default to 'Meters' if PVC Conduit is selected
    default_unit_idx = 1 if "Conduit" in selected_item or "Wire" in selected_item or "Tubing" in selected_item else 0
    selected_unit = st.selectbox("Unit", options=UNIT_LIST, index=default_unit_idx)

# "Done" button to add the selection to the pending list
if st.button("✅ Done"):
    # Adds the current item, qty, and unit to the list
    st.session_state.temp_materials.append({
        "item": selected_item, 
        "qty": selected_qty, 
        "unit": selected_unit
    })

# Display the current list of materials added so far
if st.session_state.temp_materials:
    st.markdown("### **List to be Saved:**")
    for idx, m in enumerate(st.session_state.temp_materials):
        col1, col2 = st.columns([0.9, 0.1])
        # Display format: "PVC Conduit (10.0 Meters)"
        col1.info(f"{m['item']} ({m['qty']} {m['unit']})")
        if col2.button("🗑️", key=f"delete_{idx}"):
            st.session_state.temp_materials.pop(idx)
            st.rerun()

st.markdown("---")

# Final Save Button
if st.button("🚀 SAVE FULL JOB CARD TO CLOUD"):
    if not work_done:
        st.error("Please enter a description of the work.")
    elif not st.session_state.temp_materials:
        st.error("Please add at least one material item using the 'Done' button.")
    else:
        # 1. READ FRESH DATA
        existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        # 2. Format the material list: "PVC Conduit (10.0 Meters), Screws (2.0 Boxes)"
        mat_summary = ", ".join([f"{m['item']} ({m['qty']} {m['unit']})" for m in st.session_state.temp_materials])
        
        # 3. Prepare new row
        new_entry = pd.DataFrame([{
            "Date": str(job_date),
            "Site": site,
            "Work Done": work_done,
            "Materials": mat_summary,
            "Technician": tech
        }])
        
        # 4. Combine and Update
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        
        # 5. Clear the materials list for the next job
        st.session_state.temp_materials = []
        
        st.success(f"✅ Job Card Saved Successfully!")

if st.checkbox("Show History"):
    data = conn.read(spreadsheet=SHEET_URL, ttl=0)
    st.dataframe(data.tail(10))