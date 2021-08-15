from moviepy.editor import *
from pathlib import Path
import argparse
from random import uniform, choice, randint
from glob import glob

DEFAULT_RANDOM_VOLUME_LOW = 1.0
DEFAULT_RANDOM_VOLUME_HIGH = 3.0

DEFAULT_RANDOM_DURATION_MIN = 10
DEFAULT_RANDOM_DURATION_MAX = 30

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_MARGIN = 0

parser = argparse.ArgumentParser()
parser.add_argument('-duration', type=int, default=0)
parser.add_argument('-media', type=str, default="media")
parser.add_argument('-output', type=str, default="output.mp4")
args = parser.parse_args()

path_media = Path(args.media.strip()).absolute()
path_output = Path(args.output.strip()).absolute()

path_videos = path_media / "videos"
path_audio = path_media / "audio"
path_images = path_media / "images"


def get_random_volume(
        low: float = DEFAULT_RANDOM_VOLUME_LOW,
        high: float = DEFAULT_RANDOM_VOLUME_HIGH) -> float:
    return uniform(low, high)


def get_media_file_paths(path_media_files: Path) -> list:
    return glob(str(path_media_files / "*.*"))


def generate_base_video(
        paths_videos: list,
        max_duration: int,
        with_replacement: bool = True,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        margin: int = DEFAULT_MARGIN):

    if len(paths_videos) == 0:
        raise RuntimeError("Video path list must contain at least 1 video")

    if max_duration < 1:
        raise RuntimeError("Max duration must be at least 1 second")

    used_videos = []
    list_clips = []

    while sum([clip.duration for clip in used_videos]) < max_duration:
        if with_replacement:
            video_path = choice(paths_videos)
        else:
            set_used_videos = set(used_videos)

            if len(set_used_videos) == len(paths_videos):
                break

            video_path = choice(
                list(set_used_videos.symmetric_difference(paths_videos)))

        used_videos.append(video_path)

        clip = VideoFileClip(video_path)
        clip = clip.resize((width, height))
        clip = clip.margin(margin)
        clip = clip.volumex(get_random_volume())

        list_clips.append(clip)

    clip = concatenate_videoclips(list_clips)

    if clip.duration <= max_duration:
        return clip
    else:
        return clip.subclip(0, max_duration)
