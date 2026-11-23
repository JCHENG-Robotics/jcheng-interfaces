cmake_minimum_required(VERSION 3.8)
project(jcheng_interfaces)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ContractVersion.msg"
  "msg/CapabilityManifest.msg"
  "msg/SafetyState.msg"
  "msg/ControlLease.msg"
  "msg/MotionCommand.msg"
  "msg/MotionFeedback.msg"
  "msg/MotionResult.msg"
  "msg/RobotState.msg"
  "msg/JointTrajectory.msg"
  "msg/JointTrajectoryPoint.msg"
  "msg/BasePulse.msg"
  "msg/GripperCommand.msg"
  "msg/TeleopCommand.msg"
  "msg/ValidationReport.msg"
  "srv/AcquireLease.srv"
  "srv/RenewLease.srv"
  "srv/ReleaseLease.srv"
  "srv/RevokeLease.srv"
  "srv/ValidateMotion.srv"
  "srv/GetSafetyState.srv"
  "srv/ResetSafety.srv"
  "srv/ArmSystem.srv"
  "srv/DisarmSystem.srv"
  "srv/GetCapabilities.srv"
  "action/ExecuteMotion.action"
  DEPENDENCIES
    builtin_interfaces
    geometry_msgs
    std_msgs
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
