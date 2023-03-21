import argparse
import csv
import logging
import os
import sys

import django
from tqdm import tqdm

argparser = argparse.ArgumentParser()
argparser.add_argument("--fresh", type=bool, default=True)
args = argparser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="logs.log",
    filemode="w+",
)

sys.path.append("dynamic_form")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dynamic_form.settings")
django.setup()

from django.contrib.auth.models import User
from form.model import AudioClip, Brand, Experience, UserStage, Video, VideoScene

USER_LIMIT = 10


def create_update_brand(name, id):
    if Brand.objects.filter(id=id).exists():
        brand = Brand.objects.get(id=id)
        brand.name = name
        logging.warning(f"Brand {id} already exists. Updated name to {name}.")
    else:
        brand = Brand.objects.create(id=id, name=name)
        logging.info(f"Brand {name} created.")
    brand.save()


def create_update_video(id, name, brand_id, src, length, desc, title):
    if Video.objects.filter(id=id).exists():
        video = Video.objects.get(id=id)
        video.name = name
        video.brand_id = brand_id
        video.src = src
        video.length = length
        video.desc = desc
        video.title = title
        logging.warning(f"Video {name} already exists. Updated.")
    else:
        brand = Brand.objects.get(id=brand_id)
        video = Video.objects.create(
            id=id,
            name=name,
            brand=brand,
            src=src,
            length=length,
            desc=desc,
            title=title,
        )
        logging.info(f"Video {name} created.")
    video.save()


def create_update_get_user_stage(id, username, name, password):
    if User.objects.filter(id=id).exists():
        user = User.objects.get(id=id)
        user.set_password(password)
        user.first_name = name
        logging.warning(f"User {username} already exists. Password updated.")
    else:
        user = User.objects.create_user(
            id=id,
            username=username,
            password=password,
            first_name=name,
            last_name="",
        )
        logging.info(f"User {username} created.")

    if UserStage.objects.filter(user=user).exists():
        stage = UserStage.objects.get(user=user)
        logging.warning(f"UserStage {username} already exists. Updated.")
    else:
        stage = UserStage.objects.create(user=user)
        stage.update()
    user.save()
    return user, stage


def create_update_video_scene(id, video_id, url):
    if not Video.objects.filter(id=video_id).exists():
        logging.error(f"VideoScene {id} not created. Video {video_id} does not exist.")
        return
    video = Video.objects.get(id=video_id)
    if VideoScene.objects.filter(id=id).exists():
        video_scene = VideoScene.objects.get(id=id)
        video_scene.video = video
        video_scene.url = url
        logging.warning(f"VideoScene {id} already exists. Updated.")
    else:
        video_scene = VideoScene.objects.create(id=id, video=video, url=url)
        logging.info(f"VideoScene {id} created.")
    video_scene.save()


def create_update_audio_clip(id, video_id, url):
    if not Video.objects.filter(id=video_id).exists():
        logging.error(f"VideoScene {id} not created. Video {video_id} does not exist.")
        return
    video = Video.objects.get(id=video_id)
    if AudioClip.objects.filter(id=id).exists():
        audio_clip = AudioClip.objects.get(id=id)
        audio_clip.video = video
        audio_clip.url = url
        logging.warning(f"AudioClip {id} already exists. Updated.")
    else:
        audio_clip = AudioClip.objects.create(id=id, video=video, url=url)
        logging.info(f"AudioClip {id} created.")
    audio_clip.save()


if __name__ == "__main__":
    if args.fresh:
        with open("data_new/brands.tsv") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in tqdm(reader, total=276):
                name, id = row
                create_update_brand(name, id)

        with open("data_new/videos.tsv") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in tqdm(reader, total=2821):
                id, name, brand_id, src, length, desc, title = row
                create_update_video(id, name, brand_id, src, length, desc, title)

        with open("data_new/scenes.tsv") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in tqdm(reader, total=4424):
                id, video_id, url = row
                create_update_video_scene(id, video_id, url)

        with open("data_new/audio_clips.tsv") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in tqdm(reader, total=4424):
                id, video_id, url = row
                create_update_audio_clip(id, video_id, url)

    with open("data_new/exp.tsv") as f:
        reader = csv.reader(f, delimiter="\t")
        for (
            id,
            username,
            name,
            password,
            video_ids,
            brand_seen_option_ids,
            brand_used_option_ids,
            brand_recog_ids,
            eyetracker,
            scene_ids,
            audio_clip_ids,
            cc_v,
        ) in tqdm(reader, total=min(620, USER_LIMIT)):
            if int(id) > USER_LIMIT:
                logging.log(logging.INFO, "User limit reached. Breaking.")
                break

            user, stage = create_update_get_user_stage(id, username, name, password)
            video_ids = video_ids.split(",")
            brand_seen_option_ids = brand_seen_option_ids.split(",")
            brand_used_option_ids = brand_used_option_ids.split(",")
            brand_recog_ids = brand_recog_ids.split(",")
            scene_ids = scene_ids.split(",")
            audio_clip_ids = audio_clip_ids.split(",")
            (
                videos,
                brand_seen_options,
                brand_used_options,
                brand_recogs,
                scenes,
                audio_clips,
            ) = (
                [],
                [],
                [],
                [],
                [],
                [],
            )
            for vid in video_ids:
                if not Video.objects.filter(id=vid).exists():
                    pass
                    # logging.error(f"Video {vid} does not exist.")
                else:
                    videos.append(Video.objects.get(id=vid))

            for brand_id in brand_seen_option_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    pass
                    # logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_seen_options.append(Brand.objects.get(id=brand_id))

            for brand_id in brand_used_option_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    pass
                    # logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_used_options.append(Brand.objects.get(id=brand_id))

            for brand_id in brand_recog_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    pass
                    # logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_recogs.append(Brand.objects.get(id=brand_id))

            for scene_id in scene_ids:
                if not VideoScene.objects.filter(id=scene_id).exists():
                    pass
                    # logging.error(f"Scene {scene_id} does not exist.")
                else:
                    scenes.append(VideoScene.objects.get(id=scene_id))

            for audio_clip_id in audio_clip_ids:
                if not AudioClip.objects.filter(id=audio_clip_id).exists():
                    pass

                else:
                    audio_clips.append(AudioClip.objects.get(id=audio_clip_id))

            if Experience.objects.filter(user=user).exists():
                experience = Experience.objects.get(user=user)
                pass
                # logging.warning(f"Experience {username} already exists. Updated.")
            else:
                experience = Experience.objects.create(
                    user=user,
                    cc_v=cc_v,
                )
                pass
                # logging.info(f"Experience {username} created.")

            experience.videos.set(videos)
            experience.brands_seen_options.set(brand_seen_options)
            experience.prod_used_options.set(brand_used_options)
            experience.brand_recog.set(brand_recogs)
            experience.gaze = int(eyetracker)
            experience.scene_seen.set(scenes)
            experience.cc_v = cc_v
            experience.audio_seen.set(audio_clips)
            experience.save()
