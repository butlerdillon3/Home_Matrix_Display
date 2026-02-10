import os

from dotenv import find_dotenv, load_dotenv

from modules.clock import ClockDisplay
from modules.gas_prices import GasPriceTracker
from modules.news_headlines import NewsHeadlinesTracker
from modules.oracle import OracleOfNonsense
from modules.overhead_flights import OverheadFlightsTracker
from modules.septa_transit import SeptaTransitTracker
from modules.weather import WeatherTracker

load_dotenv(find_dotenv())


def run_flights_module():
    # Get API key from environment
    api_key = os.getenv("AIRLABS_API_KEY")

    # Create tracker and display flights
    tracker = OverheadFlightsTracker(airlabs_api_key=api_key, zip_code="19122")
    tracker.display()


def run_septa_module():
    # Create tracker and display arrivals
    tracker = SeptaTransitTracker()
    tracker.display()


def run_weather_module():
    # Create tracker and display weather
    tracker = WeatherTracker(zip_code="19122")
    tracker.display()


def run_clock_module():
    # Create clock and display time
    clock = ClockDisplay(time_format="12", date_format="US")
    clock.display()


def run_gas_prices_module():
    # Create tracker and display gas prices
    tracker = GasPriceTracker(zip_code="19122", radius=5)
    tracker.display()


def run_news_module():
    # Create tracker and display news headlines
    # Options: 'bbc', 'reuters', 'npr', 'cnn', 'ap', 'techcrunch', 'phillyvoice'
    tracker = NewsHeadlinesTracker(source="phillyvoice", max_headlines=10)
    tracker.display()


def run_oracle_module():
    # Create oracle and display random phrase(s)
    oracle = OracleOfNonsense()
    oracle.display(num_phrases=1)  # Change num_phrases to display multiple


if __name__ == "__main__":
    # run_septa_module()
    # run_flights_module()
    # run_weather_module()
    # run_clock_module()
    # run_gas_prices_module()
    run_news_module()
    # run_oracle_module()
