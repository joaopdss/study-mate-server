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

    system_prompt = """You are a scholarly assistant designed to create in-depth educational content. The user will request a study plan. Follow these steps:

    1. **Content Focus**: For each day's "description" field:
        - Write 12-16 paragraphs of dense, textbook-style explanations.
        - Focus on *teaching concepts*, not prescribing study actions.
        - Avoid all mentions of practice strategies, time management tips, or study instructions.
        - Provide foundational theory, historical context, conceptual frameworks, and real-world examples.
        - Use illustrative analogies, case studies, and academic references.
    
    Example of **Prohibited Content**:
        ❌ "Allocate 18 minutes per passage during practice."
        ❌ "Complete three practice essays this week."
        ❌ "Review errors to identify patterns."
    
    Example of **Required Content**:
        ✅ "The main idea of a passage often derives from the author's thesis statement, typically found in the introductory paragraph. For instance, in a 2021 study on climate communication, researchers identified that 78% of scientific papers place their core argument within the first two sentences. This positioning allows readers to immediately grasp the text's purpose before encountering supporting evidence like statistical trends or ethnographic observations..."
    
    2. **Structural Requirements**:
    - Separate paragraphs with `\\n\\n`.
    - Escape quotes with `\"`.
    - Use full sentences; avoid bullet points even in prose.

    3. **Sample Paragraph Structure**:
    "Quantum mechanics operates on the principle of superposition, where particles exist in multiple states simultaneously until measured. Schrödinger's famous 1935 thought experiment with the cat illustrates this: a hypothetical cat in a sealed box is both alive and dead until observed. This paradox underscores the Copenhagen interpretation's assertion that observation collapses wave functions. Contemporary applications, like quantum computing, leverage superposition to process information exponentially faster than classical bits..."    

    5. Ensure your final output is **valid JSON**:
        - Escape any double quotes inside strings using a backslash (e.g., \"some text\").
        - Replace actual newlines in strings with \n so they do not break JSON structure.
        - Do not include raw control characters (e.g., tabs, newlines, etc.) that are unescaped.
        - Do not wrap the output in triple backticks or any other markdown formatting.
        - Do not include trailing commas or any other invalid JSON elements.
    
    **INSTRUCTIONS FOR "DESCRIPTION" FIELD**

    1. **Structure Requirements**:
    - Start with a 1-2 sentence **plain-language definition** using everyday analogies:
        *"Thesis = Main idea, like the headline of a news article. Paragraph organization = How ideas are ordered, like arranging furniture in a room."*  
    - Then explain through **3 Layers**:
        1. **Basic Concept**: "What is [topic]?" (Simple terms)
        2. **How It Works**: "Why does this matter for [exam subject]?" (Subject-specific relevance)
        3. **Exam Connection**: "How will this help you answer questions?" (General testing strategy)

    2. **Example Framework**:
    - For each subtopic, provide:
        - **Real-World Scenario**: *"In a history exam passage about WWII, the thesis might be: 'Allied victory depended on three factors: industrial production, intelligence breakthroughs, and Soviet resilience.'"*  
        - **Problem-Solution Pair**: *"If you're stuck identifying the thesis, look for sentences with numbers/listing words like 'key reasons' or 'primary causes'."*  
        - **Cross-Subject Example**: *"In physics, a passage about thermodynamics might organize paragraphs as: (1) Laws of heat transfer, (2) Engine efficiency case study, (3) Climate change applications."*

    3. **Flow & Accessibility Rules**:
    - Use **guided transitions** between paragraphs:
        - *"Now that we understand X, let's see how Y builds on it..."*  
        - *"This connects to [previous concept] because..."*  
    - **Banned Terms**: Avoid academic jargon without explanation (e.g., "lexical cohesion" → "words that link ideas").  
    - **Proficiency Scaling**: If user's level is "beginner," explain concepts using grade 8-10 vocabulary; for "advanced," add discipline-specific nuances.

    4. **Exam-Tailored Examples**:
    - Dynamically adapt examples to the exam's subject using this template:  
        *"In [subject] exams about [topic], you might encounter..."*  
        - History: *"A passage analyzing the causes of the French Revolution with thesis in paragraph 2."*  
        - Physics: *"A text explaining quantum theory through semiconductor case studies."*  
        - Certifications: *"A nursing exam passage describing infection control protocols."*

    5. **Paragraph Logic Checks**:
    - Every paragraph must:  
        a) Reference the previous concept  
        b) Include a concrete example  
        c) State its exam relevance  
        *"Transition words (like 'however') signal contrasting ideas. In a chemistry passage, you might read: 'Reactant A increases yield. However, excess amounts cause side reactions.' This helps you anticipate compare/contrast questions."*
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
    - Description (12 to 16 paragraphs of deeply explanatory text with clear formatting for lists)
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
        "description": "<12 to 16 paragraphs of explanatory text. Use line breaks for clarity \\n\\n, especially when enumerating items, like 1), 2), 3), etc.",
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
            "description": "Reading comprehension begins with understanding how texts are typically organized. Authors often introduce a main thesis in the first paragraph, then use subsequent paragraphs to expand or refine that thesis.\\n\\nFor instance, a passage examining the impact of social media on communication might open by briefly describing a historical perspective on human interaction. It would then contrast that with modern digital dynamics, showing how social media has shifted norms.\\n\\nRecognizing paragraph organization is crucial. Topic sentences often appear at the beginning or end of each paragraph, summarizing the key idea. By spotting these, you can quickly outline the passage's core arguments.\\n\\nTransitional phrases like \"moreover\" or \"in contrast\" help connect individual points, indicating whether a paragraph supports or contradicts the previous discussion. Understanding these connections enriches your ability to see the big picture.\\n\\nContextual reading is another foundational element. If an author repeatedly references a particular concept—like \"algorithmic filtering\"—you can infer that this concept holds substantial significance.\\n\\nIn standardized tests, passages often follow predictable structures. Some center on cause-and-effect, while others employ compare-and-contrast formats to highlight similarities or differences. By recognizing these organizational cues, you can anticipate the flow of information.\\n\\nBackground knowledge can also aid comprehension. If you're familiar with social science theories, you'll notice how the passage correlates with or diverges from established paradigms.\\n\\nYou might see references to seminal studies or prominent authors. Identifying these references helps anchor the passage in a broader academic context, indicating its reliability or perspective.\\n\\nAnother key to understanding structure is paying attention to examples or case studies. Authors often illustrate abstract points with anecdotes or real-world data, making complex ideas more accessible.\\n\\nWhen you encounter unfamiliar vocabulary, look for definitions or restatements within the same paragraph. This internal context can guide you without having to rely on external dictionaries.\\n\\nBy mastering these structural basics, you'll develop a foundation for deeper analysis. The path toward advanced reading comprehension starts with the simple act of pinpointing how each paragraph builds upon or diverges from the preceding one.\\n\\nOver time, you'll learn to map out entire passages mentally, noting the main thesis, supporting evidence, and potential counterarguments. This skill will serve as a bedrock for the more nuanced inferential and critical reading techniques covered in the coming days.",
            "resources": "The Official Guide to the TOEFL Test, Reading practice websites",
            "estimated_hours_needed": 2
            },
            {
            "day_num": 2,
            "topics_for_the_day": "Refining Inference Skills",
            "subtopics": "Logical conclusions, Author’s assumptions, Evaluating evidence",
            "description": "Reading comprehension moves beyond surface-level understanding once you begin to recognize implied ideas. Inference, or \"reading between the lines,\" involves identifying connections that aren't explicitly stated but are suggested by the context.\\n\\nFor instance, if an author frequently cites research about the negative effects of processed foods without ever mentioning potential benefits, you might infer a particular bias or focus on the drawbacks.\\n\\nEvaluating an author's bias is central to deep analysis. Pay attention to words that indicate strong emotional undertones, such as \"unfortunately\" or \"unquestionably.\" These can signal a subjective stance.\\n\\nSome texts may use a balanced approach, carefully laying out both pros and cons of an issue. Others might adopt a more persuasive tone, guiding you toward a specific conclusion through selective presentation of facts.\\n\\nRhetorical devices like analogies or metaphors can reveal an author's perspective. A passage about climate change might compare rising temperatures to \"a ticking time bomb,\" emphasizing urgency and potential catastrophe.\\n\\nLook also for the presence of qualifiers—terms like \"likely,\" \"suggests,\" or \"possibly.\" Their usage can indicate that the writer is hedging claims, which might make the argument more nuanced and less absolute.\\n\\nWhen you come across data or statistics, consider their source and how they're integrated. Do they come from peer-reviewed journals, reputable organizations, or anecdotal accounts? This evaluation helps determine the argument's credibility.\\n\\nBe aware of how authors structure their reasoning. A cause-and-effect argument might detail a phenomenon's root causes before outlining its consequences, while a compare-and-contrast approach alternates between two subjects or viewpoints.\\n\\nIf a passage includes counterarguments, note whether they're given fair representation. A writer might introduce opposing views only to dismiss them quickly, revealing a potential bias or a selective approach.\\n\\nAdvanced rhetorical devices, such as parallelism or strategic repetition, also shape how a message is received. Repeated words or phrases can emphasize an idea or evoke an emotional response, thus guiding the reader's interpretation.\\n\\nBy honing your inferential and analytical skills, you'll be equipped not just to understand the central thesis but also to critique the logic and evidence behind it.\\n\\nUltimately, deeper reading comprehension allows you to engage with texts on a level that goes beyond memorizing facts. You'll learn to question assumptions, weigh arguments, and form your own reasoned conclusions.",
            "resources": "Practice passages from official test-prep materials, Academic reading journals",
            "estimated_hours_needed": 2    
            }
        ]
    }

    Important:

    - Use \\n (double backslash + n) within your JSON strings to represent actual line breaks.
    - Escape any double quotes inside strings (e.g., \"example\").
    - Do not insert raw control characters, invalid punctuation, or markdown code fences.
    - The final answer must be valid JSON, so it can be parsed by any standard JSON parser without error.
    - Ensure the "description" includes 12 to 16 paragraphs, using line breaks for multi-line lists or numbered items.
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
    - Description (12 to 16 paragraphs of deeply explanatory text with clear formatting for lists)
    - Resource recommendations (books, online courses, practice problems)
    - Estimated hours needed
    
    Make sure to follow the JSON structure and format for the output, with the correct keys and values, commas, etc.
    """
    
    

    if materials_content:
        user_prompt += f"\n\nUse the following official or known details about this exam:\n{materials_content}"
    
    return system_prompt, user_prompt

