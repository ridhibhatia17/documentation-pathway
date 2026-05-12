import json
import requests
import os
from dotenv import load_dotenv
import math
from urllib.parse import quote_plus

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

def _build_search_variants(keyword):
    """Build broader search phrases when the exact place name is too strict."""
    base = " ".join(str(keyword).split())
    normalized = base.replace("centre", "center")
    variants = [base]

    if normalized.lower() != base.lower():
        variants.append(normalized)

    suffixes = [
        " center",
        " centre",
        " office",
        " kendra",
        " facilitation center",
        " enrollment center",
        " registration center",
        " service center",
        " csc center",
    ]

    for suffix in suffixes:
        candidate = f"{normalized}{suffix}"
        if candidate.lower() not in [variant.lower() for variant in variants]:
            variants.append(candidate)

    return variants

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
    location = f"{user_location['lat']},{user_location['lng']}"
    search_variants = _build_search_variants(keyword)
    radius_candidates = []
    for candidate_radius in [radius, max(radius * 3, 15000), max(radius * 6, 30000), 50000]:
        if candidate_radius not in radius_candidates:
            radius_candidates.append(candidate_radius)

    try:
        # Try the exact keyword first, then broader variants and wider radii.
        google_denied = False
        for variant in search_variants:
            for candidate_radius in radius_candidates:
                params = {
                    "key": GOOGLE_API_KEY,
                    "location": location,
                    "radius": candidate_radius,
                    "keyword": variant,
                }
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

                status = data.get('status')
                if status == 'REQUEST_DENIED':
                    google_denied = True
                    print(f"Google Places API denied for keyword '{keyword}': {data.get('error_message', 'Unknown API error')}")
                    break

                if status not in {'ZERO_RESULTS', 'OK'}:
                    error_msg = data.get('error_message', 'Unknown API error')
                    print(f"Google Places API error: {status} - {error_msg}")

            if google_denied:
                break

        # Immediate fallback: provide a direct maps search instead of timing out.
        fallback_query = quote_plus(search_variants[0])
        fallback_maps_url = f"https://www.google.com/maps/search/?api=1&query={fallback_query}"
        print(f"No verified places found for keyword: {keyword}; returning maps search fallback")
        return search_variants[0], f"Search maps for {search_variants[0]}", fallback_maps_url
    except requests.RequestException as e:
        print(f"Network error fetching places for keyword '{keyword}': {e}")
        fallback_query = quote_plus(search_variants[0])
        fallback_maps_url = f"https://www.google.com/maps/search/?api=1&query={fallback_query}"
        return search_variants[0], f"Search maps for {search_variants[0]}", fallback_maps_url
    except Exception as e:
        print(f"Unexpected error fetching places for keyword '{keyword}': {e}")
        fallback_query = quote_plus(search_variants[0])
        fallback_maps_url = f"https://www.google.com/maps/search/?api=1&query={fallback_query}"
        return search_variants[0], f"Search maps for {search_variants[0]}", fallback_maps_url

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
