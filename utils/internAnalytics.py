# script.py (Clean and Verified Version)

import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import re
import plotly.graph_objects as go
import altair as alt
import plotly.express as px
from collections import Counter

# --- HELPER FUNCTION ---
def clean_college_name(name):
    # Your proven cleaning function...
    # (The full function is here)
    name = str(name).upper().strip()
    name = re.sub(r'\s*\(.*?\)\s*$', '', name)
    name = re.sub(r'\s*\*.+$', '', name)
    if ' - ' in name: name = name.split(' - ', 1)[1].strip()
    name = name.replace("INSTITUTE OF SCI AND TECHNOLOGY", "INSTITUTE OF SCIENCE AND TECHNOLOGY")
    name = name.replace("EDNL SOC GRP OF INSTNS", "EDUCATIONAL SOCIETY GROUP OF INSTITUTIONS")
    name = name.replace("GEETANJALI", "GEETHANJALI")
    name = name.replace("O U COLLEGE OF ENGINEERING HYDERABAD", "OSMANIA UNIVERSITY COLLEGE OF ENGINEERING")
    name = name.replace("VIGNANA BHARATHI", "VIGNAN BHARATHI")
    name = re.sub(r'\bENGG\b', 'ENGINEERING', name)
    name = re.sub(r'\bTECH\b', 'TECHNOLOGY', name)
    name = re.sub(r'\bSCI\b', 'SCIENCE', name)
    name = re.sub(r'\bINST\b', 'INSTITUTE', name)
    name = re.sub(r'\bINSTT\b', 'INSTITUTE', name)
    name = re.sub(r'\bCOLL\b', 'COLLEGE', name)
    name = re.sub(r'\bWOMENS\b', 'FOR WOMEN', name)
    name = re.sub(r"\bWOMEN'S\b", 'FOR WOMEN', name)
    name = name.replace("COLLEGEEGE", "COLLEGE")
    if "GITAM" in name: name = "GITAM UNIVERSITY"
    if "MALLA REDDY" in name or "MALLAREDDY" in name:
        if name == "MALLAREDDY ENGINEERING COLLEGE": name = "MALLA REDDY COLLEGE OF ENGINEERING"
        if name == "MALLAREDDY INST OF ENGG AND TECHNOLOGY": name = "MALLAREDDY INSTITUTE OF ENGINEERING AND TECHNOLOGY"
        if name == "MALLAREDDY INST OF TECHNOLOGY AND SCI": name = "MALLAREDDY INSTITUTE OF TECHNOLOGY AND SCIENCE"
        if name == "MALLAREDDY COLLEGE OF ENGG TECHNOLOGY": name = "MALLA REDDY COLLEGE OF ENGINEERING TECHNOLOGY"
        if name == "MALLA REDDY ENGG COLLEGE FOR WOMEN": name = "MALLA REDDY ENGINEERING COLLEGE FOR WOMEN"
        is_mrew = "FOR WOMEN" in name
        is_mrem = "MANAGEMENT SCIENCES" in name
        is_mrits = "INSTITUTE OF TECHNOLOGY AND SCIENCE" in name
        is_mru = "UNIVERSITY" in name
        is_mrcet = "COLLEGE OF ENGINEERING TECHNOLOGY" in name and "MALLA REDDY" in name
        is_mriet = "INSTITUTE OF ENGINEERING AND TECHNOLOGY" in name and "MALLAREDDY" in name and not is_mrits
        is_mrit_short = "INSTITUTE OF TECHNOLOGY" in name and "MALLAREDDY" in name and not is_mrits and not is_mriet
        if is_mrew and not is_mrem: name = "MALLA REDDY COLLEGE OF ENGINEERING FOR WOMEN"
        elif is_mrem: name = "MALLA REDDY ENGINEERING COLLEGE AND MANAGEMENT SCIENCES"
        elif is_mrits: name = "MALLAREDDY INSTITUTE OF TECHNOLOGY AND SCIENCE"
        elif is_mru: name = "MALLA REDDY UNIVERSITY"
        elif is_mrcet: name = "MALLA REDDY COLLEGE OF ENGINEERING TECHNOLOGY"
        elif is_mriet: name = "MALLAREDDY INSTITUTE OF ENGINEERING AND TECHNOLOGY"
        elif is_mrit_short: name = "MALLAREDDY INSTITUTE OF TECHNOLOGY"
        elif "MALLA REDDY COLLEGE OF ENGINEERING" in name and not any([is_mrew, is_mrem, is_mrcet, is_mru, is_mrits, is_mriet]): name = "MALLA REDDY COLLEGE OF ENGINEERING"
    name = name.replace(" FOR WOMEN", " FOR WOMEN")
    name = name.rstrip(',.')
    cleaned = ' '.join(name.split())
    return cleaned.strip()

