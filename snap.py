# Pulls a image from Nest and stores it locally with a timestamp

import datetime
from dropcam import Dropcam
import os
import time

LIVING_ROOM_CAM = 1
IMAGES_DIR = '/Library/WebServer/Documents'

def get_cam(user, passwd):
    d = Dropcam(user, passwd)
    cams = d.cameras()
    return cams[LIVING_ROOM_CAM]

def get_timestamp(format):
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime(format)

def save_image(cam, timestamp, width=1080):
    path = IMAGES_DIR + '/' + timestamp + '.jpg'
    cam.save_image(path, width)


if __name__ == "__main__":
    try:
        cam = get_cam(os.getenv("DROPCAM_USERNAME"), os.getenv("DROPCAM_PASSWORD"))
        timestamp = get_timestamp('%H-%M-%S_%d-%m-%Y')
        save_image(cam, timestamp)
    except Exception, err:
        print err
