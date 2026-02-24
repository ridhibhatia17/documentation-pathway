from flask import Flask, render_template, request, jsonify
from utils.helper import get_task_by_name, list_all_tasks, find_nearest_offline_center, load_tasks
from fuzzywuzzy import process
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/')
def home():
    tasks = list_all_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/task', methods=['POST'])
def task_info():
    task_name = request.form.get('task_name')
    task = get_task_by_name(task_name)
    if task:
        return render_template('task_details.html', task=task)
    else:
        return "Task not found", 404

@app.route('/find_centers', methods=['POST'])
def find_centers():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        keyword = data.get('keyword')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 5000)  # Default 5km radius
        
        if not keyword or not latitude or not longitude:
            return jsonify({'error': 'Missing required parameters: keyword, latitude, longitude'}), 400
        
        # Validate coordinates
        try:
            lat = float(latitude)
            lng = float(longitude)
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return jsonify({'error': 'Invalid coordinates'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid coordinate format'}), 400

        user_location = {'lat': lat, 'lng': lng}
        name, address = find_nearest_offline_center(keyword, user_location, radius)
        
        if name and address:
            return jsonify({
                'success': True,
                'center': {
                    'name': name,
                    'address': address
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No centers found nearby. Try increasing the search radius or using different keywords.'
            })
    
    except Exception as e:
        print(f"Error in find_centers: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/nlp_search', methods=['POST'])
def nlp_search():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    all_tasks = load_tasks()
    
    try:
        # Create a list of available tasks for Gemini to choose from
        task_list = []
        for i, task in enumerate(all_tasks):
            task_info = f"{i+1}. {task['title']} - {task.get('description', '')}"
            task_list.append(task_info)
        
        # Create prompt for Gemini
        prompt = f"""
You are an AI assistant helping users find the most relevant legal/government task from a list of available tasks.

User Query: "{query}"

Available Tasks:
{chr(10).join(task_list)}

IMPORTANT MATCHING RULES:
- "aadhar", "aadhaar", "adhaar" should match "Aadhaar Card Registration"
- "pan card" should match "PAN Card Application"  
- "marriage" should match "Marriage Registration"
- "passport" should match "Passport Application"
- "driving license" should match "Driving License Application"
- "company registration", "register company", "new company" should match "Private Limited Company Registration"
- "gst registration" should match "GST Registration"

Instructions:
1. Analyze the user's query carefully
2. Look for the MOST RELEVANT task from the list above
3. Pay special attention to common misspellings and variations
4. Respond with ONLY the exact task title (not the number or description)
5. If no task is clearly relevant, respond with "NO_MATCH"

Examples:
- "i was thinking to make my aadhar card" → "Aadhaar Card Registration"
- "apply for aadhar card" → "Aadhaar Card Registration"
- "get pan card" → "PAN Card Application"
- "register my marriage" → "Marriage Registration"
- "how do I register a new company" → "Private Limited Company Registration"
- "company registration" → "Private Limited Company Registration"

Task Title:"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        gemini_result = response.text.strip()
        
        print(f'NLP Query: {query}, Gemini Response: {gemini_result}')
        
        # Check if Gemini found a match
        if gemini_result == "NO_MATCH":
            return jsonify({
                'success': False, 
                'message': 'No relevant legal task found. Try being more specific or use different keywords.'
            })
        
        # Verify the Gemini response matches an actual task
        for task in all_tasks:
            if gemini_result.lower() == task['title'].lower():
                return jsonify({'success': True, 'task': task['title']})
        
        # If exact match not found, use fuzzy matching as fallback
        task_titles = [task['title'] for task in all_tasks]
        best_match, score = process.extractOne(gemini_result, task_titles)
        
        if score > 80:  # High threshold for Gemini fallback
            return jsonify({'success': True, 'task': best_match})
        else:
            return jsonify({
                'success': False, 
                'message': f'Task suggested by AI ("{gemini_result}") not found in database.'
            })
    
    except Exception as e:
        print(f'Gemini API Error: {e}')
        # Fallback to simple fuzzy matching if Gemini fails
        task_titles = [task['title'] for task in all_tasks]
        best_match, score = process.extractOne(query, task_titles)
        print(f'Fallback - Query: {query}, Match: {best_match}, Score: {score}')
        
        if score > 50:
            return jsonify({'success': True, 'task': best_match})
        else:
            return jsonify({
                'success': False, 
                'message': 'AI service temporarily unavailable. Try using exact task names.'
            })

if __name__ == '__main__':
    app.run(debug=True)
