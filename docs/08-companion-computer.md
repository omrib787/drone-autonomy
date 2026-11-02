# 8. Companion computer

The Raspberry Pi 4 on the drone: it runs my code, reads the camera, and talks to the flight controller over a serial wire.

Status: not started

## 8.1 Why Raspberry Pi OS, not Ubuntu

ArduPilot's own Pi guide uses Ubuntu 22.04, because ROS 2 Humble is built for it. But the Pi camera stack (libcamera, picamera2) is awkward to get working on Ubuntu 22.04, and the camera is central to this project. So the Pi runs **Raspberry Pi OS (64-bit)**, where the camera works out of the box, and ROS 2 runs inside a Docker container when I need it. See [decision 0005](decisions/0005-pi-os-and-docker-ros2.md).

## 8.2 Set up the Pi

1. In [Raspberry Pi Imager](https://www.raspberrypi.com/software/): Raspberry Pi 4 → Raspberry Pi OS Lite (64-bit). In the settings, set a hostname (`drone`), a user, Wi-Fi, and turn on SSH.
2. Boot it, then from the laptop: `ssh <user>@drone.local`.
3. Update and install the basics:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git python3-venv python3-picamera2 --no-install-recommends
```

**Check:** `ssh` works without a screen attached.

## 8.3 Free the serial port

The Pi's main UART is normally used by Bluetooth and a login console. Turn both off:

```bash
sudo raspi-config        # Interface Options → Serial Port: login shell No, hardware Yes
echo 'dtoverlay=disable-bt' | sudo tee -a /boot/firmware/config.txt
sudo usermod -aG dialout $USER
sudo reboot
```

**Check:** `ls -l /dev/serial0` points to `ttyAMA0`.

## 8.4 Wiring to the flight controller

| Pi pin | Matek | |
|---|---|---|
| 8 (GPIO14, TX) | RX1 | crossed: TX to RX |
| 10 (GPIO15, RX) | TX1 | |
| 14 (GND) | G | |

Both sides use 3.3 V logic, so no level shifter is needed. UART1 on the Matek is `SERIAL2`.

**Power:**
- On the bench: the Pi on its USB-C supply, the Matek on USB.
- On the drone: UBEC 5 V → pin 4, UBEC ground → pin 6, with male-to-female jumpers. **Never both at once.**

## 8.5 MAVLink over the wire

Flight controller parameters: `SERIAL2_PROTOCOL 2` (MAVLink 2), `SERIAL2_BAUD 921` (921600).

On the Pi:

```bash
python3 -m venv --system-site-packages ~/drone
~/drone/bin/pip install pymavlink MAVProxy
~/drone/bin/mavproxy.py --master=/dev/serial0 --baudrate 921600
```

`--system-site-packages` lets the virtual environment see picamera2, which comes from apt.

**Check:** MAVProxy shows heartbeats, and `param show SERIAL2*` returns values.

## 8.6 ROS 2 from the real flight controller (DDS)

ArduPilot's ROS 2 interface isn't in the standard firmware.

1. At [custom.ardupilot.org](https://custom.ardupilot.org): Add a build → Copter → stable → MatekH743, tick the DDS feature, Generate. Load the `.apj` through Mission Planner → Install Firmware → Load custom firmware.
2. Parameters: `DDS_ENABLE 1`, `SERIAL2_PROTOCOL 45`, `SERIAL2_BAUD 115`.
3. On the Pi, run the micro-ROS agent in Docker:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER        # log out and back in
docker run --rm -it --net=host --device=/dev/ttyAMA0 \
  microros/micro-ros-agent:humble serial --dev /dev/ttyAMA0 -b 115200
```

**Check, on the Pi**, in a second terminal:

```bash
docker run --rm -it --net=host ros:humble-ros-base ros2 topic list
```

The list includes `/ap/...` topics such as `/ap/navsat` and `/ap/battery`.

To see the topics from the laptop instead: run `ros2 topic list` in the Ubuntu box on the laptop, on the same Wi-Fi. The box shares the laptop's network, so DDS discovery works directly.

**MAVLink or DDS?** One serial link runs one protocol. The patrol speaks MAVLink, so `SERIAL2_PROTOCOL` stays at 2 normally and changes to 45 for ROS 2 sessions. To run both at once later: add `dtoverlay=uart3` (GPIO 4 and 5) on the Pi, wire it to another Matek UART, and check which device appeared with `ls /dev/ttyAMA*`.

## 8.7 Camera and video

```bash
rpicam-hello --list-cameras          # should list the imx219
rpicam-vid -t 0 --inline -o udp://<laptop-ip>:5000
```

On the laptop:

```bash
ffplay udp://@:5000 -fflags nobuffer -flags low_delay -framedrop
```

In the field, both the laptop and the Pi join my phone's hotspot.

## 8.8 On the drone

- Pi on standoffs, camera pointing straight down, with the top of the image towards the nose (the patrol code assumes this).
- Camera ribbon cable away from the ESCs.
- **Check:** on battery power with the camera streaming, `vcgencmd get_throttled` returns `0x0` (no undervoltage).

## 8.9 First flight with the Pi in charge

Run a script on the Pi that takes off to 5 m, hovers 10 seconds and lands, using `/dev/serial0` at 921600. Fly it with my thumb on SwD: flipping it down takes control back.

## My notes

<!-- Problems with the serial port, camera, power. -->
