import pandas as pd

users = pd.read_csv("data_new/users.tsv", sep="\t", header=None)
columns = ["id", "email", "name", "pass"]
users.columns = columns

videos = pd.read_csv("data_new/videos.tsv", sep="\t", header=None)
columns = ["id", "name", "brand_id", "src", "length", "desc"]
videos.columns = columns

scenes = pd.read_csv("data_new/scenes.tsv", sep="\t", header=None)
columns = ["id", "video_id", "url"]
scenes.columns = columns

brands = pd.read_csv("data_new/brands.tsv", sep="\t", header=None)
columns = ["name", "id"]
brands.columns = columns


def make_experience():
    video_set = videos.sample(10)
    brand_1_2_set = brands.sample(30)
    brand_op_set = video_set["brand_id"].drop_duplicates()
    brand_non_op_set = brands[~brands["id"].isin(brand_op_set)]["id"]
    brand_op_set = pd.concat([brand_op_set, brand_non_op_set.sample(10)])
    in_scene_set = scenes[scenes["video_id"].isin(video_set["id"])]
    out_scene_set = scenes[~scenes["video_id"].isin(video_set["id"])].sample(10)
    in_scene_set = in_scene_set.groupby("video_id").apply(lambda x: x.sample(1))
    scene_set = in_scene_set.append(out_scene_set)
    video_set_ids = ",".join(video_set["id"].astype(str))
    brand_1_ids = ",".join(brand_1_2_set[:15]["id"].astype(str))
    brand_2_ids = ",".join(brand_1_2_set[15:]["id"].astype(str))
    brand_op_ids = ",".join(brand_op_set.astype(str))
    scene_set_ids = ",".join(scene_set["id"].astype(str))
    return video_set_ids, brand_1_ids, brand_2_ids, brand_op_ids, scene_set_ids


count = len(users)

video_set_ids, brand_1_ids, brand_2_ids, brand_op_ids, scene_set_ids = (
    [],
    [],
    [],
    [],
    [],
)

for i in range(count):
    video_set_id, brand_1_id, brand_2_id, brand_op_id, scene_set_id = make_experience()
    video_set_ids.append(video_set_id)
    brand_1_ids.append(brand_1_id)
    brand_2_ids.append(brand_2_id)
    brand_op_ids.append(brand_op_id)
    scene_set_ids.append(scene_set_id)

users["video_set_ids"] = video_set_ids
users["brand_1_ids"] = brand_1_ids
users["brand_2_ids"] = brand_2_ids
users["brand_op_ids"] = brand_op_ids
users["eyetracker"] = 0
users["scene_set_ids"] = scene_set_ids

users.to_csv("data_new/exp.tsv", sep="\t", index=False, header=False)