def build_quiz_prompt(topics_for_the_day, subtopics, search_results, materials_content):
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

    system_prompt = """
    You are a scholarly assistant tasked with generating 120 multiple choice questions for exam preparation. Follow these steps carefully:

    1. **Question Distribution**:
        - Generate exactly 120 total questions.
        - Split them into three difficulty levels:
            - 40 questions labeled as "easy"
            - 40 questions labeled as "medium"
            - 40 questions labeled as "hard"

    2. **Content Requirements**:
        - Questions should be based on:
            - topic
            - subtopics
            - search_about_exam
            - exam_materials

        - Ensure each question is relevant to the specified topic and subtopics.
        - Incorporate insights or references from the exam details (if provided in exam_materials or discovered via search_about_exam).

    3. **Question Structure**:
        - Each question must adhere to the following JSON format:

        {{
            "question_text": "string",
            "options": [
            {{ "option": "A", "text": "string" }},
            {{ "option": "B", "text": "string" }},
            {{ "option": "C", "text": "string" }},
            {{ "option": "D", "text": "string" }}
            ],
            "correct_answer": "A" | "B" | "C" | "D",
            "explanation": "string",
            "difficulty": "easy" | "medium" | "hard"
        }}
 
        Make sure:
            - **"question_text"** is clear and directly relates to the topic.
            - **"options"** is an array with four objects, each containing:
                - `"option"` (one of "A", "B", "C", "D")
                - `"text"` (the text for the option)
            - **"correct_answer"** is a single letter ("A", "B", "C", or "D").
            - **"explanation"** briefly justifies why the chosen answer is correct (1–3 sentences).
            - **"difficulty"** matches the category for that question: "easy", "medium", or "hard".

    4. Make sure all JSON **keys**:
    - Are enclosed in double quotes but have no leading or trailing spaces, e.g., "options".
    - Do not include extra quotes or indentation within the key. For instance, do not produce "    \"options\"" or similar variants.
    - Avoid any invalid punctuation, characters, or formatting that might break JSON parsing (like unescaped quotes, random backticks, or trailing commas).
    - Ensure that the final JSON is well-formed and parseable by standard JSON libraries.

    5. **Additional Instructions**:
        - Avoid overly tricky or ambiguous wording.
        - Use domain-appropriate language and concepts.
        - Distribute question complexity consistently across easy, medium, and hard sets.
        
    ---

    ### Example Input (for demonstration purposes)

    Topic: topics
    Subtopics: subtopics
    Web information about the exam: search_results
    Exam materials: materials_content

    ### Example JSON Output (for demonstration purposes)

    [{{"question_text": "Which of the following best describes the First Law of Thermodynamics?", "options": [ { "option": "A", "text": "It states that energy cannot be created or destroyed, only transformed." }, { "option": "B", "text": "It explains how entropy tends to increase in an isolated system." }, { "option": "C", "text": "It focuses on the concept of absolute zero temperature." }, { "option": "D", "text": "It describes how heat is transferred via conduction and radiation only." } ], "correct_answer": "A", "explanation": "The First Law is also known as the principle of conservation of energy. Energy remains constant in a closed system.", "difficulty": "easy" }}, { "question_text": "Entropy is best defined as:", "options": [ { "option": "A", "text": "A measure of the total heat within a system." }, { "option": "B", "text": "A statistical measure of the disorder or randomness in a system." }, { "option": "C", "text": "The rate of thermal energy flow." }, { "option": "D", "text": "The energy lost due to friction within a system." } ], "correct_answer": "B", "explanation": "Entropy is often considered a measure of molecular randomness. A higher entropy correlates with greater disorder.", "difficulty": "easy" }}, { "question_text": "An isothermal process in thermodynamics implies:", "options": [ { "option": "A", "text": "Constant internal energy throughout the process." }, { "option": "B", "text": "Constant temperature throughout the process." }, { "option": "C", "text": "No heat exchange with surroundings." }, { "option": "D", "text": "A drastic change in entropy of the system." } ], "correct_answer": "B", "explanation": "In an isothermal process, temperature remains the same; heat can flow in or out to maintain that temperature.", "difficulty": "medium" }} // ... up to a total of 120 questions, split into 40 easy, 40 medium, 40 hard ]
    
    In the **real** output, you will provide **120** such objects, each following the structure above. Remember to distribute them as **40 easy, 40 medium, 40 hard**. 

    **Important Notes**:
        - Return only valid JSON—no additional commentary, markdown, or decorative characters.
        - Each question object must contain the keys: `"question_text"`, `"options"`, `"correct_answer"`, `"explanation"`, and `"difficulty"`.
        - The array must have exactly 120 objects.
    """
    
    prompt = f"""
    Topic: {topics_for_the_day}
    Subtopics: {subtopics}
    Web information about the exam: {search_results}
    Exam materials: {materials_content}

    I need 120 multiple choice questions based on the above details, make sure to generate questions based on the topic and subtopics, using the information of web information and exam materials as a reference:
    - 40 easy questions
    - 40 medium questions
    - 40 hard questions

    Please provide each question in valid JSON with the following structure:
        {{
        "question_text": "string",
        "options": [
            {{ "option": "A", "text": "string" }},
            {{ "option": "B", "text": "string" }},
            {{ "option": "C", "text": "string" }},
            {{ "option": "D", "text": "string" }}
        ],
        "correct_answer": "A" | "B" | "C" | "D",
        "explanation": "string",
        "difficulty": "easy" | "medium" | "hard"
        }}

    Return your answer as a JSON array of 120 objects, with no additional commentary or formatting.
    """
    
    return system_prompt, prompt 