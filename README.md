Capturer
==============

Capture interesting images using your Raspberry Pi Cam automatically!
--------------

*A great way to capture awesome sunset photos!*

The capturer runs as a daemon and uses the Pi camera to capture images every 15 to 20 seconds, compares that new image to the last one that was saved, and saves the new one if it is "interesting" enough. Interesting is determined by the how different the new image is from that last saved one, by measuring entropy.

You can adjust the entropy threshold to your environment, which results in more or less images being captured with fewer or greater differences. Please take a look at the beginning of the source code for 'THRESHOLD'. A higher value means the images are more different before saving a file.

**Installation**
- Setup your Pi with the latest Raspian and Pi Cam
- Execute: sudo apt-get install python-scipy
- Execute: sudo apt-get install python-picamera
- Copy capturer.init to /etc/init.d
- Create the directory '/home/pi/capturer/images'
- Execute: sudo service capturer defaults
- Restart your Raspberry Pi
- Execute: 'tail -f /var/log/capturer.log' and watch the log for errors
- Type 'CTL-C' to break out of the log tailing
- You should now have have interesting photos stored in the images directory

**How it works**
- Look for CTL-C presses, in case this is run interactively
- Initializes logging and remaps stderr and stdout to logs
- Capture the first image and save it as a jpg file in the images directory
- Capture the second image
- Compute the entropy of the currently saved image and the new one
- Save the new image, if the entropy is greater than or equal to the threshold
- Repeat this process forever

