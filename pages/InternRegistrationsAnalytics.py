import streamlit as st
import pandas as pd

from utils.internAnalytics import display_data, display_sankey_diagram, display_sunburst_diagram
from utils.load_session_data import get_aidev_data, get_techlead_data, wait_for_data

st.title("🎓 Intern Registrations Dashboard")

def registrations_page():
    wait_for_data(['aidev', 'techlead']) 

    if "cohort_type" not in st.session_state: 
        st.session_state.cohort_type = "cohort1"
    if "view_type" not in st.session_state: 
        st.session_state.view_type = "tabular"
    if "data" not in st.session_state:
        st.session_state.data = None

    ai_data = get_aidev_data()
    techlead_data = get_techlead_data()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Select View Type")
        selected_view = st.selectbox(
            "Choose a view type:",
            ["tabular", "sankey", "sunburst"],
            format_func=lambda x: {"tabular": "Tabular View", "sankey": "Sankey Diagram View", "sunburst": "Sunburst View"}[x],
            key="view_selector"
        )
        st.session_state.view_type = selected_view

    with col2:
        st.subheader("Select Cohort")
        selected_cohort = st.selectbox("Choose a cohort:", ["cohort1", "cohort2"], key="cohort_selector")
        st.session_state.cohort_type = selected_cohort
        st.subheader(f"Selected Cohort: {st.session_state.cohort_type.upper()}")
    

    # Refresh button to manually clear cache and re-fetch data
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # --- DISPLAY CONTENT BASED ON VIEW TYPE ---
    aidev_ranges = {
        "cohort1": (0, 25000),
        "cohort2": (25001, 44126),
    }

    techlead_ranges = {
        "cohort1": (0, 1730),
        "cohort2": (1731, 2348),
    }

    aidev_df = pd.DataFrame(ai_data)
    techlead_df = pd.DataFrame(techlead_data)

    a_start, a_end = aidev_ranges[st.session_state.cohort_type]
    t_start, t_end = techlead_ranges[st.session_state.cohort_type]

    aidev_filtered = aidev_df[(aidev_df['Id'] >= a_start) & (aidev_df['Id'] <= a_end)]
    techlead_filtered = techlead_df[(techlead_df['Id'] >= t_start) & (techlead_df['Id'] <= t_end)]

    aidev_filtered = aidev_filtered.to_dict(orient="records")
    techlead_filtered = techlead_filtered.to_dict(orient="records")

    if ai_data is not None and techlead_data is not None:
        if st.session_state.view_type == "tabular":
            st.subheader("Select Intern Type for Tabular View")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 AI Developer Intern", use_container_width=True):
                    st.session_state.intern_type = "ai"
                    st.session_state.data = aidev_filtered
            with col2:
                if st.button("🧑‍💻 Tech Lead Intern", use_container_width=True):
                    st.session_state.intern_type = "techlead"
                    st.session_state.data = techlead_filtered

            if st.session_state.data is not None:
                display_data(st.session_state.data, st.session_state.cohort_type, st.session_state.intern_type)
            else:
                st.info("Please select an intern type to load the Tabular View.")

        elif st.session_state.view_type == "sankey":
            # The data is already loaded, so we just pass it.
            display_sankey_diagram(ai_data, techlead_data, st.session_state.cohort_type)

        elif st.session_state.view_type == "sunburst":
            display_sunburst_diagram(ai_data, techlead_data, st.session_state.cohort_type)
    else:
        st.error("Could not fetch the required data. Please check your API connection and secrets, then click the Refresh button.")
    
if __name__ == "__main__":
    registrations_page()