import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Cloud Job Card", layout="wide")

# 1. Create connection
conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["spreadsheet"]

# 2. Base Data Lists
ALL_TECHS = [
    "Denver", "Randell", "Wynand", "Lionel", "Austin", "Audrine", 
    "Sam", "Wayne", "Ernest", "Denzel", "James", "Brad", 
    "Sylvester", "Elvin", "Daniello"
]

SITE_LIST = ["Site A", "Site B", "Site C", "Other"]

MATERIAL_LIST = ["PVC Conduit", "Copper Tubing", "PVC Pipe", "Electrical Wire", "Sealant", "Screws", "Brackets"]

# Define which items are allowed to use "Meters"
METER_ITEMS = ["PVC Conduit", "Copper Tubing", "PVC Pipe", "Electrical Wire"]

# 3. Initialize Session State for dynamic lists
if "temp_materials" not in st.session_state:
    st.session_state.temp_materials = []
if "temp_techs" not in st.session_state:
    st.session_state.temp_techs = []

# --- APP HEADER ---
st.title("🏗️ Job Card System")

# Updated: Card Type as a Dropdown
job_type = st.selectbox("Select Card Type:", ["Jobcard (Completed Job)", "Pre-Jobcard (Planned Job)"])

st.markdown("---")

# --- UI LAYOUT: CORE DETAILS ---
col_1, col_2, col_3 = st.columns(3)
with col_1:
    job_date = st.date_input("Date", date.today())
    site = st.selectbox("Site Location", options=SITE_LIST)
with col_2:
    start_time = st.time_input("Start Time", value=datetime.now().time())
with col_3:
    end_time = st.time_input("End Time", value=datetime.now().time())

work_done = st.text_area("Description of Work (Done or Planned)")

st.markdown("---")

# --- UI LAYOUT: MULTIPLE TECHNICIANS ---
st.subheader("👨‍🔧 Technicians Assigned")

# Updated: Filter the list to hide technicians already added
available_techs = [t for t in ALL_TECHS if t not in st.session_state.temp_techs]

t_col1, t_col2 = st.columns([3, 1])
with t_col1:
    # If all techs are added, disable the box
    if not available_techs:
        st.info("All technicians have been added.")
        selected_tech = None
    else:
        selected_tech = st.selectbox("Pick Technician", options=available_techs)

with t_col2:
    st.write(" ") # Padding
    if st.button("✅ Done", key="btn_add_tech") and selected_tech:
        st.session_state.temp_techs.append(selected_tech)
        st.rerun() # Rerun to remove name from dropdown instantly

# Display selected technicians as removable tags
if st.session_state.temp_techs:
    st.write("**Added Technicians:**")
    cols = st.columns(4) 
    for idx, t in enumerate(st.session_state.temp_techs):
        with cols[idx % 4]:
            if st.button(f"🗑️ {t}", key=f"t_{idx}"):
                st.session_state.temp_techs.pop(idx)
                st.rerun()

st.markdown("---")

# --- UI LAYOUT: MATERIALS ---
st.subheader("🛠️ Materials Required/Used")

# Single Material Select
selected_item = st.selectbox("Pick Material", options=MATERIAL_LIST)

# Updated: Conditional Unit logic
is_meter_item = selected_item in METER_ITEMS

if is_meter_item:
    c1, c2 = st.columns(2)
    with c1:
        selected_qty = st.number_input("Amount", min_value=0.1, step=0.1, value=1.0)
    with c2:
        selected_unit = st.selectbox("Unit", options=["Meters", "Units"])
else:
    # For non-meter items, hide the unit box and lock it to "Units"
    selected_qty = st.number_input("Number Used", min_value=1, step=1, value=1)
    selected_unit = "Units"

if st.button("✅ Done", key="btn_add_material"):
    st.session_state.temp_materials.append({
        "item": selected_item, 
        "qty": selected_qty, 
        "unit": selected_unit
    })

# Display added materials list
if st.session_state.temp_materials:
    st.write("**Added Materials:**")
    for idx, m in enumerate(st.session_state.temp_materials):
        mc1, mc2 = st.columns([0.9, 0.1])
        mc1.info(f"{m['item']} ({m['qty']} {m['unit']})")
        if mc2.button("🗑️", key=f"m_{idx}"):
            st.session_state.temp_materials.pop(idx)
            st.rerun()

st.markdown("---")

# --- FINAL SAVE ACTION ---
if st.button("🚀 SAVE FULL JOB CARD TO CLOUD"):
    if not work_done:
        st.error("Please enter a description.")
    elif not st.session_state.temp_techs:
        st.error("Please add at least one technician.")
    else:
        existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        
        mat_summary = ", ".join([f"{m['item']} ({m['qty']} {m['unit']})" for m in st.session_state.temp_materials])
        tech_summary = ", ".join(st.session_state.temp_techs)
        
        new_entry = pd.DataFrame([{
            "Type": job_type,
            "Date": str(job_date),
            "Start Time": start_time.strftime("%H:%M"),
            "End Time": end_time.strftime("%H:%M"),
            "Site": site,
            "Work Done": work_done,
            "Materials": mat_summary if mat_summary else "None",
            "Technicians": tech_summary
        }])
        
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        
        st.session_state.temp_materials = []
        st.session_state.temp_techs = []
        st.success(f"✅ {job_type} successfully recorded!")

if st.checkbox("Show Recent History"):
    data = conn.read(spreadsheet=SHEET_URL, ttl=0)
    st.dataframe(data.tail(10))