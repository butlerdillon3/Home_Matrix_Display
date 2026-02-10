"""
Oracle Example for LED Matrix Display
Displays random philosophical/poetic phrases from the Oracle of Nonsense.
Uses the OracleOfNonsense module to fetch phrases.
Centered layout for 128x64 display with Helvetica 8 font.
"""

import time
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.oracle import OracleOfNonsense


def wrap_text(text, font, max_width):
    """
    Wrap text to fit within max_width pixels.
    
    Args:
        text: The text to wrap
        font: The font object
        max_width: Maximum width in pixels
    
    Returns:
        List of text lines
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Try adding this word to current line
        test_line = ' '.join(current_line + [word])
        line_width = sum([font.CharacterWidth(ord(c)) for c in test_line])
        
        if line_width <= max_width:
            current_line.append(word)
        else:
            # Current line is full, start a new one
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def get_text_width(font, text):
    """Calculate the width of text in pixels."""
    return sum([font.CharacterWidth(ord(c)) for c in text])


def prepare_image_transparent(image):
    """
    Prepare image by making black/dark pixels transparent.
    
    Args:
        image: PIL Image object
    
    Returns:
        PIL Image with transparent background
    """
    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get pixel data
    pixels = image.load()
    
    # Make dark pixels transparent
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            # Make black/dark pixels transparent (RGB values below 30)
            if r < 30 and g < 30 and b < 30:
                pixels[x, y] = (r, g, b, 0)
    
    return image


def main():
    # Initialize oracle module
    oracle = OracleOfNonsense()
    
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
    
    # Load Helvetica Regular 8 font (non-bold, smaller size)
    font = graphics.Font()
    font.LoadFont("fonts/helvR08.bdf")
    
    # Load oracle crystal ball image (PNG with transparency support)
    oracle_image = Image.open("static/Oracle-Of-Nonsense.png")
    # Resize to 35x35 pixels to fit nicely on the display
    oracle_image = oracle_image.resize((35, 35), Image.LANCZOS)
    
    # Display dimensions (total display size with chaining)
    display_width = options.cols * options.chain_length  # 64 * 2 = 128
    display_height = options.rows  # 64
    
    print("Oracle of Nonsense Display Running!")
    print("Open http://localhost:8888/ in your browser to see it")
    print(f"Display: {display_width}x{display_height} pixels")
    print("- Crystal ball with mystical phrases")
    print("- Clean layout with improved readability")
    print("- New phrase every 10 seconds")
    print("Press Ctrl+C to exit.")
    
    # Colors for different elements
    phrase_color = graphics.Color(200, 255, 200)  # Brighter cyan-green for readability
    
    try:
        while True:
            # Get a random phrase
            phrase = oracle.get_random_phrase().replace('"', '')
            
            if phrase:
                # Clear canvas
                canvas.Clear()
                
                # Draw crystal ball image on left side (centered vertically)
                # Position image a bit more to the left to give text more room
                image_x = 8  # Fixed position from left edge
                image_y = (display_height - oracle_image.height) // 2  # Center vertically
                canvas.SetImage(oracle_image, image_x, image_y)
                
                # Wrap the phrase text to fit the space to the right of the crystal ball
                margin = 8  # Pixels from edge
                # Text area starts after the crystal ball with some spacing
                text_area_start = image_x + oracle_image.width + 8
                text_area_width = display_width - text_area_start - margin
                wrapped_lines = wrap_text(phrase, font, text_area_width)
                
                # Calculate vertical centering for text
                # Line height adjusted for Times Roman 8pt
                line_height = 10
                total_text_height = len(wrapped_lines) * line_height
                
                # Center text vertically in the display
                # Account for font baseline (text is drawn from baseline, not top)
                start_y = (display_height - total_text_height) // 2 + 8  # +10 for vertical centering
                
                # Draw each line of the phrase
                current_y = start_y
                for line in wrapped_lines:
                    graphics.DrawText(canvas, font, text_area_start, current_y, phrase_color, line)
                    current_y += line_height
                
                # Display the canvas
                matrix.SwapOnVSync(canvas)
                
                # Show each phrase for 10 seconds
                time.sleep(10)
            else:
                # If no phrase available, show error message
                canvas.Clear()
                error_msg = "Oracle is silent..."
                error_width = get_text_width(font, error_msg)
                error_x = (display_width - error_width) // 2
                error_y = display_height // 2
                error_color = graphics.Color(255, 100, 100)
                graphics.DrawText(canvas, font, error_x, error_y, error_color, error_msg)
                matrix.SwapOnVSync(canvas)
                time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nExiting...")
        canvas.Clear()
        matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    main()
