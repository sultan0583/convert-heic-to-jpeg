# HEIC to JPEG Converter

A Dockerized Python application that converts HEIC (High Efficiency Image Container) files to JPEG format. The app automatically processes all HEIC files in the `photos` directory and converts them to high-quality JPEG images.

## Features

-   🔄 Batch conversion of all HEIC files in a directory
-   🐳 Fully containerized with Docker
-   📝 Comprehensive logging with both console and file output
-   ⚡ High-quality JPEG output (95% quality by default)
-   🔍 Automatic file detection (supports .heic, .heif, .HEIC, .HEIF extensions)
-   🛡️ Skip existing JPEG files to avoid overwriting
-   📊 Conversion summary with success/failure counts

## Prerequisites

-   Docker
-   Docker Compose (optional, but recommended)

## Quick Start

### Method 1: Using Docker Compose (Recommended)

1. **Place your HEIC files** in the `photos` directory:

    ```bash
    cp /path/to/your/heic/files/* ./photos/
    ```

2. **Run the converter**:

    ```bash
    docker-compose up --build
    ```

3. **Check the results**: Your converted JPEG files will be in the `photos` directory alongside the original HEIC files.

### Method 2: Using Docker directly

1. **Build the Docker image**:

    ```bash
    docker build -t heic-converter .
    ```

2. **Run the container**:
    ```bash
    docker run --rm -v $(pwd)/photos:/app/photos -v $(pwd)/logs:/app/logs heic-converter
    ```

## Directory Structure

```
convert-heic-photos/
├── photos/                 # Place your HEIC files here
├── logs/                   # Conversion logs (created automatically)
├── convert_heic.py         # Main Python script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # This file
```

## Configuration

### Image Quality

By default, JPEG files are saved with 95% quality. To modify this, edit the `quality` parameter in `convert_heic.py`:

```python
image.save(output_path, 'JPEG', quality=95, optimize=True)
```

### Supported File Extensions

The converter automatically detects files with these extensions:

-   `.heic`
-   `.heif`
-   `.HEIC`
-   `.HEIF`

## Logging

The application provides detailed logging:

-   **Console output**: Real-time conversion progress
-   **Log file**: Persistent log saved to `conversion.log` (or `logs/conversion.log` when using volumes)

### Log Levels

-   `INFO`: Successful conversions and general information
-   `ERROR`: Failed conversions and critical errors

## Troubleshooting

### Common Issues

1. **"Photos directory not found"**

    - Ensure the `photos` directory exists in your project root
    - Check that Docker has permission to access the directory

2. **"No HEIC files found"**

    - Verify your files have the correct extensions (.heic, .heif, etc.)
    - Check that files are actually in the `photos` directory

3. **Conversion failures**
    - Check the logs for specific error messages
    - Ensure HEIC files are not corrupted
    - Verify sufficient disk space for converted files

### Performance Notes

-   Conversion time depends on image size and system performance
-   Large batches may take several minutes to complete
-   The container will automatically exit when conversion is complete

## Development

### Running Locally (without Docker)

1. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Modify the script** to use local paths instead of `/app/photos`

3. **Run the script**:
    ```bash
    python convert_heic.py
    ```

### Customization

The Python script can be easily modified to:

-   Change output directory
-   Adjust image quality settings
-   Add image resizing
-   Support additional input formats
-   Implement custom naming schemes

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
