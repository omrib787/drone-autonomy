# Hardware

- [motor-layout.svg](motor-layout.svg): ArduPilot Quad X motor numbers and spin directions
- [photos/](photos/): build photos
- [prints/](prints/): 3D-printed parts

## Wiring summary

Full details in [docs/06](../docs/06-assembly-and-wiring.md).

| Connection | From | To | Setting |
|---|---|---|---|
| Main power | Battery XT60 (female) | Power module → male XT60 pigtail on the PCB plate | Smoke stopper in front for first power-ups |
| ESC power ×4 | ESC thick red/black | PCB plate + / − | |
| Flight controller power | PCB plate | Matek VBAT, G | |
| ESC signal ×4 | ESC signal + ground | Matek S1-S4, G | ESC red wire cut back and insulated |
| Current sense | Power module current wire + GND | Matek Curr, G | `BATT_MONITOR 4` |
| Receiver | FS-iA6B iBUS | Matek RX6, 4.5 V, G | iBUS; fallback `BRD_ALT_CONFIG 1`, `SERIAL7_PROTOCOL 23` |
| GPS | TX, RX, VCC, GND | Matek RX2, TX2, 4.5 V, G | `SERIAL3` = GPS (default) |
| Compass | SDA, SCL | Matek SDA, SCL | Auto-detected |
| Pi serial | Pi pin 8 (TX), 10 (RX), 14 (GND) | Matek RX1, TX1, G | `SERIAL2` |
| Pi power | UBEC 5 V (measured) | Pi pin 4 (5 V), pin 6 (GND) | Never together with USB-C |
