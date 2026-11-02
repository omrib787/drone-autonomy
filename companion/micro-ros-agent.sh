#!/bin/bash
# micro-ROS agent for ArduPilot's DDS interface.
# Needs DDS firmware and DDS_ENABLE 1, SERIAL2_PROTOCOL 45, SERIAL2_BAUD 115 on the flight controller.
set -e
exec docker run --rm -it --net=host --device=/dev/ttyAMA0 \
  microros/micro-ros-agent:humble serial --dev /dev/ttyAMA0 -b 115200
