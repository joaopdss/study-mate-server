"""
Service for interacting with OpenAI or other LLM APIs.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List, Union
from openai import OpenAI

# Load API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = "https://api.openai.com/v1"

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7, model: str = "o3-mini") -> Optional[str]:
    """
    Makes a call to the OpenAI API.
    
    Args:
        prompt (str): The prompt to send to the model
        temperature (float): Controls randomness (0-1)
        model (str): The model to use
        
    Returns:
        str: The model's response or None if the call failed
    """
    try:
        print(f"Calling LLM with model: {model}")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            reasoning_effort="low"
        )
        
        print(f"Response obtained")
        return response.choices[0].message.content  

    except Exception as e:
        print(f"Error in call_llm: {str(e)}")
        return None

def generate_study_plan(system_prompt: str, user_prompt: str):
    """
    Generates a study plan using the LLM and parses the response.
    
    Args:
        prompt (str): The prompt for generating the study plan
        
    Returns:
        dict: Parsed study plan data or None if generation failed
    """
    response = call_llm(system_prompt, user_prompt)
    if not response:
        return None
    
    try:
        # The response should be formatted text that we need to parse
        # Extract overall plan summary and day-by-day breakdown
        
        # Simple parsing for demonstration - in production, use more robust parsing
        return response
    
    except Exception as e:
        print(f"Error parsing study plan: {str(e)}")
        return None

def parse_day_section(section_lines: List[str]) -> Optional[Dict[str, Any]]:
    """
    Parses a section of text for a single day of the study plan.
    
    Args:
        section_lines (list): Lines of text for a day section
        
    Returns:
        dict: Parsed day information or None if parsing failed
    """
    try:
        if not section_lines:
            return None
        
        # First line should have the day number
        day_title = section_lines[0].strip()
        day_number = extract_day_number(day_title)
        
        topics = []
        resources = []
        estimated_hours = 0
        
        # Look for topics and resources in the remaining lines
        in_topics = False
        in_resources = False
        for line in section_lines[1:]:
            line = line.strip()
            
            # Try to find topics section
            if "topic" in line.lower() and ":" in line:
                in_topics = True
                in_resources = False
                continue
                
            # Try to find resources section
            if "resource" in line.lower() and ":" in line:
                in_topics = False
                in_resources = True
                continue
                
            # Try to find estimated hours
            if "hour" in line.lower() and ":" in line:
                try:
                    hours_text = line.split(":")[1].strip()
                    # Extract the first number found
                    import re
                    hours_match = re.search(r'\d+(\.\d+)?', hours_text)
                    if hours_match:
                        estimated_hours = float(hours_match.group())
                except:
                    pass
                    
            # Add to the appropriate section
            if in_topics and line and not line.endswith(":"):
                topics.append(line)
            elif in_resources and line and not line.endswith(":"):
                resources.append(line)
        
        # Create resource objects from the text
        resource_objects = []
        for res in resources:
            resource_objects.append({
                "description": res,
                "url": "",  # We'd need more sophisticated parsing to extract URLs
                "type": "text"  # Default type
            })
        
        return {
            "day_number": day_number,
            "planned_topics": topics,
            "resources": resource_objects,
            "estimated_hours": estimated_hours
        }
    
    except Exception as e:
        print(f"Error parsing day section: {str(e)}")
        return None

def extract_day_number(day_title: str) -> int:
    """
    Extracts the day number from a day title string.
    
    Args:
        day_title (str): The day title (e.g., "Day 1: Introduction")
        
    Returns:
        int: The day number or 0 if extraction failed
    """
    try:
        import re
        match = re.search(r'Day\s+(\d+)', day_title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    except:
        return 0

def generate_quiz(system_prompt: str, prompt: str) -> Optional[List[Dict[str, Any]]]:
    """
    Generates a quiz using the LLM and parses the response.
    
    Args:
        prompt (str): The prompt for generating the quiz
        
    Returns:
        list: List of question objects or None if generation failed
    """
    response = call_llm(system_prompt, prompt)
    
    return response
    

def parse_quiz_text(text: str) -> List[Dict[str, Any]]:
    """
    Fallback parser for quiz text when JSON parsing fails.
    
    Args:
        text (str): The raw text from the LLM
        
    Returns:
        list: List of question objects
    """
    questions = []
    current_question = None
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check if this is a new question
        if re.match(r'^(\d+\.|\*|Q\d+:|Question \d+:)', line):
            # Save the previous question if it exists
            if current_question:
                questions.append(current_question)
                
            # Start a new question
            current_question = {
                "question_text": line,
                "options": [],
                "correct_answer": "",
                "explanation": "",
                "topic": "",
                "difficulty": "Medium"  # Default difficulty
            }
        elif current_question:
            # Check if this is an option
            option_match = re.match(r'^([A-D])\.?\s+(.+)$', line)
            if option_match:
                option_letter, option_text = option_match.groups()
                current_question["options"].append(f"{option_letter}. {option_text}")
                
            # Check if this indicates the correct answer
            elif "correct" in line.lower() and "answer" in line.lower():
                answer_match = re.search(r'([A-D])', line)
                if answer_match:
                    current_question["correct_answer"] = answer_match.group(1)
                    
            # Check if this is the explanation
            elif "explanation" in line.lower() and ":" in line:
                current_question["explanation"] = line.split(":", 1)[1].strip()
                
            # Check if this is the topic
            elif "topic" in line.lower() and ":" in line:
                current_question["topic"] = line.split(":", 1)[1].strip()
    
    # Add the last question if it exists
    if current_question:
        questions.append(current_question)
        
    return questions 