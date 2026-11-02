# ROS 2 workspace

Empty for now. The ROS 2 version of the patrol goes here: a detector node, a coverage planner node and a mission node, talking to ArduPilot through its DDS interface (`/ap/...` topics and services).

ArduPilot's own ROS 2 packages live in a separate workspace, `~/ardu_ws` (see [docs/04](../docs/04-dev-environment.md#47-ardupilots-ros-2-workspace)).

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build
```
