# 0005. Raspberry Pi OS on the Pi, ROS 2 in Docker

Date: 2026-10
Status: Accepted

## Context
ROS 2 Humble, the only ROS 2 version ArduPilot supports, is built for Ubuntu 22.04. ArduPilot's Pi guide uses Ubuntu 22.04. But the Pi camera stack (libcamera and picamera2) is hard to get working on Ubuntu 22.04, and the camera is central to the project.

## Options
- **Ubuntu 22.04 on the Pi:** ROS 2 installs natively; the camera needs workarounds.
- **Raspberry Pi OS:** the camera works out of the box; ROS 2 Humble isn't packaged for it.
- **Raspberry Pi OS with ROS 2 in Docker:** the camera works, and ROS 2 runs in the official `ros:humble` and `microros/micro-ros-agent:humble` containers (both have arm64 builds).

## Decision
Raspberry Pi OS (64-bit), with ROS 2 and the micro-ROS agent in Docker.

## Consequences
- The patrol code (Python, pymavlink, OpenCV, picamera2) runs directly on the Pi.
- ROS 2 nodes that need the camera have to receive images from outside the container, or the container gets camera access. Solve that when the ROS 2 version starts.
