"""
Resume Parser page for the Streamlit application.
"""

import os
import json
import streamlit as st
import pandas as pd
from streamlit_app.utils import save_data, generate_sample_resume

# Constants
OUTPUT_DIR = "job_application_data"


def show():
    """Display the Resume Parser page."""
    st.title("Resume Parser")
    st.write("Upload your resume to extract your skills and experience.")
    
    # File upload
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Use Sample Resume"):
            # Generate sample resume data
            sample_resume = generate_sample_resume()
            
            # Save to session state
            st.session_state.resume_data = sample_resume
            
            # Save to file
            save_data(sample_resume, "resume_data.json")
            
            st.success("Sample resume loaded successfully!")
    
    with col2:
        if uploaded_file is not None:
            if st.button("Parse Resume"):
                # In a real implementation, this would call the resume parser
                # For now, we'll use the sample resume
                st.info("Parsing resume... (using sample data for demonstration)")
                
                # Generate sample resume data
                sample_resume = generate_sample_resume()
                
                # Save to session state
                st.session_state.resume_data = sample_resume
                
                # Save to file
                save_data(sample_resume, "resume_data.json")
                
                st.success("Resume parsed successfully!")
    
    # Display parsed resume data
    if st.session_state.resume_data:
        st.subheader("Parsed Resume Data")
        
        # Contact info
        contact_info = st.session_state.resume_data.get("contact_info", {})
        st.write("**Contact Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {contact_info.get('name', '')}")
            st.write(f"**Email:** {contact_info.get('email', '')}")
            st.write(f"**Phone:** {contact_info.get('phone', '')}")
        
        with col2:
            st.write(f"**Location:** {contact_info.get('location', '')}")
            st.write(f"**LinkedIn:** {contact_info.get('linkedin', '')}")
        
        # Summary
        st.write("**Summary**")
        st.write(st.session_state.resume_data.get("summary", ""))
        
        # Skills
        st.write("**Skills**")
        skills = st.session_state.resume_data.get("skills", [])
        if skills:
            st.write(", ".join(skills))
        else:
            st.write("No skills found")
        
        # Experience
        st.write("**Experience**")
        experience = st.session_state.resume_data.get("experience", [])
        
        for exp in experience:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{exp.get('title', '')} at {exp.get('company', '')}**")
            
            with col2:
                st.write(f"{exp.get('start_date', '')} - {exp.get('end_date', '')}")
            
            st.write(f"*{exp.get('location', '')}*")
            
            for desc in exp.get("description", []):
                st.write(f"- {desc}")
        
        # Education
        st.write("**Education**")
        education = st.session_state.resume_data.get("education", [])
        
        for edu in education:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{edu.get('degree', '')}**")
            
            with col2:
                st.write(f"Graduated: {edu.get('graduation_date', '')}")
            
            st.write(f"*{edu.get('institution', '')}, {edu.get('location', '')}*")
            
            if edu.get("gpa"):
                st.write(f"GPA: {edu.get('gpa')}")
        
        # Certifications
        st.write("**Certifications**")
        certifications = st.session_state.resume_data.get("certifications", [])
        
        for cert in certifications:
            st.write(f"**{cert.get('name', '')}** - {cert.get('issuer', '')}, {cert.get('date', '')}")
        
        # Export options
        st.subheader("Export Options")
        
        if st.button("Export to JSON"):
            # Create a download link for the JSON file
            json_str = json.dumps(st.session_state.resume_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="resume_data.json",
                mime="application/json"
            )
    
    else:
        st.info("No resume data available. Upload a resume or use the sample resume.")