def display_data(data):
    st.title("🏫 Intern Registration Dashboard")

    # Convert raw data to DataFrame
    df = pd.DataFrame(data)

    # Clean and rename columns
    df.rename(columns={
        'Affiliation (College/Company/Organization Name)': 'College',
        'Full Name': 'Name',
        'Id': 'StudentID'
    }, inplace=True)

    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['Gender'] = df['Gender'].str.strip().str.title()
    df['College'] = df['College'].str.strip()

    # 🔢 College-wise Summary
    st.markdown("### 📊 College-wise Registrations")

    college_summary = df.groupby('College').agg({
        'StudentID': 'count'
    }).rename(columns={'StudentID': 'Total Registrations'}).reset_index()

    college_summary = college_summary.sort_values(by='Total Registrations', ascending=False)

    # AG Grid setup for College Summary
    gb1 = GridOptionsBuilder.from_dataframe(college_summary)
    gb1.configure_pagination(paginationAutoPageSize=True)
    gb1.configure_side_bar()
    gb1.configure_default_column(sortable=True, filter=True, resizable=True)
    gb1.configure_selection(selection_mode="single", use_checkbox=False)
    grid_options1 = gb1.build()

    # Render AG Grid 1
    grid_response1 = AgGrid(
        college_summary,
        gridOptions=grid_options1,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        height=400,
        width='100%'
    )

    # 📋 Show student data if a college is selected
    st.markdown("### 👨‍🎓 Students from Selected College")

    selected_college = None
    selected_rows = grid_response1.get("selected_rows", [])

    if selected_rows is not None and not selected_rows.empty:
        selected_college = selected_rows.iloc[0]['College']
        st.success(f"📍 Showing students from: **{selected_college}**")
    else:
        st.info("👆 Please select a college from the table above to view student details.")
        return

    # Filter student data for selected college
    student_df = df[df['College'] == selected_college].copy()

    student_display = student_df[['StudentID', 'Name', 'College', 'Age', 'Gender', 'Contact Number', 'Email Address']].copy().rename(columns={
        'Contact number': 'Phone',
        'Id': 'Student ID'
    })

    # AG Grid setup for Student Details
    gb2 = GridOptionsBuilder.from_dataframe(student_display)
    gb2.configure_pagination(paginationAutoPageSize=True)
    gb2.configure_side_bar()
    gb2.configure_default_column(sortable=True, filter=True, resizable=True)
    gb2.configure_column("Name", pinned="left", width=200)
    grid_options2 = gb2.build()

    # Render AG Grid 2
    AgGrid(
        student_display,
        gridOptions=grid_options2,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        height=600,
        width='100%'
    )
    # Age Analysis
    st.header("🎂 Registrations by Age")
    age_df = df.dropna(subset=['Age'])
    bins = [15, 18, 21, 24, 27, 30, float('inf')]
    labels = ['15-18', '19-21', '22-24', '25-27', '28-30', '30-above']
    age_df['AgeGroup'] = pd.cut(age_df['Age'], bins=bins, labels=labels, right=False)

    age_group_data = age_df.groupby('AgeGroup', observed=False)['StudentID'].count().reset_index()
    age_group_data.rename(columns={'StudentID': 'TotalStudents'}, inplace=True)

    st.dataframe(age_group_data, use_container_width=True)

    age_chart = alt.Chart(age_group_data).mark_bar().encode(
        x=alt.X('AgeGroup:N', title='Age Group'),
        y=alt.Y('TotalStudents:Q', title='Total Students'),
        color='AgeGroup:N',
        tooltip=['AgeGroup', 'TotalStudents']
    ).properties(width=700, height=400)

    st.altair_chart(age_chart, use_container_width=True)

    # Gender Analysis
    st.header("🚻 Registrations by Gender")
    gender_data = df.groupby('Gender')['StudentID'].count().reset_index()
    gender_data.rename(columns={'StudentID': 'TotalStudents'}, inplace=True)

    st.dataframe(gender_data, use_container_width=True)

    gender_chart = alt.Chart(gender_data).mark_bar().encode(
        x=alt.X('Gender:N', title='Gender'),
        y=alt.Y('TotalStudents:Q', title='Total Students'),
        color='Gender:N',
        tooltip=['Gender', 'TotalStudents']
    ).properties(width=700, height=400)

    st.altair_chart(gender_chart, use_container_width=True)



