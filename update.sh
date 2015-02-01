#!/bin/bash
# Update latest capturer image on the AdaFruit 2.8 inch PiTFT display.

/home/pi/display/swipe_detector.sh&

LAST_IMAGE=""
SWIPE_FILE="/tmp/swipe.txt"
IMAGE_FILE="/tmp/latest_capturer_image"

while true; do
    # Interpret swipe command from swipe_detector.py
    if [ -a $SWIPE_FILE ]; then
        NEW=""
        IMAGES='/home/pi/capturer/images/*'
        IMAGE=$(/bin/cat $IMAGE_FILE)
        DIRECTION=$(/bin/cat $SWIPE_FILE)

        if [[ "$DIRECTION" == "UP" ]]; then
            PREV=""
            for FILE in $IMAGES; do
                if [[ "$FILE" == "$IMAGE" ]]; then
                    NEW=$PREV
                fi
                PREV=$FILE
            done
            if [[ "$NEW" == "" ]]; then
                NEW=$IMAGE
            fi
            echo $NEW > $IMAGE_FILE

        elif [[ "$DIRECTION" == "DOWN" ]]; then
            NEXT=""
            for FILE in $IMAGES; do
                if [[ "$NEW" != "" ]]; then
                    NEXT=$FILE
                    break
                fi
                if [[ "$FILE" == "$IMAGE" ]]; then
                    NEW=$FILE
                fi
            done
            NEW=$NEXT
            if [[ "$NEW" == "" ]]; then
                NEW=$IMAGE
            fi
            echo $NEW > $IMAGE_FILE
        fi
        /bin/rm $SWIPE_FILE
    fi

    # Display new image
    IMAGE=$(cat $IMAGE_FILE)
    if [[ "$LAST_IMAGE" != "$IMAGE" ]]; then
        cd $(/usr/bin/dirname $IMAGE)
        /usr/bin/fbi -T 2 -d /dev/fb1 -f "DejaVu Sans Mono-11" -v -a $(/usr/bin/basename $IMAGE)
        LAST_IMAGE="$IMAGE"
    fi
done
