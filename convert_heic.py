#!/usr/bin/env python3
"""
HEIC to JPEG Converter

This script converts all HEIC files in the 'photos' directory to JPEG format.
The converted files are saved in the same directory with .jpg extension.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('conversion.log')
    ]
)

logger = logging.getLogger(__name__)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

def convert_heic_to_jpeg(input_path, output_path, quality=95):
    """
    Convert a single HEIC file to JPEG format.
    
    Args:
        input_path (Path): Path to the input HEIC file
        output_path (Path): Path for the output JPEG file
        quality (int): JPEG quality (1-100)
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        # Open and convert the HEIC image
        with Image.open(input_path) as image:
            # Convert to RGB if necessary (HEIC can have different color modes)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as JPEG
            image.save(output_path, 'JPEG', quality=quality, optimize=True)
            
        logger.info(f"Successfully converted: {input_path.name} -> {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to convert {input_path.name}: {str(e)}")
        return False

def get_heic_files(directory):
    """
    Get all HEIC files from the specified directory.
    
    Args:
        directory (Path): Directory to search for HEIC files
        
    Returns:
        list: List of Path objects for HEIC files
    """
    heic_extensions = {'.heic', '.heif', '.HEIC', '.HEIF'}
    heic_files = []
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix in heic_extensions:
            heic_files.append(file_path)
    
    return sorted(heic_files)

def main():
    """Main function to convert all HEIC files in the photos directory."""
    
    # Define the photos directory
    photos_dir = Path('/app/photos')
    
    # Check if photos directory exists
    if not photos_dir.exists():
        logger.error(f"Photos directory not found: {photos_dir}")
        sys.exit(1)
    
    if not photos_dir.is_dir():
        logger.error(f"Photos path is not a directory: {photos_dir}")
        sys.exit(1)
    
    # Get all HEIC files
    heic_files = get_heic_files(photos_dir)
    
    if not heic_files:
        logger.info("No HEIC files found in the photos directory.")
        return
    
    logger.info(f"Found {len(heic_files)} HEIC files to convert.")
    
    # Convert each HEIC file
    successful_conversions = 0
    failed_conversions = 0
    
    for heic_file in heic_files:
        # Create output filename (replace extension with .jpg)
        jpeg_filename = heic_file.stem + '.jpg'
        jpeg_path = photos_dir / jpeg_filename
        
        # Skip if JPEG already exists
        if jpeg_path.exists():
            logger.info(f"JPEG already exists, skipping: {jpeg_filename}")
            continue
        
        # Convert the file
        if convert_heic_to_jpeg(heic_file, jpeg_path):
            successful_conversions += 1
        else:
            failed_conversions += 1
    
    # Log summary
    logger.info(f"Conversion complete!")
    logger.info(f"Successful conversions: {successful_conversions}")
    logger.info(f"Failed conversions: {failed_conversions}")
    
    if failed_conversions > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
