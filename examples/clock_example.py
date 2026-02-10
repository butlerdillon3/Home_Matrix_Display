"""
Clock Example for LED Matrix Display
Shows an analog clock on the left and digital time on the right.
Uses the ClockDisplay module to get current time information.
Centered layout for 128x64 display with Helvetica 10 font.
"""

import time
import math
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.clock import ClockDisplay


def draw_circle(canvas, cx, cy, radius, r, g, b):
    """Draw a circle using midpoint circle algorithm."""
    x = radius
    y = 0
    err = 0
    
    while x >= y:
        canvas.SetPixel(cx + x, cy + y, r, g, b)
        canvas.SetPixel(cx + y, cy + x, r, g, b)
        canvas.SetPixel(cx - y, cy + x, r, g, b)
        canvas.SetPixel(cx - x, cy + y, r, g, b)
        canvas.SetPixel(cx - x, cy - y, r, g, b)
        canvas.SetPixel(cx - y, cy - x, r, g, b)
        canvas.SetPixel(cx + y, cy - x, r, g, b)
        canvas.SetPixel(cx + x, cy - y, r, g, b)
        
        if err <= 0:
            y += 1
            err += 2 * y + 1
        
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_line(canvas, x0, y0, x1, y1, r, g, b):
    """Draw a line using Bresenham's algorithm."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        canvas.SetPixel(x0, y0, r, g, b)
        
        if x0 == x1 and y0 == y1:
            break
        
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def draw_analog_clock(canvas, cx, cy, radius, hour, minute, second):
    """Draw a simple analog clock face with hands."""
    # Draw clock circle (white)
    draw_circle(canvas, cx, cy, radius, 255, 255, 255)
    
    # Draw markers at 12, 3, 6, 9 positions
    for i in [0, 3, 6, 9]:  # 12, 3, 6, 9 positions
        angle = math.radians(i * 30 - 90)  # -90 to start at 12 o'clock
        marker_x = int(cx + (radius - 3) * math.cos(angle))
        marker_y = int(cy + (radius - 3) * math.sin(angle))
        canvas.SetPixel(marker_x, marker_y, 200, 200, 200)
    
    # Draw center dot
    canvas.SetPixel(cx, cy, 255, 255, 255)
    
    # Calculate hand positions
    # Hour hand (red) - short
    hour_angle = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
    hour_length = radius * 0.5
    hour_x = int(cx + hour_length * math.cos(hour_angle))
    hour_y = int(cy + hour_length * math.sin(hour_angle))
    draw_line(canvas, cx, cy, hour_x, hour_y, 255, 80, 80)
    
    # Minute hand (green) - longer
    minute_angle = math.radians(minute * 6 - 90)
    minute_length = radius * 0.7
    minute_x = int(cx + minute_length * math.cos(minute_angle))
    minute_y = int(cy + minute_length * math.sin(minute_angle))
    draw_line(canvas, cx, cy, minute_x, minute_y, 80, 255, 80)
    
    # Second hand (blue) - longest
    second_angle = math.radians(second * 6 - 90)
    second_length = radius * 0.85
    second_x = int(cx + second_length * math.cos(second_angle))
    second_y = int(cy + second_length * math.sin(second_angle))
    draw_line(canvas, cx, cy, second_x, second_y, 80, 150, 255)


def get_text_width(font, text):
    """Calculate the width of text in pixels."""
    return sum([font.CharacterWidth(ord(c)) for c in text])


def main():
    # Initialize clock display module
    clock = ClockDisplay(time_format="24")
    
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
    
    # Load Helvetica Bold 10 font
    font = graphics.Font()
    font.LoadFont("fonts/helvR10.bdf")
    
    # Display dimensions (total display size with chaining)
    display_width = options.cols * options.chain_length  # 64 * 2 = 128
    display_height = options.rows  # 64
    
    print("Clock Display Example Running!")
    print("Open http://localhost:8888/ in your browser to see it")
    print(f"Display: {display_width}x{display_height} pixels")
    print("- Analog clock (left, centered)")
    print("- Digital time (right, centered)")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            # Get current time from clock module
            time_info = clock.get_current_time()
            timestamp = time_info['timestamp']
            
            # Extract hours, minutes, seconds
            hour = timestamp.hour
            minute = timestamp.minute
            second = timestamp.second
            
            # Format digital time (HH:MM:SS)
            digital_time = f"{hour:02d}:{minute:02d}:{second:02d}"
            
            # Day
            day_abbr = time_info['day_of_week']
            
            # Fixed positioning for proper centering
            # Display is 128 pixels wide, 64 pixels tall
            clock_radius = 20  # Larger clock for more detail
            
            # Shift everything left by 15 pixels to fit in window
            x_offset = -10
            
            # Position analog clock - centered in left half of display + offset
            clock_center_x = (display_width // 4) + x_offset  # 128/4 - 15 = 17
            clock_center_y = display_height // 2  # 64/2 = 32
            
            # Position digital text - centered in right half of display + offset
            # Estimate text block center around x=81 (3/4 of 128 - 15)
            digital_base_x = ((display_width * 3) // 4) + x_offset  # 128*3/4 - 15 = 81
            
            # Calculate text widths to center each line around digital_base_x
            time_width = get_text_width(font, digital_time)
            date_width = get_text_width(font, time_info['date'])
            day_width = get_text_width(font, day_abbr)
            
            # Center each text line around the base position
            time_x = digital_base_x - (time_width // 2)
            date_x = digital_base_x - (date_width // 2)
            day_x = digital_base_x - (day_width // 2)
            
            # Clear canvas
            canvas.Clear()
            
            # Draw analog clock
            draw_analog_clock(canvas, clock_center_x, clock_center_y, clock_radius, 
                            hour, minute, second)
            
            # Center the text block vertically
            # Each text line is about 12 pixels tall with Helvetica 10
            line_height = 12
            total_text_height = line_height * 3  # 3 lines: time, date, day
            text_start_y = clock_center_y - (total_text_height // 2) + 10  # Offset for baseline
            
            # Draw digital time (yellow)
            time_color = graphics.Color(255, 255, 0)
            graphics.DrawText(canvas, font, time_x, text_start_y, time_color, digital_time)
            
            # Draw date below time (cyan)
            date_color = graphics.Color(0, 255, 255)
            date_y = text_start_y + line_height
            graphics.DrawText(canvas, font, date_x, date_y, date_color, time_info['date'])
            
            # Draw day of week below date (light green) - abbreviated
            day_color = graphics.Color(128, 255, 128)
            day_y = date_y + line_height
            graphics.DrawText(canvas, font, day_x, day_y, day_color, day_abbr)
            
            # Display the canvas
            matrix.SwapOnVSync(canvas)
            
            # Update once per second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        canvas.Clear()
        matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    main()
