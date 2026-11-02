# Learning scripts

Small, self-contained pymavlink scripts for the simulator. Start SITL with the extra output first:

```bash
sim_vehicle.py -v ArduCopter --console --map --out=udp:127.0.0.1:14551
```

| Script | What it teaches |
|---|---|
| [sitl/hello_mavlink.py](sitl/hello_mavlink.py) | Connecting, waiting for "ready to arm", modes, arming, takeoff, landing |
| [sitl/fly_square.py](sitl/fly_square.py) | Local NED coordinates and position targets in GUIDED |

Both were tested against ArduPilot Copter 4.7.2 SITL.
