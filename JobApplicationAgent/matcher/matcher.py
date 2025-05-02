"""
Job Matching Engine Module

This module matches parsed resume data with job descriptions to rank
job listings based on relevance to the candidate's profile.
"""

import json
import re
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class JobMatcher:
    """Class to match resumes with job descriptions."""

    def __init__(self, use_transformer: bool = True):
        """
        Initialize the JobMatcher.

        Args:
            use_transformer: If True, use BERT sentence embeddings for matching,
                            otherwise use TF-IDF
        """
        self.use_transformer = use_transformer
        
        if use_transformer:
            try:
                # Load the sentence transformer model
                self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            except Exception as e:
                print(f"Error loading transformer model: {e}")
                print("Falling back to TF-IDF vectorizer")
                self.use_transformer = False
        
        if not self.use_transformer:
            # Initialize TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=10000,
                ngram_range=(1, 2)
            )

    def match_resume_to_jobs(self, resume_data: Dict[str, Any], 
                             job_listings: List[Dict[str, Any]],
                             weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Match a resume to job listings and rank them by relevance.

        Args:
            resume_data: Parsed resume data
            job_listings: List of job listings
            weights: Dictionary of weights for different matching criteria

        Returns:
            List of job listings with added match scores, sorted by relevance
        """
        if not weights:
            weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'overall': 0.1
            }
        
        # Prepare resume text for matching
        resume_text = self._prepare_resume_text(resume_data)
        
        # Extract resume skills
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        
        # Extract resume experience
        resume_experience = []
        for exp in resume_data.get('experience', []):
            if exp.get('title'):
                resume_experience.append(exp['title'].lower())
            if exp.get('description'):
                resume_experience.extend([desc.lower() for desc in exp['description']])
        
        # Extract resume education
        resume_education = []
        for edu in resume_data.get('education', []):
            if edu.get('degree'):
                resume_education.append(edu['degree'].lower())
            if edu.get('institution'):
                resume_education.append(edu['institution'].lower())
        
        # Match each job
        scored_jobs = []
        for job in job_listings:
            # Prepare job text
            job_text = self._prepare_job_text(job)
            
            # Calculate match scores
            skill_score = self._calculate_skill_match(resume_skills, job_text)
            experience_score = self._calculate_experience_match(resume_experience, job_text)
            education_score = self._calculate_education_match(resume_education, job_text)
            overall_score = self._calculate_overall_match(resume_text, job_text)
            
            # Calculate weighted score
            weighted_score = (
                weights['skills'] * skill_score +
                weights['experience'] * experience_score +
                weights['education'] * education_score +
                weights['overall'] * overall_score
            )
            
            # Add scores to job
            job_with_score = job.copy()
            job_with_score['match_details'] = {
                'skill_score': round(skill_score * 100, 2),
                'experience_score': round(experience_score * 100, 2),
                'education_score': round(education_score * 100, 2),
                'overall_score': round(overall_score * 100, 2),
                'weighted_score': round(weighted_score * 100, 2)
            }
            job_with_score['match_score'] = round(weighted_score * 100, 2)
            
            scored_jobs.append(job_with_score)
        
        # Sort jobs by match score (descending)
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_jobs

    def _prepare_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """
        Prepare resume text for matching.

        Args:
            resume_data: Parsed resume data

        Returns:
            Processed resume text
        """
        resume_parts = []
        
        # Add summary
        if resume_data.get('summary'):
            resume_parts.append(resume_data['summary'])
        
        # Add skills
        if resume_data.get('skills'):
            resume_parts.append(' '.join(resume_data['skills']))
        
        # Add experience
        for exp in resume_data.get('experience', []):
            if exp.get('title'):
                resume_parts.append(exp['title'])
            if exp.get('company'):
                resume_parts.append(exp['company'])
            if exp.get('description'):
                resume_parts.append(' '.join(exp['description']))
        
        # Add education
        for edu in resume_data.get('education', []):
            if edu.get('degree'):
                resume_parts.append(edu['degree'])
            if edu.get('institution'):
                resume_parts.append(edu['institution'])
        
        # Add certifications
        for cert in resume_data.get('certifications', []):
            if cert.get('name'):
                resume_parts.append(cert['name'])
        
        # Join all parts
        resume_text = ' '.join(resume_parts)
        
        # Clean text
        resume_text = self._clean_text(resume_text)
        
        return resume_text

    def _prepare_job_text(self, job: Dict[str, Any]) -> str:
        """
        Prepare job text for matching.

        Args:
            job: Job listing data

        Returns:
            Processed job text
        """
        job_parts = []
        
        # Add title
        if job.get('title'):
            job_parts.append(job['title'])
        
        # Add company
        if job.get('company'):
            job_parts.append(job['company'])
        
        # Add description
        if job.get('description'):
            job_parts.append(job['description'])
        
        # Join all parts
        job_text = ' '.join(job_parts)
        
        # Clean text
        job_text = self._clean_text(job_text)
        
        return job_text

    def _clean_text(self, text: str) -> str:
        """
        Clean text for matching.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _calculate_skill_match(self, resume_skills: set, job_text: str) -> float:
        """
        Calculate skill match score.

        Args:
            resume_skills: Set of skills from the resume
            job_text: Processed job text

        Returns:
            Skill match score (0-1)
        """
        if not resume_skills:
            return 0.0
        
        # Count how many resume skills are mentioned in the job text
        mentioned_skills = sum(1 for skill in resume_skills if skill in job_text)
        
        # Calculate score as the ratio of mentioned skills to total skills
        score = mentioned_skills / len(resume_skills) if resume_skills else 0.0
        
        return min(score, 1.0)  # Cap at 1.0

    def _calculate_experience_match(self, resume_experience: List[str], job_text: str) -> float:
        """
        Calculate experience match score.

        Args:
            resume_experience: List of experience items from the resume
            job_text: Processed job text

        Returns:
            Experience match score (0-1)
        """
        if not resume_experience:
            return 0.0
        
        # Count how many experience items are mentioned in the job text
        mentioned_experience = sum(1 for exp in resume_experience if exp in job_text)
        
        # Calculate score as the ratio of mentioned experience to total experience
        score = mentioned_experience / len(resume_experience) if resume_experience else 0.0
        
        return min(score, 1.0)  # Cap at 1.0

    def _calculate_education_match(self, resume_education: List[str], job_text: str) -> float:
        """
        Calculate education match score.

        Args:
            resume_education: List of education items from the resume
            job_text: Processed job text

        Returns:
            Education match score (0-1)
        """
        if not resume_education:
            return 0.0
        
        # Count how many education items are mentioned in the job text
        mentioned_education = sum(1 for edu in resume_education if edu in job_text)
        
        # Calculate score as the ratio of mentioned education to total education
        score = mentioned_education / len(resume_education) if resume_education else 0.0
        
        return min(score, 1.0)  # Cap at 1.0

    def _calculate_overall_match(self, resume_text: str, job_text: str) -> float:
        """
        Calculate overall match score using either TF-IDF or BERT embeddings.

        Args:
            resume_text: Processed resume text
            job_text: Processed job text

        Returns:
            Overall match score (0-1)
        """
        if self.use_transformer:
            return self._calculate_transformer_match(resume_text, job_text)
        else:
            return self._calculate_tfidf_match(resume_text, job_text)

    def _calculate_transformer_match(self, resume_text: str, job_text: str) -> float:
        """
        Calculate match score using BERT sentence embeddings.

        Args:
            resume_text: Processed resume text
            job_text: Processed job text

        Returns:
            Match score (0-1)
        """
        try:
            # Encode texts
            resume_embedding = self.model.encode([resume_text])[0]
            job_embedding = self.model.encode([job_text])[0]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                resume_embedding.reshape(1, -1),
                job_embedding.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating transformer match: {e}")
            return self._calculate_tfidf_match(resume_text, job_text)

    def _calculate_tfidf_match(self, resume_text: str, job_text: str) -> float:
        """
        Calculate match score using TF-IDF vectors.

        Args:
            resume_text: Processed resume text
            job_text: Processed job text

        Returns:
            Match score (0-1)
        """
        try:
            # Combine texts for vectorization
            texts = [resume_text, job_text]
            
            # Fit and transform texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating TF-IDF match: {e}")
            return 0.0

    def explain_match(self, resume_data: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain why a job matches a resume.

        Args:
            resume_data: Parsed resume data
            job: Job listing data

        Returns:
            Dictionary with match explanation
        """
        explanation = {
            "matching_skills": [],
            "matching_experience": [],
            "matching_education": [],
            "missing_skills": []
        }
        
        # Extract job text
        job_text = self._prepare_job_text(job)
        
        # Find matching skills
        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        for skill in resume_skills:
            if skill in job_text:
                explanation["matching_skills"].append(skill)
        
        # Find matching experience
        for exp in resume_data.get('experience', []):
            title = exp.get('title', '').lower()
            if title and title in job_text:
                explanation["matching_experience"].append(title)
        
        # Find matching education
        for edu in resume_data.get('education', []):
            degree = edu.get('degree', '').lower()
            if degree and degree in job_text:
                explanation["matching_education"].append(degree)
        
        # Extract potential required skills from job description
        # This is a simple approach; a more robust solution would use NER
        skill_keywords = [
            "Python", "Java", "JavaScript", "C\\+\\+", "C#", "Ruby", "PHP", "Swift", "Kotlin",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Express",
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git"
        ]
        
        skill_pattern = r'\b(' + '|'.join(skill_keywords) + r')\b'
        found_skills = set(re.findall(skill_pattern, job_text, re.IGNORECASE))
        
        # Find missing skills
        for skill in found_skills:
            if skill.lower() not in resume_skills:
                explanation["missing_skills"].append(skill)
        
        return explanation

    def save_matches_to_json(self, matches: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save matched jobs to a JSON file.

        Args:
            matches: List of matched jobs
            output_path: Path where the JSON file will be saved
        """
        if not matches:
            raise ValueError("No matches available.")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2)
            
        print(f"Matched jobs saved to {output_path}")


# Example usage
if __name__ == "__main__":
    # Example data
    resume_data = {
        "skills": ["Python", "JavaScript", "React", "Django", "SQL"],
        "experience": [
            {"title": "Software Engineer", "description": ["Developed web applications", "Worked with APIs"]}
        ],
        "education": [
            {"degree": "Bachelor of Science in Computer Science", "institution": "University of Example"}
        ]
    }
    
    job_listings = [
        {
            "title": "Python Developer",
            "company": "Tech Co",
            "description": "We need a Python developer with Django experience. SQL knowledge is required."
        },
        {
            "title": "Frontend Developer",
            "company": "Web Solutions",
            "description": "Looking for a React developer with JavaScript skills."
        }
    ]
    
    matcher = JobMatcher(use_transformer=False)  # Use TF-IDF for simplicity in this example
    matches = matcher.match_resume_to_jobs(resume_data, job_listings)
    
    # Print matches
    for job in matches:
        print(f"{job['title']} - Match Score: {job['match_score']}%")
