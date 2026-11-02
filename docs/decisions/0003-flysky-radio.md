# 0003. FlySky FS-i6X and FS-iA6B radio

Date: 2026-09
Status: Accepted

## Context
Radios imported personally into Israel can be held at customs until the Ministry of Communications approves them. The ministry publishes lists of approved and refused items.

## Options
- **RadioMaster (ELRS):** the hobby favourite, but in August 2026 every RadioMaster model was on the refused list, and Israeli shops had pulled them.
- **Jumper, TBS Tango 2, BetaFPV and HappyModel ELRS receivers:** also on the refused list.
- **FlySky FS-i6X + FS-iA6B:** both on the approved list, cheap, and one of the most common ArduPilot beginner setups. iBUS gives all channels on one wire.

## Decision
FlySky FS-i6X with the FS-iA6B receiver.

## Consequences
- Shorter range and fewer features than ELRS, which doesn't matter for line-of-sight flying.
- The receiver holds its last outputs on signal loss unless a failsafe value is set on the transmitter. Setting that up and testing it is mandatory (docs/05, section 5.6).
