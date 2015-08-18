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
    return '.' + '/' + timestamp + '.jpg'

def gen_header(title, desc, filename, header_filename='/Library/Webserver/Documents/header.html'):
    header_text = '<html><head><title>' + title + '</title></head><body><h2>' + desc + '</h2><b>'
    header_text += '<img src="' + filename + '"><b>'
    file = open(header_filename, 'w')
    file.write(header_text)
    file.close()

if __name__ == "__main__":
    try:
        cam = get_cam(os.getenv('DROPCAM_USERNAME'), os.getenv('DROPCAM_PASSWORD'))
        timestamp = get_timestamp('%H:%M:%S_%d-%m-%Y')
        filename = save_image(cam, timestamp)
        gen_header(os.getenv('DROPCAM_TITLE'), os.getenv('DROPCAM_DESC'), filename)
    except Exception, err:
        print err
