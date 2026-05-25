import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

# Set page configurations
st.set_page_config(page_title="DevStack Central", page_icon="💻", layout="wide")

st.title("💻 DevStack Central")
st.subheader("Your Unified Project Control Tower")
st.markdown("---")

# 1. Read Data via Public Link (100% Stable & Free)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="0m")
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

if df is not None:
    df = df.dropna(how="all")
else:
    df = pd.DataFrame(columns=["Project Name", "Status", "Category", "Stack", "GitHub URL", "Hosting URL", "Workspace URL", "Description"])

# 2. Sidebar Setup - Submitting via Webhook
with st.sidebar:
    st.header("⚙️ Project Management")
    st.metric(label="Total Tracked Projects", value=len(df))
    st.markdown("---")
    
    st.subheader("➕ Add New Project")
    with st.form(key="new_project_form", clear_on_submit=True):
        new_name = st.text_input("Project Name*")
        new_status = st.selectbox("Status", ["Active", "In Progress", "Deployed", "Paused", "In Development"])
        new_category = st.selectbox("Category", ["Web App", "Mobile App", "AI/LLM Workspace", "Backend API", "Utility Script"])
        new_stack = st.text_input("Tech Stack", placeholder="e.g. Java, React, PHP, Hostinger")
        
        new_github = st.text_input("GitHub URL")
        new_hosting = st.text_input("Hosting URL")
        new_workspace = st.text_input("Workspace URL")
        new_desc = st.text_area("Description")
        
        submit_button = st.form_submit_button(label="Save to Google Sheets")
        
        if submit_button:
            if not new_name:
                st.error("Project Name is required.")
            else:
                # Prepare payload for Google Apps Script
                payload = {
                    "projectName": new_name,
                    "status": new_status,
                    "category": new_category,
                    "stack": new_stack,
                    "githubUrl": new_github,
                    "hostingUrl": new_hosting,
                    "workspaceUrl": new_workspace,
                    "description": new_desc
                }
                
                try:
                    webhook_url = st.secrets["webhook"]["url"]
                    response = requests.post(webhook_url, json=payload)
                    if response.status_code == 200 and "success" in response.text:
                        st.success(f"🎉 '{new_name}' successfully saved!")
                        st.rerun()
                    else:
                        st.error("Failed to append row. Check your Apps Script deployment.")
                except Exception as e:
                    st.error(f"Webhook communication error: {e}")

# 3. Main Dashboard Rendering Layout
if df.empty:
    st.info("Your database is empty. Use the sidebar input block to add your first project entry!")
else:
    # Use clean columns matching your sheet headers exactly
    categories = ["All"] + sorted(list(df["Category"].dropna().unique()))
    selected_tabs = st.tabs(categories)
    
    for index, tab_name in enumerate(categories):
        with selected_tabs[index]:
            filtered_df = df if tab_name == "All" else df[df["Category"] == tab_name]
            
            cols = st.columns(3)
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                col_idx = idx % 3
                with cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"### {row['Project Name']}")
                        
                        status = row['Status']
                        if status in ["Active", "Deployed"]:
                            st.success(f"🟢 {status}")
                        elif status in ["In Progress", "In Development"]:
                            st.info(f"🔵 {status}")
                        else:
                            st.warning(f"🟡 {status}")
                            
                        st.caption(f"**Category:** {row['Category']}")
                        st.write(row['Description'] if pd.notna(row['Description']) else "")
                        
                        if pd.notna(row['Stack']) and str(row['Stack']).strip() != "":
                            tags = [t.strip() for t in str(row['Stack']).split(",")]
                            st.markdown(" ".join([f"`{tag}`" for tag in tags]))
                        
                        st.markdown("---")
                        
                        if pd.notna(row['GitHub URL']) and str(row['GitHub URL']).startswith("http"):
                            st.link_button("🐙 GitHub", str(row['GitHub URL']), use_container_width=True)
                            
                        if pd.notna(row['Hosting URL']) and str(row['Hosting URL']).startswith("http"):
                            st.link_button("🌐 Live App", str(row['Hosting URL']), use_container_width=True)
                            
                        if pd.notna(row['Workspace URL']) and str(row['Workspace URL']).startswith("http"):
                            st.link_button("🛠️ Workspace", str(row['Workspace URL']), use_container_width=True)

with st.expander("📊 View Raw Spreadsheet Logs"):
    st.dataframe(df, use_container_width=True)
