#!/usr/bin/env python3
from datetime import datetime
from typing import Optional


class ClockDisplay:
    """Displays current time, date, and day of week."""

    def __init__(self, time_format: str = "12", date_format: str = "US"):
        """
        Initialize clock display.

        Args:
            time_format: '12' for 12-hour or '24' for 24-hour format
            date_format: 'US' for MM/DD/YYYY or 'EU' for DD/MM/YYYY
        """
        self.time_format = time_format
        self.date_format = date_format

    def get_current_time(self) -> dict:
        """Get current date and time information."""
        now = datetime.now()

        # Format time
        if self.time_format == "12":
            time_str = now.strftime("%I:%M:%S %p")
        else:
            time_str = now.strftime("%H:%M:%S")

        # Format date
        if self.date_format == "US":
            date_str = now.strftime("%m/%d/%Y")
        else:
            date_str = now.strftime("%d/%m/%Y")

        return {
            "time": time_str,
            "date": date_str,
            "day_of_week": now.strftime("%A"),
            "month": now.strftime("%B"),
            "day": now.strftime("%d"),
            "year": now.strftime("%Y"),
            "timestamp": now,
        }

    def display(self):
        """Display current time and date."""
        print(f"\n{'='*70}")
        print("CURRENT TIME & DATE")
        print(f"{'='*70}\n")

        time_info = self.get_current_time()

        print(f"  Time:         {time_info['time']}")
        print(f"  Date:         {time_info['date']}")
        print(f"  Day:          {time_info['day_of_week']}")
        print(
            f"  Full Date:    {time_info['day_of_week']}, {time_info['month']} {time_info['day']}, {time_info['year']}"
        )

        print(f"\n{'='*70}\n")
