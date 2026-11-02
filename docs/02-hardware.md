# 2. Hardware

Everything on the drone and on the bench, what it cost, and why it's this part and not another. Prices are what I paid in Israeli shekels, roughly, in September-October 2026. Most parts came from AliExpress.

## Flight hardware

| Part | Model | Approx. ₪ | Why this one |
|---|---|---|---|
| Frame kit | S500 with PCB bottom plate, 2212 920KV motors, 30A SimonK ESCs, 1045 props ("choice 3") | 272 | Big enough to carry a Pi and camera. The PCB plate is the power distribution board. Tall landing gear leaves room for a downward camera |
| Flight controller | Matek H743-SLIM V3 | 215 | H7 processor, which ArduPilot needs for its ROS 2 (DDS) interface. 7 UARTs and an SD card slot. See [decision 0002](decisions/0002-matek-h743.md) |
| GPS + compass | QUESCAN M10 with 5883 compass | 42 | Multi-constellation M10 receiver, compass built in, ArduPilot compatible |
| Radio | FlySky FS-i6X transmitter + FS-iA6B receiver | 206 | On the Ministry of Communications' approved list for personal import. iBUS output to the flight controller. See [decision 0003](decisions/0003-flysky-radio.md) |
| Power module | APM-style, XT60 | 21 | The Matek SLIM has no current sensor, so this measures current for ArduPilot |
| UBEC ×2 | 5 V / 6 V selectable, 3 A (5 A peak) | 22 | Powers the Pi from the flight battery. The second is a spare |
| Batteries ×2 | HRB 3S 5000 mAh 50C, XT60 | 258 | 3S because the 2212 920KV motors are rated for 3S on 10-inch props. See [decision 0006](decisions/0006-3s-batteries.md) |
| Spare props | 1045 / 1045R, 6 pairs | 23 | I will break props |
| XT60 pigtails | 12 AWG, one male, one female | 12 | The male one goes on the frame. The female is a spare |
| Battery strap | 20 × 250 mm, metal buckle | 20 | |
| Standoffs | M3 nylon kit | 16 | Mounting the flight controller and the Pi |
| microSD (flight controller) | 32 GB | 37 | ArduPilot won't arm without an SD card. Logs, scripts and DDS live on it |

## Companion computer

| Part | Model | Approx. ₪ | Why this one |
|---|---|---|---|
| Computer | Raspberry Pi 4, 4 GB | 448 | Runs Linux, ROS 2 and OpenCV. Needs 5 V / 3 A, which a UBEC can supply; a Pi 5 wants 5 A. See [decision 0004](decisions/0004-pi4-companion.md) |
| Camera | Pi Camera v2 (IMX219, 8 MP) | 84 | Standard 15-pin CSI connector on the Pi 4. Field of view 62.2° × 48.8° |
| microSD (Pi) | 32 GB, A2 class | 30 | A2 cards are faster for random access, which the OS needs |
| Power supply | 5.1 V 3 A USB-C | 53 | For bench work only. On the drone the Pi runs from a UBEC |
| Heatsink | | 17 | |

## Bench equipment

| Item | Approx. ₪ | Notes |
|---|---|---|
| Charger: iMAX B6AC clone | 90 | Built-in AC supply, balance and storage charging, 4 mm banana outputs |
| Banana to XT60 male charge lead ×2 | 15 | The battery's XT60 is female, so the lead must be male |
| Smoke stopper, XT60 | 17 | Goes between battery and drone for the first power-up after any soldering. Catches shorts |
| LiPo safety bag | 11 | Charge and store batteries in it |
| Soldering iron (60 W+), solder, flux | owned | XT60 and 12 AWG need a lot of heat |
| Multimeter | owned | For battery cells, the UBEC output and continuity checks |
| Hex drivers, wire strippers, heat shrink, zip ties | owned | |

**Total:** about ₪2,100 including the Pi, before VAT on imports.

## Things I learned while buying

- **Import rules for radios.** Personal imports of wireless gear can be held at customs. The Ministry of Communications publishes lists of [approved](https://data.gov.il/dataset/approved-items-by-personal-import) and [refused](https://data.gov.il/dataset/items-that-not-approved-by-personal-import) items. In August 2026 every RadioMaster model was on the refused list; the FlySky FS-i6X and FS-iA6B were approved.
- **Search-page prices lie.** AliExpress search results show the cheapest variant. Several "₪72 chargers" were the charger alone, needing a separate power brick.
- **XT60 genders.** The battery has the female connector (sockets); the drone has the male (pins). A charge lead labelled "XT60 female" won't plug into a battery.
- **Check the receiver letter.** The FS-iA6B has iBUS output. The plain FS-iA6 doesn't, and can't talk to a flight controller over a single wire.
- **Fake flight controllers exist.** Matek warns about fake H743-SLIM V3 boards on AliExpress, and will check photos sent to service@mateksys.com.
- **VAT.** Israel charges VAT on personal imports over $75, collected by AliExpress at checkout.

## My notes

<!-- What actually arrived, anything missing or wrong, photos of the parts laid out. -->