# --- SANKEY VIEW FUNCTION ---
def display_sankey_diagram(ai_data, techlead_data, cohort_type):
    st.title("College Intern Imbalance: AI Dev Interns vs. Tech Leads")
    st.markdown("""
    **Ideal Ratio: 1 Tech Lead : 25 AI Dev Interns**
    **Link Colors:**
    - <span style='color:red; font-weight:bold;'>Red Link:</span> College primarily needs Tech Leads.
    - <span style='color:blue; font-weight:bold;'>Blue Link:</span> College primarily needs AI Dev Interns.
    """, unsafe_allow_html=True)

    # --- NEW: WIDGET TO SELECT DATA SCOPE ---
    sankey_scope = st.radio(
        "Select Data Scope:",
        ("Selected Cohort", "Combined (Both Cohorts)"),
        horizontal=True,
        key="sankey_scope_selector"
    )

    top_n = st.slider("Select number of top colleges to view", min_value=10, max_value=100, value=50, step=5, key="sankey_top_n_slider")

    df_devs = pd.DataFrame(ai_data)
    df_tech_leads = pd.DataFrame(techlead_data)
    if sankey_scope == "Selected Cohort":
        st.info(f"Displaying the mapping for the Top {top_n} colleges in {cohort_type.upper()}.")
        ai_filter, tl_filter = 25000, 1730
        if 'Id' in df_devs.columns:
            df_devs['Id'] = pd.to_numeric(df_devs['Id'], errors='coerce')
            df_devs.dropna(subset=['Id'], inplace=True)
            df_devs['Id'] = df_devs['Id'].astype(int)
            if cohort_type == "cohort1":
                df_devs = df_devs[df_devs['Id'] <= ai_filter]
            else:
                df_devs = df_devs[df_devs['Id'] > ai_filter]
        else:
            st.error("Error: 'Id' column not found in AI Developer data.")
            return

        if 'Id' in df_tech_leads.columns:
            df_tech_leads['Id'] = pd.to_numeric(df_tech_leads['Id'], errors='coerce')
            df_tech_leads.dropna(subset=['Id'], inplace=True)
            df_tech_leads['Id'] = df_tech_leads['Id'].astype(int)
            if cohort_type == "cohort1":
                df_tech_leads = df_tech_leads[df_tech_leads['Id'] <= tl_filter]
            else:
                df_tech_leads = df_tech_leads[df_tech_leads['Id'] > tl_filter]
        else:
            st.error("Error: 'Id' column not found in Tech Lead data.")
            return
    else: # This block runs if "Combined (Both Cohorts)" is selected
        st.info(f"Displaying the mapping for the Top {top_n} colleges across BOTH cohorts.")
        # We simply do nothing and let the full df_devs and df_tech_leads pass through
        pass



    df_tech_leads.rename(columns={'Affiliation (College/Company/Organization Name)': 'College_Name'}, inplace=True)
    df_devs.rename(columns={'Affiliation (College/Company/Organization Name)': 'College_Name'}, inplace=True)
    df_tech_leads['Cleaned_Name'] = df_tech_leads['College_Name'].apply(clean_college_name)
    df_devs['Cleaned_Name'] = df_devs['College_Name'].apply(clean_college_name)
    df_tech_leads_agg = df_tech_leads.groupby('Cleaned_Name').size().reset_index(name='Tech_Leads')
    df_devs_agg = df_devs.groupby('Cleaned_Name').size().reset_index(name='Developers')
    df_merged = pd.merge(df_tech_leads_agg, df_devs_agg, on='Cleaned_Name', how='outer').fillna(0)
    df_merged['Developers'] = df_merged['Developers'].astype(int)
    df_merged['Tech_Leads'] = df_merged['Tech_Leads'].astype(int)
    filter_out_list = ["NEXTWAVE", "NIAT", "VIT", "KLH", "KUWL", "IIITH", "GOVERNMENT INSTITUTE OF ELECTRONICS", "JNTUH-5 YEAR INTEGRATED MTECH SELF FINANCE", "COLLEGE", "ICFAI", "GD GOENKA UNIVERSITY", "AMRITA VISHWA VIDHYAPEETHAM"]
    df_merged = df_merged[~df_merged['Cleaned_Name'].isin(filter_out_list)]
    df_merged = df_merged[(df_merged['Developers'] > 0) | (df_merged['Tech_Leads'] > 0)].copy()

    top_n_names = df_merged.sort_values(by='Developers', ascending=False).head(top_n)['Cleaned_Name'].tolist()
    df_plot = df_merged[df_merged['Cleaned_Name'].isin(top_n_names)].copy()
    if df_plot.empty:
        st.warning("No data available for the selected colleges.")
        return

    dev_nodes_df = df_plot.sort_values(by='Developers', ascending=False).reset_index(drop=True)
    tl_nodes_df = df_plot.sort_values(by='Tech_Leads', ascending=False).reset_index(drop=True)
    node_labels, node_colors, node_x, node_y = [], [], [], []
    for i, row in dev_nodes_df.iterrows():
        node_labels.append(f"{row.Cleaned_Name} ({int(row.Developers)} Devs)")
        node_colors.append('rgba(173,216,230,0.8)')
        node_x.append(0.01)
        node_y.append(i / max(1, len(dev_nodes_df) - 1))
    for i, row in tl_nodes_df.iterrows():
        node_labels.append(f"{row.Cleaned_Name} ({int(row.Tech_Leads)} TLs)")
        node_colors.append('rgba(255,223,186,0.8)')
        node_x.append(0.99)
        node_y.append(i / max(1, len(tl_nodes_df) - 1))

    dev_map = {name: i for i, name in enumerate(dev_nodes_df['Cleaned_Name'])}
    tl_map = {name: i + len(dev_nodes_df) for i, name in enumerate(tl_nodes_df['Cleaned_Name'])}
    source_indices, target_indices, link_values, link_colors = [], [], [], []
    IDEAL_DEVS_PER_TL = 25
    for _, row in df_plot.iterrows():
        college_name, dev_count, tl_count = row['Cleaned_Name'], row['Developers'], row['Tech_Leads']
        source_indices.append(dev_map[college_name])
        target_indices.append(tl_map[college_name])
        link_values.append(max(1, dev_count))
        if dev_count > tl_count * IDEAL_DEVS_PER_TL:
            link_colors.append('rgba(255, 0, 0, 0.7)')
        else:
            link_colors.append('rgba(0, 0, 255, 0.7)')
    
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(pad=15, thickness=15, line=dict(color="black", width=0.5), label=node_labels, color=node_colors, x=node_x, y=node_y, align="justify"),
        link=dict(source=source_indices, target=target_indices, value=link_values, color=link_colors)
    )])
    
    dynamic_height = max(800, top_n * 25)
    fig.update_layout(font_size=10, height=dynamic_height, margin=dict(l=400, r=400, t=50, b=50))
    st.plotly_chart(fig, use_container_width=True)
    with st.expander(f"View Data for Top {top_n} Colleges"):
        df_to_display = df_plot.sort_values(by="Developers", ascending=False).reset_index(drop=True)
        df_to_display.index = df_to_display.index + 1
        st.dataframe(df_to_display)
