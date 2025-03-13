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
        system_content = """You are a knowledgeable assistant specializing in standardized exams. Your primary task is to provide accurate and up-to-date information about the specified exam. This includes:

        1. **Overview & Purpose of the Exam**:
        - Summarize what the exam is for, who typically takes it, and what skills or knowledge it evaluates.

        2. **Exam Structure**:
        - List sections or components (e.g., Reading, Listening, Writing, etc.).
        - For each section, note duration, number of tasks/questions, and general topics or skills tested.
        - Include any relevant format details, such as computer-based versus paper-based, adaptive testing, etc.

        3. **Preparation Guidelines**:
        - Provide recommended study resources (e.g., official guides, reputable third-party materials).
        - Suggest strategies (e.g., time management, practice tests).
        - Mention official or recognized websites for more information.

        4. **Official Rules & Guidelines**:
        - Registration processes, fees, and locations.
        - Permitted materials or devices, security measures.
        - Scoring details (ranges, passing criteria, score validity).

        5. **Sample Questions** (at least 20 multiple-choice):
        - Questions should be illustrative of the exam’s real style and difficulty.
        - **Passages or Scenarios**: If the exam assesses reading comprehension or scenario-based reasoning (e.g., TOEFL Reading, AWS certification scenarios), include a short text passage (1–3 paragraphs) or scenario from which the question is derived.
        - If no passage is needed for a particular question type (e.g., simple math), simply omit or leave the passage blank.
        - Ensure any official or copyrighted questions are paraphrased in your own words unless they are in the public domain or provided under fair use. Cite sources or link to official materials if referencing them directly.

        6. **Presentation & Clarity**:
        - Use headings, subheadings, bullet points, and tables to structure the information clearly.
        - Write in a concise, reader-friendly style without sacrificing detail or accuracy.
        - If referencing websites or third-party resources, ensure they are credible and relevant.

        7. **Accuracy & Completeness**:
        - Always verify information against reputable or official sources.
        - If uncertain, provide a disclaimer or guide the user to official channels for final confirmation.

        Your goal is to create a thorough, easy-to-understand guide about the exam, including a selection of sample questions (with short passages or scenarios if required by the exam’s nature). Avoid extraneous commentary and ensure the user can rely on your responses to prepare effectively."""
        
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