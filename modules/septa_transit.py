#!/usr/bin/env python3
from typing import Dict, Optional

import requests


class SeptaTransitTracker:
    """Tracks SEPTA Regional Rail arrivals using public API."""

    MAJOR_STATIONS = [
        "Suburban Station",
        "Jefferson Station (Market East)",
        "30th Street Station",
        "Temple University",
        "North Philadelphia",
        "University City",
        "Wayne Junction",
        "Fern Rock Transportation Center",
    ]

    def __init__(self, default_station: str = "Suburban Station"):
        self.default_station = default_station

    def get_station_arrivals(self) -> Optional[Dict]:
        try:
            r = requests.get(
                "https://www3.septa.org/api/Arrivals/index.php",
                params={"station": self.default_station},
                timeout=10,
            )
            data = r.json() if r.status_code == 200 else None
            return (
                data
                if data and isinstance(data, dict) and "error" not in data
                else None
            )
        except:
            return None

    def display(self):
        print(
            f"\n{'='*70}\nSEPTA Regional Rail Arrivals - {self.default_station}\n{'='*70}\n"
        )
        data = self.get_station_arrivals()

        if not data:
            print(
                f"No data for '{self.default_station}'\nValid stations:\n"
                + "\n".join(f"  - {s}" for s in self.MAJOR_STATIONS)
                + f"\n{'='*70}\n"
            )
            return

        for key, directions in data.items():
            print(f"Current Time: {key.split(': ')[1] if ': ' in key else 'N/A'}\n")
            for dd in directions:
                if not isinstance(dd, dict):
                    continue
                for direction, trains in dd.items():
                    print(f"{direction}\n{'-'*70}")
                    if not trains or not isinstance(trains, list):
                        print("  No trains scheduled\n")
                        continue
                    for i, t in enumerate(trains[:10], 1):
                        if not isinstance(t, dict):
                            continue
                        print(
                            f"\nTrain #{i}\n  Line: {t.get('line','N/A')}  ID: {t.get('train_id','N/A')}\n"
                            f"  To: {t.get('destination','N/A')}  From: {t.get('origin','N/A')}\n"
                            f"  Status: {t.get('status','N/A')}  Depart: {t.get('depart_time','N/A')}\n"
                            f"  Track: {t.get('track','N/A')}  Platform: {t.get('platform','N/A')}"
                        )
                    print()
        print(f"{'='*70}\n")
