# 0004. Raspberry Pi 4 (4 GB) as the companion computer

Date: 2026-09
Status: Accepted

## Context
The companion computer runs Linux, OpenCV, my mission code and sometimes ROS 2, and it's powered from the flight battery.

## Options
- **ESP32:** a microcontroller. No Linux, no OpenCV, only micro-ROS. Useful for other things, not this.
- **Pi Zero 2 W:** enough for a simple detector, but 512 MB of RAM is painful for development and ROS 2.
- **Pi 5:** faster, but wants 5 V / 5 A and active cooling, and uses the smaller camera connector.
- **Pi 4, 4 GB:** 5 V / 3 A (a normal UBEC handles it), standard camera connector, and ArduPilot's own companion-computer guide uses one.
- **NVIDIA Jetson:** far faster for neural networks, but costs several times more. Worth it only once the Pi is the bottleneck.

## Decision
Raspberry Pi 4, 4 GB.

## Consequences
- Neural-network detectors will be slow; fine for ArUco and colour, a reason to look at a Jetson later.
- 5 V from a UBEC through the GPIO pins, which bypasses the Pi's input protection: the UBEC voltage must be checked with a meter.
