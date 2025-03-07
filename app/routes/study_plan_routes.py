"""
Routes for study plan generation and management.
"""
from flask import Blueprint, request, jsonify
from app.models.db import get_supabase_client
from app.services.search_service import search_exam_info
from app.services.llm_service import generate_study_plan
from app.utils.ai_prompt_builder import build_study_plan_prompt
from app.utils.pdf_processor import process_exam_materials

study_plan_bp = Blueprint('study_plan', __name__)

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
        system_prompt, user_prompt = build_study_plan_prompt(exam, search_results, materials_content)

        print(f"Search results: /n/n{search_results}")
        
        # Call LLM to generate study plan
        study_plan_data = generate_study_plan(system_prompt, user_prompt)

        print(f"Study plan data: /n/n{study_plan_data}")
        
        # if not study_plan_data:
        #     return jsonify({"error": "Failed to generate study plan"}), 500
        
        # # Insert study plan into Supabase
        # plan_insert_result = supabase.table('s').insert({
        #     "exam_id": exam_id,
        #     "plan_text": study_plan_data.get('overview', '')
        # }).execute()
        
        # if not plan_insert_result.data:
        #     return jsonify({"error": "Failed to save study plan"}), 500
        
        # study_plan_id = plan_insert_result.data[0]['id']
        
        # # Insert study plan days
        # for day in study_plan_data.get('days', []):
        #     supabase.table('StudyPlanDays').insert({
        #         "study_plan_id": study_plan_id,
        #         "day_number": day.get('day_number', 0),
        #         "planned_topics": day.get('planned_topics', []),
        #         "resources": day.get('resources', []),
        #         "estimated_hours": day.get('estimated_hours', 0),
        #         "completed": False
        #     }).execute()
        
        # # Return the study plan with its days
        # return jsonify({
        #     "id": study_plan_id,
        #     "exam_id": exam_id,
        #     "overview": study_plan_data.get('overview', ''),
        #     "days": study_plan_data.get('days', [])
        # }), 201
        
    except Exception as e:
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