# --- SUNBURST VIEW FUNCTION ---

def load_state_mapping_data(ai_csv_path, tech_csv_path):
    ai_state_list = []
    tech_state_list = []
    
    try:
        ai_df_csv = pd.read_csv(ai_csv_path)
        for _, row in ai_df_csv.iterrows():
            record = {
                "Affiliation (College/Company/Organization Name)": row.get("CollegeName", "Unknown"),
                "State": row.get("State", "Unknown"),
                "TotalRegistrations": row.get("TotalRegistrations", 0)
            }
            ai_state_list.append(record)
    except FileNotFoundError:
        st.error(f"State mapping CSV file not found: {ai_csv_path}")
        return None, None
    except Exception as e:
        st.error(f"Error reading state mapping CSV file {ai_csv_path}: {e}")
        return None, None
    
    try:
        tech_df_csv = pd.read_csv(tech_csv_path)
        for _, row in tech_df_csv.iterrows():
            record = {
                "Affiliation (College/Company/Organization Name)": row.get("CollegeName", "Unknown"),
                "State": row.get("State", "Unknown"),
                "TotalRegistrations": row.get("TotalRegistrations", 0)
            }
            tech_state_list.append(record)
    except FileNotFoundError:
        st.error(f"State mapping CSV file not found: {tech_csv_path}")
        return None, None
    except Exception as e:
        st.error(f"Error reading state mapping CSV file {tech_csv_path}: {e}")
        return None, None
    
    return ai_state_list, tech_state_list


def filter_data_by_cohort(ai_data, techlead_data, cohort_typ):
    df_ai = pd.DataFrame(ai_data)
    df_tech = pd.DataFrame(techlead_data)
    
    if cohort_typ == "cohort1":
        df_ai = df_ai[df_ai['Id'] <= 25000]
        df_tech = df_tech[df_tech['Id'] <= 1730]
    else:
        df_ai = df_ai[df_ai['Id'] > 25000]
        df_tech = df_tech[df_tech['Id'] > 1730]
    
    return df_ai.to_dict('records'), df_tech.to_dict('records')


