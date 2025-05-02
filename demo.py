"""
JobApplicationAgent Demo

This is a simplified demo of the JobApplicationAgent application that doesn't require
all the dependencies to be installed.
"""

import os
import json
from datetime import datetime


class DemoJobApplicationAgent:
    """Demo version of the JobApplicationAgent."""

    def __init__(self):
        """Initialize the demo agent."""
        self.output_dir = "job_application_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sample data
        self.resume_data = self._get_sample_resume()
        self.job_listings = self._get_sample_jobs()
        self.matched_jobs = self._get_sample_matches()
        
        print("JobApplicationAgent Demo initialized")

    def _get_sample_resume(self):
        """Get sample resume data."""
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

    def _get_sample_jobs(self):
        """Get sample job listings."""
        return [
            {
                "id": "JOB-0001",
                "title": "Senior Python Developer",
                "company": "Tech Innovations Inc.",
                "location": "New York, NY",
                "description": "We are looking for a Senior Python Developer to join our team. The ideal candidate will have experience with Django, Flask, and RESTful APIs. Knowledge of AWS and Docker is a plus.",
                "salary": "$120,000 - $150,000 a year",
                "date_posted": "2 days ago",
                "url": "https://example.com/job/1",
                "source": "Indeed (Sample)"
            },
            {
                "id": "JOB-0002",
                "title": "Full Stack Developer",
                "company": "WebDev Solutions",
                "location": "Remote",
                "description": "Looking for a Full Stack Developer with experience in React, Node.js, and MongoDB. Must be comfortable working in an agile environment.",
                "salary": "$100,000 - $130,000 a year",
                "date_posted": "Just posted",
                "url": "https://example.com/job/2",
                "source": "Indeed (Sample)"
            },
            {
                "id": "JOB-0003",
                "title": "Frontend Engineer",
                "company": "UI Experts",
                "location": "Boston, MA",
                "description": "Join our team as a Frontend Engineer. Experience with React, Redux, and modern JavaScript frameworks required.",
                "salary": "Not specified",
                "date_posted": "3 days ago",
                "url": "https://example.com/job/3",
                "source": "LinkedIn (Sample)"
            },
            {
                "id": "JOB-0004",
                "title": "DevOps Engineer",
                "company": "Cloud Systems",
                "location": "Seattle, WA",
                "description": "Seeking a DevOps Engineer to manage our cloud infrastructure. Experience with AWS, Docker, Kubernetes, and CI/CD pipelines required.",
                "salary": "$125,000 - $155,000 a year",
                "date_posted": "1 week ago",
                "url": "https://example.com/job/4",
                "source": "Indeed (Sample)"
            },
            {
                "id": "JOB-0005",
                "title": "Data Engineer",
                "company": "Data Insights LLC",
                "location": "San Francisco, CA",
                "description": "Join our team of data engineers to build data pipelines and ETL processes. Experience with Python, SQL, and big data technologies required.",
                "salary": "$130,000 - $160,000 a year",
                "date_posted": "5 days ago",
                "url": "https://example.com/job/5",
                "source": "LinkedIn (Sample)"
            }
        ]

    def _get_sample_matches(self):
        """Get sample matched jobs."""
        matches = []
        
        for i, job in enumerate(self.job_listings):
            # Calculate a sample match score based on job index
            # First job has highest score, decreasing for subsequent jobs
            match_score = 95 - (i * 10)
            if match_score < 50:
                match_score = 50
            
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

    def parse_resume(self, resume_path):
        """Simulate parsing a resume."""
        print(f"[DEMO] Parsing resume: {resume_path}")
        print("Using sample resume data instead of actual parsing")
        
        # Save resume data
        output_path = os.path.join(self.output_dir, "resume_data.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.resume_data, f, indent=2)
        
        print(f"Resume data saved to {output_path}")
        print(f"Name: {self.resume_data['contact_info']['name']}")
        print(f"Skills: {', '.join(self.resume_data['skills'][:5])}...")
        
        return self.resume_data

    def scrape_jobs(self, keywords, location, remote=False, limit=5):
        """Simulate scraping job listings."""
        print(f"[DEMO] Scraping jobs for: {keywords} in {location}")
        if remote:
            print("Searching for remote jobs")
        
        print(f"Using sample job data instead of actual scraping")
        
        # Filter jobs based on keywords and location
        filtered_jobs = []
        for job in self.job_listings[:limit]:
            # Simple keyword matching
            if (keywords.lower() in job["title"].lower() or 
                keywords.lower() in job["description"].lower()):
                # Simple location matching
                if (location.lower() in job["location"].lower() or 
                    (remote and "remote" in job["location"].lower())):
                    filtered_jobs.append(job)
        
        # Save job listings
        output_path = os.path.join(self.output_dir, "job_listings.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_jobs, f, indent=2)
        
        print(f"Scraped {len(filtered_jobs)} jobs and saved to {output_path}")
        
        return filtered_jobs

    def match_jobs(self, min_score=50.0):
        """Simulate matching resume to job listings."""
        print(f"[DEMO] Matching resume to job listings")
        print("Using sample match data instead of actual matching")
        
        # Filter by minimum score
        filtered_matches = [job for job in self.matched_jobs if job["match_score"] >= min_score]
        
        # Save matched jobs
        output_path = os.path.join(self.output_dir, "matched_jobs.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_matches, f, indent=2)
        
        print(f"Matched {len(filtered_matches)} jobs with score >= {min_score}% and saved to {output_path}")
        
        # Print top matches
        if filtered_matches:
            print("\nTop matches:")
            for i, job in enumerate(filtered_matches[:3]):
                print(f"{i+1}. {job['title']} at {job['company']} - Match: {job['match_score']}%")
        
        return filtered_matches

    def generate_cover_letter(self, job_id, tone="formal"):
        """Simulate generating a cover letter."""
        print(f"[DEMO] Generating cover letter for job ID: {job_id}")
        print(f"Tone: {tone}")
        
        # Find the job
        job = None
        for j in self.matched_jobs:
            if j["id"] == job_id:
                job = j
                break
        
        if not job:
            print(f"Job not found with ID: {job_id}")
            return None
        
        print(f"Generating cover letter for: {job['title']} at {job['company']}")
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Sample cover letter
        cover_letter = f"""
{self.resume_data['contact_info']['name']}
{self.resume_data['contact_info']['email']}
{self.resume_data['contact_info']['phone']}

{current_date}

{job['company']}
Hiring Manager
{job['company']}

Dear Hiring Manager,

I am writing to express my interest in the {job['title']} position at {job['company']} that I found on {job['source']}. With my background in software development and experience with {'Python' if 'Python' in job['title'] else 'web development'}, I believe I would be a valuable addition to your team.

My experience as a {self.resume_data['experience'][0]['title']} at {self.resume_data['experience'][0]['company']} has equipped me with the skills necessary to excel in this role. I have successfully {self.resume_data['experience'][0]['description'][0].lower()} and {self.resume_data['experience'][0]['description'][1].lower()}.

I am particularly drawn to {job['company']} because of its reputation for innovation and excellence. The opportunity to {job['description'].split('.')[0].lower()} aligns perfectly with my career goals and technical expertise.

My resume highlights my qualifications, but I would welcome the opportunity to discuss how my background, technical skills, and experiences would benefit your organization in an interview.

Thank you for considering my application. I look forward to the possibility of working with {job['company']} and contributing to your continued success.

{'Sincerely' if tone == 'formal' else 'Best regards'},

{self.resume_data['contact_info']['name']}
"""
        
        # Determine output path
        job_title_slug = job['title'].lower().replace(' ', '_')
        company_slug = job['company'].lower().replace(' ', '_')
        output_path = os.path.join(
            self.output_dir, 
            "cover_letters", 
            f"cover_letter_{job_title_slug}_{company_slug}.txt"
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save cover letter
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        print(f"Cover letter generated and saved to {output_path}")
        
        # Print preview
        print("\nPreview:")
        preview_lines = cover_letter.split('\n')[:10]
        print('\n'.join(preview_lines))
        print("...")
        
        return cover_letter

    def apply_to_job(self, job_id, cover_letter_path=None):
        """Simulate applying to a job."""
        print(f"[DEMO] Applying to job ID: {job_id}")
        
        # Find the job
        job = None
        for j in self.matched_jobs:
            if j["id"] == job_id:
                job = j
                break
        
        if not job:
            print(f"Job not found with ID: {job_id}")
            return None
        
        print(f"Simulating application to: {job['title']} at {job['company']}")
        
        # Create application record
        application = {
            "job_title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "job_url": job["url"],
            "date_applied": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Applied",
            "resume_path": "resume.pdf",
            "cover_letter_path": cover_letter_path or "",
            "application_id": f"APP-{job['id'][4:]}",
            "notes": ""
        }
        
        # Create applications directory if it doesn't exist
        applications_dir = os.path.join(self.output_dir, "applications")
        os.makedirs(applications_dir, exist_ok=True)
        
        # Save application to JSON
        applications_path = os.path.join(applications_dir, "applications.json")
        
        # Load existing applications if file exists
        applications = []
        if os.path.exists(applications_path):
            try:
                with open(applications_path, 'r', encoding='utf-8') as f:
                    applications = json.load(f)
            except:
                applications = []
        
        # Add new application
        applications.append(application)
        
        # Save applications
        with open(applications_path, 'w', encoding='utf-8') as f:
            json.dump(applications, f, indent=2)
        
        print(f"Application simulated successfully with ID: {application['application_id']}")
        print(f"Applications saved to {applications_path}")
        
        return application

    def show_application_status(self):
        """Show application status."""
        print("[DEMO] Showing application status")
        
        # Load applications
        applications_path = os.path.join(self.output_dir, "applications", "applications.json")
        applications = []
        
        if os.path.exists(applications_path):
            try:
                with open(applications_path, 'r', encoding='utf-8') as f:
                    applications = json.load(f)
            except:
                applications = []
        
        # Calculate statistics
        total = len(applications)
        
        # Count by status
        status_counts = {}
        for app in applications:
            status = app["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by company
        company_counts = {}
        for app in applications:
            company = app["company"]
            company_counts[company] = company_counts.get(company, 0) + 1
        
        # Get top companies
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print("\nApplication Statistics:")
        print(f"Total applications: {total}")
        
        if status_counts:
            print("Status breakdown:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
        if top_companies:
            print("\nTop companies applied to:")
            for company, count in top_companies:
                print(f"  {company}: {count}")
        
        print(f"\nShowing {len(applications)} applications:")
        for app in applications:
            print(f"ID: {app['application_id']} | {app['date_applied']} | {app['status']} | "
                  f"{app['job_title']} at {app['company']}")


def main():
    """Main function to demonstrate the JobApplicationAgent."""
    print("JobApplicationAgent Demo")
    print("=" * 50)
    
    # Initialize the agent
    agent = DemoJobApplicationAgent()
    
    while True:
        print("\nAvailable commands:")
        print("1. Parse resume")
        print("2. Scrape jobs")
        print("3. Match jobs")
        print("4. Generate cover letter")
        print("5. Apply to job")
        print("6. Show application status")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ")
        
        if choice == "0":
            print("Exiting demo...")
            break
        elif choice == "1":
            resume_path = input("Enter resume path (or press Enter for sample): ") or "sample_resume.pdf"
            agent.parse_resume(resume_path)
        elif choice == "2":
            keywords = input("Enter job keywords: ") or "Python Developer"
            location = input("Enter location: ") or "New York"
            remote = input("Search for remote jobs? (y/n): ").lower() == "y"
            agent.scrape_jobs(keywords, location, remote)
        elif choice == "3":
            min_score = float(input("Enter minimum match score (0-100): ") or "50")
            agent.match_jobs(min_score)
        elif choice == "4":
            job_id = input("Enter job ID: ") or "JOB-0001"
            tone = input("Enter tone (formal/conversational/enthusiastic): ") or "formal"
            agent.generate_cover_letter(job_id, tone)
        elif choice == "5":
            job_id = input("Enter job ID: ") or "JOB-0001"
            cover_letter_path = input("Enter cover letter path (or press Enter for none): ")
            agent.apply_to_job(job_id, cover_letter_path)
        elif choice == "6":
            agent.show_application_status()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
