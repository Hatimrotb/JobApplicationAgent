"""
JobApplicationAgent - Streamlit Web Application

This is the main entry point for the JobApplicationAgent web application.
"""

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_app import resume_page, jobs_page, matching_page, cover_letter_page, applications_page
from streamlit_app.utils import load_data, save_data, initialize_session_state

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="JobApplicationAgent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data directories
OUTPUT_DIR = "job_application_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "applications"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "cover_letters"), exist_ok=True)

# Initialize session state
initialize_session_state()

# Load data
load_data()

# Sidebar navigation
st.sidebar.title("JobApplicationAgent")
st.sidebar.image("https://img.icons8.com/color/96/000000/job-seeker.png", width=100)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Resume Parser", "Job Scraper", "Job Matcher", "Cover Letter Generator", "Applications"]
)

# Display the selected page
if page == "Dashboard":
    st.title("JobApplicationAgent Dashboard")
    st.subheader("Automate Your Job Application Process")
    
    # Dashboard metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Parsed Resume", 
            value="Yes" if st.session_state.resume_data else "No"
        )
    
    with col2:
        st.metric(
            label="Scraped Jobs", 
            value=len(st.session_state.job_listings) if st.session_state.job_listings else 0
        )
    
    with col3:
        st.metric(
            label="Applications", 
            value=len(st.session_state.applications) if st.session_state.applications else 0
        )
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if st.session_state.applications:
        # Show recent applications
        recent_apps = sorted(
            st.session_state.applications, 
            key=lambda x: x.get("date_applied", ""), 
            reverse=True
        )[:5]
        
        recent_df = pd.DataFrame(recent_apps)
        if not recent_df.empty:
            recent_df = recent_df[["application_id", "job_title", "company", "date_applied", "status"]]
            st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No recent activity. Start by parsing your resume and scraping jobs.")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Parse Resume", key="dashboard_parse"):
            st.switch_page("Resume Parser")
    
    with col2:
        if st.button("Scrape Jobs", key="dashboard_scrape"):
            st.switch_page("Job Scraper")
    
    with col3:
        if st.button("Match Jobs", key="dashboard_match"):
            st.switch_page("Job Matcher")
    
    # Getting started guide
    st.subheader("Getting Started")
    
    st.markdown("""
    Follow these steps to get started with JobApplicationAgent:
    
    1. **Parse Resume**: Upload your resume (PDF or DOCX) to extract your skills and experience.
    2. **Scrape Jobs**: Search for job listings based on keywords and location.
    3. **Match Jobs**: Match your resume with job listings to find the best opportunities.
    4. **Generate Cover Letters**: Create personalized cover letters for your top matches.
    5. **Apply to Jobs**: Track your job applications and their status.
    """)

elif page == "Resume Parser":
    resume_page.show()

elif page == "Job Scraper":
    jobs_page.show()

elif page == "Job Matcher":
    matching_page.show()

elif page == "Cover Letter Generator":
    cover_letter_page.show()

elif page == "Applications":
    applications_page.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "JobApplicationAgent v1.0.0\n\n"
    "@ 2025 Hatim"
)
