# 13 TODO — Mock SLAM & Navigation

## Phase Reference
- Phase-2 Mock/TDD → Phase-5 SLAM/Navigation

## Prompt

Mock SLAM Engine과 Navigation을 구현해 주세요.

### Dependency Rule
```text
Service -> Config -> Types
```

### Reference Docs
- `implementation_roadmap.md` Phase-2, Phase-5
- `interface.md` (ISlamEngine, INavigationEngine)
- `detailed_interface_schema.md`

### Create
```text
src/service/mock_slam_engine.py       — Mock SLAM implementing ISlamEngine
src/service/mock_navigation_engine.py — Mock Navigation implementing INavigationEngine
src/service/mock_robot_controller.py  — Mock Robot Controller implementing IRobotController
tests/unit/service/test_mock_slam_engine.py
tests/unit/service/test_mock_navigation_engine.py
tests/unit/service/test_mock_robot_controller.py
```

### Features
- MockSlamEngine: returns fixed pose, fixed map update
- MockNavigationEngine: returns fixed path from start to goal
- MockRobotController: receives control commands, reports status
- SLAM failure triggers recovery event
- Navigation path respects terrain traversability

### Required TC
- TC-SLAM-001: Mock SLAM returns fixed pose
- TC-SLAM-002: SLAM failure triggers SLAM_FAILURE event
- TC-NAV-001: Mock navigation returns fixed path
- TC-NAV-002: Navigation respects blocked terrain
- TC-CTRL-001: Robot controller receives commands
- TC-CTRL-002: Emergency stop command overrides all

### Completion Criteria
1. MockSlamEngine implements ISlamEngine Protocol
2. MockNavigationEngine implements INavigationEngine Protocol
3. MockRobotController implements IRobotController Protocol
4. All mocks return deterministic results
5. No ROS/rclpy dependency
