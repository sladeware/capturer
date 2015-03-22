# Settings for the Capturer program.
#

import logging
import socket

hostname = socket.gethostname()

# Enable debugging
DEBUG = False

# Camera image flip constants
H_FLIP = False
V_FLIP = False

# Enable gray scale histograms, which ignores color when computing entropy
GRAY = False

# Use video port. Faster, but only supports up to 1080p.
USE_VIDEO_PORT = True

# HTML template to view recent photos
INDEX_HTML = '/home/pi/capturer/latest/index.html'
HEADER1 = '<head><meta http-equiv="refresh" content="300" /></head><body><html><h1>' + hostname + '</h1><p><h1>All photos taken since '
HEADER2 = ', newest first:</h1><h2></p><br>'
IMG_SRC1 = '<p><img src=\"./images/'
IMG_SRC2 = '\"><p><hr>'
FOOTER = '</h2></body></html>'

# How many days in the past to show images on the index.html page
DAYS_IN_PAST = 3

# For monitoring setup (gdata)
EMAIL = '[YOUR_EMAIL]@gmail.com'
PASSWORD = '[YOUR_PASSWORD]'
SPREADSHEET_KEY = '[YOUR_SPREADSHEET_KEY_PARAM]'
WORKSHEET_ID = 'od6' # default
COLUMN_NAME = hostname  # Must match the spreadsheet column
COLUMN_TIMESTAMP = COLUMN_NAME + '-timestamp'
COLUMN_ENTROPY = COLUMN_NAME + '-entropy'

# Where image files are stored
DIRECTORY = '/home/pi/capturer/images/'

# Where logs are stored
LOG_FILENAME = "/var/log/capturer.log"

# Affects the amount of logs we produce
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# The entropy threshold. Store the file if we are greater or equal to it.
THRESHOLD = 0.9

# Sets the ISO to be used for captures. Valid values are: 100, 200, 320, 400, 500, 640, 800..
ISO = 500

# The image resolution in pixels (W x H)
RESOLUTION = (2592, 1944)

# Cropping constants
TOP_W = 900
TOP_H = 725
BOT_W = 1550
BOT_H = 1200
ENABLE_CROPPING = False

# Rotation contants. Rotation is counter-clockwise in degrees.
ENABLE_ROTATION = False
ROTATION_ANGLE = 0

