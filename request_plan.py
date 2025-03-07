import requests
import json
import sys

def generate_plan(exam_id, server_url="http://localhost:5000"):
    """
    Send a request to the /plan/generate endpoint on the Flask server.
    
    Args:
        exam_id (str): The ID of the exam to generate a plan for
        server_url (str): Base URL of the server
    """
    url = f"{server_url}/api/plan/generate"
    
    # Prepare request data
    data = {
        "exam_id": exam_id,
        "include_internet_search": True
    }
    
    # Send the request
    print(f"Sending request to {url} with exam_id: {exam_id}")
    try:
        response = requests.post(url, json=data)
        
        # Process the response
        if response.status_code == 201:
            result = response.json()
            print("\n✅ Study plan generated successfully!")
            print(f"Study Plan ID: {result.get('id')}")
            print(f"Overview: {result.get('overview')[:200]}...")
            print(f"Number of days: {len(result.get('days', []))}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")

if __name__ == "__main__":
    # Get exam ID from command line or use default
    exam_id = sys.argv[1] if len(sys.argv) > 1 else "73676217-e5bf-4afc-8eca-a77989a98903"
    generate_plan(exam_id) 