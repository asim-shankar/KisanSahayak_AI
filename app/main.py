from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
import traceback
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="KisanSahayak AI - Enhanced Dashboard", version="2.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize AI services
try:
    from .gemini_service import GeminiAIService
    gemini_service = GeminiAIService()
    print("✅ Gemini AI service initialized")
except Exception as e:
    print(f"❌ Gemini AI service error: {e}")
    gemini_service = None

try:
    from .weather_service import get_weather_data
    print("✅ Weather service loaded")
except Exception as e:
    print(f"❌ Weather service error: {e}")

# ==================== CROP DATABASE ====================

CROPS_DATABASE = [
    {
        "id": 1,
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "type": "Kharif",
        "category": "Cereal",
        "ideal_conditions": {
            "temperature": "25-35°C",
            "rainfall": "100-200 cm",
            "soil": "Alluvial, clayey",
            "humidity": "High"
        },
        "major_states": ["West Bengal", "Punjab", "Uttar Pradesh", "Andhra Pradesh"],
        "growing_season": "June-November",
        "pest_diseases": ["Brown planthopper", "Blast disease", "Bacterial blight"],
        "description": "Rice is the staple food crop of India and requires high water availability.",
        "image": "https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=Rice"
    },
    {
        "id": 2,
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "type": "Rabi",
        "category": "Cereal",
        "ideal_conditions": {
            "temperature": "17-20°C",
            "rainfall": "20-100 cm", 
            "soil": "Alluvial, loamy",
            "humidity": "Moderate"
        },
        "major_states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh"],
        "growing_season": "October-April",
        "pest_diseases": ["Aphids", "Rust diseases", "Smut"],
        "description": "Wheat is the second most important cereal crop in India.",
        "image": "https://via.placeholder.com/300x200/F4A460/FFFFFF?text=Wheat"
    },
    {
        "id": 3,
        "name": "Maize",
        "scientific_name": "Zea mays",
        "type": "Kharif",
        "category": "Cereal",
        "ideal_conditions": {
            "temperature": "21-27°C",
            "rainfall": "50-100 cm",
            "soil": "Well-drained loamy",
            "humidity": "Moderate to high"
        },
        "major_states": ["Karnataka", "Andhra Pradesh", "Tamil Nadu", "Rajasthan"],
        "growing_season": "June-October",
        "pest_diseases": ["Fall armyworm", "Stem borer", "Leaf blight"],
        "description": "Known as the 'Queen of Cereals' due to its high yield potential.",
        "image": "https://via.placeholder.com/300x200/FFD700/FFFFFF?text=Maize"
    },
    {
        "id": 4,
        "name": "Cotton",
        "scientific_name": "Gossypium spp.",
        "type": "Kharif",
        "category": "Fiber",
        "ideal_conditions": {
            "temperature": "21-30°C",
            "rainfall": "60-120 cm",
            "soil": "Black cotton soil",
            "humidity": "Moderate"
        },
        "major_states": ["Maharashtra", "Gujarat", "Telangana", "Karnataka"],
        "growing_season": "April-October",
        "pest_diseases": ["Bollworm", "Aphids", "Whitefly"],
        "description": "Cotton is known as 'White Gold' and is a major cash crop.",
        "image": "https://via.placeholder.com/300x200/FFFFFF/4CAF50?text=Cotton"
    },
    {
        "id": 5,
        "name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "type": "Cash Crop",
        "category": "Sugar",
        "ideal_conditions": {
            "temperature": "20-26°C",
            "rainfall": "75-150 cm",
            "soil": "Rich alluvial",
            "humidity": "High"
        },
        "major_states": ["Uttar Pradesh", "Maharashtra", "Punjab", "Tamil Nadu"],
        "growing_season": "February-November",
        "pest_diseases": ["Red rot", "Smut", "Scale insects"],
        "description": "Sugarcane is the main source of sugar production in India.",
        "image": "https://via.placeholder.com/300x200/90EE90/FFFFFF?text=Sugarcane"
    },
    {
        "id": 6,
        "name": "Tea",
        "scientific_name": "Camellia sinensis",
        "type": "Plantation",
        "category": "Beverage",
        "ideal_conditions": {
            "temperature": "20-30°C",
            "rainfall": "150-300 cm",
            "soil": "Acidic, well-drained",
            "humidity": "High"
        },
        "major_states": ["Assam", "West Bengal", "Kerala", "Tamil Nadu"],
        "growing_season": "Year-round",
        "pest_diseases": ["Tea mosquito bug", "Red spider mite", "Blister blight"],
        "description": "Tea is a major plantation crop and export commodity.",
        "image": "https://via.placeholder.com/300x200/228B22/FFFFFF?text=Tea"
    },
    {
        "id": 7,
        "name": "Pulses",
        "scientific_name": "Various Legumes",
        "type": "Kharif/Rabi",
        "category": "Legume",
        "ideal_conditions": {
            "temperature": "20-30°C",
            "rainfall": "25-75 cm",
            "soil": "Well-drained loamy",
            "humidity": "Moderate"
        },
        "major_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka"],
        "growing_season": "Both seasons",
        "pest_diseases": ["Pod borer", "Aphids", "Wilt disease"],
        "description": "Pulses are protein-rich crops essential for nutrition.",
        "image": "https://via.placeholder.com/300x200/DEB887/FFFFFF?text=Pulses"
    },
    {
        "id": 8,
        "name": "Millets",
        "scientific_name": "Various species",
        "type": "Kharif",
        "category": "Cereal",
        "ideal_conditions": {
            "temperature": "25-35°C",
            "rainfall": "25-75 cm",
            "soil": "Sandy, well-drained",
            "humidity": "Low to moderate"
        },
        "major_states": ["Rajasthan", "Maharashtra", "Gujarat", "Karnataka"],
        "growing_season": "June-October",
        "pest_diseases": ["Shoot fly", "Stem borer", "Downy mildew"],
        "description": "Millets are drought-resistant and highly nutritious.",
        "image": "https://via.placeholder.com/300x200/CD853F/FFFFFF?text=Millets"
    }
]

