import json
import requests
import os
from dotenv import load_dotenv
import math

# Load environment variables from .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# -----------------------------
# JSON TASK FUNCTIONS
# -----------------------------

# Load all tasks from JSON file
def load_tasks():
    try:
        with open('tasks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tasks', [])
    except FileNotFoundError:
        print("Error: tasks.json file not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in tasks.json - {e}")
        return []
    except Exception as e:
        print(f"Unexpected error loading tasks: {e}")
        return []

# Get a task by its name (case-insensitive)
def get_task_by_name(task_name):
    tasks = load_tasks()
    for task in tasks:
        if task_name.lower() in task['title'].lower():
            return task
    return None

# Get a task by its ID (optional)
def get_task_by_id(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get('task_id') == task_id:
            return task
    return None

# List all task titles
def list_all_tasks():
    tasks = load_tasks()
    return [task['title'] for task in tasks]

# -----------------------------
# ONLINE/OFFLINE CHECKS
# -----------------------------

def is_online_available(task):
    """Check if online application is available"""
    try:
        return task['application_mode']['online']['available'] is True
    except (KeyError, TypeError):
        return False

def is_offline_available(task):
    """Check if offline application is available"""
    try:
        return task['application_mode']['offline']['available'] is True
    except (KeyError, TypeError):
        return False

# -----------------------------
# GOOGLE PLACES API FUNCTIONS
# -----------------------------

def find_nearest_offline_center(keyword, user_location, radius=5000):
    """
    Finds the nearest offline center using Google Places API.
    
    Args:
        keyword (str): What to search for (e.g., "PAN facilitation center")
        user_location (dict): {'lat': xx.xxxxx, 'lng': yy.yyyyy}
        radius (int): search radius in meters

    Returns:
        tuple: (name, address) of the nearest place, or (None, None)
    """
    if not keyword or not user_location:
        print("Error: Missing keyword or user location")
        return None, None
    
    if not GOOGLE_API_KEY:
        # Fallback: Use Nominatim (OpenStreetMap) if no Google API key is configured.
        # Nominatim requires a valid User-Agent header.
        try:
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": keyword,
                "format": "json",
                "limit": 10,
            }
            headers = {"User-Agent": "documentation-pathway-app/1.0 (contact: none)"}
            resp = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            places = resp.json()

            if not places:
                print(f"Nominatim: no places found for keyword: {keyword}")
                return None, None

            # Helper to compute distance (meters) between two lat/lng points
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371000  # Earth radius in meters
                phi1 = math.radians(lat1)
                phi2 = math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlambda = math.radians(lon2 - lon1)
                a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

            user_lat = float(user_location.get('lat'))
            user_lng = float(user_location.get('lng'))

            nearest = None
            nearest_dist = float('inf')
            for p in places:
                try:
                    plat = float(p.get('lat'))
                    plng = float(p.get('lon'))
                except (TypeError, ValueError):
                    continue
                dist = haversine(user_lat, user_lng, plat, plng)
                if dist <= radius and dist < nearest_dist:
                    nearest_dist = dist
                    nearest = p

            if nearest:
                name = nearest.get('display_name', keyword)
                address = nearest.get('display_name', 'Address not available')
                return name, address
            else:
                print(f"Nominatim: no nearby places within {radius}m for keyword: {keyword}")
                return None, None
        except requests.RequestException as e:
            print(f"Network error fetching Nominatim: {e}")
            return None, None
        except Exception as e:
            print(f"Unexpected Nominatim error: {e}")
            return None, None
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": GOOGLE_API_KEY,
        "location": f"{user_location['lat']},{user_location['lng']}",
        "radius": radius,
        "keyword": keyword
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK':
            results = data.get('results', [])
            if results:
                nearest = results[0]
                name = nearest.get('name', 'Unknown')
                address = nearest.get('vicinity', 'Address not available')
                return name, address
            else:
                print(f"No places found for keyword: {keyword}")
                return None, None
        else:
            error_msg = data.get('error_message', 'Unknown API error')
            print(f"Google Places API error: {data.get('status')} - {error_msg}")
            return None, None
            
    except requests.RequestException as e:
        print(f"Network error fetching Google Places: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error fetching Google Places: {e}")
        return None, None

# -----------------------------
# UTILITIES
# -----------------------------

def get_application_steps(task, mode='online'):
    """
    Returns the list of steps for online/offline application
    """
    try:
        steps = task['application_mode'][mode]['steps']
        return steps
    except (KeyError, TypeError):
        return None
