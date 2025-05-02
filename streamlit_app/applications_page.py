"""
Applications page for the Streamlit application.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_app.utils import get_job_by_id, save_applications, get_application_statistics

# Constants
OUTPUT_DIR = "job_application_data"


def show():
    """Display the Applications page."""
    st.title("Applications")
    st.write("Track your job applications and their status.")
    
    # Check if resume is available
    if not st.session_state.resume_data:
        st.warning("No resume data available. Please upload your resume first.")
        if st.button("Go to Resume Parser"):
            st.switch_page("Resume Parser")
        return
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Apply to Jobs", "Application Tracker", "Statistics"])
    
    # Apply to Jobs tab
    with tab1:
        st.subheader("Apply to Jobs")
        
        # Job selection
        job_options = []
        
        # Add matched jobs first if available
        if st.session_state.matched_jobs:
            for job in st.session_state.matched_jobs:
                job_id = job.get("id", "")
                title = job.get("title", "")
                company = job.get("company", "")
                match_score = job.get("match_score", 0)
                job_options.append((job_id, f"{title} at {company} (Match: {match_score:.1f}%)"))
        
        # Add other job listings if not already included
        if st.session_state.job_listings:
            for job in st.session_state.job_listings:
                job_id = job.get("id", "")
                # Check if this job is already in the options (from matched jobs)
                if not any(job_id == option[0] for option in job_options):
                    title = job.get("title", "")
                    company = job.get("company", "")
                    job_options.append((job_id, f"{title} at {company}"))
        
        # If no jobs are available
        if not job_options:
            st.warning("No job listings available. Please search for jobs first.")
            if st.button("Go to Job Scraper"):
                st.switch_page("Job Scraper")
            return
        
        # Check if a job ID was passed from another page
        selected_job_id = st.session_state.current_job_id
        
        # If a job ID was passed, find its index in the options
        selected_index = 0
        if selected_job_id:
            for i, (job_id, _) in enumerate(job_options):
                if job_id == selected_job_id:
                    selected_index = i
                    break
        
        # Create a list of job descriptions for the selectbox
        job_descriptions = [desc for _, desc in job_options]
        
        # Job selection
        selected_job_desc = st.selectbox(
            "Select a job to apply to",
            job_descriptions,
            index=selected_index
        )
        
        # Get the job ID from the selected description
        selected_job_id = job_options[job_descriptions.index(selected_job_desc)][0]
        
        # Get the job data
        job_data = get_job_by_id(selected_job_id)
        
        if not job_data:
            st.error("Selected job not found.")
            return
        
        # Display job details
        st.write(f"**{job_data.get('title')}**")
        st.write(f"*{job_data.get('company')}*")
        st.write(f"Location: {job_data.get('location')}")
        
        if 'match_score' in job_data:
            st.write(f"Match Score: {job_data.get('match_score'):.1f}%")
        
        # Cover letter selection
        st.write("**Cover Letter**")
        
        cover_letter_options = ["None", "Generate New Cover Letter", "Use Existing Cover Letter"]
        cover_letter_option = st.radio("Cover Letter Option", cover_letter_options)
        
        cover_letter_path = None
        
        if cover_letter_option == "Generate New Cover Letter":
            st.session_state.current_job_id = selected_job_id
            if st.button("Go to Cover Letter Generator"):
                st.switch_page("Cover Letter Generator")
                return
        
        elif cover_letter_option == "Use Existing Cover Letter":
            # Check for existing cover letters
            cover_letters_dir = os.path.join(OUTPUT_DIR, "cover_letters")
            os.makedirs(cover_letters_dir, exist_ok=True)
            
            cover_letter_files = []
            if os.path.exists(cover_letters_dir):
                for file in os.listdir(cover_letters_dir):
                    if file.endswith(".txt"):
                        cover_letter_files.append(file)
            
            if cover_letter_files:
                selected_cover_letter = st.selectbox(
                    "Select a cover letter",
                    cover_letter_files
                )
                
                cover_letter_path = os.path.join(cover_letters_dir, selected_cover_letter)
                
                # Display cover letter preview
                try:
                    with open(cover_letter_path, 'r', encoding='utf-8') as f:
                        cover_letter_content = f.read()
                    
                    with st.expander("Cover Letter Preview"):
                        st.text(cover_letter_content)
                except:
                    st.error("Error reading cover letter file.")
            else:
                st.warning("No existing cover letters found.")
        
        # Application notes
        notes = st.text_area(
            "Application Notes",
            placeholder="Add any notes about this application..."
        )
        
        # Apply button
        if st.button("Apply to Job"):
            # Check if already applied
            already_applied = False
            for app in st.session_state.applications:
                if (app.get("job_title") == job_data.get("title") and 
                    app.get("company") == job_data.get("company")):
                    already_applied = True
                    break
            
            if already_applied:
                st.warning("You have already applied to this job.")
            else:
                # Create application record
                application = {
                    "job_title": job_data.get("title", ""),
                    "company": job_data.get("company", ""),
                    "location": job_data.get("location", ""),
                    "job_url": job_data.get("url", ""),
                    "date_applied": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Applied",
                    "resume_path": "resume.pdf",  # Placeholder
                    "cover_letter_path": cover_letter_path or "",
                    "application_id": f"APP-{job_data.get('id', '')[4:]}",
                    "notes": notes
                }
                
                # Add to applications list
                if "applications" not in st.session_state:
                    st.session_state.applications = []
                
                st.session_state.applications.append(application)
                
                # Save applications
                save_applications()
                
                st.success(f"Application submitted for {job_data.get('title')} at {job_data.get('company')}")
                
                # Clear the current job ID
                st.session_state.current_job_id = None
        
        # Skip button
        if st.button("Skip this Job"):
            # Check if already skipped
            already_skipped = False
            for app in st.session_state.applications:
                if (app.get("job_title") == job_data.get("title") and 
                    app.get("company") == job_data.get("company") and
                    app.get("status") == "Skipped"):
                    already_skipped = True
                    break
            
            if already_skipped:
                st.warning("You have already skipped this job.")
            else:
                # Create application record
                application = {
                    "job_title": job_data.get("title", ""),
                    "company": job_data.get("company", ""),
                    "location": job_data.get("location", ""),
                    "job_url": job_data.get("url", ""),
                    "date_applied": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Skipped",
                    "resume_path": "",
                    "cover_letter_path": "",
                    "application_id": f"APP-{job_data.get('id', '')[4:]}",
                    "notes": notes or "Skipped"
                }
                
                # Add to applications list
                if "applications" not in st.session_state:
                    st.session_state.applications = []
                
                st.session_state.applications.append(application)
                
                # Save applications
                save_applications()
                
                st.info(f"Skipped application for {job_data.get('title')} at {job_data.get('company')}")
                
                # Clear the current job ID
                st.session_state.current_job_id = None
    
    # Application Tracker tab
    with tab2:
        st.subheader("Application Tracker")
        
        if not st.session_state.applications:
            st.info("No applications yet. Apply to jobs to track them here.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    ["Applied", "Skipped", "Rejected", "Interview", "Offer", "Accepted"],
                    default=["Applied", "Interview", "Offer"]
                )
            
            with col2:
                company_filter = st.text_input("Filter by Company")
            
            # Apply filters
            filtered_applications = st.session_state.applications
            
            if status_filter:
                filtered_applications = [app for app in filtered_applications 
                                        if app.get("status", "") in status_filter]
            
            if company_filter:
                filtered_applications = [app for app in filtered_applications 
                                        if company_filter.lower() in app.get("company", "").lower()]
            
            # Create DataFrame for display
            if filtered_applications:
                apps_df = pd.DataFrame(filtered_applications)
                
                # Select columns to display
                display_cols = ["application_id", "job_title", "company", "date_applied", "status"]
                
                if all(col in apps_df.columns for col in display_cols):
                    apps_df = apps_df[display_cols]
                    
                    # Display the DataFrame
                    st.dataframe(apps_df, use_container_width=True)
                
                # Application details
                st.subheader("Application Details")
                
                # Select an application to view
                app_ids = [app["application_id"] for app in filtered_applications]
                selected_app_id = st.selectbox("Select an application to view details", app_ids)
                
                # Find the selected application
                selected_app = next((app for app in filtered_applications 
                                    if app["application_id"] == selected_app_id), None)
                
                if selected_app:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**{selected_app.get('job_title')}**")
                        st.write(f"*{selected_app.get('company')}*")
                    
                    with col2:
                        st.write(f"Status: {selected_app.get('status')}")
                        st.write(f"Applied: {selected_app.get('date_applied')}")
                    
                    st.write(f"Location: {selected_app.get('location')}")
                    
                    if selected_app.get('job_url'):
                        st.write(f"[Job Listing]({selected_app.get('job_url')})")
                    
                    if selected_app.get('notes'):
                        st.write("**Notes:**")
                        st.write(selected_app.get('notes'))
                    
                    # Update status
                    st.write("**Update Status**")
                    
                    new_status = st.selectbox(
                        "New Status",
                        ["Applied", "Skipped", "Rejected", "Interview", "Offer", "Accepted"],
                        index=["Applied", "Skipped", "Rejected", "Interview", "Offer", "Accepted"].index(
                            selected_app.get("status", "Applied")
                        )
                    )
                    
                    new_notes = st.text_area(
                        "Update Notes",
                        value=selected_app.get("notes", ""),
                        key="update_notes"
                    )
                    
                    if st.button("Update Application"):
                        # Find the application in the session state
                        for i, app in enumerate(st.session_state.applications):
                            if app["application_id"] == selected_app_id:
                                # Update status and notes
                                st.session_state.applications[i]["status"] = new_status
                                st.session_state.applications[i]["notes"] = new_notes
                                
                                # Save applications
                                save_applications()
                                
                                st.success(f"Application updated: {selected_app.get('job_title')} at {selected_app.get('company')}")
                                
                                # Refresh the page
                                st.experimental_rerun()
                                break
            else:
                st.info("No applications match the selected filters.")
    
    # Statistics tab
    with tab3:
        st.subheader("Application Statistics")
        
        if not st.session_state.applications:
            st.info("No applications yet. Apply to jobs to see statistics here.")
        else:
            # Get application statistics
            stats = get_application_statistics()
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Applications", stats["total_applications"])
            
            with col2:
                st.metric("Applications per Day", stats["applications_per_day"])
            
            with col3:
                response_rate = 0
                if stats["total_applications"] > 0:
                    interviews = stats["status_counts"].get("Interview", 0)
                    offers = stats["status_counts"].get("Offer", 0)
                    accepted = stats["status_counts"].get("Accepted", 0)
                    responses = interviews + offers + accepted
                    response_rate = (responses / stats["total_applications"]) * 100
                
                st.metric("Response Rate", f"{response_rate:.1f}%")
            
            # Status breakdown
            st.subheader("Status Breakdown")
            
            if stats["status_counts"]:
                # Create DataFrame for the pie chart
                status_df = pd.DataFrame({
                    "Status": list(stats["status_counts"].keys()),
                    "Count": list(stats["status_counts"].values())
                })
                
                # Create a pie chart
                fig = px.pie(
                    status_df,
                    values="Count",
                    names="Status",
                    title="Applications by Status",
                    color="Status",
                    color_discrete_map={
                        "Applied": "#1f77b4",
                        "Skipped": "#aec7e8",
                        "Rejected": "#ff7f0e",
                        "Interview": "#2ca02c",
                        "Offer": "#d62728",
                        "Accepted": "#9467bd"
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Top companies
            st.subheader("Top Companies")
            
            if stats["top_companies"]:
                # Create DataFrame for the bar chart
                companies_df = pd.DataFrame({
                    "Company": [company for company, _ in stats["top_companies"]],
                    "Applications": [count for _, count in stats["top_companies"]]
                })
                
                # Create a bar chart
                fig = px.bar(
                    companies_df,
                    x="Company",
                    y="Applications",
                    title="Top Companies Applied To",
                    color="Applications",
                    color_continuous_scale="Viridis"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Application timeline
            st.subheader("Application Timeline")
            
            # Create DataFrame for the timeline
            timeline_data = []
            for app in st.session_state.applications:
                try:
                    date = datetime.strptime(app.get("date_applied", ""), "%Y-%m-%d %H:%M:%S").date()
                    timeline_data.append({
                        "Date": date,
                        "Status": app.get("status", "Applied")
                    })
                except:
                    pass
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                
                # Group by date and count
                timeline_grouped = timeline_df.groupby(["Date", "Status"]).size().reset_index(name="Count")
                
                # Create a line chart
                fig = px.line(
                    timeline_grouped,
                    x="Date",
                    y="Count",
                    color="Status",
                    title="Applications Over Time",
                    markers=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Export options
            st.subheader("Export Options")
            
            if st.button("Export to CSV"):
                # Create a CSV string
                apps_df = pd.DataFrame(st.session_state.applications)
                csv = apps_df.to_csv(index=False)
                
                # Create a download button
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="applications.csv",
                    mime="text/csv"
                )
