import os
import platform
import requests
import zipfile


def download_and_extract_ffmpeg():
    system = platform.system()
    ffmpeg_url = get_ffmpeg_url(system)
    output_dir = 'ffmpeg'

    if not ffmpeg_url:
        print('Unsupported operating system for automated FFmpeg download.')
        return None

    if os.path.exists(output_dir):
        print(f'FFmpeg found: {output_dir}')
        return find_ffmpeg_executable(output_dir, system)

    try:
        download_ffmpeg(ffmpeg_url, 'ffmpeg.zip')
        extract_ffmpeg('ffmpeg.zip', output_dir)
        os.remove('ffmpeg.zip')
        if system == 'Darwin':
            ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
            os.chmod(ffmpeg_executable, 0o755)
        print(f'FFmpeg is ready to use: {
              find_ffmpeg_executable(output_dir, system)}')
        return find_ffmpeg_executable(output_dir, system)
    except Exception as e:
        print(f'Failed to download and extract FFmpeg: {e}')
        return None


def get_ffmpeg_url(system):
    if system == 'Windows':
        return 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
    elif system == 'Darwin':  # macOS
        return 'https://evermeet.cx/ffmpeg/getrelease/zip'
    return None


def download_ffmpeg(url, output_file):
    print(f'Downloading FFmpeg from {url}...')
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print('Download completed.')


def extract_ffmpeg(zip_file, output_dir):
    print('Extracting FFmpeg...')
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print('Extraction completed.')


def find_ffmpeg_executable(output_dir, system):
    if system == 'Darwin':
        ffmpeg_executable = os.path.join(output_dir, 'ffmpeg')
    elif system == 'Windows':
        ffmpeg_executable = os.path.join(output_dir, 'bin', 'ffmpeg.exe')

    if os.path.isfile(ffmpeg_executable):
        return ffmpeg_executable

    for root, _, files in os.walk(output_dir):
        if 'ffmpeg' in files or 'ffmpeg.exe' in files:
            return os.path.join(root, 'ffmpeg' if system == 'Darwin' else 'ffmpeg.exe')

    return None
