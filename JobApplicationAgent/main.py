"""
JobApplicationAgent - Main Module

This is the main entry point for the JobApplicationAgent application.
It provides a simple interface to access all the functionality of the application.
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional

# Import modules from the JobApplicationAgent package
from JobApplicationAgent.resume_parser.parser import ResumeParser
from JobApplicationAgent.job_scraper.scraper import JobScraper
from JobApplicationAgent.matcher.matcher import JobMatcher
from JobApplicationAgent.cover_letter.generator import CoverLetterGenerator
from JobApplicationAgent.simulator.applier import ApplicationSimulator
from JobApplicationAgent.cli.cli import JobApplicationAgentCLI
from JobApplicationAgent.utils.helpers import setup_logging, save_json, load_json


class JobApplicationAgent:
    """Main class for the JobApplicationAgent application."""

    def __init__(self, output_dir: str = "job_application_data"):
        """
        Initialize the JobApplicationAgent.

        Args:
            output_dir: Directory where output files will be saved
        """
        # Set up output directory
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up logging
        self.logger = setup_logging(
            log_file=os.path.join(output_dir, "job_application_agent.log")
        )
        
        # Initialize components
        self.resume_parser = ResumeParser()
        self.job_scraper = JobScraper()
        self.job_matcher = JobMatcher()
        self.cover_letter_generator = CoverLetterGenerator()
        self.application_simulator = ApplicationSimulator(
            output_dir=os.path.join(output_dir, "applications")
        )
        
        # Initialize data
        self.resume_data = None
        self.job_listings = []
        self.matched_jobs = []
        
        self.logger.info("JobApplicationAgent initialized")

    def parse_resume(self, resume_path: str) -> Dict[str, Any]:
        """
        Parse a resume file.

        Args:
            resume_path: Path to the resume file

        Returns:
            Parsed resume data
        """
        self.logger.info(f"Parsing resume: {resume_path}")
        
        try:
            self.resume_data = self.resume_parser.parse(resume_path)
            
            # Save resume data
            save_json(
                self.resume_data,
                os.path.join(self.output_dir, "resume_data.json")
            )
            
            self.logger.info("Resume parsed successfully")
            return self.resume_data
            
        except Exception as e:
            self.logger.error(f"Error parsing resume: {e}")
            raise

    def scrape_jobs(self, keywords: str, location: str, remote: bool = False,
                   limit: int = 20, use_sample: bool = False) -> List[Dict[str, Any]]:
        """
        Scrape job listings.

        Args:
            keywords: Job keywords to search for
            location: Location to search in
            remote: If True, search for remote jobs
            limit: Maximum number of jobs to scrape
            use_sample: If True, use sample data instead of making actual requests

        Returns:
            List of job listings
        """
        self.logger.info(f"Scraping jobs for: {keywords} in {location}")
        
        try:
            # Configure scraper to use sample data if requested
            self.job_scraper.use_sample_html = use_sample
            
            # Scrape from Indeed
            indeed_jobs = self.job_scraper.scrape_indeed(
                keywords=keywords,
                location=location,
                remote=remote,
                limit=limit
            )
            
            # Scrape from LinkedIn
            linkedin_jobs = self.job_scraper.scrape_linkedin(
                keywords=keywords,
                location=location,
                remote=remote,
                limit=limit
            )
            
            # Combine jobs
            self.job_listings = indeed_jobs + linkedin_jobs
            
            # Add job IDs
            for i, job in enumerate(self.job_listings):
                job["id"] = f"JOB-{i+1:04d}"
            
            # Save job listings
            save_json(
                self.job_listings,
                os.path.join(self.output_dir, "job_listings.json")
            )
            
            self.logger.info(f"Scraped {len(self.job_listings)} jobs")
            return self.job_listings
            
        except Exception as e:
            self.logger.error(f"Error scraping jobs: {e}")
            raise

    def match_jobs(self, min_score: float = 50.0) -> List[Dict[str, Any]]:
        """
        Match resume to job listings.

        Args:
            min_score: Minimum match score (0-100) to include in results

        Returns:
            List of matched jobs
        """
        if not self.resume_data:
            raise ValueError("No resume data available. Parse a resume first.")
            
        if not self.job_listings:
            raise ValueError("No job listings available. Scrape jobs first.")
            
        self.logger.info("Matching resume to job listings")
        
        try:
            self.matched_jobs = self.job_matcher.match_resume_to_jobs(
                resume_data=self.resume_data,
                job_listings=self.job_listings
            )
            
            # Filter by minimum score
            self.matched_jobs = [
                job for job in self.matched_jobs
                if job["match_score"] >= min_score
            ]
            
            # Save matched jobs
            save_json(
                self.matched_jobs,
                os.path.join(self.output_dir, "matched_jobs.json")
            )
            
            self.logger.info(f"Matched {len(self.matched_jobs)} jobs with score >= {min_score}%")
            return self.matched_jobs
            
        except Exception as e:
            self.logger.error(f"Error matching jobs: {e}")
            raise

    def generate_cover_letter(self, job_id: str, tone: str = "formal",
                             output_path: Optional[str] = None) -> str:
        """
        Generate a cover letter for a job.

        Args:
            job_id: ID of the job to generate a cover letter for
            tone: Tone of the cover letter
            output_path: Path where the cover letter will be saved

        Returns:
            Generated cover letter
        """
        if not self.resume_data:
            raise ValueError("No resume data available. Parse a resume first.")
            
        # Find the job
        job = None
        for j in self.matched_jobs + self.job_listings:
            if j.get("id") == job_id:
                job = j
                break
                
        if not job:
            raise ValueError(f"Job not found with ID: {job_id}")
            
        self.logger.info(f"Generating cover letter for: {job['title']} at {job['company']}")
        
        try:
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                resume_data=self.resume_data,
                job_data=job,
                tone=tone
            )
            
            # Determine output path if not provided
            if not output_path:
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
            
            self.logger.info(f"Cover letter generated and saved to {output_path}")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}")
            raise

    def apply_to_job(self, job_id: str, cover_letter_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate applying to a job.

        Args:
            job_id: ID of the job to apply to
            cover_letter_path: Path to the cover letter file

        Returns:
            Application record
        """
        # Find the job
        job = None
        for j in self.matched_jobs + self.job_listings:
            if j.get("id") == job_id:
                job = j
                break
                
        if not job:
            raise ValueError(f"Job not found with ID: {job_id}")
            
        self.logger.info(f"Simulating application to: {job['title']} at {job['company']}")
        
        try:
            # Use a placeholder for the resume path
            resume_path = os.path.join(self.output_dir, "resume.pdf")
            
            application = self.application_simulator.apply_to_job(
                job=job,
                resume_path=resume_path,
                cover_letter_path=cover_letter_path
            )
            
            self.logger.info(f"Application simulated successfully with ID: {application['application_id']}")
            return application
            
        except Exception as e:
            self.logger.error(f"Error applying to job: {e}")
            raise

    def get_application_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about applications.

        Returns:
            Dictionary with application statistics
        """
        return self.application_simulator.get_application_statistics()

    def load_data(self) -> None:
        """Load saved data if available."""
        # Load resume data
        resume_data_path = os.path.join(self.output_dir, "resume_data.json")
        self.resume_data = load_json(resume_data_path)
        
        # Load job listings
        job_listings_path = os.path.join(self.output_dir, "job_listings.json")
        self.job_listings = load_json(job_listings_path) or []
        
        # Load matched jobs
        matched_jobs_path = os.path.join(self.output_dir, "matched_jobs.json")
        self.matched_jobs = load_json(matched_jobs_path) or []
        
        # Load applications
        self.application_simulator.load_applications()
        
        self.logger.info("Data loaded successfully")


def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="JobApplicationAgent - Automate your job application process"
    )
    parser.add_argument("--cli", action="store_true", help="Run the command-line interface")
    args = parser.parse_args()
    
    if args.cli:
        # Run the CLI
        cli = JobApplicationAgentCLI()
        cli.run()
    else:
        # Print usage information
        print("JobApplicationAgent - Automate your job application process")
        print("\nUsage:")
        print("  python -m JobApplicationAgent.main --cli")
        print("\nFor more information, run:")
        print("  python -m JobApplicationAgent.main --cli --help")


if __name__ == "__main__":
    main()
