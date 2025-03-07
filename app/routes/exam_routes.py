"""
Routes for exam management.
"""
from flask import Blueprint, request, jsonify
from app.models.db import get_supabase_client
from app.models.models import exam

exam_bp = Blueprint('exams', __name__)

@exam_bp.route('/exams', methods=['POST'])
def create_exam():
    """
    Endpoint to create a new exam.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Create Exam object
        exam = exam(
            title=data.get('title'),
            country=data.get('country'),
            exam_date=data.get('exam_date'),
            goal_score=data.get('goal_score'),
            topics=data.get('topics', []),
            proficiency=data.get('proficiency'),
            study_schedule=data.get('study_schedule', []),
            hours_per_day=data.get('hours_per_day', 0)
        )
        
        # Basic validation
        if not exam.title or not exam.country or not exam.exam_date:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Insert exam data into Supabase
        supabase = get_supabase_client()
        result = supabase.table('exams').insert({
            "title": exam.title,
            "country": exam.country,
            "exam_date": exam.exam_date,
            "goal_score": exam.goal_score,
            "topics": exam.topics,
            "proficiency": exam.proficiency,
            "study_schedule": exam.study_schedule,
            "hours_per_day": exam.hours_per_day
        }).execute()
        
        # Process any materials if provided
        materials = data.get('materials', [])
        if materials and result.data and len(result.data) > 0:
            exam_id = result.data[0]['id']
            
            # Insert each material reference
            for material in materials:
                supabase.table('exam_materials').insert({
                    "exam_id": exam_id,
                    "file_path": material,
                    "file_name": material.split('/')[-1] if '/' in material else material,
                    "file_type": get_file_type(material),
                    "file_size": 0  # Would need file size calculation
                }).execute()
        
        return jsonify(result.data[0] if result.data else {}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_bp.route('/exams/<exam_id>', methods=['GET'])
def get_exam(exam_id):
    """
    Endpoint to get an exam by ID.
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch exam data
        result = supabase.table('exams').select('*').eq('id', exam_id).execute()
        
        if not result.data:
            return jsonify({"error": "Exam not found"}), 404
            
        # Fetch materials for this exam
        materials = supabase.table('exam_materials').select('*').eq('exam_id', exam_id).execute()
        
        # Combine the data
        exam_data = result.data[0]
        exam_data['materials'] = materials.data if materials.data else []
        
        return jsonify(exam_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exam_bp.route('/exams', methods=['GET'])
def list_exams():
    """
    Endpoint to list all exams.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table('exams').select('*').execute()
        
        return jsonify(result.data if result.data else []), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_file_type(file_path):
    """
    Helper function to get the file type from a file path.
    """
    if not file_path:
        return ""
        
    # Check for URL
    if file_path.startswith(("http://", "https://")):
        # Extract extension from URL
        path = file_path.split("?")[0]  # Remove query parameters
        extension = path.split(".")[-1].lower() if "." in path else ""
    else:
        # Local file
        extension = file_path.split(".")[-1].lower() if "." in file_path else ""
    
    # Map extensions to file types
    if extension in ["pdf"]:
        return "pdf"
    elif extension in ["jpg", "jpeg", "png", "gif"]:
        return "image"
    elif extension in ["doc", "docx"]:
        return "document"
    elif extension in ["xls", "xlsx"]:
        return "spreadsheet"
    else:
        return extension 