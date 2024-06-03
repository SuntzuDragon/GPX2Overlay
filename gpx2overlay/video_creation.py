import subprocess

def create_video(ffmpeg_executable, image_pattern, fps, video_file):
    nvenc_check_cmd = [ffmpeg_executable, '-v', 'error', '-encoders']
    nvenc_check_result = subprocess.run(nvenc_check_cmd, capture_output=True, text=True)
    encoder = 'h264_nvenc' if 'h264_nvenc' in nvenc_check_result.stdout else 'libx264'
    
    if encoder == 'h264_nvenc':
        print('NVENC is supported. Using NVENC for hardware acceleration.')
    else:
        print('NVENC is not supported. Falling back to libx264 for software encoding.')
    
    ffmpeg_cmd = [
        ffmpeg_executable,
        '-y',
        '-framerate', str(fps),
        '-i', image_pattern,
        '-c:v', encoder,
        '-pix_fmt', 'yuv420p',
        '-r', str(fps),
        video_file
    ]

    print(f'Creating video {video_file}...')
    subprocess.run(ffmpeg_cmd, check=True)
    print(f'Video saved as {video_file}')