def create_college_to_state_mapping(ai_state_list, tech_state_list):
    ai_dev_college_to_state = {}
    for entry in ai_state_list:
        college_name = entry.get("Affiliation (College/Company/Organization Name)", "Unknown")
        state_name = entry.get("State", "Unknown")
        if college_name and college_name != "Unknown" and state_name and state_name != "Unknown":
            ai_dev_college_to_state[college_name] = state_name
    
    tech_lead_college_to_state = {}
    for entry in tech_state_list:
        college_name = entry.get("Affiliation (College/Company/Organization Name)", "Unknown")
        state_name = entry.get("State", "Unknown")
        if college_name and college_name != "Unknown" and state_name and state_name != "Unknown":
            tech_lead_college_to_state[college_name] = state_name
    combined_mapping = {}
    combined_mapping.update(ai_dev_college_to_state)
    combined_mapping.update(tech_lead_college_to_state)
    
    return combined_mapping


def get_college_counts(filtered_ai_dev, filtered_tech_lead):
    ai_college_names = [entry.get("Affiliation (College/Company/Organization Name)", "Unknown") for entry in filtered_ai_dev]
    tech_college_names = [entry.get("Affiliation (College/Company/Organization Name)", "Unknown") for entry in filtered_tech_lead]
    
    ai_dev_college_counts = Counter(ai_college_names)
    tech_lead_college_counts = Counter(tech_college_names)
    all_college_counts = {}
    for college, count in ai_dev_college_counts.items():
        all_college_counts[college] = all_college_counts.get(college, 0) + count
    for college, count in tech_lead_college_counts.items():
        all_college_counts[college] = all_college_counts.get(college, 0) + count
    
    return ai_dev_college_counts, tech_lead_college_counts, all_college_counts


def prepare_sunburst_data(all_college_counts, tech_lead_college_counts, ai_dev_college_counts, college_to_state_mapping):
    tech_leads_data = []
    ai_interns_data = []
    
    for college_name, total_registrations in all_college_counts.items():
        state_name = college_to_state_mapping.get(college_name, "Unknown")
        
        tech_lead_exists = college_name in tech_lead_college_counts
        ai_dev_exists = college_name in ai_dev_college_counts
        
        if tech_lead_exists:
            tech_leads_data.append({
                'CollegeName': college_name,
                'TotalRegistrations': tech_lead_college_counts[college_name],
                'State': state_name,
                'Level': 'Tech Lead',
                'Label': f"{college_name} (Tech Lead)",
                'StateInfo': state_name,
                'Parent': 'AI Coach 1'
            })
        
        if ai_dev_exists:
            parent_label = f"{college_name} (Tech Lead)" if tech_lead_exists else "Tech Lead (Unassigned)"
            ai_interns_data.append({
                'CollegeName': college_name,
                'TotalRegistrations': ai_dev_college_counts[college_name],
                'State': state_name,
                'Level': 'AI Intern',
                'Label': f"{college_name} (Intern)",
                'StateInfo': state_name,
                'Parent': parent_label
            })
    
    return tech_leads_data, ai_interns_data


def create_intermediate_nodes(ai_interns_data):
    coaches = pd.DataFrame({
        "Label": ["AI Coach 1"],
        "Parent": ["Cohort Owner 1"],
        "TotalRegistrations": [200],
        "Level": ["AI Coach"],
        "StateInfo": ["N/A"]
    })

    cohorts = pd.DataFrame({
        "Label": ["Cohort Owner 1"],
        "Parent": ["Program Lead"],
        "TotalRegistrations": [20],
        "Level": ["Cohort Owner"],
        "StateInfo": ["N/A"]
    })

    program = pd.DataFrame({
        "Label": ["Program Lead"],
        "Parent": [""],
        "TotalRegistrations": [1],
        "Level": ["Program Lead"],
        "StateInfo": ["N/A"]
    })
    unassigned_needed = any(item['Parent'] == "Tech Lead (Unassigned)" for item in ai_interns_data)
    unassigned_df = pd.DataFrame()
    
    if unassigned_needed:
        unassigned_df = pd.DataFrame({
            "Label": ["Tech Lead (Unassigned)"],
            "Parent": ["AI Coach 1"],
            "TotalRegistrations": [0],
            "Level": ["Tech Lead"],
            "StateInfo": ["N/A"]
        })
    
    return coaches, cohorts, program, unassigned_df
