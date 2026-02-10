#!/usr/bin/env python3

from datetime import datetime
from typing import Dict, Optional

import requests


class WeatherTracker:
    """Tracks weather using Open-Meteo API (free, no API key required)."""

    WEATHER_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
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
        99: "Thunderstorm with heavy hail",
    }

    def __init__(self, zip_code: str):
        self.zip_code = zip_code

    def _get_coordinates_from_zip(self) -> Optional[tuple]:
        """Convert US zip code to coordinates using Nominatim."""
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "postalcode": self.zip_code,
                    "country": "us",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "WeatherTracker/1.0"},
                timeout=10,
            )
            data = response.json()
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
            return None
        except Exception:
            return None

    def get_weather_forecast(self) -> Optional[Dict]:
        """Get today's weather forecast from Open-Meteo API."""
        coordinates = self._get_coordinates_from_zip()
        if not coordinates:
            return None

        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": coordinates[0],
                    "longitude": coordinates[1],
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch",
                    "timezone": "auto",
                    "forecast_days": 1,
                },
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def display(self):
        """Display current weather and today's forecast to console."""
        print(f"\n{'='*70}")
        print(f"Weather Forecast - ZIP {self.zip_code}")
        print(f"{'='*70}\n")

        data = self.get_weather_forecast()

        if not data:
            print(f"Unable to fetch weather data for ZIP code {self.zip_code}")
            print(f"{'='*70}\n")
            return

        # Current conditions
        if "current" in data:
            current = data["current"]
            print("CURRENT CONDITIONS")
            print(f"{'-'*70}")

            current_time = datetime.fromisoformat(
                current["time"].replace("Z", "+00:00")
            )
            print(f"Time:            {current_time.strftime('%I:%M %p')}")

            temp = current.get("temperature_2m")
            if temp is not None:
                print(f"Temperature:     {temp:.1f}°F")

            feels_like = current.get("apparent_temperature")
            if feels_like is not None:
                print(f"Feels Like:      {feels_like:.1f}°F")

            humidity = current.get("relative_humidity_2m")
            if humidity is not None:
                print(f"Humidity:        {humidity}%")

            weather_code = current.get("weather_code")
            if weather_code is not None:
                condition = self.WEATHER_CODES.get(
                    weather_code, f"Unknown ({weather_code})"
                )
                print(f"Conditions:      {condition}")

            precip = current.get("precipitation")
            if precip is not None:
                print(f"Precipitation:   {precip:.2f} in")

            wind_speed = current.get("wind_speed_10m")
            wind_direction = current.get("wind_direction_10m")
            if wind_speed is not None:
                wind_str = f"{wind_speed:.1f} mph"
                if wind_direction is not None:
                    wind_str += f" from {wind_direction:.0f}°"
                print(f"Wind:            {wind_str}")

            print()

        # Today's forecast
        if "daily" in data:
            daily = data["daily"]
            print("TODAY'S FORECAST")
            print(f"{'-'*70}")

            high = daily.get("temperature_2m_max", [None])[0]
            low = daily.get("temperature_2m_min", [None])[0]
            if high is not None and low is not None:
                print(f"High / Low:      {high:.1f}°F / {low:.1f}°F")

            weather_code = daily.get("weather_code", [None])[0]
            if weather_code is not None:
                condition = self.WEATHER_CODES.get(
                    weather_code, f"Unknown ({weather_code})"
                )
                print(f"Conditions:      {condition}")

            precip_sum = daily.get("precipitation_sum", [None])[0]
            if precip_sum is not None:
                print(f"Precipitation:   {precip_sum:.2f} in")

            precip_prob = daily.get("precipitation_probability_max", [None])[0]
            if precip_prob is not None:
                print(f"Precip Chance:   {precip_prob}%")

            max_wind = daily.get("wind_speed_10m_max", [None])[0]
            if max_wind is not None:
                print(f"Max Wind Speed:  {max_wind:.1f} mph")

        print(f"\n{'='*70}\n")
