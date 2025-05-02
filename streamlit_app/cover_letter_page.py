"""
Cover Letter Generator page for the Streamlit application.
"""

import os
import streamlit as st
from streamlit_app.utils import get_job_by_id, save_data, generate_sample_cover_letter

# Constants
OUTPUT_DIR = "job_application_data"


def show():
    """Display the Cover Letter Generator page."""
    st.title("Cover Letter Generator")
    st.write("Generate personalized cover letters for your job applications.")
    
    # Check if resume is available
    if not st.session_state.resume_data:
        st.warning("No resume data available. Please upload your resume first.")
        if st.button("Go to Resume Parser"):
            st.switch_page("Resume Parser")
        return
    
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
        "Select a job to generate a cover letter for",
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
    
    # Cover letter options
    st.subheader("Cover Letter Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Tone",
            ["Formal", "Conversational", "Enthusiastic"],
            index=0
        )
    
    with col2:
        format_option = st.selectbox(
            "Format",
            ["Standard", "Modern", "Minimal"],
            index=0
        )
    
    # Additional instructions
    custom_instructions = st.text_area(
        "Additional Instructions",
        placeholder="Add any specific instructions for the cover letter generator...",
        height=100
    )
    
    # Generate button
    if st.button("Generate Cover Letter"):
        with st.spinner("Generating cover letter..."):
            # In a real implementation, this would call the cover letter generator
            # For now, we'll use a sample cover letter
            
            # Generate sample cover letter
            cover_letter = generate_sample_cover_letter(
                st.session_state.resume_data,
                job_data,
                tone.lower()
            )
            
            # Save to session state
            st.session_state.current_cover_letter = cover_letter
            
            # Determine file path
            job_title_slug = job_data['title'].lower().replace(' ', '_')
            company_slug = job_data['company'].lower().replace(' ', '_')
            file_name = f"cover_letter_{job_title_slug}_{company_slug}.txt"
            file_path = os.path.join(OUTPUT_DIR, "cover_letters", file_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cover_letter)
            
            st.success(f"Cover letter generated and saved to {file_path}")
    
    # Display generated cover letter
    if st.session_state.current_cover_letter:
        st.subheader("Generated Cover Letter")
        
        # Display in a text area for easy copying
        st.text_area(
            "Cover Letter",
            st.session_state.current_cover_letter,
            height=400
        )
        
        # Download button
        job_title_slug = job_data['title'].lower().replace(' ', '_')
        company_slug = job_data['company'].lower().replace(' ', '_')
        file_name = f"cover_letter_{job_title_slug}_{company_slug}.txt"
        
        st.download_button(
            label="Download Cover Letter",
            data=st.session_state.current_cover_letter,
            file_name=file_name,
            mime="text/plain"
        )
        
        # Apply button
        if st.button("Apply with this Cover Letter"):
            # Store the job ID and go to the applications page
            st.session_state.current_job_id = selected_job_id
            st.switch_page("Applications")
    
    # Tips for cover letters
    with st.expander("Cover Letter Tips"):
        st.markdown("""
        ### Tips for a Great Cover Letter
        
        1. **Address the hiring manager by name** if possible.
        2. **Customize each cover letter** for the specific job.
        3. **Keep it concise** - no more than one page.
        4. **Highlight relevant achievements** rather than just listing responsibilities.
        5. **Show enthusiasm** for the role and company.
        6. **Proofread carefully** for grammar and spelling errors.
        7. **Use a professional tone** even when being conversational.
        8. **End with a call to action** expressing interest in an interview.
        """)
    
    # Reset current job ID after use
    if st.session_state.current_job_id:
        st.session_state.current_job_id = None
