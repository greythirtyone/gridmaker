#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid Maker Script

This script overlays a configurable grid with alphabetic column labels and 
numeric row labels on an input image.

Usage:
    python grid_maker.py input_image.png [options]

Options:
    --spacing PIXELS     Grid line spacing in pixels (default: 100)
    --color R G B        Grid line RGB color (default: 0 0 255 for blue)
    --opacity VALUE      Grid line opacity from 0-255 (default: 128)
    --thickness PIXELS   Line thickness in pixels (default: 2)
    --output FILENAME    Output filename (default: input_base_grid.png)
    --debug              Enable debug mode with additional logging
"""

import argparse
import logging
import os
import sys
from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Create a labeled grid overlay on an image')
    
    parser.add_argument('input_image', help='Path to the input image')
    parser.add_argument('--spacing', type=int, default=100,
                      help='Grid line spacing in pixels (default: 100)')
    parser.add_argument('--color', type=int, nargs=3, default=[0, 0, 255],
                      help='Grid line RGB color (default: 0 0 255 for blue)')
    parser.add_argument('--opacity', type=int, default=128,
                      help='Grid line opacity from 0-255 (default: 128)')
    parser.add_argument('--thickness', type=int, default=2,
                      help='Line thickness in pixels (default: 2)')
    parser.add_argument('--output', type=str,
                      help='Output filename (default: input_base_grid.png)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode with additional logging')
    
    return parser.parse_args()

def get_column_label(index: int) -> str:
    """
    Convert a column index to an alphabetic label (A, B, ..., Z, AA, AB, ...).
    
    Args:
        index: 0-based index of the column
        
    Returns:
        Alphabetic label for the column
    """
    if index < 26:
        return chr(65 + index)  # A-Z
    else:
        # For columns after Z (AA, AB, etc.)
        return chr(65 + (index // 26) - 1) + chr(65 + (index % 26))

def draw_grid(
    image: Image.Image,
    spacing: int,
    color: Tuple[int, int, int],
    opacity: int,
    thickness: int
) -> Image.Image:
    """
    Draw a grid on the image with the specified parameters.
    
    Args:
        image: PIL Image object
        spacing: Grid line spacing in pixels
        color: RGB color tuple for grid lines
        opacity: Opacity value (0-255)
        thickness: Line thickness in pixels
        
    Returns:
        PIL Image with grid overlay
    """
    # Create a grid overlay with the same size as the input image
    width, height = image.size
    
    # Create a transparent overlay for the grid
    grid_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid_overlay)
    
    # Get a suitable font size based on image dimensions
    font_size = max(12, min(24, spacing // 5))
    try:
        font = ImageFont.truetype("Arial.ttf", font_size)
    except IOError:
        # Try a few system fonts if Arial is not available
        system_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Windows/Fonts/arial.ttf"
        ]
        
        for font_path in system_fonts:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except IOError:
                continue
        else:
            # If no fonts are found, use the default
            font = ImageFont.load_default()
            logger.warning("Could not load a TrueType font, using default font")
    
    # Grid color with opacity
    grid_color = color + (opacity,)
    
    # Calculate the number of horizontal and vertical lines
    num_horizontal = height // spacing + 1
    num_vertical = width // spacing + 1
    
    logger.info(f"Creating grid with {num_horizontal} rows and {num_vertical} columns")
    logger.info(f"Grid spacing: {spacing}px, Line thickness: {thickness}px")
    
    # Draw horizontal grid lines and row labels
    for i in range(num_horizontal):
        y = i * spacing
        if y >= height:
            continue
            
        # Draw the horizontal line
        draw.line([(0, y), (width, y)], fill=grid_color, width=thickness)
        
        # Add row label (1-based)
        row_label = str(i + 1)
        
        # Draw white background for better visibility
        # Position just below the line
        label_y = y + thickness + 2
        label_bbox = draw.textbbox((10, label_y), row_label, font=font)
        bg_box = [
            label_bbox[0] - 2,
            label_bbox[1] - 2,
            label_bbox[2] + 2,
            label_bbox[3] + 2
        ]
        draw.rectangle(bg_box, fill=(255, 255, 255, 200))
        
        # Draw the text
        draw.text((10, label_y), row_label, fill=(0, 0, 0, 255), font=font)
    
    # Draw vertical grid lines and column labels
    for i in range(num_vertical):
        x = i * spacing
        if x >= width:
            continue
            
        # Draw the vertical line
        draw.line([(x, 0), (x, height)], fill=grid_color, width=thickness)
        
        # Add column label (A, B, C, ...)
        col_label = get_column_label(i)
        
        # Draw white background for better visibility
        # Position just right of the line
        label_x = x + thickness + 2
        label_bbox = draw.textbbox((label_x, 10), col_label, font=font)
        bg_box = [
            label_bbox[0] - 2,
            label_bbox[1] - 2,
            label_bbox[2] + 2,
            label_bbox[3] + 2
        ]
        draw.rectangle(bg_box, fill=(255, 255, 255, 200))
        
        # Draw the text
        draw.text((label_x, 10), col_label, fill=(0, 0, 0, 255), font=font)
    
    # Composite the grid overlay onto the original image
    result = Image.alpha_composite(image.convert("RGBA"), grid_overlay)
    return result

def main() -> int:
    """Main function to overlay a grid on an image."""
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    try:
        # Validate input file
        if not os.path.exists(args.input_image):
            raise FileNotFoundError(f"Input file not found: {args.input_image}")
        
        # Open input image
        logger.info(f"Opening image: {args.input_image}")
        try:
            image = Image.open(args.input_image)
            logger.debug(f"Image format: {image.format}, Size: {image.size}, Mode: {image.mode}")
        except Exception as e:
            raise ValueError(f"Failed to open image: {e}")
        
        # Validate opacity
        if not 0 <= args.opacity <= 255:
            logger.warning(f"Invalid opacity value: {args.opacity}. Using default: 128")
            args.opacity = 128
        
        # Generate output path if not provided
        if args.output is None:
            base_name = os.path.splitext(os.path.basename(args.input_image))[0]
            args.output = f"{base_name}_grid.png"
            logger.debug(f"Using default output name: {args.output}")
        
        # Ensure the image is in RGBA mode
        if image.mode != 'RGBA':
            logger.debug(f"Converting image from {image.mode} to RGBA")
            image = image.convert('RGBA')
        
        # Draw the grid on the image
        grid_image = draw_grid(
            image, 
            args.spacing, 
            tuple(args.color), 
            args.opacity, 
            args.thickness
        )
        
        # Save the output image
        logger.info(f"Saving grid image to: {args.output}")
        grid_image.save(args.output, format="PNG")
        
        print(f"Successfully created grid overlay: {args.output}")
        return 0
        
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
        
    except ValueError as e:
        logger.error(str(e))
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
