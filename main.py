import shutil
from gpx2overlay import download_and_extract_ffmpeg, create_frames, create_video, parse_arguments, load_gpx


def main():
    args = parse_arguments()

    ffmpeg_executable = shutil.which('ffmpeg')
    if not ffmpeg_executable:
        ffmpeg_executable = download_and_extract_ffmpeg()
        if not ffmpeg_executable:
            raise EnvironmentError(
                'FFmpeg is required but could not be downloaded or found.')

    points_df = load_gpx(args.gpx_file)

    image_pattern = 'frame_%04d.png'
    create_frames(points_df, args.output_dir, image_pattern, (800, 800))
    create_video(ffmpeg_executable, args.output_dir,
                 image_pattern, args.fps, args.video_file)


if __name__ == "__main__":
    main()
