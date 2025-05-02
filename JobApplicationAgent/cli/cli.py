"""
Command-Line Interface Module

This module provides a command-line interface for the JobApplicationAgent application.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import modules from the JobApplicationAgent package
from JobApplicationAgent.resume_parser.parser import ResumeParser
from JobApplicationAgent.job_scraper.scraper import JobScraper
from JobApplicationAgent.matcher.matcher import JobMatcher
from JobApplicationAgent.cover_letter.generator import CoverLetterGenerator
from JobApplicationAgent.simulator.applier import ApplicationSimulator


class JobApplicationAgentCLI:
    """Command-line interface for the JobApplicationAgent application."""

    def __init__(self):
        """Initialize the CLI."""
        self.parser = argparse.ArgumentParser(
            description="JobApplicationAgent - Automate your job application process",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Set up output directory
        self.output_dir = os.path.join(os.getcwd(), "job_application_data")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.resume_parser = ResumeParser()
        self.job_scraper = JobScraper(use_sample_html=True)  # Use sample HTML for demo
        self.job_matcher = JobMatcher()
        self.cover_letter_generator = CoverLetterGenerator()
        self.application_simulator = ApplicationSimulator(output_dir=os.path.join(self.output_dir, "applications"))
        
        # Load existing data if available
        self.resume_data = self._load_json(os.path.join(self.output_dir, "resume_data.json"))
        self.job_listings = self._load_json(os.path.join(self.output_dir, "job_listings.json"))
        self.matched_jobs = self._load_json(os.path.join(self.output_dir, "matched_jobs.json"))
        
        # Load existing applications
        self.application_simulator.load_applications()
        
        # Set up subparsers for commands
        self._setup_parsers()

    def _setup_parsers(self):
        """Set up command-line argument parsers."""
        subparsers = self.parser.add_subparsers(dest="command", help="Command to execute")
        
        # Upload resume command
        parser_upload = subparsers.add_parser("upload-resume", help="Upload and parse a resume")
        parser_upload.add_argument("resume_path", help="Path to the resume file (PDF or DOCX)")
        
        # Scrape jobs command
        parser_scrape = subparsers.add_parser("scrape-jobs", help="Scrape job listings")
        parser_scrape.add_argument("--keywords", required=True, help="Job keywords to search for")
        parser_scrape.add_argument("--location", required=True, help="Location to search in")
        parser_scrape.add_argument("--remote", action="store_true", help="Search for remote jobs")
        parser_scrape.add_argument("--limit", type=int, default=20, help="Maximum number of jobs to scrape")
        parser_scrape.add_argument("--source", choices=["indeed", "linkedin", "both"], default="both", 
                                  help="Job source to scrape from")
        
        # Match jobs command
        parser_match = subparsers.add_parser("match-jobs", help="Match resume to job listings")
        parser_match.add_argument("--min-score", type=float, default=50.0, 
                                 help="Minimum match score (0-100) to include in results")
        
        # Generate cover letter command
        parser_cover = subparsers.add_parser("generate-cover-letter", help="Generate a cover letter")
        parser_cover.add_argument("--job-id", required=True, help="ID of the job to generate a cover letter for")
        parser_cover.add_argument("--tone", choices=["formal", "conversational", "enthusiastic"], 
                                 default="formal", help="Tone of the cover letter")
        parser_cover.add_argument("--output", help="Output file path for the cover letter")
        
        # Apply to job command
        parser_apply = subparsers.add_parser("apply", help="Simulate applying to a job")
        parser_apply.add_argument("--job-id", required=True, help="ID of the job to apply to")
        parser_apply.add_argument("--cover-letter", help="Path to the cover letter file")
        
        # Skip job command
        parser_skip = subparsers.add_parser("skip", help="Skip a job")
        parser_skip.add_argument("--job-id", required=True, help="ID of the job to skip")
        parser_skip.add_argument("--reason", help="Reason for skipping the job")
        
        # Update application status command
        parser_update = subparsers.add_parser("update-status", help="Update application status")
        parser_update.add_argument("--app-id", required=True, help="ID of the application to update")
        parser_update.add_argument("--status", required=True, 
                                  choices=["Applied", "Skipped", "Rejected", "Interview", "Offer", "Accepted"],
                                  help="New status")
        parser_update.add_argument("--notes", help="Additional notes")
        
        # Show application status command
        parser_status = subparsers.add_parser("status", help="Show application status")
        parser_status.add_argument("--filter", choices=["all", "applied", "skipped", "rejected", "interview", "offer", "accepted"],
                                  default="all", help="Filter by status")
        
        # List jobs command
        parser_list = subparsers.add_parser("list-jobs", help="List scraped jobs")
        parser_list.add_argument("--matched", action="store_true", help="List matched jobs instead of all jobs")
        parser_list.add_argument("--limit", type=int, default=10, help="Maximum number of jobs to list")
        
        # Show job details command
        parser_show = subparsers.add_parser("show-job", help="Show job details")
        parser_show.add_argument("--job-id", required=True, help="ID of the job to show")

    def run(self):
        """Run the CLI."""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        # Execute the appropriate command
        if args.command == "upload-resume":
            self._upload_resume(args)
        elif args.command == "scrape-jobs":
            self._scrape_jobs(args)
        elif args.command == "match-jobs":
            self._match_jobs(args)
        elif args.command == "generate-cover-letter":
            self._generate_cover_letter(args)
        elif args.command == "apply":
            self._apply_to_job(args)
        elif args.command == "skip":
            self._skip_job(args)
        elif args.command == "update-status":
            self._update_application_status(args)
        elif args.command == "status":
            self._show_application_status(args)
        elif args.command == "list-jobs":
            self._list_jobs(args)
        elif args.command == "show-job":
            self._show_job_details(args)

    def _upload_resume(self, args):
        """
        Upload and parse a resume.
        
        Args:
            args: Command-line arguments
        """
        resume_path = args.resume_path
        
        if not os.path.exists(resume_path):
            print(f"Error: Resume file not found: {resume_path}")
            return
        
        print(f"Parsing resume: {resume_path}")
        try:
            self.resume_data = self.resume_parser.parse(resume_path)
            
            # Save resume data
            output_path = os.path.join(self.output_dir, "resume_data.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.resume_data, f, indent=2)
            
            print(f"Resume parsed successfully and saved to {output_path}")
            print(f"Name: {self.resume_data.get('contact_info', {}).get('name', 'Unknown')}")
            print(f"Skills: {', '.join(self.resume_data.get('skills', [])[:5])}...")
            
        except Exception as e:
            print(f"Error parsing resume: {e}")

    def _scrape_jobs(self, args):
        """
        Scrape job listings.
        
        Args:
            args: Command-line arguments
        """
        keywords = args.keywords
        location = args.location
        remote = args.remote
        limit = args.limit
        source = args.source
        
        print(f"Scraping jobs for: {keywords} in {location}")
        if remote:
            print("Searching for remote jobs")
        
        try:
            self.job_listings = []
            
            if source in ["indeed", "both"]:
                print("Scraping from Indeed...")
                indeed_jobs = self.job_scraper.scrape_indeed(
                    keywords=keywords,
                    location=location,
                    remote=remote,
                    limit=limit
                )
                self.job_listings.extend(indeed_jobs)
            
            if source in ["linkedin", "both"]:
                print("Scraping from LinkedIn...")
                linkedin_jobs = self.job_scraper.scrape_linkedin(
                    keywords=keywords,
                    location=location,
                    remote=remote,
                    limit=limit
                )
                self.job_listings.extend(linkedin_jobs)
            
            # Add job IDs
            for i, job in enumerate(self.job_listings):
                job["id"] = f"JOB-{i+1:04d}"
            
            # Save job listings
            output_path = os.path.join(self.output_dir, "job_listings.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.job_listings, f, indent=2)
            
            print(f"Scraped {len(self.job_listings)} jobs and saved to {output_path}")
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")

    def _match_jobs(self, args):
        """
        Match resume to job listings.
        
        Args:
            args: Command-line arguments
        """
        min_score = args.min_score
        
        if not self.resume_data:
            print("Error: No resume data available. Upload a resume first.")
            return
        
        if not self.job_listings:
            print("Error: No job listings available. Scrape jobs first.")
            return
        
        print("Matching resume to job listings...")
        try:
            self.matched_jobs = self.job_matcher.match_resume_to_jobs(
                resume_data=self.resume_data,
                job_listings=self.job_listings
            )
            
            # Filter by minimum score
            self.matched_jobs = [job for job in self.matched_jobs if job["match_score"] >= min_score]
            
            # Save matched jobs
            output_path = os.path.join(self.output_dir, "matched_jobs.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.matched_jobs, f, indent=2)
            
            print(f"Matched {len(self.matched_jobs)} jobs with score >= {min_score}% and saved to {output_path}")
            
            # Print top 5 matches
            if self.matched_jobs:
                print("\nTop matches:")
                for i, job in enumerate(self.matched_jobs[:5]):
                    print(f"{i+1}. {job['title']} at {job['company']} - Match: {job['match_score']}%")
            
        except Exception as e:
            print(f"Error matching jobs: {e}")

    def _generate_cover_letter(self, args):
        """
        Generate a cover letter.
        
        Args:
            args: Command-line arguments
        """
        job_id = args.job_id
        tone = args.tone
        output = args.output
        
        if not self.resume_data:
            print("Error: No resume data available. Upload a resume first.")
            return
        
        # Find the job
        job = self._find_job_by_id(job_id)
        if not job:
            print(f"Error: Job not found with ID: {job_id}")
            return
        
        print(f"Generating cover letter for: {job['title']} at {job['company']}")
        try:
            cover_letter = self.cover_letter_generator.generate_cover_letter(
                resume_data=self.resume_data,
                job_data=job,
                tone=tone
            )
            
            # Determine output path
            if not output:
                job_title_slug = job['title'].lower().replace(' ', '_')
                company_slug = job['company'].lower().replace(' ', '_')
                output = os.path.join(
                    self.output_dir, 
                    "cover_letters", 
                    f"cover_letter_{job_title_slug}_{company_slug}.txt"
                )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output), exist_ok=True)
            
            # Save cover letter
            with open(output, 'w', encoding='utf-8') as f:
                f.write(cover_letter)
            
            print(f"Cover letter generated and saved to {output}")
            
            # Print preview
            print("\nPreview:")
            preview_lines = cover_letter.split('\n')[:10]
            print('\n'.join(preview_lines))
            if len(preview_lines) < len(cover_letter.split('\n')):
                print("...")
            
        except Exception as e:
            print(f"Error generating cover letter: {e}")

    def _apply_to_job(self, args):
        """
        Simulate applying to a job.
        
        Args:
            args: Command-line arguments
        """
        job_id = args.job_id
        cover_letter_path = args.cover_letter
        
        if not self.resume_data:
            print("Error: No resume data available. Upload a resume first.")
            return
        
        # Find the job
        job = self._find_job_by_id(job_id)
        if not job:
            print(f"Error: Job not found with ID: {job_id}")
            return
        
        # Check if cover letter exists
        if cover_letter_path and not os.path.exists(cover_letter_path):
            print(f"Warning: Cover letter file not found: {cover_letter_path}")
            cover_letter_path = None
        
        print(f"Simulating application to: {job['title']} at {job['company']}")
        try:
            # Use a placeholder for the resume path
            resume_path = os.path.join(self.output_dir, "resume.pdf")
            
            application = self.application_simulator.apply_to_job(
                job=job,
                resume_path=resume_path,
                cover_letter_path=cover_letter_path
            )
            
            print(f"Application simulated successfully with ID: {application['application_id']}")
            
        except Exception as e:
            print(f"Error applying to job: {e}")

    def _skip_job(self, args):
        """
        Skip a job.
        
        Args:
            args: Command-line arguments
        """
        job_id = args.job_id
        reason = args.reason or "No reason provided"
        
        # Find the job
        job = self._find_job_by_id(job_id)
        if not job:
            print(f"Error: Job not found with ID: {job_id}")
            return
        
        print(f"Skipping job: {job['title']} at {job['company']}")
        try:
            application = self.application_simulator.skip_job(
                job=job,
                reason=reason
            )
            
            print(f"Job skipped with ID: {application['application_id']}")
            
        except Exception as e:
            print(f"Error skipping job: {e}")

    def _update_application_status(self, args):
        """
        Update application status.
        
        Args:
            args: Command-line arguments
        """
        app_id = args.app_id
        status = args.status
        notes = args.notes or ""
        
        print(f"Updating application {app_id} to status: {status}")
        try:
            application = self.application_simulator.update_application_status(
                application_id=app_id,
                new_status=status,
                notes=notes
            )
            
            if application:
                print(f"Application status updated successfully: {application['job_title']} at {application['company']}")
            else:
                print(f"Error: Application not found with ID: {app_id}")
            
        except Exception as e:
            print(f"Error updating application status: {e}")

    def _show_application_status(self, args):
        """
        Show application status.
        
        Args:
            args: Command-line arguments
        """
        filter_status = args.filter
        
        try:
            # Get applications
            if filter_status == "all":
                applications = self.application_simulator.applications
            else:
                # Convert filter to proper case (e.g., "applied" -> "Applied")
                status = filter_status.capitalize()
                applications = self.application_simulator.get_applications_by_status(status)
            
            # Get statistics
            stats = self.application_simulator.get_application_statistics()
            
            print("\nApplication Statistics:")
            print(f"Total applications: {stats['total_applications']}")
            print("Status breakdown:")
            for status, count in stats.get('status_counts', {}).items():
                print(f"  {status}: {count}")
            
            print(f"\nApplications per day: {stats.get('applications_per_day', 0)}")
            
            print("\nTop companies applied to:")
            for company, count in stats.get('top_companies', []):
                print(f"  {company}: {count}")
            
            print(f"\nShowing {len(applications)} applications:")
            for app in applications:
                print(f"ID: {app['application_id']} | {app['date_applied']} | {app['status']} | "
                      f"{app['job_title']} at {app['company']}")
            
        except Exception as e:
            print(f"Error showing application status: {e}")

    def _list_jobs(self, args):
        """
        List scraped or matched jobs.
        
        Args:
            args: Command-line arguments
        """
        matched = args.matched
        limit = args.limit
        
        if matched:
            if not self.matched_jobs:
                print("No matched jobs available. Run match-jobs first.")
                return
            
            jobs = self.matched_jobs[:limit]
            print(f"Showing top {len(jobs)} matched jobs:")
            for job in jobs:
                print(f"ID: {job['id']} | Score: {job['match_score']}% | {job['title']} at {job['company']} | {job['location']}")
        else:
            if not self.job_listings:
                print("No job listings available. Run scrape-jobs first.")
                return
            
            jobs = self.job_listings[:limit]
            print(f"Showing {len(jobs)} job listings:")
            for job in jobs:
                print(f"ID: {job['id']} | {job['title']} at {job['company']} | {job['location']}")

    def _show_job_details(self, args):
        """
        Show job details.
        
        Args:
            args: Command-line arguments
        """
        job_id = args.job_id
        
        # Find the job
        job = self._find_job_by_id(job_id)
        if not job:
            print(f"Error: Job not found with ID: {job_id}")
            return
        
        print("\nJob Details:")
        print(f"ID: {job['id']}")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        
        if 'salary' in job and job['salary'] != "Not specified":
            print(f"Salary: {job['salary']}")
        
        if 'date_posted' in job:
            print(f"Date Posted: {job['date_posted']}")
        
        if 'url' in job:
            print(f"URL: {job['url']}")
        
        print("\nDescription:")
        print(job.get('description', 'No description available'))
        
        # Show match details if available
        if 'match_score' in job:
            print("\nMatch Details:")
            print(f"Overall Match Score: {job['match_score']}%")
            
            if 'match_details' in job:
                details = job['match_details']
                print(f"Skill Match: {details.get('skill_score', 0)}%")
                print(f"Experience Match: {details.get('experience_score', 0)}%")
                print(f"Education Match: {details.get('education_score', 0)}%")

    def _find_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a job by ID.
        
        Args:
            job_id: ID of the job to find
            
        Returns:
            Job data or None if not found
        """
        # Check matched jobs first
        if self.matched_jobs:
            for job in self.matched_jobs:
                if job.get('id') == job_id:
                    return job
        
        # Check all job listings
        if self.job_listings:
            for job in self.job_listings:
                if job.get('id') == job_id:
                    return job
        
        return None

    def _load_json(self, file_path: str) -> Optional[Any]:
        """
        Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded data or None if file doesn't exist or is invalid
        """
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return None


def main():
    """Main entry point for the CLI."""
    cli = JobApplicationAgentCLI()
    cli.run()


if __name__ == "__main__":
    main()
