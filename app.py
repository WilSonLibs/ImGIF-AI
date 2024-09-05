import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# API key
api_key = 'f34e592e904e268c392f5c6cb622d649'

def get_weather(location):
    """Fetch weather data for a given location using OpenWeatherMap API."""
    try:
        full_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={api_key}"
        print(f"Full URL: {full_url}")  # Debugging print

        response = requests.get(full_url)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes

        weather_data = response.json()
        print(f"API response: {weather_data}")  # Debugging print

        # Check if the location was found
        if weather_data.get('cod') == 200:
            weather_description = weather_data['weather'][0]['description']
            temp = round(weather_data['main']['temp'])
            return weather_description, temp
        else:
            print(f"Location not found: {weather_data.get('message')}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None  # Initialize the variable to store weather data

    if request.method == 'POST':
        # Get the area location from the form
        location = request.form['location']
        weather, temp = get_weather(location)  # Fetch weather data using the function

        if weather is not None and temp is not None:
            data = f"The weather in {location} is {weather} and the temperature is around {temp}°F."
        else:
            data = "Error: Unable to fetch weather data for this location. Please check the location name and try again."
        
        # Redirect to the home page with data to refresh the form
        return redirect(url_for('index'))

    # Render the HTML template and pass the data variable
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
