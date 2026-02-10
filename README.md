# LED Matrix Display

Python modules for displaying real-time information: transit, flights, weather, news, and more.

## Modules

**Overhead Flights** - Track nearby aircraft with real-time positions, routes, and details (requires AirLabs API key)

**SEPTA Regional Rail** - Philadelphia train arrivals and departures (no API key needed)

**Weather** - Current conditions and 5-day forecast for any US zip code (no API key needed)

**Clock** - Time, date, and day with configurable formatting (no API key needed)

**Gas Prices** - State average prices from AAA (no API key needed)

**News Headlines** - RSS feeds from BBC, Reuters, NPR, CNN, and more (optional NewsAPI key for more sources)

## Setup

**Install dependencies:**
```bash
curl -sSL https://install.python-poetry.org | python3 -  # Install Poetry if needed
poetry install
```

**Configure API keys (optional):**
```bash
cp .env.example .env
# Edit .env and add keys:
# - AIRLABS_API_KEY (required for flights): https://airlabs.co/
# - NEWS_API_KEY (optional for news): https://newsapi.org/
```

## Usage

**Run all modules:**
```bash
poetry run python main.py  # Edit main.py to select which modules to run
```

**Run individual modules:**
```bash
poetry run python modules/clock.py
poetry run python modules/weather.py
poetry run python modules/gas_prices.py
poetry run python modules/news_headlines.py
poetry run python modules/overhead_flights.py
poetry run python modules/septa_transit.py  # Add station name as argument
```

## License

MIT
