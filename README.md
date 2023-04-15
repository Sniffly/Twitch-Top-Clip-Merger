# Twitch Clip Mixer
 Grab the most popular clips of a Twitch channel for a given month and year and automatically create an mp4 compilation video.

## Installation

1. Clone the repository to your local machine.
2. Make sure you have Python 3 installed.
3. Install the required libraries using the following command:

```pip install -r requirements.txt```

4. You also need to have [Twitch-DL](https://github.com/ihabunek/twitch-dl) and [FFmpeg](https://ffmpeg.org/) installed on your system. Ensure that FFmpeg is also added to your Path variables.

5. You need to set up credentials.py with your Twitch API Client ID and Client Secret. You can obtain these by registering an application on [Twitch's Dev Console site.](https://dev.twitch.tv/console)

## Usage

To use the script, run the following command:

```python main.py <channel_name> <year> <month> <clip_count>```

- `channel_name`: The name of the Twitch channel for which you want to download the top clips.
- `year`: The year for which you want to download the top clips.
- `month`: The month for which you want to download the top clips (1-12).
- `clip_count`: The number of top clips to download.

The script will download the top clips, add a text overlay to each clip, merge the clips into a single video, and save the video file in the current directory.