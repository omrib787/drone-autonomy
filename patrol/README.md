# Patrol and search

Fly a lawnmower pattern over an area until the camera finds a target, then estimate its GPS position and report it. Design notes, safety and test plan: [docs/09-project-patrol-search.md](../docs/09-project-patrol-search.md).

## Run it in the simulator

```bash
# terminal 1
sim_vehicle.py -v ArduCopter --console --map --out=udp:127.0.0.1:14551

# terminal 2, from this folder
pip install -r requirements.txt
python3 -m patrol.run --area areas/sitl_field.json --sim-target=-35.36302,149.16560
```

Example output:

```
[   0.2s] Plan: 4 lanes, 12.7 m apart, heading 90 deg
[   0.2s]       389 m of flying, about 2.2 min at 3.0 m/s
[   0.2s]       a 0.5 m target will be about 18 px wide at 15.0 m
[   1.0s] Armed. Taking off to 15.0 m
[  11.3s] Lane 1, start: heading to -35.362687, 149.164900
...
[ 122.4s] Target confirmed (4 of the last 10 frames)
[ 131.9s] TARGET at -35.3630199, 149.1655999 (sightings agree within 0.2 m)
[ 131.9s] Returning home (RTL)
```

The result is also written to `patrol_result.json`.

## Options

`python3 -m patrol.run --help` lists them all. The useful ones:

| Option | Default | |
|---|---|---|
| `--alt` | 15 | Search altitude, metres above home. Capped at 45 |
| `--speed` | 3 | Search speed, m/s |
| `--overlap` | 0.3 | Overlap between neighbouring camera strips |
| `--on-found` | rtl | `rtl`, `hover` or `land` |
| `--wait-for-guided` | off | Don't arm or take off; start when the pilot switches to GUIDED in the air |
| `--sim-target LAT,LON` | | Pretend target, for SITL |
| `--camera pi` / `--camera webcam` | | Real camera |
| `--aruco ID` | any | Which ArUco marker to look for |

## Tests

```bash
python3 -m pytest
```

## Code map

| File | |
|---|---|
| `patrol/geo.py` | GPS ↔ local metres |
| `patrol/coverage.py` | Camera footprint, lane spacing, lawnmower waypoints |
| `patrol/geolocate.py` | Pixel ↔ ground position, using altitude and attitude |
| `patrol/detector.py` | `SimulatedDetector`, `ArucoDetector` |
| `patrol/camera.py` | Pi camera, webcam, or none |
| `patrol/vehicle.py` | pymavlink wrapper |
| `patrol/mission.py` | The state machine |
| `patrol/run.py` | Command line for the mission |
| `patrol/bench.py` | Camera and detector test without a flight controller: `python3 -m patrol.bench --camera pi --aruco 7 --height 2` |
| `areas/` | Search areas as GPS corners |
