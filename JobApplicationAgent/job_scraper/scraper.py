"""
Job Scraper Module

This module scrapes job listings from job boards (or sample HTML) and converts
them to a structured JSON format.
"""

import json
import re
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class JobScraper:
    """Class to scrape job listings from job boards."""

    def __init__(self, use_sample_html: bool = False):
        """
        Initialize the JobScraper.

        Args:
            use_sample_html: If True, use sample HTML instead of making actual requests
        """
        self.use_sample_html = use_sample_html
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.jobs = []

    def scrape_indeed(self, keywords: str, location: str, remote: bool = False, 
                      job_type: str = "fulltime", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Indeed.

        Args:
            keywords: Job keywords to search for
            location: Location to search in
            remote: If True, search for remote jobs
            job_type: Type of job (fulltime, parttime, contract, etc.)
            limit: Maximum number of jobs to scrape

        Returns:
            List of job listings as dictionaries
        """
        if self.use_sample_html:
            return self._parse_sample_indeed_html()
        
        base_url = "https://www.indeed.com/jobs"
        jobs = []
        
        # Format the query parameters
        params = {
            'q': keywords,
            'l': location,
            'jt': job_type,
        }
        
        if remote:
            params['remotejob'] = '032b3046-06a3-4876-8dfd-474eb5e7ed11'
        
        try:
            # Make the request to Indeed
            response = requests.get(base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for i, card in enumerate(job_cards):
                if i >= limit:
                    break
                
                job = self._parse_indeed_job_card(card, base_url)
                if job:
                    jobs.append(job)
                
                # Add a small delay to avoid being blocked
                time.sleep(random.uniform(1, 3))
            
        except requests.RequestException as e:
            print(f"Error scraping Indeed: {e}")
        
        self.jobs = jobs
        return jobs

    def _parse_indeed_job_card(self, card, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse a job card from Indeed.

        Args:
            card: BeautifulSoup object representing a job card
            base_url: Base URL for constructing absolute URLs

        Returns:
            Dictionary containing job information or None if parsing failed
        """
        try:
            # Extract job title
            title_elem = card.find('h2', class_='jobTitle')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            # Extract company name
            company_elem = card.find('span', class_='companyName')
            company = company_elem.get_text().strip() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.get_text().strip() if location_elem else "Unknown Location"
            
            # Extract salary if available
            salary_elem = card.find('div', class_='salary-snippet')
            salary = salary_elem.get_text().strip() if salary_elem else "Not specified"
            
            # Extract job description snippet
            description_elem = card.find('div', class_='job-snippet')
            description = description_elem.get_text().strip() if description_elem else "No description available"
            
            # Extract job URL
            url_elem = title_elem.find('a') if title_elem else None
            url = urljoin(base_url, url_elem['href']) if url_elem and 'href' in url_elem.attrs else ""
            
            # Extract date posted
            date_elem = card.find('span', class_='date')
            date_posted = date_elem.get_text().strip() if date_elem else "Unknown date"
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "salary": salary,
                "date_posted": date_posted,
                "url": url,
                "source": "Indeed"
            }
            
        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def scrape_linkedin(self, keywords: str, location: str, remote: bool = False,
                        job_type: str = "F", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape job listings from LinkedIn.

        Args:
            keywords: Job keywords to search for
            location: Location to search in
            remote: If True, search for remote jobs
            job_type: Type of job (F=Full-time, P=Part-time, C=Contract, etc.)
            limit: Maximum number of jobs to scrape

        Returns:
            List of job listings as dictionaries
        """
        if self.use_sample_html:
            return self._parse_sample_linkedin_html()
        
        base_url = "https://www.linkedin.com/jobs/search"
        jobs = []
        
        # Format the query parameters
        params = {
            'keywords': keywords,
            'location': location,
            'f_JT': job_type,
        }
        
        if remote:
            params['f_WT'] = 'R'
        
        try:
            # Make the request to LinkedIn
            response = requests.get(base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings
            job_cards = soup.find_all('div', class_='base-card')
            
            for i, card in enumerate(job_cards):
                if i >= limit:
                    break
                
                job = self._parse_linkedin_job_card(card, base_url)
                if job:
                    jobs.append(job)
                
                # Add a small delay to avoid being blocked
                time.sleep(random.uniform(1, 3))
            
        except requests.RequestException as e:
            print(f"Error scraping LinkedIn: {e}")
        
        self.jobs.extend(jobs)
        return jobs

    def _parse_linkedin_job_card(self, card, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Parse a job card from LinkedIn.

        Args:
            card: BeautifulSoup object representing a job card
            base_url: Base URL for constructing absolute URLs

        Returns:
            Dictionary containing job information or None if parsing failed
        """
        try:
            # Extract job title
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            # Extract company name
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.get_text().strip() if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.get_text().strip() if location_elem else "Unknown Location"
            
            # Extract job URL
            url_elem = card.find('a', class_='base-card__full-link')
            url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
            
            # Extract date posted
            date_elem = card.find('time', class_='job-search-card__listdate')
            date_posted = date_elem['datetime'] if date_elem and 'datetime' in date_elem.attrs else "Unknown date"
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": date_posted,
                "url": url,
                "source": "LinkedIn"
            }
            
        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def _parse_sample_indeed_html(self) -> List[Dict[str, Any]]:
        """
        Parse sample Indeed HTML for testing purposes.

        Returns:
            List of job listings as dictionaries
        """
        # Sample job data
        sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "location": "New York, NY",
                "description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python and web development. The ideal candidate will have experience with Django, Flask, and RESTful APIs.",
                "salary": "$120,000 - $150,000 a year",
                "date_posted": "3 days ago",
                "url": "https://example.com/job/1",
                "source": "Indeed (Sample)"
            },
            {
                "title": "Data Scientist",
                "company": "Data Insights LLC",
                "location": "San Francisco, CA",
                "description": "Join our team of data scientists to analyze large datasets and build machine learning models. Requires experience with Python, pandas, scikit-learn, and TensorFlow.",
                "salary": "$130,000 - $160,000 a year",
                "date_posted": "1 day ago",
                "url": "https://example.com/job/2",
                "source": "Indeed (Sample)"
            },
            {
                "title": "Full Stack Developer",
                "company": "WebDev Co.",
                "location": "Remote",
                "description": "Looking for a Full Stack Developer with experience in React, Node.js, and MongoDB. Must be comfortable working in an agile environment.",
                "salary": "$100,000 - $130,000 a year",
                "date_posted": "Just posted",
                "url": "https://example.com/job/3",
                "source": "Indeed (Sample)"
            },
            {
                "title": "DevOps Engineer",
                "company": "Cloud Systems",
                "location": "Seattle, WA",
                "description": "Seeking a DevOps Engineer to manage our cloud infrastructure. Experience with AWS, Docker, Kubernetes, and CI/CD pipelines required.",
                "salary": "$125,000 - $155,000 a year",
                "date_posted": "2 days ago",
                "url": "https://example.com/job/4",
                "source": "Indeed (Sample)"
            },
            {
                "title": "Machine Learning Engineer",
                "company": "AI Innovations",
                "location": "Boston, MA",
                "description": "Join our team to develop cutting-edge machine learning models. Experience with deep learning frameworks and NLP is a plus.",
                "salary": "$140,000 - $170,000 a year",
                "date_posted": "5 days ago",
                "url": "https://example.com/job/5",
                "source": "Indeed (Sample)"
            }
        ]
        
        self.jobs = sample_jobs
        return sample_jobs

    def _parse_sample_linkedin_html(self) -> List[Dict[str, Any]]:
        """
        Parse sample LinkedIn HTML for testing purposes.

        Returns:
            List of job listings as dictionaries
        """
        # Sample job data
        sample_jobs = [
            {
                "title": "Backend Developer",
                "company": "Software Solutions",
                "location": "Austin, TX",
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": "2023-05-01",
                "url": "https://example.com/linkedin/job/1",
                "source": "LinkedIn (Sample)"
            },
            {
                "title": "Frontend Engineer",
                "company": "UI Experts",
                "location": "Chicago, IL",
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": "2023-05-02",
                "url": "https://example.com/linkedin/job/2",
                "source": "LinkedIn (Sample)"
            },
            {
                "title": "Data Engineer",
                "company": "Big Data Inc.",
                "location": "Remote",
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": "2023-04-30",
                "url": "https://example.com/linkedin/job/3",
                "source": "LinkedIn (Sample)"
            },
            {
                "title": "Product Manager",
                "company": "Product Innovations",
                "location": "Denver, CO",
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": "2023-05-03",
                "url": "https://example.com/linkedin/job/4",
                "source": "LinkedIn (Sample)"
            },
            {
                "title": "Cloud Architect",
                "company": "Cloud Solutions",
                "location": "Atlanta, GA",
                "description": "Click URL to view full description",
                "salary": "Not specified",
                "date_posted": "2023-04-28",
                "url": "https://example.com/linkedin/job/5",
                "source": "LinkedIn (Sample)"
            }
        ]
        
        self.jobs.extend(sample_jobs)
        return sample_jobs

    def get_full_job_description(self, job_url: str) -> str:
        """
        Get the full job description from a job URL.

        Args:
            job_url: URL of the job listing

        Returns:
            Full job description as a string
        """
        if self.use_sample_html:
            return "This is a sample job description. It would normally contain details about the job responsibilities, requirements, benefits, and company information."
        
        try:
            # Add a delay to avoid being blocked
            time.sleep(random.uniform(2, 5))
            
            # Make the request to the job URL
            response = requests.get(job_url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the job description (this will vary by site)
            if "indeed.com" in job_url:
                description_elem = soup.find('div', id='jobDescriptionText')
                return description_elem.get_text().strip() if description_elem else "Description not found"
            elif "linkedin.com" in job_url:
                description_elem = soup.find('div', class_='show-more-less-html__markup')
                return description_elem.get_text().strip() if description_elem else "Description not found"
            else:
                # Generic approach
                description_elem = soup.find('div', class_=['description', 'job-description', 'details'])
                return description_elem.get_text().strip() if description_elem else "Description not found"
            
        except requests.RequestException as e:
            print(f"Error getting job description: {e}")
            return "Error retrieving job description"

    def filter_jobs(self, keywords: List[str] = None, min_salary: int = None, 
                    locations: List[str] = None, remote_only: bool = False) -> List[Dict[str, Any]]:
        """
        Filter jobs based on criteria.

        Args:
            keywords: List of keywords to filter by
            min_salary: Minimum salary to filter by
            locations: List of locations to filter by
            remote_only: If True, only include remote jobs

        Returns:
            Filtered list of job listings
        """
        if not self.jobs:
            return []
        
        filtered_jobs = self.jobs.copy()
        
        # Filter by keywords
        if keywords:
            keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
            filtered_jobs = [
                job for job in filtered_jobs
                if any(re.search(keyword_pattern, job["title"], re.IGNORECASE) or
                       re.search(keyword_pattern, job["description"], re.IGNORECASE)
                       for keyword in keywords)
            ]
        
        # Filter by minimum salary
        if min_salary:
            # Extract salary numbers from the salary string
            filtered_jobs = [
                job for job in filtered_jobs
                if self._meets_min_salary(job["salary"], min_salary)
            ]
        
        # Filter by locations
        if locations:
            filtered_jobs = [
                job for job in filtered_jobs
                if any(location.lower() in job["location"].lower() for location in locations)
            ]
        
        # Filter by remote only
        if remote_only:
            filtered_jobs = [
                job for job in filtered_jobs
                if "remote" in job["location"].lower()
            ]
        
        return filtered_jobs

    def _meets_min_salary(self, salary_str: str, min_salary: int) -> bool:
        """
        Check if a salary string meets the minimum salary requirement.

        Args:
            salary_str: Salary string to check
            min_salary: Minimum salary to compare against

        Returns:
            True if the salary meets the minimum, False otherwise
        """
        if "not specified" in salary_str.lower():
            return False
        
        # Extract numbers from the salary string
        numbers = re.findall(r'\d+[,\d]*', salary_str)
        if not numbers:
            return False
        
        # Convert to integers
        salary_numbers = [int(num.replace(',', '')) for num in numbers]
        
        # Check if any of the numbers meet the minimum salary
        return any(num >= min_salary for num in salary_numbers)

    def save_to_json(self, output_path: str) -> None:
        """
        Save the scraped jobs to a JSON file.

        Args:
            output_path: Path where the JSON file will be saved
        """
        if not self.jobs:
            raise ValueError("No jobs available. Run scrape_indeed() or scrape_linkedin() first.")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2)
            
        print(f"Jobs data saved to {output_path}")


# Example usage
if __name__ == "__main__":
    scraper = JobScraper(use_sample_html=True)
    jobs = scraper.scrape_indeed("python developer", "New York", remote=True)
    # Filter jobs
    filtered_jobs = scraper.filter_jobs(keywords=["python", "django"], remote_only=True)
    # Save to JSON
    scraper.save_to_json("jobs.json")
