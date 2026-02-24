# Legal Task Management Application

A smart Flask-based web application that helps users find and understand legal/government tasks and procedures. The application provides intelligent search capabilities using AI and helps users locate nearby offline centers for document processing.

## Features

- **AI-Powered Search**: Natural language processing using Google's Gemini AI to understand user queries
- **Fuzzy Matching**: Smart task matching even with typos or variations in search terms
- **Location Services**: Find nearest offline centers using Google Places API
- **Comprehensive Task Database**: Detailed information about various legal/government procedures
- **Multi-Modal Applications**: Support for both online and offline application processes
- **Document Requirements**: Clear listing of required documents for each task
- **Step-by-Step Guidance**: Detailed application steps for each procedure

## Supported Tasks

The application includes comprehensive information for various legal and government tasks including:
- Aadhaar Card Registration
- PAN Card Application
- Marriage Registration
- Passport Application
- Driving License Application
- Company Registration (Private Limited)
- GST Registration
- And many more...

## Requirements

- Python 3.7+
- Flask 2.3.3
- Google Gemini AI API access
- Google Places API access (for location services)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Yashwatts/documentation-pathway.git
cd legal-Task-Management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API keys:
```bash
GOOGLE_API_KEY=your_google_places_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

- `GET /` - Home page with task listing
- `POST /task` - Get specific task details
- `POST /find_centers` - Find nearest offline centers
- `POST /nlp_search` - AI-powered natural language search

## Project Structure

```
├── app.py              # Main Flask application with AI integration
├── requirements.txt    # Python dependencies
├── tasks.json         # Comprehensive task database (2000+ lines)
├── .env.example       # Environment variables template
├── static/            # Frontend assets
│   ├── style.css      # Styling
│   ├── script.js      # Core JavaScript functionality
│   └── enhanced.js    # Enhanced UI features
├── templates/         # Jinja2 HTML templates
│   ├── index.html     # Main interface
│   └── task_details.html # Task detail view
└── utils/             # Helper functions
    ├── __init__.py
    └── helper.py      # Task management and Google API utilities
```

## Key Technologies

- **Backend**: Flask (Python)
- **AI/ML**: Google Gemini AI for natural language processing
- **Location Services**: Google Places API
- **Text Matching**: FuzzyWuzzy for approximate string matching
- **Frontend**: Vanilla JavaScript with enhanced UI features
- **Data Storage**: JSON-based task database

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: Google Places API Key for location services
GOOGLE_API_KEY=your_google_places_api_key_here

# Required: Gemini AI API Key for intelligent search
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Flask secret key for sessions
FLASK_SECRET_KEY=your_secret_key_here
```

## Usage Examples

The application supports various query formats:
- "I want to make my Aadhaar card" → Aadhaar Card Registration
- "company registration" → Private Limited Company Registration
- "apply for pan card" → PAN Card Application
- "marriage registration" → Marriage Registration