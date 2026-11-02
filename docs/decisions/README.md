# Decisions

Short records of the choices that shaped this build: what I decided, what else I considered, and why. When I change my mind, I write a new record that replaces the old one instead of editing history.

| # | Decision | Status |
|---|---|---|
| [0001](0001-ardupilot.md) | ArduPilot as the flight software | Accepted |
| [0002](0002-matek-h743.md) | Matek H743-SLIM V3 flight controller | Accepted |
| [0003](0003-flysky-radio.md) | FlySky FS-i6X and FS-iA6B radio | Accepted |
| [0004](0004-pi4-companion.md) | Raspberry Pi 4 (4 GB) as the companion computer | Accepted |
| [0005](0005-pi-os-and-docker-ros2.md) | Raspberry Pi OS on the Pi, ROS 2 in Docker | Accepted |
| [0006](0006-3s-batteries.md) | 3S batteries | Accepted |
| [0007](0007-mavlink-first.md) | Patrol speaks MAVLink first, ROS 2 later | Accepted |

## Template

Copy this into a new file, `NNNN-short-name.md`:

```markdown
# NNNN. Title

Date: YYYY-MM-DD
Status: Proposed / Accepted / Replaced by NNNN

## Context
What problem I was solving and what constrained the choice.

## Options
- Option A: pros, cons
- Option B: pros, cons

## Decision
What I chose.

## Consequences
What this makes easier, what it makes harder, what I'll need to watch.
```
