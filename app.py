import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import json
import base64

# 1. Page Configurations & Injecting Premium CSS Aesthetics
st.set_page_config(
    page_title="DevStack Central", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI styling cards
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
    }
    div[data-testid="stForm"] {
        border: 1px solid rgba(30, 136, 229, 0.3) !important;
        border-radius: 12px !important;
        background-color: rgba(30, 136, 229, 0.02) !important;
    }
</style>
""", unsafe_allow_html=True)

# App branding headers
st.markdown('# ⚡ DevStack Central')
st.markdown('<p style="color: #888888; font-size: 1.2rem; margin-top: -15px;">Ecosystem Registry & Live Project Control Tower</p>', unsafe_allow_html=True)
st.markdown("---")

# 2. High-Speed Cache Engine (Zero-Lag Loads)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="10m") # Memory caching eliminates Google response lags
except Exception as e:
    st.error(f"⚠️ Sheet Link Pipeline Interrupted: {e}")
    st.stop()

if df is not None:
    df = df.dropna(how="all")
else:
    df = pd.DataFrame(columns=["Project Name", "Status", "Category", "Stack", "GitHub URL", "Hosting URL", "Workspace URL", "Description", "Dynamic Data"])

# Initialize variable to track the number of extra link boxes needed
if "links_counter" not in st.session_state:
    st.session_state.links_counter = 0

# 3. SIDEBAR PANEL (Premium Configuration Hub)
with st.sidebar:
    st.markdown("## ⚙️ Project Management")
    st.metric(label="Total Ecosystems Tracked", value=len(df))
    st.markdown("---")
    
    st.markdown("### ➕ Register New Project")
    
    # Standard static fields
    new_name = st.text_input("Project Name*", placeholder="e.g. CaseShorts")
    new_status = st.selectbox("Current Status", ["Active 🟢", "Deployed 🚀", "In Progress 🔵", "In Development 🛠️", "Paused 🟡"])
    new_category = st.selectbox("Category Architecture", ["Web App", "Mobile App", "AI/LLM Workspace", "Backend API", "Utility Script"])
    new_stack = st.text_input("Tech Stack Tokens", placeholder="e.g. Java, Spring Boot, React, PHP")
    
    st.markdown("---")
    st.markdown("**🌐 Standard Gateway URLs**")
    new_github = st.text_input("GitHub URL", placeholder="https://github.com/...")
    new_hosting = st.text_input("Hosting/Live URL", placeholder="https://...")
    new_workspace = st.text_input("Workspace Link", placeholder="Claude, Lovable, Replit...")
    
    st.markdown("---")
    st.markdown("**🖼️ Project Assets**")
    uploaded_image = st.file_uploader("Upload App Screenshot / Preview Image", type=["png", "jpg", "jpeg", "webp"])
    
    new_desc = st.text_area("Scope Description")
    
    st.markdown("---")
    st.markdown("**🔗 Dynamic Custom Links Panel**")
    
    # Render custom link entry text fields dynamically based on counter state
    extra_links_payload = []
    for idx in range(st.session_state.links_counter):
        with st.container(border=True):
            lbl_input = st.text_input(f"Custom Label #{idx+1}", value=f"Link #{idx+1}", key=f"dyn_lbl_{idx}")
            url_input = st.text_input(f"Custom Target URL #{idx+1}", key=f"dyn_url_{idx}", placeholder="https://...")
            if url_input.strip().startswith("http"):
                extra_links_payload.append({"label": lbl_input, "url": url_input})

    if st.button("➕ Add Custom Link Field", use_container_width=True):
        st.session_state.links_counter += 1
        st.rerun()
        
    st.markdown("---")
    
    # Action Button
    if st.button(label="🚀 Commit Project to Stack", use_container_width=True, type="primary"):
        if not new_name:
            st.error("❌ Project Name is an absolute requirement.")
        else:
            # Local base64 stream compression processing for the image
            img_encoded = ""
            if uploaded_image is not None:
                img_encoded = base64.b64encode(uploaded_image.read()).decode()
            
            # Bundle both the image and the custom links cleanly together using matching keys
            custom_payload_meta = {
                "image": img_encoded,
                "links": extra_links_payload
            }
            
            payload = {
                "projectName": new_name,
                "status": new_status,
                "category": new_category,
                "stack": new_stack,
                "githubUrl": new_github,
                "hostingUrl": new_hosting,
                "workspaceUrl": new_workspace,
                "description": new_desc,
                "dynamicData": json.dumps(custom_payload_meta)
            }
            
            try:
                webhook_url = st.secrets["webhook"]["url"]
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 200 and "success" in response.text:
                    st.success(f"🎉 '{new_name}' deployed successfully!")
                    st.session_state.links_counter = 0 # Clear the generation layout counter
                    st.cache_data.clear() # Wipe memory cache to pull fresh data row immediately
                    st.rerun()
                else:
                    st.error("❌ Data Pipeline Write Rejected. Check Google Apps Script logs.")
            except Exception as e:
                st.error(f"❌ Webhook connection dropped: {e}")

# 4. MAIN INTERACTIVE DASHBOARD HUB
if df.empty:
    st.info("💡 Your system ecosystem registry is empty. Populate entries via the control management panel!")
else:
    categories = ["All Frameworks"] + sorted(list(df["Category"].dropna().unique()))
    selected_tabs = st.tabs([f"📂 {cat}" for cat in categories])
    
    for index, tab_name in enumerate(categories):
        with selected_tabs[index]:
            filtered_df = df if tab_name == "All Frameworks" else df[df["Category"] == tab_name]
            
            cols = st.columns(3)
            
            for card_idx, (_, row) in enumerate(filtered_df.iterrows()):
                target_col = cols[card_idx % 3]
                with target_col:
                    with st.container(border=True):
                        
                        # Initialize safe defaults
                        parsed_links_array = []
                        binary_img_data = ""
                        raw_blob = row.get("Dynamic Data", "")
                        
                        # Unpack data out of the single Dynamic Data text column safely
                        if pd.notna(raw_blob) and str(raw_blob).strip() != "":
                            try:
                                data_block = json.loads(raw_blob)
                                parsed_links_array = data_block.get("links", [])
                                binary_img_data = data_block.get("image", "")
                            except:
                                pass
                        
                        # Render Image if data block exists in the sheet cell
                        if binary_img_data:
                            try:
                                st.image(base64.b64decode(binary_img_data), use_container_width=True)
                            except:
                                pass
                        
                        st.markdown(f"### {row['Project Name']}")
                        
                        status = str(row['Status'])
                        if "Deployed" in status or "Active" in status:
                            st.markdown(f"🏷️ **Status:** :green[{status}]")
                        elif "Progress" in status or "Development" in status:
                            st.markdown(f"🏷️ **Status:** :blue[{status}]")
                        else:
                            st.markdown(f"🏷️ **Status:** :orange[{status}]")
                            
                        st.caption(f"🧬 **Architecture Type:** {row['Category']}")
                        st.write(row['Description'] if pd.notna(row['Description']) else "")
                        
                        if pd.notna(row['Stack']) and str(row['Stack']).strip() != "":
                            chips = [c.strip() for c in str(row['Stack']).split(",")]
                            st.markdown(" ".join([f"`{chip}`" for chip in chips]))
                        
                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                        st.markdown("**Project Action Links**")
                        
                        # Core standard links layout
                        link_cols = st.columns(2)
                        with link_cols[0]:
                            if pd.notna(row['GitHub URL']) and str(row['GitHub URL']).startswith("http"):
                                st.link_button("🐙 Codebase", str(row['GitHub URL']), use_container_width=True)
                            if pd.notna(row['Workspace URL']) and str(row['Workspace URL']).startswith("http"):
                                st.link_button("🛠️ Dev Space", str(row['Workspace URL']), use_container_width=True)
                        with link_cols[1]:
                            if pd.notna(row['Hosting URL']) and str(row['Hosting URL']).startswith("http"):
                                st.link_button("🌐 Open Live", str(row['Hosting URL']), use_container_width=True)
                        
                        # Dynamically generate clickable button links from custom data rows
                        if parsed_links_array:
                            st.markdown("---")
                            st.markdown("*Custom Resources*")
                            dynamic_link_cols = st.columns(2)
                            for d_idx, d_link in enumerate(parsed_links_array):
                                if d_link["url"].strip().startswith("http"):
                                    col_assignment = dynamic_link_cols[d_idx % 2]
                                    with col_assignment:
                                        st.link_button(f"🔗 {d_link['label']}", d_link['url'], use_container_width=True)

# 5. DATASTREAM AUDIT PANEL
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📊 Google Sheets Raw Sync Audit Ledger"):
    st.dataframe(df, use_container_width=True)
