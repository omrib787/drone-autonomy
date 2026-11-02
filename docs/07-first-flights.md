# 7. First flights

Status: not started

## 7.1 Before leaving the house

- [ ] Both batteries charged (4.20 V per cell) and the transmitter's AA batteries good.
- [ ] Props, spare props, prop wrench, strap, smoke stopper, multimeter, laptop with Mission Planner.
- [ ] The field passes the [Israel checklist](03-safety-and-rules.md#flying-legally-in-israel).
- [ ] A spotter.

## 7.2 At the field, every flight

- [ ] Props on the right motors. The thick, rounded edge of each blade leads in that motor's spin direction. Don't trust the printed label.
- [ ] Prop nuts tight.
- [ ] Battery strapped down and centred. Nothing loose.
- [ ] Power up on level ground and don't move the drone until the GPS has 10+ satellites and a 3D fix.
- [ ] Mission Planner shows no PreArm messages.
- [ ] Mode switch on Stabilize (first flights) or Loiter (later). SwD (GUIDED) and SwA (RTL) down.
- [ ] Me 10 m back, upwind, with the spotter. Nobody else within 30 m.

## 7.3 The first three flights

| Flight | What | Done when |
|---|---|---|
| 1 | Stabilize hover at 1-2 m for 30 seconds, land | It lifts off evenly without tipping, and lands. Afterwards the motors are warm, not hot |
| 2 | AltHold, then Loiter, a minute each, gentle stick moves | It holds height in AltHold and position in Loiter |
| 3 | Loiter out to 20-30 m, then flip SwA (RTL) | It climbs to 15 m, flies home and lands itself |

If it tips over on takeoff: a motor is in the wrong place, spinning the wrong way, or has the wrong prop. Back to [Motor Test](06-assembly-and-wiring.md#68-motor-order-and-direction).

## 7.4 After each flight

- Feel the motors and ESCs: warm is fine, too hot to touch is not.
- Check the props for chips and the screws for looseness.
- Note the battery voltage after landing. Storage-charge any pack I won't use within two days.

## 7.5 Read the log

Download the log (Mission Planner → DataFlash Logs → Download) and open it at [plot.ardupilot.org](https://plot.ardupilot.org).

| What | Where | Good |
|---|---|---|
| Vibration | `VIBE.VibeX/Y/Z` | Under 15 good, under 30 acceptable. `VIBE.Clip` stays at 0 |
| Hover throttle | `CTUN.ThO` while hovering | About 0.35-0.5 |
| Battery under load | `BAT.Volt` | Stays above 10.5 V |
| Altitude hold | `CTUN.Alt` against `CTUN.DAlt` | Close together |

**Correct the current sensor:** after charging a pack, compare the mAh the charger put back with the mAh the log says was used (`BAT.CurrTot`). New `BATT_AMP_PERVLT` = old × (charger mAh ÷ logged mAh).

Save the logs I want to keep in `logs/` (they're big; commit only the interesting ones) and the parameters in `params/`.

## Flight log

| Date | Flight | Battery | Time | What I tested | Notes |
|---|---|---|---|---|---|
| | | | | | |

## My notes

<!-- How it felt, what surprised me, what I'd do differently. -->
