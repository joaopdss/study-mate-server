import datetime
"""
Utility module for building prompts for AI services (LLM, search).
"""
from typing import List

def build_exam_search_prompt(exam_title: str, exam_country: str, topics: List[str], educational_level: str = "", materials_content: str = ""):
    """
    Builds a search prompt for the exam information.
    
    Args:
        exam_title (str): The title of the exam
        exam_country (str): The country where the exam is held
        topics (List[str]): List of topics to be covered
        educational_level (str, optional): Educational level of the exam
        materials_content (str, optional): Text extracted from exam materials
    Returns:
        str: A formatted search prompt
    """
    prompt = f"Find official or widely recognized information about the {exam_title} in {exam_country}"
    prompt += f" for {educational_level} students"
    prompt += ".\nInclude important details such as exam format, recommended topics, common resources, sample questions, and any official guidelines."
    prompt += f"\nThe exam covers the following topics: {topics}."
    prompt += "\nReturn the most relevant, accurate, and up-to-date sources."
    prompt += "\nMake sure to include sample of at least 10 real questions from the exam."
    
    
    if materials_content:
        prompt += f"\n\nAlso consider the following content from the user's exam materials:\n{materials_content}"
        
    return prompt

def build_study_plan_prompt(exam, search_results=None, materials_content=None):
    """
    Builds a study plan generation prompt for the LLM.
    
    Args:
        exam (Exam): The exam object containing necessary details
        search_results (str, optional): Additional context from search API
        materials_content (str, optional): Text extracted from exam materials
        
    Returns:
        str: A formatted prompt for the LLM to generate a study plan
    """

    system_prompt = """You are a helpful assistant. The user will provide a text prompt. Follow these instructions:

    1. Parse the user's input based on the required structure.
    2. Output the result strictly in JSON format (no additional text before or after the JSON).

    ---

    Simple Example

    EXAMPLE INPUT (for demonstration purposes):
    Which is the highest mountain in the world? Mount Everest.

    EXAMPLE JSON OUTPUT (for demonstration purposes):
    {
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
    }

    ---

    Real Prompt to Handle

    The user's real prompt will be something like:
    Create a daily study plan for {exam.title} in {exam.country}.
    The exam is on {exam.exam_date}, today is {today_date}. User's goal score: {exam.goal_score}.
    Proficiency level: {exam.proficiency}.
    Topics to study: {topics_str}.
    The user can study {exam.hours_per_day} hours per day on the following days: {exam.study_schedule}.

    Please provide a structured plan for each day until the exam date. 
    Each day should include specific topics, recommended resources, and time estimates.
    The response should be structured as follows:

    1. A brief overview of the study plan
    2. For each day:
    - Day number
    - Topics for the day
    - Specific subtopics
    - Resource recommendations (books, online courses, practice problems)
    - Estimated hours needed

    ---

    Desired JSON Structure

    Your response must follow this JSON structure (adapt as needed, but keep JSON validity and hierarchy intact):

    {
    "overview": "<brief overview of the study plan>",
    "day_topics": [
        {
        "day_num": 1,
        "topics_for_the_day": "<list or description of topics>",
        "subtopics": "<details on subtopics>",
        "resources": "<recommended resources>",
        "estimated_hours_needed": "<number or range of hours>"
        },
        {
        "day_num": 2,
        "topics_for_the_day": "...",
        "subtopics": "...",
        "resources": "...",
        "estimated_hours_needed": "..."
        }
        // Repeat for as many days as needed
    ]
    }

    Important:
    - Do not include any additional text, explanations, or markdown formatting outside of the JSON.
    - The final answer should be valid JSON only."""

    
    user_prompt = f"""Create a daily study plan for {exam.title} in {exam.country}.
    The exam is on {exam.exam_date}. Today is {datetime.datetime.now().strftime('%Y-%m-%d')}. User's goal score: {exam.goal_score}.
    Proficiency level: {exam.proficiency}.
    Topics to study: {exam.topics}.
    The user can study {exam.hours_per_day} hours per day on the following days: {exam.study_schedule}.

    Please provide a structured plan for each day until the exam date.
    Each day should include specific topics, recommended resources, and time estimates.
    The response should be structured as follows:

    1. A brief overview of the study plan
    2. For each day:
    - Day number
    - Topics for the day
    - Specific subtopics
    - Resource recommendations (books, online courses, practice problems)
    - Estimated hours needed"""
    

    if materials_content:
        user_prompt += f"\n\nUse the following official or known details about this exam:\n{materials_content}"
    
    return system_prompt, user_prompt

def build_quiz_prompt(quiz_request, exam, search_results=None, materials_content=None):
    """
    Builds a quiz generation prompt for the LLM.
    
    Args:
        quiz_request (dict): Quiz generation parameters
        exam (Exam): The exam object for context
        search_results (str, optional): Additional context from search API
        materials_content (str, optional): Text extracted from exam materials
        
    Returns:
        str: A formatted prompt for the LLM to generate a quiz
    """
    topics_str = ", ".join(quiz_request.get("topics_of_the_day", []))
    
    prompt = f"""
    Generate {quiz_request.get("num_questions", 10)} multiple-choice questions at a {quiz_request.get("difficulty", "Medium")} 
    difficulty level on the following topics: {topics_str}.
    
    The questions should be related to {exam.title} in {exam.country}. The user's proficiency level is {exam.proficiency}.
    
    Each question should include:
    1. The question text
    2. Four options (A, B, C, D)
    3. The correct answer (indicated by the letter)
    4. A brief explanation of why the answer is correct
    5. The specific topic it belongs to
    
    Format the response as a JSON array of objects, where each object represents a question with the following properties:
    - question_text: string
    - options: array of strings (4 options)
    - correct_answer: string (the letter of the correct answer)
    - explanation: string
    - topic: string
    - difficulty: string
    """
    
    if search_results:
        prompt += f"\n\nIncorporate information from these example questions or typical exam content:\n{search_results}"
    
    if materials_content:
        prompt += f"\n\nBase some questions on the following content from the user's study materials:\n{materials_content}"
    
    return prompt 