import streamlit as st
import pandas as pd
import json
from pathlib import Path
import bcrypt
from datetime import datetime
from io import BytesIO
import streamlit.components.v1 as components

# Page Config
st.set_page_config(
    page_title="Global Data Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== MINIMAL CSS - KEEPS SIDEBAR TOGGLE ====================
hide_streamlit_style = """
<style>
    /* Hide GitHub fork button in header */
    [data-testid="stToolbar"] {
        display: none;
    }
    
    /* Hide deploy button */
    .stDeployButton {
        display: none;
    }
    
    /* Hide Made with Streamlit footer */
    footer {
        visibility: hidden;
    }
    
    /* Hide viewer badge */
    [data-testid="viewerBadge"] {
        display: none !important;
    }
    
    /* Hide manage app button */
    button[title*="Manage app"] {
        display: none !important;
    }
    
    /* Keep header for sidebar toggle */
    header[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.0);
    }
    
    /* Style sidebar */
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Power BI URL
POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiZTFlNTRlNWYtYTQ2OS00NjAwLWE1MGUtNDczZjMzYmI3Y2IzIiwidCI6ImUxNGU3M2ViLTUyNTEtNDM4OC04ZDY3LThmOWYyZTJkNWE0NiIsImMiOjEwfQ%3D%3D&pageName=f4e6760f1492a2bc4b61"

# File Paths
USERS_FILE = Path("users/users.json")
DATA_FILE = Path("data/global_data.xlsx")


# ============ USER FUNCTIONS ============
def load_users():
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Create default admin if file doesn't exist
    default_data = {
        "users": [{
            "username": "admin",
            "password": hash_pw("admin123"),
            "role": "admin",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
    }
    save_users(default_data)
    return default_data


def save_users(data):
    Path("users").mkdir(exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_pw(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_pw(stored, provided):
    try:
        return bcrypt.checkpw(provided.encode(), stored.encode())
    except:
        return False


def login(username, password):
    data = load_users()
    for u in data.get("users", []):
        if u["username"] == username and check_pw(u["password"], password):
            return u["role"]
    return None


def signup(username, password):
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    data = load_users()
    for u in data.get("users", []):
        if u["username"].lower() == username.lower():
            return False, "Username already exists"
    
    data["users"].append({
        "username": username,
        "password": hash_pw(password),
        "role": "user",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(data)
    return True, "Account created"


# ============ DATA FUNCTIONS ============
def load_data():
    try:
        if DATA_FILE.exists():
            return pd.read_excel(DATA_FILE)
    except:
        pass
    
    # Create sample data if file doesn't exist
    df = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"],
        "Category": ["Electronics", "Accessories", "Accessories", "Electronics", "Accessories"],
        "Price": [999.99, 25.50, 49.99, 299.99, 79.99],
        "Stock": [50, 200, 150, 75, 120],
        "Region": ["North", "South", "East", "West", "North"]
    })
    save_data(df)
    return df


def save_data(df):
    Path("data").mkdir(exist_ok=True)
    df.to_excel(DATA_FILE, index=False)


# ============ SESSION STATE ============
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None


# ============ LOGIN PAGE ============
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Global Data Management")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back!")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submitted:
                    if username and password:
                        role = login(username, password)
                        if role:
                            st.session_state.logged_in = True
                            st.session_state.user = username
                            st.session_state.role = role
                            st.success(f"Welcome {username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please enter username and password")
        
        with tab2:
            st.subheader("Create New Account")
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username", placeholder="At least 3 characters")
                new_pass = st.text_input("Choose Password", type="password", placeholder="At least 4 characters")
                confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if submitted:
                    if not new_user or not new_pass or not confirm:
                        st.warning("⚠️ Please fill all fields")
                    elif new_pass != confirm:
                        st.error("❌ Passwords do not match")
                    else:
                        ok, msg = signup(new_user, new_pass)
                        if ok:
                            st.success(f"✅ {msg}! Please login now.")
                        else:
                            st.error(f"❌ {msg}")


# ============ DASHBOARD PAGE ============
def show_dashboard():
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    # Info and Download button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.info("📌 Interactive Power BI Dashboard - Click download to save as PDF")
    
    with col2:
        download_html = f"""
        <a href="{POWERBI_URL}" target="_blank" 
           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 12px 24px; text-decoration: none; 
                  border-radius: 8px; font-weight: bold; display: inline-block;
                  text-align: center; width: 100%;">
           📥 Download
        </a>
        """
        st.markdown(download_html, unsafe_allow_html=True)
    
    # Embed Power BI Dashboard
    dashboard_embed = f"""
    <iframe 
        src="{POWERBI_URL}"
        width="100%"
        height="600"
        style="border: none; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    </iframe>
    """
    components.html(dashboard_embed, height=620)


# ============ VIEW DATA PAGE ============
def show_view_data():
    st.title("📋 View Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cats = ["All"] + list(df["Category"].unique()) if "Category" in df.columns else ["All"]
        cat = st.selectbox("Filter by Category", cats)
    
    with col2:
        regs = ["All"] + list(df["Region"].unique()) if "Region" in df.columns else ["All"]
        reg = st.selectbox("Filter by Region", regs)
    
    with col3:
        search = st.text_input("🔎 Search", placeholder="Type to search...")
    
    # Apply filters
    filtered = df.copy()
    if cat != "All":
        filtered = filtered[filtered["Category"] == cat]
    if reg != "All":
        filtered = filtered[filtered["Region"] == reg]
    if search:
        mask = filtered.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        filtered = filtered[mask]
    
    st.markdown("---")
    
    # Display data
    st.subheader(f"📊 Data Table ({len(filtered)} records)")
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=400)
    
    # Statistics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(filtered))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        if "Price" in filtered.columns:
            st.metric("Avg Price", f"${filtered['Price'].mean():.2f}")
    with col4:
        if "Stock" in filtered.columns:
            st.metric("Total Stock", int(filtered['Stock'].sum()))


# ============ DOWNLOAD DATA PAGE ============
def show_download():
    st.title("📥 Download Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No data available")
        return
    
    # Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    st.caption(f"Showing first 10 of {len(df)} records")
    
    st.markdown("---")
    
    # Download options
    st.subheader("📥 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Excel Format")
        st.write("Best for Excel, Google Sheets")
        buf = BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button(
            "⬇️ Download Excel",
            buf,
            "global_data.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.markdown("#### 📄 CSV Format")
        st.write("Best for data analysis tools")
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "global_data.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )


# ============ ADMIN: UPLOAD DATA ============
def show_upload():
    st.title("📤 Upload Data")
    st.markdown("---")
    
    if st.session_state.role != "admin":
        st.error("❌ Access Denied: Admin privileges required")
        st.info("Only administrators can upload data")
        return
    
    st.info("📋 Upload CSV or Excel file to replace current data")
    
    file = st.file_uploader("Choose file", type=["csv", "xlsx", "xls"])
    
    if file:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            st.success(f"✅ File loaded: {len(df)} records, {len(df.columns)} columns")
            
            # Preview
            st.subheader("Preview")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Confirm buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Upload", type="primary", use_container_width=True):
                    save_data(df)
                    st.success("Data uploaded successfully!")
                    st.balloons()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


# ============ ADMIN: MANAGE DATA ============
def show_manage():
    st.title("📊 Manage Data")
    st.markdown("---")
    
    if st.session_state.role != "admin":
        st.error("❌ Access Denied: Admin privileges required")
        return
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        if st.button("Create Sample Data"):
            save_data(load_data())
            st.rerun()
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Records", len(df))
    col2.metric("Columns", len(df.columns))
    if "Price" in df.columns:
        col3.metric("Avg Price", f"${df['Price'].mean():.2f}")
    if "Stock" in df.columns:
        col4.metric("Total Stock", int(df['Stock'].sum()))
    
    st.markdown("---")
    
    # Edit data
    st.subheader("✏️ Edit Data")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="data_editor")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            save_data(edited)
            st.success("Changes saved!")
            st.rerun()
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.rerun()


# ============ ADMIN: VIEW USERS ============
def show_users():
    st.title("👥 Registered Users")
    st.markdown("---")
    
    if st.session_state.role != "admin":
        st.error("❌ Access Denied")
        return
    
    data = load_users()
    users = data.get("users", [])
    
    if not users:
        st.warning("No users found")
        return
    
    # Create user dataframe
    user_data = []
    for u in users:
        user_data.append({
            "Username": u["username"],
            "Role": u["role"].upper(),
            "Created": u.get("created", "N/A")
        })
    
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True, hide_index=True)
    
    # User statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", len(users))
    col2.metric("Admins", len([u for u in users if u["role"] == "admin"]))
    col3.metric("Regular Users", len([u for u in users if u["role"] == "user"]))


# ============ MAIN APPLICATION ============
def main():
    # Initialize session
    if not st.session_state.logged_in:
        show_login()
        return
    
    # SIDEBAR NAVIGATION
    with st.sidebar:
        st.title("📋 Navigation")
        st.markdown("---")
        
        # User info
        st.markdown(f"**👤 User:** {st.session_state.user}")
        st.markdown(f"**🔑 Role:** {st.session_state.role.upper()}")
        st.markdown("---")
        
        # Navigation menu based on role
        st.subheader("📍 Menu")
        
        if st.session_state.role == "admin":
            # Admin menu
            page_options = {
                "📊 Dashboard": "dashboard",
                "📋 View Data": "view",
                "📥 Download Data": "download",
                "📤 Upload Data": "upload",
                "📊 Manage Data": "manage",
                "👥 View Users": "users"
            }
        else:
            # User menu
            page_options = {
                "📊 Dashboard": "dashboard",
                "📋 View Data": "view",
                "📥 Download Data": "download"
            }
        
        # Page selection
        selected = st.radio(
            "Select Page",
            list(page_options.keys()),
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
    
    # MAIN CONTENT AREA - Page routing
    page_key = page_options[selected]
    
    if page_key == "dashboard":
        show_dashboard()
    elif page_key == "view":
        show_view_data()
    elif page_key == "download":
        show_download()
    elif page_key == "upload":
        show_upload()
    elif page_key == "manage":
        show_manage()
    elif page_key == "users":
        show_users()
    
    # Footer
    st.markdown("---")
    st.caption(f"© 2024 Global Data Management System | Logged in as: {st.session_state.user}")


# Run the app
if __name__ == "__main__":
    main()