import streamlit as st
import pandas as pd
import altair as alt

from utils.load_session_data import get_aidev_data, get_corpus_users, get_gitlab_users, get_techlead_data, wait_for_data
from utils.onboardingAnalytics import aggregate_data_collegewise, filter_no_corpus_accounts, filter_no_gitlab_accounts, update_data_with_corpus_app, update_users_with_gitlabinfo

st.title("🔍 Onboarding Dashboard for AIDEV & TechLeads")

def onboarding_page():
        wait_for_data(['aidev', 'techlead', 'gitlab_users', 'corpus_users']) 

        if 'selected_group' not in st.session_state:
            st.session_state.selected_group = "aidev"
        if 'selected_analytics' not in st.session_state:
            st.session_state.selected_analytics = "gitlab_analyics"
        if "cohort_type" not in st.session_state: 
            st.session_state.cohort_type = "cohort1"

        ai_data = get_aidev_data()
        techlead_data = get_techlead_data()
        gitlab_users = get_gitlab_users()
        corpus_users = get_corpus_users()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Select Analytics")
            selected_Analytics = st.selectbox("Choose a Analytics:", ["gitlab_analytics", "corpus_analytics"], key="analytics_selector")
            st.session_state.selected_analytics = selected_Analytics
            st.subheader(f"Selected Analytics: {st.session_state.selected_analytics.upper()}")

        with col2:
            st.subheader("Select Cohort")
            selected_cohort = st.selectbox("Choose a cohort:", ["cohort1", "cohort2"], key="cohort_selector")
            st.session_state.cohort_type = selected_cohort
            st.subheader(f"Selected Cohort: {st.session_state.cohort_type.upper()}")

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

        if st.session_state.selected_analytics == "corpus_analytics":
            aidev_updated, techlead_updated = update_data_with_corpus_app(
                aidev_filtered, techlead_filtered, corpus_users
            )
        else:
            aidev_updated, techlead_updated = update_users_with_gitlabinfo(gitlab_users, aidev_filtered, techlead_filtered)

        aidev_summary, techlead_summary = aggregate_data_collegewise(aidev_updated, techlead_updated, st.session_state.selected_analytics)
        st.session_state.aidev_df = pd.DataFrame(aidev_summary)
        st.session_state.techlead_df = pd.DataFrame(techlead_summary)

        # --- Only continue if data is fetched ---
        if st.session_state.corpus_users is not None:

            st.subheader("Select User Group")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧠 AI Developers"):
                    st.session_state.selected_group = 'aidev'
            with col2:
                if st.button("🛠️ Tech Leads"):
                    st.session_state.selected_group = 'techlead'

            if st.session_state.selected_group is None:
                st.warning("Please select a group to continue.")
                st.stop()

            selected_df = (
                st.session_state.aidev_df if st.session_state.selected_group == 'aidev'
                else st.session_state.techlead_df
            )
            group_label = "AI Developers" if st.session_state.selected_group == 'aidev' else "Tech Leads"

            if selected_df is None or selected_df.empty:
                st.warning("No data found for selected group.")
                st.stop()

            # Clean & preprocess
            selected_df.fillna('Unknown', inplace=True)

            for col in ['total_registrations', 'no_of_accounts_created', 'no_of_accounts_needed']:
                selected_df[col] = pd.to_numeric(selected_df[col], errors='coerce').fillna(0).astype(int)

            selected_df = selected_df.sort_values(by='total_registrations', ascending=False)

            # Sidebar slider
            top_n = st.sidebar.slider("Show Top N Affiliations", min_value=1, max_value=10, value=5)
            top_df = selected_df.head(top_n)

            # Melt for bar chart
            chart_data = pd.melt(
                top_df,
                id_vars=['Affiliation'],
                value_vars=['no_of_accounts_created', 'no_of_accounts_needed'],
                var_name='Status',
                value_name='Count'
            )

            chart_data['Status Label'] = chart_data['Status'].map({
                'no_of_accounts_created': 'Created',
                'no_of_accounts_needed': 'Needs'
            })

            # Altair grouped bar chart
            grouped_bar = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Affiliation:N', title='Affiliation', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Count:Q'),
                color=alt.Color('Status Label:N', scale=alt.Scale(domain=['Created', 'Needs'], range=['#4CAF50', '#F44336'])),
                tooltip=['Affiliation', 'Status Label', 'Count'],
                xOffset='Status Label:N'
            ).properties(
                width=900,
                height=400,
                title=f"Top {top_n} Affiliations - {group_label}"
            )

            st.altair_chart(grouped_bar, use_container_width=True)

            # --- Search Interface ---
            st.subheader("🔍 Search for a College or Organization")
            search_term = st.text_input("Type to search affiliation:", "")
            filtered_options = selected_df[selected_df['Affiliation'].str.contains(search_term, case=False, na=False)]['Affiliation'].unique()

            if len(filtered_options) > 0:
                selected_affiliation = st.selectbox("Matching affiliations:", options=filtered_options)
                selected_data = selected_df[selected_df['Affiliation'] == selected_affiliation].iloc[0]

                st.markdown(f"### 📊 Account Status for: {selected_affiliation}")
                st.metric("Total Registrations: ",selected_data['total_registrations'])
                detail_df = pd.DataFrame({
                    'Status': ['Created', 'Needs'],
                    'Count': [selected_data['no_of_accounts_created'], selected_data['no_of_accounts_needed']],
                    'Color': ['#4CAF50', '#F44336']
                })

                detail_chart = alt.Chart(detail_df).mark_bar().encode(
                    x=alt.X('Status:N'),
                    y=alt.Y('Count:Q'),
                    color=alt.Color('Color:N', scale=None),
                    tooltip=['Status', 'Count']
                ).properties(width=300, height=300)

                st.altair_chart(detail_chart)
            elif search_term:
                st.warning("No matching affiliations found.")
            
            if st.session_state.selected_analytics == "corpus_analytics":
                st.subheader("Interns who need to create account in corpus app")
            else:
                st.subheader("Interns who need to create account in gitlab")
            indices = ['Full Name','Affiliation (College/Company/Organization Name)']
            if st.session_state.selected_group == 'aidev':
                if st.session_state.selected_analytics == "corpus_analytics":
                    aidev_missing = filter_no_corpus_accounts(aidev_updated)
                    st.metric("AI Developers need to create accounts in corpus app",len(aidev_missing))
                    data = pd.DataFrame(aidev_missing)
                    data = data[indices]
                else:
                    aidev_missing = filter_no_gitlab_accounts(aidev_updated)
                    st.metric("AI Developers need to create accounts in gitlab",len(aidev_missing))
                    indices.append('gitlab_username')
                    data = pd.DataFrame(aidev_updated)
                    data = data[indices]

                st.dataframe(data, use_container_width=True)

                selected_colleges = st.multiselect("Filter by College(s)", options=data['Affiliation (College/Company/Organization Name)'].unique(), default=[])
                if selected_colleges:
                    filtered_data = data[data['Affiliation (College/Company/Organization Name)'].isin(selected_colleges)]
                    if filtered_data.empty:
                        st.warning("No data available for the selected colleges.")
                    else:
                        st.dataframe(filtered_data, use_container_width=True)   
                        if st.session_state.selected_analytics == "gitlab_analytics":
                            csv = filtered_data.to_csv(index=False).encode('utf-8')
                            st.download_button(label="Download users with gitlab usernames", data=csv, file_name=f'{selected_colleges[0]}-{st.session_state.selected_group}-data.csv')
            else:
                if st.session_state.selected_analytics == "corpus_analytics":
                    techlead_missing = filter_no_corpus_accounts(techlead_updated)
                    st.metric("Tech Leads need to create accounts in corpus app",len(techlead_missing))
                    data = pd.DataFrame(techlead_missing)
                    data = data[indices]
                else:
                    techlead_missing = filter_no_gitlab_accounts(techlead_updated)
                    st.metric("Tech Leads need to create accounts in gitlab",len(techlead_missing))
                    indices.append('gitlab_username')

                    data = pd.DataFrame(techlead_updated)
                    data = data[indices]

                st.dataframe(data, use_container_width=True)

                selected_colleges = st.multiselect("Filter by College(s)", options=data['Affiliation (College/Company/Organization Name)'].unique(), default=[])

                if selected_colleges:
                    filtered_data = data[data['Affiliation (College/Company/Organization Name)'].isin(selected_colleges)]
                    if filtered_data.empty:
                        st.warning("No data available for the selected colleges.")
                    else:
                        st.dataframe(filtered_data, use_container_width=True)
                        if st.session_state.selected_analytics == "gitlab_analytics":
                            csv = filtered_data.to_csv(index=False).encode('utf-8')
                            st.download_button(label="Download users with gitlab usernames", data=csv, file_name=f'{selected_colleges[0]}-{st.session_state.selected_group}-data.csv')
        else:
            st.info("Click the button above to fetch users data.")

if __name__ == "__main__":
    onboarding_page()