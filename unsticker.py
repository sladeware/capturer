# Restart stuck capturer programs by watching log mod times

import os
import time

RESTART_THRESHOLD = 120

delta = time.time() - os.stat('/var/log/capturer.log').st_mtime

if delta > RESTART_THRESHOLD:
    os.system('service capturer restart')