def create_sunburst_dataframe(tech_leads_data, ai_interns_data):
    tech_df = pd.DataFrame(tech_leads_data)
    ai_df = pd.DataFrame(ai_interns_data)
    
    coaches, cohorts, program, unassigned_df = create_intermediate_nodes(ai_interns_data)

    dataframes_to_concat = [
        program[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]],
        cohorts[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]],
        coaches[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]],
    ]
    
    if not tech_df.empty:
        dataframes_to_concat.append(tech_df[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]])
    
    if not ai_df.empty:
        dataframes_to_concat.append(ai_df[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]])
    
    if not unassigned_df.empty:
        dataframes_to_concat.append(unassigned_df[["Label", "Parent", "TotalRegistrations", "Level", "StateInfo"]])

    sunburst_df = pd.concat(dataframes_to_concat, ignore_index=True)
    sunburst_df["TotalRegistrations"] = pd.to_numeric(sunburst_df["TotalRegistrations"], errors="coerce").fillna(0)
    
    return sunburst_df, tech_df, ai_df


def get_top_colleges(tech_df, ai_df, selected_state, registration_threshold):
    all_colleges = []
    for _, row in tech_df.iterrows():
        college_data = {
            'CollegeName': row['CollegeName'],
            'TotalRegistrations': row['TotalRegistrations'],
            'StateInfo': row.get('StateInfo', 'N/A')
        }
        all_colleges.append(college_data)

    for _, row in ai_df.iterrows():
        college_data = {
            'CollegeName': row['CollegeName'],
            'TotalRegistrations': row['TotalRegistrations'],
            'StateInfo': row.get('StateInfo', 'N/A')
        }
        all_colleges.append(college_data)
    
    colleges_df = pd.DataFrame(all_colleges)
    
    if colleges_df.empty:
        return pd.DataFrame()
  
    if selected_state and selected_state != "All States":
        colleges_df = colleges_df[colleges_df['StateInfo'] == selected_state]
    

    college_totals = colleges_df.groupby(['CollegeName', 'StateInfo'])['TotalRegistrations'].sum().reset_index()

    filtered_colleges = college_totals[college_totals['TotalRegistrations'] >= registration_threshold]
    

    return filtered_colleges.sort_values('TotalRegistrations', ascending=False)


def filter_sunburst_by_state(sunburst_df, selected_state):
    if selected_state == "All States":
        return sunburst_df
    
    state_filtered = sunburst_df[
        (sunburst_df["StateInfo"] == selected_state) | 
        (sunburst_df["StateInfo"] == "N/A")  
    ].copy()
    
    if len(state_filtered[state_filtered["StateInfo"] == selected_state]) == 0:
        return pd.DataFrame(columns=sunburst_df.columns)
    \
    filtered_df = sunburst_df[
        (sunburst_df["Level"].isin(["Program Lead", "Cohort Owner", "AI Coach"])) |
        (sunburst_df["StateInfo"] == selected_state) |
        ((sunburst_df["Level"] == "Tech Lead") & (sunburst_df["StateInfo"] == "N/A") & (sunburst_df["Label"] == "Tech Lead (Unassigned)"))
    ].copy()
    
 
    unassigned_interns = sunburst_df[
        (sunburst_df["Level"] == "AI Intern") & 
        (sunburst_df["Parent"] == "Tech Lead (Unassigned)") & 
        (sunburst_df["StateInfo"] == selected_state)
    ]
    
    if len(unassigned_interns) == 0:
        filtered_df = filtered_df[filtered_df["Label"] != "Tech Lead (Unassigned)"]
    
    return filtered_df


