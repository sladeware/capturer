#!/bin/bash
#
# Did we swipe up or down on the AdaFruit 2.8 inch PiTFT display?
#

A=""
TIME=0
TMP_FILE="/tmp/swipe.txt"
DELAY=2

/usr/bin/evtest /dev/input/touchscreen | \
while read LINE ; do
    NOW=$(/bin/date +%s)
    if [ $NOW -gt $((TIME+$DELAY)) ]; then
        VALUE=$(/bin/echo $LINE | /bin/grep ABS_X | /usr/bin/awk '{split($0,a," "); print a[11]}')
        if [ "$A" = "" ]; then
           A=$VALUE
        elif [[ $A -gt 0 && $VALUE -gt 0 ]]; then
           if [ $(($VALUE-$A)) -gt 0 ]; then
               /bin/echo "UP" > $TMP_FILE
           else
               /bin/echo "DOWN" > $TMP_FILE
           fi
           A=""
           TIME=$(/bin/date +%s)
        fi
    fi
done
