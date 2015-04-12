#!/bin/bash
#
# Check if wifi is working, reboot upon failure
#
# Put something like this in your root crontab:
# */5 * * * * /usr/bin/sudo -H /usr/local/bin/checkwifi.sh >> /dev/null 2>&1
#

# Your gateway IP (ICMP enabled)
IP="192.168.1.1"

/bin/ping -c4 "$IP" > /dev/null

if [ $? != 0 ]
then
  sudo /sbin/shutdown -r now
fi