def create_sunburst_chart(filtered_df, selected_state, selected_college, cohort_typ):
    if filtered_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {selected_state}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(
            height=600,
            title=f"AI Program Structure - {selected_state} ({cohort_typ})",
            title_x=0.5
        )
        return fig
    
   
    hover_template = '<b>%{label}</b><br>State: %{customdata[0]}<br>Registrations: %{value}<extra></extra>'
    sunburst_df_display = filtered_df.copy()
    sunburst_df_display.loc[sunburst_df_display["TotalRegistrations"] == 0, "TotalRegistrations"] = 0.1
    
 
    if selected_college:
        sunburst_df_display['ColorCategory'] = sunburst_df_display['Level'].copy()
        selected_mask = sunburst_df_display["Label"].str.contains(selected_college, na=False, regex=False)
        sunburst_df_display.loc[selected_mask, 'ColorCategory'] = 'Selected College'
        
        color_map = {
            "Program Lead": "#D32F2F",
            "Cohort Owner": "#F57C00",
            "AI Coach": "#FBC02D",
            "Tech Lead": "#388E3C",
            "AI Intern": "#1976D2",
            "Selected College": "#FF6B35"
        }
        color_column = 'ColorCategory'
        chart_title = f"AI Program Structure - {selected_state} ({cohort_typ}) (Highlighting: {selected_college})" if selected_state != "All States" else f"AI Program Structure - All States ({cohort_typ}) (Highlighting: {selected_college})"
    else:
        color_map = {
            "Program Lead": "#D32F2F",
            "Cohort Owner": "#F57C00",
            "AI Coach": "#FBC02D",
            "Tech Lead": "#388E3C",
            "AI Intern": "#1976D2"
        }
        color_column = 'Level'
        chart_title = f"AI Program Structure - {selected_state} ({cohort_typ})" if selected_state != "All States" else f"AI Program Structure - All States ({cohort_typ})"
    
    fig = px.sunburst(
        sunburst_df_display,
        names="Label",
        parents="Parent",
        values="TotalRegistrations",
        color=color_column,
        title=chart_title,
        color_discrete_map=color_map
    )

    fig.update_traces(
        insidetextorientation='radial',
        hovertemplate=hover_template,
        customdata=filtered_df[["StateInfo"]].values
    )
    
    fig.update_layout(
        height=600,
        font_size=12,
        title_x=0.5,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black')
    )
    
    return fig


def display_statistics(sunburst_df, selected_state, selected_college):
    if selected_state != "All States" or selected_college:
        state_data = sunburst_df[sunburst_df["StateInfo"] == selected_state] if selected_state != "All States" else sunburst_df
        
        if selected_college:
            college_data = state_data[state_data["Label"].str.contains(selected_college, na=False, regex=False)]
            display_title = f"Statistics for {selected_college}"
        else:
            college_data = state_data
            display_title = f"Statistics for {selected_state}"
        
        if not college_data.empty:
            st.subheader(display_title)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if selected_college:
                    total_registrations = college_data["TotalRegistrations"].sum()
                    st.metric("Total Registrations", int(total_registrations))
                else:
                    total_colleges = len(state_data[state_data["Level"].isin(["Tech Lead", "AI Intern"])]["Label"].str.replace(" \(.*\)", "", regex=True).unique())
                    st.metric("Colleges in State", total_colleges)
            
            with col2:
                if selected_college:
                    tech_leads = len(college_data[college_data["Level"] == "Tech Lead"])
                    ai_interns = len(college_data[college_data["Level"] == "AI Intern"])
                    st.metric("Tech Leads / AI Interns", f"{tech_leads} / {ai_interns}")
                else:
                    total_registrations = state_data["TotalRegistrations"].sum()
                    st.metric("Total Registrations", int(total_registrations))
            
            with col3:
                if not selected_college:
                    tech_leads = len(state_data[state_data["Level"] == "Tech Lead"])
                    ai_interns = len(state_data[state_data["Level"] == "AI Intern"])
                    st.metric("Tech Leads / AI Interns", f"{tech_leads} / {ai_interns}")


