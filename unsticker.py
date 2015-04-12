# Restart stuck capturer programs by watching log mod times
#
# Put something like this in your root crontab:
# */3 * * * * /usr/bin/sudo -H /usr/bin/python /home/pi/capturer/unsticker.py >> /dev/null 2>&1
#

import os
import time

RESTART_THRESHOLD = 120

delta = time.time() - os.stat('/var/log/capturer.log').st_mtime

if delta > RESTART_THRESHOLD:
    os.system('service capturer restart')
