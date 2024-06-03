import os
import platform
import requests
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
        if os.path.exists(output_dir):
            print(f'FFmpeg found: {output_dir}')
            return find_ffmpeg_executable(output_dir, system)

        print(f'Downloading FFmpeg from {ffmpeg_url}...')
        response = requests.get(ffmpeg_url, stream=True)
        if response.status_code == 200:
            with open('ffmpeg.zip', 'wb') as f:
                f.write(response.content)
            print('Download completed.')

            print('Extracting FFmpeg...')
            with zipfile.ZipFile('ffmpeg.zip', 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print('Extraction completed.')
            os.remove('ffmpeg.zip')

            if system == 'Darwin':
                ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
                os.chmod(ffmpeg_executable, 0o755)

            print(f'FFmpeg is ready to use: {find_ffmpeg_executable(output_dir, system)}')
            return find_ffmpeg_executable(output_dir, system)
        else:
            print('Failed to download FFmpeg.')
            return None
    else:
        print('Unsupported operating system for automated FFmpeg download.')
        return None

def find_ffmpeg_executable(output_dir, system):
    if system == 'Darwin':
        ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
        if not os.path.isfile(ffmpeg_executable):
            for root, dirs, files in os.walk(output_dir):
                if 'ffmpeg' in files:
                    return os.path.join(root, 'ffmpeg')
    elif system == 'Windows':
        ffmpeg_executable = os.path.join(output_dir, 'bin', 'ffmpeg.exe')
        if not os.path.isfile(ffmpeg_executable):
            for root, dirs, files in os.walk(output_dir):
                if 'ffmpeg.exe' in files:
                    return os.path.join(root, 'ffmpeg.exe')
    return None
