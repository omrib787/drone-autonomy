# 1. Goals and plan

## Why I'm building this

To learn how autonomous drones actually work, end to end: the hardware, the flight controller, the radio links, the companion computer and the software that makes decisions. The skills I want to come out with:

- Building and setting up a multirotor from individual parts
- ArduPilot: configuration, tuning, logs, safety features
- MAVLink: talking to a flight controller from code
- ROS 2: nodes, topics, services, and ArduPilot's native DDS interface
- Linux and embedded Linux on a Raspberry Pi
- Computer vision with OpenCV
- Python and C++
- Streaming video and telemetry over a network

## Why build instead of buying a ready-made drone

A ready-to-fly drone hides the parts I want to learn. Building it means I choose the flight controller, flash its firmware, wire the receiver and GPS, calibrate everything, and debug it when it doesn't work. ArduPilot also lets my own code control the drone, which consumer drones mostly don't.

## The plan

Two tracks run side by side: hardware on the bench, and software on the laptop. They meet when the Pi goes on the drone.

| Weeks | Hardware | Software |
|---|---|---|
| 1 | Check parts and batteries, register the drone | Ubuntu, ArduPilot SITL, Mission Planner |
| 2 | Flash the flight controller, radio, GPS, failsafe | First MAVLink scripts |
| 3 | Frame, power system, first power-up | ROS 2 Humble, ArduPilot's ROS 2 workspace |
| 4 | Motors, ESC calibration, compass, safety checks | ROS 2 flying the simulator |
| 5 | First flights | Pi talking to the flight controller |
| 6 | Pi and camera on the drone | Video streaming, first code-controlled flight |
| 7-9 | Field tests of the patrol | Patrol and search project |
| 10+ | | ROS 2 version, Android ground station |

The week-by-week checklist lives in my roadmap tracker. This repo holds the explanations.

## Rules I'm following

- **Hardware in order.** Each hardware step depends on the one before it.
- **Props off for every bench test.** Motor tests, failsafe tests and calibration all happen without propellers.
- **Simulate first.** Every piece of code flies in SITL before it flies on the drone.
- **The pilot always wins.** Any code that flies the drone stops the moment the mode switch leaves GUIDED.
- **Write it down as I go.** What I did, what broke, what I measured. That's what this repo is for.

## My notes

<!-- How it's actually going: what's taking longer than planned, what I'd change. -->
