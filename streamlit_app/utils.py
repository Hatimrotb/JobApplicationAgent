"""
Utility functions for the Streamlit application.
"""

import os
import json
import streamlit as st
from datetime import datetime

# Constants
OUTPUT_DIR = "job_application_data"


def initialize_session_state():
    """Initialize session state variables."""
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    
    if "job_listings" not in st.session_state:
        st.session_state.job_listings = []
    
    if "matched_jobs" not in st.session_state:
        st.session_state.matched_jobs = []
    
    if "applications" not in st.session_state:
        st.session_state.applications = []
    
    if "current_job_id" not in st.session_state:
        st.session_state.current_job_id = None
    
    if "current_cover_letter" not in st.session_state:
        st.session_state.current_cover_letter = None


def load_data():
    """Load data from files into session state."""
    # Load resume data
    resume_path = os.path.join(OUTPUT_DIR, "resume_data.json")
    if os.path.exists(resume_path):
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                st.session_state.resume_data = json.load(f)
        except Exception as e:
            st.error(f"Error loading resume data: {e}")
    
    # Load job listings
    jobs_path = os.path.join(OUTPUT_DIR, "job_listings.json")
    if os.path.exists(jobs_path):
        try:
            with open(jobs_path, 'r', encoding='utf-8') as f:
                st.session_state.job_listings = json.load(f)
        except Exception as e:
            st.error(f"Error loading job listings: {e}")
    
    # Load matched jobs
    matched_path = os.path.join(OUTPUT_DIR, "matched_jobs.json")
    if os.path.exists(matched_path):
        try:
            with open(matched_path, 'r', encoding='utf-8') as f:
                st.session_state.matched_jobs = json.load(f)
        except Exception as e:
            st.error(f"Error loading matched jobs: {e}")
    
    # Load applications
    applications_path = os.path.join(OUTPUT_DIR, "applications", "applications.json")
    if os.path.exists(applications_path):
        try:
            with open(applications_path, 'r', encoding='utf-8') as f:
                st.session_state.applications = json.load(f)
        except Exception as e:
            st.error(f"Error loading applications: {e}")


