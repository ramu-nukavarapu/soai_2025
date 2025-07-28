import streamlit as st
import time

def get_aidev_data():
    """Get AIDEV registration data from session state"""
    return st.session_state.get('aidev', [])

def get_techlead_data():
    """Get TECHLEAD registration data from session state"""
    return st.session_state.get('techlead', [])

def get_residential_data():
    """Get TECHLEAD registration data from session state"""
    return st.session_state.get('residential', [])

def get_gitlab_users():
    """Get GitLab users data from session state"""
    return st.session_state.get('gitlab_users', [])

def get_corpus_users():
    """Get corpus users data from session state"""
    return st.session_state.get('corpus_users', [])

def get_corpus_records_users():
    """Get corpus user records data from session state"""
    return st.session_state.get('corpus_user_records', [])

def wait_for_data(keys, check_interval=0.5, max_wait=10):
    start_time = time.time()

    with st.spinner("Loading required data..."):
        while any(st.session_state.get(k) is None for k in keys):
            if time.time() - start_time > max_wait:
                st.error("Data loading timed out.")
                st.stop()
            time.sleep(check_interval)