import argparse
import gpxpy
import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Create video overlay from GPX file.')
    parser.add_argument('gpx_file', type=str, help='Path to the GPX file')
    parser.add_argument('--output_dir', type=str, default='output_images',
                        help='Directory to save the generated images')
    parser.add_argument('--fps', type=int, default=30,
                        help='Frames per second for the video')
    parser.add_argument('--video_file', type=str,
                        default='output_video.mov', help='Output video file name')
    return parser.parse_args()


def load_gpx(gpx_file):
    with open(gpx_file, 'r') as file:
        gpx = gpxpy.parse(file)

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude,
                              point.time, point.elevation))

    points_df = pd.DataFrame(
        points, columns=['latitude', 'longitude', 'time', 'elevation'])

    lat_min, lat_max = points_df['latitude'].min(), points_df['latitude'].max()
    lon_min, lon_max = points_df['longitude'].min(
    ), points_df['longitude'].max()

    points_df['normalized_latitude'] = points_df['latitude'].apply(
        lambda x: normalize(x, lat_min, lat_max))
    points_df['normalized_longitude'] = points_df['longitude'].apply(
        lambda x: normalize(x, lon_min, lon_max))

    return points_df


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)
