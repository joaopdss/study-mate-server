"""
Service for interacting with Perplexity or other search APIs.
"""
import os
import requests
import json
from typing import Dict, Any, Optional, List, Union

# Load API key from environment variables
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Simple cache to avoid repeated searches
search_cache = {}

def search_exam_info(
    exam_title: str, 
    exam_country: str, 
    topics: List[str],
    educational_level: str = "",
    materials_content: str = ""
) -> Optional[str]:
    """
    Searches for information about an exam using Perplexity API.
    
    Args:
        exam_title (str): The title of the exam
        exam_country (str): The country where the exam is held
        topics (List[str]): List of topics covered in the exam
        educational_level (str, optional): Educational level of the exam
        materials_content (str, optional): Text extracted from exam materials
        
    Returns:
        str: Search results or None if the search failed
    """
    
    # Prepare search query
    from app.utils.ai_prompt_builder import build_exam_search_prompt
    query = build_exam_search_prompt(exam_title, exam_country, topics, educational_level, materials_content)
    
    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Include materials content in the system prompt if available
        system_content = "You are a helpful assistant that provides information about exams, their structure, and syllabus."
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user", 
                    "content": query
                }
            ]
        }
        
        response = requests.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return content
        else:
            print(f"Perplexity API error: {response.status_code}, {response.text}")
            return None
    
    except Exception as e:
        print(f"Error in search_exam_info: {str(e)}")
        return None 