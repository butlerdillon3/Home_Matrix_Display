#!/usr/bin/env python3
import os
import random
from typing import Optional


class OracleOfNonsense:
    """Displays random philosophical/poetic phrases from oracle of nonsense."""

    def __init__(self, csv_path: str = None):
        """
        Initialize oracle display.

        Args:
            csv_path: Path to the CSV file with phrases (defaults to static/oracle_of_nonesesne_phrases.csv)
        """
        if csv_path is None:
            # Default to the static folder in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(
                project_root, "static", "oracle_of_nonesesne_phrases.csv"
            )

        self.csv_path = csv_path
        self.phrases = []
        self._load_phrases()

    def _load_phrases(self):
        """Load phrases from the CSV file."""
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                self.phrases = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: Could not find phrases file at {self.csv_path}")
            self.phrases = ["The oracle is silent today."]
        except Exception as e:
            print(f"Warning: Error reading phrases file: {e}")
            self.phrases = ["The oracle speaks in mysteries beyond comprehension."]

    def get_random_phrase(self) -> Optional[str]:
        """Get a random phrase from the loaded phrases."""
        if not self.phrases:
            return None
        return random.choice(self.phrases)

    def get_multiple_phrases(self, count: int = 3) -> list:
        """
        Get multiple random phrases.

        Args:
            count: Number of phrases to return

        Returns:
            List of random phrases
        """
        if not self.phrases:
            return []

        # If we have fewer phrases than requested, return all
        if len(self.phrases) <= count:
            return self.phrases.copy()

        return random.sample(self.phrases, count)

    def display(self, num_phrases: int = 1):
        """
        Display random phrase(s).

        Args:
            num_phrases: Number of phrases to display (default 1)
        """
        print(f"\n{'='*70}")
        print("ORACLE OF NONSENSE")
        print(f"{'='*70}\n")

        if num_phrases == 1:
            phrase = self.get_random_phrase()
            if phrase:
                print(f"  {phrase}")
            else:
                print("  The oracle has nothing to say.")
        else:
            phrases = self.get_multiple_phrases(num_phrases)
            if phrases:
                for i, phrase in enumerate(phrases, 1):
                    print(f"  {i}. {phrase}")
                    if i < len(phrases):
                        print()
            else:
                print("  The oracle has nothing to say.")

        print(f"\n{'='*70}\n")
