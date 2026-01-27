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

TECH_LIST = ["Denver", "Randell", "Wynand", "Lionel", "Austin", "Audrine", "Sam", "Wayne", "Ernest", "Denzel", "James", "Brad", "Sylvester", "Elvin", "Daniello"]

MATERIAL_LIST = ["Copper Tubing", "PVC Pipe", "Electrical Wire", "Sealant", "Screws", "Brackets"]

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

# Single fill-in box for material entry
c1, c2 = st.columns([3, 1])
with c1:
    selected_item = st.selectbox("Pick Material", options=MATERIAL_LIST)
with c2:
    selected_qty = st.number_input("Quantity", min_value=1, step=1)

# Buttons for adding materials
btn_col1, btn_col2, _ = st.columns([1, 1, 2])

with btn_col1:
    if st.button("✅ Done"):
        # Just adds the current item to the list
        st.session_state.temp_materials.append({"item": selected_item, "qty": selected_qty})
        st.toast(f"Added {selected_item}")

with btn_col2:
    if st.button("➕ Add More Material"):
        # Adds the current item to the list
        st.session_state.temp_materials.append({"item": selected_item, "qty": selected_qty})
        st.toast("Added! Ready for next item.")
        # Note: Streamlit selectboxes reset on rerun, so this prepares the UI for the next selection

# Display the current list of materials added so far
if st.session_state.temp_materials:
    st.markdown("### **List to be Saved:**")
    for idx, m in enumerate(st.session_state.temp_materials):
        col1, col2 = st.columns([0.9, 0.1])
        col1.info(f"{m['item']} (x{m['qty']})")
        if col2.button("🗑️", key=f"delete_{idx}"):
            st.session_state.temp_materials.pop(idx)
            st.rerun()

st.markdown("---")

# Final Save Button
if st.button("🚀 SAVE FULL JOB CARD TO CLOUD"):
    if not work_done:
        st.error("Please enter a description of the work.")
    elif not st.session_state.temp_materials:
        st.error("Please add at least one material item.")
    else:
        # 1. READ FRESH DATA (ttl=0 avoids overwriting)
        existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        # 2. Format the material list into a single string
        mat_summary = ", ".join([f"{m['item']} (x{m['qty']})" for m in st.session_state.temp_materials])
        
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