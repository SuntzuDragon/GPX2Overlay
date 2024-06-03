import argparse
import gpxpy
import pandas as pd
import os
from PIL import Image, ImageDraw
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import requests
import platform
import zipfile
import shutil

def download_and_extract_ffmpeg():
    system = platform.system()
    ffmpeg_url = ''
    output_dir = 'ffmpeg'

    if system == 'Windows':
        ffmpeg_url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    elif system == 'Darwin':  # macOS
        ffmpeg_url = 'https://evermeet.cx/ffmpeg/getrelease/zip'

    if ffmpeg_url:
        # Check if the ffmpeg directory already exists
        if os.path.exists(output_dir):
            print(f'FFmpeg directory already exists: {output_dir}')
            if system == 'Darwin':
                ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
                if not os.path.isfile(ffmpeg_executable):
                    for root, dirs, files in os.walk(output_dir):
                        if 'ffmpeg' in files:
                            ffmpeg_executable = os.path.join(root, 'ffmpeg')
                            break
            elif system == 'Windows':
                ffmpeg_executable = os.path.join(output_dir, 'bin', 'ffmpeg.exe')
                if not os.path.isfile(ffmpeg_executable):
                    for root, dirs, files in os.walk(output_dir):
                        if 'ffmpeg.exe' in files:
                            ffmpeg_executable = os.path.join(root, 'ffmpeg.exe')
                            break
            return ffmpeg_executable

        # Download FFmpeg
        print(f'Downloading FFmpeg from {ffmpeg_url}...')
        response = requests.get(ffmpeg_url, stream=True)
        if response.status_code == 200:
            with open('ffmpeg.zip', 'wb') as f:
                f.write(response.content)
            print('Download completed.')

            # Extract FFmpeg
            print('Extracting FFmpeg...')
            with zipfile.ZipFile('ffmpeg.zip', 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print('Extraction completed.')

            # Cleanup
            os.remove('ffmpeg.zip')

            # Ensure ffmpeg binary is executable
            if system == 'Darwin':  # macOS
                ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
                if not os.path.isfile(ffmpeg_executable):
                    for root, dirs, files in os.walk(output_dir):
                        if 'ffmpeg' in files:
                            ffmpeg_executable = os.path.join(root, 'ffmpeg')
                            break
                os.chmod(ffmpeg_executable, 0o755)

            elif system == 'Windows':
                ffmpeg_executable = os.path.join(output_dir, 'bin', 'ffmpeg.exe')
                if not os.path.isfile(ffmpeg_executable):
                    for root, dirs, files in os.walk(output_dir):
                        if 'ffmpeg.exe' in files:
                            ffmpeg_executable = os.path.join(root, 'ffmpeg.exe')
                            break

            print(f'FFmpeg is ready to use: {ffmpeg_executable}')
            return ffmpeg_executable
        else:
            print('Failed to download FFmpeg.')
            return None
    else:
        print('Unsupported operating system for automated FFmpeg download.')
        return None

# Check for FFmpeg availability and download if necessary
ffmpeg_executable = shutil.which('ffmpeg')
if not ffmpeg_executable:
    ffmpeg_executable = download_and_extract_ffmpeg()
    if not ffmpeg_executable:
        raise EnvironmentError('FFmpeg is required but could not be downloaded or found.')

# Set up argument parser
parser = argparse.ArgumentParser(description='Create video overlay from GPX file.')
parser.add_argument('gpx_file', type=str, help='Path to the GPX file')
parser.add_argument('--output_dir', type=str, default='output_images', help='Directory to save the generated images')
parser.add_argument('--fps', type=int, default=30, help='Frames per second for the video')
parser.add_argument('--video_file', type=str, default='output_video.mov', help='Output video file name')
args = parser.parse_args()

# Load and parse the GPX file
with open(args.gpx_file, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Extract points
points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append((point.latitude, point.longitude, point.time, point.elevation))

# Convert to DataFrame
points_df = pd.DataFrame(points, columns=['latitude', 'longitude', 'time', 'elevation'])

# Calculate normalization parameters
lat_min, lat_max = points_df['latitude'].min(), points_df['latitude'].max()
lon_min, lon_max = points_df['longitude'].min(), points_df['longitude'].max()

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

# Normalize coordinates
points_df['normalized_latitude'] = points_df['latitude'].apply(lambda x: normalize(x, lat_min, lat_max))
points_df['normalized_longitude'] = points_df['longitude'].apply(lambda x: normalize(x, lon_min, lon_max))

# Create output directory if it doesn't exist
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# Image size
img_size = (800, 800)

# Draw the overall route once and save to use in all frames
route_image = Image.new('RGBA', img_size, (0, 0, 0, 0))
route_draw = ImageDraw.Draw(route_image)
for i in range(1, len(points_df)):
    route_draw.line(
        [
            (points_df['normalized_longitude'].iloc[i-1] * img_size[0], img_size[1] - points_df['normalized_latitude'].iloc[i-1] * img_size[1]),
            (points_df['normalized_longitude'].iloc[i] * img_size[0], img_size[1] - points_df['normalized_latitude'].iloc[i] * img_size[1])
        ],
        fill="white",
        width=3
    )

def generate_image(index, row, base_image):
    img = base_image.copy()
    draw = ImageDraw.Draw(img)

    # Draw the current position
    x = row['normalized_longitude'] * img_size[0]
    y = img_size[1] - row['normalized_latitude'] * img_size[1]
    draw.ellipse([x-5, y-5, x+5, y+5], fill="orange")

    # Save the image
    img.save(os.path.join(args.output_dir, f'frame_{index+1:04d}.png'))

# Multithreading image generation
with ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(generate_image, index, row, route_image)
        for index, row in points_df.iterrows()
    ]
    for future in tqdm(as_completed(futures), total=len(futures), desc="Generating images"):
        future.result()

print(f'Images saved in directory: {args.output_dir}')

# Step 3: Create the video using ffmpeg
image_pattern = os.path.join(args.output_dir, 'frame_%04d.png')
ffmpeg_cmd = [
    ffmpeg_executable,
    '-y',  # Add the -y flag to overwrite the output file without asking
    '-framerate', str(args.fps),
    '-i', image_pattern,
    '-c:v', 'qtrle',
    '-pix_fmt', 'argb',
    '-r', str(args.fps),
    args.video_file
]

print(f'Creating video {args.video_file}...')
subprocess.run(ffmpeg_cmd, check=True)
print(f'Video saved as {args.video_file}')
