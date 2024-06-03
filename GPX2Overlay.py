import argparse
import gpxpy
import pandas as pd
import os
from PIL import Image, ImageDraw
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up argument parser
parser = argparse.ArgumentParser(
    description='Create video overlay from GPX file.')
parser.add_argument('gpx_file', type=str, help='Path to the GPX file')
parser.add_argument('--output_dir', type=str, default='output_images',
                    help='Directory to save the generated images')
args = parser.parse_args()

# Load and parse the GPX file
with open(args.gpx_file, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Extract points
points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append((point.latitude, point.longitude,
                          point.time, point.elevation))

# Convert to DataFrame
points_df = pd.DataFrame(
    points, columns=['latitude', 'longitude', 'time', 'elevation'])

# Calculate normalization parameters
lat_min, lat_max = points_df['latitude'].min(), points_df['latitude'].max()
lon_min, lon_max = points_df['longitude'].min(), points_df['longitude'].max()


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


# Normalize coordinates
points_df['normalized_latitude'] = points_df['latitude'].apply(
    lambda x: normalize(x, lat_min, lat_max))
points_df['normalized_longitude'] = points_df['longitude'].apply(
    lambda x: normalize(x, lon_min, lon_max))

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
            (points_df['normalized_longitude'].iloc[i-1] * img_size[0],
             img_size[1] - points_df['normalized_latitude'].iloc[i-1] * img_size[1]),
            (points_df['normalized_longitude'].iloc[i] * img_size[0],
             img_size[1] - points_df['normalized_latitude'].iloc[i] * img_size[1])
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
