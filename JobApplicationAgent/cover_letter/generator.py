"""
Cover Letter Generator Module

This module generates personalized cover letters using the Gemini API
based on resume data and job descriptions.
"""

import os
import json
import re
from typing import Dict, Any, Optional
import google.generativeai as genai


class CoverLetterGenerator:
    """Class to generate personalized cover letters."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CoverLetterGenerator.

        Args:
            api_key: Gemini API key. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: No Gemini API key provided. Please set GEMINI_API_KEY environment variable or provide it directly.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"Error initializing Gemini API: {e}")
                self.api_key = None

    def generate_cover_letter(self, resume_data: Dict[str, Any], job_data: Dict[str, Any], 
                              tone: str = "formal", custom_instructions: str = "") -> str:
        """
        Generate a personalized cover letter.

        Args:
            resume_data: Parsed resume data
            job_data: Job listing data
            tone: Tone of the cover letter (formal, conversational, enthusiastic)
            custom_instructions: Additional instructions for the cover letter

        Returns:
            Generated cover letter as a string
        """
        if not self.api_key:
            return self._generate_sample_cover_letter(resume_data, job_data, tone)
        
        # Extract relevant information from resume
        name = resume_data.get("contact_info", {}).get("name", "")
        email = resume_data.get("contact_info", {}).get("email", "")
        phone = resume_data.get("contact_info", {}).get("phone", "")
        
        # Extract skills
        skills = resume_data.get("skills", [])
        skills_text = ", ".join(skills[:10])  # Limit to top 10 skills
        
        # Extract experience
        experience = resume_data.get("experience", [])
        experience_text = ""
        for i, exp in enumerate(experience[:3]):  # Limit to top 3 experiences
            title = exp.get("title", "")
            company = exp.get("company", "")
            description = exp.get("description", [])
            
            experience_text += f"{title} at {company}: "
            experience_text += " ".join(description[:2])  # Limit to first 2 bullet points
            if i < min(2, len(experience) - 1):  # Add separator if not the last item
                experience_text += "\n"
        
        # Extract education
        education = resume_data.get("education", [])
        education_text = ""
        for i, edu in enumerate(education[:2]):  # Limit to top 2 education entries
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            
            education_text += f"{degree} from {institution}"
            if i < min(1, len(education) - 1):  # Add separator if not the last item
                education_text += "\n"
        
        # Extract job information
        job_title = job_data.get("title", "")
        company_name = job_data.get("company", "")
        job_description = job_data.get("description", "")
        
        # Prepare the prompt
        prompt = f"""
Write a professional cover letter for the position of {job_title} at {company_name}.

Job Description:
{job_description}

Candidate Information:
Name: {name}
Skills: {skills_text}
Experience: {experience_text}
Education: {education_text}

The tone should be {tone} and enthusiastic.
{custom_instructions}

Format the cover letter with proper sections including:
1. Professional header with contact information
2. Date and addressee (company)
3. Greeting
4. Introduction paragraph that mentions the position
5. Body paragraphs highlighting relevant skills and experience
6. Closing paragraph expressing interest in an interview
7. Professional sign-off

Make the letter concise (no more than 400 words) and tailored specifically to the job description.
Highlight how the candidate's skills and experience align with the job requirements.
"""

        try:
            # Generate the cover letter
            response = self.model.generate_content(prompt)
            cover_letter = response.text
            
            # Clean up the cover letter
            cover_letter = self._clean_cover_letter(cover_letter)
            
            return cover_letter
            
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return self._generate_sample_cover_letter(resume_data, job_data, tone)

    def _clean_cover_letter(self, cover_letter: str) -> str:
        """
        Clean up the generated cover letter.

        Args:
            cover_letter: Generated cover letter

        Returns:
            Cleaned cover letter
        """
        # Remove markdown code blocks if present
        cover_letter = re.sub(r'```[a-z]*\n', '', cover_letter)
        cover_letter = re.sub(r'```', '', cover_letter)
        
        # Remove extra newlines
        cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)
        
        return cover_letter.strip()

    def _generate_sample_cover_letter(self, resume_data: Dict[str, Any], 
                                     job_data: Dict[str, Any], tone: str) -> str:
        """
        Generate a sample cover letter when API is not available.

        Args:
            resume_data: Parsed resume data
            job_data: Job listing data
            tone: Tone of the cover letter

        Returns:
            Sample cover letter as a string
        """
        # Extract basic information
        name = resume_data.get("contact_info", {}).get("name", "Applicant Name")
        email = resume_data.get("contact_info", {}).get("email", "applicant@example.com")
        phone = resume_data.get("contact_info", {}).get("phone", "(555) 123-4567")
        
        job_title = job_data.get("title", "Position")
        company_name = job_data.get("company", "Company")
        
        # Get current date
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Sample cover letter
        cover_letter = f"""
{name}
{email}
{phone}

{current_date}

{company_name}
Hiring Manager
{company_name}

Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. With my background and skills, I believe I would be a valuable addition to your team.

Throughout my career, I have developed a strong set of skills that align well with the requirements outlined in your job posting. My experience has equipped me with the knowledge and abilities necessary to excel in this role.

My resume highlights my qualifications, but I would welcome the opportunity to discuss how my background, technical skills, and experiences would benefit your organization in an interview.

Thank you for considering my application. I look forward to the possibility of working with {company_name} and contributing to your continued success.

Sincerely,

{name}
"""
        
        return cover_letter

    def save_cover_letter(self, cover_letter: str, output_path: str) -> None:
        """
        Save the generated cover letter to a file.

        Args:
            cover_letter: Generated cover letter
            output_path: Path where the cover letter will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
            
        print(f"Cover letter saved to {output_path}")


# Example usage
if __name__ == "__main__":
    # Example data
    resume_data = {
        "contact_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567"
        },
        "skills": ["Python", "JavaScript", "React", "Django", "SQL"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Co",
                "description": ["Developed web applications", "Worked with APIs"]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Example"
            }
        ]
    }
    
    job_data = {
        "title": "Python Developer",
        "company": "Tech Solutions Inc.",
        "description": "We need a Python developer with Django experience. SQL knowledge is required."
    }
    
    # Initialize with a sample API key (replace with your actual key)
    generator = CoverLetterGenerator(api_key=None)  # Use None to generate a sample letter
    
    # Generate cover letter
    cover_letter = generator.generate_cover_letter(resume_data, job_data, tone="formal")
    
    # Print the cover letter
    print(cover_letter)
