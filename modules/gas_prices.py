#!/usr/bin/env python3
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class GasPriceTracker:
    """Tracks gas prices in your area using web scraping."""

    def __init__(self, zip_code: str, radius: int = 5):
        """
        Initialize gas price tracker.

        Args:
            zip_code: ZIP code to search around
            radius: Search radius in miles (default 5)
        """
        self.zip_code = zip_code
        self.radius = radius

    def _get_state_from_zip(self) -> str:
        """
        Determine state from zip code prefix.
        Covers all 50 US states plus DC, Puerto Rico, and territories.
        """
        # Use first 3 digits for precise matching
        zip_prefix = int(self.zip_code[:3]) if len(self.zip_code) >= 3 else 0

        # Complete US ZIP code range mapping (all 50 states + DC)
        # Format: (min, max, state_name)
        zip_ranges = [
            # Northeast
            (10, 14, "New York"),
            (60, 69, "Connecticut"),
            (70, 89, "New Jersey"),
            (100, 149, "New York"),
            (150, 196, "Pennsylvania"),
            (197, 199, "Delaware"),
            (200, 205, "District of Columbia"),
            (206, 219, "Maryland"),
            (220, 246, "Virginia"),
            (247, 268, "West Virginia"),
            (270, 279, "North Carolina"),
            (280, 285, "South Carolina"),
            (286, 299, "North Carolina"),
            # New England
            (10, 27, "Massachusetts"),
            (28, 29, "Rhode Island"),
            (30, 38, "New Hampshire"),
            (39, 49, "Maine"),
            (50, 59, "Vermont"),
            # Southeast
            (300, 319, "Florida"),
            (320, 349, "Florida"),
            (350, 369, "Alabama"),
            (370, 385, "Tennessee"),
            (386, 397, "Mississippi"),
            (398, 399, "Georgia"),
            (400, 424, "Kentucky"),
            (425, 427, "Kentucky"),
            (430, 458, "Ohio"),
            (460, 479, "Indiana"),
            (480, 499, "Michigan"),
            # Midwest
            (500, 528, "Iowa"),
            (530, 549, "Wisconsin"),
            (550, 567, "Minnesota"),
            (570, 577, "South Dakota"),
            (580, 588, "North Dakota"),
            (590, 599, "Montana"),
            (600, 629, "Illinois"),
            (630, 658, "Missouri"),
            (660, 679, "Kansas"),
            (680, 693, "Nebraska"),
            # South
            (700, 714, "Louisiana"),
            (716, 729, "Arkansas"),
            (730, 749, "Oklahoma"),
            (750, 799, "Texas"),
            # Mountain West
            (800, 816, "Colorado"),
            (820, 831, "Wyoming"),
            (832, 838, "Idaho"),
            (840, 847, "Utah"),
            (850, 865, "Arizona"),
            (870, 884, "New Mexico"),
            (889, 898, "Nevada"),
            # Pacific
            (900, 961, "California"),
            (967, 968, "Hawaii"),
            (970, 979, "Oregon"),
            (980, 994, "Washington"),
            (995, 999, "Alaska"),
            # Territories
            (9, 9, "Puerto Rico"),
            (96, 96, "American Samoa"),
            (962, 966, "APO/FPO"),
            (969, 969, "Guam"),
        ]

        # Find matching state
        for min_zip, max_zip, state in zip_ranges:
            if min_zip <= zip_prefix <= max_zip:
                return state

        # Default fallback
        return "United States"

    def get_gas_prices(self) -> Optional[List[Dict]]:
        """
        Fetch gas prices from AAA state averages.

        AAA provides reliable, regularly-updated state average prices.
        """
        try:
            url = "https://gasprices.aaa.com/state-gas-price-averages/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, "lxml")

            # Find the state based on zip code
            state = self._get_state_from_zip()

            # Find the table with state data
            table = soup.find("table")
            if not table:
                return None

            # Find the row for our state
            rows = table.find_all("tr")

            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells or len(cells) < 4:
                    continue

                state_name = cells[0].get_text(strip=True)

                if state.lower() in state_name.lower():
                    # Extract prices
                    try:
                        regular = cells[1].get_text(strip=True).replace("$", "")
                        mid_grade = cells[2].get_text(strip=True).replace("$", "")
                        premium = cells[3].get_text(strip=True).replace("$", "")
                        diesel = (
                            cells[4].get_text(strip=True).replace("$", "")
                            if len(cells) > 4
                            else None
                        )

                        # Create a station entry for state average
                        station_data = {
                            "station": f"{state} State Average (AAA)",
                            "address": f"Statewide average for ZIP {self.zip_code}",
                            "regular": float(regular),
                            "mid_grade": float(mid_grade),
                            "premium": float(premium),
                        }

                        if diesel:
                            station_data["diesel"] = float(diesel)

                        # Return as a list with one entry
                        return [station_data]

                    except (ValueError, IndexError):
                        continue

            return None

        except Exception as e:
            return None

    def display(self):
        """Display gas prices."""
        print(f"\n{'='*70}")
        print(f"GAS PRICES - ZIP {self.zip_code}")
        print(f"{'='*70}\n")

        prices = self.get_gas_prices()

        if not prices:
            print("  Unable to fetch gas prices at this time.")
            print("  This could be due to:")
            print("    - Network connection issues")
            print("    - AAA website structure changes")
            print(f"\n{'='*70}\n")
            return

        for station in prices:
            print(f"{station.get('station', 'Unknown')}")
            if station.get("address"):
                print(f"  {station['address']}")
            print()
            print(f"  Regular:   ${station['regular']:.3f}")
            if station.get("mid_grade"):
                print(f"  Mid-Grade: ${station['mid_grade']:.3f}")
            if station.get("premium"):
                print(f"  Premium:   ${station['premium']:.3f}")
            if station.get("diesel"):
                print(f"  Diesel:    ${station['diesel']:.3f}")
            print()

        print("Note: These are state average prices from AAA.")
        print("Actual local prices may vary.")
        print(f"\n{'='*70}\n")
