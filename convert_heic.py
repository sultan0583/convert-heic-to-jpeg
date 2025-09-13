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

# Import additional libraries for fallback methods
try:
    import pyheif
    PYHEIF_AVAILABLE = True
except ImportError:
    PYHEIF_AVAILABLE = False
    
try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False

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
    Convert a single HEIC file to JPEG format using multiple fallback methods.
    
    Args:
        input_path (Path): Path to the input HEIC file
        output_path (Path): Path for the output JPEG file
        quality (int): JPEG quality (1-100)
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    conversion_methods = []
    
    try:
        # First, validate that this is actually a HEIC file
        if not is_heic_file(input_path):
            logger.error(f"File {input_path.name} is not a valid HEIC file")
            return False
        
        # Check file size and readability
        if not input_path.exists() or input_path.stat().st_size == 0:
            logger.error(f"File {input_path.name} is empty or does not exist")
            return False
        
        # Method 1: Try with PIL and pillow_heif (standard approach)
        try:
            with Image.open(input_path) as image:
                # Handle different color modes
                if image.mode in ['RGBA', 'LA']:
                    # Create white background for transparency
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save as JPEG
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
            logger.info(f"Successfully converted (PIL method): {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as pil_error:
            conversion_methods.append(f"PIL method failed: {pil_error}")
            logger.debug(f"PIL conversion failed for {input_path.name}: {pil_error}")
            
            # Method 2: Try direct pillow_heif with improved error handling
            try:
                heif_file = pillow_heif.open_heif(str(input_path), convert_hdr_to_8bit=True, bgr_mode=False)
                
                # Try to get the primary image if multiple images exist
                if hasattr(heif_file, 'primary_image'):
                    heif_data = heif_file.primary_image()
                else:
                    heif_data = heif_file
                
                # Create PIL image with proper handling
                image = Image.frombytes(
                    heif_data.mode,
                    heif_data.size,
                    heif_data.data,
                    "raw",
                )
                
                # Handle different color modes
                if image.mode in ['RGBA', 'LA']:
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save as JPEG
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                logger.info(f"Successfully converted (direct pillow_heif): {input_path.name} -> {output_path.name}")
                return True
                
            except Exception as direct_error:
                conversion_methods.append(f"Direct pillow_heif failed: {direct_error}")
                logger.debug(f"Direct pillow_heif failed for {input_path.name}: {direct_error}")
                
                # Method 3: Try with pyheif if available
                if PYHEIF_AVAILABLE:
                    try:
                        heif_file = pyheif.read(str(input_path))
                        image = Image.frombytes(
                            heif_file.mode,
                            heif_file.size,
                            heif_file.data,
                            "raw",
                            heif_file.mode,
                            heif_file.stride,
                        )
                        
                        # Handle color modes
                        if image.mode in ['RGBA', 'LA']:
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'RGBA':
                                background.paste(image, mask=image.split()[-1])
                            else:
                                background.paste(image, mask=image.split()[-1])
                            image = background
                        elif image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        image.save(output_path, 'JPEG', quality=quality, optimize=True)
                        
                        logger.info(f"Successfully converted (pyheif method): {input_path.name} -> {output_path.name}")
                        return True
                        
                    except Exception as pyheif_error:
                        conversion_methods.append(f"pyheif method failed: {pyheif_error}")
                        logger.debug(f"pyheif conversion failed for {input_path.name}: {pyheif_error}")
                
                # Method 4: Try with imageio if available
                if IMAGEIO_AVAILABLE:
                    try:
                        # Read with imageio
                        image_data = imageio.imread(str(input_path))
                        
                        # Convert numpy array to PIL Image
                        if len(image_data.shape) == 3 and image_data.shape[2] == 4:
                            # Handle RGBA
                            image = Image.fromarray(image_data, 'RGBA')
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            background.paste(image, mask=image.split()[-1])
                            image = background
                        else:
                            image = Image.fromarray(image_data)
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                        
                        image.save(output_path, 'JPEG', quality=quality, optimize=True)
                        
                        logger.info(f"Successfully converted (imageio method): {input_path.name} -> {output_path.name}")
                        return True
                        
                    except Exception as imageio_error:
                        conversion_methods.append(f"imageio method failed: {imageio_error}")
                        logger.debug(f"imageio conversion failed for {input_path.name}: {imageio_error}")
                
                # All methods failed
                logger.error(f"All conversion methods failed for {input_path.name}:")
                for i, method_error in enumerate(conversion_methods, 1):
                    logger.error(f"  Method {i}: {method_error}")
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
    
    # Log available conversion methods
    available_methods = ["pillow_heif + PIL"]
    if PYHEIF_AVAILABLE:
        available_methods.append("pyheif")
    if IMAGEIO_AVAILABLE:
        available_methods.append("imageio")
    
    logger.info(f"Available conversion methods: {', '.join(available_methods)}")
    
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
