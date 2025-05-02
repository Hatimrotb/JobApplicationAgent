"""
Utility Functions Module

This module provides helper functions used across the JobApplicationAgent application.
"""

import os
import json
import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


# Set up logging
def setup_logging(log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_file: Path to the log file. If None, logs will only be printed to console.
        level: Logging level (e.g., logging.INFO, logging.DEBUG)

    Returns:
        Configured logger
    """
    logger = logging.getLogger("JobApplicationAgent")
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# File operations
def save_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    Save data to a JSON file.

    Args:
        data: Data to save
        file_path: Path where the JSON file will be saved
        indent: Indentation level for the JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        return False


def load_json(file_path: str) -> Optional[Any]:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Loaded data or None if file doesn't exist or is invalid
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        return None


# Text processing
def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and extra whitespace.

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


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Text to extract keywords from
        min_length: Minimum length of keywords to extract

    Returns:
        List of keywords
    """
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Split into words
    words = cleaned_text.split()
    
    # Filter words by length
    keywords = [word for word in words if len(word) >= min_length]
    
    # Remove duplicates and sort
    return sorted(list(set(keywords)))


# Date and time
def format_date(date_str: str, input_format: str, output_format: str) -> str:
    """
    Format a date string.

    Args:
        date_str: Date string to format
        input_format: Input date format (e.g., '%Y-%m-%d')
        output_format: Output date format (e.g., '%B %d, %Y')

    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception as e:
        logging.error(f"Error formatting date {date_str}: {e}")
        return date_str


def get_current_date(format_str: str = '%Y-%m-%d') -> str:
    """
    Get the current date.

    Args:
        format_str: Date format string

    Returns:
        Current date as a string
    """
    return datetime.now().strftime(format_str)


# API key management
def get_api_key(key_name: str, env_var: str = None, config_file: str = None) -> Optional[str]:
    """
    Get an API key from environment variables or a config file.

    Args:
        key_name: Name of the API key
        env_var: Environment variable name to check
        config_file: Path to the config file

    Returns:
        API key or None if not found
    """
    # Check environment variable
    if env_var and env_var in os.environ:
        return os.environ[env_var]
    
    # Check config file
    if config_file and os.path.exists(config_file):
        config = load_json(config_file)
        if config and key_name in config:
            return config[key_name]
    
    return None


# URL operations
def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.

    Args:
        url: URL to check

    Returns:
        True if the URL is valid, False otherwise
    """
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http://, https://, ftp://, ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding the http:// prefix if missing.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    if not url.startswith(('http://', 'https://')):
        return f"https://{url}"
    
    return url


# Data validation
def validate_resume_data(resume_data: Dict[str, Any]) -> bool:
    """
    Validate resume data.

    Args:
        resume_data: Resume data to validate

    Returns:
        True if the resume data is valid, False otherwise
    """
    required_fields = ['contact_info', 'skills', 'experience', 'education']
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in resume_data:
            logging.error(f"Missing required field in resume data: {field}")
            return False
    
    # Check contact info
    contact_info = resume_data.get('contact_info', {})
    if not contact_info.get('name'):
        logging.error("Missing name in contact info")
        return False
    
    # Check if there are skills
    if not resume_data.get('skills'):
        logging.warning("No skills found in resume data")
    
    # Check if there is experience
    if not resume_data.get('experience'):
        logging.warning("No experience found in resume data")
    
    # Check if there is education
    if not resume_data.get('education'):
        logging.warning("No education found in resume data")
    
    return True


def validate_job_data(job_data: Dict[str, Any]) -> bool:
    """
    Validate job data.

    Args:
        job_data: Job data to validate

    Returns:
        True if the job data is valid, False otherwise
    """
    required_fields = ['title', 'company', 'description']
    
    # Check if all required fields are present
    for field in required_fields:
        if field not in job_data:
            logging.error(f"Missing required field in job data: {field}")
            return False
    
    # Check if title is not empty
    if not job_data.get('title'):
        logging.error("Empty title in job data")
        return False
    
    # Check if company is not empty
    if not job_data.get('company'):
        logging.error("Empty company in job data")
        return False
    
    # Check if description is not empty
    if not job_data.get('description'):
        logging.error("Empty description in job data")
        return False
    
    return True


# Example usage
if __name__ == "__main__":
    # Set up logging
    logger = setup_logging()
    
    # Example usage of helper functions
    logger.info("Testing helper functions")
    
    # Test clean_text
    text = "This is a test! With some special characters: @#$%^&*()"
    cleaned_text = clean_text(text)
    logger.info(f"Original text: {text}")
    logger.info(f"Cleaned text: {cleaned_text}")
    
    # Test extract_keywords
    keywords = extract_keywords(text)
    logger.info(f"Keywords: {keywords}")
    
    # Test get_current_date
    current_date = get_current_date()
    logger.info(f"Current date: {current_date}")
    
    # Test is_valid_url
    url = "https://example.com"
    logger.info(f"Is {url} valid? {is_valid_url(url)}")
    
    # Test normalize_url
    url = "example.com"
    normalized_url = normalize_url(url)
    logger.info(f"Original URL: {url}")
    logger.info(f"Normalized URL: {normalized_url}")
