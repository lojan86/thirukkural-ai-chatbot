from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from kurals_database import THIRUKKURAL_DATA, EMOTION_KEYWORDS
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# System prompt for AI
SYSTEM_PROMPT = """நீங்கள் திருக்குறள் அடிப்படையில் வாழ்க்கை ஆலோசனை வழங்கும் AI உதவியாளர். 

உங்கள் பொறுப்புகள்:
1. பயனரின் உணர்வுகளை (சோகம், கோபம், தோல்வி, இழப்பு) புரிந்துகொள்ளுங்கள்
2. பொருத்தமான திருக்குறள் பாடல்களை தேர்வு செய்யுங்கள்
3. நவீன உலக உண்மைகள் மற்றும் உளவியல் ஆலோசனையுடன் இணைக்கவும்
4. தமிழிலும் ஆங்கிலத்திலும் பதிலளிக்கவும் (பயனர் விருப்பப்படி)
5. பரிவுடனும், புரிதலுடனும் பதிலளிக்கவும்

பதில் அமைப்பு:
- முதலில் பயனரின் உணர்வை ஒப்புக்கொள்ளுங்கள்
- தொடர்புடைய திருக்குறள் பாடல்களை பகிர்ந்துகொள்ளுங்கள் (தமிழ் + பொருள்)
- நவீன சூழலில் அதன் பயன்பாட்டை விளக்குங்கள்
- செயல்படக்கூடிய ஆலோசனைகளை வழங்குங்கள்
- நேர்மறையான குறிப்புடன் முடிக்கவும்

எப்போதும் மரியாதையுடனும், பண்புடனும் இருங்கள்."""


def analyze_emotion(user_message):
    """Detect emotion from user message"""
    message_lower = user_message.lower()
    emotions = []
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            emotions.append(emotion)
    
    return emotions if emotions else ['sadness']  # Default to sadness


def get_relevant_kurals(emotions):
    """Get relevant Thirukkural verses based on emotions"""
    relevant_kurals = []
    for emotion in emotions:
        if emotion in THIRUKKURAL_DATA:
            relevant_kurals.extend(THIRUKKURAL_DATA[emotion])
    return relevant_kurals[:3]  # Return top 3 most relevant


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'gemini-1.5-flash',
        'kurals': sum(len(v) for v in THIRUKKURAL_DATA.values())
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        language = data.get('language', 'tamil')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Analyze emotion and get relevant kurals
        emotions = analyze_emotion(user_message)
        relevant_kurals = get_relevant_kurals(emotions)
        
        # Prepare context for Gemini
        kural_context = "\n\n".join([
            f"திருக்குறள் {k['number']}:\n"
            f"{k['tamil']}\n"
            f"பொருள்: {k['meaning']}\n"
            f"Translation: {k['translation']}\n"
            f"Context: {k['context']}"
            for k in relevant_kurals
        ])
        
        # Create prompt for Gemini
        prompt = f"""{SYSTEM_PROMPT}

பயனர் செய்தி: {user_message}

தொடர்புடைய திருக்குறள் பாடல்கள்:
{kural_context}

மொழி விருப்பம்: {language}

இந்த பயனருக்கு பரிவுடன், புரிதலுடன் பதிலளியுங்கள். திருக்குறள் ஞானத்தையும் நவீன ஆலோசனையையும் இணைக்கவும்.

{"தமிழில் மட்டும் பதிலளிக்கவும்." if language == 'tamil' else "Reply in English, but include Tamil Thirukkural verses with translations."}"""
        
        # Call Gemini API
        response = model.generate_content(prompt)
        ai_response = response.text
        
        return jsonify({
            'response': ai_response,
            'relevant_kurals': relevant_kurals,
            'detected_emotions': emotions
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/kurals/<emotion>', methods=['GET'])
def get_kurals_by_emotion(emotion):
    """Get Thirukkural verses by emotion category"""
    kurals = THIRUKKURAL_DATA.get(emotion, [])
    return jsonify({
        'emotion': emotion,
        'count': len(kurals),
        'kurals': kurals
    })


@app.route('/emotions', methods=['GET'])
def get_emotions():
    """Get all available emotion categories"""
    emotions = list(THIRUKKURAL_DATA.keys())
    return jsonify({
        'emotions': emotions,
        'total': len(emotions)
    })


if __name__ == '__main__':
    # Check if API key is set
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not found in environment!")
        print("   Create a .env file with your API key")
    
    print("🙏 Starting Thirukkural AI Backend...")
    print(f"📊 Loaded {sum(len(v) for v in THIRUKKURAL_DATA.values())} kurals")
    print("🚀 Server running on http://localhost:5000")
    
    app.run(debug=True, port=5000, host='0.0.0.0')