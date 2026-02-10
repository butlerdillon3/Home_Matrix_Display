"""
Overhead Flights Example for LED Matrix Display
Shows overhead flight information with airline logo and flight details.
Uses the OverheadFlightsTracker module to fetch real-time flight data.
Layout for 128x64 display with airline logo on left and flight info on right.
"""

import time
import os
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import sys
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.overhead_flights import OverheadFlightsTracker


def get_text_width(font, text):
    """Calculate the width of text in pixels."""
    return sum([font.CharacterWidth(ord(c)) for c in text])

def get_airline_logo(airline_name):
    """
    Get the airline logo based on the airline name.
    Returns the path to the airline's logo if it exists, otherwise returns the default logo.
    
    Args:
        airline_name: The name of the airline (e.g., "American Airlines", "Delta")
    
    Returns:
        str: Path to the airline logo BMP file
    """
    if not airline_name:
        return "static/airline_logos_pixelized/default.bmp"
    
    # Convert airline name to lowercase and remove common suffixes
    airline_name_clean = airline_name.lower()
    airline_name_clean = airline_name_clean.replace("airlines", "").replace("airways", "")
    airline_name_clean = airline_name_clean.strip()
    
    # Replace spaces and special characters with underscores
    airline_name_clean = airline_name_clean.replace(" ", "_").replace("-", "_")
    
    # Build the potential logo path
    logo_path = f"static/airline_logos_pixelized/{airline_name_clean}.bmp"
    
    # Check if the logo file exists
    if os.path.exists(logo_path):
        return logo_path
    else:
        return "static/airline_logos_pixelized/default.bmp"

def main():
    # Get API key and zip code from environment variables
    airlabs_api_key = os.getenv("AIRLABS_API_KEY")
    zip_code = os.getenv("ZIP_CODE", "19106")  # Default to Philadelphia
    
    if not airlabs_api_key:
        print("Error: AIRLABS_API_KEY environment variable not set")
        print("Please set it with: export AIRLABS_API_KEY='your_key_here'")
        return
    
    # Initialize overhead flights tracker
    flights_tracker = OverheadFlightsTracker(airlabs_api_key, zip_code)
    
    # Configure the matrix
    # For 2 64x64 panels chained horizontally = 128x64 total display
    options = RGBMatrixOptions()
    options.rows = 64          # Height of each panel
    options.cols = 64          # Width of each panel
    options.chain_length = 2   # 2 panels chained together
    options.parallel = 1       # Single chain (not parallel chains)
    options.hardware_mapping = 'regular'
    
    # Create the matrix
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()
    
    # Load fonts
    font_large = graphics.Font()
    font_large.LoadFont("fonts/helvR10.bdf")  # Helvetica Bold 10 - clear and readable
    
    font_small = graphics.Font()
    font_small.LoadFont("fonts/helvR08.bdf")  # Helvetica Regular 8 - readable small font
    
    # Display dimensions (total display size with chaining)
    display_width = options.cols * options.chain_length  # 64 * 2 = 128
    display_height = options.rows  # 64

    # Colors
    text_color = graphics.Color(200, 200, 200)  # Light gray for text
    highlight_color = graphics.Color(255, 255, 255)  # White for important info
    
    try:
        while True:
            # Get closest flights with routes
            flights = flights_tracker.get_closest_flights_with_routes(max_flights=2)
            
            if flights:
                flight = flights[0]
                route = flight.get("route")
                
                # Clear canvas
                canvas.Clear()
                
                # Draw airline logo on left side (centered vertically)
                logo_x = 7
                logo_y = 4
                current_logo = Image.open(get_airline_logo(flight["route"]["airline"]))
                canvas.SetImage(current_logo, logo_x, logo_y)
                
                # Text area starts after the logo with some spacing
                text_start_x = logo_x + 45
                line_height = 9  # Compact spacing
                
                # Start text higher up for better vertical centering
                current_y = 18
                
                # Line 1: Airline name (if available)
                if route and route.get("airline"):
                    airline_name = route["airline"]
                    graphics.DrawText(canvas, font_large, text_start_x, current_y, 
                                    highlight_color, airline_name.replace("Airlines", "").replace("Airways", "").replace("Airline", ""))
                    current_y += line_height + 4
                
                # Line 2: Route (IATA codes if available, otherwise ICAO)
                if route:
                    origin_code = route.get("origin_iata") or route.get("origin")
                    dest_code = route.get("destination_iata") or route.get("destination")
                    route_text = f"{origin_code}-{dest_code}"
                    graphics.DrawText(canvas, font_large, text_start_x-1, current_y, 
                                    text_color, route_text)
                    current_y += line_height
                else:
                    # Just show callsign if no route available
                    graphics.DrawText(canvas, font_large, text_start_x, current_y, 
                                    text_color, flight["callsign"])
                    current_y += line_height
                
                # Line 3: Aircraft type (placeholder - would need additional API)
                # For now, skip this line or show "N/A"
                # current_y += line_height
                
                # Line 4: Altitude and Speed (compact format)
                text_start_x = 5
                current_y= 50
                if flight.get("altitude_ft") and flight.get("velocity_mph"):
                    alt_kft = flight["altitude_ft"] / 1000
                    speed_mph = flight["velocity_mph"]
                    # More compact format
                    alt_speed_text = f"Alt:{alt_kft:.1f}k Ft, Spd:{speed_mph} mph"
                    graphics.DrawText(canvas, font_small, text_start_x, current_y, 
                                    text_color, alt_speed_text)
                    current_y += line_height
                
                # Line 5: Track and Vertical speed (placeholder for vertical speed)
                if flight.get("heading") is not None:
                    track = flight["heading"]
                    # Note: OpenSky API doesn't provide vertical speed in basic tier
                    # We'll show track for now
                    track_text = f"Trk:{track:.0f}deg"
                    graphics.DrawText(canvas, font_small, text_start_x, current_y, 
                                    text_color, track_text)
                    current_y += line_height
                
                # Display the canvas
                matrix.SwapOnVSync(canvas)
                
                # Update every 30 seconds (API rate limits)
                time.sleep(30)
            else:
                # No flights found
                canvas.Clear()
                no_flights_msg = "No flights overhead"
                msg_width = get_text_width(font_large, no_flights_msg)
                msg_x = (display_width - msg_width) // 2
                msg_y = display_height // 2
                graphics.DrawText(canvas, font_large, msg_x, msg_y, 
                                text_color, no_flights_msg)
                matrix.SwapOnVSync(canvas)
                
                # Check again in 30 seconds
                time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        canvas.Clear()
        matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    main()
