#!/usr/bin/env python3

import math
from typing import Dict, List, Optional

import requests


class OverheadFlightsTracker:
    """
    Tracks overhead flights using OpenSky Network for positions and AirLabs for route data.
    """

    COUNTRIES = {
        "US": "United States",
        "CA": "Canada",
        "GB": "United Kingdom",
        "FR": "France",
        "DE": "Germany",
        "ES": "Spain",
        "IT": "Italy",
        "JP": "Japan",
        "CN": "China",
        "AU": "Australia",
        "BR": "Brazil",
        "MX": "Mexico",
        "IN": "India",
        "NL": "Netherlands",
        "CH": "Switzerland",
        "SE": "Sweden",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "IE": "Ireland",
        "NZ": "New Zealand",
        "SG": "Singapore",
        "KR": "South Korea",
        "TH": "Thailand",
        "AE": "UAE",
        "SA": "Saudi Arabia",
        "IL": "Israel",
        "TR": "Turkey",
        "PL": "Poland",
        "PT": "Portugal",
        "GR": "Greece",
        "AT": "Austria",
        "BE": "Belgium",
        "CZ": "Czech Republic",
        "HU": "Hungary",
        "RO": "Romania",
        "RU": "Russia",
    }

    def __init__(self, airlabs_api_key: str, zip_code: str):
        self.airlabs_api_key = airlabs_api_key
        self.zip_code = zip_code
        self.airport_cache = {}
        self.flight_cache = {}

    def _get_coordinates_from_zip(self) -> Optional[tuple]:
        """Convert US zip code to coordinates."""
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "postalcode": self.zip_code,
                    "country": "us",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "OverheadFlightsTracker/1.0"},
                timeout=10,
            )
            data = response.json()
            return (float(data[0]["lat"]), float(data[0]["lon"])) if data else None
        except Exception:
            return None

    def _get_airport_info(self, airport_code: str) -> Optional[Dict]:
        """Get airport information from HexDB."""
        if not airport_code or airport_code in self.airport_cache:
            return self.airport_cache.get(airport_code)
        try:
            response = requests.get(
                f"https://hexdb.io/api/v1/airport/icao/{airport_code}", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = {
                        "city": data.get("region_name", ""),
                        "country": self.COUNTRIES.get(
                            data.get("country_code", ""), data.get("country_code", "")
                        ),
                        "iata": data.get("iata", ""),
                        "name": data.get("airport", ""),
                    }
                    self.airport_cache[airport_code] = result
                    return result
            self.airport_cache[airport_code] = None
            return None
        except:
            self.airport_cache[airport_code] = None
            return None

    def _get_flight_route(self, callsign: str) -> Optional[Dict]:
        """Get real-time route from AirLabs API."""
        if not callsign or callsign == "N/A":
            return None

        if callsign in self.flight_cache:
            return self.flight_cache[callsign]

        try:
            response = requests.get(
                "https://airlabs.co/api/v9/flight",
                params={
                    "api_key": self.airlabs_api_key,
                    "flight_icao": callsign.strip(),
                },
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                if data and "response" in data:
                    flight_data = data["response"]
                    dep_icao = flight_data.get("dep_icao")
                    arr_icao = flight_data.get("arr_icao")

                    if dep_icao and arr_icao:
                        route = {
                            "origin": dep_icao,
                            "destination": arr_icao,
                            "origin_iata": flight_data.get("dep_iata"),
                            "destination_iata": flight_data.get("arr_iata"),
                            "airline": flight_data.get("airline_name"),
                            "flight_number": flight_data.get("flight_number"),
                        }
                        self.flight_cache[callsign] = route
                        return route

            self.flight_cache[callsign] = None
            return None
        except:
            self.flight_cache[callsign] = None
            return None

    @staticmethod
    def _calculate_distance(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula."""
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        return 3959.0 * 2 * math.asin(math.sqrt(a))

    def get_overhead_flights(
        self, latitude: float, longitude: float, radius_deg: float = 0.5
    ) -> List[Dict]:
        """
        Get all flights within a radius of given coordinates.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_deg: Search radius in degrees (default 0.5 ≈ 35 miles)

        Returns:
            List of flight dictionaries with position and flight data
        """
        try:
            response = requests.get(
                "https://opensky-network.org/api/states/all",
                params={
                    "lamin": latitude - radius_deg,
                    "lamax": latitude + radius_deg,
                    "lomin": longitude - radius_deg,
                    "lomax": longitude + radius_deg,
                },
                timeout=10,
            )
            data = response.json()
            if not data or "states" not in data:
                return []

            return [
                {
                    "icao24": s[0],
                    "callsign": s[1].strip() if s[1] else "N/A",
                    "longitude": s[5],
                    "latitude": s[6],
                    "altitude_ft": int(s[7] * 3.28084) if s[7] else None,
                    "velocity_mph": int(s[9] * 2.23694) if s[9] else None,
                    "heading": s[10],
                    "on_ground": s[8],
                }
                for s in data["states"]
            ]
        except Exception:
            return []

    def _format_airport_display(
        self, airport_code: str, iata_code: Optional[str], airport_info: Optional[Dict]
    ) -> tuple:
        """Format airport code and location for display."""
        code = iata_code or airport_code
        if airport_info:
            parts = [
                p
                for p in [
                    airport_info.get("name"),
                    airport_info.get("city"),
                    airport_info.get("country"),
                ]
                if p
            ]
            location = ", ".join(parts) if parts else code
        else:
            location = code
        return code, location

    def get_closest_flights_with_routes(self, max_flights: int = 2) -> List[Dict]:
        """
        Get the closest flights with route information for a given zip code.

        Args:
            max_flights: Maximum number of flights to return (default 2)

        Returns:
            List of flight dictionaries with route information and formatted display strings
        """
        coordinates = self._get_coordinates_from_zip()
        if not coordinates:
            return []

        flights = self.get_overhead_flights(coordinates[0], coordinates[1])
        if not flights:
            return []

        # Filter airborne and calculate distances in one pass
        airborne = []
        for f in flights:
            if not f["on_ground"]:
                if f["latitude"] and f["longitude"]:
                    f["distance"] = self._calculate_distance(
                        coordinates[0], coordinates[1], f["latitude"], f["longitude"]
                    )
                else:
                    f["distance"] = float("inf")
                airborne.append(f)

        if not airborne:
            return []

        # Sort and fetch route data (stop at max_flights)
        flights_with_routes = []
        for flight in sorted(airborne, key=lambda x: x["distance"]):
            if len(flights_with_routes) >= max_flights:
                break

            route = self._get_flight_route(flight["callsign"])
            flight["route"] = route

            if route:
                origin_info = self._get_airport_info(route["origin"])
                dest_info = self._get_airport_info(route["destination"])

                origin_code, origin_location = self._format_airport_display(
                    route["origin"], route.get("origin_iata"), origin_info
                )
                dest_code, dest_location = self._format_airport_display(
                    route["destination"], route.get("destination_iata"), dest_info
                )

                flight["display"] = {
                    "origin_code": origin_code,
                    "origin_location": origin_location,
                    "dest_code": dest_code,
                    "dest_location": dest_location,
                }
                flights_with_routes.append(flight)

        return flights_with_routes

    def display(self):
        """
        Display the top 2 closest flights with route information to console.
        """

        # Get the 4 closest flights with routes
        flights_with_routes = self.get_closest_flights_with_routes(max_flights=4)

        if not flights_with_routes:
            print(f"\nNo flights found with route information for {self.zip_code}")
            return

        # Display each flight from the enriched array
        for i, f in enumerate(flights_with_routes, 1):
            print(f"Flight #{i} - {f['distance']:.1f} miles away")
            print(f"  Callsign:  {f['callsign']}")
            print(f"  Position:  {f['latitude']:.4f}°, {f['longitude']:.4f}°")
            print(f"  ICAO24:    {f['icao24']}")

            route = f["route"]
            if route.get("airline"):
                print(f"  Airline:   {route['airline']}")
            if route.get("flight_number"):
                print(f"  Flight #:  {route['flight_number']}")

            # Use pre-formatted display strings
            display = f["display"]
            print(f"  Route:     {display['origin_code']} → {display['dest_code']}")
            print(
                f"    From:    {display['origin_code']} - {display['origin_location']}"
            )
            print(f"    To:      {display['dest_code']} - {display['dest_location']}")

            if f["altitude_ft"]:
                print(f"  Altitude:  {f['altitude_ft']:,} ft")
            if f["velocity_mph"]:
                print(f"  Speed:     {f['velocity_mph']} mph")
            if f["heading"] is not None:
                print(f"  Heading:   {f['heading']:.0f}°")
