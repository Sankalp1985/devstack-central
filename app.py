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

# Custom Glassmorphism UI styling cards
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1E88E5 !important;
    }
    .project-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stForm"] {
        border: 1px solid rgba(30, 136, 229, 0.3) !important;
        border-radius: 12px !important;
        background-color: rgba(30, 136, 229, 0.02) !important;
    }
</style>
""", unsafe_url_allowed=True)

# App branding headers
st.markdown('# ⚡ DevStack Central')
st.markdown('<p style="color: #888888; font-size: 1.2rem; margin-top: -15px;">Ecosystem Registry & Live Project Control Tower</p>', unsafe_url_allowed=True)
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

# Tracking array states for the flexible custom links generator 
if "extra_links" not in st.session_state:
    st.session_state.extra_links = []

# 3. SIDEBAR PANEL (Premium Configuration Hub)
with st.sidebar:
    st.markdown("## ⚙️ Project Management")
    st.metric(label="Total Ecosystems Tracked", value=len(df))
    st.markdown("---")
    
    st.markdown("### ➕ Register New Project")
    with st.form(key="project_registry_form", clear_on_submit=True):
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
        st.markdown("**🖼️ Project Assets (Deliverable 2)**")
        uploaded_image = st.file_uploader("Upload App Screenshot / Preview Image", type=["png", "jpg", "jpeg", "webp"])
        
        new_desc = st.text_area("Scope Description")
        st.markdown("---")
        
        # Form Submit Processor
        submit_btn = st.form_submit_button(label="🚀 Commit Project to Stack", use_container_width=True)
        
        if submit_btn:
            if not new_name:
                st.error("❌ Project Name is an absolute requirement.")
            else:
                # Deliverable 2: Local base64 stream compression processing
                img_encoded = ""
                if uploaded_image is not None:
                    img_encoded = base64.b64encode(uploaded_image.read()).decode()
                
                # Dynamic array packing wrapper
                custom_payload_meta = {
                    "encoded_image_stream": img_encoded,
                    "generated_links_manifest": st.session_state.extra_links
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
                        st.session_state.extra_links = [] # Reset state pointers
                        st.cache_data.clear() # Wipe fast local cache to instantly sync new row
                        st.rerun()
                    else:
                        st.error("❌ Data Pipeline Write Rejected. Check Google Apps Script logs.")
                except Exception as e:
                    st.error(f"❌ Webhook connection dropped: {e}")

    # MULTI-LINK DYNAMIC INJECTOR PANEL (Placed outside structural form boundary to handle state-refresh)
    st.markdown("---")
    st.markdown("**🔗 Dynamic Custom Links Panel**")
    
    # Loop over user generated entries
    temp_links_collector = []
    for idx, link_block in enumerate(st.session_state.extra_links):
        with st.container(border=True):
            lbl_input = st.text_input(f"Custom Label #{idx+1}", value=link_block["label"], key=f"dyn_lbl_{idx}")
            url_input = st.text_input(f"Custom Target URL #{idx+1}", value=link_block["url"], key=f"dyn_url_{idx}", placeholder="https://...")
            temp_links_collector.append({"label": lbl_input, "url": url_input})
    st.session_state.extra_links = temp_links_collector

    if st.button("➕ Add Another Custom Link Field", use_container_width=True):
        st.session_state.extra_links.append({"label": "Other Link", "url": ""})
        st.rerun()

# 4. MAIN INTERACTIVE DASHBOARD HUB (Deliverable 3 UI Layout)
if df.empty:
    st.info("💡 Your system ecosystem registry is empty. Populate entries via the control management panel!")
else:
    # Segment layouts gracefully into beautiful high-contrast category view tabs
    categories = ["All Frameworks"] + sorted(list(df["Category"].dropna().unique()))
    selected_tabs = st.tabs([f"📂 {cat}" for cat in categories])
    
    for index, tab_name in enumerate(categories):
        with selected_tabs[index]:
            filtered_df = df if tab_name == "All Frameworks" else df[df["Category"] == tab_name]
            
            # Form grid layout matrix columns 
            cols = st.columns(3)
            
            for card_idx, (_, row) in enumerate(filtered_df.iterrows()):
                target_col = cols[card_idx % 3]
                with target_col:
                    # Enclose rows completely within standard structural cards
                    with st.container(border=True):
                        
                        # Safe parsing execution of structural dictionaries 
                        parsed_links_array = []
                        binary_img_data = ""
                        raw_blob = row.get("Dynamic Data", "")
                        
                        if pd.notna(raw_blob) and str(raw_blob).strip() != "":
                            try:
                                data_block = json.loads(raw_blob)
                                parsed_links_array = data_block.get("generated_links_manifest", [])
                                binary_img_data = data_block.get("encoded_image_stream", "")
                            except:
                                pass
                        
                        # Deliverable 2: Image Canvas Engine output render
                        if binary_img_data:
                            try:
                                st.image(base64.b64decode(binary_img_data), use_container_width=True)
                            except:
                                pass
                        
                        st.markdown(f"### {row['Project Name']}")
                        
                        # Clean colored status indicators
                        status = str(row['Status'])
                        if "Deployed" in status or "Active" in status:
                            st.markdown(f"🏷️ **Status:** :green[{status}]")
                        elif "Progress" in status or "Development" in status:
                            st.markdown(f"🏷️ **Status:** :blue[{status}]")
                        else:
                            st.markdown(f"🏷️ **Status:** :orange[{status}]")
                            
                        st.caption(f"🧬 **Architecture Type:** {row['Category']}")
                        st.write(row['Description'] if pd.notna(row['Description']) else "")
                        
                        # Tokenized Tech pill chip badges
                        if pd.notna(row['Stack']) and str(row['Stack']).strip() != "":
                            chips = [c.strip() for c in str(row['Stack']).split(",")]
                            st.markdown(" ".join([f"`{chip}`" for chip in chips]))
                        
                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_url_allowed=True)
                        st.markdown("**Project Action Links**")
                        
                        # Core standard quick action primary triggers
                        link_cols = st.columns(2)
                        with link_cols[0]:
                            if pd.notna(row['GitHub URL']) and str(row['GitHub URL']).startswith("http"):
                                st.link_button("🐙 Codebase", str(row['GitHub URL']), use_container_width=True)
                            if pd.notna(row['Workspace URL']) and str(row['Workspace URL']).startswith("http"):
                                st.link_button("🛠️ Dev Space", str(row['Workspace URL']), use_container_width=True)
                        with link_cols[1]:
                            if pd.notna(row['Hosting URL']) and str(row['Hosting URL']).startswith("http"):
                                st.link_button("🌐 Open Live", str(row['Hosting URL']), use_container_width=True)
                        
                        # Dynamically added custom user-defined link buttons injection
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
st.markdown("<br><br>", unsafe_url_allowed=True)
with st.expander("📊 Google Sheets Raw Sync Audit Ledger"):
    st.dataframe(df, use_container_width=True)
