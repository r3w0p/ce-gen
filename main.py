from moviepy.editor import *
from pathlib import Path
import argparse
from random import uniform, choice, randint
from glob import glob
from math import floor
from pprint import pprint

DEFAULT_RANDOM_CLIP_DURATION_MIN = 10
DEFAULT_RANDOM_CLIP_DURATION_MAX = 20

DEFAULT_RANDOM_IMAGE_DURATION_MIN = 1
DEFAULT_RANDOM_IMAGE_DURATION_MAX = 5

DEFAULT_SUBCLIP_MAX_DURATION = 5

DEFAULT_RANDOM_VOLUME_LOW = 1.0
DEFAULT_RANDOM_VOLUME_HIGH = 3.0

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_MARGIN = 0

DEFAULT_RELATIVE_WIDTH_MIN = 0.25
DEFAULT_RELATIVE_WIDTH_MAX = 0.45

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-vmd', '--video_max_duration',
                    type=int, default=0,
                    help="The maximum duration for the output video "
                         "(<1 for random)")
parser.add_argument('-imd', '--image_max_duration',
                    type=int, default=0,
                    help="The maximum duration for which an image can be "
                         "overlayed in the output video (<1 for random)")
parser.add_argument('-smd', '--subclip_max_duration',
                    type=int, default=0,
                    help="The maximum duration for which a clip can be "
                         "overlayed in the output video (<1 for random)")
parser.add_argument('-ov', '--overlay_videos',
                    type=int, default=0,
                    help="The number of videos to overlay onto the "
                         "output video (<1 for random)")
parser.add_argument('-oa', '--overlay_audio',
                    type=int, default=0,
                    help="The number of audio files to overlay onto the "
                         "output video (<1 for random)")
parser.add_argument('-oi', '--overlay_images',
                    type=int, default=0,
                    help="The number of images to overlay onto the "
                         "output video (<1 for random)")
parser.add_argument('-pv', '--path_videos',
                    type=str, default="media/videos",
                    help="The path to the directory containing videos to use "
                         "for the output video")
parser.add_argument('-pa', '--path_audio',
                    type=str, default="media/audio",
                    help="The path to the directory containing audio to use "
                         "for the output video")
parser.add_argument('-pi', '--path_images',
                    type=str, default="media/images",
                    help="The path to the directory containing images to use "
                         "for the output video")
parser.add_argument('-o', '--output',
                    type=str, default="output.mp4",
                    help="The path containing the directory and file name "
                         "for the output video")
args = parser.parse_args()


def get_random_duration(low, high) -> float:
    return uniform(low, high)


def get_media_file_paths(path_media_files: Path) -> list:
    return glob(str(path_media_files / "*.*"))


def get_random_subclip(duration: float, interval: float) -> tuple:
    start = uniform(0, duration / 4)

    max_end = start + interval
    if max_end > duration:
        max_end = duration

    end = uniform(start, max_end)
    return start, end


def clip_generate_base(
        paths_videos: list,
        clip_max_duration: float,
        with_replacement: bool = True,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        margin: int = DEFAULT_MARGIN,
        subclip_max_duration: float = 0.0):

    if len(paths_videos) == 0:
        raise RuntimeError(
            "Video path list must contain at least 1 video file")

    if clip_max_duration < 1.0:
        clip_max_duration = 1.0

    set_paths = set()
    base_clip = None

    while base_clip is None or base_clip.duration < clip_max_duration:
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
        clip = clip.volumex(get_random_duration(
            low=DEFAULT_RANDOM_VOLUME_LOW,
            high=DEFAULT_RANDOM_VOLUME_HIGH
        ))

        set_paths.add(video_path)

        if 0.0 < subclip_max_duration < clip.duration:
            start, end = get_random_subclip(
                duration=clip.duration, interval=subclip_max_duration)
            clip = clip.subclip(start, end)

        if base_clip is None:
            base_clip = clip
        else:
            base_clip = concatenate_videoclips([base_clip, clip])

    if base_clip.duration <= clip_max_duration:
        return base_clip
    else:
        return base_clip.subclip(0, clip_max_duration)


