import google.generativeai as genai
import os
from typing import Dict, Any
import speech_recognition as sr
from PIL import Image

class GeminiAIService:
    def __init__(self):
        # Try to get from environment
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Temporary: Set your API key directly for testing
        if not api_key:
            api_key = "AIzaSyBR8jfBfIryapJHEfvsqFjYNY73v4kEG7Q"  # Replace with your real key
        
        if not api_key or api_key.startswith("AIzaSyYour_"):
            raise ValueError("Please set a valid GEMINI_API_KEY!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def get_farming_advice(self, query: str, location: str, weather_data: Dict[str, Any]) -> str:
        """Generate farming advice using free Gemini API"""
        try:
            weather_context = ""
            if weather_data and 'error' not in weather_data:
                weather_context = f"""
                Current weather in {location}:
                - Temperature: {weather_data.get('temperature', 'N/A')}°C
                - Humidity: {weather_data.get('humidity', 'N/A')}%
                - Conditions: {weather_data.get('description', 'N/A')}
                - Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s
                """
            
            prompt = f"""You are KisanSahayak AI, an expert farming assistant for Indian farmers. 
            Provide practical, actionable farming advice in simple language. Consider local conditions, 
            seasonal factors, and traditional Indian farming practices. Respond in both Hindi and English 
            when appropriate. Focus on cost-effective solutions suitable for small to medium farmers.
            
            Location: {location}
            {weather_context}
            
            Farmer's Question: {query}
            
            Please provide detailed farming advice considering the current weather conditions and location.
            Give specific, practical recommendations that farmers can implement easily."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating farming advice: {str(e)}"
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using free Google Speech Recognition"""
        try:
            recognizer = sr.Recognizer()
            
            # Convert audio file to WAV if needed
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
            
            # Use free Google Speech Recognition with Hindi support
            text = recognizer.recognize_google(audio_data, language='hi-IN')
            return text
            
        except sr.UnknownValueError:
            return "Could not understand the audio. Please speak clearly and try again."
        except sr.RequestError as e:
            return f"Speech recognition service error: {str(e)}"
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
    
    async def analyze_crop_image(self, image_path: str) -> Dict[str, str]:
        """Analyze crop image using free Gemini Vision"""
        try:
            # Load and validate image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            prompt = """Analyze this crop image carefully and provide a detailed assessment:

            1. **Crop Identification**: What type of crop is this? (wheat, rice, cotton, etc.)
            
            2. **Health Status**: Assess the overall health of the plant:
               - Healthy/Good condition
               - Fair condition with minor issues
               - Poor condition with significant problems
            
            3. **Pest and Disease Detection**: Look for signs of:
               - Insect damage (holes in leaves, chewed edges)
               - Fungal infections (spots, discoloration, wilting)
               - Viral or bacterial diseases
               - Nutrient deficiencies
            
            4. **Specific Recommendations**: Provide actionable advice:
               - Immediate treatments needed
               - Organic/chemical control options
               - Preventive measures
               - Irrigation and fertilization recommendations
            
            5. **Cost-effective Solutions**: Focus on affordable treatments suitable for Indian farmers.
            
            Please provide practical advice in simple language that farmers can easily understand and implement."""
            
            # Use Gemini Vision (completely free!)
            response = self.vision_model.generate_content([prompt, image])
            
            return {
                "pest_type": "Gemini AI Crop Analysis",
                "treatment": response.text,
                "confidence": "AI Vision Analysis"
            }
            
        except FileNotFoundError:
            return {
                "pest_type": "File Error",
                "treatment": "Could not find the uploaded image file. Please try uploading again.",
                "confidence": "Low"
            }
        except Exception as e:
            return {
                "pest_type": "Analysis Error",
                "treatment": f"Error analyzing crop image: {str(e)}. Please ensure the image is clear and try again.",
                "confidence": "Low"
            }
    
    def get_crop_calendar(self, location: str, crop: str) -> str:
        """Get crop calendar information for specific location and crop"""
        try:
            prompt = f"""Provide a detailed crop calendar for {crop} cultivation in {location}, India.
            
            Include:
            1. **Best planting time** (months)
            2. **Soil preparation** timeline
            3. **Sowing/transplanting** period
            4. **Key growth stages** and their timing
            5. **Harvesting time**
            6. **Weather considerations** for each stage
            7. **Regional variations** if any
            
            Make it practical for Indian farmers."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting crop calendar: {str(e)}"
    
    def get_market_advice(self, crop: str, location: str) -> str:
        """Get market and pricing advice for crops"""
        try:
            prompt = f"""Provide market and pricing guidance for {crop} farmers in {location}, India:
            
            1. **Best selling time** for maximum profit
            2. **Storage techniques** to extend shelf life
            3. **Quality parameters** that affect pricing
            4. **Local market channels** (mandis, direct sales, online platforms)
            5. **Value addition opportunities**
            6. **Government schemes** and support available
            
            Focus on practical tips to help farmers get better prices."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting market advice: {str(e)}"
    
    def get_organic_solutions(self, problem: str, crop: str) -> str:
        """Get organic farming solutions"""
        try:
            prompt = f"""Provide organic and natural solutions for this farming problem:
            
            Problem: {problem}
            Crop: {crop}
            
            Please suggest:
            1. **Organic treatments** using locally available materials
            2. **Home-made sprays** and their preparation
            3. **Beneficial insects** and biological control
            4. **Companion planting** strategies
            5. **Soil health improvement** methods
            6. **Prevention techniques** for future
            
            Focus on cost-effective, environment-friendly solutions."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting organic solutions: {str(e)}"