def display_top_colleges_table(top_colleges, registration_threshold, selected_state, cohort_typ):
    if not top_colleges.empty:
        with st.expander(f"View {len(top_colleges)} Colleges with {registration_threshold}+ Registrations ({selected_state})"):
            
            display_top_colleges = top_colleges.copy()
            display_top_colleges['Rank'] = range(1, len(display_top_colleges) + 1)
            display_top_colleges = display_top_colleges[['Rank', 'CollegeName', 'StateInfo', 'TotalRegistrations']]
            display_top_colleges.columns = ['Rank', 'College Name', 'State', 'Total Registrations']
            
            def highlight_registrations(row):
                if row['Total Registrations'] >= 100:
                    return ['background-color: #c8e6c9; color: #1b5e20'] * len(row)
                elif row['Total Registrations'] >= 50:
                    return ['background-color: #fff9c4; color: #f57f17'] * len(row)
                else:
                    return ['background-color: #ffcdd2; color: #c62828'] * len(row)
        
            styled_df = display_top_colleges.style.apply(highlight_registrations, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
            st.markdown("""
            **Color Legend:**
            - 🟢 **Green**: 100+ registrations
            - 🟡 **Yellow**: 50-99 registrations
            - 🔴 **Red**: Less than 50 registrations
            """)
        
            csv_data = display_top_colleges.to_csv(index=False)
            st.download_button(
                label="Download Table as CSV",
                data=csv_data,
                file_name=f"top_colleges_{selected_state}_{registration_threshold}plus_{cohort_typ}.csv",
                mime="text/csv"
            )


def display_data_summary(filtered_df, selected_state):
    with st.expander("View Data Summary"):
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Total Registrations by Level - {selected_state}")
                summary = filtered_df.groupby("Level")["TotalRegistrations"].sum().reset_index()
                st.dataframe(summary, use_container_width=True)
            
            with col2:
                st.subheader("Data Preview")
                display_df = filtered_df[filtered_df["Level"].isin(["Tech Lead", "AI Intern"])].head(10)
                st.dataframe(display_df, use_container_width=True)
        
            if selected_state != "All States":
                st.subheader(f"Colleges in {selected_state}")
                state_colleges = filtered_df[
                    (filtered_df["StateInfo"] == selected_state) & 
                    (filtered_df["Level"].isin(["Tech Lead", "AI Intern"]))
                ][["Label", "Level", "TotalRegistrations"]]
                st.dataframe(state_colleges, use_container_width=True)
        else:
            st.info("No data available for the selected filters")


def display_sunburst_diagram(ai_data, techlead_data, cohort_typ):

    AI_DEV_STATE_CSV_PATH = "assets/aieLeads.csv"
    TECH_LEAD_STATE_CSV_PATH = "assets/TechLeads.csv"
    
    try:
        ai_state_list, tech_state_list = load_state_mapping_data(AI_DEV_STATE_CSV_PATH, TECH_LEAD_STATE_CSV_PATH)
        if ai_state_list is None or tech_state_list is None:
            return
        
        filtered_ai_dev, filtered_tech_lead = filter_data_by_cohort(ai_data, techlead_data, cohort_typ)
    
        college_to_state_mapping = create_college_to_state_mapping(ai_state_list, tech_state_list)

        ai_dev_college_counts, tech_lead_college_counts, all_college_counts = get_college_counts(filtered_ai_dev, filtered_tech_lead)
        
        tech_leads_data, ai_interns_data = prepare_sunburst_data(
            all_college_counts, tech_lead_college_counts, ai_dev_college_counts, college_to_state_mapping
        )
        

        sunburst_df, tech_df, ai_df = create_sunburst_dataframe(tech_leads_data, ai_interns_data)
        
        if sunburst_df.empty:
            st.error("No data available for the selected cohort type.")
            return
        
        available_states = sorted(sunburst_df[
            (sunburst_df["StateInfo"] != "N/A") & 
            (sunburst_df["StateInfo"].notna())
        ]["StateInfo"].unique())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Filter by State")
            state_options = ["All States"] + available_states
            selected_state = st.selectbox(
                "Select a state to view its program structure:",
                options=state_options,
                index=0,
                help="Choose a specific state to see only the colleges and participants from that state"
            )
        
        with col2:
            st.subheader("Filter by Registration Count")
            registration_threshold = st.selectbox(
                "Select minimum registrations:",
                options=[1,5,10,50, 100],
                index=1,
                help="Choose minimum registration count to filter colleges"
            )
        top_colleges = get_top_colleges(tech_df, ai_df, selected_state, registration_threshold)
        
        with col3:
            st.subheader("Top Colleges by Registrations")
            
            if not top_colleges.empty:
                college_options = ["All Colleges"] + [
                    f"{row['CollegeName']} ({row['StateInfo']}) - {int(row['TotalRegistrations'])} registrations"
                    for _, row in top_colleges.iterrows()
                ]
                
                selected_college_option = st.selectbox(
                    f"Select from colleges with {registration_threshold}+ registrations ({len(top_colleges)} found):",
                    options=college_options,
                    index=0,
                    help=f"Shows only colleges with {registration_threshold} or more total registrations"
                )
                
                selected_college = None
                if selected_college_option != "All Colleges":
                    selected_college = selected_college_option.split(" (")[0]
            else:
                selected_college = None
                st.info(f"No colleges found with {registration_threshold}+ registrations for {selected_state}")
        filtered_df = filter_sunburst_by_state(sunburst_df, selected_state)
        display_statistics(sunburst_df, selected_state, selected_college)
        fig = create_sunburst_chart(filtered_df, selected_state, selected_college, cohort_typ)
        st.plotly_chart(fig, use_container_width=True)
        display_top_colleges_table(top_colleges, registration_threshold, selected_state, cohort_typ)
        display_data_summary(filtered_df, selected_state)   
          
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your data format and ensure it has the required columns and state mapping datasets")