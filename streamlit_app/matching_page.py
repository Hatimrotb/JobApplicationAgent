"""
Job Matcher page for the Streamlit application.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_app.utils import save_data, generate_sample_matches

# Constants
OUTPUT_DIR = "job_application_data"


def show():
    """Display the Job Matcher page."""
    st.title("Job Matcher")
    st.write("Match your resume with job listings to find the best opportunities.")
    
    # Check if resume and job listings are available
    if not st.session_state.resume_data:
        st.warning("No resume data available. Please upload your resume first.")
        if st.button("Go to Resume Parser"):
            st.switch_page("Resume Parser")
        return
    
    if not st.session_state.job_listings:
        st.warning("No job listings available. Please search for jobs first.")
        if st.button("Go to Job Scraper"):
            st.switch_page("Job Scraper")
        return
    
    # Matching options
    st.subheader("Matching Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_score = st.slider("Minimum Match Score", 0, 100, 50)
    
    with col2:
        matching_method = st.selectbox(
            "Matching Method",
            ["TF-IDF", "BERT Embeddings (Simulated)"]
        )
    
    # Weights for different criteria
    st.write("Matching Criteria Weights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        skills_weight = st.slider("Skills", 0.0, 1.0, 0.4, 0.1)
    
    with col2:
        experience_weight = st.slider("Experience", 0.0, 1.0, 0.3, 0.1)
    
    with col3:
        education_weight = st.slider("Education", 0.0, 1.0, 0.2, 0.1)
    
    with col4:
        overall_weight = st.slider("Overall", 0.0, 1.0, 0.1, 0.1)
    
    # Normalize weights to sum to 1
    total_weight = skills_weight + experience_weight + education_weight + overall_weight
    if total_weight > 0:
        skills_weight /= total_weight
        experience_weight /= total_weight
        education_weight /= total_weight
        overall_weight /= total_weight
    
    # Match button
    if st.button("Match Jobs"):
        with st.spinner("Matching jobs to your resume..."):
            # In a real implementation, this would call the job matcher
            # For now, we'll use sample matches
            
            # Generate sample matches
            matched_jobs = generate_sample_matches(st.session_state.job_listings, min_score)
            
            # Save to session state
            st.session_state.matched_jobs = matched_jobs
            
            # Save to file
            save_data(matched_jobs, "matched_jobs.json")
            
            st.success(f"Matched {len(matched_jobs)} jobs with score >= {min_score}%")
    
    # Display matched jobs
    if st.session_state.matched_jobs:
        st.subheader("Matched Jobs")
        
        # Create a DataFrame for display
        matched_df = pd.DataFrame(st.session_state.matched_jobs)
        
        # Select columns to display
        display_cols = ["id", "title", "company", "location", "match_score"]
        
        if all(col in matched_df.columns for col in display_cols):
            # Format match score as percentage
            matched_df["match_score"] = matched_df["match_score"].apply(lambda x: f"{x:.1f}%")
            
            # Display the DataFrame
            st.dataframe(matched_df[display_cols], use_container_width=True)
        
        # Visualize match scores
        st.subheader("Match Score Visualization")
        
        # Create a DataFrame for visualization
        viz_df = pd.DataFrame(st.session_state.matched_jobs)
        
        # Select top 10 matches for visualization
        top_matches = viz_df.sort_values("match_score", ascending=False).head(10)
        
        # Create a bar chart
        fig = px.bar(
            top_matches,
            x="match_score",
            y="title",
            color="match_score",
            color_continuous_scale="Viridis",
            labels={"match_score": "Match Score (%)", "title": "Job Title"},
            title="Top 10 Job Matches",
            orientation="h"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Job match details
        st.subheader("Job Match Details")
        
        # Select a job to view
        job_ids = [job["id"] for job in st.session_state.matched_jobs]
        selected_job_id = st.selectbox("Select a job to view match details", job_ids)
        
        # Find the selected job
        selected_job = next((job for job in st.session_state.matched_jobs if job["id"] == selected_job_id), None)
        
        if selected_job:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**{selected_job.get('title')}**")
                st.write(f"*{selected_job.get('company')}*")
            
            with col2:
                st.write(f"Location: {selected_job.get('location')}")
                st.write(f"Match Score: {selected_job.get('match_score'):.1f}%")
            
            # Match details
            if "match_details" in selected_job:
                details = selected_job["match_details"]
                
                # Create a DataFrame for the match details
                details_df = pd.DataFrame({
                    "Category": ["Skills", "Experience", "Education", "Overall"],
                    "Score": [
                        details.get("skill_score", 0),
                        details.get("experience_score", 0),
                        details.get("education_score", 0),
                        details.get("overall_score", 0)
                    ]
                })
                
                # Create a radar chart
                fig = px.line_polar(
                    details_df,
                    r="Score",
                    theta="Category",
                    line_close=True,
                    range_r=[0, 100],
                    title="Match Score Breakdown"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Job description
            st.write("**Job Description**")
            st.write(selected_job.get('description', 'No description available'))
            
            # Actions
            st.write("**Actions**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Generate Cover Letter", key=f"gen_cover_{selected_job_id}"):
                    # Store the job ID for the cover letter page
                    st.session_state.current_job_id = selected_job_id
                    st.switch_page("Cover Letter Generator")
            
            with col2:
                if st.button("Apply to Job", key=f"apply_{selected_job_id}"):
                    # Store the job ID for the applications page
                    st.session_state.current_job_id = selected_job_id
                    st.switch_page("Applications")
        
        # Export options
        st.subheader("Export Options")
        
        if st.button("Export to JSON"):
            # Create a download link for the JSON file
            json_str = json.dumps(st.session_state.matched_jobs, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="matched_jobs.json",
                mime="application/json"
            )
    
    else:
        st.info("No matched jobs available. Click the 'Match Jobs' button to match your resume with job listings.")
