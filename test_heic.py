#!/usr/bin/env python3
"""
HEIC File Diagnostic Tool

This script helps diagnose issues with HEIC files and provides detailed information
about what might be preventing conversion.
"""

import sys
from pathlib import Path
from PIL import Image
import pillow_heif
import logging

# Configure logging for detailed output
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Register HEIF opener
pillow_heif.register_heif_opener()

def diagnose_heic_file(file_path):
    """Diagnose a single HEIC file and report all findings."""
    
    print(f"\n{'='*60}")
    print(f"DIAGNOSING: {file_path}")
    print(f"{'='*60}")
    
    # Basic file checks
    if not file_path.exists():
        print("❌ File does not exist")
        return
    
    if not file_path.is_file():
        print("❌ Path is not a file")
        return
    
    file_size = file_path.stat().st_size
    print(f"✅ File exists and is {file_size:,} bytes")
    
    if file_size == 0:
        print("❌ File is empty")
        return
    
    # Extension check
    print(f"📁 Extension: {file_path.suffix}")
    heic_extensions = {'.heic', '.heif', '.HEIC', '.HEIF'}
    if file_path.suffix in heic_extensions:
        print("✅ Has HEIC extension")
    else:
        print("⚠️  Does not have HEIC extension")
    
    # Try to detect MIME type
    try:
        import magic
        mime_type = magic.from_file(str(file_path), mime=True)
        print(f"🔍 MIME type: {mime_type}")
        
        if mime_type in ['image/heic', 'image/heif', 'image/heic-sequence', 'image/heif-sequence']:
            print("✅ MIME type indicates HEIC/HEIF")
        else:
            print("⚠️  MIME type does not indicate HEIC/HEIF")
    except ImportError:
        print("⚠️  python-magic not available for MIME detection")
    except Exception as e:
        print(f"❌ MIME detection failed: {e}")
    
    # Check file header
    try:
        with open(file_path, 'rb') as f:
            header = f.read(20)
            print(f"🔍 File header (hex): {header[:20].hex()}")
            print(f"🔍 File header (ascii): {header[:20]}")
            
            if len(header) >= 12:
                if header[4:8] == b'ftyp':
                    print("✅ Has 'ftyp' signature at offset 4")
                    
                    # Check for HEIC identifiers
                    heic_markers = [b'heic', b'heix', b'hevc', b'mif1', b'msf1']
                    found_markers = [marker for marker in heic_markers if marker in header]
                    if found_markers:
                        print(f"✅ Found HEIC markers: {found_markers}")
                    else:
                        print("❌ No HEIC markers found in header")
                else:
                    print("❌ No 'ftyp' signature found")
    except Exception as e:
        print(f"❌ Header analysis failed: {e}")
    
    # Try pillow_heif directly
    print("\n🔧 Testing pillow_heif direct access...")
    try:
        heif_file = pillow_heif.open_heif(str(file_path))
        if heif_file:
            print(f"✅ pillow_heif can open file")
            print(f"   Mode: {heif_file.mode}")
            print(f"   Size: {heif_file.size}")
            print(f"   Has alpha: {heif_file.has_alpha}")
        else:
            print("❌ pillow_heif returned None")
    except Exception as e:
        print(f"❌ pillow_heif failed: {e}")
    
    # Try PIL with pillow_heif
    print("\n🔧 Testing PIL with pillow_heif...")
    try:
        with Image.open(file_path) as image:
            print(f"✅ PIL can open file")
            print(f"   Format: {image.format}")
            print(f"   Mode: {image.mode}")
            print(f"   Size: {image.size}")
        
        # Try a test conversion
        print("\n🔧 Testing conversion...")
        test_output = file_path.parent / f"{file_path.stem}_test.jpg"
        try:
            with Image.open(file_path) as image:
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(test_output, 'JPEG', quality=95)
            print(f"✅ Test conversion successful: {test_output}")
            
            # Clean up test file
            if test_output.exists():
                test_output.unlink()
                
        except Exception as conv_e:
            print(f"❌ Test conversion failed: {conv_e}")
            
    except Exception as e:
        print(f"❌ PIL failed: {e}")

def main():
    """Main function to diagnose HEIC files."""
    
    if len(sys.argv) > 1:
        # Diagnose specific file
        file_path = Path(sys.argv[1])
        diagnose_heic_file(file_path)
    else:
        # Diagnose all HEIC files in photos directory
        photos_dir = Path('/app/photos') if Path('/app/photos').exists() else Path('./photos')
        
        if not photos_dir.exists():
            print(f"Photos directory not found: {photos_dir}")
            sys.exit(1)
        
        heic_extensions = {'.heic', '.heif', '.HEIC', '.HEIF'}
        heic_files = [f for f in photos_dir.iterdir() 
                     if f.is_file() and f.suffix in heic_extensions]
        
        if not heic_files:
            print("No HEIC files found in photos directory")
            return
        
        print(f"Found {len(heic_files)} potential HEIC files")
        
        for heic_file in heic_files:
            diagnose_heic_file(heic_file)

if __name__ == "__main__":
    main()