def clip_overlay_videos(
        clip_current,
        video_paths,
        num_overlay_videos: int = 1,
        with_replacement=True,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        subclip_max_duration: float = 0.0):

    if len(video_paths) == 0:
        raise RuntimeError(
            "Video path list must contain at least 1 video file")

    if num_overlay_videos < 1:
        raise RuntimeError("Video overlay must be 1 or greater")

    used_paths = set()
    list_clips = [clip_current]
    dur_original = clip_current.duration

    for _ in range(num_overlay_videos):
        if with_replacement:
            video_path = choice(video_paths)
        else:
            if len(used_paths) == len(video_paths):
                break

            video_path = choice(list(
                used_paths.symmetric_difference(video_paths)))

        # rand_audio = bool(random.getrandbits(1))
        clip = VideoFileClip(video_path, audio=True)
        clip = clip.volumex(get_random_duration(
            low=DEFAULT_RANDOM_VOLUME_LOW,
            high=DEFAULT_RANDOM_VOLUME_HIGH
        ))

        rand_width = uniform(DEFAULT_RELATIVE_WIDTH_MIN,
                             DEFAULT_RELATIVE_WIDTH_MAX)
        rand_height = uniform(DEFAULT_RELATIVE_WIDTH_MIN,
                              DEFAULT_RELATIVE_WIDTH_MAX)
        rand_size = (width * rand_width, height * rand_height)
        clip = clip.resize(rand_size)

        rand_pos = (uniform(0, 1-rand_width), uniform(0, 1-rand_height))
        clip = clip.set_position(rand_pos, relative=True)

        if 0.0 < subclip_max_duration < clip.duration:
            start, end = get_random_subclip(
                duration=clip.duration, interval=subclip_max_duration)
            clip = clip.subclip(start, end)

        rand_start = clip_current.duration * uniform(0.0, 1.0)
        clip = clip.set_start(rand_start)

        list_clips.append(clip)

    return CompositeVideoClip(list_clips).subclip(0, dur_original)


def clip_overlay_audio(
        clip_current,
        paths_audio: list,
        num_overlay_audio: int = 1,
        with_replacement: bool = True):

    if len(paths_audio) == 0:
        raise RuntimeError(
            "Audio path list must contain at least 1 audio file")

    if num_overlay_audio < 1:
        raise RuntimeError("Audio overlay must be 1 or greater")

    set_paths = set()
    list_clips = [clip_current.audio]
    duration_original_audio = clip_current.audio.duration

    for _ in range(num_overlay_audio):
        if with_replacement:
            audio_path = choice(paths_audio)
        else:
            if len(set_paths) == len(paths_audio):
                break

            audio_path = choice(list(
                set_paths.symmetric_difference(paths_audio)))

        clip = AudioFileClip(audio_path)
        clip = clip.volumex(get_random_duration(
            low=DEFAULT_RANDOM_VOLUME_LOW,
            high=DEFAULT_RANDOM_VOLUME_HIGH
        ))
        clip = clip.set_start(clip_current.duration * uniform(0, 1.0))

        set_paths.add(audio_path)
        list_clips.append(clip)

    clip_current.audio = CompositeAudioClip(list_clips) \
        .subclip(0, duration_original_audio)
    return clip_current


