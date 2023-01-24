import csv
import logging
import os
import random
import sys

import django
from tqdm import tqdm

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
from form.model import Brand, Experience, UserStage, Video, VideoScene

USER_LIMIT = 1000


def create_update_brand(name, id):
    if Brand.objects.filter(id=id).exists():
        brand = Brand.objects.get(id=id)
        brand.name = name
        logging.warning(f"Brand {id} already exists. Updated name to {name}.")
    else:
        brand = Brand.objects.create(id=id, name=name)
        logging.info(f"Brand {name} created.")
    brand.save()


def create_update_video(id, name, brand_id, src, length):
    if Video.objects.filter(id=id).exists():
        video = Video.objects.get(id=id)
        video.name = name
        video.brand_id = brand_id
        video.src = src
        video.length = length
        logging.warning(f"Video {name} already exists. Updated.")
    else:
        brand = Brand.objects.get(id=brand_id)
        video = Video.objects.create(
            id=id,
            name=name,
            brand=brand,
            src=src,
            length=length,
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
        logging.error(
            f"VideoScene {id} not created. Video {video_id} does not exist. Setting Random video for the time being"
        )
        video_id = random.choice(Video.objects.all()).id
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


def random_scene(video):
    return VideoScene.objects.filter(video=video).order_by("?").first()


if __name__ == "__main__":
    with open("data_new/brands.tsv") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in tqdm(reader, total=276):
            name, id = row
            create_update_brand(name, id)

    with open("data_new/videos.tsv") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in tqdm(reader, total=2213):
            id, name, brand_id, src, length = row
            create_update_video(id, name, brand_id, src, length)

    with open("data_new/scenes.tsv") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in tqdm(reader, total=8658):
            id, video_id, url = row
            create_update_video_scene(id, video_id, url)

    with open("data_new/users.tsv") as f:
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
        ) in tqdm(reader, total=633):
            if int(id) > USER_LIMIT:
                logging.log(logging.INFO, "User limit reached. Breaking.")
                break
            user, stage = create_update_get_user_stage(id, username, name, password)
            video_ids = video_ids.split(",")
            brand_seen_option_ids = brand_seen_option_ids.split(",")
            brand_used_option_ids = brand_used_option_ids.split(",")
            brand_recog_ids = brand_recog_ids.split(",")
            videos, brand_seen_options, brand_used_options, brand_recogs = (
                [],
                [],
                [],
                [],
            )
            for vid in video_ids:
                if not Video.objects.filter(id=vid).exists():
                    logging.error(f"Video {vid} does not exist.")
                else:
                    videos.append(Video.objects.get(id=vid))

            for brand_id in brand_seen_option_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_seen_options.append(Brand.objects.get(id=brand_id))

            for brand_id in brand_used_option_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_used_options.append(Brand.objects.get(id=brand_id))

            for brand_id in brand_recog_ids:
                if not Brand.objects.filter(id=brand_id).exists():
                    logging.error(f"Brand {brand_id} does not exist.")
                else:
                    brand_recogs.append(Brand.objects.get(id=brand_id))

            if Experience.objects.filter(user=user).exists():
                experience = Experience.objects.get(user=user)
                logging.warning(f"Experience {username} already exists. Updated.")
            else:
                experience = Experience.objects.create(
                    user=user,
                )
                logging.info(f"Experience {username} created.")

            random.seed(id)
            scenes = []
            for video in videos:
                scenes.append(random_scene(video))
            for scene in (
                VideoScene.objects.exclude(video__in=videos).order_by("?")[:10].all()
            ):
                scenes.append(scene)
            random.shuffle(scenes)

            experience.videos.set(videos)
            experience.brands_seen_options.set(brand_seen_options)
            experience.prod_used_options.set(brand_used_options)
            experience.brand_recog.set(brand_recogs)
            experience.gaze = int(eyetracker)
            experience.scene_seen.set(scenes)
            experience.save()