# Pydantic Models
class SearchQuery(BaseModel):
    query: str

class WeatherRequest(BaseModel):
    location: str

# ==================== SERVE DASHBOARD ====================

@app.get("/")
async def serve_dashboard():
    """Serve the enhanced dashboard"""
    try:
        html_path = os.path.join("frontend", "index.html")
        if os.path.exists(html_path):
            return FileResponse(html_path)
        else:
            return JSONResponse({"error": "Dashboard not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": f"Dashboard error: {str(e)}"}, status_code=500)

# ==================== NEW CROP SEARCH API ====================

@app.post("/search-crops")
async def search_crops(search_request: SearchQuery):
    """Search crops in the database"""
    try:
        query = search_request.query.lower()
        results = []
        
        for crop in CROPS_DATABASE:
            # Search in name, category, type, and description
            if (query in crop['name'].lower() or 
                query in crop['category'].lower() or
                query in crop['type'].lower() or
                query in crop['description'].lower() or
                any(query in state.lower() for state in crop['major_states'])):
                results.append(crop)
        
        return {
            "results": results,
            "total_found": len(results),
            "query": search_request.query,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/crops")
async def get_all_crops():
    """Get all crops in the database"""
    return {
        "crops": CROPS_DATABASE,
        "total_crops": len(CROPS_DATABASE),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/crops/{crop_id}")
async def get_crop_details(crop_id: int):
    """Get detailed information about a specific crop"""
    crop = next((c for c in CROPS_DATABASE if c['id'] == crop_id), None)
    if crop:
        return crop
    else:
        raise HTTPException(status_code=404, detail="Crop not found")

# ==================== ENHANCED WEATHER API ====================

@app.post("/weather-conditions")
async def get_weather_conditions(weather_request: WeatherRequest):
    """Get detailed weather conditions for farming"""
    try:
        weather_data = get_weather_data(weather_request.location)
        
        if 'error' in weather_data:
            return {
                "location": weather_request.location,
                "error": weather_data['error'],
                "fallback_advice": "Check local weather conditions manually",
                "timestamp": datetime.now().isoformat()
            }
        
        # Enhanced weather analysis for farming
        temp = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        
        farming_advice = []
        suitable_crops = []
        
        # Crop recommendations based on weather
        for crop in CROPS_DATABASE:
            ideal_temp = crop['ideal_conditions']['temperature']
            # Simple temperature range check
            if '25-35' in ideal_temp and 25 <= temp <= 35:
                suitable_crops.append(crop['name'])
            elif '20-30' in ideal_temp and 20 <= temp <= 30:
                suitable_crops.append(crop['name'])
        
        # Farming advice based on conditions
        if temp > 35:
            farming_advice.append("🌡️ High temperature: Increase irrigation frequency")
        if humidity > 80:
            farming_advice.append("💧 High humidity: Monitor for fungal diseases")
        if temp < 15:
            farming_advice.append("❄️ Cool weather: Ideal for Rabi crops like wheat")
        
        return {
            "location": weather_request.location,
            "current_weather": weather_data,
            "farming_advice": farming_advice,
            "suitable_crops": suitable_crops[:5],  # Top 5 recommendations
            "weather_alerts": [],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENHANCED IMAGE UPLOAD API ====================

@app.post("/analyze-crop-image")
async def analyze_crop_image(image: UploadFile = File(...)):
    """Analyze uploaded crop image for crop type and pest detection"""
    try:
        if not gemini_service:
            return {
                "crop_detected": "Service unavailable",
                "pest_analysis": "AI analysis service is temporarily down",
                "recommendations": "Please try again later",
                "confidence": "N/A"
            }
        
        # Save uploaded image
        image_path = f"temp_crop_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Enhanced AI analysis
        analysis = await gemini_service.analyze_crop_image(image_path)
        
        # Additional processing - try to match with crop database
        detected_crops = []
        for crop in CROPS_DATABASE:
            if crop['name'].lower() in analysis.get('treatment', '').lower():
                detected_crops.append({
                    "name": crop['name'],
                    "type": crop['type'],
                    "category": crop['category']
                })
        
        # Clean up
        os.remove(image_path)
        
        return {
            "crop_detected": detected_crops[0]['name'] if detected_crops else "Unknown crop",
            "crop_matches": detected_crops,
            "pest_analysis": analysis.get('pest_type', 'Analysis completed'),
            "detailed_analysis": analysis.get('treatment', 'No specific issues detected'),
            "recommendations": analysis.get('treatment', 'Continue regular care'),
            "confidence": analysis.get('confidence', 'Medium'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "crop_detected": "Analysis failed",
            "pest_analysis": f"Error: {str(e)}",
            "recommendations": "Please try uploading a clearer image",
            "confidence": "Low",
            "timestamp": datetime.now().isoformat()
        }

# ==================== ENHANCED VOICE RECOGNITION ====================

@app.post("/voice-recognition")
async def voice_recognition(audio: UploadFile = File(...)):
    """Process voice input for farming queries"""
    try:
        if not gemini_service:
            return {
                "transcription": "Voice service unavailable",
                "farming_response": "AI voice processing is temporarily down",
                "suggested_crops": [],
                "status": "error"
            }
        
        # Save audio file
        audio_path = f"temp_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        with open(audio_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Transcribe audio
        transcription = await gemini_service.transcribe_audio(audio_path)
        
        # Generate farming response
        farming_response = await gemini_service.get_farming_advice(
            transcription,
            "India",
            {}
        )
        
        # Suggest relevant crops based on query
        query_lower = transcription.lower()
        suggested_crops = []
        for crop in CROPS_DATABASE:
            if (crop['name'].lower() in query_lower or 
                crop['category'].lower() in query_lower):
                suggested_crops.append({
                    "name": crop['name'],
                    "type": crop['type'],
                    "description": crop['description']
                })
        
        # Clean up
        os.remove(audio_path)
        
        return {
            "transcription": transcription,
            "farming_response": farming_response,
            "suggested_crops": suggested_crops[:3],  # Top 3 suggestions
            "audio_quality": "Good" if len(transcription) > 10 else "Poor",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "transcription": "Audio processing failed",
            "farming_response": f"Voice recognition error: {str(e)}",
            "suggested_crops": [],
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

# ==================== EXISTING ENDPOINTS (Enhanced) ====================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "🌾 Enhanced KisanSahayak AI Dashboard",
        "version": "2.1.0",
        "features": {
            "crop_database": f"{len(CROPS_DATABASE)} crops",
            "search_functionality": "active",
            "weather_conditions": "active", 
            "image_analysis": "active",
            "voice_recognition": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

print("🌱 Enhanced KisanSahayak AI Dashboard Starting...")
print(f"📊 Loaded {len(CROPS_DATABASE)} crops in database")
print("🔍 Search functionality: ACTIVE")
print("🌤️ Weather conditions: ACTIVE") 
print("📸 Image analysis: ACTIVE")
print("🎤 Voice recognition: ACTIVE")
print("✨ Dashboard ready at: http://localhost:8000/")
