#!/bin/bash
#
# Did we swipe up or down on the AdaFruit 2.8 inch PiTFT display?
#

A=""
TIME=0
TMP_FILE="/tmp/swipe.txt"
SPAN=500
UP_BARRIER=0
DOWN_BARRIER=0
LAST_VALUE=-1
barrier_check () {
    if [[ -n "$VALUE" ]]; then
        if [[ "$LAST_VALUE" -gt -1 ]]; then
            if [[ "$VALUE" -gt "$LAST_VALUE" ]]; then
                DOWN_BARRIER=0
            else
                UP_BARRIER=0
            fi
        fi
        LAST_VALUE=$VALUE
    fi

    if [[ "$UP_BARRIER" -gt 0 ]]; then
        if [[ "$VALUE" -gt "$UP_BARRIER" || -z "$VALUE" ]]; then
            continue
        else
            UP_BARRIER=0
        fi
    fi

    if [[ "$DOWN_BARRIER" -gt 0 ]]; then
        if [[ "$VALUE" -lt "$DOWN_BARRIER" || -z "$VALUE" ]]; then
            continue
        else
            DOWN_BARRIER=0
        fi
    fi
}

/usr/bin/evtest /dev/input/touchscreen | \
while read LINE ; do
    VALUE=$(/bin/echo $LINE | /bin/grep ABS_X | /usr/bin/awk '{split($0,a," "); print a[11]}')
    if [ -z "$VALUE" ]; then
        continue
    fi
    barrier_check

    if [[ "$A" == "" && -n "$VALUE" ]]; then
        A=$VALUE
    elif [[ "$A" -gt 0 && "$VALUE" -gt 0 ]]; then
        if [ $(($VALUE-$A-$SPAN)) -ge 0 ]; then
            /bin/echo "UP" > $TMP_FILE
            A=""
            UP_BARRIER=$VALUE
        elif [ $(($VALUE-$A+$SPAN)) -le 0 ]; then
            /bin/echo "DOWN" > $TMP_FILE
            A=""
            DOWN_BARRIER=$VALUE
        fi
    fi
done
