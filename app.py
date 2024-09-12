
import requests
from flask import Flask, render_template, request
import base64
import random

app = Flask(__name__)

# API keys for weather, images, and audio
weather_api_key = 'f34e592e904e268c392f5c6cb622d649'
unsplash_access_key = 'wefY-JAWTnZUoVNcKJscWENryeTi7CSYuOU16G1fH4w'
huggingface_api_key = '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'

def get_weather(location):
    """Fetch weather data for a given location using OpenWeatherMap API."""
    try:
        full_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={weather_api_key}"
        response = requests.get(full_url)
        response.raise_for_status()
        weather_data = response.json()

        if weather_data.get('cod') == 200:
            weather_description = weather_data['weather'][0]['description']
            temp = round(weather_data['main']['temp'])
            humidity = weather_data['main']['humidity']
            wind_speed = round(weather_data['wind']['speed'])
            
            # Precipitation data is available under 'rain' or 'snow' keys depending on the weather
            precipitation = weather_data.get('rain', {}).get('1h', 0) or weather_data.get('snow', {}).get('1h', 0)

            return weather_description, temp, humidity, wind_speed, precipitation, weather_data['weather'][0]['main']
        else:
            return None, None, None, None, None, None
    except requests.exceptions.RequestException as e:
        return None, None, None, None, None, None

# @app.route('/new_image', methods=['GET'])
# def new_image():
#     location = request.args.get('location')
#     if location:
#         image_urls = get_city_image(location)
#         if image_urls:
#             return {'image_url': image_urls[0]}  # Return the first image URL from the list
#     return {'image_url': None}


def get_city_image(location):
    """Fetch city image from Unsplash API."""
    url = f"https://api.unsplash.com/search/photos?query={location}&client_id={unsplash_access_key}"
    try:
        response = requests.get(url)
        data = response.json()
        image_urls = [img['urls']['regular'] for img in data['results']]
        return image_urls
    except Exception as e:
        return []

# def get_weather_audio(weather_condition):
#     """Return a weather-based audio URL."""
#     weather_sounds = {
#         'Rain': 'rain-sound.mp3',
#         'Clear': 'clear-day.mp3',
#         'Snow': 'snow-sound.mp3',
#         'Clouds': 'cloudy-sound.mp3',
#     }
#     return weather_sounds.get(weather_condition, 'default-sound.mp3')

def get_suggestions(weather_condition, temp):
    """Generate suggestions using Hugging Face API."""
    huggingface_url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {
        'Authorization': f'Bearer {huggingface_api_key}',
        'Content-Type': 'application/json'
    }
    
    # Sample prompt for the Hugging Face model
    prompt = f"The weather is {weather_condition} with a temperature of {temp}°C. Suggest clothing, activities, and whether it is suitable for a picnic."
    
    response = requests.post(huggingface_url, headers=headers, json={"inputs": prompt})
    
    if response.status_code == 200:
        suggestions = response.json()[0]['generated_text']
        return suggestions
    else:
        return "Sorry, unable to generate suggestions at the moment."

def text_to_speech(text):
    """Convert text to speech using Hugging Face API."""
    tts_url = "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
    headers = {
        'Authorization': f'Bearer {huggingface_api_key}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(tts_url, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        audio_content = response.content
        return base64.b64encode(audio_content).decode('utf-8')
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    image_urls = None
    audio_file = None
    suggestions = None
    location = None
    temp = None
    precipitation = None
    humidity = None
    wind_speed = None
    weather_description = None
    tts_audio = ""

    if request.method == 'POST':
        location = request.form['location']
        weather_description, temp, humidity, wind_speed, precipitation, weather_condition = get_weather(location)

        if weather_description is not None and temp is not None:
            # Fetch city images
            image_urls = get_city_image(location)

            # Get weather-based audio
            # audio_file = get_weather_audio(weather_condition)

            # Get suggestions for clothing, activities, etc.
            suggestions = get_suggestions(weather_description, temp)

            # Convert suggestions to speech using Hugging Face
            tts_audio = text_to_speech(suggestions)

            data = f"The weather in {location} is {weather_description} and the temperature is around {temp}°C."
        else:
            data = "Error: Unable to fetch weather data for this location."

    return render_template('index.html', data=data, location=location, temp=temp, 
                           precipitation=precipitation, humidity=humidity, 
                           wind_speed=wind_speed, weather_description=weather_description, 
                           image_urls=image_urls, audio_file=audio_file, 
                           suggestions=suggestions, tts_audio=tts_audio)


if __name__ == '__main__':
    app.run(debug=True)