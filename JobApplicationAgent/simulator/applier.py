"""
Application Simulator Module

This module simulates job applications by logging selected jobs to a CSV or JSON file.
In a real implementation, this would use Selenium or Playwright to automate the application process.
"""

import os
import json
import csv
import datetime
from typing import Dict, Any, List, Optional, Union


class ApplicationSimulator:
    """Class to simulate job applications."""

    def __init__(self, output_dir: str = "applications"):
        """
        Initialize the ApplicationSimulator.

        Args:
            output_dir: Directory where application logs will be saved
        """
        self.output_dir = output_dir
        self.applications = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def apply_to_job(self, job: Dict[str, Any], resume_path: str, 
                     cover_letter_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate applying to a job.

        Args:
            job: Job listing data
            resume_path: Path to the resume file
            cover_letter_path: Path to the cover letter file (optional)

        Returns:
            Application record
        """
        # Create application record
        application = {
            "job_title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Unknown Location"),
            "job_url": job.get("url", ""),
            "date_applied": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Applied",
            "resume_path": resume_path,
            "cover_letter_path": cover_letter_path,
            "application_id": f"APP-{len(self.applications) + 1:04d}",
            "notes": ""
        }
        
        # Add to applications list
        self.applications.append(application)
        
        # Log the application
        self._log_application(application)
        
        return application

    def skip_job(self, job: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        """
        Record a job as skipped.

        Args:
            job: Job listing data
            reason: Reason for skipping the job

        Returns:
            Application record
        """
        # Create application record
        application = {
            "job_title": job.get("title", "Unknown Title"),
            "company": job.get("company", "Unknown Company"),
            "location": job.get("location", "Unknown Location"),
            "job_url": job.get("url", ""),
            "date_applied": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Skipped",
            "resume_path": "",
            "cover_letter_path": "",
            "application_id": f"APP-{len(self.applications) + 1:04d}",
            "notes": reason
        }
        
        # Add to applications list
        self.applications.append(application)
        
        # Log the application
        self._log_application(application)
        
        return application

    def update_application_status(self, application_id: str, new_status: str, notes: str = "") -> Optional[Dict[str, Any]]:
        """
        Update the status of an application.

        Args:
            application_id: ID of the application to update
            new_status: New status (Applied, Skipped, Rejected, Interview, Offer, Accepted)
            notes: Additional notes

        Returns:
            Updated application record or None if not found
        """
        # Find the application
        for i, app in enumerate(self.applications):
            if app["application_id"] == application_id:
                # Update status and notes
                self.applications[i]["status"] = new_status
                if notes:
                    self.applications[i]["notes"] = notes
                
                # Log the updated applications
                self._save_applications_to_csv()
                self._save_applications_to_json()
                
                return self.applications[i]
        
        return None

    def get_application_by_id(self, application_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an application by ID.

        Args:
            application_id: ID of the application

        Returns:
            Application record or None if not found
        """
        for app in self.applications:
            if app["application_id"] == application_id:
                return app
        
        return None

    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get applications by status.

        Args:
            status: Status to filter by

        Returns:
            List of application records
        """
        return [app for app in self.applications if app["status"] == status]

    def get_applications_by_company(self, company: str) -> List[Dict[str, Any]]:
        """
        Get applications by company.

        Args:
            company: Company to filter by

        Returns:
            List of application records
        """
        return [app for app in self.applications if company.lower() in app["company"].lower()]

    def get_application_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about applications.

        Returns:
            Dictionary with application statistics
        """
        total = len(self.applications)
        
        # Count by status
        status_counts = {}
        for app in self.applications:
            status = app["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by company
        company_counts = {}
        for app in self.applications:
            company = app["company"]
            company_counts[company] = company_counts.get(company, 0) + 1
        
        # Get top companies
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate application rate
        if total > 0:
            first_date = min(datetime.datetime.strptime(app["date_applied"], "%Y-%m-%d %H:%M:%S") 
                            for app in self.applications)
            last_date = max(datetime.datetime.strptime(app["date_applied"], "%Y-%m-%d %H:%M:%S") 
                           for app in self.applications)
            days_span = (last_date - first_date).days + 1
            applications_per_day = total / max(days_span, 1)
        else:
            applications_per_day = 0
        
        return {
            "total_applications": total,
            "status_counts": status_counts,
            "top_companies": top_companies,
            "applications_per_day": round(applications_per_day, 2)
        }

    def _log_application(self, application: Dict[str, Any]) -> None:
        """
        Log an application to CSV and JSON files.

        Args:
            application: Application record
        """
        # Save to CSV and JSON
        self._save_applications_to_csv()
        self._save_applications_to_json()

    def _save_applications_to_csv(self) -> None:
        """Save applications to a CSV file."""
        csv_path = os.path.join(self.output_dir, "applications.csv")
        
        # Define CSV fields
        fields = [
            "application_id", "job_title", "company", "location", 
            "date_applied", "status", "job_url", "resume_path", 
            "cover_letter_path", "notes"
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for app in self.applications:
                writer.writerow({field: app.get(field, "") for field in fields})
        
        print(f"Applications saved to {csv_path}")

    def _save_applications_to_json(self) -> None:
        """Save applications to a JSON file."""
        json_path = os.path.join(self.output_dir, "applications.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, indent=2)
        
        print(f"Applications saved to {json_path}")

    def load_applications(self) -> None:
        """Load applications from the JSON file if it exists."""
        json_path = os.path.join(self.output_dir, "applications.json")
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.applications = json.load(f)
                print(f"Loaded {len(self.applications)} applications from {json_path}")
            except Exception as e:
                print(f"Error loading applications: {e}")


# Example usage
if __name__ == "__main__":
    simulator = ApplicationSimulator()
    
    # Load existing applications
    simulator.load_applications()
    
    # Example job
    job = {
        "title": "Python Developer",
        "company": "Tech Solutions Inc.",
        "location": "New York, NY",
        "url": "https://example.com/job/1"
    }
    
    # Simulate applying to a job
    application = simulator.apply_to_job(
        job=job,
        resume_path="resume.pdf",
        cover_letter_path="cover_letter.pdf"
    )
    
    # Update application status
    simulator.update_application_status(
        application_id=application["application_id"],
        new_status="Interview",
        notes="Phone interview scheduled for next week"
    )
    
    # Get application statistics
    stats = simulator.get_application_statistics()
    print(f"Total applications: {stats['total_applications']}")
    print(f"Applications by status: {stats['status_counts']}")
