
# gpx2Overlay

gpx2Overlay is a Python script that generates a video overlay from GPX files. It creates a series of transparent images with an overlay of the GPS route and a dot indicating the current position, and then combines them into a video file.

## Features

- Parse GPX files to extract GPS coordinates and timestamps
- Generate transparent images showing the GPS route and current position
- Create a video from the generated images using FFmpeg
- Support for hardware-accelerated video encoding with NVENC if available, falling back to libx264 otherwise

## Requirements

- Python 3.6 or higher
- `gpxpy`, `pandas`, `Pillow`, `tqdm`, `requests`, `zipfile36`
- FFmpeg (automatically downloaded if not found)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/gpx2Overlay.git
   cd gpx2Overlay
   ```

2. Create a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

## Usage

1. Place your GPX file in the directory.

2. Run the script:
   ```sh
   python gpx2Overlay.py path_to_your_gpx_file.gpx --output_dir output_images --fps 30 --video_file output_video.mov
   ```

   - `path_to_your_gpx_file.gpx`: Path to your GPX file.
   - `--output_dir`: Directory to save the generated images (default: `output_images`).
   - `--fps`: Frames per second for the video (default: 30).
   - `--video_file`: Output video file name (default: `output_video.mov`).

## Example

```sh
python gpx2Overlay.py ./New_shoes_.gpx --output_dir ./output_images --fps 30 --video_file output_video.mov
```

## How It Works

1. **Download and Extract FFmpeg**:
   - The script checks if FFmpeg is available. If not, it downloads and extracts FFmpeg for Windows or macOS.
   
2. **Parse GPX File**:
   - The script uses `gpxpy` to parse the GPX file and extract GPS coordinates and timestamps.
   
3. **Generate Images**:
   - The script generates transparent images showing the GPS route and current position using `Pillow`.
   
4. **Create Video**:
   - The script uses FFmpeg to create a video from the generated images. It utilizes NVENC for hardware-accelerated encoding if available, falling back to `libx264` otherwise.

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
