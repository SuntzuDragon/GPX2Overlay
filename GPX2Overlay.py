import argparse
import gpxpy
import pandas as pd

# Set up argument parser
parser = argparse.ArgumentParser(description='Create video overlay from GPX file.')
parser.add_argument('gpx_file', type=str, help='Path to the GPX file')
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
df = pd.DataFrame(points, columns=['latitude', 'longitude', 'time', 'elevation'])

# Calculate normalization parameters
lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
lon_min, lon_max = df['longitude'].min(), df['longitude'].max()