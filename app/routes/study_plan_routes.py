"""
Routes for study plan generation and management.
"""
from flask import Blueprint, request, jsonify
from app.models.db import get_supabase_client
from app.services.search_service import search_exam_info
from app.services.llm_service import generate_study_plan
from app.utils.ai_prompt_builder import build_study_plan_prompt, build_prompt_to_validate_json
from app.utils.pdf_processor import process_exam_materials
import json
import uuid
from datetime import datetime
from app.utils.ai_prompt_builder import build_quiz_prompt
from app.services.llm_service import generate_quiz
from app.services.llm_service import call_llm
import threading

study_plan_bp = Blueprint('study_plan', __name__)

# Function to generate quizzes in the background
def generate_quizzes_background(study_plan_id, study_plan_data, day_ids_map, search_results, materials_content, country):
    """
    Function to generate quizzes for a study plan in the background.
    
    Args:
        study_plan_id (str): The ID of the study plan
        study_plan_data (dict): The study plan data
        day_ids_map (dict): Mapping of day numbers to day IDs
        search_results (str): Search results from Perplexity
        materials_content (str): Content from PDF materials
    """
    try:
        print(f"Starting background quiz generation for study plan: {study_plan_id}")
        supabase = get_supabase_client()
        
        # Create quizzes for each day of the study plan
        for day in study_plan_data.get('day_topics', []):
            # Create request data for the quiz generation
            day_num = day.get('day_num', 0)
            topics_for_the_day = [day.get('topics_for_the_day', '')]
            subtopics = day.get('subtopics', '')
            
            print(f"Generating quiz for day {day_num} with topics: {topics_for_the_day}")
            
            try:                    
                # Build prompt for quiz generation
                system_prompt, prompt = build_quiz_prompt(topics_for_the_day, subtopics, search_results, materials_content, country)
                
                # Generate quiz
                questions = generate_quiz(system_prompt, prompt)
                
                print(questions)

                # Parse JSON if it's returned as a string
                if isinstance(questions, str):
                    try:
                        print("entrou")
                        questions = json.loads(questions)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse questions JSON: {str(e)}")
                        print(f"Trying to fix JSON")
                        system_prompt_json, user_prompt_json = build_prompt_to_validate_json(questions)
                        
                        questions = call_llm(system_prompt_json, user_prompt_json)
                        questions = json.loads(questions)

                print(type(questions))
                
                # Insert questions into database
                for question in questions['questions'] if "questions" in questions else questions['output']:
                    # Validate question format
                    try:
                        question_id = str(uuid.uuid4())
                        topic_value = topics_for_the_day
                        # If topic is a list, extract just the string
                        if isinstance(topic_value, list):
                            topic_value = topic_value[0] if topic_value else ""
                        # If it's still a string with brackets and quotes, remove them
                        if isinstance(topic_value, str) and topic_value.startswith('[') and topic_value.endswith(']'):
                            # Strip the brackets and quotes
                            topic_value = topic_value.strip('[]"\'')

                        # Insert the question into the database
                        question_result = supabase.table('questions').insert({
                            "id": question_id,
                            "study_plan_days_id": day_ids_map[day_num],  # Use the day_id we got when inserting the day
                            "passage": question.get('passage', ''),
                            "question_text": question.get('question_text', ''),
                            "options": question.get('options', []),
                            "correct_answer": question.get('correct_answer', ''),
                            "explanation": question.get('explanation', ''),
                            "topic": topic_value,  # Now it's just the string without brackets
                            "difficulty": question.get('difficulty', 'medium')  # Default to medium if not specified
                        }).execute()
                        
                        print(f"Inserted question: {question_id}")
                    except Exception as q_e:
                        print(f"Error inserting question: {str(q_e)}")
                
                print(f"Successfully generated questions for day {day_num}")
                
            except Exception as quiz_e:
                print(f"Error generating quiz for day {day_num}: {str(quiz_e)}")
                
        print(f"Background quiz generation completed for study plan: {study_plan_id}")
    except Exception as e:
        print(f"Error in background task: {str(e)}")

