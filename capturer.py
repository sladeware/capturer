#!/usr/bin/env python
# Image capturer that saves jpgs with differences.

import argparse
import gdata.spreadsheet.service
import io
import logging
import logging.handlers
import math, sys, numpy as np
import picamera
import signal
import socket
import sys
import time

from datetime import datetime
from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average
from PIL import Image, ImageChops

# Enable debugging
DEBUG = False

# HTML template to view recent photos
INDEX_HTML = '/home/pi/capturer/latest/index.html'
HEADER = '<p><h1>The last three photos, newest first are given below:</h1><h2></p><br>'
IMG_SRC1 = '<p><img src=\"./images/'
IMG_SRC2 = '\"><p><hr>'
FOOTER = '</h2></body></html>'

# For monitoring setup (gdata)
EMAIL = ''
PASSWORD = ''
SPREADSHEET_KEY = '' # key param
WORKSHEET_ID = 'od6' # default
COLUMN_NAME = socket.gethostname() # Must match the spreadsheet column
COLUMN_TIMESTAMP = COLUMN_NAME + '-timestamp'
COLUMN_ENTROPY = COLUMN_NAME + '-entropy'

# Where image files are stored
DIRECTORY = '/home/pi/capturer/images/'

# Where logs are stored
LOG_FILENAME = "/var/log/capturer.log"

# Affects the amount of logs we produce
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# The entropy threshold. Store the file if we are greater or equal to it.
THRESHOLD = 0.1

# Sets the ISO to be used for captures. Valid values are: 100, 200, 320, 400, 500, 640, 800..
ISO = 500

# The image resolution in pixels (W x H)
RESOLUTION = (2592, 1944)

# Cropping constants
<<<<<<< Updated upstream
TOP_W = 850
TOP_H = 700
BOT_W = 1550
BOT_H = 1400
=======
TOP_W = 900
TOP_H = 500
BOT_W = 1600
BOT_H = 1250
>>>>>>> Stashed changes
ENABLE_CROPPING = True

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
        self.first = None
        self.second = None
        self.third = None

    def generate_index_html(self, name, timestamp):
        self.third = self.second
        self.second = self.first
        self.first = [name, timestamp]
        html = HEADER
        html += self.first[1]
        html += IMG_SRC1 + self.first[0] + IMG_SRC2
        if self.second:
            html += self.second[1]
            html += IMG_SRC1 + self.second[0] + IMG_SRC2
        if self.third:
            html += self.third[1]
            html += IMG_SRC1 + self.third[0] + IMG_SRC2
        html += FOOTER
        try:
            f = open(INDEX_HTML, 'w')
            f.write(html)
            f.close
        except:
            logger.info('Problems writing index.html:', INDEX_HTML)

def handler(signum, frame):
    logger.info('Good bye!')
    sys.exit(0)

def capture(camera):
    stream = io.BytesIO()
    camera.start_preview()
    camera.capture(stream, format='jpeg')
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)
    w, h = image.size
    if ENABLE_CROPPING:
        return image.crop((TOP_W, TOP_H, BOT_W, BOT_H))
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

def image_entropy(img):
    h,e = gray_histo(img)
    prob = h/np.sum(h) # normalize
    prob = prob[prob>0] # remove zeros
    return -np.sum(prob*np.log2(prob))

def compare_images(img1, img2):
    entropy = image_entropy(ImageChops.difference(img1, img2))
    logger.info('entropy= ' + str(entropy))
    return entropy

def setup(camera):
    logger.info('Setting camera quality settings.')
    camera.resolution = RESOLUTION
    camera.framerate = 30
    camera.iso = ISO
    camera.hflip = True
    camera.vflip = True

    # Give the camera's auto-exposure and auto-white-balance algorithms
    # some time to measure the scene and determine appropriate values
    time.sleep(2)

def save(img, value, client, latest):
    name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.' + value + '.jpg'
    timestamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    img.save(DIRECTORY + name)
    logger.info('Saved image: ' + name)
    row = {COLUMN_TIMESTAMP : timestamp, COLUMN_ENTROPY : value}
    try:
        client.InsertRow(row, SPREADSHEET_KEY, WORKSHEET_ID)
    except Exception as e:
        logger.info(e)
    latest.generate_index_html(name, timestamp)

## START OF MAIN CODE ##
# TODO(slade): Clean this up.
                
# Handle CTL-C cleanly
signal.signal(signal.SIGINT, handler)

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)

# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)

# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)

# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

# Attach the formatter to the handler
handler.setFormatter(formatter)

# Attach the handler to the logger
logger.addHandler(handler)

# Replace stdout with logging to file at INFO level
if not DEBUG:
    sys.stdout = MyLogger(logger, logging.INFO)

# Replace stderr with logging to file at ERROR level
if not DEBUG:
    sys.stderr = MyLogger(logger, logging.ERROR)

# Setup monitoring
client = gdata.spreadsheet.service.SpreadsheetsService()
if DEBUG:
    client.debug = True
client.email = EMAIL
client.password = PASSWORD
client.source = 'Turtle Monitor Client'
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
            if THRESHOLD <= threshold_value:
                current = new
                save(current, str(threshold_value), client, latest)
<<<<<<< Updated upstream
except:
    logger.info('Problems setting up camera')


=======
except Exception as e:
    print e
    logger.info('Problems setting up camera. ')
    logger.info(str(e))
>>>>>>> Stashed changes
