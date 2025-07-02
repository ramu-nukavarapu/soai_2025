import streamlit as st
from utils.fetch_data import fetch_corpus_data, fetch_gitlab_users, fetch_registrations_data

# Configuration
st.set_page_config(
    page_title="Unified SOAI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get secrets
DB_DEV_URL = st.secrets["DB_DEV_URL"]
DB_LEAD_URL = st.secrets["DB_LEAD_URL"]
GITLAB_URL = st.secrets["GITLAB_URL"]
CORPUS_URL = st.secrets["CORPUS_URL"]

DB_API = st.secrets["DB_API"]
GITLAB_API = st.secrets["GITLAB_API"]
CORPUS_API = st.secrets["CORPUS_API"]

# Headers
DB_HEADERS = {
    "accept": "application/json",
    "xc-token": DB_API
}
GITLAB_HEADERS = {"PRIVATE-TOKEN": GITLAB_API}
CORPUS_HEADERS = {
    "Authorization": 'Bearer ' + CORPUS_API,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'corpus_users' not in st.session_state:
        st.session_state.corpus_users = None
    if 'aidev' not in st.session_state:
        st.session_state.aidev = None
    if 'techlead' not in st.session_state:
        st.session_state.techlead = None
    if 'gitlab_users' not in st.session_state:
        st.session_state.gitlab_users = None

# Home page
def home_page():
    st.markdown('<h1 class="main-header">Unified SOAI Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧑‍🎓 Intern Analytics Dashboard
        Track and analyze intern registration and engagement metrics.

        **Features:**
        - Cohort-wise segregation and filtering
        - Multiple views:
            - Tabular View
            - Sankey View
            - Sunburst View
        - Top colleges by number of registrations
        - Graphical analysis:
            - College-wise registrations
            - Gender distribution
            - Age distribution
        """)

    with col2:
        st.markdown("""
        ### 🧭 Onboarding Dashboard
        Monitor onboarding status and detailed analytics.

        **Features:**
        - Cohort-wise onboarding analysis
        - Segregated analytics:
            - GitLab Analytics
            - Corpus Analytics
        - College-wise breakdowns
        - User filtering:
            - View users needing accounts
            - Multi-select colleges to retrieve specific user details
        """)

    
    st.markdown("---")
    
    # Overview metrics
    st.markdown("### 📊 Data Overview")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if not st.session_state.aidev or not st.session_state.techlead:
            with st.spinner("Fetching registration data..."):
                try:
                    st.session_state.aidev, st.session_state.techlead = fetch_registrations_data(
                        DB_DEV_URL, DB_LEAD_URL, DB_HEADERS
                    )
                except Exception as e:
                    st.error(f"Error fetching registration data: {str(e)}")
                    st.session_state.aidev = []
                    st.session_state.techlead = []
        
        if st.session_state.aidev is not None and st.session_state.techlead is not None:
            st.metric("Total AIDEV Registrations", len(st.session_state.aidev))
            st.metric("Total TECHLEAD Registrations", len(st.session_state.techlead))
        else:
            st.warning("Registration data not available")
    
    with col2:
        if not st.session_state.gitlab_users:
            with st.spinner("Fetching GitLab users..."):
                try:
                    st.session_state.gitlab_users = fetch_gitlab_users(GITLAB_URL, GITLAB_HEADERS)
                except Exception as e:
                    st.error(f"Error fetching GitLab data: {str(e)}")
                    st.session_state.gitlab_users = []
        
        if st.session_state.gitlab_users is not None:
            st.metric("Total GitLab Users", len(st.session_state.gitlab_users))
        else:
            st.warning("GitLab data not available")
    
    with col3:
        if not st.session_state.corpus_users:
            with st.spinner("Fetching corpus users..."):
                try:
                    st.session_state.corpus_users = fetch_corpus_data(CORPUS_URL, CORPUS_HEADERS)
                except Exception as e:
                    st.error(f"Error fetching corpus data: {str(e)}")
                    st.session_state.corpus_users = []
        
        if st.session_state.corpus_users is not None:
            st.metric("Total Corpus App Users", len(st.session_state.corpus_users))
        else:
            st.warning("Corpus data not available")

def main():
    init_session_state()
    home_page()

if __name__ == "__main__":
    main()