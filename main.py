import glob
import os
import subprocess
import sys
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime
from credentials import CLIENT_ID, CLIENT_SECRET


def get_oauth_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=payload)
    data = response.json()
    return data['access_token']


def get_user_id(oauth_token, channel_name):  # Retrieve user id for given channel name
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f"Bearer {oauth_token}"
    }
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][0]['id']


def get_monthly_clips(oauth_token, user_id, year, month):  # Get clips for user id for given month
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f"Bearer {oauth_token}"
    }

    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, 1) + pd.DateOffset(months=1)
    start_date = start_date.isoformat() + 'Z'  # Start of month at midnight
    end_date = end_date.isoformat() + 'Z'  # Start of following month at midnight
    print("Searching for clips between " + start_date + " and " + end_date)

    url = f'https://api.twitch.tv/helix/clips?broadcaster_id={user_id}&started_at={start_date}&ended_at={end_date}'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data']


def get_top_clips(clips, n):  # Function to get n most popular clips
    sorted_clips = sorted(clips, key=lambda x: x['view_count'], reverse=True)
    return sorted_clips[:n]


def download_clips(clips):  # Use Twitch-DL to download the list of provided clips
    for clip in clips:
        slug = clip['id']
        subprocess.run(
            ['twitch-dl', 'download', '-q', 'source', slug, '--overwrite', '--output',
             '{date} {title} {slug}.{format}'])


def overlay_text_on_clips():  # Use ffmpeg to label each clip
    mp4_files = glob.glob("./*.mp4")

    for input_filename in mp4_files:
        print(input_filename)
        output_filename = os.path.splitext(input_filename)[0] + "_overlay.mp4"
        filename_text = f"{Path(input_filename).stem}"
        # Files are saved with clip slug as to not overwrite, this removes the slug
        overlay_text = " ".join(filename_text.split()[:-1])

        #  Write filename on video; this will require changes on non-Windows machines for the font
        subprocess.run([
            'ffmpeg', '-i', input_filename, '-vf',
            f"drawtext=fontfile= /Windows/fonts/Arial.ttf:text='{overlay_text}':x=10:y=10:fontsize=48:fontcolor=white"
            f":bordercolor=black:borderw=5",
            '-codec:a', 'copy', output_filename
        ])


def get_overlay_files(directory):  # Returns list of videos with text overlay
    return glob.glob(f"{directory}/*overlay.mp4")


def merge_videos(files, output_filename):  # Use ffmpeg to merge overlay video into one video
    with open('file_list.txt', 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")

    subprocess.run([
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'file_list.txt',
        '-c', 'copy', output_filename
    ])

    os.remove('file_list.txt')


def main():
    # Check to make sure all arguments provided
    if len(sys.argv) != 5:
        print("Usage: python main.py <channel_name> <year> <month> <clip_count>")
        sys.exit(1)

    # Delete prior mp4 files
    mp4_files = glob.glob("./*.mp4")
    for file in mp4_files:
        print('Removing ' + file)
        os.remove(file)

    # Take in arguments
    channel_name = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    clip_count = int(sys.argv[4])

    # Twitch Authentication - remember to create credentials.py
    oauth_token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    user_id = get_user_id(oauth_token, channel_name)

    # Get clips, get top clips, download clips, and overlay text on clips
    clips = get_monthly_clips(oauth_token, user_id, year, month)
    top_clips = get_top_clips(clips, n=clip_count)
    download_clips(top_clips)
    overlay_text_on_clips()

    # Merge overlay files
    overlay_files = get_overlay_files('.')
    merge_filename = str(datetime(year, month, 1).strftime('%B %Y - ')) + str(channel_name) + ' - Top Clips.mp4'
    merge_videos(overlay_files, merge_filename)


if __name__ == "__main__":
    main()
