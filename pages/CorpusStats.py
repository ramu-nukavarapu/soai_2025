import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

from utils.corpus_records import generate_contribution_data
from utils.load_session_data import wait_for_data


def corpus_stats_page():
    wait_for_data(['aidev', 'techlead', "corpus_users", "corpus_user_records"])
    st.title("🏫 College Overview Dashboard")

    if "cohort" not in st.session_state: 
        st.session_state.cohort = "cohort1"
    if "intern" not in st.session_state: 
        st.session_state.intern = "aidev"

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Select Intern Type")
        selected_intern = st.selectbox(
            "Choose a Intern type:",
            ["aidev", "techlead", "residential"],
            key="view_selector"
        )
        st.session_state.intern = selected_intern

    with col2:
        st.subheader("Select Cohort")
        selected_cohort = st.selectbox("Choose a cohort:", ["cohort1", "cohort2", "residential"], key="cohort_selector")
        st.session_state.cohort = selected_cohort
        st.subheader(f"Selected Cohort: {st.session_state.cohort.upper()}")
    

    st.info("📊 Loading existing contributions data...")
    try:
        df_final = generate_contribution_data(st.session_state.intern, st.session_state.cohort)
    except Exception as e:
        st.error(f"Error loading contributions data: {e}")
        return
    
    # AG Grid 1: College-wise Summary
    st.markdown("### 📊 AG Grid 1: College-wise Summary")
    
    # Calculate college-wise statistics
    college_stats = df_final.groupby('College').agg({
        'Name': 'count',  # Total students
        'Registration status': lambda x: (x == 'Y').sum()  # Registered users
    }).rename(columns={
        'Name': 'No of Students',
        'Registration status': 'No of Registered Users'
    })
    
    college_stats['No of Unregistered Users'] = college_stats['No of Students'] - college_stats['No of Registered Users']
    college_stats = college_stats.reset_index()
    college_stats.rename(columns={'College': 'Total Colleges'}, inplace=True)
    
    # Configure AG Grid for college summary
    gb1 = GridOptionsBuilder.from_dataframe(college_stats)
    gb1.configure_pagination(paginationAutoPageSize=True)
    gb1.configure_side_bar()
    gb1.configure_default_column(sortable=True, filter=True, resizable=True)
    gb1.configure_selection(selection_mode="single", use_checkbox=False)
    
    grid_options1 = gb1.build()
    
    # Display AG Grid 1
    grid_response1 = AgGrid(
        college_stats,
        gridOptions=grid_options1,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        height=400,
        width='100%'
    )
    
    # AG Grid 2: Student Details for Selected College
    st.markdown("### 📋 AG Grid 2: Student Details")
    
    # Get selected college
    selected_college = None
    if (grid_response1['selected_rows'] is not None and 
        not grid_response1['selected_rows'].empty):
        # Convert DataFrame to dict and get the first row
        selected_row = grid_response1['selected_rows'].iloc[0].to_dict()
        selected_college = selected_row['Total Colleges']
        st.info(f"📍 Showing details for: **{selected_college}**")
    else:
        st.info("👆 Please select a college from the table above to view student details")
        return
    
    # Filter data for selected college
    filtered_df = df_final[df_final['College'] == selected_college].copy()
    
    # Prepare data for AG Grid 2
    student_details = filtered_df[[
        'Name', 'Registration status', 'total contributions', 'total hours',
        'video', 'video_duration', 'audio', 'audio_duration', 'image', 'text'
    ]].copy()
    
    student_details.rename(columns={
        'Registration status': 'Status of App Registration (Y/N)',
        'total contributions': 'Total No of Contributions',
        'image': 'Image',
        'video': 'Video',
        'audio': 'Audio',
        'text': 'Text'
    }, inplace=True)
    
    # Configure AG Grid for student details
    gb2 = GridOptionsBuilder.from_dataframe(student_details)
    gb2.configure_pagination(paginationAutoPageSize=True)
    gb2.configure_side_bar()
    gb2.configure_default_column(sortable=True, filter=True, resizable=True)
    
    # Configure specific columns
    gb2.configure_column("Name", pinned="left", width=200)
    gb2.configure_column("Total No of Contributions", type=["numericColumn"], width=180)
    gb2.configure_column("Image", type=["numericColumn"], width=100)
    gb2.configure_column("Video", type=["numericColumn"], width=100)
    gb2.configure_column("Audio", type=["numericColumn"], width=100)
    gb2.configure_column("Text", type=["numericColumn"], width=100)
    
    grid_options2 = gb2.build()
    
    # Display AG Grid 2
    grid_response2 = AgGrid(
        student_details,
        gridOptions=grid_options2,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        height=600,
        width='100%'
    )
    
    # Export options
    st.markdown("### 📥 Export Data")

    csv_data = student_details.to_csv(index=False)
    st.download_button(
        label="📄 Download Student Details as CSV",
        data=csv_data,
        file_name=f"{selected_college.replace(' ', '_')}_student_details.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    if not st.session_state.get("authentication_status"):
        st.warning("Please log in to access this page.")
        st.stop()
    else:
        corpus_stats_page()