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
import magic

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

def is_heic_file(file_path):
    """
    Check if a file is actually a HEIC/HEIF file using multiple methods.
    
    Args:
        file_path (Path): Path to the file to check
        
    Returns:
        bool: True if file is HEIC/HEIF, False otherwise
    """
    try:
        # Method 1: Check file extension
        heic_extensions = {'.heic', '.heif', '.HEIC', '.HEIF'}
        if file_path.suffix not in heic_extensions:
            return False
        
        # Method 2: Check file magic bytes/MIME type
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type in ['image/heic', 'image/heif', 'image/heic-sequence', 'image/heif-sequence']:
                return True
        except Exception as e:
            logger.debug(f"Magic detection failed for {file_path.name}: {e}")
        
        # Method 3: Try to read file header manually
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                # HEIC files start with specific byte patterns
                if len(header) >= 12:
                    # Check for 'ftyp' at offset 4 and HEIC/HEIF identifiers
                    if (header[4:8] == b'ftyp' and 
                        (b'heic' in header or b'heix' in header or b'hevc' in header or 
                         b'mif1' in header or b'msf1' in header)):
                        return True
        except Exception as e:
            logger.debug(f"Header check failed for {file_path.name}: {e}")
        
        # Method 4: Try opening with pillow_heif directly
        try:
            heif_file = pillow_heif.open_heif(str(file_path))
            if heif_file:
                return True
        except Exception as e:
            logger.debug(f"pillow_heif check failed for {file_path.name}: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if {file_path.name} is HEIC: {e}")
        return False

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
        # First, validate that this is actually a HEIC file
        if not is_heic_file(input_path):
            logger.error(f"File {input_path.name} is not a valid HEIC file")
            return False
        
        # Check file size and readability
        if not input_path.exists() or input_path.stat().st_size == 0:
            logger.error(f"File {input_path.name} is empty or does not exist")
            return False
        
        # Method 1: Try with PIL and pillow_heif
        try:
            with Image.open(input_path) as image:
                # Convert to RGB if necessary (HEIC can have different color modes)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save as JPEG
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
            logger.info(f"Successfully converted: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as pil_error:
            logger.warning(f"PIL conversion failed for {input_path.name}: {pil_error}")
            
            # Method 2: Try direct pillow_heif approach
            try:
                heif_file = pillow_heif.open_heif(str(input_path))
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save as JPEG
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                logger.info(f"Successfully converted (direct method): {input_path.name} -> {output_path.name}")
                return True
                
            except Exception as direct_error:
                logger.error(f"Both conversion methods failed for {input_path.name}:")
                logger.error(f"  PIL error: {pil_error}")
                logger.error(f"  Direct error: {direct_error}")
                return False
        
    except Exception as e:
        logger.error(f"Unexpected error converting {input_path.name}: {str(e)}")
        return False

def get_heic_files(directory):
    """
    Get all HEIC files from the specified directory.
    
    Args:
        directory (Path): Directory to search for HEIC files
        
    Returns:
        list: List of Path objects for HEIC files
    """
    heic_files = []
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            # Use our robust HEIC detection
            if is_heic_file(file_path):
                heic_files.append(file_path)
            else:
                # Log files that have HEIC extensions but aren't valid HEIC files
                heic_extensions = {'.heic', '.heif', '.HEIC', '.HEIF'}
                if file_path.suffix in heic_extensions:
                    logger.warning(f"File {file_path.name} has HEIC extension but is not a valid HEIC file")
    
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
