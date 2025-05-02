"""
Job Scraper page for the Streamlit application.
"""

import os
import json
import streamlit as st
import pandas as pd
from streamlit_app.utils import save_data, generate_sample_jobs

# Constants
OUTPUT_DIR = "job_application_data"


def show():
    """Display the Job Scraper page."""
    st.title("Job Scraper")
    st.write("Search for job listings based on keywords and location.")
    
    # Job search form
    with st.form("job_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            keywords = st.text_input("Keywords", "Python Developer")
        
        with col2:
            location = st.text_input("Location", "New York")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            remote = st.checkbox("Remote Jobs Only")
        
        with col2:
            job_type = st.selectbox(
                "Job Type",
                ["Full-time", "Part-time", "Contract", "Internship", "Any"]
            )
        
        with col3:
            limit = st.slider("Maximum Results", 5, 50, 10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.selectbox(
                "Source",
                ["Indeed", "LinkedIn", "Both"]
            )
        
        with col2:
            use_sample = st.checkbox("Use Sample Data", value=True, 
                                    help="Use sample data instead of making actual API requests")
        
        submitted = st.form_submit_button("Search Jobs")
        
        if submitted:
            with st.spinner("Searching for jobs..."):
                if use_sample:
                    # Generate sample job listings
                    job_listings = generate_sample_jobs(keywords, location, limit)
                    
                    # Save to session state
                    st.session_state.job_listings = job_listings
                    
                    # Save to file
                    save_data(job_listings, "job_listings.json")
                    
                    st.success(f"Found {len(job_listings)} jobs (sample data)")
                else:
                    # In a real implementation, this would call the job scraper
                    st.info("This would normally use the actual job scraper, but we're using sample data for demonstration")
                    
                    # Generate sample job listings
                    job_listings = generate_sample_jobs(keywords, location, limit)
                    
                    # Save to session state
                    st.session_state.job_listings = job_listings
                    
                    # Save to file
                    save_data(job_listings, "job_listings.json")
                    
                    st.success(f"Found {len(job_listings)} jobs")
    
    # Display job listings
    if st.session_state.job_listings:
        st.subheader("Job Listings")
        
        # Create a DataFrame for display
        jobs_df = pd.DataFrame(st.session_state.job_listings)
        
        # Select columns to display
        display_cols = ["id", "title", "company", "location", "salary", "date_posted", "source"]
        
        if all(col in jobs_df.columns for col in display_cols):
            jobs_df = jobs_df[display_cols]
            
            # Display the DataFrame
            st.dataframe(jobs_df, use_container_width=True)
        
        # Job details
        st.subheader("Job Details")
        
        # Select a job to view
        job_ids = [job["id"] for job in st.session_state.job_listings]
        selected_job_id = st.selectbox("Select a job to view details", job_ids)
        
        # Find the selected job
        selected_job = next((job for job in st.session_state.job_listings if job["id"] == selected_job_id), None)
        
        if selected_job:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**{selected_job.get('title')}**")
                st.write(f"*{selected_job.get('company')}*")
            
            with col2:
                st.write(f"Location: {selected_job.get('location')}")
                st.write(f"Posted: {selected_job.get('date_posted')}")
            
            if selected_job.get('salary') and selected_job.get('salary') != "Not specified":
                st.write(f"Salary: {selected_job.get('salary')}")
            
            st.write("**Job Description**")
            st.write(selected_job.get('description', 'No description available'))
            
            if selected_job.get('url'):
                st.write(f"[Apply on {selected_job.get('source')}]({selected_job.get('url')})")
        
        # Export options
        st.subheader("Export Options")
        
        if st.button("Export to JSON"):
            # Create a download link for the JSON file
            json_str = json.dumps(st.session_state.job_listings, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="job_listings.json",
                mime="application/json"
            )
    
    else:
        st.info("No job listings available. Use the form above to search for jobs.")
