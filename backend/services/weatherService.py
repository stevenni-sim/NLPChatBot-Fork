import requests
from fastapi import HTTPException
from datetime import datetime
import pytz
import dateparser
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
# Specify the path to your .env file
env_path = os.path.join(os.path.dirname(__file__), "../.env")  # Adjust the relative path to your .env file
load_dotenv(dotenv_path=env_path)

# Get the OpenWeather API key from the environment variables
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def fetch_weather_data(lat: float, lon: float, timestamp: int):
    """
    Fetch weather data from OpenWeather API for the given timestamp.
    """
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "dt": timestamp,
        "appid": OPENWEATHER_API_KEY,  # Use the key defined above
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract daily forecast data
        daily_forecast = data.get("daily", [])
        if not daily_forecast:
            return {"error": "No daily forecast data available."}

        # Find the forecast closest to the given timestamp
        forecast = next(
            (day for day in daily_forecast if abs(day["dt"] - timestamp) < 86400),
            None,
        )

        if not forecast:
            return {"error": "Weather data not available for the specified date."}

        # Extract weather details
        avg_temp = forecast["temp"]["day"]
        min_temp = forecast["temp"]["min"]
        max_temp = forecast["temp"]["max"]
        rain = forecast.get("rain", 0)
        description = forecast["weather"][0]["description"]
        icon_code = forecast["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"

        # Format the forecast date
        forecast_date = datetime.utcfromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")

        return {
            "average_temp": avg_temp,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "total_rainfall": rain,
            "description": description,
            "icon": icon_url,
            "date": forecast_date,
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching weather data: {str(e)}"
        )

def convert_to_local_timestamp(date_phrase: str, timezone: str = "Asia/Singapore") -> int:
    #Convert a date phrase (e.g., "Tuesday") to a local timestamp.
    try:
        # Define the local time zone
        local_tz = pytz.timezone(timezone)

        # Get the current date in the local time zone
        today = datetime.now(local_tz)

        # Parse the date phrase relative to today
        parsed_date = dateparser.parse(
            date_phrase,
            settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": today},
        )

        if not parsed_date:
            raise ValueError(f"Unable to parse date phrase: {date_phrase}")

        # Localize the parsed date and convert to a Unix timestamp
        localized_date = local_tz.localize(parsed_date)
        return int(localized_date.timestamp())

    except Exception as e:
        raise ValueError(f"Error converting date phrase to timestamp: {e}")