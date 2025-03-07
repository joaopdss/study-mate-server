from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, date

@dataclass
class exam:
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: str = ""
    country: str = ""
    exam_date: Union[str, date] = None
    goal_score: str = ""
    topics: List[str] = None
    proficiency: str = ""
    study_schedule: List[str] = None
    hours_per_day: int = 0
    exam_materials: List[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if self.study_schedule is None:
            self.study_schedule = []

@dataclass
class ExamMaterial:
    id: Optional[str] = None
    exam_id: str = ""
    file_path: str = ""
    file_name: str = ""
    file_type: str = ""
    file_size: int = 0
    created_at: Optional[datetime] = None

@dataclass
class StudyPlan:
    id: Optional[str] = None
    exam_id: str = ""
    plan_text: str = ""
    created_at: Optional[datetime] = None

@dataclass
class StudyPlanDay:
    id: Optional[str] = None
    study_plan_id: str = ""
    day_number: int = 0
    planned_topics: List[str] = None
    resources: List[Dict] = None
    estimated_hours: int = 0
    completed: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.planned_topics is None:
            self.planned_topics = []
        if self.resources is None:
            self.resources = []

@dataclass
class Quiz:
    id: Optional[str] = None
    exam_id: str = ""
    date: Union[str, date] = None
    difficulty: str = ""
    topics_of_the_day: List[str] = None
    num_questions: int = 0
    
    def __post_init__(self):
        if self.topics_of_the_day is None:
            self.topics_of_the_day = []

@dataclass
class Question:
    id: Optional[str] = None
    quiz_id: str = ""
    question_text: str = ""
    options: List[str] = None
    correct_answer: str = ""
    explanation: str = ""
    topic: str = ""
    difficulty: str = ""
    
    def __post_init__(self):
        if self.options is None:
            self.options = [] 