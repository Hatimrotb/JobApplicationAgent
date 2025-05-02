# JobApplicationAgent

A comprehensive Python application that automates the job application process based on a resume and user preferences.

## 📋 Overview

JobApplicationAgent is a modular tool designed to streamline your job search by:

1. Parsing your resume to extract key information
2. Scraping job listings from popular job boards
3. Matching your skills and experience with job requirements
4. Generating personalized cover letters using AI
5. Tracking your job applications

## 🔧 Features

- **Resume Parser**: Extract structured data from PDF or DOCX resumes
- **Job Scraper**: Find relevant job listings from Indeed and LinkedIn
- **Job Matching Engine**: Rank jobs based on relevance to your profile
- **Cover Letter Generator**: Create tailored cover letters using Google's Gemini API
- **Application Simulator**: Track your job applications and their status
- **Command-Line Interface**: Easy-to-use CLI for all functionality

## 📁 Project Structure

```
JobApplicationAgent/
├── main.py                 # Main entry point
├── resume_parser/          # Resume parsing module
│   └── parser.py
├── job_scraper/            # Job scraping module
│   └── scraper.py
├── matcher/                # Job matching module
│   └── matcher.py
├── cover_letter/           # Cover letter generation module
│   └── generator.py
├── simulator/              # Application simulation module
│   └── applier.py
├── cli/                    # Command-line interface
│   └── cli.py
├── utils/                  # Utility functions
│   └── helpers.py
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/JobApplicationAgent.git
   cd JobApplicationAgent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy model (if not automatically installed):
   ```bash
   python -m spacy download en_core_web_sm
   ```

## 🔑 API Keys

To use the cover letter generator with Google's Gemini API:

1. Get an API key from [Google AI Studio](https://ai.google.dev/)
2. Set it as an environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key"  # On Windows: set GEMINI_API_KEY="your-api-key"
   ```

## 💻 Usage

### Command-Line Interface

The application provides a comprehensive CLI:

```bash
# Parse a resume
python -m JobApplicationAgent.cli.cli upload-resume path/to/resume.pdf

# Scrape job listings
python -m JobApplicationAgent.cli.cli scrape-jobs --keywords "python developer" --location "New York" --remote

# Match resume to job listings
python -m JobApplicationAgent.cli.cli match-jobs --min-score 70

# List matched jobs
python -m JobApplicationAgent.cli.cli list-jobs --matched

# Generate a cover letter
python -m JobApplicationAgent.cli.cli generate-cover-letter --job-id JOB-0001 --tone formal

# Simulate applying to a job
python -m JobApplicationAgent.cli.cli apply --job-id JOB-0001 --cover-letter path/to/cover_letter.txt

# Show application status
python -m JobApplicationAgent.cli.cli status
```

### Python API

You can also use the application programmatically:

```python
from JobApplicationAgent.main import JobApplicationAgent

# Initialize the agent
agent = JobApplicationAgent()

# Parse a resume
resume_data = agent.parse_resume("path/to/resume.pdf")

# Scrape job listings
jobs = agent.scrape_jobs(
    keywords="python developer",
    location="New York",
    remote=True,
    use_sample=True  # Use sample data for testing
)

# Match jobs
matched_jobs = agent.match_jobs(min_score=70.0)

# Generate a cover letter
cover_letter = agent.generate_cover_letter(
    job_id="JOB-0001",
    tone="formal"
)

# Apply to a job
application = agent.apply_to_job(
    job_id="JOB-0001",
    cover_letter_path="path/to/cover_letter.txt"
)

# Get application statistics
stats = agent.get_application_statistics()
```

## 📊 Job Matching

The job matching engine uses two approaches:

1. **TF-IDF Vectorization**: Compares the text similarity between your resume and job descriptions
2. **BERT Sentence Embeddings**: Uses advanced NLP to understand semantic meaning (when available)

The matcher calculates separate scores for:
- Skills match
- Experience match
- Education match
- Overall semantic match

## 📝 Cover Letter Generation

The cover letter generator uses Google's Gemini API to create personalized cover letters based on:
- Your resume information
- The job description
- Your preferred tone (formal, conversational, enthusiastic)

If no API key is available, it will generate a sample cover letter template.

## 📈 Application Tracking

The application simulator tracks:
- Jobs you've applied to
- Application status (Applied, Skipped, Rejected, Interview, Offer, Accepted)
- Application dates
- Notes and follow-ups

## 🔍 Sample Data

For testing purposes, the job scraper includes sample job listings that can be used without making actual web requests.

## 🛠️ Future Enhancements

- **Web UI**: Add a Streamlit-based web interface
- **Automated Applications**: Implement actual job application submission via Selenium/Playwright
- **Interview Preparation**: Generate potential interview questions based on job descriptions
- **Networking Suggestions**: Identify potential networking connections for target companies
- **Resume Optimization**: Suggest resume improvements based on job requirements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

For questions or feedback, please open an issue on GitHub or contact the maintainer.
