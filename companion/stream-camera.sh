#!/bin/bash
# Stream the Pi camera as H.264 over UDP.
# Usage: ./stream-camera.sh <laptop-ip>
# On the laptop: ffplay udp://@:5000 -fflags nobuffer -flags low_delay -framedrop
set -e
if [ -z "$1" ]; then echo "usage: $0 <laptop-ip>"; exit 1; fi
exec rpicam-vid -t 0 --width 1280 --height 720 --framerate 30 --inline -o "udp://$1:5000"
