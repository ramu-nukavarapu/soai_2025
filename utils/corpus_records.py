import pandas as pd
import streamlit as st

from utils.load_session_data import get_aidev_data, get_corpus_records_users, get_corpus_users, get_techlead_data

def clean_phone_number(phone):
    """Clean and normalize phone numbers for matching"""
    if pd.isna(phone) or phone == 'nan' or str(phone).strip() == '':
        return None
    
    phone_str = str(phone).strip()
    # Remove country code, spaces, dashes, parentheses
    phone_clean = phone_str.replace("+91", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    phone_clean = phone_clean.lstrip("0")
    
    if phone_clean.isdigit() and len(phone_clean) == 10:
        return phone_clean
    return None

def generate_contribution_data(intern_type, cohort_type):
    try:
        users_data = get_corpus_users()
        if not users_data:
            st.error("Failed to fetch users data")
            return None
        
        df_users = pd.DataFrame(users_data)
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return None
    
    aidev_ranges = {
        "cohort1": (0, 25000),
        "cohort2": (25001, 44126),
    }

    techlead_ranges = {
        "cohort1": (0, 1730),
        "cohort2": (1731, 2348),
    }

    a_start, a_end = aidev_ranges[cohort_type]
    t_start, t_end = techlead_ranges[cohort_type]
    
    try:
        if intern_type == "aidev":
            df_clg = pd.DataFrame(get_aidev_data())
            df_clg = df_clg[(df_clg['Id'] >= a_start) & (df_clg['Id'] <= a_end)]
        elif intern_type == "techlead":
            df_clg = pd.DataFrame(get_techlead_data())
            df_clg = df_clg[(df_clg['Id'] >= t_start) & (df_clg['Id'] <= t_end)]
        else:
            pass

    except Exception as e:
        st.error(f"Error reading college details: {e}")
        return None
    
    # Clean phone numbers in both dataframes
    df_users['clean_phone'] = df_users['phone'].apply(clean_phone_number)
    df_clg['clean_phone'] = df_clg['Contact Number'].apply(clean_phone_number)
    
    # Create user lookup dictionary
    user_lookup = {}
    for _, user in df_users.iterrows():
        clean_phone = user['clean_phone']
        if clean_phone:
            user_lookup[clean_phone] = {
                'user_id': user.get('id', user.get('user_id', 'N/A')),
                'registered': 'Y'
            }

    # Map students with users
    mapped_students = []
    for _, student in df_clg.iterrows():
        clean_phone = student['clean_phone']
        original_phone = student['Contact Number']
        
        if clean_phone and clean_phone in user_lookup:
            # Student is registered
            user_info = user_lookup[clean_phone]
            mapped_students.append({
                'Name': student['Full Name'],
                'Phone no': original_phone,
                'Registration status': 'Y',
                'user id': user_info['user_id'],
                'College': student['Affiliation (College/Company/Organization Name)'],
                'Email': student.get('Email Address', ''),
                'CreatedAt': student.get('CreatedAt', '')
            })
        else:
            # Student is not registered
            mapped_students.append({
                'Name': student['Full Name'],
                'Phone no': original_phone,
                'Registration status': 'N',
                'user id': 'N/A',
                'College': student['Affiliation (College/Company/Organization Name)'],
                'Email': student.get('Email Address', ''),
                'CreatedAt': student.get('CreatedAt', '')
            })
    
    df_mapped = pd.DataFrame(mapped_students)
    
    try:
        df_records = pd.DataFrame(get_corpus_records_users())
    except Exception as e:
        st.error(f"Error reading records: {e}")
        return None
    
    # Calculate contributions by user_id
    df_records['media_type'] = df_records['media_type'].str.lower()
    
    # Group by user_id and count contributions by media type
    contributions = df_records.groupby('user_id').agg({
        'title': 'count',  # total contributions
        'media_type': list
    }).rename(columns={'title': 'total_contributions'})

    # totals_by_media = df_records.groupby('media_type')['duration_seconds'].sum()
    # print(totals_by_media)
    
    # Count each media type
    def count_media_types(media_list):
        counts = {'image': 0, 'video': 0, 'audio': 0, 'text': 0}
        for media in media_list:
            if media in counts:
                counts[media] += 1
        return counts
    
    # Apply media type counting
    contribution_details = []
    duration_by_user_media = df_records.groupby(['user_id', 'media_type'])['duration_seconds'].sum().unstack(fill_value=0)

    for user_id, row in contributions.iterrows():
        media_counts = count_media_types(row['media_type'])
        
        # Get duration values, default to 0 if not present
        user_durations = duration_by_user_media.loc[user_id] if user_id in duration_by_user_media.index else {}
        audio_duration = user_durations.get('audio', 0.0)/3600
        video_duration = user_durations.get('video', 0.0)/3600
        total_hours = audio_duration + video_duration

        contribution_details.append({
            'user_id': user_id,
            'total contributions': row['total_contributions'],
            'total hours': total_hours,
            'image': media_counts['image'],
            'video': media_counts['video'],
            'video_duration': video_duration,
            'audio': media_counts['audio'],
            'audio_duration': audio_duration,
            'text': media_counts['text']
        })
    
    df_contributions = pd.DataFrame(contribution_details)
    
    # Merge mapped students with contributions
    df_final = df_mapped.merge(
        df_contributions,
        left_on='user id',
        right_on='user_id',
        how='left'
    )
    
    # Fill missing contribution data with zeros
    contribution_columns = ['total contributions', 'image', 'video', 'audio', 'text']
    for col in contribution_columns:
        df_final[col] = df_final[col].fillna(0).astype(int)
    
    # Select and reorder final columns as specified
    final_columns = ['Name', 'Phone no', 'Registration status', 'user id', 
                 'total contributions', 'total hours', 'image', 'audio', 'audio_duration',
                 'video', 'video_duration', 'text', 
                 'College', 'Email', 'CreatedAt']
    
    df_final = df_final[final_columns]
    return df_final