# Companion computer scripts

Things that run on the Raspberry Pi. Setup steps are in [docs/08](../docs/08-companion-computer.md).

| Script | What it does |
|---|---|
| `mavproxy.sh` | Opens MAVProxy on the serial link to the flight controller |
| `micro-ros-agent.sh` | Runs the micro-ROS agent in Docker so ROS 2 can talk to ArduPilot (DDS firmware) |
| `stream-camera.sh` | Streams the camera to the laptop over UDP |

Copy the repo to the Pi with `git clone`, then run them from this folder.
