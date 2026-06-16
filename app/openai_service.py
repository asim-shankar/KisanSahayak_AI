import google.generativeai as genai
import os
from typing import Dict, Any
import speech_recognition as sr
from PIL import Image

class GeminiAIService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Please set GEMINI_API_KEY in your .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Free model
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Same model for vision
    
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
            
            Please provide detailed farming advice considering the current weather conditions and location."""
            
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
                audio_data = recognizer.record(source)
            
            # Use free Google Speech Recognition with Hindi support
            text = recognizer.recognize_google(audio_data, language='hi-IN')
            return text
            
        except sr.UnknownValueError:
            return "Could not understand the audio. Please speak clearly."
        except sr.RequestError as e:
            return f"Speech recognition error: {str(e)}"
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
    
    async def analyze_crop_image(self, image_path: str) -> Dict[str, str]:
        """Analyze crop image using free Gemini Vision"""
        try:
            # Load image
            image = Image.open(image_path)
            
            prompt = """Analyze this crop image and identify:
            1. Crop type (if identifiable)
            2. Overall plant health status
            3. Any visible pests, diseases, or problems
            4. Specific farming recommendations and treatments
            5. Preventive measures for the future
            
            Provide practical advice suitable for Indian farmers in simple language.
            If you detect any issues, suggest both organic and conventional treatment options."""
            
            # Use Gemini Vision (completely free!)
            response = self.vision_model.generate_content([prompt, image])
            
            return {
                "pest_type": "Gemini Vision Analysis Complete",
                "treatment": response.text,
                "confidence": "AI Analysis"
            }
            
        except Exception as e:
            return {
                "pest_type": "Analysis Error",
                "treatment": f"Error analyzing crop image: {str(e)}",
                "confidence": "Low"
            }
