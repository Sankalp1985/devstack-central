import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import base64

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DevStack Central",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM UI CSS
# =========================================================

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

.stButton button {
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("# ⚡ DevStack Central")
st.markdown(
    '<p style="color: #888888; font-size: 1.2rem; margin-top: -15px;">Ecosystem Registry & Live Project Control Tower</p>',
    unsafe_allow_html=True
)

st.markdown("---")

# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m")

except Exception as e:
    st.error(f"⚠️ Google Sheets Connection Failed: {e}")
    st.stop()

# =========================================================
# DEFAULT EMPTY DATAFRAME
# =========================================================

if df is not None:
    df = df.dropna(how="all")
else:
    df = pd.DataFrame(columns=[
        "Project Name",
        "Status",
        "Category",
        "Stack",
        "GitHub URL",
        "Hosting URL",
        "Workspace URL",
        "Description",
        "Image"
    ])

# =========================================================
# SESSION STATE
# =========================================================

if "links_counter" not in st.session_state:
    st.session_state.links_counter = 0

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Project Management")

    st.metric(
        label="Total Ecosystems Tracked",
        value=len(df)
    )

    st.markdown("---")

    st.markdown("### ➕ Register New Project")

    # =====================================================
    # BASIC FIELDS
    # =====================================================

    new_name = st.text_input(
        "Project Name*",
        placeholder="e.g. CaseShorts"
    )

    new_status = st.selectbox(
        "Current Status",
        [
            "Active 🟢",
            "Deployed 🚀",
            "In Progress 🔵",
            "In Development 🛠️",
            "Paused 🟡"
        ]
    )

    new_category = st.selectbox(
        "Category Architecture",
        [
            "Web App",
            "Mobile App",
            "AI/LLM Workspace",
            "Backend API",
            "Utility Script"
        ]
    )

    new_stack = st.text_input(
        "Tech Stack Tokens",
        placeholder="e.g. React, FastAPI, MongoDB"
    )

    st.markdown("---")

    # =====================================================
    # STANDARD URLS
    # =====================================================

    st.markdown("### 🌐 Standard Gateway URLs")

    new_github = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/..."
    )

    new_hosting = st.text_input(
        "Hosting/Live URL",
        placeholder="https://..."
    )

    new_workspace = st.text_input(
        "Workspace Link",
        placeholder="https://..."
    )

    st.markdown("---")

    # =====================================================
    # IMAGE
    # =====================================================

    st.markdown("### 🖼️ Project Preview")

    uploaded_image = st.file_uploader(
        "Upload App Screenshot",
        type=["png", "jpg", "jpeg", "webp"]
    )

    # =====================================================
    # DESCRIPTION
    # =====================================================

    new_desc = st.text_area(
        "Scope Description"
    )

    st.markdown("---")

    # =====================================================
    # DYNAMIC LINKS
    # =====================================================

    st.markdown("### 🔗 Dynamic Custom Links Panel")

    extra_links_payload = []

    for idx in range(st.session_state.links_counter):

        with st.container(border=True):

            lbl_input = st.text_input(
                f"Custom Label #{idx+1}",
                key=f"dyn_lbl_{idx}",
                value=f"Link {idx+1}"
            )

            url_input = st.text_input(
                f"Custom URL #{idx+1}",
                key=f"dyn_url_{idx}",
                placeholder="https://..."
            )

            if (
                lbl_input.strip() != ""
                and url_input.strip().startswith("http")
            ):

                extra_links_payload.append({
                    "label": lbl_input.strip(),
                    "url": url_input.strip()
                })

    # =====================================================
    # ADD LINK FIELD BUTTON
    # =====================================================

    if st.button(
        "➕ Add Custom Link Field",
        use_container_width=True
    ):
        st.session_state.links_counter += 1
        st.rerun()

    st.markdown("---")

    # =====================================================
    # SAVE PROJECT
    # =====================================================

    if st.button(
        "🚀 Commit Project to Stack",
        use_container_width=True,
        type="primary"
    ):

        if not new_name.strip():

            st.error("❌ Project Name is required.")

        else:

            # =============================================
            # IMAGE ENCODING
            # =============================================

            img_encoded = ""

            if uploaded_image is not None:

                try:
                    img_encoded = base64.b64encode(
                        uploaded_image.read()
                    ).decode()

                except Exception as e:
                    st.error(f"Image encoding failed: {e}")

            # =============================================
            # PAYLOAD
            # =============================================

            payload = {
                "projectName": new_name,
                "status": new_status,
                "category": new_category,
                "stack": new_stack,
                "githubUrl": new_github,
                "hostingUrl": new_hosting,
                "workspaceUrl": new_workspace,
                "description": new_desc,
                "image": img_encoded,
                "dynamicLinks": extra_links_payload
            }

            # =============================================
            # SEND TO APPS SCRIPT
            # =============================================

            try:

                webhook_url = st.secrets["webhook"]["url"]

                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=20
                )

                if (
                    response.status_code == 200
                    and "success" in response.text.lower()
                ):

                    st.success(
                        f"🎉 '{new_name}' deployed successfully!"
                    )

                    st.session_state.links_counter = 0

                    st.cache_data.clear()

                    st.rerun()

                else:

                    st.error(
                        f"❌ Apps Script Error:\n{response.text}"
                    )

            except Exception as e:

                st.error(
                    f"❌ Webhook Connection Failed: {e}"
                )

