# Assumes Brand.json to have all brands
# Assumes Video.json to have all videos

import json
import os
import random

brands = json.load(open("Brand.json"))
videos = json.load(open("Video.json"))

brand_id_map = {brand["name"]: brand["id"] for brand in brands}
video_id_map = {video["path"]: video["id"] for video in videos}
id_video_map = {video["id"]: video["path"] for video in videos}


def make_entry(user_id, entries_path, VID_IDX=721, set_a_ids=list(range(1, 82))):
    videos_a = random.sample(set_a_ids, 3)
    videos_b = list(range(VID_IDX, VID_IDX + 7))
    VID_IDX += 7
    videos = videos_a + videos_b
    video_brands = [brand_id_map[id_video_map[video_id]] for video_id in videos]
    random_brands = random.sample(list(set(brands) - set(video_brands)), 40)
    brand_ops = video_brands + random_brands[:10]
    brand_produse = random_brands[10:25]
    brand_seen = random_brands[25:]
    random.shuffle(videos)
    random.shuffle(brand_ops)
    random.shuffle(brand_produse)
    random.shuffle(brand_seen)
    experience = [
        {
            "id": user_id,
            "user": user_id,
            "videos": ",".join(videos),
        }
    ]
    brand_op = [
        {
            "id": user_id,
            "user": user_id,
            "brand_opinion": ",".join(brand_ops),
        }
    ]
    brand_prod = [
        {
            "id": user_id,
            "user": user_id,
            "brand_produse": ",".join(brand_produse),
        }
    ]
    brand_seen = [
        {
            "id": user_id,
            "user": user_id,
            "brand_ads_seen": ",".join(brand_seen),
        }
    ]
    os.makedirs(f"{entries_path}/{user_id}", exist_ok=True)
    with open(f"{entries_path}/{user_id}/experience.json", "w") as f:
        json.dump(experience, f)
    with open(f"{entries_path}/{user_id}/brand_op.json", "w") as f:
        json.dump(brand_op, f)
    with open(f"{entries_path}/{user_id}/brand_prod.json", "w") as f:
        json.dump(brand_prod, f)
    with open(f"{entries_path}/{user_id}/brand_seen.json", "w") as f:
        json.dump(brand_seen, f)

    return VID_IDX
