"""
Routes for quiz generation and management.
"""
from flask import Blueprint, request, jsonify
from app.models.db import get_supabase_client
from app.services.search_service import search_exam_info
from app.services.llm_service import generate_quiz
from app.utils.ai_prompt_builder import build_quiz_prompt
from app.utils.pdf_processor import process_exam_materials
from typing import List, Dict, Any

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz/generate', methods=['POST'])
def generate_quiz_endpoint():
    """
    Endpoint to generate a quiz for an exam.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        exam_id = data.get('exam_id')
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'Medium')
        topics_of_the_day = data.get('topics_of_the_day', [])
        
        if not exam_id:
            return jsonify({"error": "Missing exam_id parameter"}), 400
        
        # Fetch exam data from Supabase
        supabase = get_supabase_client()
        exam_result = supabase.table('Exams').select('*').eq('id', exam_id).execute()
        
        if not exam_result.data:
            return jsonify({"error": "Exam not found"}), 404
        
        exam_data = exam_result.data[0]
        
        # Fetch materials for this exam
        materials_result = supabase.table('exam_materials').select('*').eq('exam_id', exam_id).execute()
        exam_materials = [item.get('file_path') for item in materials_result.data] if materials_result.data else []
        
        # Process PDF materials, focusing on the current topics
        materials_content = ""
        if exam_materials:
            materials_content = process_exam_materials(exam_materials)
        
        # Optional: Call Perplexity to get more info about the topics
        search_results = None
        if topics_of_the_day:
            search_results = search_exam_info(
                exam_data.get('title', ''),
                exam_data.get('country', ''),
                topics_of_the_day,
                exam_data.get('educational_level', ''),
                materials_content
            )
        
        # Build the prompt for the LLM
        from app.models.models import exam
        exam = exam(
            id=exam_data.get('id'),
            title=exam_data.get('title'),
            country=exam_data.get('country'),
            proficiency=exam_data.get('proficiency')
        )
        
        quiz_request = {
            "num_questions": num_questions,
            "difficulty": difficulty,
            "topics_of_the_day": topics_of_the_day
        }
        
        system_prompt, prompt = build_quiz_prompt(quiz_request, exam, search_results, materials_content)
        
        # Call LLM to generate quiz
        questions = generate_quiz(system_prompt, prompt)
        
        if not questions:
            return jsonify({"error": "Failed to generate quiz"}), 500
        
        # Insert quiz into Supabase
        import datetime
        quiz_insert_result = supabase.table('Quiz').insert({
            "exam_id": exam_id,
            "date": datetime.datetime.now().isoformat(),
            "difficulty": difficulty,
            "topics_of_the_day": topics_of_the_day,
            "num_questions": num_questions
        }).execute()
        
        if not quiz_insert_result.data:
            return jsonify({"error": "Failed to save quiz"}), 500
        
        quiz_id = quiz_insert_result.data[0]['id']
        
        # Insert questions
        for question in questions:
            # Validate question format
            if isinstance(question, dict) and 'question_text' in question and 'options' in question:
                supabase.table('Questions').insert({
                    "quiz_id": quiz_id,
                    "question_text": question.get('question_text', ''),
                    "options": question.get('options', []),
                    "correct_answer": question.get('correct_answer', ''),
                    "explanation": question.get('explanation', ''),
                    "topic": question.get('topic', ''),
                    "difficulty": question.get('difficulty', difficulty)
                }).execute()
        
        # Return the quiz with its questions
        return jsonify({
            "id": quiz_id,
            "exam_id": exam_id,
            "date": datetime.datetime.now().isoformat(),
            "difficulty": difficulty,
            "topics_of_the_day": topics_of_the_day,
            "num_questions": num_questions,
            "questions": questions
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quiz/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """
    Endpoint to get a quiz by ID.
    """
    try:
        if not quiz_id:
            return jsonify({"error": "Missing quiz_id parameter"}), 400
        
        supabase = get_supabase_client()
        
        # Get the quiz
        quiz_result = supabase.table('Quiz').select('*').eq('id', quiz_id).execute()
        
        if not quiz_result.data:
            return jsonify({"error": "Quiz not found"}), 404
        
        quiz = quiz_result.data[0]
        
        # Get the questions for this quiz
        questions_result = supabase.table('Questions').select('*').eq('quiz_id', quiz_id).execute()
        
        # Combine the data
        response = {
            **quiz,
            "questions": questions_result.data if questions_result.data else []
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/quiz/exam/<exam_id>', methods=['GET'])
def get_quizzes_for_exam(exam_id):
    """
    Endpoint to get all quizzes for an exam.
    """
    try:
        if not exam_id:
            return jsonify({"error": "Missing exam_id parameter"}), 400
        
        supabase = get_supabase_client()
        
        # Get all quizzes for this exam
        quiz_result = supabase.table('Quiz').select('*').eq('exam_id', exam_id).execute()
        
        return jsonify(quiz_result.data if quiz_result.data else []), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 