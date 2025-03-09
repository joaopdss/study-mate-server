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
    3. For each "description" field in the output:
        - Provide at least four (4) paragraphs of explanatory text.
        - Make it as detailed and in-depth as possible, as if writing a condensed textbook section or academic mini-lesson.
        - Include real-world examples, conceptual explanations, and clarifications in a didactic style.
        - Avoid simply listing tasks or instructions; focus on teaching and elucidating concepts.
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
    - Description (an extensive, multi-paragraph, didactic text)
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
        "description": "<at least four paragraphs of deeply explanatory text—like a mini-textbook chapter>",
        "resources": "<recommended resources>",
        "estimated_hours_needed": "<number or range of hours>"
        },
        {
        "day_num": 2,
        "topics_for_the_day": "...",
        "subtopics": "...",
        "description": "...",
        "resources": "...",
        "estimated_hours_needed": "...",
        }
        // Repeat for as many days as needed
    ]
    }

    
    ### Example JSON Output (Illustrative)

    Below is an **illustrative example** to show the level of detail we expect in the `"description"` field. **Do not** include any extra text outside of the JSON in your final answer.
    
    {
        "overview": "This plan will guide you through key aspects of reading comprehension step by step, ensuring a deep understanding of passage structures, question types, and strategies for effective reading in an exam context.",
        "day_topics": [
            {
            "day_num": 1,
            "topics_for_the_day": "Reading Comprehension Basics",
            "subtopics": "Identifying passage structures, Main ideas, Basic question types (Factual Information, Vocabulary)",
            "description": "Reading comprehension relies on understanding how authors structure their arguments and present information. At its simplest level, each passage has a main idea—a core concept that the writer wants to convey. These key ideas often appear at the beginning or end of a paragraph, but they can also be woven subtly throughout the text. By paying attention to transitional phrases such as 'in contrast,' 'moreover,' or 'for example,' you can follow the logical flow of the argument from one point to the next.\n\nWhen analyzing paragraph structures, it helps to see each paragraph as a building block. The first paragraph might introduce the overall topic, while subsequent paragraphs provide evidence, examples, or counterarguments. For instance, if you’re reading an article about the environmental impact of deforestation, the second paragraph might focus on the economic reasons behind logging, and the third might explore the ecological consequences. Understanding this structure makes it easier to piece together the author's main argument and critique its strengths or weaknesses.\n\nAnother fundamental aspect of reading comprehension is vocabulary in context. Instead of treating unfamiliar words in isolation, examine how they function in the sentence or paragraph around them. Authors often give hints about a word’s meaning by rephrasing an idea or by providing examples that clarify how a concept works. For example, if you encounter the term 'photosynthesis' and the paragraph also references the way plants convert sunlight into chemical energy, you can deduce the term’s meaning even if you’ve never seen it before.\n\nEqually important is recognizing your own background knowledge. If you’ve read widely on environmental topics, you might already be familiar with certain key terms or debates. Leveraging this prior understanding allows you to make more nuanced connections between ideas. The ultimate goal of Day 1 is to ground you in the basics: identifying main ideas, discerning paragraph organization, and decoding unfamiliar vocabulary without losing the flow of the passage.",
            "resources": "The Official Guide to the TOEFL Test, Reading practice websites",
            "estimated_hours_needed": 2
            },
            {
            "day_num": 2,
            "topics_for_the_day": "Refining Inference Skills",
            "subtopics": "Logical conclusions, Author’s assumptions, Evaluating evidence",
            "description": "Once you've mastered the fundamentals of mapping out main ideas and following logical structures, the next step is to develop stronger inferential and analytical skills. Inference involves reading between the lines, connecting details that may not be explicitly stated but are implied by the overall context. For instance, if an author consistently highlights negative aspects of deforestation while downplaying any economic benefits, you can infer that the writer likely has an environmental advocacy perspective.\n\nEvaluating author bias is closely tied to these inferential skills. Writers often frame their arguments using particular word choices or examples that reflect their subjective viewpoints. Phrases like 'it is undeniable' or 'obviously' can be markers of bias, since they assume no room exists for contrary opinions. By noting such language, you develop a critical lens, allowing you to weigh the legitimacy of the evidence presented. If a piece on deforestation overlooks the concerns of local communities who rely on logging, you might question whether the author is providing a fully balanced view.\n\nAnother layer of advanced reading involves understanding rhetorical strategies—techniques writers use to persuade or inform their audience. An author may use anecdotal evidence to create an emotional appeal, or they might reference authoritative sources to establish credibility (an appeal to ethos). Spotting these strategies will sharpen your ability to judge the passage’s persuasiveness and logic. For example, if a text about environmental policy cites a study from an internationally respected scientific journal, it likely bolsters the article’s credibility, whereas reliance on unverified data can diminish its overall impact.\n\nUltimately, inferential and analytical reading forms the bridge between basic comprehension and critical thinking. By delving deeper into implied meanings, identifying bias, and recognizing rhetorical devices, you gain a more holistic understanding of the text. This skill set is invaluable not only for standardized exams but also for navigating the vast array of articles, reports, and essays encountered in academic and professional life.",
            "resources": "Practice passages from official test-prep materials, Academic reading journals",
            "estimated_hours_needed": 2    
            }
        ]
    }

    Important:

    - Produce only the JSON in the final answer—no explanations, markdown, or additional text before/after it.
    - Each "description" must be long-form and explanatory, with at least four paragraphs or more.
    """

    
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
    - Description (an extensive text that **explains** the day’s topic in a didactic, educational way, as if it were a short textbook or mini-lesson. It should focus on clarifying concepts, providing background, giving examples, and offering insights. **Avoid** listing tasks or instructions to do.)
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