# =========================================================
# MAIN DASHBOARD
# =========================================================

if df.empty:

    st.info(
        "💡 Your project ecosystem is empty. Add projects from sidebar."
    )

else:

    # =====================================================
    # CATEGORY TABS
    # =====================================================

    categories = ["All Frameworks"] + sorted(
        list(df["Category"].dropna().unique())
    )

    tabs = st.tabs(
        [f"📂 {cat}" for cat in categories]
    )

    # =====================================================
    # STANDARD FIXED COLUMNS
    # =====================================================

    standard_cols = [
        "Project Name",
        "Status",
        "Category",
        "Stack",
        "GitHub URL",
        "Hosting URL",
        "Workspace URL",
        "Description",
        "Image"
    ]

    # =====================================================
    # TAB LOOP
    # =====================================================

    for tab_idx, category in enumerate(categories):

        with tabs[tab_idx]:

            if category == "All Frameworks":
                filtered_df = df
            else:
                filtered_df = df[
                    df["Category"] == category
                ]

            cols = st.columns(3)

            # =================================================
            # PROJECT CARD LOOP
            # =================================================

            for card_idx, (_, row) in enumerate(filtered_df.iterrows()):

                target_col = cols[card_idx % 3]

                with target_col:

                    with st.container(border=True):

                        # =====================================
                        # IMAGE
                        # =====================================

                        binary_img_data = row.get("Image", "")

                        if (
                            pd.notna(binary_img_data)
                            and str(binary_img_data).strip() != ""
                        ):

                            try:

                                st.image(
                                    base64.b64decode(binary_img_data),
                                    use_container_width=True
                                )

                            except:
                                pass

                        # =====================================
                        # TITLE
                        # =====================================

                        st.markdown(
                            f"### {row['Project Name']}"
                        )

                        # =====================================
                        # STATUS
                        # =====================================

                        status = str(row["Status"])

                        if (
                            "Active" in status
                            or "Deployed" in status
                        ):

                            st.markdown(
                                f"🏷️ **Status:** :green[{status}]"
                            )

                        elif (
                            "Progress" in status
                            or "Development" in status
                        ):

                            st.markdown(
                                f"🏷️ **Status:** :blue[{status}]"
                            )

                        else:

                            st.markdown(
                                f"🏷️ **Status:** :orange[{status}]"
                            )

                        # =====================================
                        # CATEGORY
                        # =====================================

                        st.caption(
                            f"🧬 Architecture: {row['Category']}"
                        )

                        # =====================================
                        # DESCRIPTION
                        # =====================================

                        if pd.notna(row["Description"]):

                            st.write(
                                row["Description"]
                            )

                        # =====================================
                        # STACK TAGS
                        # =====================================

                        if (
                            pd.notna(row["Stack"])
                            and str(row["Stack"]).strip() != ""
                        ):

                            chips = [
                                c.strip()
                                for c in str(row["Stack"]).split(",")
                            ]

                            st.markdown(
                                " ".join(
                                    [
                                        f"`{chip}`"
                                        for chip in chips
                                    ]
                                )
                            )

                        st.markdown("---")

                        # =====================================
                        # STANDARD LINKS
                        # =====================================

                        st.markdown(
                            "**Project Action Links**"
                        )

                        link_cols = st.columns(2)

                        with link_cols[0]:

                            if (
                                pd.notna(row["GitHub URL"])
                                and str(row["GitHub URL"]).startswith("http")
                            ):

                                st.link_button(
                                    "🐙 Codebase",
                                    row["GitHub URL"],
                                    use_container_width=True
                                )

                            if (
                                pd.notna(row["Workspace URL"])
                                and str(row["Workspace URL"]).startswith("http")
                            ):

                                st.link_button(
                                    "🛠️ Dev Space",
                                    row["Workspace URL"],
                                    use_container_width=True
                                )

                        with link_cols[1]:

                            if (
                                pd.notna(row["Hosting URL"])
                                and str(row["Hosting URL"]).startswith("http")
                            ):

                                st.link_button(
                                    "🌐 Open Live",
                                    row["Hosting URL"],
                                    use_container_width=True
                                )

                        # =====================================
                        # DYNAMIC LINKS
                        # =====================================

                        dynamic_cols = [
                            col
                            for col in df.columns
                            if col not in standard_cols
                        ]

                        valid_dynamic_links = []

                        for dyn_col in dynamic_cols:

                            val = row.get(dyn_col, "")

                            if (
                                pd.notna(val)
                                and str(val).startswith("http")
                            ):

                                valid_dynamic_links.append(
                                    (dyn_col, val)
                                )

                        if valid_dynamic_links:

                            st.markdown("---")
                            st.markdown("*Custom Resources*")

                            dyn_btn_cols = st.columns(2)

                            for idx, (label, url) in enumerate(valid_dynamic_links):

                                with dyn_btn_cols[idx % 2]:

                                    st.link_button(
                                        f"🔗 {label}",
                                        url,
                                        use_container_width=True
                                    )

# =========================================================
# RAW SHEET VIEW
# =========================================================

st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("📊 Google Sheets Raw Sync Audit Ledger"):

    st.dataframe(
        df,
        use_container_width=True
    )
