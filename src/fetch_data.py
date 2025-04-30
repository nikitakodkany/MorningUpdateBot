import requests
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Any
import time

class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.news_api_key = config['api_keys']['news']

    def fetch_weather(self) -> Dict[str, Any]:
        """Fetch weather data for the configured city using Open-Meteo API."""
        try:
            # First, get coordinates for the city using Open-Meteo's Geocoding API
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            geocoding_params = {
                'name': self.config['city'],
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            geocoding_response = requests.get(geocoding_url, params=geocoding_params)
            geocoding_data = geocoding_response.json()
            
            if not geocoding_data.get('results'):
                raise ValueError(f"Could not find coordinates for city: {self.config['city']}")
            
            location = geocoding_data['results'][0]
            latitude = location['latitude']
            longitude = location['longitude']
            
            # Now fetch weather data using the coordinates
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'timezone': 'auto'
            }
            
            weather_response = requests.get(weather_url, params=weather_params)
            weather_data = weather_response.json()
            
            # Map weather codes to descriptions
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Foggy",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow",
                73: "Moderate snow",
                75: "Heavy snow",
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
            
            current = weather_data['current']
            weather_code = current['weather_code']
            
            return {
                'location': self.config['city'],
                'temperature': current['temperature_2m'],
                'conditions': weather_codes.get(weather_code, "Unknown"),
                'humidity': current['relative_humidity_2m'],
                'wind_speed': current['wind_speed_10m']
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {}

    def fetch_stocks(self) -> Dict[str, Dict[str, float]]:
        """Return mock stock data for demonstration."""
        try:
            # Mock data with realistic values
            mock_data = {
                'TSLA': {'price': 168.29, 'change': 1.45},
                'AAPL': {'price': 169.89, 'change': -0.75},
                'AMZN': {'price': 179.55, 'change': 2.15}
            }
            
            stocks_data = {}
            for symbol in self.config['stocks']:
                if symbol in mock_data:
                    stocks_data[symbol] = mock_data[symbol]
            return stocks_data
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return {}

    def fetch_news(self) -> List[Dict[str, str]]:
        """Fetch top news headlines."""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'us',
                'apiKey': self.news_api_key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return [{
                'title': article['title'],
                'description': article.get('description', '')
            } for article in data['articles'][:5]]
        except Exception as e:
            print(f"Error fetching news data: {e}")
            return []

    def fetch_sports(self) -> Dict[str, List[Dict[str, str]]]:
        """Return mock sports data since we don't have a free sports API."""
        try:
            # Mock data for demonstration
            mock_data = {
                'nba': [
                    {'summary': 'GSW vs LAL: Warriors won 120-115'},
                    {'summary': 'BOS vs MIA: Celtics won 108-102'}
                ],
                'nfl': [
                    {'summary': 'SF vs SEA: 49ers won 31-13'},
                    {'summary': 'KC vs BAL: Chiefs won 17-10'}
                ]
            }
            return mock_data
        except Exception as e:
            print(f"Error fetching sports data: {e}")
            return {} 