# 5. Flight controller setup

Getting ArduPilot running on the Matek H743-SLIM V3, with the radio, GPS and failsafes working. All of this happens on the bench, powered over USB, before the board goes on the frame.

Screen names below are Mission Planner's, as in ArduPilot's docs. I use QGroundControl on CachyOS; the [name table in section 4.3](04-dev-environment.md#mission-planner-names--qgroundcontrol) shows where each one is.

Status: not started

## 5.1 Check it's genuine

Matek warns about fake H743-SLIM V3 boards sold on AliExpress. Compare mine with the photos on [Matek's product page](https://www.mateksys.com/?portfolio=h743-slim): the logo, the printed labels, and the chips. If anything looks off, Matek will check photos sent to service@mateksys.com.

## 5.2 Flash ArduPilot

The board ships with INAV or Betaflight. ArduPilot goes on once through the bootloader (DFU), and after that it updates itself through Mission Planner.

1. From [firmware.ardupilot.org](https://firmware.ardupilot.org/Copter/stable/MatekH743/), download `arducopter_with_bl.hex` from Copter → stable → MatekH743. One firmware covers the whole H743 family, SLIM included.
2. Install [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) (Linux version; see [section 4.3](04-dev-environment.md#flashing-the-flight-controller-the-first-time) for the udev rules).
3. Hold the board's BOOT button, plug in USB, then let go. `lsusb` should show "STMicroelectronics STM Device in DFU Mode".
4. In STM32CubeProgrammer: choose USB, Connect, Open file (the `.hex`), Download.
5. Unplug, plug back in. The LEDs should blink in a new pattern.

Later updates: Mission Planner → Setup → Install Firmware, using `.apj` files.

## 5.3 First connection

1. SD card in (32 GB or smaller, FAT32). ArduPilot refuses to arm without one.
2. QGroundControl connects on its own over USB (the board appears as `/dev/ttyACM0`).
3. Setup → Mandatory Hardware → Frame Type: Quad, X. (`FRAME_CLASS 1`, `FRAME_TYPE 1`.)
4. Accel Calibration: follow the prompts through all six sides. The arrow on the board points forward.
5. Calibrate Level, on a flat surface.

**Check:** the artificial horizon on Flight Data tilts the right way when I tilt the board: nose down shows nose down, right side down shows a right roll.

## 5.4 Receiver

The FS-iA6B sends all channels down one wire using FlySky's iBUS protocol.

**Wiring:** a servo lead from the receiver's iBUS servo port to the Matek:

| Receiver | Matek pad |
|---|---|
| signal | RX6 (the default RC input) |
| + | the 4.5 V pad that is powered over USB (labelled 4V5 on many Matek boards; check my board's diagram) |
| − | G |

On the 4.5 V pad the receiver works on USB power alone, which makes bench setup easier. On a 5 V pad it only powers up with a battery plugged in.

**Bind** (AFHDS 2A): power the receiver with the bind plug in (or hold its bind button). On the transmitter: System setup → RX bind. The receiver LED goes solid. Remove the bind plug and power-cycle.

**Switch the transmitter to iBUS:** System setup → RX setup → Output mode → Serial: **i-BUS**.

**If Radio Calibration shows nothing:** set `BRD_ALT_CONFIG 1` and `SERIAL7_PROTOCOL 23`, then reboot. That turns RX6 into a normal serial receiver input.

## 5.5 Radio calibration and switches

Setup → Mandatory Hardware → Radio Calibration. Move every stick and switch to both ends, then Click when Done.

**Check the directions**, because ArduPilot has a convention:

| Stick | Channel | Correct |
|---|---|---|
| Roll right | 1 | value goes up |
| Pitch forward | 2 | value goes **down** |
| Throttle up | 3 | value goes up |
| Yaw right | 4 | value goes up |

If one is backwards, reverse that channel on the transmitter: Functions setup → Reverse.

**Switches** (on the transmitter, Functions setup → Aux. channels):

| Channel | Switch | Parameter | What it does |
|---|---|---|---|
| 5 | SwC (3 positions) | `FLTMODE1 0`, `FLTMODE4 2`, `FLTMODE6 5` | Stabilize / AltHold / Loiter |
| 6 | SwD (2 positions) | `RC6_OPTION 55` | Up: GUIDED (my code flies). Down: back to the mode on channel 5 |
| 7 | SwA (2 positions) | `RC7_OPTION 4` | Up: RTL, come home and land |

The GUIDED switch is how I hand control to the Pi, and flipping it back is how I take control away again. The patrol code stops the moment the mode leaves GUIDED.

**Check:** on Setup → Flight Modes, each SwC position highlights the right mode. Flipping SwD to up shows GUIDED, and flipping it back shows the SwC mode again. SwA up shows RTL.

## 5.6 Radio failsafe

If the radio link drops, ArduPilot has to know. By default the FS-iA6B keeps sending the last stick positions over iBUS, so the drone would carry on as if nothing happened. The fix is to make the receiver send an impossibly low throttle when the signal is lost:

1. Transmitter: Functions setup → End points. Set channel 3's low end to **120%**.
2. Throttle stick fully down. Functions setup → Failsafe → Channel 3 → On, and save it with the stick held down.
3. Set channel 3's end point back to **100%**.
4. Mission Planner, Radio Calibration: with the transmitter on and throttle down, note channel 3 (about 1000). Turn the transmitter off and note it again (about 900).
5. Set `FS_THR_ENABLE 1` (RTL, or Land without GPS) and set `FS_THR_VALUE` between those two numbers: at least 10 below the normal low, at least 10 above the failsafe value, and above 910. With 1000 and 900, use 950.

**Check:** transmitter off → channel 3 drops below `FS_THR_VALUE`, and Mission Planner shows a radio failsafe. The full armed test comes after assembly, with props off. See [ArduPilot's radio failsafe page](https://ardupilot.org/copter/docs/radio-failsafe.html).

## 5.7 GPS and compass

| GPS wire | Matek pad |
|---|---|
| TX | RX2 |
| RX | TX2 |
| VCC | the USB-powered 4.5 V pad |
| GND | G |
| SDA, SCL (compass) | the I2C SDA and SCL pads |

UART2 is `SERIAL3`, which ArduPilot uses for GPS by default. The compass is found automatically on I2C.

**Check:** near a window, the GPS gets a 3D fix within a few minutes, and Setup → Compass lists the external compass. Don't calibrate the compass yet: that happens on the finished drone, outdoors.

## 5.8 Battery monitor

The board measures battery voltage itself. Current comes from the power module's current wire, soldered to the Curr pad during assembly.

| Parameter | Value | Note |
|---|---|---|
| `BATT_MONITOR` | 4 | Voltage and current, already the board's default |
| `BATT_VOLT_PIN` / `BATT_CURR_PIN` | 10 / 11 | Board defaults. Don't change them |
| `BATT_VOLT_MULT` | 11.0 to start | Adjust until Mission Planner matches the multimeter |
| `BATT_AMP_PERVLT` | 17 to start | Typical for APM-style modules. Correct it after the first flights |
| `BATT_CAPACITY` | 5000 | |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 10.5 / 9.9 | 3.5 and 3.3 V per cell under load |
| `BATT_FS_LOW_ACT` / `BATT_FS_CRT_ACT` | 2 / 1 | Low: RTL. Critical: land where it is |

Don't use Mission Planner's battery "sensor" presets: some of them also change the pin numbers, which are specific to this board.

## 5.9 Fence and return-home height

| Parameter | Value | Why |
|---|---|---|
| `FENCE_ENABLE` | 1 | |
| `FENCE_TYPE` | 3 | Maximum altitude and a circle around home |
| `FENCE_ALT_MAX` | 45 | Stays under Israel's 50 m limit |
| `FENCE_RADIUS` | 150 | Metres from home |
| `RTL_ALT_M` | 15 | Return height in metres (called `RTL_ALT`, in centimetres, before Copter 4.7) |

The fence needs a GPS fix before it lets the drone arm.

## 5.10 Save the parameters

Config → Full Parameter List → Save to file. Save it as `params/YYYY-MM-DD-bench-setup.param` in this repo and commit it. If anything goes wrong later, this is the known-good starting point.

## My notes

<!-- Flashing problems, which pads I actually used, my FS_THR_VALUE readings, photos of the wiring. -->
