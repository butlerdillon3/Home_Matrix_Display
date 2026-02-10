#!/usr/bin/env python3
"""
Pixelizer Tool - Converts PNG images to 40x40 BMP format.

This tool takes an input PNG file and converts it to a 40x40 BMP file
while maintaining transparent background pixels by converting them to
a specified background color.
"""

from PIL import Image
import argparse
import os
import sys


def convert_png_to_bmp(input_path: str, output_path: str, bg_color: tuple = (0, 0, 0), 
                       maintain_aspect: bool = True, resample_filter: int = Image.Resampling.LANCZOS,
                       target_size: tuple = (40, 40)):
    """
    Convert a PNG image to a BMP file with specified dimensions.
    
    Args:
        input_path: Path to the input PNG file
        output_path: Path to save the output BMP file
        bg_color: RGB tuple for transparent pixel replacement (default: black)
        maintain_aspect: Whether to maintain aspect ratio (adds padding if True)
        resample_filter: PIL resampling filter for resize operation
        target_size: Target dimensions (width, height) (default: 40x40)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Open the input PNG
        img = Image.open(input_path)
        
        # Ensure the image has an alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Calculate new size while maintaining aspect ratio if requested
        if maintain_aspect:
            img.thumbnail(target_size, resample_filter)
            
            # Create a new image with the target size and background color
            new_img = Image.new('RGB', target_size, bg_color)
            
            # Calculate position to paste the resized image (center it)
            paste_x = (target_size[0] - img.size[0]) // 2
            paste_y = (target_size[1] - img.size[1]) // 2
            
            # Create a background layer
            background = Image.new('RGB', img.size, bg_color)
            
            # Composite the image over the background using alpha channel
            background.paste(img, (0, 0), img)
            
            # Paste onto the final canvas
            new_img.paste(background, (paste_x, paste_y))
        else:
            # Resize without maintaining aspect ratio
            img = img.resize(target_size, resample_filter)
            
            # Create RGB image with background color
            new_img = Image.new('RGB', target_size, bg_color)
            
            # Composite using alpha channel as mask
            new_img.paste(img, (0, 0), img)
        
        # Save as BMP
        new_img.save(output_path, 'BMP')
        
        print(f"✓ Successfully converted {input_path} to {output_path}")
        print(f"  Output size: {new_img.size}")
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: Input file '{input_path}' not found", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Error converting image: {e}", file=sys.stderr)
        return False


def process_airline_logos(logos_dir: str = 'static/airline_logos', 
                         output_dir: str = 'static/airline_logos_pixelized',
                         size: tuple = (30, 30), bg_color: tuple = (0, 0, 0)):
    """
    Process all PNG files in the airline logos directory and convert them to BMP.
    
    Args:
        logos_dir: Directory containing the airline logo PNG files
        output_dir: Output directory for pixelized BMP files
        size: Target size (width, height)
        bg_color: Background color for transparent pixels
    
    Returns:
        Number of successfully processed files
    """
    # Get the absolute path to the logos directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    logos_path = os.path.join(project_dir, logos_dir)
    
    if not os.path.exists(logos_path):
        print(f"✗ Error: Directory '{logos_path}' not found", file=sys.stderr)
        return 0
    
    # Create output directory
    output_path = os.path.join(project_dir, output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # Find all PNG files
    png_files = [f for f in os.listdir(logos_path) 
                 if f.lower().endswith('.png') and os.path.isfile(os.path.join(logos_path, f))]
    
    if not png_files:
        print(f"✗ No PNG files found in '{logos_path}'", file=sys.stderr)
        return 0
    
    print(f"Found {len(png_files)} PNG file(s) to process")
    print(f"Output directory: {output_path}")
    print(f"Target size: {size[0]}x{size[1]}")
    print("-" * 60)
    
    success_count = 0
    for png_file in sorted(png_files):
        input_file = os.path.join(logos_path, png_file)
        output_file = os.path.join(output_path, os.path.splitext(png_file)[0] + '.bmp')
        
        print(f"Processing: {png_file}...", end=' ')
        
        if convert_png_to_bmp(input_file, output_file, bg_color=bg_color, 
                             maintain_aspect=True, target_size=size):
            success_count += 1
            print("✓")
        else:
            print("✗")
    
    print("-" * 60)
    print(f"Successfully processed {success_count}/{len(png_files)} file(s)")
    
    return success_count


def parse_color(color_str: str) -> tuple:
    """
    Parse color string in format 'R,G,B' or hex '#RRGGBB'.
    
    Args:
        color_str: Color string in RGB format (e.g., '255,0,0') or hex (e.g., '#FF0000')
    
    Returns:
        RGB tuple (r, g, b)
    """
    color_str = color_str.strip()
    
    # Handle hex format
    if color_str.startswith('#'):
        color_str = color_str.lstrip('#')
        if len(color_str) != 6:
            raise ValueError("Hex color must be 6 characters (RRGGBB)")
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return (r, g, b)
    
    # Handle RGB format
    parts = color_str.split(',')
    if len(parts) != 3:
        raise ValueError("RGB color must be in format 'R,G,B'")
    
    r, g, b = [int(p.strip()) for p in parts]
    
    if not all(0 <= c <= 255 for c in (r, g, b)):
        raise ValueError("RGB values must be between 0 and 255")
    
    return (r, g, b)


def main():
    """Main entry point for the pixelizer tool."""
    parser = argparse.ArgumentParser(
        description='Convert PNG images to BMP format with transparent pixel handling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file conversion
  %(prog)s input.png output.bmp
  %(prog)s input.png output.bmp --bg-color 255,255,255
  %(prog)s input.png output.bmp --bg-color #FF0000 --no-aspect
  %(prog)s input.png  # Auto-generates output filename
  
  # Batch process airline logos
  %(prog)s --airline-logos --size 30
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input PNG file path')
    parser.add_argument('output', nargs='?', help='Output BMP file path (optional, auto-generated if not provided)')
    parser.add_argument('--airline-logos', action='store_true',
                        help='Process all airline logos in static/airline_logos/ directory')
    parser.add_argument('--size', type=int, default=40,
                        help='Target size for width and height in pixels (default: 40)')
    parser.add_argument('--bg-color', '--background', default='0,0,0',
                        help='Background color for transparent pixels (RGB format: "R,G,B" or hex: "#RRGGBB") (default: 0,0,0 black)')
    parser.add_argument('--no-aspect', action='store_true',
                        help='Do not maintain aspect ratio (stretches image to fill target size)')
    parser.add_argument('--filter', choices=['lanczos', 'bilinear', 'bicubic', 'nearest'],
                        default='lanczos', help='Resampling filter for resize (default: lanczos)')
    
    args = parser.parse_args()
    
    # Parse background color
    try:
        bg_color = parse_color(args.bg_color)
    except ValueError as e:
        print(f"✗ Error parsing background color: {e}", file=sys.stderr)
        return 1
    
    # Handle airline logos batch processing mode
    if args.airline_logos:
        target_size = (args.size, args.size)
        count = process_airline_logos(
            size=target_size,
            bg_color=bg_color
        )
        return 0 if count > 0 else 1
    
    # Single file mode - require input file
    if args.input is None:
        parser.error("Input file is required unless using --airline-logos")
    
    # Auto-generate output filename if not provided
    if args.output is None:
        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}_{args.size}x{args.size}.bmp"
    
    # Map filter names to PIL constants
    filter_map = {
        'lanczos': Image.Resampling.LANCZOS,
        'bilinear': Image.Resampling.BILINEAR,
        'bicubic': Image.Resampling.BICUBIC,
        'nearest': Image.Resampling.NEAREST
    }
    
    # Convert the image
    target_size = (args.size, args.size)
    success = convert_png_to_bmp(
        args.input,
        args.output,
        bg_color=bg_color,
        maintain_aspect=not args.no_aspect,
        resample_filter=filter_map[args.filter],
        target_size=target_size
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
