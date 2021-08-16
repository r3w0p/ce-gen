from moviepy.editor import *
from pathlib import Path
import argparse
from random import uniform, choice, randint
from glob import glob
from math import floor

DEFAULT_RANDOM_VOLUME_LOW = 1.0
DEFAULT_RANDOM_VOLUME_HIGH = 3.0

DEFAULT_RANDOM_DURATION_MIN = 10.0
DEFAULT_RANDOM_DURATION_MAX = 30.0

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_MARGIN = 0
DEFAULT_SUBCLIP_ON_DURATION = 0

parser = argparse.ArgumentParser()
parser.add_argument('-max_duration', type=float, default=0.0)
parser.add_argument('-subclip_duration', type=float, default=0.0)
parser.add_argument('-audio_overlay', type=int, default=0)
parser.add_argument('-path_videos', type=str, default="media/videos")
parser.add_argument('-path_audio', type=str, default="media/audio")
parser.add_argument('-path_images', type=str, default="media/images")
parser.add_argument('-output', type=str, default="output.mp4")
args = parser.parse_args()


def get_random_volume(
        low: float = DEFAULT_RANDOM_VOLUME_LOW,
        high: float = DEFAULT_RANDOM_VOLUME_HIGH) -> float:
    return uniform(low, high)


def get_random_duration(
        low: float = DEFAULT_RANDOM_DURATION_MIN,
        high: float = DEFAULT_RANDOM_DURATION_MAX) -> float:
    return uniform(low, high)


def get_media_file_paths(path_media_files: Path) -> list:
    return glob(str(path_media_files / "*.*"))


def get_random_subclip(duration: float, interval: int) -> tuple:
    start = uniform(0, duration / 4)

    max_end = start + interval
    if max_end > duration:
        max_end = duration

    end = uniform(start, max_end)
    return start, end


def generate_base_clip(
        paths_videos: list,
        max_duration: int,
        with_replacement: bool = True,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        margin: int = DEFAULT_MARGIN,
        subclip_duration: int = DEFAULT_SUBCLIP_ON_DURATION):

    if len(paths_videos) == 0:
        raise RuntimeError(
            "Video path list must contain at least 1 video file")

    if max_duration < 1:
        raise RuntimeError("Max duration must be at least 1 second")

    set_paths = set()
    base_clip = None

    while base_clip is None or base_clip.duration < max_duration:
        if with_replacement:
            video_path = choice(paths_videos)
        else:
            if len(set_paths) == len(paths_videos):
                break

            video_path = choice(list(
                set_paths.symmetric_difference(paths_videos)))

        clip = VideoFileClip(video_path)
        clip = clip.resize((width, height))
        clip = clip.margin(margin)
        clip = clip.volumex(get_random_volume())

        set_paths.add(video_path)

        if 0 < subclip_duration < clip.duration:
            start, end = get_random_subclip(clip.duration, subclip_duration)
            clip = clip.subclip(start, end)

        if base_clip is None:
            base_clip = clip
        else:
            base_clip = concatenate_videoclips([base_clip, clip])

    if base_clip.duration <= max_duration:
        return base_clip
    else:
        return base_clip.subclip(0, max_duration)


def overlay_audio(
        clip_current,
        paths_audio: list,
        audio_overlay: int = 1,
        with_replacement: bool = True):

    if len(paths_audio) == 0:
        raise RuntimeError(
            "Audio path list must contain at least 1 audio file")

    set_paths = set()
    list_clips = [clip_current.audio]
    duration_original_audio = clip_current.audio.duration

    for _ in range(audio_overlay):
        if with_replacement:
            audio_path = choice(paths_audio)
        else:
            if len(set_paths) == len(paths_audio):
                break

            audio_path = choice(list(
                set_paths.symmetric_difference(paths_audio)))

        clip = AudioFileClip(audio_path)
        clip = clip.volumex(get_random_volume())
        clip = clip.set_start(clip_current.duration * uniform(0, 1.0))

        set_paths.add(audio_path)
        list_clips.append(clip)

    clip_current.audio = CompositeAudioClip(list_clips) \
        .subclip(0, duration_original_audio)
    return clip_current


def main():
    path_videos = Path(args.path_videos.strip()).absolute()
    path_audio = Path(args.path_audio.strip()).absolute()
    path_images = Path(args.path_images.strip()).absolute()
    path_output = Path(args.output.strip()).absolute()

    list_videos = get_media_file_paths(path_videos)
    list_audio = get_media_file_paths(path_audio)
    list_images = get_media_file_paths(path_images)

    max_duration = args.max_duration if args.max_duration > 0 \
        else get_random_duration()

    print("Generating base video")
    print("Max duration: {}s".format(max_duration))

    clip = generate_base_clip(
        paths_videos=list_videos,
        max_duration=max_duration,
        subclip_duration=args.subclip_duration)

    clip = overlay_audio(
        clip_current=clip,
        paths_audio=list_audio,
        audio_overlay=args.audio_overlay)

    # todo overlay videos
    # todo overlay images

    print("Final clip: {}s".format(clip.duration))
    print("Writing to file: {}".format(path_output))
    clip.write_videofile(str(path_output))


if __name__ == "__main__":
    main()
