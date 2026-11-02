#!/bin/bash
# MAVProxy on the Pi's serial port. Needs SERIAL2_PROTOCOL 2 and SERIAL2_BAUD 921 on the flight controller.
# Usage: ./mavproxy.sh [laptop-ip]   (with an IP, MAVLink is also forwarded to Mission Planner on the laptop)
set -e
OUT=""
if [ -n "$1" ]; then OUT="--out=udp:$1:14550"; fi
exec ~/drone/bin/mavproxy.py --master=/dev/serial0 --baudrate 921600 $OUT