@study_plan_bp.route('/plan/generate', methods=['POST'])
def generate_plan():
    """
    Endpoint to generate a study plan for an exam.
    """
    try:
        print("eai koe")
        # Get JSON data from request
        data = request.get_json()
        exam_id = data.get('exam_id')
        amount_of_days = data.get('amount_of_days', 1)
        include_internet_search = data.get('include_internet_search', True)
        
        if not exam_id:
            return jsonify({"error": "Missing exam_id parameter"}), 400
        
        # Fetch exam data from Supabase
        supabase = get_supabase_client()
        exam_result = supabase.table('exams').select('*').eq('id', exam_id).execute()
        
        if not exam_result.data:
            return jsonify({"error": "Exam not found"}), 404
        
        exam_data = exam_result.data[0]
        
        print(f"Exam data: {exam_data.get('exam_materials', [])}")
        # Process PDF materials
        materials_content = process_exam_materials(exam_data.get('exam_materials', []))
        
        # Optional: Call Perplexity to get more info about the exam
        print("Calling Perplexity")
        search_results = None
        if include_internet_search:
            search_results = search_exam_info(
                exam_data.get('title', ''),
                exam_data.get('country', ''),
                exam_data.get('exam_topics', []),
                exam_data.get('educational_level', ''),
                materials_content
            )
        
        # Build the prompt for the LLM
        from app.models.models import exam
        exam = exam(
            id=exam_data.get('id'),
            title=exam_data.get('title'),
            country=exam_data.get('country'),
            exam_date=exam_data.get('exam_date'),
            goal_score=exam_data.get('goal_score'),
            topics=exam_data.get('exam_topics', []),
            proficiency=exam_data.get('proficiency'),
            study_schedule=exam_data.get('study_schedule', []),
            hours_per_day=exam_data.get('hours_per_day', 0)
        )
        
        print("Creating plan prompt")
        system_prompt, user_prompt = build_study_plan_prompt(exam, search_results, materials_content, amount_of_days)

        print(f"Search results: /n/n{search_results}")
        
        # Call LLM to generate study plan
        study_plan_data = generate_study_plan(system_prompt, user_prompt)

        print(f"Study plan data: \n\n{study_plan_data}")
        
        if not study_plan_data:
            return jsonify({"error": "Failed to generate study plan"}), 500
        
        print("Converting plan to JSON")
        # Ensure study_plan_data is a dictionary (parse JSON if it's a string)
        if isinstance(study_plan_data, str):
            try:
                print("Parsing study_plan_data from JSON string")
                study_plan_data = json.loads(study_plan_data)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                return jsonify({"error": f"Invalid study plan data format: {str(e)}"}), 500
        
        print(type(study_plan_data))
        print("Inserting study plan into Supabase")
        # Generate a new UUID for the study plan
        study_plan_id = str(uuid.uuid4())
        
        # Current timestamp for created_at
        current_timestamp = datetime.utcnow().isoformat()
        
        try:
            print(f"Inserting study plan into Supabase with ID: {study_plan_id}")
            insert_data = {
                "id": study_plan_id,
                "exam_id": exam_id,
                "plan_text": json.dumps(study_plan_data),  # Store the entire JSON as text
                "overview": study_plan_data.get('overview', ''),
                "created_at": current_timestamp
            }
            print(f"Insert data: {insert_data}")
            plan_insert_result = supabase.table('study_plans').insert({
                "id": study_plan_id,
                "exam_id": exam_id,
                "plan_text": json.dumps(study_plan_data),  # Store the entire JSON as text
                "overview": study_plan_data.get('overview', ''),
                "created_at": current_timestamp
            }).execute()
            
            print(f"Plan insert result: {plan_insert_result}")
            
            if not plan_insert_result.data:
                print("No data returned from study_plan insert")
                return jsonify({"error": "Failed to save study plan"}), 500
                
            # Insert study plan days
            print(f"Inserting study plan days into Supabase for plan: {study_plan_id}")
            day_ids_map = {}
            for day in study_plan_data.get('day_topics', []):
                day_id = str(uuid.uuid4())
                day_ids_map[day.get('day_num', 0)] = day_id
                day_insert_result = supabase.table('study_plan_days').insert({
                    "id": day_id,
                    "study_plan_id": study_plan_id,
                    "day_number": day.get('day_num', 0),
                    "planned_topics": day.get('topics_for_the_day', ''),
                    "subtopics": day.get('subtopics', ''),
                    "resources": day.get('resources', ''),
                    "estimated_hours": day.get('estimated_hours_needed', 0),
                    "completed": False,
                    "description": day.get('description', ''),  # Empty description for now
                    "created_at": current_timestamp
                }).execute()
                print(f"Inserted day {day.get('day_num', 0)} with ID: {day_id}")
            
            # Return the response immediately while starting quiz generation in background
            response_data = {
                "id": study_plan_id,
                "exam_id": exam_id,
                "overview": study_plan_data.get('overview', ''),
                "days": study_plan_data.get('day_topics', [])
            }
            
            # Add the first day ID to the response if available
            if day_ids_map and len(day_ids_map) > 0:
                # Find the minimum day number (first day)
                first_day_num = min(day_ids_map.keys())
                first_day_id = day_ids_map[first_day_num]
                response_data["first_day_id"] = first_day_id
            
            # Start quiz generation in a background thread
            quiz_thread = threading.Thread(
                target=generate_quizzes_background,
                args=(study_plan_id, study_plan_data, day_ids_map, search_results, materials_content, exam_data.get('country', ''))
            )
            quiz_thread.daemon = True  # This ensures the thread won't block app shutdown
            quiz_thread.start()
            
            print(f"Successfully created study plan: {study_plan_id} - Background quiz generation started")
            return jsonify(response_data), 201
                
        except Exception as e:
            print(f"Supabase error: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@study_plan_bp.route('/plan/<exam_id>', methods=['GET'])
def get_study_plan(exam_id):
    """
    Endpoint to get a study plan for an exam.
    """
    try:
        if not exam_id:
            return jsonify({"error": "Missing exam_id parameter"}), 400
        
        supabase = get_supabase_client()
        
        # Get the study plan for this exam
        plan_result = supabase.table('StudyPlan').select('*').eq('exam_id', exam_id).execute()
        
        if not plan_result.data:
            return jsonify({"error": "Study plan not found"}), 404
        
        study_plan = plan_result.data[0]
        study_plan_id = study_plan['id']
        
        # Get the days for this study plan
        days_result = supabase.table('StudyPlanDays').select('*').eq('study_plan_id', study_plan_id).order('day_number').execute()
        
        # Combine the data
        response = {
            "id": study_plan_id,
            "exam_id": exam_id,
            "overview": study_plan.get('plan_text', ''),
            "days": days_result.data if days_result.data else []
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@study_plan_bp.route('/plan/day/<day_id>/complete', methods=['POST'])
def complete_day(day_id):
    """
    Endpoint to mark a study plan day as completed.
    """
    try:
        if not day_id:
            return jsonify({"error": "Missing day_id parameter"}), 400
        
        supabase = get_supabase_client()
        
        # Update the day's completed status
        result = supabase.table('StudyPlanDays').update({"completed": True}).eq('id', day_id).execute()
        
        if not result.data:
            return jsonify({"error": "Day not found or update failed"}), 404
        
        return jsonify({"success": True, "data": result.data[0]}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 