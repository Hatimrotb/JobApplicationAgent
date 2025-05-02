# JobApplicationAgent

A comprehensive web application that automates the job application process based on a resume and user preferences.

## 🚀 Features

- **Resume Parser**: Extract structured data from PDF or DOCX resumes
- **Job Scraper**: Find relevant job listings from job boards
- **Job Matching Engine**: Rank jobs based on relevance to your profile
- **Cover Letter Generator**: Create tailored cover letters using AI
- **Application Tracker**: Track your job applications and their status

## 📋 Requirements

- Python 3.8+
- Streamlit
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. Clone this repository:
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

4. Set up your API key:
   - Create a `.env` file in the root directory
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

## 🖥️ Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Or with Python module syntax:
```bash
python -m streamlit run app.py
```

Then open your browser and go to http://localhost:8501

## 📱 Deployment Options

### Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add your API key as a secret
5. Deploy the app

### Heroku

1. Create a `Procfile` with: `web: streamlit run app.py --server.port $PORT`
2. Push to Heroku: `git push heroku main`
3. Set environment variables: `heroku config:set GEMINI_API_KEY=your_api_key_here`

## 🔒 Security Notes

- Never commit your API keys to GitHub
- Use environment variables for sensitive information
- The `.env` file is included in `.gitignore` to prevent accidental commits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Created by Hatim
