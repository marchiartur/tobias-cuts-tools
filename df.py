import json
import os

videos_data_filename = 'videos/data.json'
videos_uploaded_filename = 'videos/uploaded.json'


def get_videos_data():
    videos = []

    with open(videos_data_filename, 'r') as file:
        videos = json.load(file)['videos']

    return videos


def initialize_uploaded():
    if os.path.exists(videos_uploaded_filename):
        return

    with open(videos_uploaded_filename, 'w') as file:
        json.dump({'uploaded': []}, file)


def get_uploaded_videos():
    uploaded = []

    with open(videos_uploaded_filename, 'r') as file:
        uploaded = json.load(file)['uploaded']

    return uploaded


def add_id_uploaded(id: int) -> bool:
    try:
        uploaded = get_uploaded_videos()
        uploaded.append(id)

        with open(videos_uploaded_filename, 'w') as file:
            json.dump({'uploaded': uploaded}, file)

        return True
    except:
        return False


def verify_id_was_uploaded(id: int) -> bool:
    try:
        uploaded = get_uploaded_videos()
        return id in uploaded
    except:
        return False


def delete_videos() -> bool:
    try:
        os.rmdir('/videos/')
        return True
    except:
        return False
