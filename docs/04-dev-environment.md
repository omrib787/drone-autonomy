# 4. Development environment

Everything on the laptop: an Ubuntu 22.04 container, the ArduPilot simulator (SITL), QGroundControl, and ROS 2. None of this needs the drone, and most of the learning happens here.

My laptop runs CachyOS (Arch-based). The ArduPilot and ROS 2 tools run in an Ubuntu 22.04 container; QGroundControl and the flashing tool run on CachyOS itself.

Status: not started

## 4.1 Ubuntu 22.04 in a container

ArduPilot's ROS 2 support is ROS 2 Humble only, and Humble is built for **Ubuntu 22.04**. There are no Arch packages, and building it from source on Arch is slow and fragile. So instead of reinstalling, I run Ubuntu 22.04 in a [Distrobox](https://distrobox.it/) container. It shares my screen, network and USB devices, so graphical tools, SITL and the flight controller all work from inside it.

On CachyOS:

```bash
sudo pacman -S --needed distrobox podman
distrobox create --name drone --image ubuntu:22.04 --home ~/distrobox/drone
distrobox enter drone -- bash -l
```

Inside the box:

```bash
sudo apt update && sudo apt install -y git lsb-release x11-apps
```

- `--home ~/distrobox/drone` gives the box its own home folder. ArduPilot's install script and ROS 2 both add lines to `~/.profile` and `~/.bashrc`, and those would break my normal CachyOS shell if the home were shared. The folder is still a normal folder on CachyOS, so my usual editor can open files in it.
- Everything ArduPilot and ROS 2 from here on happens inside the box, always entered with `distrobox enter drone -- bash -l`. CachyOS's default shell is fish, and without `bash -l` the box starts fish too. ArduPilot's and ROS's setup scripts are bash, so fish fails with errors like `Unsupported use of '='`. A shortcut on CachyOS: `alias drone 'distrobox enter drone -- bash -l'; funcsave drone`, then type `drone`.
- For the flight controller over USB, my CachyOS user needs to be in the `uucp` group (Arch's serial-port group): `sudo usermod -aG uucp $USER`, then log out and in.

**Check:** inside the box, `lsb_release -a` prints `Ubuntu 22.04` and `xeyes` opens a window on my desktop.

## 4.2 ArduPilot SITL

SITL ("software in the loop") is the real ArduPilot firmware compiled to run on the laptop, with a physics model instead of a real drone. Everything I do here works the same way on the real flight controller.

```bash
sudo apt update && sudo apt install -y git
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```

The install script takes a while. When it finishes, `which sim_vehicle.py` should print a path. If it doesn't, close the terminal and open a new one.

Launch it. The first run compiles the firmware, which takes several minutes:

```bash
sim_vehicle.py -v ArduCopter --console --map -w --out=udp:127.0.0.1:14551
```

- `-w` wipes the simulated parameters back to defaults. Use it on the first run and whenever I've broken something.
- `--out=udp:127.0.0.1:14551` adds a MAVLink output for my own scripts. QGroundControl uses 14550, which SITL sends to by default.

**Check:** the console shows the vehicle, and after 30-60 seconds the messages settle and GPS shows a 3D fix. Then:

```
mode guided
arm throttle
takeoff 20
```

The map shows the drone climbing to 20 m. `mode rtl` brings it home and lands it.

### MAVProxy commands worth knowing

| Command | What it does |
|---|---|
| `mode guided` / `mode loiter` / `mode rtl` / `mode land` | Change flight mode |
| `arm throttle` / `disarm` | Arm or disarm |
| `takeoff 20` | Climb to 20 m (GUIDED only) |
| `param show WP_SPD*` | Show parameters (wildcards work) |
| `param set FENCE_ENABLE 1` | Change a parameter |
| `status` | Every MAVLink message, latest values |
| `wp load mission.txt` / `wp list` | Missions |
| right-click on the map | Fly here, draw a mission |

Parameter names: Copter 4.7 renamed several parameters to say their units. For example `RTL_ALT` (centimetres) became `RTL_ALT_M` (metres), and `WPNAV_SPEED` (cm/s) became `WP_SPD` (m/s). Older tutorials use the old names.

## 4.3 QGroundControl

The ground station I'll use to set up the real flight controller. Mission Planner, which most ArduPilot guides use, is Windows-only; [QGroundControl](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html) runs on Linux and supports ArduPilot fully. It runs on CachyOS itself, not in the box:

```bash
sudo pacman -S --needed fuse2
chmod +x QGroundControl-x86_64.AppImage
./QGroundControl-x86_64.AppImage
```

It listens on UDP port 14550, which is where SITL sends by default, and the box shares my network, so it connects on its own whenever SITL is running. If the real flight controller won't connect over USB, check I'm in the `uucp` group and stop ModemManager if it's installed: `sudo systemctl mask --now ModemManager`.

**Check:** the Fly view shows the simulated drone on the map and its instruments moving. Takeoff and Land work from the Fly view.

### Mission Planner names → QGroundControl

ArduPilot's docs and most tutorials describe Mission Planner screens. Where to find the same thing:

| Mission Planner | QGroundControl |
|---|---|
| Flight Data | Fly view |
| Install Firmware | Vehicle Setup → Firmware (updates after the first DFU flash; custom `.apj` files under Advanced settings) |
| Frame Type | Vehicle Setup → Frame |
| Accel Calibration, Calibrate Level, Compass | Vehicle Setup → Sensors |
| Radio Calibration | Vehicle Setup → Radio |
| Flight Modes | Vehicle Setup → Flight Modes (channel 7-12 switch options too) |
| Battery Monitor | Vehicle Setup → Power |
| Failsafe | Vehicle Setup → Failsafes |
| Motor Test | Vehicle Setup → Motors |
| ESC calibration | Vehicle Setup → ESC |
| Full Parameter List, save to file | Vehicle Setup → Parameters → Tools → Save to file |
| DataFlash Logs | Analyze Tools → Log Download |
| Messages | The megaphone icon at the top |

The rest of these docs use the Mission Planner names, because that's what ArduPilot's own pages use.

### Flashing the flight controller the first time

[STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) has a Linux version; install it on CachyOS. If it can't see the board in DFU mode, copy the udev rules from its `Drivers/rules` folder into `/etc/udev/rules.d/` and replug. `lsusb` should show "STMicroelectronics STM Device in DFU Mode".

## 4.4 First scripts

The scripts in [scripts/sitl/](../scripts/sitl/) talk to SITL with [pymavlink](https://mavlink.io/en/mavgen_python/):

```bash
pip3 install pymavlink
python3 scripts/sitl/hello_mavlink.py    # connect, arm, take off to 10 m, land
python3 scripts/sitl/fly_square.py       # fly a 20 m square at 10 m, land
```

Both were tested against Copter 4.7.2 SITL.

## 4.5 Flight logs

SITL writes `.BIN` logs into a `logs/` folder where it was launched. Open one at [plot.ardupilot.org](https://plot.ardupilot.org) and plot:

- `CTUN.Alt` against `CTUN.DAlt`: actual against desired altitude
- `ATT.Roll` against `ATT.DesRoll`: how well the attitude controller follows
- `BAT.Volt` and `BAT.Curr`
- `GPS.NSats` and `GPS.HDop`

The real drone writes the same logs to its SD card.

## 4.6 ROS 2 Humble

From the [official instructions](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html):

```bash
# UTF-8 locale
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# ROS 2 apt repository
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install -y curl
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# ROS 2 itself. Upgrade first: on 22.04, skipping this can remove system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-humble-desktop ros-dev-tools
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

**Check:** in one terminal `ros2 run demo_nodes_cpp talker`, in another `ros2 run demo_nodes_py listener`. The listener prints "I heard: [Hello World: N]".

Then the [beginner tutorials](https://docs.ros.org/en/humble/Tutorials.html): nodes, topics, services, parameters, and writing a publisher and subscriber in both Python and C++.

## 4.7 ArduPilot's ROS 2 workspace

ArduPilot talks ROS 2 natively through DDS (its `AP_DDS` library), with a small "micro-ROS agent" in between. Older tutorials use MAVROS; that's the old way.

From ArduPilot's [install page](https://ardupilot.org/dev/docs/ros2-install.html):

```bash
mkdir -p ~/ardu_ws/src && cd ~/ardu_ws
vcs import --recursive --input https://raw.githubusercontent.com/ArduPilot/ardupilot/master/Tools/ros2/ros2.repos src
sudo apt update && rosdep update
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y

sudo apt install -y default-jre
git clone --recurse-submodules --branch v4.7.0 https://github.com/ardupilot/Micro-XRCE-DDS-Gen.git
cd Micro-XRCE-DDS-Gen && ./gradlew assemble
echo "export PATH=\$PATH:$PWD/scripts" >> ~/.bashrc
source ~/.bashrc && microxrceddsgen -help

cd ~/ardu_ws
colcon build --packages-up-to ardupilot_dds_tests
```

Then SITL with DDS, from [ROS 2 with SITL](https://ardupilot.org/dev/docs/ros2-sitl.html):

```bash
source /opt/ros/humble/setup.bash
cd ~/ardu_ws && colcon build --packages-up-to ardupilot_sitl
source install/setup.bash
ros2 launch ardupilot_sitl sitl_dds_udp.launch.py \
  transport:=udp4 \
  refs:=$(ros2 pkg prefix ardupilot_sitl)/share/ardupilot_sitl/config/dds_xrce_profile.xml \
  synthetic_clock:=True wipe:=False model:=quad speedup:=1 slave:=0 instance:=0 \
  defaults:=$(ros2 pkg prefix ardupilot_sitl)/share/ardupilot_sitl/config/default_params/copter.parm,$(ros2 pkg prefix ardupilot_sitl)/share/ardupilot_sitl/config/default_params/dds_udp.parm \
  sim_address:=127.0.0.1 master:=tcp:127.0.0.1:5760 sitl:=127.0.0.1:5501
```

**Check:** `ros2 node list` shows `/ap`, and `ros2 topic echo /ap/geopose/filtered` streams positions. Then fly it from ROS 2 (mode 4 is GUIDED, 9 is LAND):

```bash
ros2 service call /ap/mode_switch ardupilot_msgs/srv/ModeSwitch "{mode: 4}"
ros2 service call /ap/arm_motors ardupilot_msgs/srv/ArmMotors "{arm: True}"
ros2 service call /ap/experimental/takeoff ardupilot_msgs/srv/Takeoff "{alt: 10.5}"
```

If no topics appear, set `DDS_ENABLE 1` and check that `DDS_DOMAIN_ID` matches `ROS_DOMAIN_ID` (both default to 0).

## Troubleshooting

| Problem | Fix |
|---|---|
| `sim_vehicle.py: command not found` | Run `. ~/.profile`, or open a new terminal |
| `Unsupported use of '='. In fish, please use 'set ...'` | The box started fish. Type `bash -l`, or enter with `distrobox enter drone -- bash -l` |
| `PreArm: Need 3D Fix` | Wait up to a minute after launch for the simulated GPS and EKF |
| Script waits forever for a heartbeat | SITL wasn't started with `--out=udp:127.0.0.1:14551` |
| Patrol aborts with "battery at 2x%" in SITL | The simulated battery drains across flights. Restart SITL |
| Build fails on a missing submodule | `git submodule update --init --recursive` |
| Map window doesn't open from the box | Check `xeyes` works; otherwise leave out `--map`, nothing depends on it |

## My notes

<!-- What I actually ran, what went wrong, how long each part took. -->
