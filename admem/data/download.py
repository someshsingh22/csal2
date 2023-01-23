import os
import time

from pytube import YouTube


def download(video_id, brand, yt_id, out_path, SLEEP=1):
    url = f"https://www.youtube.com/watch?v={yt_id}"
    try:
        yt = YouTube(url)
        try:
            avs = yt.streams.filter(progressive=True).all()
            res = [
                (stream.itag, int(stream.resolution[:-1]))
                for stream in avs
                if stream.mime_type == "video/mp4"
            ]
            itag = max(res, key=lambda x: x[1])[0]
            dl = yt.streams.get_by_itag(itag)
        except:
            dl = yt.streams.first()

        dl.download(output_path=out_path, filename=f"{video_id}_{brand}_{yt_id}")
    except:
        print("Error in downloading video for", video_id, brand, yt_id)
    time.sleep(SLEEP)
