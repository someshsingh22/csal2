import random

import pandas as pd

users = pd.read_csv("data_new/users.tsv", sep="\t", header=None)
columns = ["id", "email", "name", "pass"]
users.columns = columns

videos = pd.read_csv("data_new/videos.tsv", sep="\t", header=None)
columns = ["id", "name", "brand_id", "src", "length", "desc", "title"]
videos.columns = columns

scenes = pd.read_csv("data_new/scenes.tsv", sep="\t", header=None)
columns = ["id", "video_id", "url"]
scenes.columns = columns

audio_clips = pd.read_csv("data_new/audio_clips.tsv", sep="\t", header=None)
columns = ["id", "video_id", "url", "start", "end"]
audio_clips.columns = columns

brands = pd.read_csv("data_new/brands.tsv", sep="\t", header=None)
columns = ["name", "id"]
brands.columns = columns


def make_experience():
    video_set = videos[~(videos["name"] == "example")].sample(10)
    out_videos = videos[~videos["id"].isin(video_set["id"])]
    brand_1_2_set = brands.sample(30)
    brand_op_set = video_set["brand_id"].drop_duplicates()
    brand_non_op_set = brands[~brands["id"].isin(brand_op_set)]["id"]
    brand_op_set = pd.concat([brand_op_set, brand_non_op_set.sample(10)])

    out_videos = out_videos[out_videos["brand_id"].isin(brand_op_set)].groupby(
        "brand_id"
    )
    samples = []
    for brand_id, group in out_videos:
        samples.append(group.sample(2))

    out_brand_videos = pd.concat(samples)

    in_scene_set = scenes[scenes["video_id"].isin(video_set["id"])]
    in_audio_set = audio_clips[audio_clips["video_id"].isin(video_set["id"])]
    out_scene_set = scenes[~scenes["video_id"].isin(video_set["id"])].sample(10)
    out_audio_set = audio_clips[
        audio_clips["video_id"].isin(out_brand_videos["id"])
    ].sample(10)
    in_scene_set = in_scene_set.groupby("video_id").apply(lambda x: x.sample(1))
    in_audio_set = in_audio_set.groupby("video_id").apply(lambda x: x.sample(1))
    scene_set = in_scene_set.append(out_scene_set)
    audio_set = in_audio_set.append(out_audio_set)
    if random.random() < 0.5:
        consistency_check_video = video_set[:3].sample(1)["id"].tolist()[0]
    else:
        consistency_check_video = (
            videos[~(videos["name"] == "example")].sample(1)["id"].tolist()[0]
        )
    video_set_ids = ",".join(video_set["id"].astype(str))
    brand_1_ids = ",".join(brand_1_2_set[:15]["id"].astype(str))
    brand_2_ids = ",".join(brand_1_2_set[15:]["id"].astype(str))
    brand_op_ids = ",".join(brand_op_set.astype(str))
    scene_set_ids = ",".join(scene_set.sample(frac=1)["id"].astype(str))
    audio_set_ids = ",".join(audio_set.sample(frac=1)["id"].astype(str))
    return (
        video_set_ids,
        brand_1_ids,
        brand_2_ids,
        brand_op_ids,
        scene_set_ids,
        audio_set_ids,
        consistency_check_video,
    )


count = len(users)

(
    video_set_ids,
    brand_1_ids,
    brand_2_ids,
    brand_op_ids,
    scene_set_ids,
    audio_set_ids,
    cc_vs,
) = (
    [],
    [],
    [],
    [],
    [],
    [],
    [],
)

for i in range(count):
    (
        video_set_id,
        brand_1_id,
        brand_2_id,
        brand_op_id,
        scene_set_id,
        audio_set_id,
        cc_v,
    ) = make_experience()
    video_set_ids.append(video_set_id)
    brand_1_ids.append(brand_1_id)
    brand_2_ids.append(brand_2_id)
    brand_op_ids.append(brand_op_id)
    scene_set_ids.append(scene_set_id)
    audio_set_ids.append(audio_set_id)
    cc_vs.append(cc_v)

users["video_set_ids"] = video_set_ids
users["brand_1_ids"] = brand_1_ids
users["brand_2_ids"] = brand_2_ids
users["brand_op_ids"] = brand_op_ids
users["eyetracker"] = 0
users["scene_set_ids"] = scene_set_ids
users["audio_set_ids"] = audio_set_ids
users["id"] += 1
users["consistency_check_video"] = cc_vs

users.to_csv("data_new/exp.tsv", sep="\t", index=False, header=False)
