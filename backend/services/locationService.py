import requests
from typing import List, Dict, Optional
from fastapi import HTTPException
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
# Specify the path to your .env file
env_path = os.path.join(os.path.dirname(__file__), "../.env")  # Adjust the relative path to your .env file
load_dotenv(dotenv_path=env_path)

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Foursquare API configuration
FOURSQUARE_API_URL = os.getenv("FOURSQUARE_API_URL")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
FOURSQUARE_HEADERS = {
    "Accept": "application/json",
    "Authorization": FOURSQUARE_API_KEY,
}

# --- Google Maps API Functions ---

def get_google_maps_directions(lat: float, long: float, destination: str) -> str:
    """
    Generate a Google Maps embed URL for directions.
    """
    try:
        destination_with_context = f"{destination}, Singapore"
        return (
            f"https://www.google.com/maps/embed/v1/directions?key={GOOGLE_MAPS_API_KEY}"
            f"&origin={lat},{long}&destination={destination_with_context}&mode=driving"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Google Maps URL: {e}")


# --- Foursquare API Functions ---
def get_allinfo(latitude,longitude,query):
    radius = 2500  
    limit = 20  
    params = {
        "query": query,
        "ll": f"{latitude},{longitude}",
        "radius": radius,
        "limit": limit
    }
   
    response = requests.get(FOURSQUARE_API_URL, headers=FOURSQUARE_HEADERS, params=params)
    
    try:
        response = requests.get(FOURSQUARE_API_URL, headers=FOURSQUARE_HEADERS, params=params)


        if response.status_code == 200:
            return response.json()  
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

    except requests.exceptions.RequestException as e:
      
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    



def search_foursquare_nearby(
    latitude: float, 
    longitude: float, 
    query: str = "restaurant", 
    radius: int = 2500, 
    limit: int = 20) -> List[Dict]:
    
    #Search for nearby places using the Foursquare API.
    
    try:
        params = {
            "ll": f"{latitude},{longitude}",
            "query": query,
            "radius": radius,
            "limit": limit,
        }
        response = requests.get(FOURSQUARE_API_URL, headers=FOURSQUARE_HEADERS, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Foursquare data: {e}")


def format_foursquare_response(results: List[Dict]) -> List[Dict]:
    """
    Format the Foursquare response into a user-friendly structure.
    """
    try:
        return [
            {
                "name": place.get("name", "Unknown"),
                "distance": f"{place.get('distance', 'Unknown')} meters",
                "latitude": place.get("geocodes", {}).get("main", {}).get("latitude", "Unknown"),
                "longitude": place.get("geocodes", {}).get("main", {}).get("longitude", "Unknown"),
            }
            for place in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting Foursquare response: {e}")

