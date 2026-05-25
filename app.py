import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd

# Set page configurations
st.set_page_config(page_title="DevStack Central", page_icon="💻", layout="wide")

st.title("💻 DevStack Central")
st.subheader("Your Unified Project Control Tower")
st.markdown("---")

# 1. Establish Google Sheets Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Read existing project data from the connected spreadsheet
    df = conn.read(ttl="1m")  # Caches data for 1 minute to stay fresh
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.info("Please verify your Advanced Settings Secrets on Streamlit Cloud.")
    st.stop()

# Clean up empty rows if any exist in the spreadsheet
df = df.dropna(how="all")

# 2. Sidebar / Top Control Panel - Add New Project
with st.sidebar:
    st.header("⚙️ Project Management")
    st.metric(label="Total Tracked Projects", value=len(df))
    st.markdown("---")
    
    st.subheader("➕ Add New Project")
    with st.form(key="new_project_form", clear_on_submit=True):
        new_name = st.text_input("Project Name*")
        new_status = st.selectbox("Status", ["Active", "In Progress", "Deployed", "Paused", "In Development"])
        new_category = st.selectbox("Category", ["Web App", "Mobile App", "AI/LLM Workspace", "Backend API", "Utility Script"])
        new_stack = st.text_input("Tech Stack (comma-separated)", placeholder="e.g. Streamlit, GitHub, Hostinger")
        
        new_github = st.text_input("GitHub URL")
        new_hosting = st.text_input("Hosting/Live URL")
        new_workspace = st.text_input("Workspace Link (Claude/Lovable/Replit)")
        new_desc = st.text_area("Project Description")
        
        submit_button = st.form_submit_button(label="Save to Google Sheets")
        
        if submit_button:
            if not new_name:
                st.error("Project Name is required.")
            else:
                # Structure the new entry data
                new_row = pd.DataFrame([{
                    "Project Name": new_name,
                    "Status": new_status,
                    "Category": new_category,
                    "Stack": new_stack,
                    "GitHub URL": new_github,
                    "Hosting URL": new_hosting,
                    "Workspace URL": new_workspace,
                    "Description": new_desc
                }])
                
                # Merge new data with existing data frame and push back to Google Sheets
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success(f"🎉 '{new_name}' successfully added!")
                st.rerun()

# 3. Main Dashboard Display
if df.empty:
    st.info("Your database is empty. Use the input panel to add your first project entry!")
else:
    # Filter Tabs based on categories present in your sheet
    categories = ["All"] + sorted(list(df["Category"].dropna().unique()))
    selected_tabs = st.tabs(categories)
    
    for index, tab_name in enumerate(categories):
        with selected_tabs[index]:
            # Filter rows for the active tab view
            if tab_name == "All":
                filtered_df = df
            else:
                filtered_df = df[df["Category"] == tab_name]
            
            # Create a flexible layout grid (Responsive columns)
            cols = st.columns(2 if st.sidebar.to_dict() else 3)
            
            for idx, (_, row) in enumerate(filtered_df.iterrows()):
                col_idx = idx % len(cols)
                with cols[col_idx]:
                    # Render project item card block
                    with st.container(border=True):
                        st.markdown(f"### {row['Project Name']}")
                        
                        # Status badge styling flags
                        status = row['Status']
                        if status in ["Active", "Deployed"]:
                            st.success(f"🟢 {status}")
                        elif status in ["In Progress", "In Development"]:
                            st.info(f"🔵 {status}")
                        else:
                            st.warning(f"🟡 {status}")
                            
                        st.caption(f"**Category:** {row['Category']}")
                        st.write(row['Description'] if pd.notna(row['Description']) else "*No description added.*")
                        
                        # Render technical tags markup 
                        if pd.notna(row['Stack']) and str(row['Stack']).strip() != "":
                            tags = [t.strip() for t in str(row['Stack']).split(",")]
                            st.markdown(" ".join([f"`{tag}`" for tag in tags]))
                        
                        st.markdown("---")
                        
                        # Dynamic Quick Launch Integration Links
                        if pd.notna(row