def save_data(data, file_name):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_name: Name of the file (without directory)
    """
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {e}")
        return False


def save_applications():
    """Save applications to a JSON file."""
    applications_path = os.path.join(OUTPUT_DIR, "applications", "applications.json")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(applications_path), exist_ok=True)
    
    try:
        with open(applications_path, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.applications, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving applications: {e}")
        return False


def get_job_by_id(job_id):
    """
    Get a job by its ID.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Job data or None if not found
    """
    # Check matched jobs first
    if st.session_state.matched_jobs:
        for job in st.session_state.matched_jobs:
            if job.get('id') == job_id:
                return job
    
    # Check all job listings
    if st.session_state.job_listings:
        for job in st.session_state.job_listings:
            if job.get('id') == job_id:
                return job
    
    return None


def get_application_statistics():
    """
    Get statistics about applications.
    
    Returns:
        Dictionary with application statistics
    """
    applications = st.session_state.applications
    total = len(applications)
    
    # Count by status
    status_counts = {}
    for app in applications:
        status = app.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count by company
    company_counts = {}
    for app in applications:
        company = app.get("company", "Unknown")
        company_counts[company] = company_counts.get(company, 0) + 1
    
    # Get top companies
    top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate application rate
    if total > 0:
        try:
            first_date = min(datetime.strptime(app.get("date_applied", "2025-01-01"), "%Y-%m-%d %H:%M:%S") 
                            for app in applications if app.get("date_applied"))
            last_date = max(datetime.strptime(app.get("date_applied", "2025-01-01"), "%Y-%m-%d %H:%M:%S") 
                           for app in applications if app.get("date_applied"))
            days_span = (last_date - first_date).days + 1
            applications_per_day = total / max(days_span, 1)
        except:
            applications_per_day = 0
    else:
        applications_per_day = 0
    
    return {
        "total_applications": total,
        "status_counts": status_counts,
        "top_companies": top_companies,
        "applications_per_day": round(applications_per_day, 2)
    }


def generate_sample_resume():
    """Generate a sample resume for demonstration purposes."""
    return {
        "contact_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "location": "New York, NY",
            "linkedin": "https://www.linkedin.com/in/johndoe"
        },
        "summary": "Experienced software engineer with a passion for building scalable applications.",
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "Django", "Flask",
            "SQL", "MongoDB", "AWS", "Docker", "Git", "CI/CD"
        ],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "location": "New York, NY",
                "start_date": "2020",
                "end_date": "Present",
                "description": [
                    "Led a team of 5 developers to build a cloud-based SaaS platform",
                    "Implemented CI/CD pipelines using GitHub Actions",
                    "Reduced API response time by 40% through optimization"
                ]
            },
            {
                "title": "Software Developer",
                "company": "Web Innovations",
                "location": "Boston, MA",
                "start_date": "2018",
                "end_date": "2020",
                "description": [
                    "Developed RESTful APIs using Django and Flask",
                    "Built responsive web applications with React",
                    "Implemented automated testing with pytest"
                ]
            }
        ],
        "education": [
            {
                "degree": "Master of Science in Computer Science",
                "institution": "University of Technology",
                "location": "New York, NY",
                "graduation_date": "2018",
                "gpa": "3.8"
            },
            {
                "degree": "Bachelor of Science in Computer Engineering",
                "institution": "State University",
                "location": "Chicago, IL",
                "graduation_date": "2016",
                "gpa": "3.7"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "date": "2021"
            },
            {
                "name": "Certified Scrum Master",
                "issuer": "Scrum Alliance",
                "date": "2020"
            }
        ]
    }


def generate_sample_jobs(keywords="python", location="New York", count=5):
    """Generate sample job listings for demonstration purposes."""
    job_titles = [
        "Senior Python Developer",
        "Full Stack Engineer",
        "Data Scientist",
        "DevOps Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Machine Learning Engineer",
        "Software Architect",
        "QA Engineer",
        "Product Manager"
    ]
    
    companies = [
        "Tech Innovations Inc.",
        "Data Solutions LLC",
        "Cloud Systems",
        "WebDev Co.",
        "AI Research Group",
        "Software Solutions",
        "Digital Transformers",
        "Agile Development",
        "Mobile Experts",
        "Enterprise Systems"
    ]
    
    locations = [
        f"{location}",
        "Remote",
        "San Francisco, CA",
        "Boston, MA",
        "Austin, TX",
        "Seattle, WA",
        "Chicago, IL",
        "Denver, CO",
        "Atlanta, GA",
        f"{location} (Hybrid)"
    ]
    
    descriptions = [
        f"We are looking for a {keywords} developer to join our team. The ideal candidate will have experience with Django, Flask, and RESTful APIs. Knowledge of AWS and Docker is a plus.",
        f"Join our team as a {keywords} engineer. You will be responsible for designing and implementing scalable solutions for our clients. Experience with React, Node.js, and MongoDB required.",
        f"Seeking a talented {keywords} specialist to help us analyze large datasets and build machine learning models. Experience with pandas, scikit-learn, and TensorFlow is required.",
        f"We need a {keywords} expert to manage our cloud infrastructure. Experience with AWS, Docker, Kubernetes, and CI/CD pipelines is essential.",
        f"Looking for a {keywords} developer with strong frontend skills. Experience with React, Redux, and modern JavaScript frameworks is required."
    ]
    
    salaries = [
        "$120,000 - $150,000 a year",
        "$100,000 - $130,000 a year",
        "$130,000 - $160,000 a year",
        "$125,000 - $155,000 a year",
        "Not specified"
    ]
    
    date_posted = [
        "Just posted",
        "1 day ago",
        "2 days ago",
        "3 days ago",
        "1 week ago"
    ]
    
    jobs = []
    for i in range(min(count, 10)):
        job = {
            "id": f"JOB-{i+1:04d}",
            "title": job_titles[i % len(job_titles)],
            "company": companies[i % len(companies)],
            "location": locations[i % len(locations)],
            "description": descriptions[i % len(descriptions)],
            "salary": salaries[i % len(salaries)],
            "date_posted": date_posted[i % len(date_posted)],
            "url": f"https://example.com/job/{i+1}",
            "source": "Sample Data"
        }
        jobs.append(job)
    
    return jobs


def generate_sample_matches(jobs, min_score=50):
    """Generate sample job matches for demonstration purposes."""
    matches = []
    
    for i, job in enumerate(jobs):
        # Calculate a sample match score based on job index
        # First job has highest score, decreasing for subsequent jobs
        match_score = 95 - (i * 10)
        if match_score < min_score:
            match_score = min_score
        
        # Add match details to the job
        job_with_score = job.copy()
        job_with_score["match_score"] = match_score
        job_with_score["match_details"] = {
            "skill_score": round(match_score * 1.05, 2) if match_score * 1.05 <= 100 else 100,
            "experience_score": round(match_score * 0.95, 2),
            "education_score": round(match_score * 0.9, 2),
            "overall_score": round(match_score * 1.0, 2)
        }
        
        matches.append(job_with_score)
    
    # Sort by match score (descending)
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matches


def generate_sample_cover_letter(resume_data, job_data, tone="formal"):
    """Generate a sample cover letter for demonstration purposes."""
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Sample cover letter
    cover_letter = f"""
{resume_data['contact_info']['name']}
{resume_data['contact_info']['email']}
{resume_data['contact_info']['phone']}

{current_date}

{job_data['company']}
Hiring Manager
{job_data['company']}

Dear Hiring Manager,

I am writing to express my interest in the {job_data['title']} position at {job_data['company']} that I found on {job_data['source']}. With my background in software development and experience with {'Python' if 'Python' in job_data['title'] else 'web development'}, I believe I would be a valuable addition to your team.

My experience as a {resume_data['experience'][0]['title']} at {resume_data['experience'][0]['company']} has equipped me with the skills necessary to excel in this role. I have successfully {resume_data['experience'][0]['description'][0].lower()} and {resume_data['experience'][0]['description'][1].lower()}.

I am particularly drawn to {job_data['company']} because of its reputation for innovation and excellence. The opportunity to {job_data['description'].split('.')[0].lower()} aligns perfectly with my career goals and technical expertise.

My resume highlights my qualifications, but I would welcome the opportunity to discuss how my background, technical skills, and experiences would benefit your organization in an interview.

Thank you for considering my application. I look forward to the possibility of working with {job_data['company']} and contributing to your continued success.

{'Sincerely' if tone == 'formal' else 'Best regards'},

{resume_data['contact_info']['name']}
"""
    
    return cover_letter
