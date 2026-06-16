import requests
from typing import Dict, Any

def get_weather_data(location: str) -> Dict[str, Any]:
    """Get weather data using Open-Meteo (no API key needed)"""
    
    try:
        # Step 1: Get coordinates for the location
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {
            'name': location,
            'count': 1,
            'language': 'en'
        }
        
        geo_response = requests.get(geocode_url, params=geocode_params)
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return {'error': f'Location "{location}" not found'}
        
        # Get coordinates
        result = geo_data['results'][0]
        lat = result['latitude']
        lon = result['longitude']
        city_name = result['name']
        
        # Step 2: Get current weather data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'current': [
                'temperature_2m',
                'relative_humidity_2m', 
                'wind_speed_10m',
                'weather_code'
            ],
            'timezone': 'auto'
        }
        
        weather_response = requests.get(weather_url, params=weather_params)
        weather_data = weather_response.json()
        
        if 'current' not in weather_data:
            return {'error': 'Weather data not available'}
        
        current = weather_data['current']
        
        return {
            'location': city_name,
            'temperature': round(current['temperature_2m'], 1),
            'humidity': current['relative_humidity_2m'],
            'description': get_weather_description(current['weather_code']),
            'wind_speed': round(current['wind_speed_10m'], 1),
            'weather_code': current['weather_code']
        }
        
    except requests.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except KeyError as e:
        return {'error': f'Data parsing error: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def get_weather_description(code: int) -> str:
    """Convert Open-Meteo weather code to human-readable description"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle", 
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, f"Unknown weather (code: {code})")

def get_farming_recommendation(weather_data: dict, crop_type: str) -> str:
    """Generate farming recommendations based on weather"""
    if 'error' in weather_data:
        return "Weather data unavailable. Please check with local meteorological conditions."
    
    temp = weather_data.get('temperature', 0)
    humidity = weather_data.get('humidity', 0)
    weather_code = weather_data.get('weather_code', 0)
    
    recommendations = []
    
    # Temperature recommendations
    if temp > 35:
        recommendations.append(f"🌡️ High temperature alert ({temp}°C)! Increase irrigation for {crop_type}.")
    elif temp < 10:
        recommendations.append(f"❄️ Low temperature warning ({temp}°C). Protect {crop_type} from frost.")
    
    # Humidity recommendations  
    if humidity > 80:
        recommendations.append(f"💧 High humidity ({humidity}%). Monitor {crop_type} for fungal diseases.")
    elif humidity < 30:
        recommendations.append(f"🏜️ Low humidity ({humidity}%). Consider additional irrigation.")
    
    # Weather condition recommendations
    if weather_code in [61, 63, 65, 80, 81, 82]:  # Rain conditions
        recommendations.append(f"🌧️ Rainy conditions. Good for irrigation but watch for waterlogging.")
    elif weather_code in [95, 96, 99]:  # Thunderstorms
        recommendations.append(f"⛈️ Thunderstorm warning! Avoid field activities and secure equipment.")
    elif weather_code == 0:  # Clear sky
        recommendations.append(f"☀️ Clear weather conditions - ideal for field activities.")
    
    if not recommendations:
        recommendations.append(f"✅ Current weather conditions are suitable for {crop_type} cultivation.")
    
    return " ".join(recommendations)

# Optional: Add forecast functionality
def get_weather_forecast(location: str, days: int = 5) -> Dict[str, Any]:
    """Get weather forecast for farming planning"""
    try:
        # Geocode first
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {'name': location, 'count': 1}
        
        geo_response = requests.get(geocode_url, params=geocode_params)
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return {'error': f'Location "{location}" not found'}
        
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        
        # Get forecast
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        forecast_params = {
            'latitude': lat,
            'longitude': lon,
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min', 
                'precipitation_sum',
                'weather_code'
            ],
            'forecast_days': days,
            'timezone': 'auto'
        }
        
        response = requests.get(forecast_url, params=forecast_params)
        data = response.json()
        
        return {
            'location': location,
            'forecast': data['daily'],
            'units': data['daily_units']
        }
        
    except Exception as e:
        return {'error': f'Forecast error: {str(e)}'}
