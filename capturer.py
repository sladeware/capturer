#!/usr/bin/env python
# Image capturer that saves jpgs with differences.

import argparse
import gdata.spreadsheet.service
import io
import logging
import logging.handlers
import math, sys, numpy as np
import picamera
import settings as s
import signal
import socket
import sys
import time

from datetime import datetime, timedelta
from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average
from PIL import Image, ImageChops

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

def write(self, message):
    # Only log if there is a message (not just a new line)
    if message.rstrip() != "":
        self.logger.log(self.level, message.rstrip())

class LatestIndexPage(object):
    def __init__(self):
        self.images = None

    def generate_index_html(self, name, now):
        yesterday = now - timedelta(days = s.DAYS_IN_PAST)
        if self.images:
            self.images.insert(0, [name, now]) # Push to front of list
        else:
            self.images = [[name, now]]
        begin = datetime.now() - timedelta(days = s.DAYS_IN_PAST)
        html = s.HEADER1 + begin.strftime('%m/%d/%Y %H:%M') + s.HEADER2
        for image in self.images[:]:
            if image[1] > yesterday:
                html += image[1].strftime('%m/%d/%Y %H:%M:%S')
                html += s.IMG_SRC1 + image[0] + s.IMG_SRC2
            else:
                self.images.remove(image)
        html += s.FOOTER
        try:
            f = open(s.INDEX_HTML, 'w')
            f.write(html)
            f.close
        except:
            logger.info('Problems writing index.html:', s.INDEX_HTML)
  
def handler(signum, frame):
    logger.info('Good bye!')
    sys.exit(0)

def capture(camera):
    stream = io.BytesIO()
    camera.start_preview()
    if s.USE_VIDEO_PORT:
        camera.capture(stream, format='jpeg', use_video_port=True)
    else:
        camera.capture(stream, format='jpeg')
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)
    w, h = image.size
    if s.ENABLE_CROPPING:
        return image.crop((s.TOP_W, s.TOP_H, s.BOT_W, s.BOT_H))
    else:
        return image

def color_histo(img):
    w,h = img.size
    a = np.array(img.convert('RGB')).reshape((w*h,3))
    return np.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)

def gray_histo(img):
    w,h = img.size
    a = np.array(img.convert('L')).reshape((w*h))
    return np.histogramdd(a, bins=(16,), range=((0,256),))

def histo(img):
    if s.GRAY:
        return gray_histo(img)
    else:
        return color_histo(img)

def image_entropy(img):
    h,e = histo(img)
    prob = h/np.sum(h) # normalize
    prob = prob[prob>0] # remove zeros
    return -np.sum(prob*np.log2(prob))

def compare_images(img1, img2):
    entropy = image_entropy(ImageChops.difference(img1, img2))
    logger.info('entropy= ' + str(entropy))
    return entropy

def setup(camera):
    logger.info('Setting camera quality settings.')
    camera.resolution = s.RESOLUTION
    camera.framerate = 30
    camera.iso = s.ISO
    camera.hflip = s.H_FLIP
    camera.vflip = s.V_FLIP

    # Give the camera's auto-exposure and auto-white-balance algorithms
    # some time to measure the scene and determine appropriate values
    time.sleep(2)

def save_filename(name):
    try:
        f = open('/tmp/latest_capturer_image', 'w')
        f.write(name)
        f.close()
    except Exception as e:
        logger.info(e)

def save(img, value, client, latest):
    """
    We save the image to a file on the local filesystem as a JPG. We also
    push the timestamp and entropy values to a Google Spreadsheet
    for the purposes of monitoring and tuning the entropy threshold.
    """
    now = datetime.now()
    name = now.strftime('%Y-%m-%d_%H-%M-%S') + '.' + value + '.jpg'
    timestamp = now.strftime('%m/%d/%Y %H:%M:%S')
    img.save(s.DIRECTORY + name)
    save_filename(s.DIRECTORY + name)
    logger.info('Saved image: ' + name)
    row = {s.COLUMN_TIMESTAMP : timestamp, s.COLUMN_ENTROPY : value}
    try:
        client.InsertRow(row, s.SPREADSHEET_KEY, s.WORKSHEET_ID)
    except Exception as e:
        logger.info(e)
    latest.generate_index_html(name, now)

## START OF MAIN CODE ##
# TODO(slade): Clean this up.
                
# Handle CTL-C cleanly
signal.signal(signal.SIGINT, handler)

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + s.LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
    s.LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)

# Set the log level to LOG_LEVEL
logger.setLevel(s.LOG_LEVEL)

# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(s.LOG_FILENAME, when="midnight", backupCount=3)

# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

# Attach the formatter to the handler
handler.setFormatter(formatter)

# Attach the handler to the logger
logger.addHandler(handler)

# Replace stdout with logging to file at INFO level
if not s.DEBUG:
    sys.stdout = MyLogger(logger, logging.INFO)

# Replace stderr with logging to file at ERROR level
if not s.DEBUG:
    sys.stderr = MyLogger(logger, logging.ERROR)

# Setup monitoring via a Google Spreadsheet
client = gdata.spreadsheet.service.SpreadsheetsService()
if s.DEBUG:
    client.debug = True
client.email = s.EMAIL
client.password = s.PASSWORD
client.source = 'Capturer Monitor Client'
try:
    client.ProgrammaticLogin()
except:
    logger.info('Cannot login to Google')

# Setup Latest Index Page generator
latest = LatestIndexPage()

logger.info('Starting at: ' + str(datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
try:
    with picamera.PiCamera() as camera:
        setup(camera)
        logger.info('Capturing images.')
        current = capture(camera)
        save(current, '0', client, latest)
        while True:
            new = capture(camera)
            threshold_value = compare_images(current, new)
            if s.THRESHOLD <= threshold_value:
                current = new
                save(current, str(threshold_value), client, latest)
except Exception as e:
    print e
    logger.info('Problems setting up camera. ')
    logger.info(str(e))
