#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

import requests


class NewsHeadlinesTracker:
    """Displays news headlines from RSS feeds or News API."""

    # Popular RSS feeds
    RSS_FEEDS = {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "reuters": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "npr": "https://feeds.npr.org/1001/rss.xml",
        "ap": "https://apnews.com/apf-topnews",
        "cnn": "http://rss.cnn.com/rss/cnn_topstories.rss",
        "techcrunch": "https://techcrunch.com/feed/",
        "phillyvoice": "https://www.phillyvoice.com/feed/",
    }

    def __init__(
        self, source: str = "bbc", max_headlines: int = 10, use_api: bool = False
    ):
        """
        Initialize news headlines tracker.

        Args:
            source: News source ('bbc', 'reuters', 'npr', 'cnn', 'ap', 'techcrunch', 'phillyvoice')
            max_headlines: Maximum number of headlines to display
            use_api: If True, use NewsAPI instead of RSS (requires API key in .env)
        """
        self.source = source.lower()
        self.max_headlines = max_headlines
        self.use_api = use_api

    def get_headlines_from_rss(self) -> Optional[List[Dict]]:
        """Fetch headlines from RSS feed."""
        feed_url = self.RSS_FEEDS.get(self.source)

        if not feed_url:
            print(f"Unknown source: {self.source}")
            print(f"Available sources: {', '.join(self.RSS_FEEDS.keys())}")
            return None

        try:
            # Add User-Agent header to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(feed_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code} when fetching {self.source}")
                return None

            # Parse RSS XML
            root = ET.fromstring(response.content)
            headlines = []

            # Handle different RSS formats
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            for item in items[: self.max_headlines]:
                # Try different tag names for title and link
                title = item.find("title")
                if title is None:
                    title = item.find("{http://www.w3.org/2005/Atom}title")

                link = item.find("link")
                if link is None:
                    link = item.find("{http://www.w3.org/2005/Atom}link")

                pub_date = item.find("pubDate")
                if pub_date is None:
                    pub_date = item.find("{http://www.w3.org/2005/Atom}published")

                if title is not None:
                    headline = {
                        "title": title.text if title.text else "No title",
                        "link": (
                            link.text
                            if link is not None and link.text
                            else (link.get("href") if link is not None else "")
                        ),
                        "published": (
                            pub_date.text
                            if pub_date is not None and pub_date.text
                            else "Unknown"
                        ),
                    }
                    headlines.append(headline)

            return headlines if headlines else None

        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return None

    def get_headlines_from_api(self) -> Optional[List[Dict]]:
        """
        Fetch headlines from NewsAPI.

        Requires NEWS_API_KEY in .env file.
        Sign up at: https://newsapi.org/
        """
        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            print("NEWS_API_KEY not found in .env file")
            print("Sign up at https://newsapi.org/ to get a free API key")
            return None

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": api_key,
                "country": "us",
                "pageSize": self.max_headlines,
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()
            if data.get("status") != "ok":
                return None

            headlines = []
            for article in data.get("articles", []):
                headlines.append(
                    {
                        "title": article.get("title", "No title"),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "link": article.get("url", ""),
                        "published": article.get("publishedAt", "Unknown"),
                    }
                )

            return headlines if headlines else None

        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return None

    def display(self):
        """Display news headlines."""
        print(f"\n{'='*70}")
        if self.use_api:
            print("TOP NEWS HEADLINES (NewsAPI)")
        else:
            print(f"TOP NEWS HEADLINES - {self.source.upper()}")
        print(f"{'='*70}\n")

        if self.use_api:
            headlines = self.get_headlines_from_api()
        else:
            headlines = self.get_headlines_from_rss()

        if not headlines:
            print("  Unable to fetch headlines at this time.")
            print(f"\n  Available RSS sources: {', '.join(self.RSS_FEEDS.keys())}")
            print("\n  For more sources and better reliability:")
            print("    1. Sign up for NewsAPI at https://newsapi.org/")
            print("    2. Add NEWS_API_KEY to .env file")
            print("    3. Use: NewsHeadlinesTracker(use_api=True)")
            print(f"\n{'='*70}\n")
            return

        for i, headline in enumerate(headlines, 1):
            print(f"{i}. {headline['title']}")
            if headline.get("source"):
                print(f"   Source: {headline['source']}")
            if headline.get("published") and headline["published"] != "Unknown":
                pub_time = (
                    headline["published"][:19]
                    if len(headline["published"]) > 19
                    else headline["published"]
                )
                print(f"   Published: {pub_time}")
            print()

        print(f"{'='*70}\n")