def clip_overlay_images(
        clip_current,
        paths_images: list,
        num_overlay_images: int = 1,
        with_replacement=True,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        image_max_duration: float = 1.0):

    if len(paths_images) == 0:
        raise RuntimeError(
            "Image path list must contain at least 1 image file "
            "that is not of type GIF")

    if num_overlay_images < 1:
        raise RuntimeError("Image overlay must be 1 or greater")

    if image_max_duration < 1.0:
        image_max_duration = 1.0

    set_paths = set()
    list_clips = [clip_current]
    dur_original = clip_current.duration

    for _ in range(num_overlay_images):
        if with_replacement:
            image_path = choice(paths_images)
        else:
            if len(set_paths) == len(paths_images):
                break

            image_path = choice(list(
                set_paths.symmetric_difference(paths_images)))

        clip = ImageClip(image_path)

        rand_width = uniform(DEFAULT_RELATIVE_WIDTH_MIN,
                             DEFAULT_RELATIVE_WIDTH_MAX)
        rand_height = uniform(DEFAULT_RELATIVE_WIDTH_MIN,
                              DEFAULT_RELATIVE_WIDTH_MAX)
        rand_size = (width * rand_width, height * rand_height)
        clip = clip.resize(rand_size)

        rand_pos = (uniform(0, 1-rand_width), uniform(0, 1-rand_height))
        clip = clip.set_position(rand_pos, relative=True)

        rand_start = clip_current.duration * uniform(0, 1.0)
        clip = clip.set_start(rand_start)

        rand_dur = uniform(1.0, image_max_duration)
        clip = clip.set_duration(rand_dur)

        list_clips.append(clip)

    return CompositeVideoClip(list_clips).subclip(0, dur_original)


def main():
    path_videos = Path(args.path_videos.strip()).absolute()
    path_audio = Path(args.path_audio.strip()).absolute()
    path_images = Path(args.path_images.strip()).absolute()
    path_output = Path(args.output.strip()).absolute()

    list_videos = get_media_file_paths(path_videos)
    list_audio = get_media_file_paths(path_audio)
    list_images = get_media_file_paths(path_images)

    list_gifs = [path_image for path_image in list_images
                 if path_image.lower().endswith(".gif")]

    list_videos.extend(list_gifs)
    list_images = [i for i in list_images if i not in list_gifs]

    video_max_duration = float(args.video_max_duration) \
        if args.video_max_duration > 0 \
        else get_random_duration(low=DEFAULT_RANDOM_CLIP_DURATION_MIN,
                                 high=DEFAULT_RANDOM_CLIP_DURATION_MAX)

    image_max_duration = float(args.image_max_duration) \
        if args.image_max_duration > 0 \
        else get_random_duration(low=DEFAULT_RANDOM_IMAGE_DURATION_MIN,
                                 high=DEFAULT_RANDOM_IMAGE_DURATION_MAX)

    subclip_max_duration = float(args.subclip_max_duration) \
        if args.subclip_max_duration > 0 \
        else DEFAULT_SUBCLIP_MAX_DURATION

    overlay_videos = args.overlay_videos \
        if args.overlay_videos > 0 \
        else randint(floor(len(list_videos) / 4),
                     floor(len(list_videos) - (len(list_videos) / 4)))

    overlay_audio = args.overlay_audio \
        if args.overlay_audio > 0 \
        else randint(floor(len(list_audio) / 4),
                     floor(len(list_audio) - (len(list_audio) / 4)))

    overlay_images = args.overlay_images \
        if args.overlay_images > 0 \
        else randint(floor(len(list_images) / 4),
                     floor(len(list_images) - (len(list_images) / 4)))

    print("Generating video")
    print("Max duration: {:.1f}s".format(video_max_duration))

    video_clip = clip_generate_base(
        paths_videos=list_videos,
        clip_max_duration=video_max_duration,
        subclip_max_duration=subclip_max_duration)

    video_clip = clip_overlay_videos(
        clip_current=video_clip,
        video_paths=list_videos,
        num_overlay_videos=overlay_videos,
        subclip_max_duration=subclip_max_duration
    )

    video_clip = clip_overlay_audio(
        clip_current=video_clip,
        paths_audio=list_audio,
        num_overlay_audio=overlay_audio
    )

    video_clip = clip_overlay_images(
        clip_current=video_clip,
        paths_images=list_images,
        num_overlay_images=overlay_images,
        image_max_duration=image_max_duration
    )

    print("Final video: {:.1f}s".format(video_clip.duration))
    print("Writing to file: {}".format(path_output))
    video_clip.write_videofile(str(path_output))


if __name__ == "__main__":
    main()
