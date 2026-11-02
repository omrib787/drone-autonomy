# 3. Safety and the rules in Israel

## Rules that never change

- **Props off** for any bench test, motor test, calibration or failsafe test. Props go on only at the flying field.
- **Smoke stopper** between the battery and the drone the first time it's powered after any soldering.
- **Arm only on the ground**, with me behind the drone and at least 10 m from it and from anyone else.
- **Never power the Pi from USB-C and the UBEC at the same time.**
- **The mode switch is the off switch for my code.** Every script stops the moment the mode leaves GUIDED. Know which switch position is Loiter before every autonomous flight.

## LiPo batteries

LiPos store a lot of energy and can catch fire if they're damaged, overcharged or shorted.

| Situation | What to do |
|---|---|
| Charging | In the LiPo bag, on a non-flammable surface (tiles, concrete), while I'm in the room. LiPo Balance mode, 3S, 5.0 A |
| Full charge | 4.20 V per cell, 12.6 V for the pack |
| Storage (more than ~2 days unused) | 3.80-3.85 V per cell. Use the charger's Storage mode |
| Landing voltage | Land by about 3.5 V per cell under load (10.5 V). ArduPilot's battery failsafe is set to that |
| Never below | 3.0 V per cell. A pack that went this low is suspect |
| Puffed, dented or hot | Stop using it. Put it in the bag, outside, away from anything flammable |
| Disposal | Discharge to about 3.0 V per cell, then take it to a battery recycling point |

How to check cells: multimeter on DC volts, probe neighbouring pins of the white 4-pin balance plug. Each pair of neighbours is one cell; the outer two pins give the whole pack.

## Flying legally in Israel

Checked October 2026. Rules change with the security situation: check the Civil Aviation Authority's current guidance before each trip.

**Once:**
- [ ] Register the drone with the CAAI. Any drone over 250 g must be registered. About ₪30, valid four years. Put the registration sticker on the frame.
- [ ] Pass the CAAI's online knowledge test: 15 questions, about ₪30, retries allowed.

**Before every flight:**
- [ ] Checked the zone map. The Israeli Drone Organization keeps one: blue for airports, red for military and restricted areas, purple for nature reserves.
- [ ] At least 2 km from any airport or airfield, and outside its controlled airspace (CTR).
- [ ] Far enough from the borders: 8 km from Lebanon, 6 km from Syria, 6 km from Jordan, 6 km from Gaza, 3 km from Egypt.
- [ ] Not within 500 m of police stations or prisons, and not near military bases.
- [ ] Not within 250 m of homes or public buildings without approval. Never over people.
- [ ] Planned to stay below 50 m and within 500 m, in direct line of sight. FPV video doesn't count as line of sight.
- [ ] A spotter with me.
- [ ] No alerts or military activity nearby. If one starts, land and wait.

The blanket ban on civilian drone flights during the war ended on 30 March 2026.

**What this means for the patrol project:** the search area must be small (tens of metres across), the search altitude stays under 45 m, and the drone stays where I can see it. The patrol code enforces a maximum altitude and range.

## Sources

- [TAKE-FPV: CAAI ends the blanket ban (March 2026)](https://takefpv.co.il/news-page/caai-drone-ban-lifted-march-2026)
- [TAKE-FPV: drone rules in Israel 2026](https://takefpv.co.il/%D7%97%D7%93%D7%A9%D7%95%D7%AA/drone-laws-israel-2026)

## Incident log

Write down anything that went wrong or nearly did: crashes, fly-aways, a battery that got hot, a failsafe that didn't trigger. Date, what happened, why, what I changed.

| Date | What happened | Cause | What I changed |
|---|---|---|---|
| | | | |
