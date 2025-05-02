"""
Resume Parser Module

This module extracts information from resume files (PDF or DOCX) and converts them
to a structured JSON format.
"""

import os
import json
import re
import pdfplumber
import docx
import spacy
from typing import Dict, Any, List, Optional, Union

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


class ResumeParser:
    """Class to parse resume files and extract structured information."""

    def __init__(self):
        """Initialize the ResumeParser."""
        self.text = ""
        self.sections = {}
        self.parsed_data = {}

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a resume file and extract structured information.

        Args:
            file_path: Path to the resume file (PDF or DOCX)

        Returns:
            Dict containing structured resume information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract text based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.pdf':
            self.text = self._extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            self.text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Process the extracted text
        self._segment_resume()
        self._extract_information()

        return self.parsed_data

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def _extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from a DOCX file.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text as a string
        """
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _segment_resume(self) -> None:
        """
        Segment the resume into different sections based on common section headers.
        """
        # Common section headers in resumes
        section_headers = [
            "EDUCATION", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS",
            "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE",
            "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "KEY SKILLS",
            "PROJECTS", "PROJECT EXPERIENCE",
            "CERTIFICATIONS", "CERTIFICATES", "LICENSES",
            "SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE",
            "CONTACT", "CONTACT INFORMATION",
            "REFERENCES", "PROFESSIONAL REFERENCES"
        ]

        # Create a regex pattern for section headers
        pattern = r"(?i)^(?:{})(?:\s*|:)$".format("|".join(section_headers))
        
        # Split the text by section headers
        lines = self.text.split('\n')
        current_section = "HEADER"  # Default section for the top of the resume
        self.sections[current_section] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if the line is a section header
            if re.match(pattern, line, re.IGNORECASE):
                current_section = line.upper().strip()
                self.sections[current_section] = []
            else:
                self.sections[current_section].append(line)

    def _extract_information(self) -> None:
        """
        Extract structured information from the segmented resume.
        """
        # Initialize the parsed data structure
        self.parsed_data = {
            "contact_info": self._extract_contact_info(),
            "summary": self._extract_summary(),
            "education": self._extract_education(),
            "experience": self._extract_experience(),
            "skills": self._extract_skills(),
            "certifications": self._extract_certifications(),
            "projects": self._extract_projects()
        }

    def _extract_contact_info(self) -> Dict[str, str]:
        """
        Extract contact information from the resume.

        Returns:
            Dict containing name, email, phone, and location
        """
        contact_info = {
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": ""
        }

        # Extract name from the header section
        if "HEADER" in self.sections and self.sections["HEADER"]:
            contact_info["name"] = self.sections["HEADER"][0]

        # Look for contact information in the header or contact sections
        contact_sections = []
        if "HEADER" in self.sections:
            contact_sections.extend(self.sections["HEADER"])
        if "CONTACT" in self.sections or "CONTACT INFORMATION" in self.sections:
            contact_key = "CONTACT" if "CONTACT" in self.sections else "CONTACT INFORMATION"
            contact_sections.extend(self.sections[contact_key])

        # Process all potential contact sections
        contact_text = "\n".join(contact_sections)
        
        # Extract email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', contact_text)
        if email_match:
            contact_info["email"] = email_match.group(0)

        # Extract phone number
        phone_match = re.search(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', contact_text)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)

        # Extract LinkedIn URL
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', contact_text)
        if linkedin_match:
            contact_info["linkedin"] = "https://www." + linkedin_match.group(0)

        # Extract location (city, state)
        # This is a simplistic approach; a more robust solution would use NER
        doc = nlp(contact_text)
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        if locations:
            contact_info["location"] = ", ".join(locations)

        return contact_info

    def _extract_summary(self) -> str:
        """
        Extract professional summary from the resume.

        Returns:
            Summary text as a string
        """
        summary_sections = ["SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE"]
        for section in summary_sections:
            if section in self.sections and self.sections[section]:
                return " ".join(self.sections[section])
        return ""

    def _extract_education(self) -> List[Dict[str, str]]:
        """
        Extract education information from the resume.

        Returns:
            List of education entries, each containing degree, institution, etc.
        """
        education = []
        education_sections = ["EDUCATION", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS"]
        
        for section in education_sections:
            if section not in self.sections:
                continue
                
            edu_text = "\n".join(self.sections[section])
            doc = nlp(edu_text)
            
            # Split into potential education entries (paragraphs or bullet points)
            entries = re.split(r'\n\s*\n|\n•|\n-|\n\*', edu_text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                edu_entry = {
                    "degree": "",
                    "institution": "",
                    "location": "",
                    "graduation_date": "",
                    "gpa": ""
                }
                
                # Extract degree
                degree_patterns = [
                    r'(Bachelor|Master|Ph\.?D|B\.S|M\.S|M\.B\.A|B\.A|B\.E|M\.E|B\.Tech|M\.Tech)\.?\s+(?:of|in)?\s+([A-Za-z\s]+)',
                    r'([A-Za-z\s]+) (degree|diploma)'
                ]
                
                for pattern in degree_patterns:
                    degree_match = re.search(pattern, entry, re.IGNORECASE)
                    if degree_match:
                        edu_entry["degree"] = degree_match.group(0).strip()
                        break
                
                # Extract institution
                doc_entry = nlp(entry)
                orgs = [ent.text for ent in doc_entry.ents if ent.label_ == "ORG"]
                if orgs:
                    edu_entry["institution"] = orgs[0]
                
                # Extract graduation date
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}', entry)
                if date_match:
                    edu_entry["graduation_date"] = date_match.group(0)
                
                # Extract GPA
                gpa_match = re.search(r'GPA\s*(?:of|:)?\s*(\d+\.\d+)', entry, re.IGNORECASE)
                if gpa_match:
                    edu_entry["gpa"] = gpa_match.group(1)
                
                # Extract location
                locations = [ent.text for ent in doc_entry.ents if ent.label_ == "GPE"]
                if locations:
                    edu_entry["location"] = locations[0]
                
                education.append(edu_entry)
        
        return education

    def _extract_experience(self) -> List[Dict[str, str]]:
        """
        Extract work experience information from the resume.

        Returns:
            List of experience entries, each containing job title, company, etc.
        """
        experience = []
        experience_sections = ["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE"]
        
        for section in experience_sections:
            if section not in self.sections:
                continue
                
            exp_text = "\n".join(self.sections[section])
            
            # Split into potential experience entries (paragraphs or bullet points)
            entries = re.split(r'\n\s*\n|\n(?=\w+\s*\d{4}\s*-)', exp_text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                exp_entry = {
                    "title": "",
                    "company": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "description": []
                }
                
                lines = entry.split('\n')
                
                # First line often contains title and company
                if lines:
                    header = lines[0]
                    
                    # Extract company
                    doc_header = nlp(header)
                    orgs = [ent.text for ent in doc_header.ents if ent.label_ == "ORG"]
                    if orgs:
                        exp_entry["company"] = orgs[0]
                    
                    # Extract job title (if company is found, title is often before it)
                    if exp_entry["company"] and exp_entry["company"] in header:
                        title_part = header.split(exp_entry["company"])[0].strip()
                        if title_part:
                            exp_entry["title"] = title_part
                    
                    # If no title found yet, try to extract from the first line
                    if not exp_entry["title"]:
                        # Common job titles
                        title_patterns = [
                            r'(Software Engineer|Developer|Data Scientist|Project Manager|Product Manager|Analyst|Engineer|Director|VP|Chief|Manager)',
                            r'(Senior|Junior|Lead|Principal|Staff)?\s*(Software|Data|Product|Project|Business|Marketing|Sales)?\s*(Engineer|Developer|Scientist|Analyst|Manager|Designer)'
                        ]
                        
                        for pattern in title_patterns:
                            title_match = re.search(pattern, header, re.IGNORECASE)
                            if title_match:
                                exp_entry["title"] = title_match.group(0).strip()
                                break
                
                # Extract dates
                date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}'
                dates = re.findall(date_pattern, entry)
                if len(dates) >= 2:
                    exp_entry["start_date"] = dates[0]
                    exp_entry["end_date"] = dates[1]
                elif len(dates) == 1:
                    exp_entry["start_date"] = dates[0]
                    if "present" in entry.lower() or "current" in entry.lower():
                        exp_entry["end_date"] = "Present"
                
                # Extract location
                doc_entry = nlp(entry)
                locations = [ent.text for ent in doc_entry.ents if ent.label_ == "GPE"]
                if locations:
                    exp_entry["location"] = locations[0]
                
                # Extract description (bullet points)
                description_lines = []
                bullet_pattern = r'•|-|\*|\d+\.'
                for line in lines[1:]:
                    line = line.strip()
                    if line and (re.match(bullet_pattern, line) or not description_lines):
                        # Remove bullet point markers
                        clean_line = re.sub(r'^(•|-|\*|\d+\.)\s*', '', line)
                        if clean_line:
                            description_lines.append(clean_line)
                
                exp_entry["description"] = description_lines
                
                experience.append(exp_entry)
        
        return experience

    def _extract_skills(self) -> List[str]:
        """
        Extract skills from the resume.

        Returns:
            List of skills
        """
        skills = []
        skills_sections = ["SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "KEY SKILLS"]
        
        for section in skills_sections:
            if section not in self.sections:
                continue
                
            skills_text = "\n".join(self.sections[section])
            
            # Extract skills from bullet points or comma-separated lists
            skill_patterns = [
                r'•\s*([\w\s\(\)\/\-\+\#\.\,]+)',
                r'-\s*([\w\s\(\)\/\-\+\#\.]+)',
                r'\*\s*([\w\s\(\)\/\-\+\#\.]+)',
                r'(\w+[\w\s\(\)\/\-\+\#\.]*)'
            ]
            
            for pattern in skill_patterns:
                found_skills = re.findall(pattern, skills_text)
                for skill in found_skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1:  # Avoid single characters
                        # If the skill contains commas, split it
                        if ',' in skill:
                            sub_skills = [s.strip() for s in skill.split(',')]
                            skills.extend([s for s in sub_skills if s and len(s) > 1])
                        else:
                            skills.append(skill)
        
        # Remove duplicates and sort
        return sorted(list(set(skills)))

    def _extract_certifications(self) -> List[Dict[str, str]]:
        """
        Extract certifications from the resume.

        Returns:
            List of certifications, each containing name, issuer, and date
        """
        certifications = []
        cert_sections = ["CERTIFICATIONS", "CERTIFICATES", "LICENSES"]
        
        for section in cert_sections:
            if section not in self.sections:
                continue
                
            cert_text = "\n".join(self.sections[section])
            
            # Split into potential certification entries
            entries = re.split(r'\n\s*\n|\n•|\n-|\n\*', cert_text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                cert_entry = {
                    "name": "",
                    "issuer": "",
                    "date": ""
                }
                
                # Extract certification name (first part of the entry)
                lines = entry.split('\n')
                if lines:
                    cert_entry["name"] = lines[0].strip()
                
                # Extract issuer
                issuer_pattern = r'(issued|provided|offered|by)\s+([\w\s]+)', 
                issuer_match = re.search(issuer_pattern, entry, re.IGNORECASE)
                if issuer_match:
                    cert_entry["issuer"] = issuer_match.group(2).strip()
                else:
                    # Try to extract organization names
                    doc_entry = nlp(entry)
                    orgs = [ent.text for ent in doc_entry.ents if ent.label_ == "ORG"]
                    if orgs:
                        cert_entry["issuer"] = orgs[0]
                
                # Extract date
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}', entry)
                if date_match:
                    cert_entry["date"] = date_match.group(0)
                
                certifications.append(cert_entry)
        
        return certifications

    def _extract_projects(self) -> List[Dict[str, str]]:
        """
        Extract projects from the resume.

        Returns:
            List of projects, each containing name, description, etc.
        """
        projects = []
        project_sections = ["PROJECTS", "PROJECT EXPERIENCE"]
        
        for section in project_sections:
            if section not in self.sections:
                continue
                
            project_text = "\n".join(self.sections[section])
            
            # Split into potential project entries
            entries = re.split(r'\n\s*\n|\n(?=[\w\s]+:)', project_text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                    
                project_entry = {
                    "name": "",
                    "description": [],
                    "technologies": []
                }
                
                lines = entry.split('\n')
                
                # First line is often the project name
                if lines:
                    project_entry["name"] = lines[0].strip()
                
                # Extract description (bullet points)
                description_lines = []
                bullet_pattern = r'•|-|\*|\d+\.'
                for line in lines[1:]:
                    line = line.strip()
                    if line and (re.match(bullet_pattern, line) or not description_lines):
                        # Remove bullet point markers
                        clean_line = re.sub(r'^(•|-|\*|\d+\.)\s*', '', line)
                        if clean_line:
                            description_lines.append(clean_line)
                
                project_entry["description"] = description_lines
                
                # Extract technologies (look for tech keywords in the description)
                tech_keywords = [
                    "Python", "Java", "JavaScript", "C\\+\\+", "C#", "Ruby", "PHP", "Swift", "Kotlin",
                    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Express",
                    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
                    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite",
                    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git"
                ]
                
                tech_pattern = r'\b(' + '|'.join(tech_keywords) + r')\b'
                found_techs = re.findall(tech_pattern, entry, re.IGNORECASE)
                project_entry["technologies"] = sorted(list(set(found_techs)))
                
                projects.append(project_entry)
        
        return projects

    def save_to_json(self, output_path: str) -> None:
        """
        Save the parsed resume data to a JSON file.

        Args:
            output_path: Path where the JSON file will be saved
        """
        if not self.parsed_data:
            raise ValueError("No parsed data available. Run parse() first.")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.parsed_data, f, indent=2)
            
        print(f"Resume data saved to {output_path}")


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    # Example: parser.parse("path/to/resume.pdf")
    # parser.save_to_json("parsed_resume.json")
